# 01 — Regulatory Obligations

## Scope framing (read this first)

Two distinct regulatory personas must be separated, because conflating them is the single most common architecture error in this space:

| Persona | Who | Regime that binds them directly |
|---|---|---|
| **Customer** | EU crypto-asset management firms (CASPs authorised under MiCA) | MiCA, DORA, GDPR (controller), AMLR/TFR, NIS2 (if separately in scope) |
| **Us** | The AI compliance platform (SaaS vendor) | GDPR (processor), NIS2 (likely in scope as a cloud computing service provider), CRA (only for shipped software components), DORA **indirectly** via Art. 28–30 contractual flow-down, EU AI Act (provider of an AI system) |

We are **not** a financial entity. DORA does not apply to us *de jure*. It applies to us *de facto* and completely, because every customer is legally obliged to impose DORA Chapter V contractual terms on us, and our services will support their "critical or important functions" (CIFs). Design to DORA as if it bound us directly — that is the commercially and legally safe posture.

## Best practices

- **Build the obligation register before the architecture.** Every control in this research set traces to a specific article. Untraced controls are cost; untraced obligations are fines.
- **Design to the strictest common denominator.** Where MiCA (5-year records), DORA (backup/restoration, incident timelines) and GDPR (storage limitation, erasure) conflict, resolve explicitly and document the resolution as an ADR — do not let it become an implicit default.
- **Treat "supports a critical or important function" as true.** Customers will classify a compliance-reporting and evidence platform as supporting a CIF. That triggers the heavier DORA Art. 30(3) contractual set: full audit and access rights, exit strategies, subcontracting restrictions, service level descriptions, unrestricted right of inspection by the customer and by competent authorities.
- **Publish a regulator-ready assurance pack** (SOC 2 Type II + ISO/IEC 27001 + ISO/IEC 27701 + EU Cloud CoC adherence + pooled audit / DORA register-of-information extract). This converts per-customer due diligence from a bespoke engineering interrupt into a document handoff.
- **Version the compliance matrix with the product.** Obligations change (AMLR 2027, CRA 2026/2027, AI Act 2026/2027). Treat regulatory change as a backlog input with owners and dates.

## EU regulatory implications

### MiCA — Regulation (EU) 2023/1114

Applies to our customers, not to us. Relevant obligations we must *enable*:

- **Art. 68 — Governance arrangements.** CASPs must have "sound administrative arrangements", "resilient ICT systems and security access protocols in accordance with Regulation (EU) 2022/2554". Our platform is part of how they discharge this.
- **Art. 68(9) — Record keeping.** Records of all services, activities, orders and transactions retained for **at least 5 years**, extendable to **7 years** on competent-authority request. Our retention model must support 5y default, 7y extension, and per-record legal hold.
- **Art. 70 — Safekeeping of clients' crypto-assets and funds.** Segregation and custody policy evidence. We store the evidence, not the assets — but our tamper-evidence guarantees become part of their control narrative.
- **Art. 73 — Outsourcing.** CASPs remain fully responsible for outsourced functions; they must be able to monitor us and terminate without detriment to service continuity. Exit assistance and data export are contractual obligations that must be *engineered*, not promised.
- **Art. 60/59** — Notification and authorisation records; **Art. 66** — honest, fair, professional conduct evidence.

Timeline: CASP provisions applied from **30 December 2024**, with member-state transitional ("grandfathering") windows that ended no later than **1 July 2026**.

### DORA — Regulation (EU) 2022/2554 (applies from 17 January 2025)

Flows to us through customer contracts. The five pillars and their architectural consequence:

| Pillar | Articles | What it forces into our design |
|---|---|---|
| ICT risk management | 5–16 | Documented ICT risk framework, asset inventory, CIA classification, network segmentation, encryption at rest/in transit/in use where feasible (Art. 9), identity and access controls, change management, learning and evolving |
| Incident management & reporting | 17–23 | Classification per Delegated Reg. (EU) 2024/1772, root-cause analysis, and **contractual duty to notify customers fast enough for them to hit regulator deadlines** |
| Resilience testing | 24–27 | Annual vulnerability assessments, scenario-based testing, source-code review; TLPT (TIBER-EU) at least every 3 years for significant entities — we will be pulled in as a scope participant |
| Third-party risk | 28–44 | Register of information (Art. 28(3)) — customers must report our entity ID (LEI), subcontractors, data locations, CIF support flag. Art. 30(2)/(3) mandatory contract clauses. Concentration risk assessment. Exit plans |
| Information sharing | 45 | Voluntary threat-intel sharing |

