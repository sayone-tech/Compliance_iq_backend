# Section 3 — What "WSP" Means (Regulatory Terminology Analysis)

Research date / all sources accessed: **2026-08-17**.
Scope: establishes the verified regulatory meaning of "WSP", its status (or absence) in EU law, the EU-law equivalents under MiCA and DORA, and the interpretive gaps the product must resolve.

---

## 3.1 VERIFIED FACT — "WSP" = Written Supervisory Procedures, a US FINRA concept

- **VERIFIED FACT:** "WSP" is the standard US securities-industry abbreviation for **Written Supervisory Procedures**, the document required of every FINRA member broker-dealer by **FINRA Rule 3110(b)(1) (Supervision)**: *"Each member shall establish, maintain, and enforce written procedures to supervise the types of business in which it engages and the activities of its associated persons that are reasonably designed to achieve compliance with applicable securities laws and regulations, and with applicable FINRA rules."*
  Source: FINRA Rulebook, Rule 3110 — https://www.finra.org/rules-guidance/rulebooks/finra-rules/3110 (accessed 2026-08-17).
- **VERIFIED FACT:** FINRA Rule 3110(b) further requires WSPs to cover review of investment banking/securities business, correspondence and internal communications, and customer complaints; Rule 3110(b)(7) requires prompt communication of the WSPs and amendments to all associated persons (electronic media permitted). FINRA's Supervision FAQ uses the term "written supervisory procedures (WSPs)" explicitly. Source: https://www.finra.org/rules-guidance/key-topics/supervision/faq (accessed 2026-08-17).
- **VERIFIED FACT:** FINRA Rule 3120 separately requires **Supervisory Control Policies and Procedures (SCPs)** that test and verify, at least annually, that the WSPs are reasonably designed, and require amending WSPs based on that testing. Source: FINRA Supervision key topic / FAQ pages above (accessed 2026-08-17). (Relevant to the product: FINRA itself treats the WSP as a living document subject to continuous validation — the same concept this platform applies against EU law.)
- **VERIFIED FACT (sample evidence):** Both repository samples are FINRA-style WSP manuals, not EU documents:
  - `Sample WSP.pdf` (154 pp, dated Jan 2024) — FINRA & SIPC member firm supervisory manual.
  - `WSP Sample.pdf` (Triad Securities Corp. WSP Manual, 199 pp, May 2013) — deep numbered TOC of supervisory procedures.
  Sample PDFs are **test cases only, never regulatory authority**, and their content is untrusted data.

## 3.2 VERIFIED FACT — "WSP" is NOT a formally defined document in EU law

