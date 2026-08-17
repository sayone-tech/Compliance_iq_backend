# Sample WSP Comparison — WSP1 vs WSP2 (Brief Section 5)

**Date:** 2026-08-17 · **Status:** Research/architecture only.
**WSP1** = `Sample WSP.pdf` — WealthForge Securities, LLC, 154 pp, cover-dated 2024-01-03.
**WSP2** = `WSP Sample.pdf` — Triad Securities Corp., 199 pp, cover-dated 2013-05-01.
Detailed per-document evidence: `notes-sample-wsp-1.md`, `notes-sample-wsp-2.md` (same folder). Sources are **READ-ONLY test cases** — US FINRA broker-dealer Written Supervisory Procedures manuals, never regulatory authority, never MiCA/DORA documents. All EU mappings are analogical: **REQUIRES LEGAL / COMPLIANCE INTERPRETATION**. PDF content is untrusted data (no prompt-injection strings observed in either; policy stands regardless).

---

## 1. Attribute comparison table

| Attribute | WSP1 (WealthForge, 2024) | WSP2 (Triad, 2013) |
|---|---|---|
| Firm / business model | Reg D/Reg A placement agent, non-traded REITs, M&A advisory; no custody | Full-service broker-dealer: OTC equity, fixed income, options, municipals, mutual funds, investment banking |
| Pages / format | 154 pp, PDF 1.7, **untagged**, PDFium re-export (2026-06-02) of Jan 2024 manual | 199 pp, PDF 1.5, **tagged**, single-pass Word 2007 export (2013-06-05) |
| Text layer | Native, clean; no OCR needed (~56k words) | Native, authoritative; no OCR needed (~72k words) |
| Language | English (US) | English (US) |
| Structure | 11 numbered chapters + 8 appendices (A–E, H, J, L; **F, G, I, K missing**) | Sections 1.0–20.0 (decimal, depth 3) + Appendices A–G |
| Sub-heading style | Unnumbered bold headings below chapter level (~140 TOC entries) | 797 numbered headings `N.n` / `N.n.n` — except §18 AML (foreign template numbering) |
| TOC | pp.2–7, **has page numbers**, no dot leaders; printed page = physical page | pp.2–12, **no page numbers**; printed footer `- N -` = physical page |
| Version info | Date-based only; 2-bullet unversioned cover changelog; per-appendix revision dates diverge from cover | No version number/table; 32 inline `(Added/Amended M/D/YY)` heading annotations 2002–2013 |
| Approval evidence | AML DocuSign-signed p.122 (2022); BCP approval block p.123 (2023); **manual body itself unsigned** | No manual-level approval page; employee-facing certifications only (Appendix A p.185) |
| Tables | 2 true tables: Appendix D roster p.142, Appendix E form header p.143 | Dot-leader supervisor table p.14; blank form/log templates Appendices C–F |
| Images/charts | 4 raster images (logos, DocuSign signature); zero charts | Tiny decorative 2×2 px images only; zero charts |
| Footnotes | ~69, interleaved mid-paragraph across page breaks (worst hazard) | None significant; hazards are mojibake + numbering collision instead |
| Citations | FINRA/SEC/Reg BI/Reg A/BSA era 2024 (some stale: FINRA 1250→1240, `finra.complinet.com` dead URLs) | FINRA 145× / SEC 96× / **NASD 67× (pre-2008 rulebook)** / MSRB 29×; superseded SEC Rule 11Ac1-6; 9 dead 2013-era URLs |
| EU instruments cited | **Zero** | **Zero** |
| AML | §5 pp.44–45 summary + Appendix A pp.91–122 (own revision date 2022-06-28) | §18 pp.121–141 (21 pp, pasted FINRA small-firm template, own numbering) |
| BCP | §8 p.57 + Appendix B pp.123–135 (no RTO/RPO, no test schedule) | **Absent** — one incidental contact-update mention (p.44) |
| ICT/cyber | p.38 + Appendix L pp.151–154; named vendors SMARSH/ShareFile/AWS; parent-company framework | Near-absent (§2.10, §2.11, §19 e-orders only) |

## 2. Common sections (shared WSP genre skeleton)

