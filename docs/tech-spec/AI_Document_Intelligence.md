# ComplianceIQ – AI & Document Intelligence

**Version:** 1.0
**Status:** Baseline
**Depends On:** Technical Architecture Baseline (TAB) v2.0, Database Architecture v1.2, Backend Architecture v1.1, Domain Model & Ubiquitous Language v1.0
**Audience:** AI Engineers, Backend Engineers, Architects, QA

> This document defines the FastAPI AI Service architecture: the document intelligence pipeline, the WSP-to-Requirement mapping algorithm, provider abstraction and EU-residency enforcement, prompt/model versioning, the AI evaluation harness (implementing TAB v2.0 §10.2), and the human-in-the-loop boundaries that keep AI advisory rather than decision-making, per Domain Model §9.

---

# 1. Purpose

This document translates the AI principles fixed in TAB v2.0 and the ADR set (ADR-002, ADR-007, ADR-009, ADR-025) into a concrete, buildable AI service design. It answers:

- How is the FastAPI AI Service internally structured, and how does it talk to Django (Backend Architecture §9 fixed the *pattern*; this document fixes the *content*)?
- How does WSP-to-Requirement mapping actually work — what's retrieved, how is it ranked, how is a suggestion produced?
- How is EU data residency enforced for third-party AI provider calls, given WSP content is firm-confidential?
- How are prompts and models versioned and gated before reaching UAT/production?
- What exactly gets logged, and what must never leave the tenant-scoped boundary?

---

# 2. AI Principles (Reaffirmed from TAB v2.0 §10.1)

AI responsibilities: OCR, document parsing, semantic search, WSP mapping, gap analysis, summaries, recommendations.

