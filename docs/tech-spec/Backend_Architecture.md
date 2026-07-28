# ComplianceIQ – Backend Architecture

**Version:** 1.0
**Status:** Baseline
**Depends On:** Technical Architecture Baseline (TAB) v2.0, Database Architecture v1.1, Domain Model & Ubiquitous Language v1.0
**Audience:** Backend Engineers, Architects, QA, AI Engineers

> This document defines the backend implementation architecture for ComplianceIQ Phase 1: module structure, API conventions, tenant resolution, authentication/authorization, the domain event and state-machine mechanisms fixed at baseline level (TAB v2.0 Section 4a), the reusable dual-control pattern, background processing, and the AI service integration contract. It is the source of truth for how the Django modular monolith is actually organized and how requests flow through it.

---

# 1. Purpose

This document translates TAB v2.0 and the Database Architecture into a concrete backend implementation design. It answers the questions those documents deliberately left open:

- How is the Django project actually organized into modules?
- How does a request resolve to the correct tenant schema?
- How are the outbox and state-machine patterns (TAB v2.0 §4a) implemented in code?
- What are the API versioning, pagination, and error-response conventions (TAB v2.0 §4a.4, explicitly deferred to this document)?
- How does the maker-checker/dual-control pattern — which repeats across four separate PRD features — get built once instead of four times?
- How does Django talk to the FastAPI AI service?

---

# 2. Guiding Principles (from TAB v2.0, applied concretely)

- **Modular Monolith, Hexagonal internally.** One Django project. Each bounded context (Section 3 of the Domain Model) is a Django app with its own `domain/` (entities, business rules), `services/` (use cases), `adapters/` (ORM models, external calls), and `api/` (DRF views/serializers) sub-packages — ports & adapters within a single deployable, per ADR-004 (ADR set).
- **Firm/Portal separation is enforced in code, not convention.** `firm_api` and `admin_portal_api` are separate Django URL namespaces with separate permission-class base classes; a `admin_portal_api` view has no import path to any tenant-scoped ORM manager.
- **Every compliance-critical write goes through a service, never a bare ORM `.save()` from a view.** This is where state-machine checks, dual-control checks, and outbox event emission are enforced — putting them in the service layer means they can't be bypassed by a future view that forgets to call them.

---

# 3. Module Structure

```
compliance_iq/
├── config/                        # settings, urls, celery app config
├── core/                          # cross-cutting: tenant middleware, outbox, dual-control, base permission classes
│
├── identity/                      # Identity & Access bounded context
│   ├── domain/  services/  adapters/  api/firm_api/  api/admin_portal_api/
├── organization/                   # Firm, Staff, Service Line, Org Chart
├── regulatory_library/             # Regulation, Requirement, Test Library, Sampling Methodology (shared-schema owner)
├── wsp_management/                 # WSP, WSP Version, AI Mapping, Gap Analysis
├── compliance_testing/             # Test Schedule, Test Execution, Evidence, Sampling Record
├── findings_remediation/           # Finding, Remediation Plan, Remediation Milestone
├── reporting/                      # Report generation, multi-format rendering orchestration
├── notifications/                  # Notification, Distribution List, Notification Preference
├── it_risk/                        # IT System, IT Vendor, IT Incident, Monitoring Data Upload
├── ai_gateway/                     # Django-side client for the FastAPI AI Service (Section 9)
└── platform_admin/                 # Portal-only: regulatory content authoring, tenant provisioning, golden dataset mgmt
```

Each bounded-context app owns its own tables (Database Architecture Sections 4–5) and exposes a **service interface** that other apps call — apps never reach into another app's ORM models directly. E.g., `findings_remediation` calls `compliance_testing.services.get_test_execution(id)`, not `TestExecution.objects.get(id=...)`.

---

# 4. API Conventions (resolves TAB v2.0 §4a.4)

## 4.1 Versioning

