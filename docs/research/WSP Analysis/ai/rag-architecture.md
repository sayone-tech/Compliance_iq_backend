# RAG / LLM Evaluation Architecture for WSP Compliance Validation

**Sections 17–19 (brief) + supporting research** — Continuous Regulatory Compliance Validation Platform
**Date:** 2026-08-17 · **Status:** Research / architecture only (no application code)
**Scope:** How to ingest 150–200pp Written Supervisory Procedures (WSP) manuals, retrieve evidence, and produce evidence-backed PASS/PARTIAL/FAIL findings against MiCA (EU 2023/1114) and DORA (EU 2022/2554) requirements.

> **Terminology note (VERIFIED FACT):** In this product a "WSP" is a US FINRA-style *Written Supervisory Procedures* manual — a firm's internal compliance/supervision manual — NOT a MiCA crypto-asset white paper. Both sample documents in this repo are FINRA broker-dealer WSPs: `Sample WSP.pdf` (154pp, Jan 2024, untagged PDF 1.7, PDFium producer) and `WSP Sample.pdf` (Triad Securities Corp., 199pp, May 2013, tagged PDF 1.5, Word 2007, deep numbered TOC like `2.4.7`). They are **test cases only, never regulatory authority**. Authority flows: Official Regulation → Requirement → Control → Expected Evidence → WSP evidence. Applying FINRA-style manuals to EU MiCA/DORA obligations involves interpretive mapping — **REQUIRES LEGAL / COMPLIANCE INTERPRETATION**.

---

## 17. Document Ingestion & Chunking

### 17.1 Section-aware, page-aware chunking (ARCHITECTURAL RECOMMENDATION)

Policy manuals of 150–200pp are hierarchical documents. Naive fixed-size chunking destroys the section identity that findings must cite. Recommended pipeline:

1. **Layout-preserving extraction.** Use a layout-aware extractor (e.g., Docling, Unstructured, Azure Document Intelligence self-hosted equivalent, or PyMuPDF + heuristics) that emits text blocks with `(page_number, bbox, font_size, style)`. The two samples differ materially: `WSP Sample.pdf` is a *tagged* PDF with a real structure tree and numbered TOC — heading extraction is reliable; `Sample WSP.pdf` is *untagged* (PDFium-produced), so headings must be inferred from font-size/weight/numbering regexes. Build both paths; treat tagged structure as preferred signal. (VERIFIED FACT about the samples; recommendation is architectural.)
2. **TOC-driven section tree.** Parse numbered headings (`1.0`, `2.4.7`) into a section tree. Every chunk carries `section_id`, `section_title`, `section_path` (e.g., `2.4 > 2.4.7`), `page_start`, `page_end`, and character offsets. Cross-validate against the PDF TOC/bookmarks when present.
3. **Chunk sizing.** Chunk at paragraph/subsection boundaries, target ~400–800 tokens, hard max ~1,024, with small overlap only within a section (never across section boundaries). Keep a parallel "parent section" text for parent-document retrieval (retrieve child chunk → expand to enclosing subsection for generation context).
4. **Table handling.** WSPs contain supervisory-responsibility matrices (who reviews what, how often, evidenced how). Extract tables as distinct chunk type: serialize to Markdown/HTML preserving header rows; prepend a generated one-sentence table description; never split a table row across chunks; if a table exceeds the chunk budget, repeat header row in each slice. Store the raw cell grid too, for the evidence-verification step (§19.4).
5. **Contextual retrieval enrichment.** Prepend a 50–100-token LLM-generated context ("This chunk is from Section 3.2 'Anti-Money-Laundering Procedures' of the Triad Securities WSP manual and covers …") to every chunk *before* embedding and BM25 indexing. Anthropic reports contextual embeddings + contextual BM25 cut retrieval failures ~49%, and ~67% with reranking added (VERIFIED FACT per vendor benchmark; source: Anthropic engineering post, https://www.anthropic.com/engineering/contextual-retrieval, accessed 2026-08-17).
6. **Immutable provenance.** Each chunk stores `document_id`, `document_sha256`, `document_version`, page(s), section path, char offsets. Findings cite `filename + page + section` — offsets make citations machine-verifiable (§19.4).

### 17.2 Embedding model choice (EU-hostable)

Data-residency constraint: WSPs are confidential firm compliance manuals; embeddings should be computed in EU infrastructure or self-hosted. (ASSUMPTION: client requires EU residency — confirm; OPEN QUESTION for DPA/GDPR Art. 28 review.)

Candidates (2026 landscape):
- **BGE-M3** (BAAI, open weights, MIT-style license): dense + sparse + multi-vector in one model, 100+ languages, 8k context — practical self-hosted default for regulatory text. (Source: Milvus/BentoML 2026 embedding guides, https://milvus.io/blog/choose-embedding-model-rag-2026.md, accessed 2026-08-17.)
- **Qwen3-Embedding** (open weights): top multilingual MTEB scores in 2026 comparisons; heavier to serve.
- **multilingual-e5-large-instruct**: solid, lighter fallback.
- **Caution:** jina-embeddings-v3 is CC-BY-NC — not usable commercially without a license (VERIFIED FACT per license terms cited in the same guides).
- Managed EU-region alternatives (Azure OpenAI EU region, Mistral embed on EU infra) acceptable if DPA terms fit — REQUIRES LEGAL REVIEW.

**Recommendation:** BGE-M3 self-hosted (or EU-region managed equivalent), 1024-d dense vectors in pgvector, with its sparse output optionally reused for lexical signal. Pin the embedding model version; re-embedding is a versioned migration (see eval records, security doc §32).

## 18. Retrieval & Generation

### 18.1 Hybrid retrieval (ARCHITECTURAL RECOMMENDATION)

- **Dense:** pgvector (HNSW) in the existing Postgres — operationally cheapest, adequate at this corpus scale (hundreds of firms × ~1–2k chunks each, tenant-filtered).
- **Lexical:** BM25. Options: OpenSearch alongside Postgres, or Postgres-native (`tsvector` ranking or the ParadeDB/pg_search BM25 extension) to avoid a second datastore. Lexical matters for compliance: exact terms of art ("ICT third-party service provider", "Article 17", "AMLCO") must match exactly.
- **Fusion:** Reciprocal Rank Fusion (RRF) of dense + BM25 lists; retrieve ~50–150 candidates per requirement query.
- **Reranking:** cross-encoder reranker (self-hostable: BGE-reranker-v2-m3; managed: Cohere Rerank EU) → top 10–20 chunks. Reranking is the single highest-leverage addition per Anthropic's numbers.
- **Query formulation:** queries are generated per **Control** from the regulatory hierarchy (Requirement → Control → Expected Evidence), not free-form user questions. Each control ships with curated query templates + synonym expansions (FINRA vocabulary ↔ EU vocabulary, e.g. "designated supervisor" ↔ "management body responsibility"). This vocabulary bridge is itself a maintained mapping artifact — REQUIRES LEGAL / COMPLIANCE INTERPRETATION.
- **Negative-evidence retrieval:** absence of evidence is a finding. If top-k relevance scores fall below a floor, the control is a candidate FAIL ("no section addresses ICT incident classification"), routed with lower confidence (§19.3).

### 18.2 Structured output with enforced citations

Generation must emit **schema-constrained JSON** (grammar/JSON-schema enforced decoding, not "please output JSON"):

```json
{
  "control_id": "DORA-ART17-C03",
  "decision": "PARTIAL",
  "confidence": 0.72,
  "rationale": "…",
  "citations": [
    {"chunk_id": "…", "document": "WSP Sample.pdf", "page": 87,
     "section": "4.3.2", "quoted_span": "…verbatim excerpt…"}
  ],
  "gaps": ["No escalation timeline defined"],
  "model_version": "…", "prompt_version": "…", "control_version": "…"
}
```

Rules: every `decision` other than `NOT_APPLICABLE` MUST carry ≥1 citation (FAIL may cite the closest near-miss section or explicitly assert `"citations": []` with `absence_asserted: true`); `quoted_span` must be verbatim; page + section are mandatory fields, populated from chunk metadata (the model selects chunk_ids; the system fills page/section — never let the LLM invent page numbers).

## 19. Decision Contract, Confidence, Verification

### 19.1 Decision contract (per control × WSP)

| Decision | Meaning |
|---|---|
| `PASS` | Cited WSP evidence satisfies the control's expected evidence |
| `PARTIAL` | Evidence exists but is incomplete/outdated/contradicted elsewhere |
| `FAIL` | No adequate evidence (including verified absence) |
| `NOT_APPLICABLE` | Control out of scope for this firm's activity profile (must state why; firm-profile driven) |
| `NEEDS_HUMAN_REVIEW` | Model cannot decide within confidence policy; ambiguity, contradiction, or interpretive question |

`NEEDS_HUMAN_REVIEW` is a first-class terminal state for the AI stage, not an error. Contradiction findings (two WSP sections that conflict) always route here initially.

### 19.2 Confidence scoring

Composite, not a single logit: (a) retrieval strength (reranker scores of cited chunks), (b) groundedness score from the verification pass (§19.4), (c) self-consistency (k=3 sampled runs; disagreement lowers confidence), (d) calibration mapping learned from the golden dataset. Report 0–1 with the components stored in the eval record.

### 19.3 Human-review thresholds (initial policy — tune against golden set)

- confidence < 0.6 → `NEEDS_HUMAN_REVIEW` always.
- 0.6–0.8 → auto-decision allowed for PASS; FAIL/PARTIAL require human confirmation (asymmetric because false FAIL costs analyst trust, false PASS costs compliance risk — prioritize recall on FAIL: a missed gap is the worst error class).
- \> 0.8 → auto-decision, sampled human QA (e.g. 10%).
- All contradiction findings and all `NOT_APPLICABLE` on high-severity controls → human review during the first N validations per tenant ("trust ramp").

### 19.4 Evidence-verification step (anti-hallucination gate)

A deterministic, non-LLM post-processor runs on every finding **before** it is persisted or alerted:

1. **Span existence:** `quoted_span` must string-match (whitespace/hyphenation-normalized) the stored chunk text at the recorded offsets. No match → finding rejected → regenerate once → else `NEEDS_HUMAN_REVIEW`.
2. **Citation integrity:** cited `chunk_id` belongs to the right document version; page/section fields equal chunk metadata.
3. **Groundedness (LLM-as-judge, second model/prompt):** decompose rationale into atomic claims; each claim must be entailed by cited spans. Claim-level entailment is current best practice; judges reach ~80% agreement with humans (source: Openlayer RAG groundedness guides 2026, https://www.openlayer.com/blog/measuring-rag-groundedness-complete-evaluation-guide; Braintrust hallucination-detection roundup 2026, https://www.braintrust.dev/articles/ai-hallucination-evaluations-metrics-methods-2026, accessed 2026-08-17). Gate: groundedness < 0.8 → flag; < 0.7 → block/route to human (thresholds to be recalibrated on golden set).
4. **Table findings:** claims about table cells re-checked against the stored raw cell grid, not the serialized text.

### 19.5 Incremental re-validation

Regulation change → affected Requirements → Controls → only re-run those controls' retrieval+generation per WSP; document re-upload → diff chunks by hash, re-embed changed chunks, re-run only controls whose prior citations touched changed sections (plus a sampled full sweep). Eval records (security doc §32) make each run reproducible and comparable.

---

### Open questions
- OPEN QUESTION: OpenSearch vs Postgres-native BM25 — decide on ops budget; corpus size does not force OpenSearch.
- OPEN QUESTION: generation LLM hosting (EU-region API vs self-hosted open-weights) — interacts with confidentiality posture and DPA; REQUIRES LEGAL REVIEW.
- OPEN QUESTION: whether scanned/image-only WSP pages must be supported (OCR path); neither sample requires it.

### Sources (accessed 2026-08-17)
- Anthropic, *Contextual Retrieval*: https://www.anthropic.com/engineering/contextual-retrieval
- OWASP GenAI Security Project, LLM01:2025 Prompt Injection: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- Milvus, *Choosing an Embedding Model for RAG (2026)*: https://milvus.io/blog/choose-embedding-model-rag-2026.md
- BentoML, *Open-Source Embedding Models 2026*: https://www.bentoml.com/blog/a-guide-to-open-source-embedding-models
- Openlayer, *RAG Groundedness Evaluation Guide (2026)*: https://www.openlayer.com/blog/measuring-rag-groundedness-complete-evaluation-guide
- Braintrust, *AI hallucination evaluations 2026*: https://www.braintrust.dev/articles/ai-hallucination-evaluations-metrics-methods-2026
- EUR-Lex, MiCA (EU) 2023/1114: https://eur-lex.europa.eu/eli/reg/2023/1114/oj · DORA (EU) 2022/2554: https://eur-lex.europa.eu/eli/reg/2022/2554/oj

*Vendor blogs above are engineering references, not regulatory authority.*
