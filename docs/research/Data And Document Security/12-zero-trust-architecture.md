# 12 — Zero Trust Architecture

## Best practices

- **Zero Trust is an outcome, not a product.** It is achieved when no access decision depends on network position, and every access decision is made per-request against verified identity, device state, and resource sensitivity.
- **The five NIST SP 800-207 tenets that matter operationally:** all data sources and services are resources; all communication is secured regardless of network location; access is granted per-session; access is determined by dynamic policy including observable state; the enterprise measures the integrity and security posture of all assets continuously.
- **Start with the highest-value asset flow.** For this platform: the path from a user to a decrypted document. Make that path fully Zero Trust first; expand outward.
- **Identity for machines is as important as for humans.** A service that trusts any caller from inside the VPC is a flat network wearing a mesh costume.
- **Continuous verification, not one-time authentication.** Session state is re-evaluated against changing signals — device compliance drift, impossible travel, anomalous volume.
- **Assume breach.** Design so that a fully compromised pod, workstation or CI job yields a bounded, detectable loss.

## EU regulatory implications

Zero Trust is not named in EU regulation, but it is the most direct way to satisfy several explicit requirements simultaneously:

- **DORA Art. 9(4)(c)** — need-to-know, least privilege, segregation of duties. Per-request authorisation is the mechanism.
- **Delegated Reg. (EU) 2024/1774** — network segmentation, strong authentication for remote and privileged access, privileged access management, and protection of data in transit within the organisation. mTLS everywhere and JIT privilege satisfy these together.
- **NIS2 Art. 21(2)(j)** — explicitly references "multi-factor authentication or **continuous authentication** solutions, secured voice, video and text communications". Continuous authentication is Zero Trust vocabulary appearing in EU law.
- **GDPR Art. 25(2)** — by default, personal data must not be made accessible to an indefinite number of natural persons without intervention. Per-request, purpose-bound authorisation is the strongest technical expression of this.
- **GDPR Art. 32(1)(b)** — ongoing confidentiality and resilience.
- **Cross-border (doc 03)** — device- and location-aware policy is the enforcement point for "no India-based access to EU production personal data".
- **CISA Zero Trust Maturity Model v2.0** and **NCSC Zero Trust principles** are useful assurance frameworks to map against for customer security questionnaires, even though neither is an EU instrument.

## Recommended architecture

### Policy Decision Point / Policy Enforcement Point model

```
                          ┌──────────────────────────────────┐
   Signals ──────────────▶│  Policy Decision Point (PDP)     │
   • IdP: user, groups,   │  Cedar policy engine             │
     MFA strength, risk   │  versioned, git-managed, tested  │
   • MDM: device posture  └───────────┬──────────────────────┘
   • Threat intel                     │ allow/deny + reason + policy_version
   • Behaviour baseline               │
   • Resource metadata:               ▼
     classification,      ┌──────────────────────────────────┐
     tenant, legal hold   │  Policy Enforcement Points       │
                          │  • API gateway / ingress          │
                          │  • Service mesh authz policy      │
                          │  • Application authz middleware   │
                          │  • Database RLS                   │
                          │  • KMS key policy (enc. context)  │
                          │  • S3 bucket / VPC endpoint policy│
                          └───────────┬──────────────────────┘
                                      │ every decision
                                      ▼
                              Audit log (doc 14)
```

Five enforcement points on the path to a document, each independently sufficient to stop a cross-tenant read. This is the concrete meaning of "assume breach" for our top risk.

### Workload identity (SPIFFE/SPIRE)

- Every workload receives a **SPIFFE ID** (`spiffe://platform.eu/ns/documents/sa/document-service`) attested from Kubernetes node and pod attributes, materialised as a short-lived X.509 SVID (≤1 hour).
- **All service-to-service traffic is mTLS** with both peers verifying the other's SPIFFE ID. Linkerd provides this transparently.
- **Mesh authorisation policies** define the allowed call graph by identity: only `document-service` may call `key-broker`; only `api-gateway` may call `document-service`; nothing may call `evidence-writer` except `assessment-service`.
- Result: network position confers nothing. A compromised pod in another namespace cannot call the document service even with full network reachability.

