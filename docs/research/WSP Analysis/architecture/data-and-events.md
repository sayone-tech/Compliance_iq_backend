# Data & Events Architecture — Continuous Regulatory Compliance Validation Platform

**Scope:** Database strategy (PostgreSQL schema, hybrid search, graph question, versioning, tenant isolation with EU residency) and event/workflow infrastructure (broker selection, MVP vs enterprise, durable workflows for revalidation fan-out).
**Context:** Firms upload Written Supervisory Procedures (WSPs — internal compliance manuals, FINRA-origin term; test corpus: `Sample WSP.pdf` 154pp, `WSP Sample.pdf` 199pp). Platform validates them against MiCA (EU 2023/1114) and DORA (EU 2022/2554) and incrementally re-validates on regulatory change.
**Date:** 2026-08-17. Labels: VERIFIED FACT / ARCHITECTURAL RECOMMENDATION / ASSUMPTION / OPEN QUESTION.

---

## 1. PostgreSQL as the system of record

**ARCHITECTURAL RECOMMENDATION:** A single PostgreSQL (≥16) cluster is the system of record for *all* structured entities. The workload is relational to its core: a regulatory hierarchy (Regulation → Article → Paragraph → Requirement → Control → Expected Evidence), a document hierarchy (Firm → WSP version → Section → Claim/Evidence), and a many-to-many mapping layer between them, plus append-only evaluation history. Nothing in this shape requires a document store, and the audit/versioning requirements strongly favor ACID transactions and foreign keys.

### 1.1 Entity/table sketch

```
-- Tenancy
firms(id PK, name, lei, jurisdiction, tier, created_at, ...)          -- tenant root; every tenant-scoped table carries firm_id

-- Document side (per tenant)
wsp_documents(id PK, firm_id FK, title, doc_type, created_at)
wsp_versions(id PK, wsp_document_id FK, version_no, file_uri,         -- file_uri -> object storage (EU region)
             sha256, page_count, status, ingested_at, supersedes_id FK NULL)
wsp_sections(id PK, wsp_version_id FK, parent_section_id FK NULL,     -- tree via adjacency + materialized path
             section_number text, heading, path ltree,                -- '2.4.7'-style numbering seen in Triad sample
             page_start, page_end, char_start, char_end, text_sha256)
wsp_claims(id PK, wsp_section_id FK, claim_type, text_span, extracted_by, confidence)
wsp_evidence(id PK, wsp_section_id FK, claim_id FK NULL,
             evidence_kind, quote, page, char_start, char_end)        -- exact provenance for evidence-backed findings

-- Regulatory side (global, shared across tenants — NOT tenant-scoped)
regulations(id PK, celex_id, short_name, source_url, in_force_from)   -- e.g. 32023R1114 (MiCA), 32022R2554 (DORA)
regulation_versions(id PK, regulation_id FK, version_label, published_at, consolidated_text_uri)
articles(id PK, regulation_version_id FK, article_no, title)
paragraphs(id PK, article_id FK, para_no, point_no NULL, text, text_sha256)
requirements(id PK, paragraph_id FK, summary, obligation_type,
             applicability_expr jsonb)                                -- who it applies to (CASP class, size thresholds...)
controls(id PK, code UNIQUE, name, kind ENUM('deterministic','semantic','hybrid'))
control_versions(id PK, control_id FK, version_no, logic jsonb,       -- prompt / rule / expected-evidence spec
                 model_id text NULL, prompt_sha256, effective_from, created_by)
control_requirement_map(control_version_id FK, requirement_id FK,     -- N:M mapping layer
                        weight, rationale, PK(control_version_id, requirement_id))
expected_evidence(id PK, control_version_id FK, description, evidence_kind, min_specificity)

-- Evaluation side (append-only)
evaluation_runs(id PK, firm_id FK, wsp_version_id FK, trigger ENUM('upload','reg_change','control_change','manual','schedule'),
                change_event_id FK NULL, started_at, finished_at, engine_version, status)
evaluations(id PK, evaluation_run_id FK, control_version_id FK, wsp_version_id FK,
            wsp_section_ids uuid[] ,                                   -- sections consulted
            verdict ENUM('pass','gap','contradiction','partial','not_applicable','needs_review'),
            severity ENUM('critical','high','medium','low','info'),
            score numeric NULL, model_id, prompt_sha256, input_sha256, -- reproducibility & cache key
            raw_output jsonb, cost_usd numeric, created_at)            -- APPEND-ONLY: no UPDATE/DELETE
findings(id PK, evaluation_id FK, firm_id FK, kind, severity, title, description,
         evidence_refs jsonb,                                          -- [{wsp_evidence_id, page, quote}, {paragraph_id,...}]
         status ENUM('open','acknowledged','in_remediation','resolved','waived'),
         first_seen_run_id FK, last_seen_run_id FK, resolved_at NULL)
remediation_items(id PK, finding_id FK, firm_id FK, assignee, due_date, plan, status, updated_at)
remediation_events(id PK, remediation_item_id FK, actor, event_type, note, created_at)   -- append-only trail

-- Change & notification side
regulatory_changes(id PK, regulation_id FK, source ENUM('eur_lex','esma','eba','nca','manual'),
                   change_kind ENUM('amendment','rts_its','guideline','qa','interpretation'),
                   affected_paragraph_ids uuid[], summary, source_url, detected_at, effective_at)
change_impacts(id PK, regulatory_change_id FK, control_version_id FK, impact ENUM('invalidates','review','none'))
notifications(id PK, firm_id FK, channel, template, payload jsonb, dedupe_key UNIQUE NULL,
              status, created_at, sent_at)
audit_log(id PK bigserial, firm_id FK NULL, actor, action, entity_type, entity_id, before jsonb NULL,
          after jsonb NULL, request_id, created_at)                    -- append-only, partitioned by month
```

