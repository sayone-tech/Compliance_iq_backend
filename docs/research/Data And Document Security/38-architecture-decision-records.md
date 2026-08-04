# 38 — Architecture Decision Records

The significant, hard-to-reverse decisions, in ADR form. The full list of ~130 design decisions (`DD-nn-nn`) lives in the topic documents; this file captures the ones where the alternative was genuinely viable and the choice shapes everything downstream.

---

## ADR-001 — AWS EU regions as the target platform, with engineered portability

**Status:** Accepted · **Date:** 2026-08-03 · **Deciders:** CTO, Head of Security

**Context.** Customers are EU-regulated CASPs with strong sovereignty expectations. Options: AWS/Azure/GCP EU regions; an EU-sovereign provider (OVHcloud, Scaleway, IONOS, StackIT); or a hyperscaler sovereign offering (AWS European Sovereign Cloud, Microsoft EU Data Boundary). US CLOUD Act exposure is the objection sophisticated buyers raise.

**Decision.** AWS `eu-central-1` primary, `eu-north-1` DR. Portability preserved architecturally: Kubernetes, PostgreSQL wire protocol, S3 API, PKCS#11/KMIP abstraction over the KMS, Terraform modules with the provider isolated. EU-sovereign deployment offered as a paid Tier 3 option.

**Consequences.** *Positive:* mature managed services reduce operational risk (itself a DORA resilience benefit); deep KMS/HSM/Object Lock/enclave capability; hiring pool; speed. *Negative:* CLOUD Act narrative must be answered by key custody (ADR-005) rather than by geography; some lock-in accepted (Aurora, KMS, Nitro). *Mitigation:* portability constraints enforced at design review; annually tested exit plan; concentration analysis published.

**Alternatives rejected.** EU-sovereign provider as primary — thinner managed-service catalogue pushes patching, HA and backup operations onto a small team, which is a *net* resilience risk under DORA. Multi-cloud — see ADR-002.

---

## ADR-002 — Single cloud provider; multi-cloud explicitly rejected

**Status:** Accepted · **Date:** 2026-08-03 · **Deciders:** CTO

**Context.** DORA Art. 29 requires concentration risk assessment. Customers will ask about single-provider dependency.

**Decision.** Single cloud (AWS). Concentration risk addressed through documented analysis, engineered portability, an annually tested exit plan, and honest disclosure — not through active multi-cloud.

**Consequences.** *Positive:* one consistent control model; every control implemented once and implemented well; far lower operational surface. *Negative:* a genuine AWS-wide failure has no immediate alternative; some buyers may push back. *Mitigation:* multi-AZ and multi-region within AWS; four degraded modes including an evidence-only read path; portability keeps migration feasible in months rather than years.

**Rationale for rejection of multi-cloud.** Running the same security controls consistently across two providers roughly doubles operational surface and, in practice, degrades every control to the weaker provider's capability. Inconsistency in tenant isolation or key management is a larger risk than provider outage. This is a defensible and commonly accepted position with EU financial supervisors when documented.

---

## ADR-003 — Per-tenant customer master keys with encryption-context binding

**Status:** Accepted · **Date:** 2026-08-03 · **Deciders:** Head of Security, CTO

**Context.** Tenant isolation is the catastrophic risk (R-01). Options: a single platform key; a shared key with encryption context; per-tenant CMKs; per-document keys.

**Decision.** Per-tenant KMS CMK for all tenants including the lowest tier, with per-document DEKs for `RESTRICTED` and `PRIVILEGED` classes. Every operation binds `tenant_id` in the KMS encryption context, enforced by the key policy.

**Consequences.** *Positive:* a data-mixing bug fails closed rather than leaking; crypto-shredding becomes available for erasure; upgrading a tenant to customer-managed keys is a key migration rather than an architectural change; per-tenant blast radius. *Negative:* ~€1/key/month plus request costs; KMS request volume needs caching; key count limits to monitor at scale. *Cost at 1,000 tenants:* roughly €12k/year — trivial against the risk.

---

## ADR-004 — Managed frontier model (Bedrock) for production inference, not self-hosted

**Status:** Accepted · **Date:** 2026-08-03 · **Deciders:** CTO, Head of Product

