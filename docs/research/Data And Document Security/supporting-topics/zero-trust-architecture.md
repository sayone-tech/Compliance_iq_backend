# Zero Trust Architecture

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](../future-scope/future-and-optional-scope.md).

Not named by the PRD. This document is **[PROPOSED]**: it describes the property that makes NFR-01 hold under failure — **no access decision depends on network position** — and the enforcement layers that deliver it. No mesh, policy-engine or workload-identity product is selected.

## Best practices

- **Zero Trust is an outcome, not a product.** It is achieved when every access decision is made per request against verified identity, resource sensitivity and context.
- **Start with the highest-value flow.** For ComplianceIQ that is the path from a user to decrypted evidence. Make that path fully per-request-authorised first; expand outward.
- **Identity for machines matters as much as for humans.** A service that trusts any caller inside the network is a flat network wearing a costume.
- **Continuous verification, not one-time authentication.** Session state is re-evaluated against changing signals.
- **Assume breach.** Design so a fully compromised workload, workstation or CI job yields a bounded, detectable loss.

## Regulatory implications

Zero Trust is not named in EU regulation, but it is a direct way to satisfy several explicit expectations at once:

- **GDPR Art. 25(2)** — by default, personal data must not be accessible to an indefinite number of persons without intervention. Per-request, purpose-bound authorisation is the strongest technical expression of this.
- **GDPR Art. 32(1)(b)** — ongoing confidentiality and resilience.
- **Delegated Reg. (EU) 2024/1774** — network segmentation, strong authentication for remote and privileged access, privileged access management, protection of data in transit within the organisation. *(Design reference.)*
- **Cross-border (`cross-border-data-processing`)** — location- and device-aware policy is the technical enforcement point if any non-EU access path exists.

## Recommended architecture

### Policy decision and enforcement

```
Signals ─────────────▶  Policy decision layer
• Identity: user, system role, firm, MFA state    versioned, reviewed, unit-tested,
• Device posture (workforce)                       evaluated per request
• Resource metadata: classification, firm,                │
  record state (signed off, report issued,               │ allow/deny + reason + policy version
  legal hold)                                            ▼
• Context: purpose, session age, location        Enforcement points
                                                 • API ingress authorisation
                                                 • Service-to-service identity authorisation
                                                 • Application repository tenant scoping
                                                 • Database row-level security
                                                 • Key policy requiring a matching firm
                                                   encryption context
                                                          │ every decision
                                                          ▼
                                                 Audit log (FR-13, `audit-logging`)
```

**Five independent enforcement points stand between a user and evidence plaintext, and any one of them alone prevents cross-firm disclosure.** That redundancy is deliberate: cross-firm disclosure (NFR-01) is the failure mode that ends the product.

### Workload identity **[PROPOSED]**

- Every workload receives a cryptographic identity attested from its platform attributes, materialised as a short-lived certificate.
- **All service-to-service traffic is mutually authenticated**, with both peers verifying the other's identity.
- **Authorisation policies define the allowed call graph by identity**, deny-by-default: only the API layer may call the document service; only the mapping service may call the inference gateway; nothing may write to the audit sink except the audit writer.
- Result: network position confers nothing.

### Device trust **[PROPOSED — workforce only]**

- Workforce devices enrolled in management with enforced disk encryption, endpoint detection, patch level, screen lock and firewall.
- **Device compliance is an input to the policy decision.** A non-compliant device gets read-only metadata at most; never evidence content, never production.

Device-trust enforcement for **firm users** is not in the PRD, would add friction for a B2B compliance tool used by small teams (TI-06 records roughly ten platform users per firm), and is **[FUTURE]**.

### Per-request authorisation inputs

| Signal | Example condition |
|---|---|
| Subject identity and system role | actor holds the CCO / Compliance Manager system role |
| Firm match | resource firm equals subject firm — the NFR-01 predicate |
| Assignment | actor is the assigned Lead Tester for this test (FR-20, GAP-05) |
| MFA state | second factor satisfied for this session (FR-11) |
| Device posture | workforce sessions only |
| Location | production access from an approved location (`cross-border-data-processing`) |
| Purpose | test execution, review, report generation, remediation validation, support |
| Record state | test signed off (FR-27), report issued (FR-61), N/A recorded (FR-21b) — all of which make records immutable |
| Resource classification | `RESTRICTED` evidence requires step-up |

Decisions are cached only for an identical tuple and only for seconds — never for the session.

### Continuous verification **[PROPOSED]**

