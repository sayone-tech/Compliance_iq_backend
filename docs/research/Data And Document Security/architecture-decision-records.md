# Architecture Decision Records

> **Baseline:** PRD v4.0.
>
> **Status vocabulary used here — and there is no "Accepted":**
>
> | Status | Meaning |
> |---|---|
> | **PRD REQUIRED** | Fixed by the PRD. The supporting requirement is named and, where useful, quoted. Not open for redecision without an amendment to the baseline |
> | **PROPOSED** | This research recommends it. Nobody has approved it |
> | **OPEN — STAKEHOLDER DECISION REQUIRED** | The choice genuinely belongs to the Client or to counsel, and is not made here |
> | **FUTURE/OPTIONAL** | Outside the MVP baseline — see [Future and Optional Scope](future-scope/future-and-optional-scope.md) |
>
> **No deciders are named.** The PRD assigns no security, technical or data-protection roles, and this research does not invent approvals. Where a PRD decision has a recorded approver, that approval is cited from the PRD itself.

---

## ADR-001 — AWS, EU data centre, account owned solely by the Client

**Status: PRD REQUIRED** · **Basis:** the PRD's technical and security requirements, the confirmed cloud decision (*"RESOLVED: AWS, deployed inside an EU-resident data centre, on an account owned solely by the Client (not SayOne)"*), the EU residency requirement.

**Context.** Clients are EU-licensed CASPs with strong residency expectations. The EU residency requirement requires EU data centres for all client data.

**Decision.** AWS, EU data centre, Client-owned account. **The region is not specified by the PRD and is not chosen here** (ADR-002).

**Consequences.** *Positive:* mature managed services; the Client owns the account, which simplifies the "who can compel production of plaintext" conversation and aligns with the IP ownership term's exclusive IP assignment. *Negative:* provisioning, role handover and root-credential custody inside a Client-owned account are operational questions the PRD does not answer (`open-questions`, P-2). *Mitigation:* portability maintained as a design discipline; the handover model agreed before go-live.

---

## ADR-002 — EU region selection

**Status: OPEN — STAKEHOLDER DECISION REQUIRED** · **Basis:** PRD is silent; the EU residency requirement requires only "EU data centres".

**Context.** Every subsequent resource inherits the region. Service availability, availability-zone count, write-once storage features and key-service capabilities differ by region.

**Decision required.** Select one EU region against documented criteria (`data-residency`), and decide separately whether a second EU location is funded for record copies or recovery (`disaster-recovery`, `open-questions` P-3).

**Consequence of not deciding.** The foundation build cannot complete. This is the first decision needed.

---

## ADR-003 — Per-firm encryption keys with context binding

**Status: PRD REQUIRED (the per-firm key) / PROPOSED (the binding mechanism)** · **Basis:** The encryption requirement (*"Each firm has its own encryption key"*), the PRD's data and retention table (*"per-tenant encryption keys"*), the tenant isolation requirement.

**Context.** Cross-firm disclosure is the failure this product cannot survive (R-01).

**Decision.** A distinct key per firm, as the PRD requires. **Proposed** implementation: envelope encryption with per-object data keys wrapped by the firm key, and a key policy that only permits decryption when the request's encryption context carries the matching firm identifier.

**Consequences.** *Positive:* a data-mixing bug fails closed rather than leaking; the per-firm key becomes a real isolation control rather than a label. *Negative:* per-key cost and key-service request volume; key count to monitor at scale. *Mitigation:* bounded data-key caching; benchmark against the performance requirement performance target.

---

## ADR-004 — Records that cannot be deleted, by anyone

**Status: PRD REQUIRED** · **Basis:** The immutable audit requirement (*"Not even the system administrators at SayOne can modify or delete this log"*), the non-deletable retention requirement (*"No user — including administrators — can delete them"*), the PRD's data and retention table retention table, the PRD's testing workflow step 5, the permanent audit log requirement, the amendment-not-edit requirement, the immutable issued report requirement, the permanent WSP version history requirement, the Not Applicable immutability requirement, the sample-change approval requirement.

**Context.** The product's promise is a permanent, provable record of a firm's compliance activity.