Notes:
- **VERIFIED FACT (sample-driven):** the Triad Securities sample WSP has a deep numbered TOC (1.0 / 2.4.7-style); `wsp_sections.path` as Postgres `ltree` (or a materialized-path text column) supports subtree queries (`path <@ '2.4'`) cheaply.
- `text_sha256` on sections and paragraphs is load-bearing: it is the reuse key for incremental revalidation (see `incremental-revalidation.md`) — unchanged section text ⇒ prior deterministic results and embeddings are reusable.
- `evaluations` carries `model_id + prompt_sha256 + input_sha256`: an evaluation is reproducible and cacheable by construction, and severity/verdict changes over time are queryable without ever mutating rows.
- Regulatory content is **global** (one copy, all tenants); tenant data references it read-only. This matters for both cost and isolation design (§1.5).

### 1.2 Versioning: append-only evaluations

**ARCHITECTURAL RECOMMENDATION:**
- `evaluations`, `remediation_events`, `audit_log`, `regulatory_changes` are strictly append-only (enforce with `REVOKE UPDATE, DELETE` + a trigger raising an exception; optionally a `pg_partman` monthly partitioning scheme on `evaluations(created_at)` for retention and index size).
- Mutable "current state" lives in *projection* tables (`findings.status`, `remediation_items.status`) whose transitions are themselves journaled (`remediation_events`). Current compliance posture = latest `evaluation_run` per (firm, wsp_version) — resolvable with `DISTINCT ON` or a `latest_evaluation` materialized view.
- WSP versions and control versions are immutable once ingested/published; corrections create a new version with `supersedes_id`. This gives an audit story regulators/auditors accept: you can reconstruct "what did the platform believe on date X, evaluated with which control logic, against which regulation text."

### 1.3 Hybrid search: pgvector vs OpenSearch

Search needs: (a) semantic retrieval of WSP sections relevant to a control's expected evidence; (b) keyword/BM25-ish search for defined terms ("designated principal", "ICT third-party service provider"); (c) filtered by tenant + wsp_version.

