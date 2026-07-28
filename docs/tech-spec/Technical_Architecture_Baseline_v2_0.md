# ComplianceIQ – Technical Architecture Baseline (TAB)

**Version:** 2.2
**Status:** Baseline Architecture — Updated
**Supersedes:** TAB v1.0 (Draft), TAB v2.0, TAB v2.1
**Aligned With:** PRD v4.0 (SRS), ADR v1.0, Domain Model v1.0
**Audience:** Architects, Engineering, QA, DevOps, AI Engineers, Product Team

> This document establishes the technical baseline for ComplianceIQ Phase 1. Version 2.0 incorporates decisions made during the technical debt review session following PRD v4.0, resolving gaps between the original TAB/ADR set and the client-confirmed product requirements. Detailed implementation specifications (database, backend, AI, infrastructure, security, engineering standards) are covered in subsequent documents that inherit from this baseline.

---

# 1. Purpose

The Technical Architecture Baseline (TAB) defines the foundational engineering decisions for ComplianceIQ. Its objectives are to:

- Establish a single source of truth for technical decisions.
- Prevent architectural drift during implementation.
- Ensure consistency across development teams.
- Provide a reference for future architecture decision records (ADRs).
- Serve as the parent document for all technical specifications.
- Resolve identified gaps between PRD v4.0 (product/commercial decisions) and the original architecture baseline.

---

# 2. Scope

This document covers:

- High-level system architecture (including application topology)
- Technology stack
- AI architecture and evaluation strategy
- Multi-tenancy
- Security principles
- Search strategy
- Regulatory monitoring architecture
- Reporting architecture
- Marketing site architecture
- Deployment strategy
- Engineering principles
- Future extensibility
- Open items carried forward from PRD v4.0

It intentionally does **not** define detailed APIs, database schemas, or implementation logic. These are covered in later specifications (see Section 20).

---

# 3. Architectural Vision

ComplianceIQ is an AI-assisted enterprise SaaS platform for regulatory compliance management, purpose-built for Crypto Asset Service Providers (CASPs) under MiCA (EU 2023/1114) and DORA (EU 2022/2554).

The platform is designed around the following principles:

1. AI-assisted, not AI-driven.
2. Human approval for compliance decisions.
3. Modular architecture with clear domain boundaries.
4. Regulatory traceability and immutable audit history.
5. Tenant isolation.
6. Cloud-native deployment.
7. Future extensibility without major rewrites.
8. **Clear separation between the Firm Application and the Platform Admin Portal at every layer where a boundary violation would compromise confidentiality or trust** (new in v2.0 — see Section 5).

---

# 4. Guiding Engineering Principles

- Modular Monolith for Phase 1 (backend).
- Hexagonal (Ports & Adapters) Architecture.
- Domain-driven design concepts where appropriate.
- Event-driven internal communication.
- Asynchronous processing for long-running operations.
- Configuration over hardcoding.
- Version everything that impacts compliance.
- Every AI-assisted decision is reversible and human-reviewable before it affects compliance status.

---

# 4a. Cross-Cutting Architectural Conventions (New in v2.0)

These are decisions that affect more than one downstream specification document. They are pinned here, at the baseline level, so that Backend Architecture, AI & Document Intelligence, and Infrastructure & DevOps do not each make an independent (and potentially conflicting) choice.

## 4a.1 Domain Event Dispatch

The Domain Model (Section 6, Domain Model v1.0) defines the canonical domain events (`FirmCreated`, `WSPUploaded`, `RequirementPublished`, `TestAssigned`, `EvidenceUploaded`, `FindingCreated`, `FindingClosed`, `ReportGenerated`, `ReportPublished`, `RegulatoryUpdateDetected`, etc.) and ADR-013 mandates "event-driven internal communication," but neither specifies a dispatch mechanism.

**Decision:** Domain events are persisted via a **transactional outbox table**, written in the same database transaction as the state change that produced them, and relayed to Celery task consumers by a lightweight outbox-polling worker. Consumers (notifications, audit logging, re-indexing, AI evaluation triggers) subscribe by event type.

**Rationale:** A direct in-process signal (e.g., Django signals firing Celery tasks inline) risks losing an event if the transaction rolls back after the signal fires, or if Celery is briefly unavailable. Given several events here are compliance-critical (`FindingClosed`, `ReportPublished`), the outbox pattern guarantees at-least-once delivery tied to the actual committed state change — consistent with the append-only, tamper-proof audit log requirement (NFR-04).