**Decision.** Test results, findings, evidence, remediation evidence, reports, audit logs and notification logs are retained for a **minimum of six years** and have **no deletion path for any principal**. Signed-off results are corrected only by amendment; issued reports are archived exactly as issued; WSP versions and mapping changes are retained permanently.

**Proposed** implementation: write-once object retention in a mode no principal can override, hash chaining for tamper evidence, a write-only log-archive account, and key-deletion denial so the requirement cannot be defeated indirectly (ADR-005).

**Consequences.** *Positive:* the strongest insider control in the product; the promise becomes a property rather than a claim. *Negative:* mistakes are permanent; storage grows monotonically; it collides with GDPR erasure (ADR-006). *Mitigation:* staged rollout of irreversible controls (`deployment-recommendations` §5); retention derived only from the retention service, never hand-entered.

---

## ADR-005 — Key destruction cannot be a route around ADR-004

**Status: PRD REQUIRED in effect / PROPOSED as mechanism** · **Basis:** The non-deletable retention requirement, the PRD's data and retention table, read together with the encryption requirement.

**Context.** Destroying a firm's key would render that firm's six-year records unreadable. An unreadable record is a deleted record in substance.

**Decision.** Deletion is denied unconditionally for the audit, sealing and backup keys. Deletion of a per-firm key is **blocked by a precondition check against the retention registry** while any of that firm's records remain inside their retention period. **Crypto-shredding is not adopted as an erasure mechanism.**

**Consequences.** *Positive:* closes the obvious indirect route around ADR-004. *Negative:* removes the mechanism most SaaS products use to answer erasure requests, which is precisely why ADR-006 stays open. *Mitigation:* none needed technically; the legal question is escalated rather than engineered around.

---

## ADR-006 — GDPR erasure versus the non-deletability rule

**Status: OPEN — STAKEHOLDER AND LEGAL DECISION REQUIRED** · **Basis:** the PRD's data and retention table and the non-deletable retention requirement versus GDPR Art. 17; the GDPR processor requirement makes the platform a processor.

**Context.** The PRD says protected records cannot be deleted by anyone. GDPR grants a right to erasure, subject to Art. 17(3)(b) where processing is necessary for compliance with a legal obligation on the *controller* — which is the client firm, not the platform.

**Not decided here.** This research **does not** resolve the conflict and **does not** adopt crypto-shredding, deletion sagas or soft-delete grace periods.

**What is built in the meantime.** No deletion path for protected classes; a record-class registry distinguishing protected from unprotected classes; a documented refusal path the controller can use; deletion capability only for classes with no retention obligation.

**Decision required from the Client with counsel.** `open-questions`, L-3 and L-4.

---

## ADR-007 — AI-assisted WSP mapping is advisory and human-approved

**Status: PRD REQUIRED** · **Basis:** The advisory AI mapping requirement (*"The AI suggestions are a starting point only — not a final determination… the human makes the final call"*), the two-person mapping approval requirement, the mapping reversal requirement, the PRD's WSP mapping accuracy commitment (accepted 3 Jul 2026), the PRD's mapping sign-off rules (the mapping override initiation gap answer), the permanent WSP version history requirement.

**Context.** The product's only AI feature suggests mappings between a firm's compliance manual and regulatory Requirement IDs.

**Decision.** Model output is a suggestion. A compliance officer confirms or adjusts it. Confirmation — and any reversal — requires **two independent senior approvers**, and the policy author cannot be one of them. Mapping re-runs automatically on a new labelled WSP version; manual overrides carry a visible tag. Every version and change is retained permanently. **Minimum 85% verified accuracy against pre-defined verification vectors at UAT.**

**Consequences.** *Positive:* the automated-decision question under GDPR Art. 22 does not arise on this design; a wrong suggestion has two human gates before it becomes a record. *Negative:* the 85% bar is a contractual commitment that must be measured continuously, not discovered at UAT. *Mitigation:* an evaluation harness gating promotion (ADR-009).

**This decision must not be weakened.** Removing the human confirmation or the two-approver rule would change the regulatory analysis materially.

---

## ADR-008 — AI inference is EU-resident, no-training, no-retention; provider unselected

**Status: PROPOSED (the properties) / OPEN — STAKEHOLDER DECISION REQUIRED (the provider)** · **Basis:** The EU residency requirement requires EU residency; the PRD names no provider or model.

