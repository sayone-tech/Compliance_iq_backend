# Structural Analysis — Sample WSP #2 ("WSP Sample.pdf", Triad Securities Corp.)

**Source file (READ-ONLY):** `/home/sayone-348/ClientProjects/Compliance_iq_backend/docs/research/WSP Analysis/WSP Sample.pdf`
**Analysis date:** 2026-08-17. Tooling: `pdfinfo`, `pdftotext -layout`, `pdffonts`, `pdfimages`, Python regex over extracted text.
**Status of document:** Test-case sample only — never regulatory authority. It is a **US FINRA broker-dealer Written Supervisory Procedures manual**, not an EU MiCA/DORA artifact. All mappings to MiCA/DORA concepts are analogical and flagged **REQUIRES LEGAL / COMPLIANCE INTERPRETATION**.

---

## 1. File & PDF metadata (VERIFIED FACT)

| Attribute | Value |
|---|---|
| Title (cover) | "TRIAD SECURITIES CORP. — WRITTEN SUPERVISORY PROCEDURES MANUAL" |
| Cover date | May 1, 2013 |
| Pages | 199 (pdftotext splits 200 due to trailing form feed) |
| Producer/Creator | Microsoft Office Word 2007 (native export, not scanned) |
| CreationDate = ModDate | 2013-06-05 01:30:52 IST (single-pass export; no incremental edits after export) |
| PDF version | 1.5, **Tagged: yes**, not encrypted, no forms, no JavaScript, no XMP metadata stream |
| Page size | 612×792 pt (US Letter), no rotation |
| File size | 1,400,265 bytes |
| Fonts | Mix of **non-embedded** Times New Roman & Arial (WinAnsi) plus embedded CID/Identity-H duplicates of the same faces; subset Baskerville Old Face (cover), Courier New, **Wingdings** (checkbox/bullet glyphs) |
| Images | Only tiny 2×2 indexed images with 600-dpi smasks (decorative shading artifacts); **no scanned content — text layer is authoritative** |
| Doc-info Title/Author | absent |

Printed footer page numbers (`- N -`) **exactly match physical PDF page numbers** (cover = uncounted p1; TOC footers -2- … -12-; body -13- … -199-). This is a gift for citation anchoring: `printed page == PDF page`.

## 2. Section inventory & numbering scheme (VERIFIED FACT)

Numbering: decimal hierarchy `N.0 / N.n / N.n.n` (e.g., 2.4.7), max observed depth 3. TOC spans pp2–12 (headings only, **no page numbers in TOC** — TOC is navigational by order only). Intro & abbreviations p13; body pp14–184; Appendices A–G pp185–199.

| # | Top-level section (body title) | Body pages | Notes |
|---|---|---|---|
| — | Introduction | 13 | Confidentiality clause; CO owns amendments w/ sr-mgmt approval |
| 1.0 | Designation of Supervisors | 14 | Dot-leader **name↔area table** (see §9 below) |
| 2.0 | General Employee Policies | 15–27 | 17 subsections incl. 2.16 Special Supervision, 2.17 Dual Registration |
| 3.0 | Training and Education | 28–30 | CE Regulatory/Firm Element |
| 4.0 | Registration and Licensing | 31–33 | U-4/U-5, Form BD, statutory disqualification |
| 5.0 | Communications with the Public (Amended 5/1/13) | 34–42 | FINRA 2210 retail/institutional taxonomy; complaints (5.4); Reg S-P (5.9) |
| 6.0 | Financial and Operations Procedures | 43–49 | Books & records, net capital, Reg T, OFAC (6.10) |
| 7.0 | Insider Trading | 50–56 | Chinese Wall, restricted/watch lists |
| 8.0 | Accounts | 57–64 | New-account docs, discretionary accounts |
| 9.0 | Orders | 65–73 | Suitability, prohibited transactions, Rule 144, Reg NMS (9.10) |
| 10.0 | Supervision (Amended 12/31/04) | 74 | CEO annual certification (FINRA 3130 analog); annual business review |
| 11.0 | **Branch Offices** (TOC says "BRANCHES") | 74–76 | OSJ designation, office inspections (11.7) |
| 12.0 | OTC Equity Trading | 76–95 | Best execution, short sales, limit orders, OATS, penny stocks |
| 13.0 | Corporate Fixed Income Trading | 96 | |
| 14.0 | Mutual Funds | 97–101 | Breakpoints, switching |
| 15.0 | Options (Amended 7/1/08) | 102–108 | ROSFP duties, position/exercise limits |
| 16.0 | Municipal Securities | 109–118 | MSRB G-rules, G-37 political contributions |
| 17.0 | Government Securities | 119–120 | |
| 18.0 | Anti-Money Laundering Procedures (Amended 10/1/10) | 121–141 | **Breaks the numbering scheme** — see §7 |
| 19.0 | Electronic Transmission of Orders (Added 10/1/04) | 142 | |
| 20.0 | Investment Banking, Public & Private Offerings, and Resales | 143–184 | Largest section (42 pp): underwriting, SPACs, ATM offerings, private placements/PIPEs, DPP/REITs, Rule 144, IPO restrictions (5130/5131 analog), M&A, fairness opinions |
| A–G | Appendices | 185–199 | A: RR annual certification agreement (p185); B: special-supervision list stub "SEE FILE" (p187); C: Branch Office Review log table (p188); D: OATS Trade Blotter Review log table (p189); E: MSRB G-37 affidavit form, 3 pp (p190); F: CIP Account/Customer Profile form (p197); G: Uncovered-options risk statement (p199) |

