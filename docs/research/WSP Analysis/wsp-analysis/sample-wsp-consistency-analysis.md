# Sample WSP Consistency Analysis — Contradiction Detection & Claim Extraction Design (Brief Section 20)

**Date:** 2026-08-17 · **Status:** Research/architecture only.
**WSP1** = `Sample WSP.pdf` (WealthForge, 154 pp, 2024) · **WSP2** = `WSP Sample.pdf` (Triad, 199 pp, 2013).
Evidence base: `notes-sample-wsp-1.md` §8, `notes-sample-wsp-2.md` §10 (verified against the PDFs). Samples are test cases only; PDF text is untrusted data.

---

## 1. Realistic contradiction inventory (found in the samples, VERIFIED)

These are naturally occurring inconsistencies in real FINRA manuals — exactly the fault classes the product must detect in EU CASP documents.

### 1.1 Role/designation conflicts

| ID | Doc | Evidence | Description | Detection tier |
|---|---|---|---|---|
| C-01 | WSP1 | p.44 + App. A pp.91, ~103 vs App. D p.142 | **AML-CO identity conflict:** body + signed AML program designate Kolby Griffin (designated 2021-04-12, signed 2022-02-03); Compliance Positions roster lists Jim Raper. Highest-value seeded finding — direct role-assignment contradiction inside one document | Deterministic once role-claims extracted (same canonical role, two person entities) |
| C-02 | WSP1 | App. D p.142 vs App. B ~p.126 | **Title drift:** Donna Arles = "Financial Operations Principal" vs "CFO" | Deterministic (entity + title tuple mismatch) — but severity needs semantic judgment (alias vs conflict) |
| C-03 | WSP1 | App. D p.142 | **Concentration of duties:** James L Raper Jr. holds CCO + Executive Rep + DR Coordinator + Reg BI + Senior Investor Specialist (5 roles) | Semantic governance finding (aggregation over role claims) |
| C-04 | WSP2 | p.14 vs §11.7 p.76 | **Orphan designation:** Ray Holland assigned "Branches" on p.14, never mentioned again; §11.7 makes Compliance (DeMarco) owner of office inspections | Hybrid: mention-count = deterministic signal; ownership conflict = semantic |
| C-05 | WSP2 | p.14 | **Segregation-of-duties:** Goldsmith is both AML Officer and Operations supervisor while the AML program monitors operations activity | Semantic (requires role-incompatibility knowledge) |

### 1.2 Frequency/obligation conflicts

| ID | Doc | Evidence | Description | Detection tier |
|---|---|---|---|---|
| C-06 | WSP2 | §2.4.3 p.17 vs §9.5.1/§9.5.2 p.68 | **Employee-account review stated three ways:** "periodically… cycle determined by supervisor" vs Mattos monthly/each-account-annually vs daily order-ticket review by Mattos AND Linden — overlapping, non-identical owners and cycles | Hybrid: (topic, frequency, owner) triple comparison + semantic scope disambiguation |
| C-07 | WSP2 | §2.11 pp.21–23 vs §5.7 p.39 vs §5.2.2 p.36 | **Duplicated-policy divergence:** e-comms governed in two places with different reviewer framing; 5.2.2 defers back to 2.11 — a 3-node cross-reference cycle | Hybrid: cross-ref graph detects duplication; divergence judgment is semantic |
| C-08 | WSP1 | §8 p.57 vs App. B pp.123–135 | Summary-vs-appendix drift risk: BCP summary and full plan each state review commitments — must be compared every revision | Semantic (NLI between paired sections) |
| C-09 | WSP2 | §11.7 p.76 vs §10.3 p.74 | OSJ inspection "annually" vs annual business review — overlapping scopes, "the designated supervisor" unnamed | Semantic (vagueness + owner-resolution) |

### 1.3 Temporal/staleness conflicts

| ID | Doc | Evidence | Description | Detection tier |
|---|---|---|---|---|
| C-10 | WSP1 | p.1 vs App. A p.91 ("Last Revision June 28, 2022") vs App. B p.123 (approved 2023-01-05) vs AML-CO designation 2021-04-12 | **Component staleness chain:** cover claims Jan 2024 currency; "annual CEO approval of AML program" (pp.44/91) has no post-2022 evidence in-document | Deterministic (date extraction + ordering rules: cover ≥ component dates; claimed cycle vs latest evidenced date) |
| C-11 | WSP2 | heading annotations, latest 5/1/13 | Whole-document staleness: latest amendment 2013; NASD-era rulebook (67 mentions), superseded SEC 11Ac1-6 | Deterministic (amendment-date recency + superseded-rule registry) |
| C-12 | WSP1 | App. C pp.136–141 | FINRA Rule 1250 cited though superseded by Rule 1240 (CE transformation, eff. 2022) — stale citation inside a current-era document | Deterministic (citation registry lookup) |

### 1.4 Repetition-drift and non-contradiction controls

- **R-01 (WSP1):** "10% of subscribers processed each day" appears 3× (pp.~41, 72, 149) — consistent today; classic future-drift monitor: track repeated claims across versions and alert when one instance changes.
- **N-01 (WSP1, must-NOT-flag):** "WFS prohibits transactions involving currency" yet maintains a CTR filing procedure — an internally coherent prohibition+fallback pair. Calibration case for the NLI tier: contradiction detectors that fire here are over-triggering.
- **N-02 (WSP1, must-verify-not-flag):** CCO reviews all email incl. CEO's; CEO reviews the CCO's email (pp.26–27) — a valid reviewer cycle, correct because CEO ≠ CCO in App. D (Robbins ≠ Raper). The check is conditional: it *becomes* a finding only if roster shows the same person in both roles.

## 2. Claim extraction design (ARCHITECTURAL RECOMMENDATION)

