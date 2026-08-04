# Executive Summary

> **Baseline:** `docs/requirement-specification/PRD.md` (ComplianceIQ PRD v4.0) is the sole source of truth for this research set. Where research and PRD disagree, the PRD wins. Classification used throughout:
> **[PRD REQUIRED]** — explicitly required by the PRD (section or requirement ID cited) · **[PROPOSED]** — implementation recommendation, reasonably necessary to deliver a PRD requirement but not selected by the PRD · **[OPEN]** — stakeholder or legal decision required · **[FUTURE]** — outside the MVP baseline, see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

**Subject:** Data and document security for the ComplianceIQ MVP — a two-application, multi-tenant compliance testing platform for EU-licensed CASPs, delivered by SayOne, deployed on AWS in an EU data centre on an account owned solely by the Client.
**Status:** Research revised against PRD v4.0. **Nothing here is an approved decision unless the PRD itself states it.**

---

## 0. Confirmed scope of this research set

The top level of this folder covers exactly the confirmed security scope for the MVP:

EU-only storage of client data · AWS as the selected cloud provider · a Client-owned AWS account · AES-256 at rest and TLS 1.3 in transit · per-tenant encryption keys · strong multi-tenant isolation · immutable audit logging · non-deletable evidence and signed-off records · MFA and least-privilege role enforcement · secure document upload, malware inspection and sandboxed parsing · secure backups and tested recovery (**with SLA, RTO and RPO values remaining proposals only**) · human approval of AI-generated WSP mappings · prompt-injection and hallucination controls specific to WSP mapping · secure SDLC, secrets management, vulnerability scanning and supply-chain controls · EU residency checks for AI inference over customer documents · incident monitoring and customer notification appropriate to DORA support obligations.

Material outside that list was **moved, not deleted**:

| Folder | What is in it |
|---|---|
| [`supporting-topics/`](supporting-topics/) | MVP-relevant depth outside the confirmed list — network security, Zero Trust enforcement, insider threat, data loss prevention, threat-modelling method, and the conditional cross-border analysis. Still referenced by the control matrix, threat model and risk register |
| [`future-scope/`](future-scope/) | Nothing in the MVP — customer-managed encryption / HYOK, and the full deferred list |

See the [README](README.md) for the scope-item-to-document mapping.

## 1. What the PRD fixes

These are not recommendations. They are the security baseline the MVP must meet.

| Requirement | PRD reference |
|---|---|
| Complete data isolation between firms — multi-tenant from day one | NFR-01, §2 |
| AES-256 at rest, TLS 1.3 in transit, **a distinct encryption key per firm** | NFR-02, §2 |
| All client data in EU data centres | NFR-03 |
| **AWS, EU-resident data centre, account owned solely by the Client** | TI-01 (resolved) |
| Immutable audit log — no modify or delete capability for anyone, including SayOne administrators | NFR-04, FR-13, §2 |
| Minimum six-year retention; test results, findings, evidence, remediation evidence, reports and audit logs **cannot be deleted by any user including administrators** | NFR-07, §2 |
| Signed-off results are amendable but never editable; issued reports are permanently archived exactly as issued; every WSP version and mapping change is kept permanently | FR-27, FR-61, FR-37, FR-21b, FR-21c |
| GDPR processor obligations under a DPA | NFR-06 |
| Eight fixed system roles; firm role names map to system roles; invitation-only accounts; phone-based second factor; minimum two Firm Super Admins; deactivate-never-delete | §3, FR-09 → FR-15 |
| Exactly the FR-24 evidence file types; maximum size is Portal configuration, changeable without a code release | FR-24, NFR-11 |
| AI-assisted WSP-to-rule mapping is **advisory**; a compliance officer confirms or adjusts; two independent senior approvers, never the policy author; reversal follows the same process | FR-31, FR-32, FR-33, §6.3 |
| **Minimum 85% verified mapping accuracy against pre-defined verification text vectors at UAT** — tuning inside the fixed fee | §6.2 (accepted 3 Jul 2026) |
| Availability **target** 99.5%; dashboard within two seconds; up to 100 concurrent users per firm | NFR-08, NFR-05 |
| ISO 27001 and SOC 2 Type II are roadmap items; **timeline to be agreed with the Client** | NFR-09 |

