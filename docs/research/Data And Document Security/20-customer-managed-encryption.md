# 20 — Customer-Managed Encryption

Customer-managed keys (CMK/BYOK/HYOK) are simultaneously a security control, a regulatory answer, a sales differentiator and an availability risk. Handle all four deliberately.

## Best practices

- **Be precise about what the customer actually controls.** Marketing terms are abused in this space. Define your tiers by the answer to one question: *who can produce plaintext under legal compulsion?*
- **Make revocation real and fast.** A customer key control that takes days to take effect is not a control. Revocation must render data unreadable within minutes.
- **Make the availability consequence explicit and contractually acknowledged.** Customers who take key control also take the risk of locking themselves out. Get that in writing, with a signature.
- **Monitor customer key health continuously.** Their key becoming unavailable is our outage — detect it before their users do.
- **Cache data keys carefully.** Some caching is essential for performance; too much undermines the revocation guarantee. Bound it explicitly and disclose the window.
- **Design for key rotation by the customer** on their schedule, without downtime and without re-encrypting all data (envelope encryption makes this straightforward — doc 07).

## EU regulatory implications

- **GDPR Chapter V / EDPB Recommendations 01/2020** — customer-held keys are the strongest recognised technical supplementary measure. For a customer worried about US CLOUD Act exposure or about our Indian development entity, T3 (HYOK) is a complete technical answer: neither AWS nor we can produce plaintext.
- **GDPR Art. 32/34** — proper encryption with keys held by the customer means a compromise of our infrastructure may not constitute a breach of intelligible personal data at all, potentially removing the Art. 34 notification duty. Explain this benefit to customers; it is a real risk reduction for them.
- **GDPR Art. 28(3)(a)** — the processor acts only on documented instructions. Key revocation is the strongest possible expression of an instruction to stop processing.
- **DORA Art. 30(3)(f)/(g)** — termination rights and exit strategies. Key revocation gives the customer a hard, technical exit guarantee independent of our cooperation, which is precisely what DORA exit-strategy planning seeks.
- **DORA Art. 9** and **Delegated Reg. (EU) 2024/1774** — the customer's own cryptographic key management policy must cover keys they use with third-party services. Our documentation must support their policy, not fight it.
- **DORA Art. 11/12** — the customer must consider the availability impact of their own key management. Their HSM becoming unavailable is an ICT incident *for them*, and their business continuity plan must cover it. Say so explicitly at onboarding.
- **MiCA Art. 68(9)** — if a key is lost and records become unreadable, the CASP has failed its record-keeping obligation. This is a serious consequence that must be stated plainly.
- **eIDAS/national requirements** — some customers may require keys in a device certified to Common Criteria EAL4+ or equivalent; XKS with their own HSM accommodates this.

## Recommended architecture

### Tier definitions (be rigorous; publish these exact words)

| | **T1 — Platform-managed** | **T2 — Customer-managed (BYOK/CMEK)** | **T3 — Hold Your Own Key (HYOK/XKS)** |
|---|---|---|---|
| Key location | Our AWS KMS, `eu-central-1` | Customer's AWS KMS, customer's account | Customer's HSM (on-prem or EU-sovereign), accessed via AWS KMS External Key Store |
| Key material visible to AWS | Yes (within FIPS-validated HSMs) | Yes | **No** |
| Key material visible to us | No | No | No |
| Who can produce plaintext under compulsion | Us, and AWS | Customer controls the grant; we operate under it | **Customer only** |
| Revocation effect | We must act | Customer revokes the grant — effective in minutes | Customer takes the XKS proxy offline — effective immediately |
| Availability risk owner | Us | Shared | **Customer** |
| Rotation control | Us (automatic annual) | Customer | Customer |
| Typical buyer | SMB, mid-market | Enterprise, regulated | Tier-1 CASP, sovereignty-sensitive |
| Operational burden on customer | None | Low | **High — requires HSM operations expertise** |

### T2 implementation (AWS KMS cross-account grant)

```
Customer AWS account                     Our production account
────────────────────                     ──────────────────────
KMS CMK (customer-owned)                 Document service (IRSA role)
  key policy allows our role to:              │
   • kms:GenerateDataKey                      ├─ GenerateDataKey (encryption context:
   • kms:Decrypt                              │    tenant_id=<theirs>) → plaintext DEK
   • kms:DescribeKey                          │    + wrapped DEK
  conditioned on encryption context           │
  kms:EncryptionContext:tenant_id = <theirs>  └─ encrypt document, store wrapped DEK
  CloudTrail in customer account logs
  every use — they see our access
```