URL path versioning: `/api/v1/firm/...` and `/api/v1/admin/...`. A breaking change ships as `/api/v2/...` alongside the still-supported `v1`, rather than header-based versioning — simpler to reason about, cache, and document (e.g., in Swagger/OpenAPI per-version specs).

## 4.2 Pagination

- **Standard list endpoints** (test schedules, findings register, staff list): DRF `PageNumberPagination`, default page size 25, max 100.
- **Audit logs and notifications** specifically: **cursor pagination** (`created_at`/`id` composite cursor), since these are append-only, time-ordered, and can grow to a size where offset-based pagination degrades badly.

## 4.3 Error Response Format

A consistent JSON error envelope on every non-2xx response, loosely modeled on RFC 7807:

```json
{
  "error": {
    "code": "FINDING_ALREADY_CLOSED",
    "message": "This finding has already been closed and cannot be modified.",
    "details": { "finding_id": "...", "closed_at": "..." }
  }
}
```

`code` is a stable machine-readable string (used by the frontend for conditional UI logic, e.g., disabling a button); `message` is human-readable; `details` is optional structured context. Validation errors (400s) use the same envelope with `details` containing a field → message map.

## 4.4 Authentication Header

`Authorization: Bearer <JWT>` on every request. The JWT carries `user_id`, `tenant_id` (omitted entirely for Portal Super Admin tokens — see Section 5), `system_role`, and `mfa_verified` claims.

---

# 5. Tenant Context Resolution

## 5.1 Decision

Tenant resolution is **subdomain-first, with JWT-claim cross-validation** — a hybrid of routing convenience and an unspoofable security check.

- Each firm is assigned a unique **slug** at onboarding (e.g., `acme`), and is reachable at `{slug}.complianceiq.com`. DNS is a single wildcard record (`*.complianceiq.com`) plus a wildcard ACM certificate — no per-firm DNS or certificate provisioning is required, so this adds no operational step to the Tenant Migration Runner (Database Architecture §8) beyond generating and validating the slug.
- On login, the firm user's JWT is issued with a `tenant_id` claim pointing at their `tenant_<firm_uuid>` schema (unchanged from v1.0 of this document).
- A Django middleware (`TenantContextMiddleware`), running early in the middleware stack (immediately after authentication, before any view logic):
  1. Resolves the requested subdomain to a `firm_registry.slug` → `tenant_id` lookup (shared schema, cached).
  2. Cross-checks that value against the `tenant_id` claim in the validated JWT.
  3. **Rejects the request outright (403) on any mismatch** — e.g., a valid token for Firm A hitting Firm B's subdomain — rather than silently trusting either signal alone.
  4. On match, sets the PostgreSQL `search_path` for the current request's database connection to `tenant_<firm_uuid>, public`.
- Every subsequent ORM query in `firm_api` views resolves against that schema automatically — no per-query tenant filtering needed, no risk of a forgotten `WHERE tenant_id = ...` clause leaking cross-tenant data.

## 5.2 Why Subdomain-Only (or JWT-Only) Isn't Enough on Its Own

- **Subdomain alone is not a security boundary** — the `Host` header is client-controlled and can be spoofed, or mis-set by a misconfigured proxy. Routing tenant context purely off the subdomain would let a crafted request potentially resolve into the wrong schema.
- **JWT-only** (the original v1.0 design of this document) is secure but gives up real operational and UX value for free: instant visual/URL confirmation of which firm's environment is in view, cleaner incident response (a firm's subdomain can be pulled at the routing layer without touching others), and same-origin isolation between tenants for anything that behaves origin-scoped in the browser.
- The hybrid keeps the JWT claim as the **authoritative** security check while using the subdomain as the primary routing signal and the UX/operational win — a mismatch between the two is always treated as a rejection, never as "trust whichever one is present."

## 5.3 Portal Requests Never Get a Tenant Context