**Context.** Assessment quality is the product. Options: Amazon Bedrock (Claude) in `eu-central-1`; direct Anthropic API; self-hosted open-weight model in-region.

**Decision.** Amazon Bedrock in `eu-central-1` with cross-region inference disabled. No training on inputs/outputs; no provider-side retention. A self-hosted open-weight model is maintained as a degraded-mode fallback and as the option for Tier 3 sovereign customers who accept the quality trade-off.

**Consequences.** *Positive:* strongest available residency position; AWS is an existing sub-processor so no new contractual relationship; integrated IAM, KMS and CloudTrail; best-in-class quality. *Negative:* dependency on a provider's terms; concentration risk under DORA; token cost. *Mitigation:* fallback provider exercised quarterly (DD-05-09); contractual change-notice; annual review.

**Alternative rejected.** Self-hosted as primary — a materially weaker model produces worse compliance advice, which is a safety issue in this domain, not merely a quality one.

---

## ADR-005 — Three key-custody tiers; key custody is the sovereignty control

**Status:** Accepted · **Date:** 2026-08-03 · **Deciders:** CEO, CTO, Head of Security

**Context.** "Where is the data?" is the wrong question; "who can produce plaintext under legal compulsion?" is the right one. This is also the answer to both the CLOUD Act objection and the EU→India transfer problem.

**Decision.** Three published tiers: T1 platform-managed; T2 customer-managed via cross-account KMS grant; T3 hold-your-own-key via KMS External Key Store. Fail closed on key unavailability — no fallback key exists anywhere. T2/T3 availability risk is contractually acknowledged by the customer with a separate signature.

**Consequences.** *Positive:* a complete technical answer to third-country access concerns; a genuine commercial differentiator; strengthens the transfer impact assessment for India (ADR-006). *Negative:* customers can lock themselves out permanently; T3 requires customer HSM operations maturity; XKS latency; not all AWS services support XKS-backed keys. *Mitigation:* canary key-health monitoring; key-degraded mode; T3 piloted with one design partner before general availability; service compatibility verified before selling T3.

---

## ADR-006 — Zero standing production access; India development with no production data path

**Status:** Accepted · **Date:** 2026-08-03 · **Deciders:** CEO, CTO, DPO

**Context.** Development in India, production serving EU customers. India has no adequacy decision. Remote access is a restricted transfer. SCCs alone are insufficient for confidential regulated financial data given Indian lawful-access powers.

**Decision.** Three zones: Zone D (India, synthetic data only), Zone S (EU staging, synthetic/anonymised), Zone P (EU production, **no standing human access at all**). Break-glass only, dual-approved by two EU-resident approvers, through an EU-hosted VDI with egress disabled, session-recorded, ≤4 hours, auto-revoked. SCCs Module 3 plus a documented TIA plus technical supplementary measures (EU-held keys the Indian entity cannot reach).

**Consequences.** *Positive:* the strongest defensible transfer position; removes the dominant insider and cross-border risks; survives customer due diligence. *Negative:* slows some production incident resolution; requires investment in redacted observability and synthetic reproduction; requires EU-resident production on-call, which is a real hiring cost and lead-time item. *Mitigation:* fund the observability work that makes zero-access viable; hire or contract EU on-call before the first enterprise customer.

**This decision constrains the operating model more than any other in this set. It should be revisited only with legal advice, never for convenience.**

---

## ADR-007 — Immutable evidence via Object Lock COMPLIANCE + hash chain + eIDAS qualified timestamps

**Status:** Accepted · **Date:** 2026-08-03 · **Deciders:** CTO, Head of Product, Compliance Lead

**Context.** The product's core promise is evidence a regulator will accept. Options: application-level immutability flags; a ledger database (Amazon QLDB reached end of support in 2025); blockchain anchoring; S3 Object Lock with cryptographic anchoring.

**Decision.** Self-contained evidence packages (manifest + content + Ed25519 signature + RFC 3161 qualified timestamp), stored in S3 with Object Lock in **COMPLIANCE mode**, per-tenant hash chain, daily Merkle root timestamped by an **EU QTSP on the EU Trusted List**, published to a customer-visible append-only feed. Open-source `evidence-verify` CLI shipped.