Key properties:
- The customer sees **every** key operation we perform in **their own CloudTrail**. This is powerful transparency — they can audit our access to their data independently, without trusting our logs.
- The encryption-context condition means our role cannot use their key for any other tenant's data.
- Revoking the key policy statement or disabling the key stops all access within the data-key cache TTL.
- Onboarding is a documented CloudFormation/Terraform template the customer applies in their account — not a bespoke engineering exercise.

### T3 implementation (AWS KMS External Key Store)

- The customer runs an **XKS proxy** (a standardised HTTPS API) in front of their HSM. AWS KMS calls the proxy for every cryptographic operation; key material never enters AWS.
- Requirements imposed on the customer, contractually:
  - HA XKS proxy (minimum two instances, independent failure domains).
  - Documented availability target and monitoring, with alerting to both parties.
  - Network path from AWS (public endpoint with mutual TLS, or VPC endpoint service).
  - Tested key backup and recovery procedures, evidenced.
- **Latency is real:** every decrypt round-trips to the customer's HSM. Data-key caching becomes essential, not optional. Measure and disclose the performance profile at onboarding.
- Not all AWS services support XKS-backed keys. **Validate the exact service set (S3 SSE-KMS, RDS, EBS, Secrets Manager) before offering T3**, and design the T3 architecture to use only supported services for tenant data.

### Data-key caching policy

| Document class | Cache TTL | Max uses | Rationale |
|---|---|---|---|
| `PUBLIC` / `INTERNAL` | 15 min | 1000 | Performance |
| `CONFIDENTIAL` | 5 min | 100 | Balance |
| `RESTRICTED` / `PRIVILEGED` | **No caching** | 1 | Every access hits the customer's key and appears in their audit trail |

Disclose the caching window in the contract: "revocation takes effect within N minutes for class X." A customer who believes revocation is instantaneous for all data will be justifiably upset otherwise.

### Key health monitoring and failure handling

- A synthetic canary performs a `Decrypt` against every customer key every 60 seconds.
- Failures escalate: 3 consecutive failures → alert our on-call **and** the customer's registered contacts; 10 minutes of failure → tenant enters **key-degraded mode** (doc 16) with a clear in-app message identifying the cause as customer key unavailability.
- Grant and key-policy changes in the customer account are detected (via a scheduled `DescribeKey`/`ListGrants` check) and alerted, so an accidental revocation is caught in seconds rather than discovered by users.
- **Never fail open.** If the key is unavailable, data is unavailable. There is no fallback key — that would defeat the entire model, and customers will ask this question in diligence.

### Commercial and contractual framing

- T2/T3 priced as premium tiers; T3 additionally carries a professional-services onboarding fee reflecting the real integration effort.
- Contract must contain, in plain language and separately acknowledged:
  - Customer is solely responsible for key availability, backup and recovery.
  - Loss of key material results in **permanent, unrecoverable loss** of their data, including all backups (our backups are encrypted with the same key hierarchy).
  - SLA carve-out for outages caused by customer key unavailability.
  - Rotation and revocation notice expectations.
  - Their obligation to test key recovery annually and to evidence it.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Customer accidentally deletes or disables their key | Permanent data loss including backups; MiCA record-keeping failure for them | Contractual acknowledgement; grant/key monitoring with immediate alerting; strongly recommend (and verify) that they enable a 30-day KMS deletion window |
| Customer XKS proxy outage | Full tenant outage; SLA dispute | HA requirement in contract; SLA carve-out; canary monitoring; data-key caching to ride short interruptions |
| Customer revokes key in a commercial dispute | Data hostage situation; support burden | Contractual notice period before revocation; documented data-export process available while access remains |
| Latency degradation with T3 | Poor user experience blamed on us | Benchmark and disclose at onboarding; class-based caching; set expectations in writing |
| Key policy misconfiguration by the customer allows over-broad access | Their key usable beyond intended scope | We supply the exact template; validate the policy at onboarding and re-validate periodically |
| An AWS service used for tenant data does not support XKS keys | T3 promise cannot be met after it has been sold | Validate service support before offering T3; restrict T3 architecture to supported services |
| Operational complexity of three tiers | Bugs, inconsistent behaviour, high support cost | Single key-broker abstraction; tier is configuration, not a code path; identical test suite run against all three tiers |
| Customer believes CMK protects against our application-layer access | Misunderstanding surfaces during an audit | Be explicit: CMK protects against infrastructure-level and legal-compulsion access, **not** against a compromise of our running application, which legitimately holds decrypted data in memory during processing |