## 2. The five things that determine whether this works

**1. Non-deletability is the hardest constraint in the architecture, and it is a PRD requirement.**
NFR-07 and §2 say records cannot be deleted by anyone, including administrators. NFR-04 says the same of the audit log. That is an *absence* of capability, and absences are only credible if they are structurally impossible: write-once storage in a compliance-grade mode, no deletion API for protected classes, and — critically — **key destruction blocked as a route around it**, because deleting a per-firm key would make six-year records unreadable just as effectively as deleting them. This research therefore **does not adopt crypto-shredding, deletion sagas or soft-delete grace periods**. (ADR-004, ADR-005, ADR-012 · `immutable-evidence-retention`, `key-management`)

**2. Tenant isolation must survive a single bug.**
NFR-01 is the failure mode that ends the engagement. The proposal is layered enforcement on the path to evidence plaintext — repository scoping, forced row-level security, per-firm key with a firm-bound encryption context, per-request authorisation, and a cross-firm negative test matrix (every system role × every action) as a **blocking CI gate**. Any one layer alone prevents cross-firm disclosure; the redundancy is deliberate. **[PROPOSED]** implementing **[PRD REQUIRED]** NFR-01/NFR-02. (ADR-003, ADR-010 · `document-confidentiality`, `identity-and-access-management`, `zero-trust-architecture`)

**3. The AI feature is one feature, it is advisory, and it carries a contractual accuracy number.**
The PRD contains exactly one AI capability: AI-assisted mapping of a firm's WSP to Requirement IDs (§6.2). It suggests; a compliance officer decides; two senior people approve. The platform does **not** make compliance assessments, automated compliance decisions or regulator-ready AI conclusions — no PRD text supports that framing. The 85% UAT bar is a commitment, not a stretch goal, which means an evaluation harness against the agreed verification vectors must exist *before* UAT and must gate any prompt or model change. Prompt injection is treated as a live threat because uploaded WSPs are untrusted input. (ADR-007, ADR-009 · `ai-governance`)

**4. Where delivery happens is unresolved, and the safe engineering position costs little now and a lot later.**
The PRD states where *data* lives (NFR-03, TI-01). It does not state where development, support or production administration is performed. Until the Client and counsel settle that, the position taken here is to build so that **no production personal data is reachable from outside the EU/EEA at all** — synthetic data only outside production, zero standing human access to production, break-glass dual-approved and session-recorded. A transfer that cannot happen needs no transfer analysis. **[PROPOSED]**, with the underlying question **[OPEN — LEGAL]** (`open-questions`, L-1/L-2). (ADR-011 · `cross-border-data-processing`)

**5. Nothing about technology stack, region, recovery targets or certification dates has been decided.**
The PRD fixes the provider (AWS), the residency (EU), and the account ownership (Client). It fixes nothing else. This research therefore names **no region, no compute platform, no database engine, no service mesh, no authorisation engine, no AI provider or model, and no recovery time or recovery point figure.** Each is presented as selection criteria plus an open decision. (`reference-cloud-architecture`, `disaster-recovery`, `architecture-decision-records`)

## 3. Regulatory position

| Regime | Position for this MVP | Consequence |
|---|---|---|
| **GDPR** | **Binds the platform directly** as processor, under a DPA (NFR-06) | Data protection impact assessment; sub-processor disclosure; processor security obligations. **The Art. 17 erasure right versus the PRD's non-deletability rule is a genuine unresolved conflict** — see §7 |
| **MiCA** (EU 2023/1114) | **Customer-domain**, principal. The product exists to serve it | Evidence integrity and retention become part of the customer's supervisory file |
| **DORA** (EU 2022/2554) | **Customer-domain**, principal. May reach the platform through customer contract terms | Delegated Reg. (EU) 2024/1774 is used as a **design reference**, not as an assumed obligation. **No assumption is made that every customer designates ComplianceIQ as supporting a critical or important function** |
| **NIS2, CRA, AI Act, AMLR, TFR, eIDAS 2, EU Data Act** | **Adjacent / conditional.** None is confirmed applicable by the PRD | Mentioned only where genuinely relevant, always marked as requiring legal confirmation. **None drives MVP architecture or scope without Client approval** |