## 3. Representation forms present

1. **Prose policy paragraphs** (dominant form, ~90%).
2. **Dot-leader responsibility table** (p14): supervisory area → named individual(s), including a 3-person Best Execution committee.
3. **Bulleted lists** — mixed markers: plain indents, `o` bullets (p76), `•`(47×), Wingdings glyphs.
4. **Numbered inline lists** (e.g., "(1)…(9)" in Options §15, p104).
5. **Blank form/log templates** in Appendices C, D, E, F (underscore fill-ins, column headers like `Date | Result | Initials`).
6. **Certification/affidavit text** (Appendix A, E) with signature semantics.
7. **Cross-references** ("See Section 2.11", "See Appendix C/A") — machine-resolvable link graph.
8. **Amendment annotations embedded in headings**: "(Amended 5/1/13)", "(Added 11/15/02)" etc.
9. **URLs** (9 unique): treas.gov/fincen forms, OFAC SDN list, OECD FATF NCCT page, sec.gov, oats.finra.org, www.triadsecurities.com — all 2013-era, several now dead (link-rot detector candidate).
10. No true multi-column data grids in body (margin requirements are delegated: "available by contacting Operations", 6.4.4 p45 — an **evidence gap**, not a table).

## 4. Dates & version info (VERIFIED FACT)

- Cover date May 1, 2013; PDF exported Jun 5, 2013.
- **32 distinct inline amendment dates** spanning 11/15/02 → 5/1/13 in "(Added/Amended M/D/YY)" heading suffixes — a de-facto per-section change log. Same date appears in two formats ("4/1/10" and "4/1/2010") — date-normalization needed.
- No document-level version number, no revision-history table, no approval signature page for the manual itself (only employee-facing certifications). **Gap vs. product expectation of versioned WSPs.**
- Content is pre-2013-consolidation era: 67 "NASD" mentions (NASD Rules 3010, 3040, 3110, 2210, 2860…), 13 NYSE mentions, 2× superseded SEC Rule 11Ac1-6 (→ now Rule 606). A 2026 validator must flag **stale-rulebook citations** — deterministic check.

## 5. Supervisory topics & named individuals

Named designated supervisors (p14 table): Arthur Linden (Special Supervision, Annual Review, Trade Reporting†, Mutual Funds, Corporate Securities Sales, Options; appoints all supervisors), Cynthia DeMarco (Director of Compliance/CCO, Firm & Regulatory Element, Electronic Communication), Ray Holland (Branches), Darren Mattos (Trade Reporting† joint), Larry Goldsmith (AML Compliance Officer, Operations), Russell Campbell (FINOP). Best Execution = committee (Holland/Linden/DeMarco). Qualification: Series 24 required for supervisors. Mention distribution: Linden 16 pp, Goldsmith 6, Mattos 5, DeMarco 5, Campbell 2, Holland **1 (only p14)** — Branch supervisor never re-appears in the Branch section (see §10 c).

Exam series referenced: 7, 8, 24, 53, 62, 63, 79, 82.

## 6. AML / BCP / ICT content