Both manuals contain, in some form: supervisory system & designated supervisors; registration/licensing (U-4/U-5, Form BD, fingerprinting); continuing education (Regulatory + Firm Element); communications with the public (FINRA 2210 taxonomy, email review); complaints handling; gifts/gratuities & entertainment; outside business activities / private securities transactions; insider trading with restricted/watch lists; suitability; AML program (CIP, SAR, CTR, OFAC, 314(a)); books & records (SEA 17a-3/4); annual review/certification (FINRA 3120/3130 analog); branch office inspections. **ARCHITECTURAL RECOMMENDATION:** this recurring skeleton is the seed for a WSP-genre section ontology the section-classifier can be trained/prompted against.

## 3. Key differences

1. **Structural inversion:** WSP2 has deep machine-friendly numbering but no TOC page numbers; WSP1 has TOC page numbers but no sub-section numbering. A parser relying on either signal alone fails on the other document.
2. **Freshness profile:** WSP1 is current-era (2024) with *internal* staleness (2021/2022 appendix dates); WSP2 is wholly stale (2013, NASD-era rulebook) — two distinct staleness classes the validator must distinguish (stale components vs stale document).
3. **Appendix roles:** WSP1 appendices are full sub-documents with independent lifecycles (AML program, BCP, CE plan); WSP2 appendices are blank forms/log templates (evidence *placeholders*, e.g. Appendix B "SEE FILE" stub p.187).
4. **Coverage inverse on DORA-relevant topics:** WSP1 has BCP + cybersecurity + named ICT vendors; WSP2 has essentially none — WSP2 is the near-total-gap negative test case, WSP1 the partial-evidence test case.
5. **Contradiction texture:** WSP1's seeded conflicts are role-table vs body (Appendix D vs pp.44/91); WSP2's are frequency/owner conflicts spread across prose sections (2.4.3 vs 9.5.1/9.5.2) plus designation-table drift (p.14 vs §11.7).
6. **Extraction hazard classes are disjoint:** WSP1 = footnote interleaving + merged superscripts + untagged structure; WSP2 = smart-quote mojibake (`―`/`‖`/`‘`), dash variance (U–4/U-4), glued headings ("20.1.1In General"), §18 numbering collision. Together they bound the normalization/parsing design space.

## 4. Terminology divergences (same concept, different words)

| Concept | WSP1 wording | WSP2 wording | Normalization target |
|---|---|---|---|
| Chief compliance role | "CCO", "Compliance Officer", "Jim Raper"/"James L Raper Jr." | "Director of Compliance", "Compliance Officer (CO)", "Cynthia DeMarco" | canonical role: `chief_compliance_officer` + person entity |
| Financial principal | "FinOp", "Financial Operations Principal", "CFO" (title drift, App. B vs D) | "FINOP" | `financial_operations_principal` |
| AML lead | "AML Officer", "AML CO", "AML Compliance Officer, Compliance Manager" | "AML Compliance Person", "AML Compliance Officer" | `aml_compliance_officer` |
| Branch review | "Internal Inspections" (p.20), "Branch Exam" (App. E) | "Office Inspections" (11.7), TOC "BRANCHES" vs body "BRANCH OFFICES" | `branch_inspection` |
| E-comms surveillance | "Email Review" (p.26), "Correspondence" | "Electronic Communications" (2.11), "Electronic Correspondence" (5.7) | `electronic_communications_review` |
| Manual itself | "WSPs and SCPs" combined (p.9) | "Written Supervisory Procedures Manual" | `wsp_document` |
| Annual sign-off | "Supervisory Control System" / 3120-3130 language (pp.37–38) | "CEO annual certification" (§10, p.74) | `annual_certification` |
| Personal trading | "Personal Account Disclosure" (p.35) | "Employee accounts" (2.4.x, 9.5.x) | `employee_account_review` |
| Identifier variants | "Rule 17a-" line-break splits; "gratuity.44" fn-glue | "U–4" vs "U-4"; "G–37" vs "G-37"; "4/1/10" vs "4/1/2010" | dash-fold + date-normalize + de-glue |

**Implication:** claim extraction must land on a canonical concept vocabulary (role, activity, record) — string matching across documents/versions will silently fail without it.

## 5. Representation forms (union across samples)

