# 08 — Key Management

Key management is where the residency, sovereignty, insider-threat and erasure stories all converge. If the keys are right, several otherwise-hard problems become tractable. If they are wrong, encryption is theatre.

## Best practices

- **Key custody, not encryption, is the sovereignty control.** The question a regulator or buyer actually asks is: *who can compel production of plaintext?* Answer it with key architecture.
- **Keys never leave the HSM boundary in plaintext.** Generation, storage, wrapping and unwrapping happen inside a certified module.
- **Strict separation of duties.** The people who can administer keys cannot access the data; the people who can access the data cannot administer keys. Enforce in IAM, not in policy prose.
- **Every key has a documented lifecycle:** generate → activate → rotate → deactivate → archive → destroy, with owners, cryptoperiods and evidence at each transition.
- **Automate rotation.** Manual rotation is either not done or done wrong.
- **Design for key destruction from the start.** Crypto-shredding is the only workable answer to "erase this from immutable backups".
- **Maintain a key inventory** — purpose, algorithm, custodian, cryptoperiod, dependency map. Required by DORA's RTS and essential for the PQC migration.

## EU regulatory implications

- **GDPR Art. 32/34** — key separation is what makes encrypted data "unintelligible" and can remove the Art. 34 duty to notify data subjects. **Chapter V / EDPB Recommendations 01/2020** — EU-held keys inaccessible to the third-country entity is the primary recognised technical supplementary measure for the India transfer (doc 03).
- **DORA Art. 9 and Commission Delegated Regulation (EU) 2024/1774** — an explicit **cryptographic key management policy** is required, covering generation, renewal, storage, backup, archival, retrieval, transmission, retirement, revocation and destruction of keys, plus a register of certificates and key lifecycle records. This is prescriptive; build the register.
- **DORA Art. 28–30** — if a key management service is provided by a third party supporting a critical or important function, it inherits the contractual regime. Customer-managed keys shift some of that burden to the customer, which many prefer.
- **NIS2 Art. 21(2)(h)** — cryptography and encryption policy.
- **MiCA** — the CASP retains responsibility for the confidentiality of records; loss of keys causing loss of records is a records-retention failure under Art. 68(9), not merely an availability incident.
- **eIDAS 2** — signing keys used for qualified seals must reside in a qualified signature creation device operated by a QTSP.

## Recommended architecture

### Key hierarchy

```
Root of trust
└── AWS KMS (FIPS 140-3 validated HSMs, eu-central-1)         [Tier 1 — default]
    ├── Platform CMK              ── infra secrets, non-tenant data
    ├── Audit-log CMK             ── separate key, separate admin role, no delete permission
    ├── Backup CMK                ── separate key, cross-region replica key in eu-north-1
    ├── Evidence-signing key      ── asymmetric, sign-only, for WORM evidence manifests
    └── Per-tenant CMK  (tenant-<id>)
        ├── Document DEKs         ── per-document, wrapped, stored beside ciphertext
        ├── Field DEK             ── per-tenant, for field-level encryption
        └── Blind-index HMAC key  ── per-tenant

Tier 2 — Customer-managed key (CMK in the customer's own AWS account, granted to us)
Tier 3 — External Key Store (XKS): key material in the customer's HSM, outside AWS entirely
```

### Tiering (this is also the commercial model — see doc 20)

| Tier | Key custody | Who can produce plaintext | Fit |
|---|---|---|---|
| **T1 — Platform-managed** | Our AWS KMS CMK per tenant | Us (and, under legal compulsion, AWS) | Default; SMB and mid-market |
| **T2 — Customer-managed (BYOK/CMEK)** | Customer's KMS key in the customer's account, used by us via a grant | Customer controls; revocation instantly disables access | Enterprise, regulated buyers |
| **T3 — External Key Store (HYOK)** | Customer's on-prem/EU-sovereign HSM via KMS XKS proxy | Customer only; AWS never holds the material | Tier-1 CASPs, sovereignty-sensitive |

T2/T3 give the customer a **kill switch**: revoking the grant or taking the XKS offline renders all their data unreadable within minutes. That is an availability risk we must document explicitly (see Risks) and a compelling control they will pay for.

### Key policies (the actual enforcement)