Key RTS/ITS to design against:
- **Commission Delegated Regulation (EU) 2024/1774** — RTS on ICT risk management framework (this is the de facto technical control catalogue; map controls to it directly).
- **Commission Delegated Regulation (EU) 2024/1773** — RTS on the policy for ICT services supporting critical or important functions (subcontracting conditions).
- **Commission Delegated Regulation (EU) 2024/1772** — RTS on major-incident classification criteria and materiality thresholds.
- **Commission Delegated Regulation (EU) 2025/301 and Implementing Regulation (EU) 2025/302** — content and time limits for major incident reporting. Working deadlines: **initial report within 4 hours of classification as major and no later than 24 hours from detection; intermediate within 72 hours; final within 1 month.** *(Verify exact wording against the published RTS/ITS before contracting — see Open Questions.)*

**Architectural consequence:** our customer-notification SLA must be materially tighter than 24 hours — target **≤2 hours from our confirmation of a security incident affecting a customer's data**, so the customer retains time to classify and report.

### GDPR — Regulation (EU) 2016/679

We are a **processor** for customer documents, customer records and audit evidence; **controller** for our own workforce and telemetry data.

- Art. 5 (principles, incl. storage limitation and integrity/confidentiality), Art. 6/9 (special-category data may appear in uploaded KYC/AML documents — health, biometric passport data, political exposure inferences), Art. 22 (automated decision-making — see AI assessments below), Art. 25 (data protection by design and by default), Art. 28 (processor contract, sub-processor authorisation), Art. 30 (records), Art. 32 (security of processing — explicitly names pseudonymisation and encryption), Art. 33/34 (breach notification: controller notifies supervisory authority within **72 hours**; processor notifies controller **"without undue delay"** — contract this to a number), Art. 35 (DPIA — mandatory here), Chapter V Art. 44–49 (transfers, see doc 03).
- **Art. 22 exposure:** AI-generated compliance assessments are decision *support*. Keep a documented human-in-the-loop with authority and competence to override, and log the override. This is the difference between "decision support" and a regulated automated decision producing legal effects.

### NIS2 — Directive (EU) 2022/2555

Directive, so binding via national transposition (deadline 17 October 2024; several member states transposed late — verify per establishment country).

- A multi-tenant B2B SaaS falls within the broad NIS2 definition of a **cloud computing service** (Annex I, digital infrastructure). Expect classification as an **important entity** at SME scale, **essential** above the size thresholds.
- Obligations: Art. 21 risk-management measures (10 named areas incl. supply chain security, cryptography, MFA, incident handling, business continuity), Art. 23 incident reporting — **early warning within 24 hours, incident notification within 72 hours, final report within 1 month**, Art. 20 management-body accountability and training, Art. 24 possible mandated certification schemes.
- Art. 4 lex specialis: for *financial entities*, DORA displaces NIS2. That carve-out does **not** cover us — we are subject to NIS2 directly.

### Cyber Resilience Act — Regulation (EU) 2024/2847

- In force 10 December 2024. **Vulnerability and incident reporting obligations apply from 11 September 2026; the main body of obligations from 11 December 2027.**
- Pure SaaS is generally **out of scope**; it is caught only where the service qualifies as a "remote data processing solution" integral to a product with digital elements.
- **In scope for us the moment we ship anything the customer installs or embeds:** on-prem connectors, desktop agents, browser extensions, CLI tools, SDKs, self-hostable components.
- Obligations if triggered: secure-by-design/default, SBOM covering at minimum top-level dependencies (Annex I Part II), coordinated vulnerability disclosure policy, free security updates for the support period (default expectation 5 years), CE marking and conformity assessment, and 24h/72h/14-day reporting of actively exploited vulnerabilities and severe incidents to CSIRT and ENISA.