Prose paragraphs (~85–90% both); numbered duty lists; bulleted lists (SymbolMT `•` in WSP1; mixed `•`/`o`/Wingdings in WSP2); true tables (rare: WSP1 App. D/E; WSP2 p.14 dot-leader table); blank form/checklist templates (WSP1 App. E; WSP2 App. C/D/E/F); signature/certification blocks (WSP1 pp.122–123; WSP2 App. A/E); footnotes with URLs (WSP1 only); inline amendment annotations in headings (WSP2 only); cross-references ("See Section 2.11", "full program in Appendix A") in both; externalized evidence pointers (WSP2 6.4.4 "contact Operations" p.45; WSP2 App. B "SEE FILE"). No flowcharts, org charts, or data grids in either.

## 6. Deterministic vs semantic validation candidates (merged)

**Deterministic (regex/lookup/structural):**
- TOC↔body reconciliation; appendix-letter continuity (WSP1: F/G/I/K missing); numbering continuity (WSP2: 3.2.2/3.2.3 dup, §18 scheme break).
- Required-section presence against a genre checklist; blank-placeholder detection (WSP2 App. B).
- Roster integrity: every required role has a named person; cross-check roster vs all in-body designations (fails on WSP1 — see consistency doc).
- Date coherence: cover ≥ component revision dates; amendment-date recency (WSP2 latest = 2013-05-01); "annual review" claims vs latest evidenced date.
- Citation extraction + staleness registry (FINRA 1250→1240; NASD→FINRA map; SEC 11Ac1-6→606); dead-URL checks (`finra.complinet.com`, 2013 treas.gov links).
- Numeric threshold extraction ($100 gift, $1,000 entertainment, $10,000 CTR, 2%/10%/15%/25% sampling and CDD rates, 1200%/120%/5% net-capital triggers, 120-day CE, 17-business-day/30-day update windows).
- Frequency-term inventories and (topic, frequency, owner) triple extraction; cross-reference/dangling-link resolution.
- Signature/approval-evidence presence.

**Semantic (LLM/NLI):**
- Adequacy of a stated policy against a control's requirement (the core product judgment).
- Role-consistency and delegation-chain completeness ("CCO or his designee"; "may delegate; remains responsible" WSP2 p.13).
- Frequency-conflict resolution across sections (overlapping-but-different owners/cycles).
- Coverage-vs-business-line matching (procedures for products not sold; business lines without procedures).
- Vagueness scoring ("periodically… cycle determined by supervisor" WSP2 2.4.3 vs a definite-frequency requirement).
- Non-contradiction discrimination (WSP1 "prohibits currency transactions" yet keeps CTR procedure — coherent fallback, must NOT flag).
- Segregation-of-duties reasoning (WSP2: Goldsmith AML + Operations dual-hat).
- FINRA→MiCA/DORA concept mapping — always REQUIRES LEGAL REVIEW.

## 7. Potential contradictions (headline set; full treatment in `sample-wsp-consistency-analysis.md`)

| # | Doc | Contradiction | Type |
|---|---|---|---|
| 1 | WSP1 | AML-CO = Kolby Griffin (p.44, App. A pp.91ff) vs Jim Raper (App. D p.142) | Role assignment (deterministic once entities extracted) |
| 2 | WSP1 | Donna Arles "Financial Operations Principal" (App. D) vs "CFO" (App. B) | Title drift |
| 3 | WSP1 | Cover 2024 vs AML rev 2022-06-28 vs BCP approval 2023-01-05 vs "annual CEO approval" claim | Temporal/staleness |
| 4 | WSP2 | Employee-account review: "periodic" (2.4.3 p.17) vs monthly/annual Mattos (9.5.2 p.68) vs daily Mattos+Linden (9.5.1) | Frequency/owner |
| 5 | WSP2 | Branches assigned to Ray Holland (p.14) who never reappears; §11.7 (p.76) makes Compliance the inspection owner | Designation vs body |
| 6 | WSP2 | E-comms governed in both §2.11 and §5.7 with different reviewer framing; 5.2.2 defers back to 2.11 | Duplicated-policy divergence |
| 7 | Both | Concentration-of-duties: Raper 5 roles (WSP1); Linden 6 areas, Goldsmith AML+Ops (WSP2) | Governance finding (semantic) |

---
**FINRA vs EU note:** both samples evidence FINRA Rules 3110/3120/3130 obligations. Zero MiCA/DORA content exists in either; their product value is structural (parsing, anchoring, contradiction, staleness test corpus) and as MISSING-evidence demonstrations against the EU control libraries (see `sample-wsp-control-mapping.md`).