Per-tenant CMK policy enforces:
- Only the document service role may `Decrypt`, and only with an `EncryptionContext` whose `tenant_id` matches the key's tenant. This is the mechanism that makes a cross-tenant data-mixing bug fail closed.
- No principal has both `kms:ScheduleKeyDeletion` and data-plane `Decrypt`.
- `kms:ViaService` restricts use to `s3.eu-central-1.amazonaws.com` and `rds.*` where applicable, so a stolen credential cannot call KMS directly.
- Deny all principals outside `aws:PrincipalOrgID`, and deny requests where `aws:RequestedRegion` is outside the EU set.
- Key administration is a separate role, assumable only via break-glass with dual approval, never held standing.

### Rotation

| Key | Cryptoperiod | Mechanism |
|---|---|---|
| KMS CMKs (symmetric) | 365 days | KMS automatic rotation; old material retained for decryption of existing ciphertext |
| Document DEKs | Per-document; re-wrapped on tenant CMK rotation | No re-encryption of bulk data needed — the envelope pattern's main payoff |
| Field DEKs | 365 days, with background re-encryption | Versioned; ciphertext carries key version |
| Blind-index HMAC keys | Rotation requires full index rebuild — 3 years, or on compromise | Plan the rebuild path before launch |
| TLS certificates | ≤90 days (ACM automated) | Automated |
| Service identity certs (SPIFFE) | ≤24h | Automated |
| Evidence-signing keys | 2 years, with all historical public keys retained forever for verification | Key history published in the evidence manifest |
| Customer-managed keys | Customer's schedule; we must handle rotation transparently | Test with each T2/T3 onboarding |

**Emergency rotation runbook** (suspected key compromise): new key version → re-wrap all DEKs → re-encrypt field data → revoke old version → forensic assessment of exposure window → customer notification. Time-boxed and rehearsed annually.

### Backup, escrow and destruction

- **KMS key material cannot be exported** for Tier 1 — that is the point. The dependency risk is regional KMS availability, mitigated by multi-region keys for the backup CMK only.
- **For T2/T3, key backup is the customer's responsibility** and must be stated in bold in the contract. A customer losing their HSM material means permanent, unrecoverable loss of their data. This has happened to real organisations; make them acknowledge it in writing.
- **Destruction:** `ScheduleKeyDeletion` with a **30-day** waiting period (never 7 — the extra window has saved real companies), dual approval, automatic alerting to security and to the customer, and a documented reason. Deletion of a tenant CMK is the crypto-shred operation for that tenant's entire dataset including backups.
- **Key deletion is an evidence event** written to the WORM store with the approvals attached.

### Key inventory / register