- **AML: extensive** — §18, pp121–141 (21 pp, ~11% of manual): FinCEN 314(a) (13 mentions)/314(b), CIP (9), OFAC (13), SAR/SAR-SF (64 mentions), CTR, foreign correspondent/shell-bank due diligence, PEP/senior-foreign-political-figures, red-flag lists, independent testing (random-sampling scope, p141), AML training, clearing-firm reliance (14., p140). AML Compliance Person = Larry Goldsmith "with full responsibility" (p121).
- **BCP: essentially absent** — single mention (p44) that FINRA Web CRD contact data incl. "BCP Primary and Secondary Contact" must be updated within 17 business days of year-end (note in-document typo "Anuual"). **No business-continuity/disaster-recovery procedures at all.**
- **ICT/cyber: near-absent** — 2.10 Computer Records/Equipment/Software, 2.11 Electronic Communications (email/internet review, password mentions ×4), §19 e-order transmission. No incident response, no encryption, no cybersecurity, no third-party ICT-risk content. **For a DORA-style validator this sample would produce a near-total gap profile — useful negative test case.** (ASSUMPTION: US 2013 WSPs predate FINRA cyber sweep expectations; REQUIRES LEGAL/COMPLIANCE INTERPRETATION for any EU mapping.)

## 7. Regulatory citation inventory (counts in extracted text)

FINRA 145 | SEC 96 | NASD 67 | SAR 64 | FinCEN 34 | MSRB 29 | BSA/PATRIOT Act 20 | Rule 144 21 | SEA 17a-3/17a-4 15 | NYSE 13 | OFAC 13 | SIPC 12 | Reg S-P 7 | Reg NMS 4 | Reg T 3 | Reg SHO 1.
Distinct FINRA rules cited: 2010, 2111, 2210, 2310, 3230, 3270, 4511, 4530, 5110, 5130, 5150, 5160, 5190, 6600, 6710, 6730. NASD legacy rules: 1140, 2210, 2320, 2860, 3010, 3040, 3110, 3170. MSRB: G-8, G-9, G-14, G-15, G-30, G-37, G-38.
**Zero citations of any EU instrument** — as expected; every MiCA/DORA finding against this document is a mapping exercise, not literal citation matching.

## 8. Extraction hazards (Word-2007 tagged-PDF pipeline)

| Hazard | Evidence | Severity |
|---|---|---|
| **Smart-quote mojibake**: Word curly double quotes extract as U+2015 `―` (245×) and U+2016 `‖` (250×); apostrophe as `‘` (359×, wrong-side left single quote) | "―Compliance‖", "Firm‘s" throughout | High for string matching/dedup; normalize before NLP |
| Mixed WinAnsi + Identity-H encodings of the *same* fonts; several base fonts **not embedded** | pdffonts output | Medium (rendering variance across viewers; ToUnicode present so text extraction OK) |
| En-dash `–` (220×) used inside identifiers ("U–4", "G–37", "Mark–Ups") interchangeably with hyphen ("U-4", "G-37" both occur) | TOC vs body | High for citation regexes — must dash-fold |
| Heading/number concatenation: "20.1.1In General", "20.1.4Compensation Arrangements", "20.1.8Offerings…" (missing space) | §20 | Medium — heading regex must allow `\d(?=[A-Z])` |
| TOC≠body drift: "11.0 BRANCHES" vs body "11.0 BRANCH OFFICES"; "Office Inspection" vs "Office Inspections"; TOC lists 3.2.2 *and* 3.2.3 both as "Regulatory Element" while body collapses to "3.2.2 –3.2.3 Regulatory Element" (p29) | pp8, 74–76, 29 | Medium — don't treat TOC as ground truth |
| **§18 numbering collision**: AML section is a pasted FINRA small-firm-template with its own top-level list "1. Firm Policy … 20. Senior Manager Approval" (pp121–141). Bare "2." / "12." headings collide with manual sections 2.0/12.0 and with inline "(1)…(9)" lists | pp121–141 | **High** — hierarchical parser must scope-switch inside §18 |
| Unnumbered prose subheadings inside §18 ("Identity verification", "Recordkeeping", …) and headings split across lines ("…Foreign Bank / Accounts of Foreign Financial Institutions") | pp124–136 | Medium |
| Footer noise `- N -` interleaves with body text on every page; TOC has no page numbers so section→page map must be built from body scan | all pages | Low (regular pattern) |
| Wingdings-encoded checkbox glyphs and `o`-as-bullet; blank underscore form fields in appendices | pp76, 185–199 | Low–Medium (forms extract as sparse text; table structure of Appendix C/D headers collapses) |
| Typos usable as OCR-false-positive controls: "Anuual" (p44), "SUPERVISON" (p185) | | Info |
| Tagged PDF: structure tree exists (Word export) → heading roles potentially recoverable via a tag-aware parser (pdftotext ignores tags) | pdfinfo Tagged:yes | Opportunity |

**Prompt-injection check:** No instruction-like text addressed to an AI was observed in extracted content (VERIFIED over full text). Standard confidentiality notice on p13 only. Treat all PDF text as untrusted data regardless.

## 9. Deterministic vs semantic validation candidates

