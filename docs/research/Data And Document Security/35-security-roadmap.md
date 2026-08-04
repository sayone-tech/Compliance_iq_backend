# 35 — Security Roadmap

Four phases. Phase boundaries are gated by capability, not by calendar — the durations are estimates for a team of roughly 6–10 engineers plus a security lead, and should be re-baselined against actual headcount.

---

## Phase 0 — Foundation (weeks 1–6)
**Goal: guardrails exist before any customer data can be created.**
**Exit gate: a developer cannot create a resource outside the EU, cannot commit a secret, and cannot access a production credential — because the system prevents it, not because policy says so.**

| Workstream | Deliverables | Doc |
|---|---|---|
| Cloud foundation | AWS Organizations; 10-account topology; SCPs (EU-only regions, no IAM access keys, no disabling security services); RCPs | 30, 11 |
| Logging | CloudTrail all accounts/regions → `log-archive` with Object Lock; Config; GuardDuty; Security Hub | 14, 22 |
| Identity | IdP selected and deployed; FIDO2 enrolment for all staff; IAM Identity Center; conditional access incl. EU-location policy for prod | 10 |
| Cryptography | KMS hierarchy and key policy templates; cryptographic control policy document; crypto module skeleton with mandatory AAD | 07, 08 |
| Development | Repo with branch protection, signed commits, CODEOWNERS, secret scanning + push protection; OIDC federation for CI; synthetic data fixture factory | 04, 09, 19 |
| AI governance | Managed Claude Code settings deployed via MDM and **enforcement verified by test**; AI usage policy | 05 |
| Governance | Obligation register v1; accountable executive named; DPO appointed; risk register opened | 01 |
| Legal | SCCs Module 3 drafted with the Indian entity; TIA started | 03 |

**Key risk in this phase:** pressure to skip guardrails "just to get moving". Every day of delay here saves a week later.

---

## Phase 1 — Secure MVP (weeks 7–20)
**Goal: the platform can hold real customer data safely for a design-partner customer.**
**Exit gate: the go/no-go checklist in doc 34 §11 is fully satisfied.**

| Workstream | Deliverables | Doc |
|---|---|---|
| **Tenant isolation** | Repository pattern; forced PostgreSQL RLS; per-tenant CMK with `tenant_id` encryption context; cross-tenant negative test matrix as a blocking CI gate | 06, 10 |
| Document pipeline | Quarantine-scan-promote with multi-engine AV, fail-closed; sandboxed processing account (no credentials, no egress); five-bucket topology; derivative registry | 13, 06 |
| Access | Cedar policy engine with signed bundles; per-request authorisation; step-up auth; zero standing production access with break-glass workflow | 10, 12 |
| Audit | Canonical audit event schema; redaction by construction with SAST enforcement; hash-chained writes to Object Lock storage; coverage tests per endpoint | 14 |
| Evidence | Evidence package format; Ed25519 signing; daily Merkle root; **QTSP qualified timestamps**; retention policy engine | 15 |
| AI | Bedrock EU-only inference; untrusted-data delimiting; schema-constrained output; **deterministic citation verification**; named human approval workflow; inference audit records | 05 |
| Network | Three-tier VPC; VPC endpoints with policies; default-deny egress (staged rollout); WAF (count → block); Session Manager only, no bastions | 11 |
| Supply chain | SLSA L3 provenance; Sigstore signing; Kyverno admission verification; CycloneDX SBOM into Dependency-Track; dependency pinning with cooldown | 18, 19 |
| Backup | Backup account isolation; Vault Lock (governance → compliance); **daily automated restore verification** | 21 |
| Detection | 14 priority detections as code with tests; honeytokens seeded; log-source heartbeats; MDR engaged | 22 |
| Insider | Separation-of-duties capability matrix; dual authorisation on irreversible actions; session recording for break-glass; offboarding automation | 17 |
| Legal/assurance | DPIA complete; SCCs executed; TIA documented; sub-processor list published; penetration test + remediation | 01, 03 |

**Phase 1 is where the product's regulatory credibility is built.** Everything here is mandatory before real data.

---

## Phase 2 — Enterprise readiness (months 6–12)
**Goal: pass a tier-1 CASP's security and DORA due diligence without a six-month remediation cycle.**
**Exit gate: a signed enterprise contract with a full DORA Art. 30(3) addendum, closed on our paper, with no open Critical or High findings.**

