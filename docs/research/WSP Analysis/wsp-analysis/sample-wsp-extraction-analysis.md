# Sample WSP Extraction Analysis — Document Processing Tool Evaluation & MVP Pipeline

**Scope:** Technology evaluation for ingesting Written Supervisory Procedures (WSP) manuals into the Continuous Regulatory Compliance Validation Platform (MiCA / DORA validation). Covers brief Sections 12–13 (document processing / extraction stack). Grounded against the two real sample WSPs in this repo.

**Date:** 2026-08-17 · **Status:** Research / architecture only — no application code.

> **Terminology note (VERIFIED FACT):** In this product, "WSP" = *Written Supervisory Procedures* — a firm's internal compliance/supervision manual. The term originates in US FINRA broker-dealer practice (FINRA Rule 3110(b) requires written procedures). Both sample PDFs are FINRA-context US broker-dealer manuals, **not** MiCA crypto-asset white papers. The product applies the same document *genre* (internal compliance procedures manual) to EU CASPs/financial entities under MiCA (Reg. (EU) 2023/1114) and DORA (Reg. (EU) 2022/2554). Whether an EU CASP's "WSP-equivalent" (compliance manual, ICT policy set, governance arrangements under MiCA Art. 68 / DORA Art. 5–6) maps 1:1 onto the FINRA WSP format is an interpretive question — **REQUIRES LEGAL / COMPLIANCE INTERPRETATION**.

---

## 1. The two real samples — measured properties (VERIFIED FACT, probed locally 2026-08-17)

Probes: `pdfinfo`, `pdffonts`, `pdfimages -list`, `pdftotext -layout` (poppler), read-only. Samples were never modified.

| Property | `Sample WSP.pdf` | `WSP Sample.pdf` (Triad Securities Corp.) |
|---|---|---|
| Pages | 154 | 199 |
| Producer | PDFium (creation date Jun 2026 — likely a re-export of the Jan 2024 manual) | Microsoft Office Word 2007 (Jun 2013) |
| PDF version / tagged | 1.7, **untagged**, no structure tree | 1.5, **tagged** (`/StructTreeRoot` present) |
| Bookmarks (`/Outlines`) | **None** | **None** |
| Page size | 612×792 pt (US Letter) | 612×792 pt (US Letter) |
| Text layer | Full text-native; `pdftotext` yields ~56k words | Full text-native; ~72k words |
| Encryption / JS / forms | None | None |
| Images | 3 small raster images (logo p.1, one image p.122) — no scanned pages | Tiny decorative images only (2×2 px, p.15) — no scanned pages |
| Fonts | Embedded subsets (ArialMT, Calibri, TimesNewRoman); **SymbolMT has no ToUnicode map** | Mixed: **non-embedded** Times New Roman + embedded CID fonts; some without ToUnicode |
| TOC style | Flat chapter numbers `1`–`11` + **unnumbered** sub-headings ("Introduction:", "Background:") with dot-less page numbers | Deep numbered TOC, `1.0` / `2.4.7`-style; **797 numbered-heading lines** matched `^\d+\.\d+(\.\d+)?\s+[A-Z]` in extracted text; TOC prints **no page numbers** |
| Extraction artifacts observed | 16× `∑` glyphs (mis-mapped SymbolMT bullets/checkmarks — no ToUnicode); heavy `•` bullet use | Word-2007 smart quotes extract as `‖` (250×) and `―` (245×) instead of `"` — classic non-embedded-font cmap issue; needs a normalization pass |
| Tables | Mostly prose + bullet lists; supervisory-matrix content expressed as narrative ("Designated supervisor, …, reviews … monthly") rather than ruled tables | Same: responsibilities/frequency largely narrative, few true grid tables |

**Implications (VERIFIED FACT, sample-grounded):**
1. Both samples need **zero OCR** — a text-native fast path must exist; OCR-first pipelines waste money and degrade quality here.
2. **Neither PDF has bookmarks**, and only one is tagged → section detection must come from *text/layout heuristics*, not PDF structure metadata. The tagged Triad file's structure tree can be exploited when present, but cannot be relied on.
3. Two distinct heading regimes must both be handled: deep decimal numbering (`2.4.7`) and flat chapter + unnumbered bold sub-headings. A numbered-TOC parser alone fails on `Sample WSP.pdf`.
4. A **Unicode normalization / mojibake-repair step is mandatory** (`‖`→`"`, `―`→`"`/em-dash, `∑`→bullet) before claim extraction and embedding, or entity extraction quality suffers.
5. Table extraction is a *secondary* signal for these documents: obligations live mostly in prose and bullets. Do not over-invest in table ML for MVP; do preserve list structure.
6. Sample PDF text is **UNTRUSTED DATA**: any instruction-like strings inside must be ignored by LLM stages (prompt-injection surface). No injection strings were observed in probes, but the pipeline must treat WSP text as data-only (system-prompt hardening + no tool access for extraction prompts). ASSUMPTION: customer uploads will be similarly adversarial-capable.

