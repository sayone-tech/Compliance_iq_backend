# Regulatory Obligations

> **Baseline:** PRD v4.0 (`docs/requirement-specification/PRD.md`) is the sole source of truth. Classification used throughout this set:
> **[PRD REQUIRED]** — explicitly required by the PRD (the requirement is named, and quoted where it settles the point) · **[PROPOSED]** — implementation recommendation, reasonably necessary to deliver a PRD requirement but not selected by the PRD · **[OPEN]** — stakeholder or legal decision required · **[FUTURE]** — outside the MVP baseline, see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

## Scope framing (read this first)

Two regulatory personas must be separated:

| Persona | Who | What binds them |
|---|---|---|
| **Customer** | EU-licensed CASPs (PRD title block, the PRD's product overview) | MiCA and DORA directly; GDPR as controller; other regimes as their own counsel determines |
| **Platform** | ComplianceIQ, delivered by SayOne, operated on an AWS account owned solely by the Client (the confirmed cloud decision) | **GDPR as processor** (the GDPR processor requirement). Everything else reaches the platform indirectly, through customer contracts, or not at all |

**The PRD names exactly two customer-domain regulations — MiCA and DORA — and one that binds the platform's own processing — GDPR.** That is the regulatory perimeter for the MVP.

MiCA and DORA do **not** apply to the platform vendor *de jure*. Customers may impose DORA Chapter V contractual terms; how far they do so is a commercial matter not settled by the PRD. **[OPEN]**

## Best practices

- **Build the obligation register before the architecture.** Every control in this set should trace to a PRD requirement or to a specific article the PRD's own regulations impose on the customer. Untraced controls are cost. **[PROPOSED]**
- **Where obligations conflict, resolve explicitly and record the resolution.** In this product the live conflict is retention versus erasure (see below and `immutable-evidence-retention`). Do not let it become an implicit default.
- **Version the compliance mapping with the product.** Regulatory content in the Platform Admin Portal is already versioned (the Requirement ID library, the test procedure versioning requirement, the publication review requirement); apply the same discipline to the platform's own obligation register. **[PROPOSED]**

## What the PRD requires

| PRD ref | Requirement | Consequence for this research set |
|---|---|---|
| Tenant isolation requirement | Complete data isolation between firms; multi-tenant architecture from day one | `document-confidentiality`, 12, 30 |
| Encryption requirement | AES-256 at rest, TLS 1.3 in transit, **each firm has its own encryption key** | `encryption-architecture`, 08 |
| EU residency requirement, the confirmed cloud decision | All client data in EU data centres; AWS; account owned solely by the Client | `data-residency`, 30 |
| Immutable audit requirement, the permanent audit log requirement, the PRD's data and retention table | Tamper-proof, append-only audit log; not modifiable or deletable by anyone, including SayOne administrators | `audit-logging`, 15 |
| GDPR processor requirement | GDPR compliance as a **data processor**, under a Data Processing Agreement | `regulatory-obligations`, 03, 06, 15 |
| Non-deletable retention requirement, the PRD's data and retention table | **Minimum six years** retention for test results, findings, evidence, reports and audit logs; no user, including administrators, can delete them | `immutable-evidence-retention` |
| Availability target | Availability target **99.5%**; planned maintenance communicated in advance. The open uptime-SLA question records 99.5% vs 99.9% as still **open** | `disaster-recovery` |
| Certification roadmap item, the open certification question | ISO 27001 and SOC 2 Type II are **on the roadmap**; the timeline is to be agreed with the Client. Whether clients require them is open | `deployment-recommendations`, 35 |
| The PRD's access requirements the access requirements | Role-enforced access, invitation-only account creation, phone-based MFA, permanent audit of every action, deactivation without data loss, minimum two Firm Super Admins | `identity-and-access-management` |
| The PRD's WSP mapping accuracy commitment the advisory AI mapping requirement | AI mapping suggestions are a starting point only; a compliance officer confirms or adjusts. Minimum **85% verified accuracy at UAT** | `ai-governance`, 32 |
| The PRD's mapping sign-off rules the two-person mapping approval requirement, the mapping reversal requirement | Two-person independent sign-off on every mapping and every reversal; the policy author cannot be an approver | `ai-governance`, 15 |
| IP ownership term | All platform source code, architecture, schemas and regulatory content belong 100% exclusively to the Client | Affects anything proposing to publish or open-source platform components |

## Regulatory analysis

### MiCA — Regulation (EU) 2023/1114

Applies to customers. The platform's job is to **enable** their compliance; the PRD's product overview and the PRD's test-building section make the regulatory content itself the Client's product.

- **Art. 68 — governance arrangements**, including resilient ICT systems and security access protocols assessed in accordance with DORA. The platform is part of how a CASP discharges this.
- **Art. 68(9) — record keeping.** Records of services, activities, orders and transactions retained for at least 5 years, extendable to 7 on competent-authority request.
- **Art. 73 — outsourcing.** The CASP remains fully responsible; it must be able to monitor the provider and terminate without detriment to continuity.
- **Art. 92 (transaction monitoring), Art. 66 (honest, fair, professional conduct)** and similar articles are the subject matter of the test library (the Requirement ID library), not obligations on the platform.

> **Retention note — PRD wins.** MiCA's 5-year floor is *lower* than the PRD's baseline. **The platform's retention baseline is the PRD's minimum six years (the non-deletable retention requirement), with the PRD's non-deletability rule on top.** Do not substitute a 5-year or 7-year default anywhere in this set. **[PRD REQUIRED]**

### DORA — Regulation (EU) 2022/2554

Applies to customers from 17 January 2025. It reaches the platform only through customer contracts. Useful as a design reference because customers will ask; not a source of MVP requirements on its own.

| Pillar | Articles | Relevance here |
|---|---|---|
| ICT risk management | 5–16 | Asset inventory, classification, encryption at rest and in transit, access control, change management — all consistent with the PRD's isolation, encryption, residency and immutable audit requirements |
| Incident management | 17–23 | Customers must notify their regulator on their own clocks (the PRD's own four-hour DORA notification workflow, the regulator notification drafting requirement, is a *customer feature*, not a platform SLA) |
| Resilience testing | 24–27 | Customers' obligation. Platform participation in customer TLPT is **[FUTURE]** |
| Third-party risk | 28–44 | Customers may need data locations, sub-processor lists and an entity identifier for their register of information |
| Information sharing | 45 | Voluntary |

Commission Delegated Regulation (EU) 2024/1774 (RTS on ICT risk management) remains the most useful published technical control catalogue for a financial-sector supplier and is cited throughout this set as a **reference**, not as a binding obligation on the platform. **[PROPOSED]**

> **Not confirmed:** that every customer will designate ComplianceIQ as supporting a *critical or important function*, or that the full Art. 30(3) contractual set will apply. Both are contract-negotiation outcomes. **[OPEN]**

### GDPR — Regulation (EU) 2016/679 — the one regime that binds the platform directly

The platform is a **processor** for firm documents, staff records, test evidence and audit records (the GDPR processor requirement); a **controller** for its own workforce and telemetry data.

- Art. 5 principles, including storage limitation and integrity/confidentiality.
- Art. 6/9 — special-category data can appear inside uploaded evidence (identity documents, health-related context in staff records). The accepted evidence file type list permits any of the listed file types as evidence, so the platform cannot assume evidence is free of it.
- Art. 22 — automated decision-making. **The PRD's AI feature is advisory and human-confirmed (the advisory AI mapping requirement) with two-person sign-off (the two-person mapping approval requirement).** Keep it that way and the Art. 22 question does not arise.
- Art. 25 — data protection by design and by default.
- Art. 28 — processor contract and sub-processor authorisation. The DPA is named in the GDPR processor requirement.
- Art. 30 — records of processing.
- Art. 32 — security of processing; names pseudonymisation and encryption explicitly.
- Art. 33/34 — breach notification: controller to supervisory authority within 72 hours; processor notifies the controller "without undue delay". **A specific numeric processor-notification SLA is not set by the PRD.** **[OPEN]**
- Art. 35 — a DPIA is appropriate given large-scale processing of regulated firms' evidence with an AI processing step. **[PROPOSED]**
- Chapter V — transfers, only if any processing or access occurs outside the EU/EEA. See `cross-border-data-processing`; the PRD does not state where development or support is performed. **[OPEN]**

### The retention-versus-erasure conflict — recorded, not resolved

The PRD states, repeatedly and without qualification, that evidence files, test results, findings, reports and audit logs **cannot be deleted by anyone** and are retained for a **minimum of six years** (the PRD's data and retention table, the non-deletable retention requirement, the permanent audit log requirement).

GDPR Art. 17 grants data subjects a right to erasure, subject to Art. 17(3)(b) where processing is necessary for compliance with a legal obligation to which the controller is subject. The customer firm — not the platform — is the controller, and the legal obligation is theirs.

**This is an open legal and product question, not something this research set resolves.** The PRD's non-deletability rule stands. Candidate positions to be put to counsel and to the Client:

1. Erasure requests for records inside the customer's own retention obligation are refused by the controller under Art. 17(3)(b), with the platform providing the documented basis and record class.
2. Records demonstrably outside any retention obligation (for example, marketing contacts, or a firm's own non-evidential uploads) are erasable.
3. Any technical erasure mechanism that would render PRD-protected records unreadable — including key destruction — **must not be adopted as an accepted requirement without the Client's explicit decision**, because it conflicts with the non-deletable retention requirement on its face.

See `immutable-evidence-retention` for the mechanics and `open-questions` question L-3. **[OPEN — LEGAL]**

### Adjacent regimes — mentioned, not adopted

None of the following is confirmed applicable by the PRD. None may drive MVP architecture or scope without stakeholder approval and, where noted, legal confirmation.

| Regime | Status here | Why it might matter | What would trigger it |
|---|---|---|---|
| **NIS2** (Dir. (EU) 2022/2555) | **[OPEN — LEGAL]** Adjacent. Not confirmed | A multi-tenant B2B SaaS may fall within the "cloud computing service" definition, with national transposition determining scope and thresholds | A national-law opinion in the establishment member state. Do not assume in-scope; do not assume out-of-scope |
| **CRA** (Reg. (EU) 2024/2847) | **[OPEN]** Conditional | Pure SaaS is generally out of scope; obligations attach if an installable or embeddable artefact is shipped | The PRD ships no installable component (the PRD's product overview, the open public-API question API is a later phase). Gate any future one behind a scoping review |
| **AI Act** (Reg. (EU) 2024/1689) | **[OPEN — LEGAL]** Classification not determined | The platform provides an AI-assisted mapping feature (the advisory AI mapping requirement) | The PRD does not classify it. Do not self-classify either way without a documented assessment; transparency labelling of AI output is good practice regardless |
| **AMLR** (Reg. (EU) 2024/1624), **TFR** (Reg. (EU) 2023/1113) | **[FUTURE]** Customer-domain | Affects the *content* of a firm's own AML records | The PRD's ICT-monitoring intake explicitly excludes PII and customer-level data (the IT system inventory requirement). No Travel Rule data architecture is required |
| **eIDAS 2** (Reg. (EU) 2024/1183) | **[FUTURE]** | Qualified timestamps would give evidence a legal presumption of integrity | Not required by the PRD; see appendix 39 |
| **EU Data Act** (Reg. (EU) 2023/2854) | **[OPEN]** Adjacent | Cloud switching and egress provisions | Relevant mainly to the Client's own contract with AWS, which the Client owns (the confirmed cloud decision) |

## Recommended architecture

1. **Obligation register as versioned configuration.** `obligation_id, source (PRD requirement ID | regulation article), applies_to (platform|customer), control_ids[], evidence_source, owner, review_date`. Generates the control matrix (`security-control-matrix`). Single source of truth. **[PROPOSED]**
2. **Retention policy service.** Per-record-class policy objects: `min_retention` (never below the PRD's six years for PRD-listed classes), `deletable` (false for the PRD's non-deletable classes), `legal_hold`. Drives storage retention settings and any expiry job. **[PROPOSED, implementing the non-deletable retention requirement]**
3. **Incident handling with a documented customer-notification path.** Security event → severity triage → GDPR Art. 33 processor assessment → notification to the affected firm with the facts they need for their own filing. **The notification time limit is not set by the PRD and must be agreed.** **[PROPOSED / OPEN]**
4. **Per-tenant regulatory profile.** Tenant metadata already exists in the product: home jurisdiction, branch jurisdictions, service lines, client base (the firm registration requirement→the automatic test loading requirement). Security policy decisions should read this profile rather than hard-coding assumptions. **[PROPOSED]**
5. **Continuous control-evidence collection.** Configuration snapshots, access reviews and test results collected automatically into the same immutable store the product already needs for the immutable audit requirement. **[PROPOSED]**

## Risks

| Risk | Impact | Notes |
|---|---|---|
| Retention/erasure conflict handled ad hoc | Both a data-subject complaint and a breach of the non-deletable retention requirement | Escalate as an open legal question; do not pre-empt it in code |
| Customer contractual terms exceed operational capability (on-site audit rights, short notification windows) | Contract breach, forced remediation | Standardise a DORA-aware addendum early; negotiate from the Client's paper |
| Assuming a regime applies that does not (NIS2, AI Act high-risk) | Unbudgeted scope added to a fixed-price MVP (the fixed-price milestone engagement model) | Classification decisions require legal confirmation and Client approval |
| Assuming a regime does not apply that does | Unreported incidents, management liability | Same control: get the opinion, record it |
| Regulatory change outpaces the register | Silent drift | Named owner and periodic review; the Portal already monitors EUR-Lex/EBA/ESMA for customer content (the regulatory monitoring requirement) and the same feeds serve here |

## Trade-offs

- **Design to DORA voluntarily vs. only what the PRD and contracts require.** Voluntary alignment costs more up front and shortens customer security reviews. **The PRD does not commit to it.** Recommendation: use Delegated Reg. (EU) 2024/1774 as a design reference where it costs little, and treat anything with material cost as an explicit Client decision. **[OPEN]**
- **Certify early vs. defer.** The certification roadmap item places ISO 27001 and SOC 2 Type II on the roadmap with the timeline to be agreed. **No delivery date may be assumed.** **[OPEN — The open certification question]**
- **Self-classify AI Act risk vs. external opinion.** Self-classification carries liability if wrong. Recommendation: external opinion before any customer-facing claim. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification | Basis |
|---|---|---|---|
| DD-01-01 | GDPR processor obligations are implemented directly; a DPA governs the relationship | **[PRD REQUIRED]** | GDPR processor requirement |
| DD-01-02 | MiCA and DORA are treated as the customer-domain regulations the product serves, not as direct obligations on the platform | **[PRD REQUIRED]** | the PRD's product overview, title block |
| DD-01-03 | Delegated Reg. (EU) 2024/1774 is used as a design reference for ICT controls where it does not add material cost | **[PROPOSED]** | — |
| DD-01-04 | NIS2 scope is treated as undetermined; no NIS2-specific reporting commitment is made until a national-law opinion exists | **[OPEN — LEGAL]** | — |
| DD-01-05 | AI-assisted WSP mapping output is advisory, human-confirmed, and subject to two-person sign-off; it never becomes a final determination without that | **[PRD REQUIRED]** | Advisory AI mapping requirement, the two-person mapping approval requirement, the mapping reversal requirement |
| DD-01-06 | Customer incident-notification timing is agreed contractually; no numeric SLA is assumed by this research | **[OPEN]** | — |
| DD-01-07 | No installable or embeddable artefact ships without a CRA scoping decision | **[PROPOSED]** | — |
| DD-01-08 | Obligation register maintained as versioned configuration, reviewed periodically, with a named owner | **[PROPOSED]** | — |

## References

- Regulation (EU) 2023/1114 (MiCA) — https://eur-lex.europa.eu/eli/reg/2023/1114/oj
- Regulation (EU) 2022/2554 (DORA) — https://eur-lex.europa.eu/eli/reg/2022/2554/oj
- Commission Delegated Regulation (EU) 2024/1774 (ICT risk management RTS) — design reference
- Regulation (EU) 2016/679 (GDPR) — https://eur-lex.europa.eu/eli/reg/2016/679/oj
- Directive (EU) 2022/2555 (NIS2) — adjacent, scope undetermined
- Regulation (EU) 2024/1689 (AI Act) — adjacent, classification undetermined
- Regulation (EU) 2024/2847 (CRA); Regulation (EU) 2023/2854 (Data Act) — conditional
- ESMA/EBA/EIOPA Joint Committee DORA materials

## Confidence level

**High** — the persona split, the GDPR processor position, the mapping of PRD requirements to controls, and the identification of the retention/erasure conflict.

**Medium** — how far individual customers will push DORA Chapter V terms onto the platform in contract.

**Not determined, and deliberately left so** — NIS2 scope, AI Act classification, and the erasure/retention resolution. Each requires qualified counsel and, for the last, a Client decision.