`admin_portal_api` requests are served from a separate, non-wildcard host (e.g., `admin.complianceiq.com`) and are authenticated against **Platform Super Admin** accounts, whose JWTs carry no `tenant_id` claim at all. `TenantContextMiddleware` explicitly does not run for `admin_portal_api/` routes; instead, `AdminPortalDbRouter` restricts all ORM access on that path to the `public` (shared) schema only. This is the concrete code-level enforcement of the TAB v2.0 Section 5.2 boundary — a Portal view has no code path, not even an error-handled one, that can set a tenant search_path.

## 5.4 Supporting Infrastructure Notes

- **CORS:** `django-cors-headers` configured with a regex origin pattern (`^https://[\w-]+\.complianceiq\.com$`) rather than an explicit allow-list, so new tenants require no CORS config change at onboarding.
- **Local development:** wildcard-friendly DNS resolution (e.g., `*.lvh.me` or `*.nip.io`, both of which resolve to `127.0.0.1`) so developers can exercise subdomain routing locally without editing `/etc/hosts` per tenant.
- **Marketing site domain (MKT-05):** this decision should be finalized alongside MKT-05, since the marketing site root, the `app.` (or bare) domain, and `*.complianceiq.com` tenant subdomains all need to sit under one coherent domain strategy rather than being decided independently.

---

# 6. Domain Event Implementation (implements TAB v2.0 §4a.1)

## 6.1 Outbox Table

```
outbox_event (per-schema: exists in both shared and every tenant schema)
├── id                uuid, PK
├── event_type         text        e.g. "FindingClosed", "ReportPublished"
├── aggregate_id       uuid        the entity the event is about
├── payload            jsonb
├── created_at         timestamptz
├── processed_at        timestamptz, nullable
└── attempt_count       integer, default 0
```

Written in the **same database transaction** as the state change that produced it (e.g., `finding.close()` service method inserts both the `finding` status update and the `outbox_event` row atomically).

## 6.2 Poller

A Celery Beat task runs every 2–5 seconds per schema, executing:

```sql
SELECT * FROM outbox_event
WHERE processed_at IS NULL
ORDER BY created_at
FOR UPDATE SKIP LOCKED
LIMIT 100;
```

`SKIP LOCKED` lets multiple poller workers run concurrently without double-processing the same row. Each claimed event is dispatched to its registered consumer(s) (a simple `event_type → [handler_function]` registry per app), and `processed_at` is set once all handlers succeed. A handler failure increments `attempt_count` and leaves the row unprocessed for retry (with backoff), rather than silently dropping it.

## 6.3 Consumer Idempotency

Consumers (notification dispatch, audit-log mirroring, re-indexing, AI evaluation triggers) must be idempotent, since the outbox guarantees **at-least-once** delivery, not exactly-once. Each consumer checks a `processed_event_ids` de-dup table (or, where the downstream action is naturally idempotent — e.g., re-indexing a document — simply re-runs safely) before acting.

---

# 7. State Machine Implementation (implements TAB v2.0 §4a.2)

## 7.1 Transition Table Pattern

For each state-machined entity (Test Execution, Finding, Report, Regulatory Update), a `<entity>_transition` config (Python dict, not a database table, since these rarely change and are reviewed as code) defines:

```python
TEST_EXECUTION_TRANSITIONS = {
    ("draft", "assigned"): {"allowed_roles": ["CCO"]},
    ("assigned", "in_progress"): {"allowed_roles": ["LEAD_TESTER"]},
    ("in_progress", "review"): {"allowed_roles": ["LEAD_TESTER"]},
    ("review", "approved"): {"allowed_roles": ["CCO"]},
    ("review", "in_progress"): {"allowed_roles": ["CCO"]},  # sent back for correction
    ("approved", "closed"): {"allowed_roles": ["CCO"]},
}
```

A single `apply_transition(entity, from_state, to_state, actor)` service function:
1. Checks `(from_state, to_state)` exists in the table.
2. Checks `actor`'s role is in `allowed_roles`.
3. Performs the state change and the audit log write in one transaction.
4. Emits the corresponding domain event via the outbox (Section 6).