**ARCHITECTURAL RECOMMENDATION — start with pgvector + Postgres FTS, in the same database:**
- `wsp_chunks(id, wsp_version_id, wsp_section_id, firm_id, chunk_no, text, tsv tsvector, embedding vector(1536), text_sha256)`, with an HNSW index on `embedding` and a GIN index on `tsv`. Hybrid ranking = Reciprocal Rank Fusion of the two result lists in SQL — a well-trodden pattern.
- Scale check: a 200-page WSP yields ~300–500 chunks. 10,000 firms × ~10 stored versions ≈ 30–50M vectors *total*, but **queries are always filtered to one `wsp_version_id`** (a few hundred vectors). Even a partial or filtered HNSW scan is trivial; per-version retrieval could honestly be brute-force `ORDER BY embedding <=> q` over ~400 rows with no ANN index at all. pgvector (and pgvectorscale) benchmarks show strong performance to tens of millions of vectors (pgvectorscale reports 471 QPS @ 99% recall on 50M vectors — Timescale benchmark cited via [Firecrawl vector DB comparison](https://www.firecrawl.dev/blog/best-vector-databases), accessed 2026-08-17; see also [Instaclustr pgvector vs OpenSearch](https://www.instaclustr.com/education/vector-database/pgvector-vs-opensearch-for-vector-databases-5-differences-and-how-to-choose/), accessed 2026-08-17). VERIFIED FACT (vendor-published benchmarks; not independently reproduced here).
- **When OpenSearch earns its place:** cross-tenant analytics search, regulator-corpus search UX with heavy faceting, or if vector count grows into the hundreds of millions with high-QPS *unfiltered* queries ([Zilliz comparison](https://zilliz.com/comparison/pgvector-vs-opensearch), accessed 2026-08-17). None of these exist at MVP. Adding OpenSearch early costs a second cluster, a second consistency domain (index lag vs Postgres truth), and a second EU-residency surface. Defer it; keep an `search_index_outbox` pattern ready if it becomes needed.
- ASSUMPTION: embedding dim 1536 (e.g. OpenAI `text-embedding-3-small`) or 1024 (Voyage/Cohere); pgvector supports both, plus `halfvec` to halve storage.

### 1.4 Honest Neo4j assessment — not needed at this shape

The "dependency graph" is: paragraph → requirement → control(version) → wsp_section → evaluation, plus change → impacted controls. Assessed honestly:

- **Depth is fixed and shallow (≤5 hops), edges are typed and known at design time.** Graph databases pay off for variable-depth traversals, unknown-schema exploration, or pathfinding (fraud rings, knowledge graphs). Here every traversal is a static join path: "which evaluations are stale given change to paragraph P" is three joins (`paragraphs → control_requirement_map → control_versions → evaluations`), each on indexed FKs. Postgres executes this in milliseconds at 100k-firm scale.
- **The one recursive structure — the section tree — is bounded** (~4 levels in the samples) and handled by `ltree`/materialized path or a `WITH RECURSIVE` CTE. Recursive CTEs in Postgres are fully adequate for trees of hundreds of nodes per document.
- **What Neo4j would cost:** a second stateful system to operate, replicate to, keep transactionally consistent with the system of record (dual-write problem), secure per-tenant, and host in-EU. Cypher's expressiveness buys nothing when the queries are enumerable and fixed.
- **The genuine future trigger** would be: cross-regulation semantic dependency inference (e.g. "DORA Art. 5 interpretations transitively affect controls derived from MiCA Art. 68 via shared ICT definitions") explored ad hoc by analysts at large scale. Even then, a read-only graph *projection* (or Apache AGE inside Postgres) beats a primary Neo4j.

**ARCHITECTURAL RECOMMENDATION: no Neo4j. Join tables + recursive CTEs/ltree suffice; the dependency "graph" is a materialized index table (`control_section_dependency`, see revalidation doc), not a graph database workload.**

### 1.5 Tenant isolation with EU residency

Options compared:

| Option | Isolation | Ops cost | Fit |
|---|---|---|---|
| **Row-level security (RLS)**, `firm_id` on every tenant table, `SET app.current_firm` per request/connection | Logical; strong if RLS is forced (`FORCE ROW LEVEL SECURITY`) and app role is non-superuser | One schema, one migration path, works with PgBouncer (tx pooling + `SET LOCAL`) | **Default for MVP → mid-scale.** Scales to 100k firms; noisy-neighbor managed via partitioning on `firm_id` hash for the big tables (`wsp_chunks`, `evaluations`) |
| Schema-per-tenant | Moderate | Migration fan-out (10k+ schemas → catalog bloat, tooling pain) | Not recommended beyond ~100s of tenants |
| DB-per-tenant | Strongest | Fleet management, per-DB cost | Reserve for **enterprise/regulated top tier** — banks/CASPs who contractually demand dedicated instances; run as an exception path, same schema, same code (connection routing by tenant tier) |

**EU residency (relevant because customers are MiCA/DORA-regulated EU entities):**
- Primary Postgres, object storage (WSP PDFs), search indexes, queues, and **LLM/embedding inference endpoints** all pinned to EU regions (e.g. AWS eu-central-1/eu-west-1 or an EU sovereign offering). Backups and replicas EU-only.
- Note DORA itself pushes firms to scrutinize ICT third-party providers (the platform is one!) — expect vendor due-diligence questionnaires, sub-processor lists, and exit-plan clauses. ARCHITECTURAL RECOMMENDATION: keep the sub-processor list short (this argues again for Postgres-only over Postgres+OpenSearch+Neo4j).
- OPEN QUESTION / REQUIRES LEGAL REVIEW: whether customers will accept US-headquartered model providers with EU endpoints (Schrems-II style transfer analysis), or require EU-hosted/EU-owned models. Design the model-gateway so the model vendor is a per-tenant configuration.

---

## 2. Events & workflow

### 2.1 Event inventory (from the platform's behavior)

`wsp.uploaded`, `wsp.extracted`, `wsp.sectioned`, `wsp.embedded`, `evaluation.run.requested`, `evaluation.control.completed`, `evaluation.run.completed`, `finding.created|changed|worsened`, `remediation.updated`, `regulation.change.detected`, `control.version.published`, `revalidation.fanout.requested`, `notification.requested`, `audit.recorded`.

Two distinct shapes hide in this list:
1. **Pipelines/workflows** — multi-step, stateful, retryable, minutes-long, human-visible (ingest → extract → chunk → embed → evaluate → report; regulatory-change fan-out). These want *orchestration with durable state*.
2. **Notifications/integration events** — fire-and-forget fan-out to consumers (alerting, audit, webhooks, analytics). These want a *broker*.

### 2.2 Technology comparison

| Option | Strengths | Weaknesses here |
|---|---|---|
| **Kafka** | High-throughput streaming, replayable log, multi-consumer fan-out | Heavy ops; no workflow state; our volumes (thousands of events/day at MVP, millions/day at 100k firms — still small for Kafka) don't need it early. Right foundation only at large scale / when an event log for replay & analytics becomes a product feature ([Kai Waehner on durable execution vs Kafka](https://www.kai-waehner.de/blog/2025/06/05/the-rise-of-the-durable-execution-engine-temporal-restate-in-an-event-driven-architecture-apache-kafka/), accessed 2026-08-17) |
| **RabbitMQ** | Solid work-queue semantics, routing keys, mature | Another cluster to run; SQS/SNS covers the same need managed if on AWS |
| **SQS/SNS (or GCP Pub/Sub)** | Managed, EU-region, DLQs, cheap, near-zero ops | At-least-once only; no orchestration; AWS lock-in (acceptable) |
| **Celery (+ Redis/RabbitMQ)** | Trivial to adopt in a Python stack; fine for short background jobs | Weak durability/visibility for long multi-step workflows; crash recovery and fan-out/join logic is hand-rolled ([Celery vs Temporal](https://suhasbhairav.com/blog/celery-vs-temporal-for-ai-agent-tasks-background-jobs-vs-durable-execution), accessed 2026-08-17) |
| **Temporal (or equivalent durable execution: Restate, AWS Step Functions)** | Durable workflow state, automatic retries/backoff, heartbeats, signals, per-step idempotency, visibility UI, child workflows for fan-out/join | Extra infra (or Temporal Cloud — check EU residency); learning curve ([Temporal vs Kafka guide](https://www.xgrid.co/resources/temporal-vs-kafka-workflow-orchestration/); [HackerNoon practical guide](https://hackernoon.com/a-practical-guide-to-temporal-what-it-does-how-it-compares-and-when-to-use-it), accessed 2026-08-17) |

### 2.3 Recommendation

**MVP (≤1k firms):**
- **Postgres-backed job queue + transactional outbox** as the only "broker": an `outbox`/`jobs` table written in the same transaction as domain changes, drained by workers (`SELECT ... FOR UPDATE SKIP LOCKED`). Exactly-once effect via idempotency keys; zero extra infrastructure; events are already durable and auditable in the system of record. Celery is an acceptable substitute if the team already lives in it, but the outbox is still required for atomicity.
- Pipeline steps modeled as explicit job types with a `pipeline_runs` state row — a poor-man's workflow that is *deliberately shaped like Temporal workflows* so migration is mechanical.

**Enterprise (10k–100k firms):**
- **Temporal (self-hosted in EU, or Temporal Cloud EU region — verify residency contractually) for all pipelines**, especially regulatory-change revalidation fan-out; **SNS/SQS (EU region) for integration events and notifications**; introduce **Kafka only if/when** an immutable event log becomes a product requirement (compliance analytics, replay, external integrations at scale).

**Where Temporal-style durable workflows fit revalidation fan-out (the strongest single argument for it):**
A MiCA delegated-act change may invalidate 5 controls × 60k affected firms = 300k control evaluations, executed against rate-limited LLM APIs over hours/days, with partial failures, provider 429s, and cost caps. That is exactly the durable-execution sweet spot:

```
RegulatoryChangeWorkflow(change_id)
 ├─ activity: compute impacted control_versions (SQL, §1.4)
 ├─ activity: compute impacted (firm, wsp_version) set via dependency index
 ├─ continue-as-new over batches of N firms:
 │    └─ child workflow per batch: RevalidateBatch(firm_ids, control_ids)
 │         ├─ activity: reuse-check (hash lookups — no LLM)
 │         ├─ activity: submit LLM Batch-API job for the residue; poll to completion
 │         ├─ activity: persist evaluations (append-only), diff vs previous, emit finding events
 │         └─ retry policy: exponential backoff, budget/heartbeat guards
 └─ activity: aggregate + notify (alert-on-worsening only)
```

Durable state means a deploy, crash, or provider outage mid-fan-out resumes instead of restarts; signals allow pausing a fan-out (cost brake); the visibility UI answers "how far along is the DORA RTS revalidation" — a question compliance ops *will* ask.

**ASSUMPTION:** Python/TypeScript backend; all recommendations are language-agnostic among the mainstream options.

## Sources

- pgvector vs OpenSearch: [Instaclustr](https://www.instaclustr.com/education/vector-database/pgvector-vs-opensearch-for-vector-databases-5-differences-and-how-to-choose/), [Zilliz](https://zilliz.com/comparison/pgvector-vs-opensearch), [Firecrawl 2026 vector DB guide](https://www.firecrawl.dev/blog/best-vector-databases), [pgvector/OpenSearch benchmark repo](https://github.com/flavienbwk/pgvector-opensearch-benchmark) — all accessed 2026-08-17.
- Workflow/eventing: [Temporal vs Kafka (xgrid)](https://www.xgrid.co/resources/temporal-vs-kafka-workflow-orchestration/), [Kai Waehner — durable execution engines in EDA](https://www.kai-waehner.de/blog/2025/06/05/the-rise-of-the-durable-execution-engine-temporal-restate-in-an-event-driven-architecture-apache-kafka/), [Celery vs Temporal](https://suhasbhairav.com/blog/celery-vs-temporal-for-ai-agent-tasks-background-jobs-vs-durable-execution), [Practical guide to Temporal (HackerNoon)](https://hackernoon.com/a-practical-guide-to-temporal-what-it-does-how-it-compares-and-when-to-use-it) — accessed 2026-08-17.
- Regulations named for context: MiCA = Regulation (EU) 2023/1114 (EUR-Lex CELEX 32023R1114), DORA = Regulation (EU) 2022/2554 (CELEX 32022R2554). These are identifiers, not new claims; regulatory-content analysis lives in the sibling regulatory research docs.