---

## 2. Tool evaluation

Ratings: ●●● strong · ●●○ adequate · ●○○ weak/absent. Costs are list prices accessed 2026-08-17; cloud prices change — re-verify at procurement.

| Criterion | PyMuPDF | pypdf | Unstructured (OSS) | Apache Tika | Docling (IBM) | Azure Doc Intelligence | AWS Textract | Google Document AI | Tesseract |
|---|---|---|---|---|---|---|---|---|---|
| Text extraction quality (digital PDF) | ●●● | ●●○ | ●●○ (wraps pdfminer/PyMuPDF) | ●●○ (PDFBox) | ●●● | ●●● | ●●● | ●●● | n/a (raster only) |
| Table extraction | ●●○ (`find_tables`, rule-based) | ●○○ | ●●○ | ●○○ | ●●● (TableFormer DL model) | ●●● | ●●● (Tables feature) | ●●● | ●○○ |
| Layout / heading detection | ●●○ (font size/flags via `dict` output; DIY heuristics) | ●○○ | ●●○ (category tagging: Title/NarrativeText/ListItem) | ●○○ | ●●● (layout model + reading order + heading levels) | ●●● (Layout model, paragraph roles incl. `sectionHeading`) | ●●○ (Layout feature) | ●●● (Layout Parser) | ●○○ |
| Page refs + coordinates (evidence anchoring!) | ●●● (word/span bboxes) | ●○○ | ●●○ (element metadata w/ page no., coords) | ●○○ (page only) | ●●● (provenance: page + bbox per item) | ●●● (polygons + spans) | ●●● (geometry per block) | ●●● | ●●○ (hOCR boxes) |
| OCR for scanned docs | via Tesseract integration | ●○○ | via Tesseract | via Tesseract | pluggable (Tesseract/RapidOCR/…) | ●●● built-in | ●●● built-in | ●●● built-in | ●●○ |
| Multilingual (EU languages) | ●●● (Unicode-native) | ●●● | ●●○ | ●●● | ●●○ | ●●● | ●●○ (OCR lang coverage narrower) | ●●● (200+ langs OCR) | ●●○ (100+ lang packs, quality varies) |
| Cost per 1k pages | $0 (AGPL **or** commercial license — see note) | $0 (BSD) | $0 (Apache-2.0 OSS; paid API/serverless separate) | $0 (Apache-2.0) | $0 (MIT) | ~$10/1k (Layout); ~$1.50/1k (Read) | $15/1k (Tables; Layout free with Tables); ~$1.50/1k (DetectText) | $10/1k (Layout Parser); $1.50/1k (Enterprise OCR ≤5M) | $0 + compute |
| Scalability | High (fast C lib; ~154pp in <1s) | Medium | Medium (heavier deps) | High (JVM server mode) | Medium (DL models; GPU helps; ~seconds/page CPU) | Managed, quota-bound | Managed, async batch | Managed, batch | CPU-bound, parallelize |
| EU data residency / cloud dependency | **None — runs in our VPC** | None | None (OSS lib) | None | **None — fully local** | EU regions (West Europe, Sweden Central etc.); MSFT EU Data Boundary applies | EU regions exist (Frankfurt, Ireland, Paris, London) **but content may be stored cross-region for service improvement unless org opts out** — must set opt-out policy | EU multi-region processors available | None |
| Python integration | ●●● | ●●● | ●●● | ●●○ (server/REST or tika-python subprocess) | ●●● | ●●● (azure SDK) | ●●● (boto3) | ●●● | ●●● (pytesseract) |

**Licensing note (VERIFIED FACT / REQUIRES LEGAL REVIEW):** PyMuPDF is AGPL-3.0 with a paid commercial alternative from Artifex. For a closed-source SaaS backend, AGPL obligations must be assessed; a commercial license or substituting `pdfplumber`/pdfminer.six (MIT) is the mitigation. Docling is MIT, Unstructured OSS is Apache-2.0, Tika Apache-2.0, pypdf BSD — all safe.

### Per-tool notes (sample-grounded where possible)