Session risk is recomputed on new IP, new device, location change, elevated volume, endpoint alert or identity-provider risk event. Elevated risk triggers step-up or session termination. Loss of device compliance revokes active workforce sessions promptly.

Behavioural analytics beyond a small set of high-signal rules is **[FUTURE]** (`insider-threat-protection`).

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| The policy layer becomes a single point of failure | Total outage — every request depends on it | Locally evaluated, signed policy bundles; fail-closed for writes and `RESTRICTED` reads; documented degraded mode |
| Policy complexity outgrows comprehension | Unintended allows; nobody can reason about the rules | Mandatory policy unit tests; a written authoring standard; periodic review; keep firm-role mapping as data, permissions as code |
| Zero Trust theatre — mutual TLS deployed but every service allowed to call every other | False assurance | Explicit authorisation policy per service; deny-by-default; automated call-graph conformance checks |
| Workload certificate rotation failure | Cascading outage against NFR-08 | Rotation well before expiry; alerting on renewal failure; rotation tested |
| Device posture signal unavailable | Either lockout or fail-open | Documented decision: fail-closed for production and `RESTRICTED`; degraded-allow with alerting for low-sensitivity reads |
| Per-request authorisation overhead | Latency against the NFR-05 two-second dashboard target | Benchmark early; evaluate policy locally; measure p99 |
| Users defeat friction (shared logins) | Control erosion; FR-13 attribution broken | Monitor for it; make the compliant path fast; note FR-12 makes each account individually invited, so sharing is a policy violation with an audit trail |

## Trade-offs

- **Full mutual TLS between services vs. TLS termination at ingress only.** Recommendation: mutual TLS where the chosen platform provides it at acceptable operational cost; the identity-based authorisation it enables is the core of the model. **[PROPOSED / OPEN]**
- **Centralised policy evaluation vs. locally evaluated signed bundles.** Recommendation: central authoring, local evaluation — consistency of authorship with resilience of execution; bundle staleness bounded and alerted. **[PROPOSED]**
- **Fail-closed vs. fail-open on signal unavailability.** Recommendation: fail-closed for writes, privileged actions and `RESTRICTED` reads; fail-open with alerting for low-sensitivity metadata. Document it — it is asked about in every security review. **[PROPOSED]**
- **Big-bang adoption vs. incremental by data path.** Recommendation: incremental, starting with the user → evidence path, which is where the catastrophic risk lives. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification |
|---|---|---|
| DD-12-01 | Five independent enforcement points on the path to evidence plaintext: ingress authorisation, service identity authorisation, application tenant scoping, database row-level security, key policy encryption context | **[PROPOSED]** — implements NFR-01 |
| DD-12-02 | Cryptographic workload identities with short-lived credentials; mutual authentication between services; deny-by-default call graph | **[PROPOSED]** |
| DD-12-03 | Policy authored centrally, version-controlled, unit-tested in CI, evaluated locally per request | **[PROPOSED]** — implements FR-09 |
| DD-12-04 | Device posture is a mandatory input for workforce access; non-compliant devices cannot reach production or evidence content | **[PROPOSED]** |
| DD-12-05 | Session location is a policy input for production access | **[PROPOSED]** — enforcement point for `cross-border-data-processing` |
| DD-12-06 | Purpose is a required parameter on evidence access requests, logged and policy-evaluated | **[PROPOSED]** — supports FR-13 |
| DD-12-07 | Fail-closed for writes, privileged operations and `RESTRICTED` reads; fail-open with alerting for low-sensitivity metadata reads | **[PROPOSED]** |
| DD-12-08 | Continuous session re-evaluation with automatic revocation on device non-compliance or identity risk events | **[PROPOSED]** |
| DD-12-09 | Device-trust enforcement for firm users | **[FUTURE]** |

## References

- NIST SP 800-207 — Zero Trust Architecture (https://csrc.nist.gov/pubs/sp/800/207/final)
- NIST SP 1800-35 — Implementing a Zero Trust Architecture
- CISA Zero Trust Maturity Model v2.0 — useful as a self-assessment framework, not adopted as a target here
- Commission Delegated Regulation (EU) 2024/1774 — access management, segmentation, remote access *(design reference)*
- SPIFFE/SPIRE specification (https://spiffe.io) — one workload-identity option

## Confidence level

**High** — the decision/enforcement model, layered enforcement points and incremental adoption path.

**Medium** — the real latency cost of five enforcement layers against NFR-05 at production scale in a small team. Benchmark rather than assume.