AI never: makes regulatory decisions, publishes regulations, approves compliance, closes findings, or auto-confirms a WSP mapping. Every AI output that affects compliance status is written as `pending_review` and requires human action (per the dual-control service, Backend Architecture §8, for FR-32's two-person sign-off specifically).

---

# 3. AI Service Structure

```
ai_service/                          # FastAPI, deployed independently of the Django backend
├── ingestion/                       # Upload handling, classification, Docling/Textract orchestration
├── chunking/                        # Section-aware chunking of parsed documents
├── embedding/                       # Embedding generation, provider-abstracted (Section 6)
├── retrieval/                       # Hybrid search: pgvector + full-text, reciprocal rank fusion
├── mapping/                         # WSP-to-Requirement mapping orchestration (LangGraph)
├── gap_analysis/                    # Coverage comparison: required Requirement IDs vs. confirmed mappings
├── evaluation/                      # Golden-dataset harness runner (Section 9)
├── providers/                       # Provider abstraction adapters (OpenAI, Bedrock, Anthropic, Azure OpenAI, self-hosted)
└── internal_api/                    # Contract consumed only by Django's ai_gateway app (Backend Architecture §9)
```

The AI Service has **no direct database access to any tenant schema**. It receives document content and context via the internal API contract from Django, processes it in memory / temporary storage, and returns results via callback or polling — it never queries PostgreSQL directly. This keeps tenant isolation (ADR-004) intact even though the AI Service is a separate deployable from the Django modular monolith.

---

# 4. Document Intelligence Pipeline (Expanded from TAB v2.0 §10.4)

| Stage | Detail |
|---|---|
| **1. Upload** | Django's evidence/WSP upload flow (Backend Architecture §12) lands the file in S3; a reference (not the file itself) is passed to the AI Service job. |
| **2. Classification** | Determines document type (WSP manual, evidence file, licence document) — routes to the correct downstream pipeline. A WSP upload always runs the full pipeline below; an evidence file (e.g., a screenshot) typically skips mapping/gap-analysis stages. |
| **3. Parsing (Docling)** | Extracts structured text, preserving page/section boundaries — required so `wsp_section.page_range` (Database Architecture §5.3) can be populated accurately. |
| **4. OCR (AWS Textract)** | Applied when Docling detects a scanned/image-based PDF (FR-30's OCR requirement). Output is merged back into the same structured text stream as native-text pages. |
| **5. Chunking** | Section-aware, not fixed-token-window: chunk boundaries align to `wsp_section` boundaries wherever Docling's structure detection is confident, falling back to a token-window with overlap where it isn't (e.g., unstructured legacy manuals). |
| **6. Metadata extraction** | Page range, section heading (if detected), document version, upload timestamp — attached to each chunk. |
| **7. Embedding generation** | Per Section 6 below; writes to the tenant's `wsp_content_embedding_genN` table (Database Architecture §10.3) via Django, not directly. |
| **8. Indexing** | HNSW index (pgvector) and full-text `tsvector` index, both already defined in Database Architecture §11 — the AI Service doesn't manage indexes itself, it writes rows and Postgres/Django handle indexing. |
| **9. Human review** | Mapping suggestions land as `pending_review`; gap analysis results are advisory dashboard flags, never auto-applied. |

---

# 5. WSP-to-Requirement Mapping — Retrieval & Ranking

## 5.1 Hybrid Retrieval

For each WSP section (or each Requirement, run in the reverse direction for gap analysis — Section 8), candidates are retrieved via:

1. **Semantic search:** pgvector cosine similarity against `regulatory_embedding_current` (Database Architecture §10.3), top-N candidates.
2. **Keyword search (BM25, not Postgres's default `ts_rank`):** Postgres's built-in `ts_rank`/`ts_rank_cd` is a simple term-frequency score — it doesn't apply BM25's saturation (diminishing returns on repeated terms) or proper document-length normalization, both of which matter here since WSP sections and Article texts vary widely in length. The GIN `tsvector` index (Database Architecture §11) is still used for fast initial candidate narrowing, but the final keyword ranking is computed with **actual BM25 scoring** as a re-ranking step over that narrowed set (e.g., via a lightweight library such as `rank_bm25` inside the AI Service's retrieval module) — this catches exact-term matches (e.g., "Art. 92", "transaction monitoring") that pure semantic similarity can under-rank, with a ranking formula actually suited to variable-length passage retrieval. This adds no new infrastructure — indexing and storage stay exactly as committed in ADR-005; only the scoring formula applied on top of the FTS-narrowed candidates differs from Postgres's default.
3. **Fusion:** Reciprocal Rank Fusion (RRF) combines the vector-ranked list and the BM25-ranked list into a single candidate set, avoiding the failure mode of either method alone.

## 5.2 LLM Re-Ranking & Suggestion Generation

The fused candidate set (typically top 10–15) is passed to the LLM (via the provider abstraction, Section 6) with the WSP section text, asking it to:

- Select the best-matching Requirement ID(s) from the candidate set (not free-generate an ID — this prevents hallucinated Requirement IDs that don't exist in the shared schema).
- Produce a short rationale (stored alongside the suggestion for the human reviewer).
- Return a confidence score (0–1).

## 5.3 Confidence Threshold Policy

- **Below a configurable floor (default 0.4):** no suggestion is surfaced for that section at all — an unmapped section shows as "no AI suggestion" rather than a low-quality guess that erodes reviewer trust.
- **At or above the floor:** always written as `ai_mapping.status = 'pending_review'`, regardless of score. Score is stored and used to sort the CCO's/compliance officer's review queue (highest-confidence-first, or lowest-confidence-first — a UI preference, not a workflow gate) but never triggers auto-confirmation. This keeps FR-31's "AI suggestions are a starting point only" absolute, independent of how confident the model claims to be.

---

# 6. Provider Abstraction & EU Data Residency

## 6.1 Provider Interface

A single internal interface (`EmbeddingProvider`, `CompletionProvider`) is implemented per backend (OpenAI, AWS Bedrock, Anthropic Claude, Azure OpenAI, self-hosted). No code outside `ai_service/providers/` constructs a provider-specific request — this is the concrete implementation of ADR-007/ADR-009's "no module may directly call an LLM provider."

## 6.2 EU-Region Enforcement

A `model_config` record (extends the `embedding_model_registry` concept from Database Architecture §10.2 to completion models as well) carries a `region` field. The provider abstraction layer **refuses to route a request** to any `model_config` whose `region` isn't in an EU allowlist for any call that touches firm-confidential content (WSP text, evidence-adjacent summarization). This is enforced in code, not left as an operational assumption:

```python
if model_config.region not in EU_ALLOWED_REGIONS and request.contains_tenant_content:
    raise ProviderRegionViolation(model_config.id)
```

**Rationale:** NFR-03 requires EU-resident data for everything ComplianceIQ stores; since WSP content necessarily leaves PostgreSQL to reach an inference endpoint, the endpoint itself must be EU-resident (e.g., Azure OpenAI EU region, AWS Bedrock EU region) or this guarantee is silently broken the moment AI mapping is used. This check exists so that adding a new provider/model in the future can't accidentally violate data residency by omission.

## 6.3 No Training on Client Data

All provider integrations are configured with data-use opt-outs / zero-retention API tiers where the provider offers them (e.g., enterprise API terms rather than consumer terms), consistent with the Data Processing Agreement obligations under NFR-06. This is a contractual/configuration matter tracked per-provider, not a code-level control, but is recorded here so it isn't assumed away.

---

# 7. Prompt & Model Versioning

## 7.1 `prompt_template` Registry (shared schema)

Mirrors the `embedding_model_registry` pattern (Database Architecture §10.2):

| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| template_name | text | e.g. `wsp_mapping_suggestion` |
| version | integer | |
| prompt_text | text | Jinja2-style template with variable slots |
| model_config_id | uuid, FK | which completion model this version targets |
| status | enum | `draft`, `evaluating`, `active`, `deprecated` |
| activated_at | timestamptz, nullable | |

Only one `template_name` may have `status = 'active'` at a time — enforced by a partial unique index, same convention as the embedding registry.

## 7.2 Release Gate

A new `prompt_template` version (or a `model_config` change for an existing active template) cannot move from `evaluating` to `active` until the golden-dataset evaluation job (Section 9) passes the ≥85% accuracy gate defined in ADR-025 / TAB v2.0 §10.2. This is the same CI-style gate philosophy applied consistently across embeddings, prompts, and models — one governance pattern, not three.

---

# 8. Gap Analysis Engine (FR-34)

Runs the mapping relationship in reverse: for each Requirement ID applicable to the firm (per its confirmed service lines), check whether any `ai_mapping` row with `status = 'confirmed'` references it. Unmapped-but-applicable Requirement IDs are flagged as compliance gaps on the firm's dashboard.

This is a **read-only aggregation query**, not an AI call — no LLM involvement is needed once mappings exist, since it's a set-difference between "applicable Requirements" and "Requirements with a confirmed mapping." Recomputed on-demand (dashboard load) and on every `ai_mapping` status change (via the outbox event `FindingCreated`-style pattern — specifically a `WSPMappingConfirmed`/`WSPMappingReversed` event triggers a gap-analysis cache refresh, Backend Architecture §6).

---

# 9. AI Evaluation Harness (Implements TAB v2.0 §10.2, ADR-025)

## 9.1 Golden Dataset

Uses `ai_eval_golden_case` (Database Architecture §4.4) — human-expert-labeled WSP-section-to-Requirement-ID pairs, the "verification text vectors" the PRD's 85% commitment refers to. Dataset is versioned; additions are reviewed with the same rigor as regulatory content changes (governance requirement from TAB v2.0 §10.2.5).

## 9.2 Evaluation Job

An `ai_eval` queue Celery task (Backend Architecture §11) runs the full mapping pipeline (Sections 5–6 of this document) against every golden case, then computes:

- **Precision:** of suggested mappings, what fraction match the expert label.
- **Recall:** of expert-labeled mappings, what fraction the pipeline surfaced as a suggestion (at any confidence above the floor).
- **Accuracy:** overall correct-mapping rate — the headline number gated at 85%.

Results are written to `ai_eval_run` (Database Architecture §4.4), tied to the specific `dataset_version` and `model_config_ref`/`prompt_template` version under test.

## 9.3 Trigger Conditions

The evaluation job runs automatically whenever:
- A `prompt_template` moves to `evaluating` status.
- A `model_config` (provider/model/region) changes for any template currently `active`.
- The golden dataset itself is updated to a new `dataset_version` (re-validates the *existing* active configuration against the new bar, catching silent regressions from dataset improvements).

## 9.4 Production Feedback Loop

The human override rate (how often a compliance officer rejects or edits an AI suggestion vs. confirms it as-is) is tracked per `ai_mapping` row and aggregated into the same metrics store as the golden-dataset runs. This doesn't replace the UAT gate but gives Sosinna's team an ongoing accuracy signal from real usage, surfaced on a Portal-side quality dashboard.

---

# 10. AI Job Data Model

Referenced informally in Backend Architecture §9; formally defined here since it's AI-Service-specific.

**`ai_job`** (tenant schema — job metadata belongs to the firm whose document is being processed)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| job_type | enum | `ocr_parse`, `wsp_mapping`, `gap_analysis_refresh`, `embedding_backfill` |
| source_document_ref | text | S3 pointer or `wsp_version_id` |
| status | enum | `queued`, `processing`, `completed`, `failed` |
| requested_by | uuid, FK | |
| requested_at | timestamptz | |
| completed_at | timestamptz, nullable | |
| model_config_id | uuid, FK, nullable | which model/provider handled it |
| prompt_template_id | uuid, FK, nullable | |
| result_payload | jsonb, nullable | structured result (mapping suggestions, gap list); **full content stays here, not mirrored to observability tooling (Section 11)** |
| error_detail | text, nullable | |
| retry_count | integer, default 0 | |

No delete grant — consistent with the platform-wide non-deletion posture (Database Architecture §7), since `ai_job.result_payload` is part of the evidentiary trail for how an AI-suggested mapping was produced.

---

# 11. Observability & Logging Boundaries

- **What ships to CloudWatch/New Relic/Grafana Alloy (TAB v2.0 monitoring stack):** job id, job type, model/provider identifier, latency, token counts, confidence score, pass/fail status. This is sufficient for performance and cost monitoring.
- **What never ships there:** raw WSP text, raw prompt content, raw LLM completion text. This stays exclusively in `ai_job.result_payload` (tenant schema, same access controls and retention as any other tenant data) and is never mirrored verbatim into third-party-facing observability tooling.
- **Rationale:** WSP content is firm-confidential; observability platforms are operated for engineering diagnostics, not compliance-data custody, and may not carry the same EU-residency or access-control guarantees as the primary database. Keeping content out of logs entirely avoids relitigating that question per-tool.

---

# 12. Cost & Latency Considerations

- Mapping suggestion generation (Section 5) is the most expensive/slowest operation (LLM re-ranking over ~10–15 candidates per section, for a potentially dozens-of-sections WSP). It runs fully asynchronously (Backend Architecture §9) — no user-facing request waits on it.
- Embedding generation (Section 4, stage 7) is comparatively cheap and fast; still queued via Celery to avoid competing with mapping jobs for AI Service capacity (separate internal queue inside the AI Service, mirroring the Django-side `ai` queue isolation from Backend Architecture §11).
- Golden-dataset evaluation runs (Section 9.2) are the least time-sensitive — triggered on config change, not on a tight user-facing SLA — and can run against a lower-priority internal queue.

---

# 13. Open Items Carried Forward

| Item | Status |
|---|---|
| Final choice of EU-region provider/model per completion vs. embedding use case | Architecture supports any EU-region-compliant provider (Section 6.2); specific vendor selection is an implementation-phase decision |
| Golden dataset initial size/composition | Content/governance decision for Sosinna's team, not an architectural blocker |
| Whether gap-analysis dashboard needs real-time push (websocket) vs. on-load recompute | Currently on-load + event-triggered cache refresh (Section 8); revisit if UX testing shows staleness is an issue |
| GAP-09 (who may initiate a WSP mapping override) | Still open at product level (Backend Architecture §14); AI Service behavior is unaffected either way — this only changes who can *submit* a manual override, not how AI suggestions are generated |

---

# 14. Version History

| Version | Date | Notes |
|---------|------|------|
| 1.0 | Jul 2026 | Initial AI & Document Intelligence specification: AI Service structure, expanded document intelligence pipeline, hybrid retrieval + LLM re-ranking for WSP mapping, confidence threshold policy, EU-region provider enforcement, prompt/model versioning registry with release gate, gap analysis engine, AI evaluation harness implementation, formal `ai_job` data model, and observability content boundaries. |
| 1.1 | Jul 2026 | Corrected keyword-retrieval scoring from Postgres's default `ts_rank`/`ts_rank_cd` to true BM25 (computed as a re-ranking step over GIN-narrowed candidates), since `ts_rank` lacks BM25's term-frequency saturation and document-length normalization — both material for variable-length WSP section and Article text matching. No new infrastructure required. |
