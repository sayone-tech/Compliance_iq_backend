# ComplianceIQ – Architecture Decision Records (ADR)

**Version:** 1.1
**Status:** Approved Baseline Decisions
**Supersedes:** ADR v1.0 (adds ADR-023 through ADR-027 in full, adds governance ownership/cadence)

> This document captures the major architectural decisions for ComplianceIQ Phase 1. Each ADR records the context, alternatives, decision, rationale, consequences, and future evolution. ADR-001 through ADR-022 are unchanged from v1.0. ADR-023 through ADR-027 — previously only summarized in Technical Architecture Baseline v2.0 §8 — are given full entries here for the first time, per the ADR Template below.

---

# ADR Template

## Status
Accepted

## Context
Why this decision is required.

## Options Considered

## Decision

## Rationale

## Consequences

## Future Review

---

# ADR-001 — Modular Monolith

## Context
Phase 1 targets approximately 100 firms and rapid delivery.

## Options
- Modular Monolith
- Microservices

## Decision
Use a Modular Monolith.

## Rationale
- Faster development
- Simpler deployment
- Lower operational cost
- Clear module boundaries
- Easy future extraction

## Future Review
Revisit if independent service scaling becomes necessary.

---

# ADR-002 — Backend Framework

## Decision
Use Django + Django REST Framework.

## Alternatives
- FastAPI only
- Flask

## Rationale
Enterprise workflows, mature ORM, authentication, migrations, admin, ecosystem.

AI workloads are isolated in a dedicated AI service.

---

# ADR-003 — Dedicated AI Service

## Decision
Implement a separate FastAPI AI Service.

## Responsibilities
- OCR orchestration
- RAG
- Prompt execution
- Embeddings
- AI evaluation
- Model routing

Business workflows remain in Django.

---

# ADR-004 — Architecture Style

## Decision
Hexagonal (Ports & Adapters).

## Benefits
- Testability
- Framework independence
- Easier refactoring
- Clear separation of concerns

---

# ADR-005 — Multi-Tenant Strategy

## Decision
Single PostgreSQL cluster.

Shared schema for global reference data.

Dedicated schema per tenant.

## Alternatives
- tenant_id
- Database per tenant

## Rationale
Strong logical isolation with manageable operational complexity.

---

# ADR-006 — Database

## Decision
PostgreSQL 16+

## Rationale
ACID transactions, JSONB, mature ecosystem, full text search, pgvector support.

---

# ADR-007 — Vector Storage

## Decision
pgvector

## Alternatives
- Pinecone
- Weaviate
- Qdrant
- Milvus

## Rationale
Expected scale (~100 firms) does not justify a dedicated vector database.

Business metadata and vectors remain together.

---

# ADR-008 — Search

## Decision
Phase 1 uses:

- PostgreSQL Full Text Search
- pgvector

Search implementation hidden behind a Search Service abstraction.

Future adapter:

OpenSearch.

---

# ADR-009 — AI Provider Strategy

## Decision
Provider abstraction.

Supported providers

- OpenAI
- AWS Bedrock
- Anthropic Claude
- Azure OpenAI
- Self-hosted

No module may directly call an LLM provider.

---

# ADR-010 — Embedding Strategy

## Decision
Embedding provider and model are configurable.

Store with every embedding

- Provider
- Model
- Dimensions
- Version

Initial model

text-embedding-3-small

Model migration occurs asynchronously.

---

# ADR-011 — Regulatory Knowledge

## Decision
Maintain a curated Regulatory Knowledge Base.

Automatic detection.

Human review.

Manual publication.

AI consumes only published knowledge.

---

# ADR-012 — Document Intelligence

## Decision

Pipeline

Upload

↓

Classification

↓

Docling

↓

Textract

↓

Chunking

↓

Embedding

↓

Indexing

↓

Human Review (where applicable)

---

# ADR-013 — Background Processing

## Decision

Celery + Redis.

Used for:

- OCR
- AI
- Notifications
- Reports
- Re-indexing
- Regulatory monitoring

---

# ADR-014 — Workflow Management

## Decision

Use explicit state machines.

Do not manage workflows with free-form status fields.

Applies to:

- Tests
- Findings
- Reports
- Regulatory updates

---

# ADR-015 — Audit

## Decision

Application-level immutable audit log.

Audit records are append-only.

No updates or deletes.

---

# ADR-016 — Reporting

## Decision

HTML templates rendered using WeasyPrint.

Reason

Consistent branding and easier maintenance.

---

# ADR-017 — Infrastructure

## Decision

Docker containers deployed to AWS ECS Fargate.

Reason

Managed orchestration with lower operational overhead than Kubernetes.

---

# ADR-018 — Deployment

## Decision

Rolling deployment.

Database migrations executed before application rollout.

Tenant migrations managed by a tenant migration runner.

---

# ADR-019 — Observability

## Decision

- CloudWatch
- Grafana Alloy
- New Relic