Full table design and consumer registration is detailed in the forthcoming Backend Architecture document; this section only fixes the pattern so that document doesn't need to re-litigate it.

## 4a.2 State Machine Implementation

ADR-014 mandates explicit state machines (not free-form status fields) for Tests, Findings, Reports, and Regulatory Updates, but does not specify an implementation approach.

**Decision:** State transitions are implemented as an explicit, versioned **transition table per entity** (allowed from-state → to-state pairs, with the role permitted to trigger each transition), enforced in the Django service layer rather than via a third-party state-machine library. Every transition is written to the immutable audit log (ADR-015) as part of the same transaction.

**Rationale:** A hand-rolled transition table keeps the compliance-critical transition rules (e.g., who may close a Finding, who may reopen a Test) visible and reviewable as data/config rather than buried in a library's decorator syntax — this matters for a domain where the transition rules themselves are subject to audit.

## 4a.3 Environment & Release Strategy

Not previously stated in v1.0, but required by the AI Evaluation Harness (Section 10.2), which explicitly depends on a UAT environment and a defined promotion gate.

**Decision:** Four environments — **Development → Staging → UAT → Production**.

- **Development:** per-developer or shared dev environment, synthetic data only.
- **Staging:** integration testing, mirrors production configuration, synthetic/anonymized data only.
- **UAT:** client-facing acceptance environment. This is where the AI accuracy gate (Section 10.2) is formally evaluated and where Sosinna's team validates Portal-authored content against real workflows before sign-off.
- **Production:** live client data, EU-resident (per TI-01), rolling deployment (ADR-018).

Promotion from Staging to UAT for any change touching AI mapping requires the golden-dataset evaluation job (Section 10.2) to pass at ≥85% before promotion is permitted. This is a hard gate, not a manual checklist item.

## 4a.4 API Conventions

Versioning, pagination, and error-response format are **not** decided at the baseline level — they are owned by the forthcoming Backend Architecture document, since they don't cross-cut in the way the three items above do. Noted here only so the omission is deliberate, not accidental.

---

# 5. Application Topology (New in v2.0)

## 5.1 Decision

ComplianceIQ Phase 1 consists of **three deployable applications**, sharing one backend:

| Application | Frontend | Backend | Users |
|---|---|---|---|
| **Firm Application** | React + TypeScript SPA (`firm-app`) | Django backend, `firm_api` namespace | Firm users (CCO, Compliance Officer, Senior Management, Remediation Owner, IT Admin, Firm Super Admin) |
| **Platform Admin Portal** | React + TypeScript SPA (`admin-portal`) | Django backend, `admin_portal_api` namespace | Sosinna's team (Platform Super Admin) only |
| **Marketing Site** | Next.js (SSG/ISR) — fully decoupled | Independent — lead-capture endpoint only | Public / prospects |

## 5.2 Backend: Single Django Project, Namespaced APIs

- One Django project, one modular monolith, one deployment pipeline (per ADR-001/ADR-003).
- Two logically separate API namespaces:
  - `firm_api/` — serves the Firm Application. All queries scoped to the authenticated firm's tenant schema. Can never read Portal-only tables (prompt templates, cross-firm content authoring tables).
  - `admin_portal_api/` — serves the Platform Admin Portal. Can read cross-firm metadata explicitly permitted by CC-08/SA-06 (firm name, jurisdiction, service lines, last-active date) but is **architecturally prevented** from querying any individual firm's tenant schema (test results, findings, evidence, WSP content). This is enforced at the permission-class level, not just the UI level.
- Shared domain core: Requirement Library, Test Library, Sampling Methodology Library, Regulation/Article/Requirement models — authored in the Portal, consumed read-only by the Firm Application.

**Rationale:** A single backend keeps operational overhead low (matches ADR-001's ~100-firm scale target) while the namespace + permission-class separation gives a hard boundary that satisfies the PRD's requirement that Portal staff never access firm compliance data. Two backend services were considered and rejected for Phase 1 — the operational and deployment overhead isn't justified until scale demands it (see Section 5.4).

## 5.3 Frontend: Two Separate SPAs

- `firm-app` and `admin-portal` are **separate build artifacts**, separate repositories or separate packages in a monorepo, separate deploy pipelines.
- **Rationale:** The PRD is explicit that firm users must have no visibility into the Portal's existence (PRD Section 4). Bundling both into a single SPA — even behind route guards — risks bundle/string leakage and couples two unrelated release cadences. Separate SPAs also let the Portal (lower release frequency, used only by Sosinna's team) and the Firm App (higher release frequency, used daily by all client firms) evolve independently.