## Trade-offs

- **Offering T3 at all (unlocks the largest, most demanding deals; substantial engineering, support and operational risk) vs. T1/T2 only.** **Recommendation: build T1 and T2 first; offer T3 from roadmap phase 3, initially to a single design-partner customer, priced to reflect true cost.**
- **Aggressive data-key caching (performance, cost) vs. minimal caching (revocation fidelity, full audit visibility in the customer's CloudTrail).** **Recommendation: class-based caching as tabled, with the window disclosed contractually.**
- **Per-tenant CMK for all customers including T1 (uniform architecture, easy tier upgrades) vs. shared key for T1.** **Recommendation: per-tenant CMK universally (DD-08-01). It costs little and means moving a customer from T1 to T2 is a key-migration operation rather than an architectural change.**
- **Fail-closed on key unavailability (correct, causes outages) vs. a cached fallback.** **Recommendation: fail closed, absolutely. Any fallback key destroys the security proposition and will be found in diligence.**
- **Supporting customer key rotation transparently (good experience; complexity around re-wrapping in-flight DEKs) vs. requiring a maintenance window.** **Recommendation: transparent rotation — envelope encryption makes it a background re-wrap of DEKs with no bulk re-encryption.**

## Design decisions

- **DD-20-01:** Three published key-custody tiers with the precise definitions above; the differentiating question ("who can produce plaintext under compulsion?") is stated explicitly in customer documentation.
- **DD-20-02:** All tiers use per-tenant CMKs and identical envelope encryption; the tier is a configuration of the key-broker service, not a separate code path.
- **DD-20-03:** T2 implemented via cross-account KMS grants with mandatory `tenant_id` encryption-context conditions; customers audit our key usage in their own CloudTrail.
- **DD-20-04:** T3 implemented via AWS KMS External Key Store, offered only after validating that every AWS service handling tenant data supports XKS-backed keys.
- **DD-20-05:** Class-based data-key caching (no caching for `RESTRICTED`/`PRIVILEGED`), with the revocation-effect window disclosed contractually.
- **DD-20-06:** 60-second canary decrypt against every customer key; grant and policy changes detected and alerted; failure escalates to key-degraded mode with a clear customer-facing cause.
- **DD-20-07:** Fail closed on key unavailability. No fallback key exists anywhere in the architecture.
- **DD-20-08:** Contract requires separate customer acknowledgement of permanent data-loss risk, HA obligations for T3, annual evidenced key-recovery testing, and an SLA carve-out for customer key unavailability.
- **DD-20-09:** T3 launched with a single design-partner customer before general availability.
- **DD-20-10:** Customer documentation states explicitly that CMK/HYOK protects against infrastructure-level and legal-compulsion access but not against compromise of the running application during legitimate processing.

## References

- Regulation (EU) 2016/679 (GDPR) Art. 28(3)(a), 32, 34; Chapter V
- EDPB Recommendations 01/2020 on supplementary measures — technical measures, encryption scenarios
- Regulation (EU) 2022/2554 (DORA) Art. 9, 11, 12, 30(3); Commission Delegated Regulation (EU) 2024/1774
- Regulation (EU) 2023/1114 (MiCA) Art. 68(9)
- AWS KMS: External Key Store (XKS), cross-account key grants, encryption context, key policies
- AWS Encryption SDK — data key caching guidance and security considerations
- NIST SP 800-57 Part 1 Rev. 5 — key management lifecycle
- US CLOUD Act, 18 U.S.C. §2713 (context for the tiering rationale)

## Confidence level

**High** — the tier model, cross-account grant implementation, fail-closed principle, caching policy, and the contractual risk allocation. This is the established pattern for regulated multi-tenant SaaS and the security properties are well understood.

**Medium** — the current breadth of AWS service support for XKS-backed keys (verify against live documentation before selling T3), and real-world XKS latency at production volumes, which must be benchmarked with the design-partner customer before general availability.