| Workstream | Deliverables | Doc |
|---|---|---|
| Resilience | Warm standby in `eu-north-1`; Aurora Global Database; S3 CRR with RTC; **first full regional failover and failback test**; four degraded modes implemented | 16 |
| Backup | Tenant-granular point-in-time restore; ransomware-scenario exercise; crisis communication tabletop | 21, 16 |
| Keys | **Tier 2 customer-managed keys** (cross-account grants); canary key-health monitoring; key-degraded mode | 20, 08 |
| Data protection | **Nitro Enclave** for key-broker and document decryption; entity pseudonymisation before inference; steganographic watermarking | 07, 05, 23 |
| Product security features | Customer-facing exportable tenant audit trail; time-boxed scoped `auditor` role; operator access visible in tenant logs; `evidence-verify` CLI open-sourced | 14, 10, 17, 15 |
| Identity | Customer enterprise SSO (SAML/OIDC) + SCIM; quarterly access recertification | 10 |
| AI | Model registry with golden-set evaluation gate; fallback inference provider exercised quarterly; AI Act classification with external legal opinion | 05 |
| Assurance | **ISO/IEC 27001 certification**; SOC 2 Type II observation window started; security whitepaper and full customer security pack | 01 |
| Testing | Quarterly purple-team exercises; second penetration test; DR test evidence pack for customers | 24, 04 |
| Governance | DORA register-of-information extract feature; machine-readable residency/sub-processor attestation API | 01, 02, 18 |
| Compliance ops | Incident classification engine; 2-hour customer notification SLA operational and drilled | 22 |

---

## Phase 3 — Scale and sovereignty (months 12–24)
**Goal: serve the most demanding buyers and stay ahead of the regulatory curve.**

| Workstream | Deliverables | Doc |
|---|---|---|
| Sovereignty | **Tier 3 HYOK via KMS External Key Store**, piloted with one design-partner customer before GA; EU-sovereign deployment option evaluated and costed | 20, 02 |
| Cryptography | Hybrid post-quantum in transit (X25519MLKEM768); dual signatures (Ed25519 + ML-DSA) on long-lived evidence; PQC migration status tracked in the key register | 07, 08 |
| Insider | Customer-approved access (lockbox) for T2/T3; broader UEBA once the security team can triage it | 17 |
| Zero Trust | CISA ZTMM "Advanced" across all pillars; continuous session re-evaluation with automated revocation | 12 |
| Assurance | SOC 2 Type II report issued; ISO/IEC 27701 for privacy; EU Cloud Code of Conduct adherence; participation in customer TLPT / TIBER-EU exercises | 01 |
| Programme | Private bug bounty; detection coverage mapped to ATT&CK with tracked gaps; annual T3 threat model refresh | 04, 22, 24 |
| Regulatory | AMLR readiness (applicable July 2027); CRA readiness if installable components ship (reporting obligations from September 2026); AI Act re-classification on material feature change | 01 |

---

## Cross-cutting continuous activities

| Activity | Cadence | Owner |
|---|---|---|
| Obligation register review | Quarterly | Compliance Lead + Head of Security |
| Risk register review | Monthly; board-level quarterly | Head of Security |
| Access recertification (privileged) | Quarterly | Head of Security |
| Vulnerability SLA reporting | Monthly | Platform Lead |
| Purple team | Quarterly | Security |
| Penetration test | Annual | External |
| DR full failover + failback | Semi-annual | SRE |
| Restore verification | **Daily, automated** | Automated |
| Backup ransomware scenario | Annual | SRE + Security |
| Crisis communication tabletop | Annual | Executive |
| Security awareness training | Annual + role-specific | People + Security |
| Threat model T3 refresh | Annual | Security + Engineering |
| Sub-processor reconciliation | Quarterly | Compliance |
| TIA review | Annual and on legal change | DPO + Legal |
| Government access playbook test | Annual, both entities | Legal + Security |

---

## Dependency-critical items (long lead time — start early)

| Item | Lead time | Start by |
|---|---|---|
| EU-resident production on-call hiring | 3–6 months | Phase 0 |
| ISO/IEC 27001 certification | 6–9 months | Phase 1 |
| SOC 2 Type II (6-month observation) | 9–12 months | Phase 1 |
| QTSP selection and integration | 6–8 weeks | Phase 1 |
| Legal opinions (NIS2 scope, AI Act, TIA) | 6–10 weeks | Phase 0 |
| MDR provider selection and onboarding | 6–8 weeks | Phase 1 |
| Penetration test booking | 4–6 weeks | Phase 1 |

## Budget shape (indicative, annual, once at Phase 2)

| Category | Indicative range | Notes |
|---|---|---|
| Cloud infrastructure (prod + DR + non-prod) | €120k–250k | Aurora Global DB and evidence storage dominate |
| Security tooling (SIEM, EDR, SAST/SCA, reachability, MDM) | €50k–100k | Reachability tooling pays for itself in engineer time |
| MDR / 24-7 triage | €40k–80k | Scoped to telemetry only |
| Certifications (ISO 27001 + SOC 2, first year) | €60k–120k | Higher in year one |
| Penetration testing | €25k–45k | Annual, application + infrastructure + multi-tenancy |
| QTSP timestamping | €2k–10k | Daily Merkle anchoring keeps this trivial |
| Legal (DPIA, TIA, SCCs, opinions) | €30k–60k | Front-loaded in Phase 0/1 |

Treat these as order-of-magnitude planning figures to be replaced with quotes, not as estimates to budget against directly.