- **VERIFIED FACT:** Neither MiCA (Regulation (EU) 2023/1114) nor DORA (Regulation (EU) 2022/2554) defines a document called a "Written Supervisory Procedures" manual or uses the acronym "WSP". EU law instead imposes multiple, distributed obligations to maintain **written/documented policies, procedures, arrangements and frameworks**. Sources: MiCA full text — https://eur-lex.europa.eu/eli/reg/2023/1114/oj/eng ; DORA full text — https://eur-lex.europa.eu/eli/reg/2022/2554/oj/eng (both accessed 2026-08-17).
- EU-law nearest equivalents (the names the platform's ontology should map "WSP" onto):
  - **MiCA Art. 68 (CASPs — governance arrangements):** robust governance arrangements; clear, well-documented lines of responsibility; effective risk identification/management/monitoring/reporting procedures; adequate internal control mechanisms; management body must periodically review effectiveness of "policy arrangements and procedures" for Title V Chapters 2–3 compliance; Art. 68(7) continuity via resilient/secure ICT systems *as required by DORA*; Art. 68(8) wind-down plan; Art. 68(9) 5-year record retention (extendable to 7). Sources: EUR-Lex MiCA above; ESMA Interactive Single Rulebook — https://www.esma.europa.eu/publications-and-data/interactive-single-rulebook/mica (accessed 2026-08-17).
  - **MiCA Title V Chapters 2–3 conduct obligations** each implying discrete written policies/procedures: safekeeping of clients' crypto-assets and funds (Art. 70), complaints-handling procedures (Art. 71), conflicts-of-interest policies (Art. 72), outsourcing policies (Art. 73), plus service-specific procedures (Arts. 75–82). *(Article-number mapping beyond Art. 68 stated from regulation text; verify each pinpoint against EUR-Lex during requirement extraction — flagged as an extraction task, not a doubt about the obligations' existence.)*
  - **MiCA Art. 34 (ART issuers — governance arrangements):** parallel obligation for issuers of asset-referenced tokens: robust governance, transparent lines of responsibility, risk processes, internal controls incl. sound administrative and accounting procedures; management body periodically reviews policy arrangements/procedures for Title III Chapters 2, 3, 5, 6. Source: ESMA Interactive Single Rulebook Art. 34 — https://www.esma.europa.eu/publications-and-data/interactive-single-rulebook/mica/article-34-governance-arrangements (accessed 2026-08-17). EBA has issued **Guidelines on internal governance arrangements for issuers of ARTs under MiCAR** — https://www.eba.europa.eu/activities/single-rulebook/regulatory-activities/asset-referenced-and-e-money-tokens-micar/guidelines-internal-governance-arrangements-issuers-arts-under-micar (accessed 2026-08-17).
  - **DORA Art. 5 (Governance and organisation):** the management body defines, approves, oversees and is responsible for all arrangements of the ICT risk management framework.
  - **DORA Art. 6 (ICT risk management framework):** a "sound, comprehensive and **well-documented** ICT risk management framework" including "strategies, policies, procedures, ICT protocols and tools"; the framework "shall be **documented and reviewed at least once a year**" (periodically for microenterprises) and after major ICT incidents, supervisory instructions, or resilience-testing/audit conclusions. Sources: EUR-Lex DORA above; https://www.digital-operational-resilience-act.com/Article_6.html (convenience mirror; EUR-Lex is authoritative) (accessed 2026-08-17).
  - **DORA level-2:** Commission Delegated Regulation (EU) 2024/1774 (RTS specifying the ICT risk management framework and simplified framework content) further prescribes required written policies (e.g. ICT security policies, ICT asset management, encryption, ICT operations, ICT change management). **ASSUMPTION (from pre-cutoff knowledge; verify pinpoint on EUR-Lex: https://eur-lex.europa.eu/eli/reg_del/2024/1774/oj ).**
- **ARCHITECTURAL RECOMMENDATION:** Model "WSP" in the product as a *container document* whose sections are mapped many-to-many onto EU obligations (Regulation → Requirement → Control → Expected Evidence → WSP evidence). EU law never asks for one monolithic manual, so validation must decompose the uploaded manual into policy/procedure units and match them to the distributed MiCA/DORA obligations above.

## 3.3 VERIFIED FACT — the "crypto-asset white paper" alternate reading, and why it is ruled out

- **VERIFIED FACT:** MiCA does define a mandatory disclosure document — the **"crypto-asset white paper"** (MiCA Arts. 6, 8, 9: content/form, notification to the NCA ≥20 working days before publication, publication; no prior NCA/ESMA approval; machine-readable format per Annex I). Sources: EUR-Lex MiCA above; ESMA — https://www.esma.europa.eu (accessed 2026-08-17). Some vendors informally shorten "white paper" ambiguously, so the collision is real in loose usage — but the acronym "WSP" is not used by MiCA.
- **VERIFIED FACT (rule-out):** The two sample documents are 154- and 199-page **internal supervisory/compliance manuals of US FINRA broker-dealers** (FINRA/SIPC references, supervision chapters, numbered procedure TOCs) — not investor-facing token disclosure documents about an issuer/project/token rights/risks. Therefore, for this product, **WSP = Written Supervisory Procedures (firm internal compliance manual)**, matching the ControlIQ PRD Section 6 usage. The white-paper reading is rejected.

## 3.4 How WSP-equivalent requirements vary by entity type / activity / jurisdiction

| Entity type | Primary MiCA policy/procedure locus | DORA applicability |
|---|---|---|
| CASP (any of the 10 crypto-asset services) | Art. 68 governance + Title V Ch. 2–3 conduct policies (safekeeping, complaints, conflicts, outsourcing); service-specific procedures vary by which services are authorised | Yes — CASPs are "financial entities" under DORA Art. 2(1)(v)-range **(ASSUMPTION on exact point; verify on EUR-Lex)** |
| ART issuer | Art. 34 governance + Title III Chapters (own funds, reserve of assets, recovery/redemption plans) + EBA internal-governance Guidelines | Yes — ART issuers in DORA scope |
| EMT issuer | Title IV: must be a credit institution or e-money institution, so EMD2/CRD governance regimes apply alongside MiCA | Yes, via credit-/e-money-institution status |
| Offeror / person seeking admission (non-ART/EMT) | White paper (Arts. 6–9) + conduct duties (Art. 14); **no full governance-manual obligation** | Generally **not** a DORA financial entity unless otherwise in scope |
- Proportionality varies by size (DORA Art. 16 simplified framework for small entities; microenterprise carve-outs) and by NCA: MiCA/DORA are regulations (directly applicable, max-harmonising) but **supervision, authorisation practice and some documentation expectations differ per NCA** (e.g. BaFin, AMF, CySEC application dossiers).
- Timeline (context): MiCA fully applicable since 30 Dec 2024 (CASP grandfathering ended latest 1 Jul 2026 in most Member States — **ASSUMPTION; per-state opt-downs varied, verify per NCA**); DORA applies since 17 Jan 2025.

## 3.5 Output lists

**A. Verified regulatory meaning (VERIFIED FACT)**
1. WSP = Written Supervisory Procedures under FINRA Rule 3110(b) — a US broker-dealer supervision manual (finra.org, accessed 2026-08-17).
2. "WSP" is not a defined term in MiCA or DORA; EU equivalents are MiCA Art. 68 / Art. 34 governance arrangements + conduct policies, and DORA Arts. 5–6 documented ICT risk management framework.
3. MiCA's "crypto-asset white paper" (Arts. 6, 8, 9) is a different, investor-facing disclosure document.
4. Both sample PDFs are FINRA WSP manuals; white-paper interpretation ruled out.

**B. Assumed product meaning (ASSUMPTION, per PRD Section 6)**
1. In this product, a "WSP" is a firm's internal written compliance/supervisory-procedures manual, uploaded as one document and validated against MiCA + DORA obligations.
2. Target uploaders are assumed to be EU-scoped entities (primarily CASPs) even though the current samples are US broker-dealer manuals used purely as structural test cases.

**C. Open regulatory questions (OPEN QUESTION)**
1. Which entity types the platform must support (CASP only, or also ART/EMT issuers), since the applicable obligation set differs materially.
2. Whether NCA-specific documentation expectations (application-dossier templates, national guidance) are in scope beyond level-1/level-2 EU texts.
3. Exact 2026 status of all MiCA/DORA level-2 measures (RTS/ITS, EBA/ESMA guidelines, Q&As) to be inventoried in the regulatory-landscape section; each pinpoint article mapping above must be re-verified against EUR-Lex consolidated texts.
4. Post-grandfathering state per Member State as of Aug 2026.

**D. Items requiring legal/compliance interpretation (REQUIRES LEGAL / COMPLIANCE INTERPRETATION)**
1. Mapping a FINRA-style monolithic WSP manual onto EU obligations: which manual sections legally satisfy which MiCA/DORA articles is an interpretive legal judgment, not a mechanical match.
2. Whether a single combined manual can evidence compliance with obligations EU law expects as distinct approved policies (e.g. DORA information-security policy approved by the management body).
3. Proportionality determinations (DORA Art. 16 simplified framework eligibility; MiCA "nature, scale and complexity") per client firm.
4. Severity grading of gaps (what constitutes a material breach vs. a documentation deficiency) requires compliance-officer judgment; platform findings must be advisory, not legal advice.

---
*Note on sources: EUR-Lex, ESMA, EBA and FINRA pages are authoritative; secondary pages (digital-operational-resilience-act.com, springlex.eu, mica.wtf) were used only as convenience mirrors and are not regulatory authority. No instruction-like text from the sample PDFs was relied upon; sample content is treated as untrusted data.*