- **PyMuPDF (fitz):** Best-in-class speed and span-level metadata (font name, size, bold flag, bbox per span) — exactly what the heading-detector needs for the untagged PDFium sample where numbering is absent at sub-heading level. `page.find_tables()` handles ruled tables; both samples have few, so adequate. **ARCHITECTURAL RECOMMENDATION:** core extractor, pending AGPL resolution.
- **pypdf:** Fine for metadata/split/merge/hashing utilities; text extraction lacks layout fidelity (no reliable reading-order or coordinates at span granularity). Utility role only.
- **Unstructured:** Convenient element typing (`Title`, `ListItem`) and chunking helpers (`chunk_by_title`), but its PDF path just wraps pdfminer/PyMuPDF + Detectron2-style layout models in `hi_res` mode (slow). Adds heavy deps for value we can replicate. Optional.
- **Apache Tika:** Unmatched *format breadth* (DOCX, legacy DOC, emails, ZIPs) and battle-tested content-type detection — useful at the upload/validation gate (MIME sniffing, "is this really a PDF?"), not as the primary PDF extractor. JVM dependency is the drawback.
- **Docling:** MIT-licensed, runs fully locally (no cloud upload — decisive for EU residency), DL layout + TableFormer table structure, reading-order recovery, heading levels, and **per-item provenance (page + bbox)** in its DoclingDocument model; exports Markdown/JSON; integrates with LangChain/LlamaIndex. Trained models reported within a few points of human accuracy on layout/table detection. Cost: compute only; CPU-viable at our volumes (a 199pp manual is minutes, not hours), GPU optional. **ARCHITECTURAL RECOMMENDATION: primary structure-aware parser.**
- **Azure Document Intelligence:** Layout model ($10/1k pages) returns paragraphs with roles (`title`, `sectionHeading`), tables, and polygon coordinates; strong built-in OCR; EU regions + Microsoft EU Data Boundary. Best cloud option *if* the platform already lands on Azure. 
- **AWS Textract:** High-quality Tables/Layout ($15/1k with Tables; Layout free when combined) and EU regions (Frankfurt, Ireland, Paris, London), **but** default service-improvement data handling can store content outside the processing region unless an organizational opt-out policy is set — must be configured before any production use. **REQUIRES LEGAL REVIEW** for GDPR/DORA outsourcing register implications.
- **Google Document AI:** Layout Parser $10/1k, Enterprise OCR $1.50/1k, EU multi-region processors; excellent multilingual OCR (200+ languages). Comparable to Azure; choice is mostly a cloud-alignment decision.
- **Tesseract (+ OCRmyPDF):** Free, local, EU-residency-clean OCR fallback. `ocrmypdf` produces searchable PDF/A with a text layer that then flows through the *same* text-native pipeline — keeps one downstream path. Quality below cloud OCR on poor scans; acceptable for MVP given scanned WSPs are the minority case (ASSUMPTION — validate with real customer uploads).
- **Cloud OCR generally:** reserve as an escalation tier for low-confidence Tesseract output, gated by an explicit per-tenant data-processing consent flag (EU residency + DORA third-party-risk considerations).

---

## 3. Recommended MVP pipeline (ARCHITECTURAL RECOMMENDATION)

```
upload → validation → malware scan → hash → version → parse → section detection
      → table extraction → claim/entity extraction → chunking → embedding → index
```