Structured JSON logging throughout the platform.

---

# ADR-020 — Internationalization

## Decision

Phase 1 languages

- English
- German
- French

Architecture supports all official EU languages.

Business logic references canonical Requirement IDs.

---

# ADR-021 — Security

## Decision

- JWT
- MFA
- RBAC
- TLS
- AES-256
- Immutable audit
- Schema isolation

---

# ADR-022 — AI Evaluation

## Decision

AI quality is a Phase 1 capability.

Metrics include

- Precision
- Recall
- Confidence
- Human override rate
- Latency
- Cost

---

# ADR-023 — Application Topology

## Status
Accepted

## Context
The PRD confirms two structurally separate applications (Firm Application, Platform Admin Portal) with a hard requirement that firm users have no visibility into the Portal's existence, and Portal staff never access individual firm data. The original TAB and ADR set predates this requirement and describes only a single modular monolith without addressing how two audiences with this confidentiality boundary are actually served.

## Options Considered
- Single Django backend, single frontend SPA with route-guarded sections
- Two fully separate backend services (one per application)
- Single Django backend with namespaced APIs, two separate frontend SPAs

## Decision
Single Django backend with two logically separate API namespaces (`firm_api`, `admin_portal_api`), each with its own permission-class base and database-access boundary. Two separate frontend SPAs (`firm-app`, `admin-portal`), each an independent build/deploy artifact. A separate, fully decoupled Next.js Marketing Site (three deployables total).