### Device trust

- Workforce devices enrolled in MDM (Intune/Jamf/Kandji) with enforced: full-disk encryption, EDR agent healthy, OS patch level within policy, screen lock, no jailbreak/root, firewall on.
- **Device compliance state is an input to the PDP.** Non-compliant device → read-only metadata access at most; never document content, never production.
- **Certificate-based device identity** issued via MDM, presented in mTLS to the internal access proxy — a stolen password and even a stolen FIDO2 key are insufficient without an enrolled device.

### Per-request authorisation with purpose and context

Every document access decision evaluates:

| Signal | Example condition |
|---|---|
| Subject identity + role | `principal in Role::"compliance_officer"` |
| Tenant match | `resource.tenant == principal.tenant` |
| MFA strength | `context.mfa == "phishing_resistant"` for `RESTRICTED` |
| Device posture | `context.device.compliant == true` |
| Geography | `context.country in EU_COUNTRIES` for production personal data |
| Purpose | `context.purpose in ["review","audit_response"]` |
| Session age | `context.session_age < 4h` for privileged actions |
| Resource classification | `resource.classification != "PRIVILEGED" \|\| principal in resource.named_access` |
| Behavioural anomaly | `context.risk_score < threshold` |

Decisions are cached only for the exact same tuple and only for seconds — not for the session.

### Continuous verification

- Session risk is recomputed on: new IP, new device, geography change, elevated volume, EDR alert on the device, IdP risk-event, and time.
- Elevated risk → step-up authentication, or session termination for high-risk signals.
- Device falling out of compliance → active sessions revoked within minutes.

### Maturity roadmap (CISA ZTMM v2.0 pillars)

| Pillar | Target state | Phase |
|---|---|---|
| Identity | Phishing-resistant MFA, JIT privilege, continuous risk scoring | 1–2 |
| Devices | MDM enforcement, posture as a policy input, certificate identity | 1–2 |
| Networks | Micro-segmentation, mTLS everywhere, default-deny egress | 1–2 |
| Applications & workloads | Per-request authz, SPIFFE identities, mesh authz policy | 1–2 |
| Data | Classification-driven policy, per-tenant keys, DLP | 1–3 |
| **Cross-cutting: visibility & analytics** | Full decision logging, behavioural baselines, UEBA | 2–3 |
| **Cross-cutting: automation & orchestration** | Automated response, auto-revocation, policy-as-code CI | 2–3 |
| **Cross-cutting: governance** | Policy versioning, review cadence, control attestation | 1 |

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| PDP becomes a single point of failure | Total outage — every request depends on it | Sidecar/embedded policy evaluation with locally-cached, signed policy bundles; fail-closed for writes, fail-closed for `RESTRICTED` reads, documented degraded mode |
| Policy complexity outgrows comprehension | Unintended allows; nobody can reason about the policy set | Cedar's analysability; mandatory policy unit tests; a written policy-authoring standard; periodic policy review |
| Zero Trust theatre — mesh deployed but every service allowed to call every other | False assurance | Explicit authorisation policies required per service; deny-by-default in the mesh; automated call-graph conformance checks |
| Certificate/SVID rotation failure | Cascading service outage | SPIRE HA, rotation well before expiry, alerting on renewal failures, chaos test of rotation |
| Device posture signal unavailable (MDM outage) | Either lockout or fail-open | Documented decision: fail-closed for `RESTRICTED`/production, degraded-allow for low-sensitivity reads with alerting |
| Performance overhead of per-request authorisation and mTLS | Latency, cost, pressure to shortcut | Benchmark early; sidecar-local decisions; mesh at the data-plane proxy level; measure p99 |
| Users defeat friction (shared accounts, disabling MDM) | Control erosion | Monitor for it; make the compliant path fast; single sign-on everywhere so security is the low-friction option |

