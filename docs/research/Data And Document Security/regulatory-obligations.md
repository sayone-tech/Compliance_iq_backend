# Regulatory Obligations

> **Baseline:** PRD v4.0 (`docs/requirement-specification/PRD.md`) is the sole source of truth. Classification used throughout this set:
> **[PRD REQUIRED]** — explicitly required by the PRD (section or requirement ID cited) · **[PROPOSED]** — implementation recommendation, reasonably necessary to deliver a PRD requirement but not selected by the PRD · **[OPEN]** — stakeholder or legal decision required · **[FUTURE]** — outside the MVP baseline, see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

## Scope framing (read this first)

Two regulatory personas must be separated:

| Persona | Who | What binds them |
|---|---|---|
| **Customer** | EU-licensed CASPs (PRD title block, §1) | MiCA and DORA directly; GDPR as controller; other regimes as their own counsel determines |
| **Platform** | ComplianceIQ, delivered by SayOne, operated on an AWS account owned solely by the Client (PRD TI-01) | **GDPR as processor** (NFR-06). Everything else reaches the platform indirectly, through customer contracts, or not at all |

**The PRD names exactly two customer-domain regulations — MiCA and DORA — and one that binds the platform's own processing — GDPR.** That is the regulatory perimeter for the MVP.

MiCA and DORA do **not** apply to the platform vendor *de jure*. Customers may impose DORA Chapter V contractual terms; how far they do so is a commercial matter not settled by the PRD. **[OPEN]**

## Best practices

- **Build the obligation register before the architecture.** Every control in this set should trace to a PRD requirement or to a specific article the PRD's own regulations impose on the customer. Untraced controls are cost. **[PROPOSED]**
- **Where obligations conflict, resolve explicitly and record the resolution.** In this product the live conflict is retention versus erasure (see below and `immutable-evidence-retention`). Do not let it become an implicit default.
- **Version the compliance mapping with the product.** Regulatory content in the Platform Admin Portal is already versioned (SA-01, SA-02, SA-04); apply the same discipline to the platform's own obligation register. **[PROPOSED]**

## What the PRD requires

| PRD ref | Requirement | Consequence for this research set |
|---|---|---|
| NFR-01 | Complete data isolation between firms; multi-tenant architecture from day one | `document-confidentiality`, 12, 30 |
| NFR-02 | AES-256 at rest, TLS 1.3 in transit, **each firm has its own encryption key** | `encryption-architecture`, 08 |
| NFR-03, TI-01 | All client data in EU data centres; AWS; account owned solely by the Client | `data-residency`, 30 |
| NFR-04, FR-13, §2 | Tamper-proof, append-only audit log; not modifiable or deletable by anyone, including SayOne administrators | `audit-logging`, 15 |
| NFR-06 | GDPR compliance as a **data processor**, under a Data Processing Agreement | `regulatory-obligations`, 03, 06, 15 |
| NFR-07, §2 | **Minimum six years** retention for test results, findings, evidence, reports and audit logs; no user, including administrators, can delete them | `immutable-evidence-retention` |
| NFR-08 | Availability target **99.5%**; planned maintenance communicated in advance. TI-02 records 99.5% vs 99.9% as still **open** | `disaster-recovery` |
| NFR-09, TI-03 | ISO 27001 and SOC 2 Type II are **on the roadmap**; the timeline is to be agreed with the Client. Whether clients require them is open | `deployment-recommendations`, 35 |
| §3.3 FR-09→FR-15 | Role-enforced access, invitation-only account creation, phone-based MFA, permanent audit of every action, deactivation without data loss, minimum two Firm Super Admins | `identity-and-access-management` |
| §6.2 FR-31 | AI mapping suggestions are a starting point only; a compliance officer confirms or adjusts. Minimum **85% verified accuracy at UAT** | `ai-governance`, 32 |
| §6.3 FR-32, FR-33 | Two-person independent sign-off on every mapping and every reversal; the policy author cannot be an approver | `ai-governance`, 15 |
| CC-03 | All platform source code, architecture, schemas and regulatory content belong 100% exclusively to the Client | Affects anything proposing to publish or open-source platform components |

## Regulatory analysis

### MiCA — Regulation (EU) 2023/1114

Applies to customers. The platform's job is to **enable** their compliance; PRD §1 and §4.1 make the regulatory content itself the Client's product.

- **Art. 68 — governance arrangements**, including resilient ICT systems and security access protocols assessed in accordance with DORA. The platform is part of how a CASP discharges this.
- **Art. 68(9) — record keeping.** Records of services, activities, orders and transactions retained for at least 5 years, extendable to 7 on competent-authority request.
- **Art. 73 — outsourcing.** The CASP remains fully responsible; it must be able to monitor the provider and terminate without detriment to continuity.
- **Art. 92 (transaction monitoring), Art. 66 (honest, fair, professional conduct)** and similar articles are the subject matter of the test library (SA-01), not obligations on the platform.