Contradiction detection = extract structured claims → normalize → compare. LLM extraction per chunk emits typed claims; comparison is then mostly deterministic set logic, with an NLI/LLM tier for prose-level conflicts.

### 2.1 Claim type schema

```json
{
  "claim_id": "uuid",
  "wsp_version_id": "…",
  "type": "role_assignment | obligation | frequency | threshold | date_assertion | citation | cross_reference | prohibition | delegation",
  "subject": {"person": "kolby_griffin", "raw": "Kolby Griffin"},
  "predicate": "holds_role | must_perform | reviews | approves | retains | prohibits | designates | refers_to",
  "object": {"canonical": "aml_compliance_officer", "raw": "AML Officer, Compliance Manager"},
  "qualifiers": {"frequency": "P1Y", "frequency_raw": "annually", "threshold": {"value": 100, "unit": "USD"}, "effective_date": "2021-04-12", "scope": "employee accounts", "condition": "…"},
  "provenance": {"chunk_id": "…", "section_id": "…", "page": 44, "char_span": [1234, 1310], "quoted_span": "…"},
  "confidence": 0.93
}
```

Every claim keeps `raw` surface forms beside canonical values (auditability + the verbatim span check from `../ai/rag-architecture.md`).

### 2.2 Normalization layers (all sample-motivated)

1. **Character:** mojibake repair (`―`/`‖`/`‘` in WSP2, `∑` in WSP1), dash folding (U–4→U-4), heading de-glue (`20.1.1In`), footnote-marker stripping ("gratuity.44"). Runs pre-extraction (see `sample-wsp-extraction-analysis.md`).
2. **Date:** "January 3rd, 2024" / "2/6/03" / "4/1/10" vs "4/1/2010" → ISO-8601; ambiguity flag for 2-digit years.
3. **Frequency:** "annually"/"each year"/"at least annually" → ISO-8601 duration (P1Y) + modifier (`at_least`, `at_most`, `exact`, `vague`); "periodically"/"regular basis"/"as appropriate" → `vague:true` (vagueness itself is a finding class, C-06/C-09).
4. **Role canonicalization:** controlled vocabulary seeded from the samples (`chief_compliance_officer` ← "CCO"/"Director of Compliance"/"Compliance Officer"; `financial_operations_principal` ← "FinOp"/"FINOP"/"CFO"-as-drift; `aml_compliance_officer` ← "AML CO"/"AML Compliance Person"; full table in `sample-wsp-comparison.md` §4). Unmapped titles get provisional canonical IDs + review queue.
5. **Person entity resolution:** within one document, cluster name variants ("Jim Raper" = "James L Raper Jr." — nickname + suffix handling). Conservative: merge only on high-confidence match; C-01 only surfaces if Griffin ≠ Raper resolution holds.
6. **Citation normalization:** rule-ID grammar per regime (FINRA/SEC/NASD/MSRB now; MiCA `Art. 68(4)`, DORA, CDR/CIR numbers for production) + supersession registry (1250→1240, NASD→FINRA map, 11Ac1-6→606; EU analog: repealed/amended article registry from the ingestion pipeline in `../regulatory/regulatory-ingestion.md`).

### 2.3 Comparison engine

- **Deterministic joins (tier 1):** group claims by `(canonical_role)` → conflicting persons (C-01); by `(person)` → title sets (C-02) and role-count aggregates (C-03); by `(topic, obligation)` → frequency/owner sets (C-06 candidates); date-ordering rules (C-10); registry lookups (C-11/C-12); roster-vs-body mention join (C-04 signal); repeated-claim clustering for drift monitoring (R-01).
- **Semantic tier (tier 2):** candidate pairs from tier 1 that need scope disambiguation ("daily order-ticket review" vs "monthly account review" may be different obligations on the same topic — C-06), plus NLI over section pairs flagged by the cross-ref/duplication graph (C-07, C-08). Prohibition-vs-procedure pairs route through a coherence prompt calibrated on N-01.
- **Conditional checks (tier 3):** rules parameterized by other extractions (N-02 fires only if roster resolves CEO = CCO).
- **Output:** contradiction findings carry both claims' full provenance (two page/section anchors minimum), a conflict type, severity (role-conflict on a mandated function like AML-CO = high; title drift = low/medium), and a dedupe key stable across re-validations.

### 2.4 Severity guidance (ASSUMPTION, calibrate with compliance experts)

- **High:** conflicting designation of a regulatorily mandated function (C-01 analog for MiCA Art. 68 governance/DORA Art. 5 roles); claimed-cycle-without-evidence on a mandatory review (C-10).
- **Medium:** frequency conflicts on supervisory obligations (C-06); duplicated-policy divergence (C-07); orphan designations (C-04); stale citations in a current document (C-12).
- **Low:** title drift (C-02), TOC↔body drift, style inconsistencies (§18 un-adapted template boilerplate, WSP2).
- Concentration/segregation findings (C-03, C-05): **REQUIRES LEGAL / COMPLIANCE INTERPRETATION** — proportionality-dependent (small firms legitimately dual-hat; DORA Art. 4 / microenterprise context).

## 3. Golden-set contribution

The inventory above yields 12 positive contradiction cases, 2 negative controls (N-01, N-02), and 1 drift monitor (R-01) — seed labels for the evaluation harness in `../security/llm-security-governance.md` (golden set) with known page/section ground truth in both samples.

## 4. Limits

Two same-genre US documents cannot validate EU-specific conflict classes (e.g., conflicting DORA incident-reporting deadlines across policy suites) — synthetic EU-flavored fixtures are required (**OPEN QUESTION:** fixture authoring plan). Person-resolution across *documents* (policy suite uploads) is unaddressed by these samples (**ASSUMPTION:** in-document resolution ships first).