## Rationale
A single backend keeps operational overhead low at the ~100-firm Phase 1 scale (consistent with ADR-001's modular-monolith rationale), while the namespace/permission-class/database-router separation gives a hard, code-enforced boundary rather than a UI-only route guard, which is what the confidentiality requirement actually needs. Separate frontend SPAs prevent bundle/string leakage between the two audiences and let the two applications' independently different release cadences (Firm App: frequent; Portal: infrequent) evolve without coupling.

## Consequences
Two frontend codebases/pipelines to maintain instead of one; the Portal's `admin_portal_api` namespace is structured so it could be extracted into an independent service later without touching firm-facing code, if scale ever demands it.

## Future Review
Revisit if Portal usage or firm count grows meaningfully beyond Phase 1 assumptions.

---

# ADR-024 — Reporting Multi-Format Strategy

## Status
Accepted

## Context
ADR-016 fixed WeasyPrint for PDF generation. The PRD confirms PDF export and leaves Word export as likely and Excel export as undecided (RP-04). Building three independent report-generation code paths risks the three formats drifting out of structural sync as the report schema evolves.

## Options Considered
- Three independent renderers, each reading from live database queries directly
- A single structured Report Data Model feeding three independent renderers (WeasyPrint, docxtpl, openpyxl)

## Decision
A single structured Report Data Model (`report.report_data_snapshot`, frozen at generation time) feeds three format-specific renderers: WeasyPrint (PDF), docxtpl (Word), openpyxl (Excel).

## Rationale
A structural change to what a report contains is made once, in the shared data model, and propagates to every enabled export format automatically, rather than requiring three parallel updates that can silently diverge. Freezing the snapshot at generation time also means a later amendment to underlying source data (e.g., a finding edited after report generation) never silently changes an already-generated report's content.

## Consequences
Word/Excel rendering logic exists and is maintained regardless of whether RP-04 confirms them as contracted deliverables — enabling/disabling a format for a given client is a configuration flag, not a build decision.

## Future Review
Revisit if RP-04 resolves in a direction that changes which formats are actually needed.

---

# ADR-025 — AI Evaluation Harness

## Status
Accepted

## Context
The PRD commits to a minimum 85% verified accuracy rate for AI-assisted WSP-to-Requirement mapping, measured against pre-defined verification text vectors, with all tuning included in the fixed-fee scope. ADR-022 established that AI quality is a Phase 1 capability but didn't define a concrete mechanism to gate a prompt/model change before it reaches UAT.

## Options Considered
- Manual spot-check before each UAT promotion
- Automated golden-dataset evaluation as a CI-style release gate

## Decision
A golden dataset of human-expert-labeled WSP-section-to-Requirement-ID pairs, evaluated automatically whenever a prompt, model, or embedding configuration changes. A version must clear ≥85% accuracy on this dataset before promotion to UAT — a hard gate, not an advisory check.

## Rationale
A manual spot-check doesn't scale and is easy to skip under delivery pressure; an automated gate makes the 85% commitment structurally enforced rather than a promise that depends on someone remembering to verify it.

## Consequences
Every prompt/model change now has a mandatory evaluation step in the pipeline (Infrastructure & DevOps §10.1), adding latency to AI-related releases but removing the risk of an accuracy regression reaching production undetected.

## Future Review
Golden dataset composition/size should be periodically reviewed by Sosinna's team as real usage reveals edge cases the initial dataset didn't anticipate.

---

# ADR-026 — Regulatory Monitoring Source Constraint

## Status
Accepted

## Context
ADR-011 established automatic detection → human review → manual publication for regulatory updates, but didn't constrain *how* detection happens. An HTML-scraping approach is fragile — it breaks silently whenever a regulator redesigns a page, which is a worse failure mode here than most software (a missed regulatory update is a compliance risk, not just a bug).

## Options Considered
- HTML scraping of regulator websites
- RSS feeds and official public APIs only

## Decision
MVP regulatory monitoring is restricted to RSS feeds and official public APIs from EUR-Lex, EBA, ESMA, and key national regulators. No HTML scraping or layout-dependent parsing.

## Rationale
RSS/API sources are stable contracts; scraping depends on page structure remaining unchanged, which is outside ComplianceIQ's control and fails in a way that's easy to miss (a redesigned page returns different HTML, not an error).

## Consequences
Coverage is bounded by which regulators offer RSS/API access — a manual entry interface (Portal-side) exists as the fallback for regulatory changes identified outside these automated channels.

## Future Review
Revisit if a regulator relevant to client firms offers no RSS/API access and manual entry proves operationally insufficient.

---

# ADR-027 — IT Monitoring-System Ingestion

## Status
Accepted

## Context
The PRD envisions eventual integration with firms' AML/transaction-monitoring vendor systems (e.g., SumSub, Veritas). Building direct API connectors before knowing which vendors client firms actually use, and before a Data Processing Agreement framework exists for ingesting individual-level monitoring data, is premature.

## Options Considered
- Direct API integration to vendor systems now
- CSV upload against a fixed, SayOne-defined template, aggregated counts only

## Decision
No direct API integration to firm AML/transaction-monitoring systems for MVP. Firms upload a CSV extract against a fixed field template; only aggregated counts and period-over-period comparatives are accepted — explicitly no PII, no individual customer-level data.

## Rationale
Avoids building and maintaining bespoke connectors to vendor APIs (each with its own auth model and data contract) before validating actual client vendor usage, and sidesteps the PII/data-processing complexity of individual-level data ingestion before the DPA framework for that specific data flow is agreed.

## Consequences
Direct API integration remains a tracked future extension point (Technical Architecture Baseline §20), not built now. The Data Import/Export Framework's `ImportValidator` pattern (Data Import/Export Framework §2.2) enforces the aggregated-counts-only, no-PII constraint at validation time, not just as a documented expectation.

## Future Review
Revisit once specific client vendor usage patterns and a DPA framework for individual-level monitoring data are both confirmed.

---

# ADR Governance

## Lifecycle

Every future architectural change is recorded as a **new** ADR rather than by editing a historical one. Status values:

- **Proposed** — under discussion, not yet in effect.
- **Accepted** — the current, active decision.
- **Superseded** — replaced by a specific later ADR (the superseding ADR is cited by number in the superseded one's Future Review section, retroactively, at the time of supersession).
- **Deprecated** — no longer applicable (e.g., the technology itself is being phased out) without a direct replacement decision.

Each ADR must include implementation impact and migration considerations — a decision without a stated consequence isn't a complete ADR entry.

## Ownership (New in v1.1)

- **ADR authorship:** any engineer or architect proposing an architectural change drafts the ADR as part of the same change (Architecture Change Checklist, TAB v2.1 §21a — "which ADR changed, or does a new one need to be written?").
- **ADR acceptance:** requires sign-off from the Lead Architect (or, in a smaller-team phase, whoever holds that responsibility for the engagement) — the same elevated-review bar Engineering Standards §6 already applies to the highest-risk code modules extends here, since an ADR governs those modules' *design*, not just their implementation.
- **Supersession:** only the Lead Architect (or delegate) may mark an ADR Superseded — this prevents a well-intentioned but under-discussed change from quietly overriding a prior decision without the same scrutiny the original decision received.

## Review Cadence (New in v1.1)

- **Quarterly ADR review:** a standing review of the full ADR set, checking for decisions that have quietly become stale (referenced technology deprecated, an assumption invalidated by a product change) without a formal supersession — catching drift here is cheaper than discovering it mid-incident.
- **Ad hoc trigger:** any Cross-Document Traceability Matrix update (per that document's Section 9 maintenance rule) that touches an ADR-backed decision triggers a check of whether that ADR still accurately describes the current state, independent of the quarterly cadence.

---

# Version History

| Version | Date | Notes |
|---------|------|------|
| 1.0 | Draft | Initial ADR set, ADR-001 through ADR-022. |
| 1.1 | Jul 2026 | Added full ADR-023 through ADR-027 entries (previously only summarized in TAB v2.0 §8): Application Topology, Reporting Multi-Format Strategy, AI Evaluation Harness, Regulatory Monitoring Source Constraint, IT Monitoring-System Ingestion. Added ADR Governance ownership (authorship/acceptance/supersession responsibility) and review cadence (quarterly + traceability-matrix-triggered) — closing the governance gap identified in a structured architecture review. |