**Consequences.** *Positive:* eIDAS Art. 41 gives a legal presumption of time accuracy and data integrity — a technical claim becomes a legal one; verification requires no access to our systems; independent third-party anchoring; the highest value-per-euro control in the architecture. *Negative:* COMPLIANCE mode mistakes are permanent; QTSP is an external dependency requiring long-term validation support; storage cost over 7 years. *Mitigation:* GOVERNANCE-mode staging and seal-preview before COMPLIANCE locking; retention derived only from the policy engine; LTV data stored in the package; Glacier lifecycle preserving the lock.

**Alternative rejected.** Blockchain anchoring — gives a technical presumption where eIDAS gives a *legal* one, adds cost and volatility, and creates an awkward "which chain" conversation with crypto-firm customers. Optional secondary anchor only if requested.

---

## ADR-008 — Five independent authorisation enforcement points on the document path

**Status:** Accepted · **Date:** 2026-08-03 · **Deciders:** Head of Security, Engineering Lead

**Context.** Cross-tenant disclosure is the risk that ends the company. Single-layer enforcement, however well written, will eventually have a bug.

**Decision.** Five independent enforcement points: (1) Cedar policy sidecar at the API, (2) service mesh mTLS identity authorisation, (3) application repository tenant scoping, (4) forced PostgreSQL row-level security, (5) KMS key policy requiring a matching `tenant_id` encryption context. Each is independently sufficient to prevent cross-tenant disclosure.

**Consequences.** *Positive:* no single bug produces a breach; the design is explainable to auditors and buyers in one diagram. *Negative:* per-request latency across five layers; five places to keep consistent; RLS adds query-planning complexity. *Mitigation:* sidecar-local policy evaluation with signed bundles; benchmark p99 authorisation latency under 10ms; cross-tenant negative test matrix as a blocking CI gate.

---

## ADR-009 — Governed AI-assisted development rather than prohibition

**Status:** Accepted · **Date:** 2026-08-03 · **Deciders:** CTO, Head of Security

**Context.** Claude Code is used by engineers in India. The CLAUDE.md rule "No Customer Documents in AI Prompts" read literally would forbid the product's core function.

**Decision.** Two distinct surfaces, governed separately. **AI-in-development:** permitted in Zone D against synthetic data only, with MDM-deployed managed settings (deny rules for secrets and production paths, bypass mode disabled), enforcement verified by test, and paste-blocking DLP for customer-data patterns. **AI-in-product:** customer content may enter inference only through the governed EU-resident Bedrock path. The policy wording is amended to state this precisely.

**Consequences.** *Positive:* retains a real productivity advantage; avoids shadow usage on personal accounts, which is strictly worse; the synthetic-only Zone D means even total tool compromise yields no customer data. *Negative:* requires MDM enforcement and ongoing verification as tool settings evolve; requires training and cultural reinforcement. *Mitigation:* managed settings enforcement tested after every rollout; AI-generated code labelled in commit trailers and subject to identical review and CI gates.

---

## ADR-010 — Warm standby DR with manual failover approval

**Status:** Accepted · **Date:** 2026-08-03 · **Deciders:** CTO, SRE Lead

**Context.** DORA Art. 12(3) requires geographically separated recovery. Options: backup-and-restore (cheap, RTO in days); warm standby; active-active.

**Decision.** Warm standby in `eu-north-1` with Aurora Global Database and S3 Cross-Region Replication. Failover requires human dual approval against pre-defined criteria with a 15-minute decision SLA; all preparatory steps automated. Read paths recover before write paths (T1 = document and evidence retrieval).

**Consequences.** *Positive:* 15-minute RPO for T1 makes the evidence-retention promise credible; avoids split-brain; ~35–45% of primary infrastructure cost rather than ~200% for active-active. *Negative:* Aurora Global Database is the largest DR line item; manual approval adds minutes to RTO. *Mitigation:* semi-annual full failover *and failback* testing; RTO/RPO measured twice before any customer SLA is contracted.

**Alternative rejected.** Active-active multi-region PostgreSQL — introduces write-consistency risk that exceeds its availability benefit for this workload.

---