Any attempt to change status outside this function (e.g., a direct `.save()`) is caught by the Database Architecture's PostgreSQL immutability triggers as a second line of defense.

## 7.2 Workflow Configuration Boundary (Cross-Reference)

The transition tables in Section 7.1 are **intentionally code-defined, not tenant-configurable**, in Phase 1 — this is a deliberate architectural boundary, not an oversight. The full rationale (why customization isn't built now, and what the extension point looks like if a client's need for a custom workflow — e.g., an added "Manager Review" stage before "Compliance Review" — is ever confirmed on the roadmap) lives in **Configuration Architecture §7**, which governs this boundary from the configuration-taxonomy side. This section is where the boundary is *implemented*; Configuration Architecture §7 is where it's *governed and justified*. If that boundary ever moves, both sections change together — see the Architecture Change Checklist (TAB v2.1 §21a).

---

# 7a. Application Search Architecture (New)

AI & Document Intelligence covers *semantic* search over regulatory and WSP content (hybrid BM25 + vector retrieval, AI & Document Intelligence §5). This section covers a different, previously undocumented concern: **ordinary structured-entity search** across the Firm App and Admin Portal — global search, staff search, finding search, report search — none of which need embeddings or an LLM, but which still need a defined indexing and ranking approach so five different list screens don't each reinvent filtering logic independently.

## 7a.1 Scope

| Search Surface | Entities | Notes |
|---|---|---|
| Global search (Firm App) | WSP sections, Findings, Test Executions, Staff, Evidence file names | Cross-entity, single search box — the "find anything" experience |
| Staff search | `staff_member` | Name, title, department, reports-to chain |
| Finding search / register filter | `finding` | Status, severity, requirement code, date range — mostly structured filtering, not free-text ranking |
| Report search | `report` | Testing period, status, publication date |
| Portal-side firm search (Admin Portal) | `firm_registry` only | Bounded by the Portal/Firm data boundary (TAB v2.0 §5.2) — never reaches into a tenant schema |

## 7a.2 Indexing & Ranking Approach

- **Structured filtering** (status, date range, severity, requirement code): standard indexed B-tree columns and DRF `django-filter`-style query parameters — no special ranking needed, this is exact-match/range filtering, not relevance search.
- **Free-text fields** (WSP section text, finding descriptions, staff names): the same PostgreSQL GIN `tsvector` indexing already established for regulatory content (Database Architecture §11) is reused here — **BM25 scoring** (Section 5.1 pattern from AI & Document Intelligence, reused rather than reinvented) applies wherever free-text relevance ranking matters, keeping one consistent ranking philosophy across the platform instead of a second, different one just for application search.
- **Global search specifically** fans out to each entity's own indexed search (parallel queries, not a single denormalized search-everything table) and merges results by entity type in the UI, rather than building a separate search index/service (e.g., Elasticsearch) — unjustified operational overhead at Phase 1 scale (~100 firms), consistent with the "PostgreSQL FTS is sufficient for Phase 1, OpenSearch remains a future extension point" position already established in ADR-005/ADR-008.

## 7a.3 Tenant Scoping

Every application search query runs through the same `TenantContextMiddleware`-scoped connection as any other request (Section 5) — search results are automatically bounded to the requesting user's tenant schema with no separate search-specific isolation logic needed. This is a direct benefit of the schema-per-tenant model: there's no cross-tenant search index to accidentally leak from.

---

# 8. Dual-Control (Maker-Checker) Service

## 8.1 Why a Shared Service

Four separate PRD features require a maker-checker pattern with slightly different rules:

| Feature | Approvers Required | "Must Differ From" Rule |
|---|---|---|
| WSP mapping confirmation (FR-32) | 2 | Both must differ from the WSP's author |
| Finding closure (FR-44/45) | CCO + 1 Senior Mgmt | Both must differ from `recorded_by` |
| Sampling selection change (FR-21c) | 1 senior team member | Must differ from original recorder |
| Remediation deadline extension (GAP-08) | CCO or 1 other Senior role | (no author-exclusion rule) |