### Adjacent regimes that materially bind this product

- **EU AI Act — Regulation (EU) 2024/1689.** We are a **provider** of an AI system. Prohibited practices and AI literacy obligations applied 2 February 2025; GPAI obligations 2 August 2025; the bulk of high-risk obligations 2 August 2026/2027. Compliance assessment for firms is *not* an Annex III high-risk use case (Annex III credit/insurance items concern natural persons). Expect **limited-risk + Art. 50 transparency** obligations plus contractual expectations far above the legal floor. Do not self-classify as out-of-scope without a documented assessment.
- **AMLR — Regulation (EU) 2024/1624 / AMLD6 (EU) 2024/1640 / AMLA (EU) 2024/1620.** Applies from **10 July 2027**. Drives KYC/CDD record content and 5-year retention in the customer records we hold.
- **TFR — Regulation (EU) 2023/1113 ("Travel Rule").** Applies from 30 December 2024. If we ingest or reason over originator/beneficiary data, we handle transaction-linked personal data — a materially higher sensitivity class.
- **eIDAS 2 — Regulation (EU) 2024/1183 amending (EU) 910/2014.** Qualified electronic timestamps and qualified electronic seals carry a legal presumption of accuracy and integrity. This is the highest-value, lowest-cost upgrade available to our immutable-evidence story (see doc 15).
- **EU Data Act — Regulation (EU) 2023/2854.** Cloud switching and egress provisions applicable from 12 September 2025; reinforces the exit-plan and portability engineering DORA already demands.

## Recommended architecture

1. **Obligation register as code.** A versioned YAML/JSON register: `obligation_id, regulation, article, applies_to (us|customer|both), control_ids[], evidence_source, owner, review_date`. Generates the compliance matrix (doc 31) and the customer-facing assurance pack. Single source of truth; no parallel spreadsheets.
2. **Retention policy engine as a first-class service.** Per-record-class policy objects: `min_retention`, `max_retention`, `legal_hold`, `erasure_eligibility`, `jurisdiction`. Drives S3 Object Lock durations, database soft-delete/purge jobs and backup expiry. Reconciles MiCA 5–7y against GDPR storage limitation deterministically, per record class, with an audit trail of the decision.
3. **Incident classification pipeline.** Security events → severity triage → DORA Art. 18 / Delegated Reg. 2024/1772 criteria evaluation → GDPR Art. 33 assessment → NIS2 Art. 23 assessment → templated customer notification with the facts customers need for *their* regulatory filing. Clock starts at detection, tracked and alarmed.
4. **Per-tenant regulatory profile.** Tenant metadata: home member state, CASP authorisation status, CIF designation, data residency tier, retention overrides, sub-processor consents. Policy decisions read this profile rather than hard-coding assumptions.
5. **Continuous evidence collection.** Control evidence (config snapshots, access reviews, test results, DR test reports) collected automatically into the same WORM evidence store the product sells. Dogfood it.

## Risks

| Risk | Impact | Notes |
|---|---|---|
| Misclassifying ourselves as out of NIS2 scope | Unreported incidents, management-body liability, national fines up to €7m/1.4% turnover (important entity) | Broad "cloud computing service" definition; get a national-law opinion |
| Customer contractual DORA terms exceed our operational capability (e.g. on-site audit rights, 1-hour notification) | Contract breach, forced remediation, deal loss | Standardise a DORA-compliant addendum early; negotiate from our paper |
| MiCA/AMLR retention vs GDPR erasure conflict handled ad hoc | Both a data-subject complaint and a records-integrity finding | Retention policy engine + documented Art. 17(3)(b) legal-obligation basis |
| CRA scope creep via a "small" connector or SDK release | Full conformity assessment, CE marking, 5-year update commitment on an unplanned product | Gate any installable artefact behind a CRA scoping review |
| AI Act classification drift as features expand (e.g. scoring individuals) | Jump from limited-risk to Annex III high-risk mid-lifecycle | Re-run classification per material feature change |
| Regulatory change outpaces the register | Silent non-compliance | Named owner, quarterly review, subscribe to ESMA/EBA/EIOPA/ENISA/EDPB feeds |

