# Sample WSP Structure Analysis (Brief Section 6)

**Date:** 2026-08-17 · **Status:** Research/architecture only. Sources READ-ONLY; test cases, not authority.
**WSP1** = `Sample WSP.pdf` (WealthForge Securities, 154 pp, 2024) · **WSP2** = `WSP Sample.pdf` (Triad Securities Corp., 199 pp, 2013).
Evidence backing every claim below: `notes-sample-wsp-1.md`, `notes-sample-wsp-2.md`; tooling detail in `sample-wsp-extraction-analysis.md`.

---

## 1. WSP1 structure narrative (WealthForge)

A flat-chaptered manual: cover with two-bullet update notice (p.1), TOC (pp.2–7), eleven numbered chapters (pp.8–90), conclusion (p.90), then eight appendices (pp.91–154). The chapters carry single-level numbers (1–11) only; **everything below chapter level is an unnumbered bold heading** (~140 TOC entries, max 2 indent levels in the TOC). The appendices are the real substance for several domains: the AML program (Appendix A, pp.91–122, own revision date and DocuSign sign-off), the BCP (Appendix B, pp.123–135, own approval block), CE plan (C), compliance-position roster (D, p.142), branch-exam form (E), fairness opinions (H), non-traded REITs (J), rep cybersecurity policy (L). **Appendix letters F, G, I, K are absent** — evidence of removed appendices without re-lettering.

Structural signals available to a parser:
- **TOC page numbers are trustworthy:** printed page = physical PDF page (offset 0, verified pp.44, 91, 122–123, 136, 142). TOC entries are space-aligned (no dot leaders).
- **No PDF structure tree, no bookmarks** (untagged, PDFium re-export). Heading detection must come from font spans (bold runs, size, trailing colons) reconciled against the TOC.
- **Footnote system** (~69 notes) interleaves footnote bodies mid-paragraph at page breaks and glues superscript markers to words ("gratuity.44") — the dominant reading-order hazard.
- Appendices behave as **embedded sub-documents with independent metadata** (own dates, own signature blocks, own internal headings) — the section model must support component-level version attributes, not just document-level.

## 2. WSP2 structure narrative (Triad)

A deeply numbered manual: cover (p.1), TOC (pp.2–12, headings only, **no page numbers**), introduction + abbreviations (p.13), body sections 1.0–20.0 (pp.14–184), Appendices A–G (pp.185–199). Numbering is decimal `N.0 / N.n / N.n.n`, max depth 3, with 797 numbered heading lines in extracted text. Section 1.0 (p.14) is a dot-leader table assigning supervisory areas to named individuals. Headings embed a de-facto changelog: 32 distinct `(Added/Amended M/D/YY)` suffixes spanning 2002–2013.

The one structural break: **§18 AML (pp.121–141) is a pasted FINRA small-firm template with its own top-level "1.–20." numbering**, colliding with the manual's section numbers and containing unnumbered prose subheadings — a parser must detect the scope switch or it will corrupt the section tree.

Structural signals:
- **Printed footer `- N -` exactly equals physical page number** — citation anchoring is trivial.
- **Tagged PDF** (Word 2007 export, `/StructTreeRoot` present): heading roles are potentially recoverable via a tag-aware parser; plain `pdftotext` ignores tags. No bookmarks.
- TOC is order-only navigation: section→page map must be built from a body scan, matching by title with fuzz tolerance (TOC↔body drift: "BRANCHES" vs "BRANCH OFFICES"; duplicate TOC entries 3.2.2/3.2.3 collapsed in body p.29).
- Character-level hazards: smart-quote mojibake (`―` 245×, `‖` 250×, `‘` 359×), en-dash/hyphen variance in identifiers (U–4/U-4), glued heading numbers ("20.1.1In General").

## 3. Numbering schemes, side by side

| Property | WSP1 | WSP2 |
|---|---|---|
| Top level | `1`–`11` (+ lettered appendices with gaps) | `1.0`–`20.0` (+ appendices A–G, contiguous) |
| Depth | 1 numbered level; sub-structure via bold headings | 3 numbered levels (`2.4.7`) |
| Stability hazards | none in numbering itself; gaps in appendix letters | §18 foreign scheme; duplicate TOC numbers; glued numbers |
| TOC→page mapping | direct (numbers printed, offset 0) | must be derived (title match against body) |
| Changelog encoding | cover bullets + per-appendix dates | inline `(Added/Amended …)` per heading |

## 4. Section-detection implications (ARCHITECTURAL RECOMMENDATIONS)

1. **A single hybrid detector, four signal classes, per-document weighting:** (a) decimal-numbering grammar; (b) font-weight/size/position heuristics for unnumbered headings; (c) TOC reconciliation (page-number-driven for WSP1-class, title-match-driven for WSP2-class); (d) PDF structure tags when present. Neither sample supports bookmarks; neither signal class alone covers both samples.
2. **Scoped numbering contexts:** the parser needs a stack of numbering schemes so a pasted template (WSP2 §18) opens a child scope instead of colliding with the parent scheme. Trigger heuristics: numbering-style discontinuity + heading-title change + template boilerplate markers ("the firm" lowercase vs defined "Firm").
3. **Appendices are first-class components:** model them as child documents with their own `revision_date`, `approval_evidence`, and internal section trees (WSP1 App. A/B prove this is required). Completeness checks run on the letter/number sequence (detects WSP1's missing F/G/I/K).
4. **TOC is a claim, not ground truth:** always reconcile; report TOC↔body drift as findings (WSP2 drift cases), and tolerate title fuzz (case, singular/plural, dash/quote folding).
5. **Pre-parse normalization pass is mandatory** before heading regexes run: mojibake repair (`‖ ― ‘ ∑`), dash folding, de-gluing `\d(?=[A-Z])`, footnote-marker stripping, footer removal (`- N -`, bare centered integers).
6. **Page anchoring:** both samples have printed==physical page parity — but treat that as a per-document measured property (`page_offset`, verified during ingestion), not an assumption; evidence citations use `(doc_sha256, section_id, page, bbox)`.
7. **Output contract:** section tree of `(section_id, number_or_letter, title, page_start, page_end, parent_id, numbering_scope, component_metadata)` — this is the addressing scheme every downstream stage (chunking, claims, findings, incremental re-validation) keys on.
8. **Cross-reference graph:** both samples use resolvable internal references ("full program in Appendix A", "See Section 2.11", "See Appendix C") and *external* evidence pointers (WSP2 6.4.4 "contact Operations"; App. B "SEE FILE"). Resolve internal links into a graph (dangling-link detection is deterministic); classify external pointers as evidence-externalization findings.

## 5. Generalization caution

Two samples of one US genre bound but do not exhaust the design space (**ASSUMPTION**): EU CASP uploads may be multi-document policy suites, non-English, DOCX-born, or scanned. The detector must degrade gracefully (flat text + OCR path per `sample-wsp-extraction-analysis.md`) and record per-document structure confidence. Whether EU NCAs expect a consolidated WSP-style manual at all is an **OPEN QUESTION / REQUIRES LEGAL REVIEW** (see `../regulatory/wsp-meaning.md`).