## 8.2 Design

A single `DualControlRequest` service, parameterized per use:

```python
DualControlPolicy(
    required_approvals=2,
    excluded_actor_ids=[author_id],   # cannot approve their own submission
    allowed_roles=["CCO", "SENIOR_MGMT"],
    require_written_reason=False,
)
```

Each of the four features constructs its own `DualControlPolicy` and calls a shared `dual_control.request_approval(...)` / `dual_control.record_approval(...)` pair of service functions. Approval records are written to a shared `approval_record` table (tenant schema) with `policy_context` (e.g., `"finding_closure"`), keeping all four features' audit trails structurally consistent instead of four ad hoc implementations that could each get the "must differ from author" rule subtly wrong.

---

# 9. AI Service Integration (Django ↔ FastAPI)

## 9.1 Decision: Asynchronous Job Pattern

Django never makes a synchronous blocking call to the FastAPI AI Service for anything that could be slow (OCR, WSP mapping, gap analysis). Instead:

1. Django enqueues a Celery task (`ai_gateway.tasks.request_wsp_mapping`) and creates an `ai_job` record (`status: queued`).
2. The Celery task calls the FastAPI AI Service's endpoint, which itself processes asynchronously (Docling parse → Textract OCR → chunk → embed → mapping suggestion) and either:
   - **Callback:** POSTs the result back to a Django webhook endpoint (`/internal/ai-callback/`) on completion, or
   - **Polling fallback:** if the callback fails/times out, a periodic Celery task polls the AI Service's job-status endpoint.
3. Django updates `ai_job.status` to `completed` and writes the `ai_mapping` suggestion rows (as `pending_review` — never auto-confirmed, per ADR/PRD AI boundaries).
4. The frontend polls `/api/v1/firm/wsp/{id}/mapping-status/` or receives a websocket/notification push once ready.

## 9.2 Why Not Synchronous

WSP documents can be dozens of pages; OCR and LLM-based mapping suggestion generation are variable-latency operations that can run well past any reasonable HTTP request timeout. A synchronous call would tie up a Django worker thread for the duration and produce a poor user experience (a spinning page with no feedback) for what should be an async background job with progress visibility.

## 9.3 Provider Abstraction Boundary

Per ADR-007/ADR-009, no Django code calls an LLM provider directly — only the FastAPI AI Service does, behind its own provider abstraction. Django's `ai_gateway` app only ever talks to the AI Service's own internal API contract, never to OpenAI/Bedrock/Anthropic/Azure directly. This keeps the "no module may directly call an LLM provider" rule enforceable at the network boundary, not just by convention.

---

# 10. Test Scheduling Engine (Anchor Strategy Pattern)

GAP-01 (the exact anchor-date logic — calendar quarter vs. 90-days-from-onboarding vs. mid-quarter-onboarding handling) is still open at the product level. Rather than hardcode one interpretation and risk a rewrite once it's resolved, the scheduler is built behind a strategy interface:

```python
class AnchorStrategy(Protocol):
    def compute_due_dates(self, test_definition, firm_onboarded_at) -> list[date]: ...
```

Phase 1 ships with a default `CalendarQuarterAnchorStrategy`. Once GAP-01 is resolved with Sosinna, either that default is confirmed or swapped for `RollingWindowAnchorStrategy` (90-days-from-onboarding) — a configuration change, not a rewrite of the scheduling engine itself. The CCO-facing manual scheduling calendar (GAP-04) and the "required test not scheduled" alert (Section 12, PRD) sit on top of this and are unaffected by which anchor strategy is active.

---

# 11. Background Processing (Celery Queue Design)