## Trade-offs

- **Full mesh mTLS (strong, ~5–15% resource overhead, operational learning curve) vs. TLS termination at ingress only.** **Recommendation: full mesh. The identity-based authorisation it enables is the core of the model, and Linkerd's overhead is modest.**
- **Centralised PDP (consistent, single point of failure, network latency per decision) vs. distributed policy evaluation with signed bundles (fast, resilient, potential staleness).** **Recommendation: distributed evaluation with centrally-authored, signed, versioned policy bundles pushed to sidecars — consistency of authorship with resilience of execution. Bundle staleness is bounded and alerted.**
- **Device trust for customer users (very strong, unacceptable friction for a B2B SaaS) vs. workforce only.** **Recommendation: workforce only; customers get risk-based signals and step-up, plus optional device-trust enforcement for tenants that request it.**
- **Fail-closed (secure, outage-prone) vs. fail-open (available, dangerous) on signal unavailability.** **Recommendation: fail-closed for writes, privileged actions and `RESTRICTED`/`PRIVILEGED` reads; fail-open with alerting for low-sensitivity reads. Document this decision explicitly — it will be asked about in every security review.**
- **Big-bang Zero Trust vs. incremental by data path.** **Recommendation: incremental, starting with the user→document path, which is where the catastrophic risk lives.**

## Design decisions

- **DD-12-01:** Zero Trust implemented as five independent enforcement points on the path to document plaintext: ingress authz, mesh identity authz, application authz, database RLS, KMS encryption-context key policy.
- **DD-12-02:** SPIFFE/SPIRE workload identities with ≤1-hour SVIDs; mTLS mandatory for all service-to-service traffic; mesh authorisation policies are deny-by-default and explicitly enumerate the allowed call graph.
- **DD-12-03:** Policy authored centrally in Cedar, version-controlled, unit-tested in CI, distributed as signed bundles evaluated locally by sidecars.
- **DD-12-04:** Device posture from MDM is a mandatory PDP input for workforce access; non-compliant devices cannot reach production or document content.
- **DD-12-05:** Session geography is a policy input; production personal-data access requires an EU-located session (enforcement point for doc 03).
- **DD-12-06:** Purpose is a required parameter on document access requests, logged and policy-evaluated.
- **DD-12-07:** Fail-closed for writes, privileged operations and `RESTRICTED`/`PRIVILEGED` reads; fail-open with alerting for low-sensitivity metadata reads. Documented and disclosed.
- **DD-12-08:** Continuous session re-evaluation with automatic revocation on device non-compliance, IdP risk events, or behavioural anomaly.
- **DD-12-09:** Maturity mapped and reported against CISA ZTMM v2.0 for customer assurance; target "Advanced" across all pillars by end of phase 3.

## References

- NIST SP 800-207 — Zero Trust Architecture (https://csrc.nist.gov/pubs/sp/800/207/final)
- NIST SP 1800-35 — Implementing a Zero Trust Architecture
- CISA Zero Trust Maturity Model v2.0 (April 2023)
- UK NCSC — Zero Trust Architecture Design Principles
- Commission Delegated Regulation (EU) 2024/1774 — access management, network segmentation, remote access
- Directive (EU) 2022/2555 (NIS2) Art. 21(2)(j) — continuous authentication
- SPIFFE/SPIRE specification (https://spiffe.io); Linkerd automatic mTLS documentation
- Cedar policy language and analysis tooling

## Confidence level

**High** — the PDP/PEP model, layered enforcement points, SPIFFE workload identity, and incremental adoption path. This is mainstream, well-documented architecture and it maps cleanly onto the regulatory requirements.

**Medium** — the real-world latency and operational cost of five enforcement layers at production scale in a small team, and how much device-trust friction customers will tolerate if we later offer it. Benchmark and pilot rather than assume.