## 5.4 Future Evolution Path

If Portal usage or firm count grows beyond Phase 1 assumptions, the `admin_portal_api` namespace is structured so it can be extracted into an independent service without touching firm-facing code — consistent with ADR-001's "easy future extraction" rationale.

---

# 6. Marketing Site Architecture (New in v2.0)

## 6.1 Decision

The public marketing site (MKT-01/02/03) is built as a **Next.js application using static generation (SSG) with incremental static regeneration (ISR)**, fully decoupled from the ComplianceIQ platform.

## 6.2 Rationale

- **SEO:** Prospective CASP firms will find ComplianceIQ via search; Next.js gives server-rendered/pre-rendered pages out of the box, which a plain React SPA does not.
- **Editability:** MKT-04 (open question) is resolved in favor of Next.js + a lightweight headless CMS (e.g., Sanity or Payload), so Sosinna's team can edit plan descriptions, copy, and positioning without a developer.
- **Zero shared logic:** The site carries no tenant data and no authentication complexity — the only integration point is the "Request a Demo" lead-capture form, which posts to a simple lead-capture endpoint (can be a lightweight Django endpoint outside the tenant-scoped API, or a third-party form/CRM integration).
- **Independent deploy:** Own repository, own deploy pipeline (e.g., Vercel or the same ECS Fargate cluster as a separate service) — a marketing copy change should never require a platform release.

## 6.3 Open Item Carried Forward

- **MKT-05 (domain):** Still open — SayOne-managed, Synergy-owned, or eventual ComplianceIQ product domain. Ties to CC-02 (platform branding). No architectural blocker either way; DNS/domain is a configuration concern, not a code dependency.

---

# 7. Technology Stack

## Frontend — Firm Application & Platform Admin Portal

- React
- TypeScript
- React Router
- React Query
- react-i18next

## Frontend — Marketing Site

- Next.js
- Headless CMS (Sanity or Payload — final selection deferred to implementation phase)

## Backend

- Python 3.13
- Django
- Django REST Framework
- Celery

## AI

- FastAPI
- LangGraph
- Docling
- AWS Textract

## Storage

- PostgreSQL 16+
- pgvector
- Redis
- Amazon S3

## Reporting (expanded in v2.0 — see Section 11)

- WeasyPrint (PDF)
- docxtpl (Word/.docx export)
- openpyxl (Excel/.xlsx export)

## Monitoring

- CloudWatch
- Grafana Alloy
- New Relic

---

# 8. Architecture Decisions (Summary)

## ADR-001 — Business Platform
**Decision:** Django + DRF. **Reason:** Enterprise workflows, authentication, admin tooling, mature ORM, migrations.

## ADR-002 — AI Platform
**Decision:** Dedicated FastAPI AI Service. **Reason:** Independent AI lifecycle, provider abstraction, easier scaling.

## ADR-003 — Architecture Style
**Decision:** Modular Monolith. **Reason:** Faster delivery while preserving modular boundaries.

## ADR-004 — Tenant Isolation
**Decision:** Schema-per-Tenant. Shared reference data remains in a shared schema.

## ADR-005 — Search
**Decision:** PostgreSQL Full Text Search + pgvector. OpenSearch remains an extension point.

## ADR-006 — Embeddings
**Decision:** Embedding provider configurable. Initial model: text-embedding-3-small. Metadata stored with every vector.

## ADR-007 — AI Providers
**Decision:** Provider abstraction supporting OpenAI, AWS Bedrock, Anthropic Claude, Azure OpenAI, self-hosted models.

## ADR-008 — Regulatory Updates
**Decision:** Automatic detection → human review → manual publish. AI never directly changes the regulatory baseline. **(Constrained further in v2.0 — see Section 9.)**

## ADR-023 — Application Topology *(New in v2.0)*
**Decision:** Single Django backend with namespaced APIs (`firm_api`, `admin_portal_api`); two separate frontend SPAs (Firm App, Admin Portal); marketing site as an independent Next.js application. See Section 5 and 6 for full rationale.