Applicability determinations for NIS2, the AI Act and CRA are **[OPEN — LEGAL]** (`open-questions`, L-5/L-6/L-7). Assuming a regime applies when it does not adds unbudgeted scope to a fixed-price contract (CC-04).

## 4. Architecture in brief — technology-neutral

Multi-account topology inside the **Client-owned AWS organisation**, with organisation-wide guardrails denying non-EU regions, long-lived access keys and the disabling of audit or threat-detection services. A dedicated write-only log archive with write-once retention and deletion denied to every principal. A separate no-credential, no-egress account for parsing untrusted uploads. Envelope encryption — per-object data key under a per-firm key under a managed key service in the selected EU region — with the firm identifier bound into the encryption context so a mis-scoped read fails at the cryptographic layer, not just the application layer. Evidence is uploaded through quarantine-scan-promote and served by default as a watermarked, server-side-rendered preview rather than a raw download.

**Region, compute platform, database engine, mesh, policy engine and AI provider are deliberately unselected** — `reference-cloud-architecture` lists the criteria for each. Portability is maintained as a design discipline so those choices stay reversible.

## 5. Top residual risks

From `risk-register` (residual = with the `security-control-matrix` controls implemented; 1–5 likelihood × impact):

| Risk | Residual | Why it stays elevated |
|---|---|---|
| Cross-firm data disclosure (breaches NFR-01) | 10 | Catastrophic impact; layering reduces likelihood, not consequence |
| Prompt injection in an uploaded WSP conceals a compliance gap | 9 | No complete technical defence exists. Mitigated in depth by the PRD's own FR-31 confirmation and FR-32 two-approver rules |
| Malicious or coerced insider exfiltrates firm evidence | 9 | Crypto-sector staff are a plausible target |
| A firm user fabricates or backdates evidence | 9 | Addressed by immutability and the approver-exclusion rules, not eliminated |
| Mapping accuracy falls below the 85% commitment after a change | 8 | Contractual exposure; needs the harness as a promotion gate |
| Compromised upstream dependency | 8 | Outside our control by definition |
| Ransomware attempting to destroy backups | 8 | Immutable copies make loss unlikely; recovery *time* is the residual |
| Records destroyed before six years by deletion, key destruction or misconfiguration | 8 | Directly breaches NFR-07 |
| Unresolved delivery topology leaves an unlawful access path live | 8 | Depends on an unanswered question, not on a control |

Full register: `risk-register`. Full threat model with attack trees: `threat-model`.

## 6. What must be true before real client data

`deployment-recommendations` §11 lists the full go/no-go set. The four most often skipped:

1. **Cross-firm negative test matrix passing in CI** — every system role × every action, no skipped tests.
2. **Negative tests proving protected records cannot be deleted or modified by any principal**, and that a per-firm key cannot be deleted while records are inside retention.
3. **A restore actually performed** from an immutable copy, with measured timing, including decryption with the correct firm key.
4. **Mapping accuracy measured at or above 85%** against the agreed verification vectors — measured, not asserted.

## 7. What needs a decision, and from whom

`open-questions` holds the full list. The ones that block work:

| # | Question | Owner |
|---|---|---|
| P-1 | Which EU region? Nothing else can be built until this is recorded | Client |
| P-2 | How is infrastructure provisioned into and handed over inside the Client-owned AWS account (TI-01)? Who holds root and break-glass custody? | Client |
| L-1 | Where will development, support and production administration be performed? | Client |
| L-3 | **How do GDPR erasure requests interact with the PRD's non-deletability rule?** (§2, NFR-07 vs GDPR Art. 17) | Client + counsel |
| A-5 | How much firm data may the Platform Admin Portal team see? (SA-06/SA-08 — an authorisation boundary, expensive to build twice) | Client |
| A-6 | Remediation Owner scope — FR-52 versus GAP-07, a contradiction **the PRD itself flags** | Client |
| P-5 | What concrete second factor satisfies FR-11's "verification step on their phone"? | Client |
| P-6 | Which AI inference provider and model, with what residency, no-training and no-retention terms? | Client |
| P-9 | Who is the named owner accountable for platform security? | Client |
| A-1 | TI-02: is 99.5% sufficient, or is 99.9% required? Determines the entire recovery investment | Client |

**None of these is answered by a default in this research set.** Where an interim engineering position is given, it is explicitly reversible and explicitly not a decision.

## 8. Roadmap shape

Two phases inside the MVP, **gated by capability, not by calendar**. `security-roadmap` contains no durations, no headcount and no budget figures — the engagement is a fixed-price milestone contract (CC-04) scoped by the PRD.

| Phase | Exit gate |
|---|---|
| **0 — Foundation** | A developer cannot create a resource outside the EU, cannot commit a secret, and cannot hold a production credential — because the system prevents it |
| **1 — Secure MVP** | The `deployment-recommendations` §11 go/no-go checklist fully satisfied; real client data can be accepted |

Everything beyond that is **proposed, not committed** (`security-roadmap`) or **[FUTURE]** (`future-and-optional-scope`).

## 9. What was removed from earlier drafts of this research

Earlier drafts asserted decisions the PRD does not support. They have been withdrawn, not softened: three-tier key custody as a product offering; hold-your-own-key and external key store; EU sovereign-cloud paid tiers; post-quantum commitments; enclave-based processing; eIDAS qualified timestamping, Merkle-root publication and an open-source verifier CLI; crypto-shredding as the erasure answer; named cloud services (compute platform, database engine, mesh, policy engine, AI provider); specific regions; warm standby, RTO and RPO values; a 99.9% availability commitment; fixed certification dates; enterprise security tiers, auditor roles and customer assurance features; NIS2 and AI Act applicability as settled; and staffing, on-call and budget assumptions. Retained items live in [Future and Optional Scope](future-scope/future-and-optional-scope.md) with no commitment attached. Full accounting in [REVIEW-TRACEABILITY.md](REVIEW-TRACEABILITY.md).

## 10. Confidence

**High** in the control architecture — isolation, key hierarchy, immutability, audit design, upload handling and pipeline security are established practice for regulated multi-tenant workloads.

**Medium, and dependent on decisions this set cannot make** — the delivery topology and its legal consequences; the erasure-versus-immutability conflict; whether the 85% bar is reachable with a given retrieval and prompting architecture (`open-questions`, T-4); and the applicability of any regime beyond GDPR, MiCA and DORA.

**This is engineering and architecture research, not legal advice.** The transfer position, the erasure conflict, and any NIS2 / AI Act / CRA determination each require qualified counsel before anything is contracted or represented to a customer.

---

## Reading order

| If you are… | Read |
|---|---|
| A decision-maker | This document, then [open-questions.md](open-questions.md) and [security-roadmap.md](security-roadmap.md) |
| An architect | [reference-cloud-architecture.md](reference-cloud-architecture.md), [architecture-diagrams.md](architecture-diagrams.md), [architecture-decision-records.md](architecture-decision-records.md), then the topic documents |
| A security engineer | [threat-model.md](threat-model.md), [security-control-matrix.md](security-control-matrix.md), then the data-protection and records topics, plus [`supporting-topics/`](supporting-topics/) |
| Handling data protection | [regulatory-obligations.md](regulatory-obligations.md), [immutable-evidence-retention.md](immutable-evidence-retention.md), [security-control-matrix.md](security-control-matrix.md), [risk-register.md](risk-register.md), and [supporting-topics/cross-border-data-processing.md](supporting-topics/cross-border-data-processing.md) if any delivery is non-EU |
| Reviewing this set against the PRD | [REVIEW-TRACEABILITY.md](REVIEW-TRACEABILITY.md) |