> **Retention note — PRD wins.** MiCA's 5-year floor is *lower* than the PRD's baseline. **The platform's retention baseline is the PRD's minimum six years (NFR-07), with the PRD's non-deletability rule on top.** Do not substitute a 5-year or 7-year default anywhere in this set. **[PRD REQUIRED]**

### DORA — Regulation (EU) 2022/2554

Applies to customers from 17 January 2025. It reaches the platform only through customer contracts. Useful as a design reference because customers will ask; not a source of MVP requirements on its own.

| Pillar | Articles | Relevance here |
|---|---|---|
| ICT risk management | 5–16 | Asset inventory, classification, encryption at rest and in transit, access control, change management — all consistent with PRD NFR-01→NFR-04 |
| Incident management | 17–23 | Customers must notify their regulator on their own clocks (the PRD's own four-hour DORA notification workflow, FR-76, is a *customer feature*, not a platform SLA) |
| Resilience testing | 24–27 | Customers' obligation. Platform participation in customer TLPT is **[FUTURE]** |
| Third-party risk | 28–44 | Customers may need data locations, sub-processor lists and an entity identifier for their register of information |
| Information sharing | 45 | Voluntary |

Commission Delegated Regulation (EU) 2024/1774 (RTS on ICT risk management) remains the most useful published technical control catalogue for a financial-sector supplier and is cited throughout this set as a **reference**, not as a binding obligation on the platform. **[PROPOSED]**

> **Not confirmed:** that every customer will designate ComplianceIQ as supporting a *critical or important function*, or that the full Art. 30(3) contractual set will apply. Both are contract-negotiation outcomes. **[OPEN]**

### GDPR — Regulation (EU) 2016/679 — the one regime that binds the platform directly

The platform is a **processor** for firm documents, staff records, test evidence and audit records (NFR-06); a **controller** for its own workforce and telemetry data.

- Art. 5 principles, including storage limitation and integrity/confidentiality.
- Art. 6/9 — special-category data can appear inside uploaded evidence (identity documents, health-related context in staff records). PRD FR-24 permits any of the listed file types as evidence, so the platform cannot assume evidence is free of it.
- Art. 22 — automated decision-making. **The PRD's AI feature is advisory and human-confirmed (FR-31) with two-person sign-off (FR-32).** Keep it that way and the Art. 22 question does not arise.
- Art. 25 — data protection by design and by default.
- Art. 28 — processor contract and sub-processor authorisation. The DPA is named in NFR-06.
- Art. 30 — records of processing.
- Art. 32 — security of processing; names pseudonymisation and encryption explicitly.
- Art. 33/34 — breach notification: controller to supervisory authority within 72 hours; processor notifies the controller "without undue delay". **A specific numeric processor-notification SLA is not set by the PRD.** **[OPEN]**
- Art. 35 — a DPIA is appropriate given large-scale processing of regulated firms' evidence with an AI processing step. **[PROPOSED]**
- Chapter V — transfers, only if any processing or access occurs outside the EU/EEA. See `cross-border-data-processing`; the PRD does not state where development or support is performed. **[OPEN]**

### The retention-versus-erasure conflict — recorded, not resolved

The PRD states, repeatedly and without qualification, that evidence files, test results, findings, reports and audit logs **cannot be deleted by anyone** and are retained for a **minimum of six years** (PRD §2, NFR-07, FR-13).

GDPR Art. 17 grants data subjects a right to erasure, subject to Art. 17(3)(b) where processing is necessary for compliance with a legal obligation to which the controller is subject. The customer firm — not the platform — is the controller, and the legal obligation is theirs.

**This is an open legal and product question, not something this research set resolves.** The PRD's non-deletability rule stands. Candidate positions to be put to counsel and to the Client:

1. Erasure requests for records inside the customer's own retention obligation are refused by the controller under Art. 17(3)(b), with the platform providing the documented basis and record class.
2. Records demonstrably outside any retention obligation (for example, marketing contacts, or a firm's own non-evidential uploads) are erasable.
3. Any technical erasure mechanism that would render PRD-protected records unreadable — including key destruction — **must not be adopted as an accepted requirement without the Client's explicit decision**, because it conflicts with NFR-07 on its face.

See `immutable-evidence-retention` for the mechanics and `open-questions` question L-3. **[OPEN — LEGAL]**

### Adjacent regimes — mentioned, not adopted

None of the following is confirmed applicable by the PRD. None may drive MVP architecture or scope without stakeholder approval and, where noted, legal confirmation.

| Regime | Status here | Why it might matter | What would trigger it |
|---|---|---|---|
| **NIS2** (Dir. (EU) 2022/2555) | **[OPEN — LEGAL]** Adjacent. Not confirmed | A multi-tenant B2B SaaS may fall within the "cloud computing service" definition, with national transposition determining scope and thresholds | A national-law opinion in the establishment member state. Do not assume in-scope; do not assume out-of-scope |
| **CRA** (Reg. (EU) 2024/2847) | **[OPEN]** Conditional | Pure SaaS is generally out of scope; obligations attach if an installable or embeddable artefact is shipped | The PRD ships no installable component (§1, TI-05 API is a later phase). Gate any future one behind a scoping review |
| **AI Act** (Reg. (EU) 2024/1689) | **[OPEN — LEGAL]** Classification not determined | The platform provides an AI-assisted mapping feature (FR-31) | The PRD does not classify it. Do not self-classify either way without a documented assessment; transparency labelling of AI output is good practice regardless |
| **AMLR** (Reg. (EU) 2024/1624), **TFR** (Reg. (EU) 2023/1113) | **[FUTURE]** Customer-domain | Affects the *content* of a firm's own AML records | The PRD's ICT-monitoring intake explicitly excludes PII and customer-level data (FR-72). No Travel Rule data architecture is required |
| **eIDAS 2** (Reg. (EU) 2024/1183) | **[FUTURE]** | Qualified timestamps would give evidence a legal presumption of integrity | Not required by the PRD; see appendix 39 |
| **EU Data Act** (Reg. (EU) 2023/2854) | **[OPEN]** Adjacent | Cloud switching and egress provisions | Relevant mainly to the Client's own contract with AWS, which the Client owns (TI-01) |

## Recommended architecture

1. **Obligation register as versioned configuration.** `obligation_id, source (PRD requirement ID | regulation article), applies_to (platform|customer), control_ids[], evidence_source, owner, review_date`. Generates the control matrix (`security-control-matrix`). Single source of truth. **[PROPOSED]**
2. **Retention policy service.** Per-record-class policy objects: `min_retention` (never below the PRD's six years for PRD-listed classes), `deletable` (false for the PRD's non-deletable classes), `legal_hold`. Drives storage retention settings and any expiry job. **[PROPOSED, implementing NFR-07]**
3. **Incident handling with a documented customer-notification path.** Security event → severity triage → GDPR Art. 33 processor assessment → notification to the affected firm with the facts they need for their own filing. **The notification time limit is not set by the PRD and must be agreed.** **[PROPOSED / OPEN]**
4. **Per-tenant regulatory profile.** Tenant metadata already exists in the product: home jurisdiction, branch jurisdictions, service lines, client base (FR-01→FR-07). Security policy decisions should read this profile rather than hard-coding assumptions. **[PROPOSED]**
5. **Continuous control-evidence collection.** Configuration snapshots, access reviews and test results collected automatically into the same immutable store the product already needs for NFR-04. **[PROPOSED]**

## Risks

| Risk | Impact | Notes |
|---|---|---|
| Retention/erasure conflict handled ad hoc | Both a data-subject complaint and a breach of NFR-07 | Escalate as an open legal question; do not pre-empt it in code |
| Customer contractual terms exceed operational capability (on-site audit rights, short notification windows) | Contract breach, forced remediation | Standardise a DORA-aware addendum early; negotiate from the Client's paper |
| Assuming a regime applies that does not (NIS2, AI Act high-risk) | Unbudgeted scope added to a fixed-price MVP (CC-04) | Classification decisions require legal confirmation and Client approval |
| Assuming a regime does not apply that does | Unreported incidents, management liability | Same control: get the opinion, record it |
| Regulatory change outpaces the register | Silent drift | Named owner and periodic review; the Portal already monitors EUR-Lex/EBA/ESMA for customer content (SA-03) and the same feeds serve here |

## Trade-offs

- **Design to DORA voluntarily vs. only what the PRD and contracts require.** Voluntary alignment costs more up front and shortens customer security reviews. **The PRD does not commit to it.** Recommendation: use Delegated Reg. (EU) 2024/1774 as a design reference where it costs little, and treat anything with material cost as an explicit Client decision. **[OPEN]**
- **Certify early vs. defer.** NFR-09 places ISO 27001 and SOC 2 Type II on the roadmap with the timeline to be agreed. **No delivery date may be assumed.** **[OPEN — TI-03]**
- **Self-classify AI Act risk vs. external opinion.** Self-classification carries liability if wrong. Recommendation: external opinion before any customer-facing claim. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification | Basis |
|---|---|---|---|
| DD-01-01 | GDPR processor obligations are implemented directly; a DPA governs the relationship | **[PRD REQUIRED]** | NFR-06 |
| DD-01-02 | MiCA and DORA are treated as the customer-domain regulations the product serves, not as direct obligations on the platform | **[PRD REQUIRED]** | PRD §1, title block |
| DD-01-03 | Delegated Reg. (EU) 2024/1774 is used as a design reference for ICT controls where it does not add material cost | **[PROPOSED]** | — |
| DD-01-04 | NIS2 scope is treated as undetermined; no NIS2-specific reporting commitment is made until a national-law opinion exists | **[OPEN — LEGAL]** | — |
| DD-01-05 | AI-assisted WSP mapping output is advisory, human-confirmed, and subject to two-person sign-off; it never becomes a final determination without that | **[PRD REQUIRED]** | FR-31, FR-32, FR-33 |
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