## ADR-024 — Reporting Multi-Format Strategy *(New in v2.0)*
**Decision:** A single structured Report Data Model feeds three renderers — WeasyPrint (PDF), docxtpl (Word), openpyxl (Excel) — rather than three independently maintained report-building code paths. See Section 11.

## ADR-025 — AI Evaluation Harness *(New in v2.0)*
**Decision:** A golden-dataset evaluation harness gates AI mapping accuracy before UAT promotion. See Section 10.

## ADR-026 — Regulatory Monitoring Source Constraint *(New in v2.0)*
**Decision:** MVP regulatory monitoring is restricted to RSS feeds and official public APIs from EUR-Lex, EBA, ESMA, and key national regulators. No HTML scraping or layout-parsing engines. See Section 9.

## ADR-027 — IT Monitoring-System Ingestion *(New in v2.0)*
**Decision:** No direct API integration to firm AML/transaction-monitoring systems for MVP. CSV upload against a fixed SayOne-defined template; aggregated counts only, explicitly no PII. See Section 12.

---

# 9. Regulatory Monitoring Architecture (Expanded in v2.0)

This section makes explicit a constraint that existed only informally in v1.0.

## 9.1 Source Constraint (ADR-026)

- **Permitted sources:** Standard RSS feeds and official public APIs from EUR-Lex, the EBA, the ESMA, and key national regulators (e.g., Banco de Portugal, BaFin).
- **Explicitly not permitted for MVP:** Custom HTML web-scraping, brittle layout-parsing engines, or any scraper dependent on a regulator's page structure remaining stable.
- **Rationale:** Scraping-based approaches break silently when a regulator redesigns a page, creating compliance risk (a missed regulatory update is far worse than a missing feature). RSS/API sources are stable contracts.

## 9.2 Metadata Requirements

Every fetched regulatory item must store:
- **Effective date** (when the rule takes legal effect)
- **Date of download** (when ComplianceIQ retrieved it)

This lets Sosinna's team confirm they are reviewing the most current version, and gives firms an audit-defensible record of when a change was actually known to the platform vs. when it took effect.

## 9.3 Human-in-the-Loop Pattern (unchanged from ADR-008/011, reaffirmed)

Automatic detection → Portal alert to Sosinna's team → human review → manual publish. AI/automation never publishes a regulatory update directly to firms.

## 9.4 Manual Input Interface

The Portal must also provide a structured manual-entry interface so Sosinna's team can enter regulatory changes by hand when a change is identified through channels outside the automated feeds (e.g., direct communication with a regulator, industry briefings).

## 9.5 RE-01 / RE-05 Resolution

- **RE-01 (who maintains the regulatory content database):** Automatic fetch feeds the Portal; Sosinna's team reviews and approves before publication. Content ownership and curation responsibility sits with Sosinna's team; SayOne builds and maintains the ingestion pipeline.
- **RE-05 (news feed sourcing model):** Manual curation by Sosinna's team for MVP. Public regulator portals (e.g., Banco de Portugal) are candidate seed sources for the live news feed (FR-54), not an automated aggregation service.

---

# 10. AI Architecture & Evaluation Strategy (Expanded in v2.0)

## 10.1 AI Principles (unchanged)

AI responsibilities: OCR, document parsing, semantic search, WSP mapping, gap analysis, summaries, recommendations.

AI never: makes regulatory decisions, publishes regulations, approves compliance, closes findings.

## 10.2 AI Evaluation Harness (ADR-025) — New in v2.0

The PRD commits to a **minimum 85% verified accuracy rate** for AI-assisted WSP-to-Requirement mapping, measured against pre-defined verification text vectors during UAT, with all tuning work included in the fixed-fee scope. This requires a concrete, buildable evaluation component:

1. **Golden dataset:** A curated set of representative WSP documents where a human compliance expert has pre-labeled the correct Requirement ID ↔ WSP Section mappings. These labeled pairs are the "verification text vectors."
2. **Evaluation job:** An automated Celery task runs the AI mapping pipeline against the golden dataset whenever the prompt, model version, or embedding configuration changes. It computes precision, recall, and overall accuracy against ground truth.
3. **Release gate:** A model/prompt version must clear the 85% accuracy threshold on the golden dataset before it is promoted to the UAT environment. This is a CI-style gate, not a one-off manual spot-check.
4. **Production feedback loop:** In live use, the rate at which compliance officers override or correct AI suggestions (human override rate — already an ADR-022 metric) feeds back into the same evaluation metrics store, giving Sosinna's team an ongoing accuracy signal beyond the initial UAT gate.
5. **Golden dataset governance:** The dataset itself is versioned; additions/corrections to it are reviewed the same way regulatory content is reviewed, to prevent the evaluation bar from drifting silently.

