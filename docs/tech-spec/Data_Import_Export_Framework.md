# ComplianceIQ – Data Import/Export Framework

**Version:** 1.0
**Status:** Baseline
**Depends On:** Technical Architecture Baseline (TAB) v2.0, Database Architecture v1.2, Backend Architecture v1.2, Security Architecture v1.0
**Audience:** Backend Engineers, Architects, QA

> This document defines one reusable framework for bulk data import (communication channels, IT monitoring data, staff, and future import types) and one for data export (ad hoc/bulk extraction, distinct from the report-generation pipeline). Prior documents referenced CSV imports repeatedly (OS-02 communication channels, TAB v2.0 §12 IT monitoring data) without a shared mechanism — each risked becoming a bespoke, inconsistently-audited implementation.

---

# 1. Purpose

Communication channel imports (OS-02), IT monitoring data uploads (TAB v2.0 §12), and future needs (staff bulk import, evidence metadata bulk tagging) all share the same real shape: a file lands, gets validated, a human reviews what will change, approves it, and the change is applied and audited. Building each independently means five slightly different validation UX patterns, five different audit trails, and five chances to get the "what happens on a bad row" question answered differently. This document fixes that with one framework, instantiated per import type.

Exports are a related but distinct concern — ad hoc or bulk data extraction (a findings register as CSV, an audit log export for a regulator, a DSAR data export per Security Architecture §12.2) — not to be confused with the Reporting pipeline (TAB v2.0 §11), which produces the formal, immutable, signed-off compliance report artifact. This document also defines that as a second, related framework.

---

# 2. Import Pipeline

```
Upload → Validate → Preview → Errors → Approve → Import → Audit
```

## 2.1 `import_job` Table (tenant schema)

| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| import_type | enum | `communication_channels`, `it_monitoring_data`, `staff_bulk`, extensible |
| status | enum | `uploaded`, `validating`, `preview_ready`, `awaiting_approval`, `importing`, `completed`, `failed` |
| file_ref | text | S3 pointer (quarantine-scanned per Security Architecture §9 before validation begins) |
| uploaded_by | uuid, FK | |
| uploaded_at | timestamptz | |
| validation_report | jsonb | per-row pass/fail detail |
| row_count | integer | |
| error_count | integer | |
| approved_by | uuid, FK, nullable | |
| approved_at | timestamptz, nullable | |
| imported_at | timestamptz, nullable | |

No delete grant — an `import_job` record is itself an evidentiary artifact (what data entered the system, when, approved by whom), consistent with the platform's general no-hard-delete posture (Database Architecture §7).

## 2.2 `ImportValidator` Interface

One interface per `import_type`, mirroring the provider-abstraction philosophy already established for AI providers (ADR-007/009) and notification channels (Notification Architecture §7) — no import type gets a bespoke, ungoverned validation code path:

```python
class ImportValidator(Protocol):
    expected_columns: list[str]
    def validate_row(self, row: dict) -> RowValidationResult: ...
```

Registered validators (Phase 1): `CommunicationChannelValidator` (OS-02), `ITMonitoringDataValidator` (TAB v2.0 §12 — enforces aggregated-counts-only, rejects any column resembling individual/PII data outright rather than silently accepting it).

## 2.3 Pipeline Stages

1. **Upload:** presigned S3 upload (Backend Architecture §12 pattern reused), lands in the malware-scan quarantine flow (Security Architecture §9) before validation ever begins.
2. **Validate:** `ImportValidator.validate_row()` runs against every row; results populate `validation_report` (jsonb) — per-row pass/fail with a reason for any failure (e.g., "channel_name is a duplicate," "level_1_alerts must be numeric").
3. **Preview:** the uploader sees a summary (row count, error count, a sample of both valid and invalid rows) **before anything is committed** — no import type silently applies partial data.
4. **Errors:** invalid rows are never partially imported alongside valid ones by default — the uploader can either fix and re-upload, or explicitly choose to proceed with valid rows only (an explicit choice, logged, not a silent default).
5. **Approve:** an explicit approval step, gated per `import_type` via a `Configuration Architecture`-governed flag (`import.{type}.requires_second_approver`) — low-risk reference data (e.g., communication channels) defaults to self-approval by the uploader; higher-risk types can require a second approver via the existing Dual-Control service (Backend Architecture §8) without building new approval logic.
6. **Import:** applies validated rows transactionally within a single service-layer call, writes a `source_import_job_id` foreign key on every created/updated row (so any imported record is traceable back to the exact import event that produced it — genuinely useful the first time someone asks "where did this bad data come from"), and emits a `DataImported` domain event via the outbox (Backend Architecture §6).
7. **Audit:** the full `import_job` record persists indefinitely; the `DataImported` event feeds the standard Tenant Audit Log (Database Architecture §5.9) alongside the specific rows changed.