## Trade-offs

- **Design to DORA voluntarily vs. only what contracts force.** Voluntary compliance costs materially more up front and is the only way to sell into tier-1 CASPs without 6-month security reviews. Recommended: comply voluntarily.
- **Single strictest global policy vs. per-tenant policy engine.** Strictest-global is simpler and cheaper to assure but overprices low-sensitivity tenants and blocks residency-tier upsell. Recommended: policy engine, defaulting to strictest.
- **Certify early (ISO 27001 + SOC 2) vs. defer.** ~€60–120k/yr and real engineering drag, but it is the entry ticket to regulated buyers and collapses per-deal due diligence. Recommended: start ISO 27001 immediately, SOC 2 Type II after 6 months of control operation.
- **Self-classify AI Act risk vs. external legal opinion.** Opinion costs money and time; self-classification carries personal management liability if wrong. Recommended: external opinion, refreshed annually.

## Design decisions

- **DD-01-01:** Design and operate as if DORA applied directly. *(Rationale: contractual flow-down makes it binding in practice; retrofitting is more expensive than building it in.)*
- **DD-01-02:** Assume every customer designates us as supporting a critical or important function. Default contract = DORA Art. 30(3) full set.
- **DD-01-03:** Assume NIS2 in-scope as a cloud computing service; implement Art. 21 measures and Art. 23 reporting readiness. Revisit only on a written national-law opinion.
- **DD-01-04:** No installable/embeddable software artefact ships without a documented CRA scoping decision.
- **DD-01-05:** All AI-generated compliance assessments are advisory, require a named human reviewer to approve, and record the reviewer identity, timestamp and any override rationale. Never produce a legally-effective automated decision.
- **DD-01-06:** Customer incident-notification SLA = **2 hours** from our confirmation, contractually committed.
- **DD-01-07:** Obligation register maintained as versioned code in the product repo, reviewed quarterly, owned by the DPO/Compliance Lead jointly with the Head of Security.

## References

- Regulation (EU) 2023/1114 (MiCA) — https://eur-lex.europa.eu/eli/reg/2023/1114/oj
- Regulation (EU) 2022/2554 (DORA) — https://eur-lex.europa.eu/eli/reg/2022/2554/oj
- Commission Delegated Regulation (EU) 2024/1774 (ICT risk management RTS)
- Commission Delegated Regulation (EU) 2024/1772 (major incident classification RTS)
- Commission Delegated Regulation (EU) 2024/1773 (RTS on ICT services supporting CIFs)
- Regulation (EU) 2016/679 (GDPR) — https://eur-lex.europa.eu/eli/reg/2016/679/oj
- Directive (EU) 2022/2555 (NIS2) — https://eur-lex.europa.eu/eli/dir/2022/2555/oj
- Regulation (EU) 2024/2847 (Cyber Resilience Act) — https://eur-lex.europa.eu/eli/reg/2024/2847/oj
- Regulation (EU) 2024/1689 (AI Act) — https://eur-lex.europa.eu/eli/reg/2024/1689/oj
- Regulation (EU) 2024/1624 (AMLR); Regulation (EU) 2023/1113 (TFR)
- Regulation (EU) 2024/1183 (eIDAS 2); Regulation (EU) 2023/2854 (Data Act)
- ESMA/EBA/EIOPA Joint Committee DORA materials; ENISA NIS2 Technical Implementation Guidance (2025)

## Confidence level

**High (regulation identities, scope logic, core article mapping).** MiCA/DORA/GDPR/NIS2/CRA applicability reasoning is well established and I would defend it in a design review.

**Medium (exact incident-reporting time limits under the 2025 DORA RTS/ITS, NIS2 national transposition specifics per member state, precise CRA treatment of borderline SaaS-adjacent components).** These are recent, detailed, and member-state dependent — confirm with counsel before contractual commitment.

**Low-to-medium (AI Act final classification for compliance-assessment AI).** Guidance and harmonised standards were still maturing; the conservative posture above is defensible but not certain.