## 10.3 AI Provider Abstraction (unchanged)

No module may directly call an LLM provider. Provider abstraction supports OpenAI, AWS Bedrock, Anthropic Claude, Azure OpenAI, self-hosted models.

## 10.4 Document Intelligence Pipeline (unchanged)

Upload → Classification → Parsing (Docling) → OCR (Textract) → Chunking → Metadata extraction → Embedding generation → Indexing → Human review (where applicable).

---

# 11. Reporting Architecture (Expanded in v2.0)

## 11.1 Multi-Format Strategy (ADR-024)

The PRD confirms PDF export (FR-60) and leaves Word export "likely" and Excel export "undecided" (RP-04). To avoid three divergent report-building code paths, the architecture uses a **single structured Report Data Model** (a well-defined internal representation of a testing-cycle report: cover details, scope, tests performed, findings, remediation plan, sign-off block) that feeds three independent renderers:

| Format | Renderer | Use Case |
|---|---|---|
| PDF | WeasyPrint (HTML → PDF) | Primary format, regulator-inspection-ready, ComplianceIQ-branded |
| Word (.docx) | docxtpl (Jinja2-style templating over python-docx) | Legal team commentary/markup after generation |
| Excel (.xlsx) | openpyxl | Structured data analysis (e.g., findings register, test result breakdown) |

## 11.2 Rationale

Building all three off one data model means a change to report structure (e.g., a new section added per a future PRD revision) is made once and propagates to all enabled export formats, rather than requiring three parallel updates.

## 11.3 Open Item Carried Forward

**RP-04:** Word export is likely (legal team use case implied by PRD narrative) but not contractually confirmed; Excel export is still undecided. The architecture supports both without committing scope — final inclusion is a product/contract decision, not a technical blocker.

---

# 12. IT Systems & Monitoring-Data Ingestion (New in v2.0)

## 12.1 Decision (ADR-027)

For MVP, ComplianceIQ does **not** integrate directly with firms' AML/transaction-monitoring systems (e.g., SumSub, Veritas) via API.

- Firms manually upload a **CSV extract** against a fixed field template defined by SayOne.
- Only **aggregated counts and period-over-period comparatives** are accepted (e.g., Level 1/2/3 alert counts this month vs. last).
- **Explicitly no PII and no individual customer-level data** may be ingested this way.
- Direct API integration to vendor systems is a later-phase capability, tracked as a Future Extension Point (Section 17).

## 12.2 Rationale

This avoids building and maintaining bespoke connectors to third-party vendor APIs (each with its own auth model, rate limits, and data contract) before the platform has validated which vendors its client firms actually use. The CSV template approach also sidesteps the PII/data-processing complexity of ingesting individual-level monitoring data before a DPA framework for that data flow is agreed.

## 12.3 Vendor Template Sourcing

Sosinna is collecting sample vendor reports (SumSub, Veritas) to inform the CSV field template design — this is a content/design input, not an architectural dependency.

---

# 13. Communication Channel Reference Data (Carried Forward from PRD)

Per OS-02 (resolved): communication channel types are **not** a fixed platform-wide dropdown. Each firm's IT team supplies its own channel list at onboarding via CSV; on import, the platform validates entries against that firm-specific reference list and flags mismatches (e.g., "mail" vs. "email") for admin correction or override. This is a per-tenant reference table, not a shared/global one — noted here because it affects the tenant schema design (see forthcoming Database Architecture document).

---

# 14. Search Strategy (unchanged)

Phase 1: PostgreSQL Full Text Search + pgvector. Future: OpenSearch Adapter. Search abstraction ensures backend code remains unchanged when the adapter is introduced.

---

# 15. Background Processing (unchanged)

Celery + Redis. Used for: OCR, AI processing, report generation (all three formats — Section 11), notification delivery, re-indexing, regulatory monitoring (Section 9), AI evaluation jobs (Section 10).

---

# 16. Multi-Tenant Strategy (unchanged, reaffirmed against v2.0 topology)

One PostgreSQL cluster, shared schema for global reference data (Requirement Library, Test Library, Sampling Methodology Library), dedicated schema per tenant for firm-specific data. The `admin_portal_api` namespace (Section 5) is permitted to read only the shared schema and explicitly-permitted cross-firm metadata — never a tenant schema directly.