**Context.** WSP content must reach an inference service without leaving the EU boundary or being retained or trained on.

**Decision.** State the requirement as an outcome: EU-resident inference under terms giving no training on inputs or outputs and no provider-side retention, with contractual change notice. Build behind an abstraction so the provider is replaceable.

**Selection criteria:** EU-resident processing; no-training and no-retention terms; contractual change notice; measured accuracy against the PRD's WSP mapping accuracy commitment verification vectors; cost per mapping run, noting that re-runs are automatic on every new WSP version.

**Not decided.** No provider or model is chosen here (`open-questions`, P-6).

---

## ADR-009 — Deterministic verification of cited WSP spans

**Status: PROPOSED** · **Basis:** supports the PRD's WSP mapping accuracy commitment's accuracy commitment and the advisory AI mapping requirement's reviewability.

**Context.** A suggestion pointing at text that does not exist in the manual is the most damaging failure class: it wastes reviewer time and erodes trust in the feature that the fixed fee is committed to delivering at 85% accuracy.

**Decision.** Every cited WSP span must exist in the source document at the stated offset, verified deterministically in code before the suggestion is presented as grounded. Failure blocks the suggestion. This is **in addition to**, not instead of, the human confirmation and two-person approval that ADR-007 requires.

**Consequences.** *Positive:* removes a whole failure class without relying on a model to check a model; cheap; explainable. *Negative:* constrains the output format — citations must carry offsets — and rejects some otherwise-valid paraphrase-style outputs. *Mitigation:* prompt design that always emits verifiable spans; rejected suggestions logged and fed into the evaluation set.

---

## ADR-010 — Layered enforcement on the path to evidence

**Status: PROPOSED** · **Basis:** implements the tenant isolation requirement.

**Context.** Cross-firm disclosure is the risk that ends the product. Single-layer enforcement, however well written, will eventually have a bug.

**Decision.** Five independent enforcement points: per-request authorisation at ingress; service-identity authorisation between services; application repository firm scoping; database row-level security; and a key policy requiring a matching firm encryption context. Each is independently sufficient to prevent cross-firm disclosure.

**Consequences.** *Positive:* no single bug produces a breach; the design is explainable in one diagram. *Negative:* per-request latency across five layers, against the performance requirement's two-second dashboard target and 100 concurrent users per firm; five places to keep consistent. *Mitigation:* local policy evaluation; benchmark p99 early; a cross-firm negative test matrix as a blocking CI gate.

---

## ADR-011 — Zero standing human access to production

**Status: PROPOSED** · **Basis:** supports the immutable audit requirement, the permanent audit log requirement and, if any delivery is non-EU, the transfer position in `cross-border-data-processing`.

**Context.** The platform concentrates every client firm's compliance evidence. The immutable audit requirement and the non-deletable retention requirement already say administrators cannot alter or delete records; access to *read* them is the remaining insider surface.

**Decision.** No standing human access to production. Deployment via pipeline identity only. Break-glass is dual-approved, conducted through a controlled EU-hosted session with egress disabled, fully recorded, time-boxed and auto-revoked, with every use reviewed and trended toward zero.

**Consequences.** *Positive:* removes most insider scenarios and the highest-risk cross-border scenario at once. *Negative:* slows some production incident resolution; requires investment in redacted observability and synthetic reproduction; may require EU-resident cover the PRD does not fund. *Mitigation:* fund the observability work that makes zero-access viable; escalate the cover question (`open-questions`, L-1, P-8).

---

## ADR-012 — Retention service as the single source of truth

**Status: PROPOSED** · **Basis:** implements the non-deletable retention requirement and the PRD's data and retention table.

**Context.** Retention is stated per record class across the PRD's data and retention table and the non-deletable retention requirement, with different rules for evidence, results, reports, WSP versions and requirement-ID versions.

**Decision.** A retention service holds per-record-class policy objects — minimum retention, legal basis, deletability, legal-hold capability. It is the **only** source for write-once retain-until dates and for any future disposal scheduling. Extension is supported (a firm whose authority extends its own retention); shortening below the PRD floor is impossible. **No maximum retention or expiry job is defined, because the PRD sets a floor and no ceiling** (ADR-006, `open-questions` L-4).