| Queue | Used For | Notes |
|---|---|---|
| `default` | General service-layer async tasks | |
| `outbox` | Outbox poller + event dispatch | High frequency, short tasks |
| `ai` | AI Service job dispatch/polling | Long-running, isolated so a slow AI call can't starve other queues |
| `reporting` | Report generation (all 3 formats) | CPU/IO heavy (WeasyPrint/docxtpl/openpyxl), isolated from user-facing request queues |
| `notifications` | Notification delivery (email, in-platform) | |
| `regulatory_monitoring` | RSS/API polling for regulation changes (TAB v2.0 §9) | Scheduled, low frequency |
| `ai_eval` | Golden-dataset evaluation runs (TAB v2.0 §10.2) | Triggered on prompt/model config change, gates UAT promotion |

Each queue has its own Celery worker pool sizing and retry policy (exponential backoff, max 5 retries for transient failures, dead-letter logging for anything that exhausts retries — surfaced to CloudWatch/New Relic per TAB v2.0 monitoring stack).

---

# 12. Evidence Upload Flow

1. Frontend requests a presigned S3 upload URL from `/api/v1/firm/evidence/upload-url/` (scoped to the firm's tenant, per-tenant encryption key per NFR-02).
2. Frontend uploads directly to S3 (bypasses Django for the file bytes themselves — avoids tying up an app server thread on large video/audio evidence uploads).
3. Frontend confirms completion to Django, which writes the `evidence` row (Database Architecture §5.4) with the S3 key, `uploaded_by`, `uploaded_at`.
4. No delete endpoint exists for `evidence` at the API layer at all — consistent with the "no DELETE grant" database-level enforcement (Database Architecture §5.4).

---

# 13. Permission Enforcement Layering

Three layers, deliberately redundant:

1. **DRF permission classes** — per-endpoint, role-based (e.g., `IsCCO`, `IsLeadTesterAssignedToTest`).
2. **Service-layer checks** — e.g., `apply_transition()` (Section 7) re-checks the actor's role independent of what the view already checked, so a service is safe to call from anywhere, including future code paths.
3. **Database triggers** — immutability enforcement (Database Architecture §6) as the final backstop.

This mirrors the DB immutability philosophy: a permission check that only exists in one layer is one bug away from being bypassed.

---

# 14. Open Items Carried Forward

| Item | Status |
|---|---|
| GAP-01 anchor-date logic | Scheduler built behind `AnchorStrategy` interface (Section 10) pending product resolution |
| GAP-09 (who may initiate a WSP mapping override) | Dual-control policy (Section 8) currently allows any Compliance Officer to initiate; role restriction pending product clarification |
| GAP-10 (mid-test regulation update UX) | Backend emits the event (`RegulatoryUpdateDetected` → outbox); banner vs. persistent-notice UI decision belongs to frontend/UX, not backend |
| RP-04 (Word/Excel export final scope) | Both renderers implemented per Reporting Architecture (TAB v2.0 §11); enabling/disabling per contract is a configuration flag, not a build blocker |

---

# 15. Version History

| Version | Date | Notes |
|---------|------|------|
| 1.0 | Jul 2026 | Initial Backend Architecture: module structure, API conventions, JWT-claim tenant resolution, outbox and state-machine implementations, shared dual-control service, async AI integration pattern, pluggable test-scheduling anchor strategy. |
| 1.1 | Jul 2026 | Adopted subdomain-per-tenant (`{slug}.complianceiq.com`) with JWT-claim cross-validation, replacing pure JWT-only tenant resolution. Subdomain mismatch against the JWT's `tenant_id` claim is rejected outright — subdomain is the routing signal, JWT remains the authoritative security check. Added CORS/local-dev notes and tied the decision to the open MKT-05 domain question. |
| 1.2 | Jul 2026 | Added Section 7.2 cross-referencing the workflow configuration boundary now governed in Configuration Architecture §7. Added Section 7a — Application Search Architecture, covering global/staff/finding/report search (distinct from AI & Document Intelligence's semantic search over regulatory/WSP content), reusing the platform's established GIN/BM25 pattern rather than introducing a separate search stack. |