Future capability: large tenants can be migrated to dedicated databases.

---

# 17. Internationalization (unchanged)

Initial languages: English, German, French. Architecture supports all official EU languages. Requirement IDs remain language-independent.

---

# 18. Security Principles (unchanged)

JWT authentication, MFA, RBAC, immutable audit logs, TLS, AES-256 encryption at rest, Secrets Manager integration. Full detail deferred to the forthcoming Security Architecture document.

---

# 19. Infrastructure (unchanged)

Deployment: Docker, AWS ECS Fargate (client-owned AWS account, EU-resident data centre — per PRD TI-01). Storage: PostgreSQL, Redis, Amazon S3. Observability: CloudWatch, Grafana Alloy, New Relic. Deployment strategy: Rolling deployment. Uptime target: 99.5% (TI-02, confirmed).

---

# 20. Future Extension Points

- OpenSearch
- Public APIs (TI-05 — confirmed later-phase, not in MVP scope)
- Webhooks
- Self-hosted LLMs
- Dedicated tenant databases
- Additional AI providers
- Direct API integration to IT/AML monitoring vendor systems (Section 12)
- Independent extraction of the Platform Admin Portal into its own service, if scale demands (Section 5.4)
- Non-EU rule sets (e.g., UK post-Brexit) — architecture supports future ingestion but not exposed in UI for MVP
- Marketing site domain decision (MKT-05) and CMS final selection

---

# 21. Open Items Carried Forward from PRD v4.0

These remain open at the product/commercial level; none are architectural blockers, but they are tracked here so the technical specs that follow don't silently assume an answer:

| Ref | Topic | Status |
|---|---|---|
| CC-02 | Platform branding (SayOne / Synergy / ComplianceIQ-only) | Open |
| CC-05 | Demo Day presentation approach | Open |
| MKT-05 | Marketing site domain ownership | Open |
| RP-04 | Word/Excel export — final scope confirmation | Architecture supports both; contractual scope open |
| TI-03 | ISO 27001 / SOC 2 Type II required by clients? | Open — roadmap item, not MVP blocker |
| TI-06 | Total firm count Year 1 | Partial — per-firm user caps known (~50 MVP, uncapped Enterprise), total firm count not yet known |
| GAP-03 | RES-02 significance determination (manual flag vs. platform-calculated) | Open |
| GAP-09 | Who may initiate a WSP mapping override | Partially open |
| GAP-10 | Mid-test regulation update UX (banner vs. persistent notice) | Open |
| GAP-11 | Force-prompt reassignment on user deactivation, or manual? | Partially open |

**Note on Remediation Owner visibility:** The PRD contains an unresolved internal contradiction — FR-52 states Remediation Owners see only their own assigned items, while a client comment on FR-42 (GAP-07) states they should have full view access. Per direction received during this review, **the technical specification builds to FR-52 (own items only)**. This decision reverses the GAP-07 answer as currently documented in PRD v4.0 Section 8.3, and should be reconciled back into the PRD/contract documentation before firm-facing UI work begins on the Remediation Owner dashboard, to avoid a mismatch between what was contractually communicated to Sosinna and what is built.

---

# 21a. Architecture Change Governance — Change Checklist (New in v2.1)

## 21a.1 The Drift Risk

This baseline now sits alongside nine other documents (Database, Backend, AI & Document Intelligence, Security, Infrastructure & DevOps, Engineering Standards, Configuration, Notification, and the Cross-Document Traceability Matrix), all of which reference each other. A single requirement change — e.g., a change to how Requirement versioning works — can require updates across Domain Model, Database, Backend, AI, Reporting, and Security simultaneously. If only some of those are updated, the document set doesn't fail loudly — it silently drifts, and the first sign of trouble is usually a production incident or a client-facing inconsistency months later, not a build failure.

## 21a.2 The Checklist

Every pull request that touches architecture (not routine feature work within an already-specified boundary) must answer the following before merge, recorded in the PR description per Engineering Standards §13:

1. **Which documents are affected?** (List them explicitly — TAB, Database, Backend, AI, Security, Infrastructure, Engineering Standards, Configuration, Notification.)
2. **Which ADR changed, or does a new one need to be written?** (Per ADR Governance — historical ADRs are never edited, only superseded.)
3. **Which diagrams changed?** (Where applicable — pipeline diagrams, schema topology, etc.)
4. **Which tests changed?** (Particularly: does this touch a mandatory-coverage module per Engineering Standards §5.2?)
5. **Which APIs changed?** (Does this trigger the OpenAPI contract diff-check, Engineering Standards §7?)
6. **Which database objects changed?** (New tables, new triggers, new migration — does Database Architecture need a version bump?)
7. **Does the Cross-Document Traceability Matrix need a new or updated row?** (Per that document's Section 9 maintenance rule.)

## 21a.3 Enforcement

This checklist is not a separate approval gate — it's folded into the existing elevated code review requirement (Engineering Standards §6) for any PR touching one of the named high-risk modules, and into the standard PR template (Engineering Standards §13) as a required section for anything self-identified as an architectural change. A PR that answers "no other documents affected" for a change that clearly touches multiple bounded contexts should be treated as a review red flag, not taken at face value.

---

# 21b. Follow-up Specification Set (Updated in v2.1)

The original seven-document follow-up plan (Section 22 below) has been extended based on a structured architecture review following completion of the initial set. Current full document inventory:

| Document | Status |
|---|---|
| Domain Model & Ubiquitous Language | Complete (v1.0) |
| Database Architecture | Complete (v1.2) |
| Backend Architecture | Complete (v1.2) |
| AI & Document Intelligence | Complete (v1.1) |
| Security Architecture | Complete (v1.0) |
| Infrastructure & DevOps | Complete (v1.0) |
| Engineering Standards | Complete (v1.1) |
| Configuration Architecture | Complete (v1.0) |
| Notification Architecture | Complete (v1.0) |
| Cross-Document Traceability Matrix | Complete (v1.0), living document |
| **Architecture Decision Records** | Complete (v1.1) — full ADR-023–027 entries, governance ownership/cadence added |
| **Localization Architecture** | Complete (v1.0) — new |
| **Data Import/Export Framework** | Complete (v1.0) — new |

Deliberately deferred (see the architecture review discussion for rationale): API Integration Framework, standalone Observability Specification, and Operational Runbooks. Search Architecture and the Workflow Configuration boundary statement were folded into Backend Architecture §7a/§7.2 and Configuration Architecture §7 respectively, rather than becoming standalone documents.

---

# 22. Original Follow-up Specifications (Superseded by Section 21b — retained for history)

This baseline (v2.0) is followed by, in planned build order:

1. Database Architecture
2. Backend Architecture
3. AI & Document Intelligence
4. Security Architecture
5. Infrastructure & DevOps
6. Engineering Standards

(Domain Model & Ubiquitous Language v1.0 is already complete and remains valid against this baseline; no changes required.)

---

# 23. Version History

| Version | Date | Notes |
|---------|------|------|
| 1.0 | Draft | Initial Technical Architecture Baseline |
| 2.0 | Jul 2026 | Incorporated PRD v4.0 decisions: application topology (3-app model), marketing site architecture, regulatory monitoring source constraints, IT monitoring-ingestion constraints, AI evaluation harness, multi-format reporting strategy, Remediation Owner visibility resolution, and confirmed/open PRD items carried forward. New ADR-023 through ADR-027 added. Added Section 4a — Cross-Cutting Architectural Conventions (domain event dispatch via transactional outbox, state machine implementation via versioned transition tables, four-environment release strategy with a hard AI-accuracy promotion gate). |
| 2.1 | Jul 2026 | Added Section 21a — Architecture Change Governance / Change Checklist, addressing document-drift risk identified in a structured architecture review. Added Section 21b documenting the extended follow-up specification set: Configuration Architecture, Notification Architecture, and the Cross-Document Traceability Matrix (all v1.0) added alongside the original seven documents. Several review recommendations (Search Architecture, Workflow Configuration boundary) were folded into existing documents rather than becoming standalone specs; others (Localization, Data Import/Export Framework, API Integration Framework, standalone Observability spec, Operational Runbooks) were deliberately deferred as premature or out of scope for this document set. |
| 2.2 | Jul 2026 | Completed the "Next" tier from the architecture review: Localization Architecture (v1.0) and Data Import/Export Framework (v1.0) added as new standalone documents; Search Architecture and the Workflow Configuration boundary cross-reference added to Backend Architecture (§7a, §7.2); Architecture Decision Records updated to v1.1 with full ADR-023–027 entries and new ownership/review-cadence governance. Document inventory (§21b) updated accordingly. |