| Stage | Tooling | Notes (sample-grounded) |
|---|---|---|
| 1. Upload | Object storage (EU region), size cap (samples ~1.4 MB; cap 100 MB is generous), TLS | Store original immutably; never mutate (mirrors repo rule for samples). |
| 2. Validation | Apache Tika or `python-magic` MIME sniff; `pdfinfo`/pypdf sanity (page count, encryption, JS present?) | Both samples: no encryption, no JS, no forms — reject or quarantine PDFs with JS/embedded files. |
| 3. Malware scan | ClamAV container (local, no cloud) | Before any parser touches bytes. |
| 4. Hash | SHA-256 of bytes → dedupe + evidence integrity anchor | Findings cite `(doc_sha256, page, bbox)` — immutable evidence chain. |
| 5. Version | New hash ⇒ new document version; diff vs prior version at section level | WSPs are living documents ("updated throughout each calendar year" — Sample WSP.pdf p.1); incremental re-validation needs section-level diffing. |
| 6. Parse | **Text-native path:** Docling (structure, provenance) + PyMuPDF/pdfplumber (span-level font features). **Scanned path:** detect via chars-per-page threshold → OCRmyPDF/Tesseract → same text-native path. Cloud OCR (Azure/Google, EU region) as opt-in escalation. | Both samples take the text-native path; OCR trigger: <~100 extractable chars on a majority of pages. |
| 7. Section detection | Hybrid detector tuned to WSP manuals: (a) decimal-numbering grammar `\d+(\.\d+)*` (Triad: 797 numbered headings, 3 levels); (b) font-size/bold/position heuristics for unnumbered headings (Sample WSP: "Introduction:", "Background:"); (c) TOC reconciliation — parse TOC pages, match titles to body pages (Sample WSP's TOC has page numbers; Triad's does not — matching must work by title, not page); (d) use PDF structure tree when tagged. Output: section tree with `(section_id, number, title, page_start, page_end)`. | This is the platform's core evidence-addressing scheme ("WSP §2.4.4, p. 37"). |
| 8. Table extraction | Docling TableFormer primary; PyMuPDF `find_tables` cross-check | Low volume in both samples; preserve bullet lists as list elements — most obligations are prose/bullets. |
| 9. Claim/entity extraction | LLM over section-scoped text: extract obligations, named responsible persons/roles (e.g., "Designated supervisor … reviews customer account activity monthly" — WSP Sample.pdf §9.5.1), frequencies, evidence artifacts ("initialing the daily blotter"), rule citations. **Pre-step: Unicode normalization** (`‖ ― ∑` repairs). WSP text is untrusted → data-only prompts, no tools. | Entities: role, control, frequency, record produced, regulation cited. Mapping FINRA-style citations to MiCA/DORA articles is analytic, not extraction — REQUIRES LEGAL / COMPLIANCE INTERPRETATION. |
| 10. Chunking | Section-aware chunking (never split mid-section below ~1.5k tokens; parent-child: subsection chunks linked to section headers) | Deep numbering (2.4.7) gives natural chunk boundaries; flat-manual fallback uses detected heading spans. |
| 11. Embedding + index | EU-hosted or self-hosted embedding model; vector DB in EU region; metadata filters on `(doc_id, version, section_id, page)` | Every retrieval hit must carry page + section for evidence-backed findings. |

**Cost sanity (VERIFIED FACT, list prices):** an all-local stack (Docling + PyMuPDF + Tesseract) costs compute only; the cloud-layout alternative costs ~$10–15 per 1,000 pages — i.e., ~$2–3 per 200-page WSP, which is negligible per document but adds residency/vendor obligations. Local-first is recommended for MVP; cloud OCR as an opt-in fallback.

**OPEN QUESTIONS:** (1) Expected share of scanned/image-only WSP uploads? (2) Will customers upload DOCX (favors Tika/Docling multi-format ingest)? (3) AGPL posture → PyMuPDF license purchase vs pdfplumber substitution? (4) Which cloud the platform lands on (decides the OCR escalation vendor)? (5) Non-English WSPs expected at launch (affects embedding model choice)?

---

## Sources (accessed 2026-08-17)

- EUR-Lex, MiCA Reg. (EU) 2023/1114: https://eur-lex.europa.eu/eli/reg/2023/1114/oj — applicable in full since 2024-12-30.
- EUR-Lex, DORA Reg. (EU) 2022/2554: https://eur-lex.europa.eu/eli/reg/2022/2554/oj — applies since 2025-01-17.
- FINRA Rule 3110 (Supervision / WSP requirement): https://www.finra.org/rules-guidance/rulebooks/finra-rules/3110
- Azure AI Document Intelligence pricing (Layout ~$10/1k pages): https://azure.microsoft.com/en-us/pricing/details/ai-document-intelligence/ (corroborated: https://docuocr.com/blog/azure-document-intelligence-pricing)
- AWS Textract pricing (Tables $15/1k; Layout free with Tables): https://aws.amazon.com/textract/pricing/
- AWS Textract FAQs — cross-region storage for service improvement unless opt-out: https://aws.amazon.com/textract/faqs/
- Textract EU region availability: https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/
- Google Document AI pricing (Layout Parser $10/1k; Enterprise OCR $1.50/1k): https://cloud.google.com/document-ai/pricing
- Docling project (MIT, TableFormer, provenance): https://docling.org/ and https://github.com/docling-project/docling
- PyMuPDF licensing (AGPL/commercial): https://pymupdf.readthedocs.io/en/latest/about.html
- Apache Tika: https://tika.apache.org/ · Unstructured: https://github.com/Unstructured-IO/unstructured · OCRmyPDF: https://ocrmypdf.readthedocs.io/ · Tesseract: https://github.com/tesseract-ocr/tesseract

*Local probe evidence: poppler-utils (`pdfinfo`, `pdffonts`, `pdfimages`, `pdftotext -layout`) run read-only against the two sample PDFs on 2026-08-17; outputs summarized in Section 1. Blogs cited only as price corroboration, never as regulatory authority.*