## ADR-011 — Deterministic citation verification as a blocking gate on AI assessments

**Status:** Accepted · **Date:** 2026-08-03 · **Deciders:** Head of Product, Head of Security

**Context.** A hallucinated regulatory citation reaching a customer's audit file is among the most damaging failure modes (R-07). Options: model self-evaluation; LLM-as-judge; human review only; deterministic verification.

**Decision.** Every cited span must exist in the source document at the stated offset, verified deterministically in code. Failure blocks the assessment. This is in addition to — not instead of — mandatory named-human approval.

**Consequences.** *Positive:* eliminates the most dangerous hallucination class outright, without relying on a model to check a model; cheap and fast; explainable to auditors. *Negative:* constrains output format (citations must carry offsets); rejects some valid paraphrase-style outputs. *Mitigation:* prompt engineering to always emit verifiable spans; rejected assessments are retried and logged for evaluation.

---

## ADR-012 — Retention policy engine as the single source of truth

**Status:** Accepted · **Date:** 2026-08-03 · **Deciders:** Compliance Lead, CTO

**Context.** MiCA Art. 68(9) requires 5–7 years. AMLR requires 5 years post-relationship. GDPR Art. 5(1)(e) requires retention to *end* and Art. 17 grants erasure. These conflict, and ad hoc resolution produces both data-subject complaints and records-integrity findings.

**Decision.** A retention policy engine holds per-record-class objects (`min_retention`, `max_retention`, legal basis, erasability, legal-hold capability). It is the only source for Object Lock retain-until dates, backup expiry, and deletion scheduling. Erasure conflicts resolve per class: legal-obligation refusal under Art. 17(3)(b), full deletion saga, or crypto-shredding. Object Lock COMPLIANCE is applied only to classes with an identified legal retention obligation; erasable classes live in separate buckets.

**Consequences.** *Positive:* deterministic, auditable, defensible resolution of the central regulatory tension; retention decisions are reviewable as configuration rather than as code. *Negative:* the engine must exist before the first document is stored; misconfiguration has permanent consequences. *Mitigation:* staged rollout via GOVERNANCE mode; quarterly retention conformance report; automatic expiry job emits its own evidence record.

---

## ADR-013 — Detections and policies as code; no console-authored security configuration

**Status:** Accepted · **Date:** 2026-08-03 · **Deciders:** Head of Security, Platform Lead

**Context.** Security rules edited in consoles drift, break silently, and cannot be audited or tested.

**Decision.** All detection rules, authorisation policies, IaC, admission policies and pipeline definitions are version-controlled, peer-reviewed, unit-tested in CI, and deployed through the pipeline. No manual production changes; drift detection alerts and GitOps reverts.

**Consequences.** *Positive:* every security control change is reviewable, testable and auditable — which is also DORA change-management evidence; rules can be tested before deployment. *Negative:* slower iteration on detection tuning; requires discipline when an urgent rule change is needed. *Mitigation:* fast-path review for detection tuning; emergency changes use a faster approval path but never bypass review entirely.

---

## Decision log summary

| ADR | Decision | Reversibility | Primary risk addressed |
|---|---|---|---|
| 001 | AWS EU with portability | Medium (months) | Residency, resilience |
| 002 | Single cloud | Medium | Operational consistency |
| 003 | Per-tenant CMKs | **Low** (data migration) | R-01 cross-tenant |
| 004 | Managed frontier model | High | Assessment quality |
| 005 | Three key-custody tiers | Medium | Sovereignty, R-04 |
| 006 | Zero standing access / three zones | Medium (operating model) | R-03, R-04 |
| 007 | Object Lock + QTSP evidence | **Very low** (permanent) | R-14, evidence credibility |
| 008 | Five enforcement points | Medium | R-01 |
| 009 | Governed AI development | High | R-04 |
| 010 | Warm standby, manual failover | Medium | R-06, R-19 |
| 011 | Deterministic citation verification | High | R-07 |
| 012 | Retention policy engine | **Low** | R-21, erasure conflict |
| 013 | Everything as code | High | R-38, auditability |

Decisions marked **low** or **very low** reversibility deserve the most scrutiny before implementation — particularly ADR-003 and ADR-007, where a mistake is permanent.