A machine-maintained register: `key_id, alias, purpose, algorithm, tier, tenant_id, custodian_role, created, last_rotated, next_rotation, dependencies[], destruction_policy, pqc_migration_status`. Generated from cloud APIs, reconciled daily, and exported for DORA evidence. The `pqc_migration_status` column is what makes the 2030 deadline manageable.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Key deletion (accidental or malicious) destroys all tenant data irrecoverably | Total data loss for a tenant; company-ending if platform-wide | 30-day deletion window, dual approval, alerting, separation of duties, deny-deletion in the key policy for audit/evidence keys |
| Customer revokes T2/T3 key by accident or in a dispute | Immediate loss of service; customer may hold data hostage | Contractual notice period, health monitoring of customer key availability, alarm on grant changes, documented degraded mode |
| XKS proxy outage (customer's HSM unreachable) | Full service outage for that tenant | HA XKS proxy required contractually; cached data-key TTL to ride short outages; explicit SLA carve-out |
| Encryption context not enforced in the key policy | Cross-tenant decryption possible with one leaked role | Policy template with mandatory `kms:EncryptionContext:tenant_id` condition; automated policy conformance scanning |
| KMS request cost/throttling at scale | Latency, cost surprise, throttling incidents | Data-key caching (bounded TTL and use count) via the AWS Encryption SDK caching provider; monitor `ThrottlingException` |
| Key administrator with standing access | Insider compromise of all data | No standing key-admin; break-glass with dual approval and session recording |
| KMS regional dependency | Regional KMS impairment blocks all decryption | Multi-region key for backups; documented RTO impact; DR test includes a KMS-degraded scenario |
| Blind-index key rotation requires full reindex, never planned | Rotation deferred indefinitely; stale key risk | Rebuild path implemented and tested before launch |

## Trade-offs

- **AWS KMS (managed, cheap, FIPS 140-3, integrated) vs. CloudHSM (single-tenant HSM, FIPS 140-3 Level 3, full control, ~10× cost and real ops burden).** KMS's shared HSM model is the objection sophisticated buyers raise; XKS answers it better than CloudHSM does, at lower operational cost. **Recommendation: KMS as the default; XKS for sovereignty-sensitive customers; CloudHSM only if a specific customer contractually demands single-tenant HSM under our control.**
- **Per-tenant CMK (isolation, shredding, ~€1/key/month + request costs, key-count limits to watch) vs. shared key with encryption context.** **Recommendation: per-tenant CMK. At 1,000 tenants that is ~€12k/year — trivial against the risk.**
- **Data-key caching (large cost and latency win) vs. no caching (every operation hits KMS, maximum auditability).** Caching means a decrypted data key lives in process memory for its TTL. **Recommendation: cache with a short TTL (≤5 min), bounded use count, and never across tenant boundaries; disable for `RESTRICTED`/`PRIVILEGED` classes.**
- **30-day vs. 7-day deletion window.** Longer window means a departing malicious insider's deletion is recoverable; it also means a genuine erasure request takes 30 days to complete cryptographically. **Recommendation: 30 days, disclosed in the DPA.**
- **Multi-region keys (DR resilience) vs. single-region (tighter residency story).** Multi-region within the EU set is fine; the risk is misconfiguring a replica into a non-EU region. **Recommendation: multi-region only for the backup CMK, with an SCP preventing non-EU replicas.**

## Design decisions

- **DD-08-01:** AWS KMS in `eu-central-1` is the root of trust. Per-tenant CMK for all customer data. Separate CMKs for audit logs, backups and evidence signing, each with distinct administrative roles.
- **DD-08-02:** Key policies mandate `kms:EncryptionContext:tenant_id` matching, `kms:ViaService` restriction, `aws:PrincipalOrgID` and EU-region conditions. Enforced by a policy template and continuous conformance scanning.
- **DD-08-03:** Hard separation of duties — no principal holds both key administration and data-plane decrypt rights. Key administration is break-glass only, dual-approved, session-recorded.
- **DD-08-04:** Automatic annual rotation for KMS CMKs; envelope design ensures rotation never requires bulk re-encryption.
- **DD-08-05:** Three key-custody tiers offered commercially (platform-managed / customer-managed grant / External Key Store), with the availability and data-loss consequences of T2/T3 contractually acknowledged by the customer.
- **DD-08-06:** Key deletion uses a 30-day window with dual approval and automatic customer notification; deletion of audit and evidence keys is denied outright in the key policy.
- **DD-08-07:** Machine-generated key register with a `pqc_migration_status` field, reconciled daily and exported as DORA evidence.
- **DD-08-08:** Data-key caching with ≤5-minute TTL and bounded use count; disabled for `RESTRICTED` and `PRIVILEGED` document classes.
- **DD-08-09:** Documented key management policy covering the full lifecycle, reviewed annually, mapped clause-by-clause to Delegated Reg. (EU) 2024/1774.

## References

- NIST SP 800-57 Part 1 Rev. 5 — Recommendation for Key Management
- NIST SP 800-130 — Framework for Designing Cryptographic Key Management Systems
- FIPS 140-3 — Security Requirements for Cryptographic Modules
- Commission Delegated Regulation (EU) 2024/1774 — cryptographic key management requirements
- Regulation (EU) 2016/679 (GDPR) Art. 32, 34; EDPB Recommendations 01/2020
- AWS KMS: key policies, encryption context, grants, External Key Store (XKS), multi-region keys
- AWS Encryption SDK — data key caching guidance
- OASIS KMIP 2.x; PKCS#11 v3.0

## Confidence level

**High** — hierarchy, per-tenant CMK with encryption-context binding, separation of duties, tiered custody model, and crypto-shredding as the erasure mechanism. This is the standard and correct design for regulated multi-tenant SaaS.

**Medium** — operational cost and latency of KMS at the eventual transaction volume (needs load testing), and the practical reliability of customer-operated XKS proxies, which varies enormously by customer maturity. Pilot T3 with one customer before offering it generally.