**Deterministic (regex/lookup, no LLM):**
- Presence/absence of mandated named roles (AML Officer, CCO, FINOP) and Series-24 qualification statements.
- Citation extraction + staleness check (NASD→FINRA rulebook map; SEC Rule 11Ac1-6→606; dead URLs).
- Amendment-date recency (`(Amended M/D/YY)` parse; latest = 5/1/13 → instantly flags "not reviewed in N years").
- TOC↔body heading reconciliation; numbering-continuity check (catches 3.2.2/3.2.3 dup, §18 scheme break, "20.1.1In" glue).
- Frequency-term inventory: daily 45, annual(ly) 69, monthly 19, quarterly 16, periodic(ally) 23; 51 lines pair "review"+frequency → extract (topic, frequency, owner) triples.
- Cross-reference resolution ("See Section 2.11", "See Appendix C") — dangling-link detection.
- Blank-form detection (Appendix B "SEE SPECIAL SUPERVISION FILE" = evidence placeholder, no actual evidence).

**Semantic (LLM/embedding required):**
- Mapping FINRA supervisory obligations to MiCA/DORA requirement taxonomy (pure analogy; REQUIRES LEGAL REVIEW).
- Detecting *coverage gaps* (no BCP, no incident response, no ICT third-party risk) — needs requirement→control ontology.
- Contradiction detection between prose passages (below), suitability-logic consistency, delegated-vs-retained responsibility reasoning ("may delegate; remains responsible", p13).
- Judging whether "periodically … in a cycle determined by the designated supervisor" (2.4.3, p17) satisfies a definite-frequency requirement (vagueness scoring).

## 10. Internal contradiction / inconsistency candidates (test-case seeds)

a. **Employee-account review frequency stated three ways**: 2.4.3 (p17) "periodically… cycle determined by supervisor" + daily clearing-firm report reviewed by compliance officer, vs 9.5.2 (p68) Mattos reviews account activity **monthly** with each account at least **annually**, vs 9.5.1 daily order-ticket review by Mattos *and* Linden. Overlapping but non-identical owners/frequencies.
b. **Electronic communications governed in two places** (2.11 pp21–23 and 5.7 p39) with different reviewer framing (designated supervisor vs "Compliance… ongoing basis"); 5.2.2 (p36) defers e-correspondence to §2.11 — 3-node cross-ref cycle, good contradiction-graph test.
c. **Branch supervision**: p14 assigns "Branches" to Ray Holland, but Holland never appears again; 11.7 (p76) makes "Compliance" (DeMarco) owner of the inspection program — designation-table vs body-responsibility mismatch.
d. **OSJ inspection "annually"** (11.7 p76) vs 10.3 annual review of business areas (p74) — overlapping scopes, single-owner ambiguity ("the designated supervisor" unnamed).
e. **AML dual-hat**: Goldsmith is both AML Officer and Operations supervisor (p14) while AML program monitors operations activity — segregation-of-duties finding (semantic).
f. TOC/body title drift and duplicate TOC entry (see §8) — deterministic contradictions.
g. §18 template retains "the firm" lowercase boilerplate and generic clearing-firm language vs manual's defined-term "Firm" — style/definition inconsistency signal of un-adapted template text.
h. Margin requirements not stated in WSP ("contact Operations", 6.4.4 p45) vs product expectation that controls carry expected evidence — evidence-externalization finding.

## 11. Extraction difficulty per feature (summary)

| Feature | Difficulty | Why |
|---|---|---|
| Page-anchored citations | **Easy** | footer N == PDF page N |
| Top-level & N.n headings | Easy–Medium | regular, but glue/typo cases in §20 |
| §18 AML substructure | **Hard** | foreign numbering scheme, unnumbered split headings |
| Supervisor table p14 | Medium | dot leaders + wrapped committee cell |
| Frequencies/owners triples | Medium | prose-embedded, vague terms |
| Appendix forms as evidence templates | Medium–Hard | collapsed table geometry, Wingdings |
| Citation normalization | Medium | dash/quote folding + legacy-rule mapping |
| Amendment-date changelog | Easy | consistent `(Added/Amended …)` pattern |

## 12. Comparison hooks vs Sample WSP #1 (`Sample WSP.pdf`)

Same genre (FINRA WSP) but opposite pipeline: #1 is 2024/PDFium/untagged/154pp; #2 is 2013/Word-2007/tagged/199pp with printed==physical page parity, deep 1.0/2.4.7 numbering, embedded amendment log, and a template-pasted AML section. Together they bound the parser design space: tag-aware structural extraction (worth building for #2-class docs) vs layout-only heuristics (#1-class).