**Consequences.** *Positive:* deterministic, auditable, reviewable as configuration rather than code. *Negative:* the service must exist before the first record is stored; misconfiguration has permanent consequences. *Mitigation:* staged rollout; retention derived only from the service; scheduled verification.

---

## ADR-013 — Availability target, recovery architecture and recovery objectives

**Status: PRD REQUIRED (the 99.5% target) / OPEN — STAKEHOLDER DECISION REQUIRED (everything else)** · **Basis:** The availability target (*"targets 99.5% availability"*), the open uptime-SLA question (*"Is 99.5% sufficient, or do clients require 99.9%? — still open — estimation blocker"*).

**Context.** The PRD states an availability target and simultaneously records it as unresolved. It sets no recovery-time or recovery-point objective and mandates no recovery architecture.

**Decision.** The stated target is 99.5%. **No recovery-time or recovery-point objective is proposed, and no recovery architecture is selected.** What this research does recommend: record copies must exist outside the primary environment's failure domain, within the EU, because record loss breaches the non-deletable retention requirement and cannot be remediated — and record durability should be funded before faster service recovery.

**Decision required.** Resolve the open uptime-SLA question; then choose a recovery architecture against measured restore times (`deployment-recommendations` §7). **No figure may be quoted to a customer before it is measured twice.**

---

## ADR-014 — Security controls, policies and detections as code

**Status: PROPOSED** · **Basis:** supports the tenant isolation requirement, the immutable audit requirement and the auditability the product itself sells.

**Context.** Security rules edited in consoles drift, break silently, and cannot be tested or audited.

**Decision.** Detection rules, authorisation policy, infrastructure, admission policy and pipeline definitions are version-controlled, peer-reviewed, unit-tested in CI and deployed through the pipeline. No manual production changes; drift is detected and reverted.

**Consequences.** *Positive:* every security-control change is reviewable and testable. *Negative:* slower iteration on detection tuning. *Mitigation:* a fast-path review for tuning; emergency changes use a faster approval path but never bypass review entirely.

---

## Decision log summary

| ADR | Subject | Status | Reversibility | Primary risk addressed |
|---|---|---|---|---|
| 001 | AWS, EU data centre, Client-owned account | **PRD REQUIRED** — The confirmed cloud decision, the EU residency requirement | Low | Residency (R-32) |
| 002 | EU region selection | **OPEN** | Low once built | Foundation blocker |
| 003 | Per-firm keys with context binding | **PRD REQUIRED** (key) / **PROPOSED** (binding) — The encryption requirement | **Low** (data migration) | R-01 cross-firm |
| 004 | Non-deletable records, six-year minimum | **PRD REQUIRED** — The immutable audit requirement, the non-deletable retention requirement, the PRD's data and retention table | **Very low** (permanent) | R-04, R-08, R-27 |
| 005 | Key destruction blocked during retention | **PRD REQUIRED in effect** | Low | R-08 |
| 006 | Erasure versus non-deletability | **OPEN — LEGAL** | — | R-16 |
| 007 | AI mapping advisory, human-approved | **PRD REQUIRED** — The advisory AI mapping requirement, the two-person mapping approval requirement, the PRD's WSP mapping accuracy commitment | High | R-02, R-05 |
| 008 | EU-resident inference; provider unselected | **PROPOSED** / **OPEN** | High | R-23 |
| 009 | Deterministic span verification | **PROPOSED** | High | R-02, R-05 |
| 010 | Layered enforcement to evidence | **PROPOSED** | Medium | R-01 |
| 011 | Zero standing production access | **PROPOSED** | Medium (operating model) | R-03, R-09 |
| 012 | Retention service as single source | **PROPOSED** | **Low** | R-08 |
| 013 | Availability and recovery objectives | **PRD REQUIRED** (target) / **OPEN** (rest) | Medium | R-19, R-26 |
| 014 | Everything as code | **PROPOSED** | High | R-35, auditability |

Decisions marked **low** or **very low** reversibility deserve the most scrutiny before implementation — particularly ADR-003, ADR-004 and ADR-012, where a mistake is permanent by design.