---

# 3. Export Pipeline

## 3.1 `export_job` Table (tenant schema)

| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| export_type | enum | `findings_register`, `audit_log`, `dsar_export`, extensible |
| format | enum | `csv`, `json`, `xlsx`, `zip` |
| requested_by | uuid, FK | |
| requested_at | timestamptz | |
| filters_applied | jsonb | exact query filters used — reproducibility and audit, not just convenience |
| status | enum | `queued`, `processing`, `ready`, `expired`, `failed` |
| file_ref | text, nullable | S3 pointer, per-tenant KMS-encrypted (Security Architecture §6.1) |
| signed_url_expires_at | timestamptz, nullable | |
| row_count | integer, nullable | |

## 3.2 Signed, Time-Limited Delivery

Every export is delivered as a **presigned S3 URL with a defined expiry** (default 24 hours), not a permanent link — accessing it requires the requester to still be an authenticated session at generation time, and the link itself expires rather than remaining valid indefinitely if it were ever forwarded or logged somewhere it shouldn't be.

## 3.3 Distinction from the Reporting Pipeline

| | Reports (TAB v2.0 §11) | Exports (this document) |
|---|---|---|
| Purpose | Formal, immutable, signed-off compliance artifact | Ad hoc/bulk data extraction for analysis, regulator request, or DSAR |
| Immutability | Yes — `report.report_data_snapshot` frozen at publication (Database Architecture §5.6) | No — reflects live data at export time; re-running the same export later can yield different results if underlying data changed |
| Formats | PDF, DOCX, XLSX (via the shared Report Data Model) | CSV, JSON, XLSX, ZIP |
| Approval gate | AML officer agreement + Senior Mgmt sign-off (FR-55, FR-61) | None required by default — an export is a read operation, not a compliance assertion |

They can share rendering libraries (`openpyxl` for XLSX, standard CSV writer) but are architecturally and semantically distinct — an export is never mistaken for, or substitutable as, a formal report.

## 3.4 Audit

Every `export_job` — what was exported, by whom, when, and under what filters — is logged to the Tenant Audit Log, directly supporting the DSAR export capability described in Security Architecture §12.2 ("a report of all personal data held about a given individual"), which is itself just a specific, pre-defined `export_type`.

---

# 4. Registered Import/Export Types (Phase 1)

| Type | Direction | Ties To |
|---|---|---|
| `communication_channels` | Import | OS-02, TAB v2.0 §13 |
| `it_monitoring_data` | Import | TAB v2.0 §12, ADR-027 |
| `findings_register` | Export | PRD Findings & Remediation |
| `audit_log` | Export | Security Architecture §10 |
| `dsar_export` | Export | Security Architecture §12.2 |

`staff_bulk` import and additional export types are extension points, registered the same way, as real requirements confirm the need — not built speculatively now.

---

# 5. Deliberately Not Built Now

- **Scheduled/recurring exports** (e.g., an automatic monthly export to an external mailbox) — no confirmed PRD requirement for this; the `export_job` table and Scheduled Jobs Registry (Configuration Architecture §8) could support it later without a redesign, but it isn't built speculatively.
- **A generic external API integration framework for imports** (as distinct from CSV upload) — explicitly deferred per the earlier architecture review, consistent with ADR-027's later-phase treatment of direct vendor API integrations.

---

# 6. Open Items Carried Forward

| Item | Status |
|---|---|
| Full validator rule set for `staff_bulk` (once confirmed as a real Phase 1 need) | Not yet built; framework supports adding it as a registered `ImportValidator` |
| Whether any export type needs a second-approver gate | Currently none do by default; the Dual-Control service (Backend Architecture §8) is available if a future requirement needs one |
| Signed URL expiry window (24h default) | Tunable via Configuration Architecture if operational experience suggests otherwise |

---

# 7. Version History

| Version | Date | Notes |
|---------|------|------|
| 1.0 | Jul 2026 | Initial Data Import/Export Framework: unified Upload → Validate → Preview → Errors → Approve → Import → Audit pipeline with a registered `ImportValidator` interface; `import_job`/`export_job` tables with full traceability (`source_import_job_id`) and no-delete audit posture; signed time-limited export delivery; explicit distinction from the Reporting pipeline; DSAR export framed as a registered export type rather than a bespoke mechanism. |
