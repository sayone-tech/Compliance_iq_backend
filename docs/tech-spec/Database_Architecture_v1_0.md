# ComplianceIQ – Database Architecture

**Version:** 1.0
**Status:** Baseline
**Depends On:** Technical Architecture Baseline (TAB) v2.0, Domain Model & Ubiquitous Language v1.0
**Audience:** Backend Engineers, DBAs, Architects, QA

> This document defines the database design for ComplianceIQ Phase 1: schema topology, table structures for core entities, versioning and immutability enforcement, audit logging, retention, tenant provisioning, and vector storage. It implements the decisions fixed in TAB v2.0 (ADR-004, ADR-005, ADR-015, ADR-024, ADR-025, ADR-026, ADR-027) and the entities defined in the Domain Model.

---

# 1. Purpose

This document translates the architectural decisions in TAB v2.0 and the entities in the Domain Model into a concrete, buildable database design. It is the source of truth for:

- Schema topology (shared vs. tenant)
- Core table structures
- Versioning and immutability patterns
- Audit log design
- Retention and deletion policy
- Tenant provisioning
- Vector/embedding storage

It does not define Django ORM model code or migration file contents — that is an implementation detail of Backend Architecture — but every table here is intended to map directly to one.

---

# 2. Key Design Decisions

## 2.1 Primary Key Strategy

**All tables, shared and tenant, use UUIDv7 primary keys.**

Rationale: schema-per-tenant (ADR-004) means IDs don't need to be globally unique for correctness today, but the TAB already commits to a future capability of migrating large tenants to dedicated databases (TAB Section 16). Auto-increment integers would collide or require remapping in that migration; UUIDv7 avoids that entirely while preserving better index locality than random UUIDv4 (time-ordered, so B-tree inserts stay sequential rather than random).

## 2.2 Immutability Enforcement — Database-Level, Not Just Application-Level

Tables holding regulator-facing, immutable-once-finalized data (Test Results, Findings after closure, Evidence, Reports after sign-off, Audit Logs, published Regulation/Requirement/WSP versions) enforce immutability with **PostgreSQL triggers** that raise an exception on `UPDATE` or `DELETE` once a row's status reaches a terminal state — in addition to Django-level permission checks.

Rationale: NFR-04 and NFR-07 state that **not even administrators** can modify or delete these records. Application-layer-only enforcement can be bypassed by anyone with direct database access (a DBA, a support engineer running a manual fix, a compromised admin account). A database trigger cannot be bypassed without a superuser role explicitly altering the trigger itself — which is its own audited, exceptional event.

## 2.3 Audit Log Placement — Two-Tier

- **Tenant Audit Log** (per-tenant schema): every action a firm user takes.
- **Platform Audit Log** (shared schema): every action a Platform Super Admin takes in the Portal — publishing a regulation update, editing the Test Library, provisioning a tenant, changing system-wide settings.

Rationale: mirrors the hard Portal/Firm boundary established in TAB v2.0 Section 5 — Portal actions and firm actions are different audiences' evidence trails and must not be interleavable or queryable from the same table.

## 2.4 Embedding Storage — Split by Ownership

- **Regulatory content embeddings** (Requirement text, Article text, Guidance) → shared schema. Authored once by the Portal, read by every tenant.
- **WSP content embeddings** (a firm's own compliance manual, chunked and embedded for AI mapping) → each tenant's own schema.

Rationale: WSP content is firm-confidential (ADR-004 tenant isolation applies to it fully); regulatory text is common reference data shared across all tenants and would be wasteful and inconsistent to duplicate per-tenant.

## 2.5 Tenant Provisioning — Automated

A new tenant schema is created and migrated automatically when a Firm transitions from `Prospect` to `Active` in its lifecycle (Domain Model Section 4), via a Celery task (the "Tenant Migration Runner," per ADR-018) — not a manual DBA step. See Section 8.

---

# 3. Schema Topology

```
PostgreSQL Cluster (single, EU-resident — per TI-01)
│
├── shared schema (public)
│   ├── Regulatory Library (Regulation, Regulation Version, Article, Requirement)
│   ├── Test Library (Test Definition, Test Step Template, Evidence Checklist Template)
│   ├── Sampling Methodology Library
│   ├── Regulatory Content Embeddings
│   ├── Prompt Templates
│   ├── AI Evaluation Golden Dataset (Section 10, TAB v2.0)
│   ├── Platform Audit Log
│   ├── Firm Registry (cross-firm metadata visible to Portal: name, jurisdiction, service lines, last-active — per SA-06)
│   └── Tenant Schema Registry (tracks which schema belongs to which firm, migration version applied)
│
├── tenant_<firm_uuid> schema (one per firm)
│   ├── Firm Profile
│   ├── Users, Roles, Role Mappings
│   ├── Staff (non-login governance records)
│   ├── Service Lines (firm's active set)
│   ├── WSP, WSP Version, WSP Section, AI Mapping
│   ├── WSP Content Embeddings
│   ├── Test Schedule, Test Execution, Test Step Instance
│   ├── Evidence
│   ├── Sampling Records
│   ├── Findings, Remediation, Remediation Milestone
│   ├── Reports
│   ├── Tenant Audit Log
│   ├── Notifications, Notification Preferences
│   ├── Distribution Lists
│   ├── IT Systems / Vendor Inventory, IT Incidents
│   ├── Communication Channel Reference (per-firm, per OS-02)
│   └── BCP Call Tree
│
└── tenant_<firm_uuid> schema (next firm) ...
```

Naming convention: `tenant_<firm_uuid>` where `firm_uuid` is the Firm's primary key, sanitized for PostgreSQL schema-name rules (hyphens replaced with underscores).

---

# 4. Shared Schema — Core Tables

## 4.1 Regulatory Library

**`regulation`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| name | text | e.g. "MiCA", "DORA" |
| official_reference | text | e.g. "EU 2023/1114" |
| created_at | timestamptz | |

**`regulation_version`** — versioned, immutable once published (ADR-008, ADR-011)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| regulation_id | uuid, FK → regulation | |
| version_label | text | |
| effective_date | date | when the rule takes legal effect |
| fetched_at | timestamptz | date-of-download (Section 9.2, TAB v2.0) |
| source | text | RSS/API source identifier (ADR-026) |
| status | enum | `detected`, `under_review`, `published`, `superseded` |
| published_at | timestamptz, nullable | set only on publish; row becomes immutable once set |
| published_by | uuid, FK → platform_user | |

*Immutability trigger: blocks UPDATE/DELETE once `status = 'published'`.*

**`article`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| regulation_version_id | uuid, FK | |
| article_number | text | e.g. "Art. 92" |
| text_content | text | |

**`requirement`** — canonical, versioned, language-independent ID (Domain Model Section 10)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| canonical_code | text, unique | e.g. `REQ-MICA-001`, `TM-01` |
| article_id | uuid, FK | |
| version | integer | |
| status | enum | `active`, `retired` |
| superseded_by | uuid, FK → requirement, nullable | |
| created_at | timestamptz | |
| retired_at | timestamptz, nullable | |

Requirement rows are never deleted; retirement is a status change, and old versions remain queryable (SA-01, SA-02).

## 4.2 Test Library

**`test_definition`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| requirement_id | uuid, FK | |
| version | integer | |
| frequency | enum | `monthly`, `quarterly`, `annual`, `ad_hoc` |
| id_family | text | e.g. `RES-xx`, `BCP-xx`, `AML-xx` (GAP-02 resolution) |
| status | enum | `active`, `retired` |

**`test_step_template`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| test_definition_id | uuid, FK | |
| sequence_order | integer | |
| instruction_text | text | |
| evidence_required | boolean | |
| min_sample_size | integer, nullable | |

**`sampling_methodology`** (SA-05)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| name | text | e.g. "Risk-based judgement sampling" |
| description | text | |
| guidance_notes | text | |
| status | enum | `active`, `retired` |

## 4.3 Regulatory Content Embeddings

**`regulatory_embedding_gen1`** *(generation-versioned — see Section 10 for why this isn't a single fixed table, and how a model/dimension swap creates `regulatory_embedding_gen2`, etc.)*
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| source_type | enum | `requirement`, `article`, `guidance` |
| source_id | uuid | |
| chunk_text | text | |
| embedding | vector(1536) | dimension fixed per generation; gen1 = `text-embedding-3-small` (1536-dim, ADR-006 default) |
| model_registry_id | uuid, FK → embedding_model_registry | |
| created_at | timestamptz | |

Application code queries the `regulatory_embedding_current` routing view (Section 10.3), never this table directly.

Index: HNSW index on `embedding` for approximate nearest-neighbor search (see Section 11).

## 4.4 AI Evaluation Golden Dataset (TAB v2.0 Section 10.2)

**`ai_eval_golden_case`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| wsp_sample_document_ref | text | pointer to reference S3 object |
| requirement_id | uuid, FK | ground-truth mapping |
| section_reference | text | expert-labeled section |
| labeled_by | uuid | reviewing expert |
| dataset_version | integer | versioned, per Section 10.2.5 |
| created_at | timestamptz | |

**`ai_eval_run`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| dataset_version | integer | |
| model_config_ref | text | prompt/model/embedding version under test |
| precision | numeric | |
| recall | numeric | |
| accuracy | numeric | |
| passed_gate | boolean | ≥85% per ADR-025 |
| run_at | timestamptz | |

## 4.5 Platform Audit Log

**`platform_audit_log`** (append-only, immutable — see Section 6)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| actor_id | uuid | Platform Super Admin user |
| action | text | e.g. `regulation.publish`, `tenant.provision`, `test_definition.update` |
| target_type | text | |
| target_id | uuid | |
| payload | jsonb | full before/after or action detail |
| occurred_at | timestamptz | |
| ip_address | inet | |

## 4.6 Firm Registry (Portal-visible metadata only)

**`firm_registry`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | matches the Firm's own id in its tenant schema |
| legal_name | text | |
| slug | text, unique | subdomain identifier (`{slug}.complianceiq.com`); generated at onboarding from legal_name with collision handling, immutable once assigned (see Backend Architecture §5) |
| jurisdiction | text | |
| service_lines | text[] | denormalized for Portal listing (SA-06) |
| last_active_at | timestamptz | |
| tenant_schema_name | text | |
| status | enum | `prospect`, `active`, `suspended`, `archived` |
| plan_tier | enum | `enterprise`, `seat_based` (CC-01) |
| seat_count | integer, nullable | |

`slug` has a unique index and is validated at onboarding (lowercase, alphanumeric + hyphen, reserved-word blocklist e.g. `admin`, `api`, `www`) before the Tenant Migration Runner (Section 8) proceeds — a slug collision or reserved word blocks provisioning rather than silently appending a suffix.

**Critical boundary:** this table intentionally excludes anything from Section 2 of the PRD (test results, findings, evidence, WSP content) — the Portal's `admin_portal_api` namespace can query this table freely but has no code path to any `tenant_<firm_uuid>` schema (TAB v2.0 Section 5.2).

---

# 5. Tenant Schema — Core Tables

*(one instance of this full set per firm, inside `tenant_<firm_uuid>`)*

## 5.1 Firm Profile & Identity

**`firm_profile`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | matches `firm_registry.id` |
| legal_name | text | |
| registered_address | text | |
| home_jurisdiction | text | |
| branch_jurisdictions | text[] | |
| licence_number | text | |
| licence_document_ref | text, nullable | S3 pointer |
| client_base | enum | `retail`, `institutional`, `both` |

**`platform_user`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| email | text, unique | |
| password_hash | text | |
| mfa_enrolled | boolean | |
| status | enum | `invited`, `active`, `disabled` |
| firm_role_id | uuid, FK → firm_role | |
| created_at | timestamptz | |

**`system_role`** (fixed, seeded, not editable by firms — the 8 roles in PRD Section 3.1)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| code | text, unique | e.g. `CCO`, `LEAD_TESTER`, `SENIOR_MGMT`, `REMEDIATION_OWNER`, `IT_ADMIN`, `FIRM_SUPER_ADMIN`, `STAFF_NO_LOGIN` |
| permissions | jsonb | |

**`firm_role`** (custom names, FR-09/FR-10)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| custom_name | text | e.g. "VP of Compliance" |
| system_role_id | uuid, FK | |
| active | boolean | |
| deactivated_at | timestamptz, nullable | |

**`service_line`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| dora_activity_code | text | A–H activity list, maintained centrally |
| derived_from_revenue_file | boolean | |
| confirmed_by_cco | boolean | |
| confirmed_at | timestamptz, nullable | |

## 5.2 Staff & Governance

**`staff_member`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| linked_user_id | uuid, FK → platform_user, nullable | null if no-login staff |
| name | text | |
| job_title | text | |
| department | text | |
| reports_to_id | uuid, FK → staff_member, nullable | org chart edge |
| alternate_work_location | text | |

**`staff_certification`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| staff_member_id | uuid, FK | |
| certification_name | text | |
| expiry_date | date | |

**`communication_channel_reference`** (per-firm, OS-02 resolution — TAB v2.0 Section 13)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| channel_name | text | firm-supplied via CSV |
| imported_at | timestamptz | |

**`staff_channel_assignment`**
| Column | Type | Notes |
|---|---|---|
| staff_member_id | uuid, FK | |
| channel_reference_id | uuid, FK | |
| flagged_mismatch | boolean | set on import validation failure |

**`staff_hardware`**, **`bcp_call_tree_link`** — straightforward FK tables to `staff_member`, omitted here for brevity; same pattern.

## 5.3 WSP Management

**`wsp`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| current_version_id | uuid, FK → wsp_version | |

**`wsp_version`** — immutable once superseded (FR-37)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| wsp_id | uuid, FK | |
| version_number | integer | |
| file_ref | text | S3 pointer |
| uploaded_at | timestamptz | |
| uploaded_by | uuid, FK | |

**`wsp_section`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| wsp_version_id | uuid, FK | |
| page_range | text | |
| extracted_text | text | |

**`wsp_content_embedding_gen1`** (per Section 2.4 — lives in tenant schema; generation-versioned per Section 10)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| wsp_section_id | uuid, FK | |
| embedding | vector(1536) | dimension fixed per generation, mirrors shared-schema convention |
| model_registry_id | uuid, FK → embedding_model_registry (shared schema) | |
| created_at | timestamptz | |

Application code queries the per-tenant `wsp_content_embedding_current` routing view, never this table directly.

**`ai_mapping`** (FR-31, FR-32, FR-33)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| wsp_section_id | uuid, FK | |
| requirement_id | uuid | references shared schema `requirement.id` (cross-schema logical FK, not enforceable by Postgres FK constraint across schemas — validated at application layer) |
| source | enum | `ai_suggested`, `manual_override` |
| confidence_score | numeric, nullable | |
| status | enum | `pending_review`, `confirmed`, `reversed` |
| approver_1_id | uuid, FK | two-person sign-off (FR-32) |
| approver_2_id | uuid, FK | must differ from author and from approver_1 |
| confirmed_at | timestamptz, nullable | |
| reversed_at | timestamptz, nullable | |
| reversal_reason | text, nullable | |

*Immutability trigger: once `status = 'confirmed'` or `'reversed'`, the row cannot be updated — a reversal creates a new row referencing the old one, per FR-33.*

## 5.4 Compliance Testing

**`test_schedule`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| test_definition_id | uuid | references shared schema |
| due_period_start | date | |
| due_period_end | date | |
| status | enum | `planned`, `ongoing`, `completed`, `not_applicable` |
| auto_generated | boolean | vs. manually created thematic/selective review (FR-17) |

**`test_execution`** — states per Domain Model: Draft → Assigned → In Progress → Review → Approved → Closed
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| test_schedule_id | uuid, FK | |
| lead_tester_id | uuid, FK → platform_user | |
| assigned_by | uuid, FK | must be CCO (FR-20) |
| assigned_at | timestamptz | |
| status | enum | see above |
| scope_description | text | partial testing scope (FR-19) |
| overall_result | enum, nullable | `pass`, `fail`, `observation`, `not_applicable` |
| na_reason | text, nullable | required if not_applicable (FR-21b) |
| cco_approved_at | timestamptz, nullable | |
| cco_approved_by | uuid, FK, nullable | |
| amended_from_id | uuid, FK → test_execution, nullable | amendment chain (FR-27) |

*Immutability trigger: blocks UPDATE once `cco_approved_at` is set, except for the amendment path, which always inserts a new row.*

**`test_execution_version`** — one row per contributor edit while in progress (GAP-05 resolution)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| test_execution_id | uuid, FK | |
| contributor_id | uuid, FK | |
| edited_at | timestamptz | |
| diff_snapshot | jsonb | |

**`sampling_record`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| test_execution_id | uuid, FK | |
| methodology_id | uuid | references shared schema `sampling_methodology.id` |
| population_size | integer | |
| sample_size | integer | |
| selection_rationale | text | |
| locked_at | timestamptz | |
| changed_at | timestamptz, nullable | requires senior approval (FR-21c) |
| change_approved_by | uuid, FK, nullable | |
| change_reason | text, nullable | |

*Original selection is never overwritten — a change writes new values into a linked `sampling_record_amendment` row, preserving the original per FR-21c.*

**`evidence`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| test_execution_id | uuid, FK, nullable | |
| remediation_milestone_id | uuid, FK, nullable | evidence can attach to either |
| file_ref | text | S3 pointer, per-tenant encryption key (NFR-02) |
| file_type | enum | pdf, docx, xlsx, png, jpg, mp3, wav, mp4, mov, avi, zip, csv |
| uploaded_by | uuid, FK | |
| uploaded_at | timestamptz | |
| valid_until | date, nullable | shelf-life tracking (FR-28) |

*No delete permitted at application or database level — table has no DELETE grant for any application role.*

## 5.5 Findings & Remediation

**`finding`** — states: Open → In Remediation → Under Review → Closed
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| test_execution_id | uuid, FK | |
| requirement_id | uuid | references shared schema |
| regulation_article_ref | text | |
| severity | enum | `high`, `moderate`, `low` — auto-calculated (FR-38 agreed list) |
| root_cause_category | enum | `process_gap`, `control_failure`, `missing_documentation`, `system_issue`, `training_gap` |
| description | text | |
| recorded_by | uuid, FK | |
| status | enum | see above |
| is_repeat_finding | boolean | computed against prior period (FR-46) |
| closed_at | timestamptz, nullable | |
| closed_by_cco | uuid, FK, nullable | |
| closed_by_senior_mgmt | uuid, FK, nullable | must differ from `recorded_by` (FR-45) |

*Immutability trigger: blocks UPDATE once `status = 'closed'`.*

**`remediation_plan`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| finding_id | uuid, FK | |
| description | text | |

**`remediation_milestone`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| remediation_plan_id | uuid, FK | |
| owner_id | uuid, FK → platform_user | must be registered user |
| due_date | date | |
| status | enum | `pending`, `completed`, `overdue`, `reassigned` |
| completed_at | timestamptz, nullable | |
| extension_granted_by | uuid, FK, nullable | CCO or one other Senior role (GAP-08) |
| extension_reason | text, nullable | forced field |
| reassignment_reason | text, nullable | |

**Note on visibility (per confirmed decision):** `remediation_milestone` queries scoped to a Remediation Owner filter `WHERE owner_id = current_user_id` at the application/query layer — this table does not need a separate visibility-control column since access is enforced by the query predicate itself.

## 5.6 Reports

**`report`** — immutable after publication (FR-61)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| testing_period_start | date | |
| testing_period_end | date | |
| status | enum | `draft`, `pending_signoff`, `published` |
| generated_at | timestamptz | |
| generated_by | uuid, FK | |
| aml_officer_agreed_at | timestamptz, nullable | gate per FR-55 |
| senior_mgmt_signoff_at | timestamptz, nullable | |
| senior_mgmt_signoff_by | uuid, FK, nullable | |
| report_data_snapshot | jsonb | the structured Report Data Model (TAB v2.0 Section 11.1) — frozen at generation time so PDF/Word/Excel renders are always reproducible even if underlying rows later get amendments |
| pdf_ref | text, nullable | |
| docx_ref | text, nullable | |
| xlsx_ref | text, nullable | |

*Immutability trigger: blocks UPDATE once `status = 'published'`.*

## 5.7 Notifications & Distribution

**`notification`**, **`notification_preference`**, **`distribution_list`**, **`distribution_list_member`** — standard tables; distribution lists seeded with the six fixed list types from PRD Section 10.6 (`compliance_testing_reports`, `regulatory_org_responses`, `regulatory_org_requests`, `remediation_deadlines`, `new_rules_guidance`, `critical_system_alerts`).

## 5.8 IT Systems & Risk

**`it_system`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| name | text | |
| category | text | extensible list |
| classification | enum | `critical`, `important`, `other` — not nullable (FR-72 enforced) |

**`it_vendor`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| vendor_name | text | |
| service_type | text | |
| contract_reference | text | |
| dora_tier | enum | `CIF`, `CTPP` (FR-73) |
| contract_review_due | date | |

**`monitoring_data_upload`** (Section 12, TAB v2.0 — CSV ingestion only, no PII)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| uploaded_at | timestamptz | |
| period | text | |
| aggregated_counts | jsonb | e.g. `{"level_1_alerts": 42, "level_2_alerts": 5}` |
| source_vendor | text | |

**`it_incident`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| is_major | boolean | via guided checklist (FR-75) |
| notification_clock_started_at | timestamptz, nullable | |
| notification_submitted_at | timestamptz, nullable | |
| draft_notification_text | text, nullable | |

## 5.9 Tenant Audit Log

**`tenant_audit_log`** (append-only, immutable, no delete grant — NFR-04)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| actor_id | uuid, FK → platform_user | |
| action | text | e.g. `finding.close`, `test_execution.approve`, `report.publish` |
| target_type | text | |
| target_id | uuid | |
| payload | jsonb | |
| occurred_at | timestamptz | |
| ip_address | inet | |
| device_fingerprint | text | FR-13 "from which device" |

---

# 6. Versioning & Immutability Pattern (Applied Consistently)

Every versioned entity (Regulation Version, Requirement, WSP Version, Report, Prompt Template, Embedding — per Domain Model Section 8) follows the same shape:

1. **Insert-only history.** A new version is always a new row; the old row is never updated to reflect new content.
2. **A `current_version_id` pointer** on the parent entity (e.g., `wsp.current_version_id`) is the only mutable field — updating "what's current" never touches historical rows.
3. **A terminal status field** (`published`, `closed`, `confirmed`, etc.) that, once set, is enforced immutable by a PostgreSQL trigger:

```sql
CREATE OR REPLACE FUNCTION prevent_modification_after_terminal_status()
RETURNS TRIGGER AS $$
BEGIN
  IF OLD.status IN ('published', 'closed', 'confirmed', 'reversed') THEN
    RAISE EXCEPTION 'Row % is immutable (status=%): direct modification not permitted', OLD.id, OLD.status;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

Applied via `BEFORE UPDATE OR DELETE` triggers on: `regulation_version`, `requirement` (retirement path), `wsp_version`, `ai_mapping`, `test_execution`, `finding`, `report`, and both audit log tables (which have no terminal-status concept — they simply never allow UPDATE/DELETE at all, enforced by revoking those grants outright from the application database role).

This gives NFR-04/NFR-07 compliance that survives even a misconfigured application permission, not just a correctly-configured one.

---

# 7. Retention & Deletion Policy

- **Minimum retention: 6 years** for test executions, results, evidence, findings, remediation records, reports, audit logs, notification logs (NFR-07).
- **No hard delete** is implemented for any of these tables — there is no application code path or database grant that permits `DELETE`.
- A `retention_review_flag` (boolean, default false) is available on tenant-level tables for a future archival tier (e.g., moving cold data older than the retention window to cheaper storage) — but this is a storage-tiering concern, not a deletion concern, and is out of scope for Phase 1 build.
- Firm profile data (non-regulatory-evidence data) is retained "for as long as the firm is a client" — on account closure, the tenant schema is archived (not dropped) rather than deleted, consistent with the 6-year evidentiary requirement potentially outliving the commercial relationship.

---

# 8. Tenant Provisioning

**Trigger:** Firm lifecycle transition `Prospect → Active` (Domain Model Section 4).

**Process (Tenant Migration Runner, Celery task, per ADR-018):**

1. Generate and validate the firm's **slug** (subdomain identifier — Section 4.6) against the uniqueness/reserved-word rules; abort provisioning on collision rather than auto-suffixing.
2. Generate `tenant_<firm_uuid>` schema name.
3. Create the PostgreSQL schema.
4. Run the full tenant migration set against it (every table in Section 5).
5. Register the schema name, slug, and current migration version in the shared-schema `tenant_schema_registry` table.
6. Seed the eight `system_role` mappings' defaults are already global (shared schema); no per-tenant seeding needed there.
7. Seed the six default `distribution_list` entries.
8. Emit a `FirmCreated` domain event (via the outbox pattern, TAB v2.0 Section 4a.1) to trigger downstream welcome notifications.

**Ongoing migrations:** when a new backend release includes a schema change, the Tenant Migration Runner applies it to every registered tenant schema in sequence, tracked per-tenant in `tenant_schema_registry.migration_version`, so a partially-failed rollout is visible and resumable per tenant rather than all-or-nothing.

---

# 9. Cross-Schema Reference Handling

Several tenant-schema tables reference shared-schema rows (e.g., `finding.requirement_id` → shared `requirement.id`). PostgreSQL cannot enforce a foreign key constraint across schemas in different logical namespaces in a way that's practical here (tenant schemas are created dynamically), so these references are:

- Validated at the **application/service layer** on write (confirm the referenced shared-schema row exists and is `active` before allowing the insert).
- Never validated by a database-level FK constraint.
- Protected from dangling references by the fact that shared-schema reference rows (Requirement, Test Definition, Sampling Methodology) are **never hard-deleted**, only retired — so a historical reference from any tenant schema always resolves, even to a retired requirement.

---

# 10. Vector / Embedding Storage Design

## 10.1 The Dimension Problem

pgvector's `vector(N)` column type fixes its dimension `N` at table-creation time. A `provider`/`model`/`embedding_version` metadata column (as in v1.0 of this section) is sufficient to distinguish *same-dimension* model changes (e.g., a minor model revision), but is **not sufficient** for a real model swap where the new model outputs a different vector size (e.g., 1536 → 3072, or switching provider families entirely). Inserting a 3072-dim vector into a `vector(1536)` column fails outright — this is a hard type constraint, not a data-quality issue. The design below fixes this properly rather than papering over it with metadata.

## 10.2 Embedding Model Registry (shared schema)

**`embedding_model_registry`**
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| provider | text | e.g. `openai`, `bedrock`, `anthropic` |
| model_name | text | e.g. `text-embedding-3-small` |
| dimensions | integer | fixes which physical table generation this model writes to |
| generation | integer | monotonically increasing; determines table suffix (Section 10.3) |
| status | enum | `active`, `backfilling`, `deprecated` |
| activated_at | timestamptz | |
| deprecated_at | timestamptz, nullable | |

Only one `provider`/`model_name` combination may have `status = 'active'` at a time per embedding class (`regulatory` or `wsp_content`) — enforced by a partial unique index.

## 10.3 Versioned Physical Tables (Dimension-Safe)

Rather than one fixed-dimension column trying to serve every future model, embedding storage is **physically versioned by generation**:

- `regulatory_embedding_gen1`, `regulatory_embedding_gen2`, ... (shared schema)
- `wsp_content_embedding_gen1`, `wsp_content_embedding_gen2`, ... (tenant schema)

Each generation table has its own `vector(N)` column sized correctly for that generation's model — created automatically (via migration) the first time `embedding_model_registry` registers a new `generation` with a different `dimensions` value. Table structure otherwise matches Section 4.3/5.3 (chunk reference, provider, model, created_at).

A thin **routing view** (`regulatory_embedding_current`, `wsp_content_embedding_current`) always points at whichever generation table is currently `active` in the registry, so application code queries the view and never needs to know the physical table name or dimension directly.

## 10.4 Migration Procedure (Model Swap, Including Dimension Change)

1. Register the new model in `embedding_model_registry` with `status = 'backfilling'` and its correct `generation`/`dimensions`.
2. If `dimensions` differs from the current active generation, migrate-create the new `..._genN` table with the correct `vector(N)` column (schema-only change, no data movement yet).
3. Backfill: an asynchronous Celery job re-embeds all source content (Requirement/Article text, or WSP sections) into the new generation table. The old generation table remains fully queryable and `active` throughout — search continues to work uninterrupted on the outgoing model.
4. Once backfill completes and a spot-check confirms coverage, flip `embedding_model_registry.status` — new model to `active`, old model to `deprecated` — which atomically repoints the routing view.
5. The deprecated generation table is retained for a defined grace period (e.g., 30 days) in case of rollback, then dropped. This is safe to actually delete (unlike Evidence or Audit Logs, Section 7) because embeddings are **derived** data — the source Requirement/Article/WSP text they were generated from is retained under its own retention rules regardless.

This gives a genuinely dimension-safe, zero-downtime path for switching embedding providers or models — not just a metadata tag on a column that would break on the first real swap.

---

# 11. Indexing Strategy

| Table class | Index type | Purpose |
|---|---|---|
| All FK columns | B-tree | Standard join performance |
| `*_embedding.embedding` | HNSW (pgvector) | Approximate nearest-neighbor semantic search; HNSW chosen over IVFFlat for better recall at the platform's expected scale (~100 firms, moderate per-tenant document volume) without requiring a separate training/build step per tenant |
| `wsp_section.extracted_text`, `article.text_content` | GIN (PostgreSQL Full Text Search, `tsvector`) | Keyword search (ADR-005/ADR-008) |
| `*_audit_log.occurred_at`, `*_audit_log.actor_id` | B-tree, composite | Audit log queries are near-always time-range + actor filtered |
| `test_execution.status`, `finding.status` | B-tree | Dashboard filtering (FR-49) |

---

# 12. Backup & Disaster Recovery

- Continuous WAL archiving + daily full snapshots, all within EU-resident infrastructure (TI-01).
- Point-in-time recovery window aligned to the 6-year retention requirement is impractical to hold as live WAL — instead, daily snapshots are retained per a standard operational window (e.g., 35 days), while the actual 6-year regulatory retention guarantee is satisfied by the database rows themselves being non-deletable (Section 7), not by backup retention. Backups protect against infrastructure failure; the immutability design protects against data loss/tampering — these are deliberately two different mechanisms for two different risks.
- Tenant schema isolation means a restore can, if ever needed, be scoped to a single tenant's schema without affecting others.

---

# 13. Open Items Carried Forward

| Item | Status |
|---|---|
| Final embedding dimension/provider selection | Configurable per ADR-006; default assumed 1536 (`text-embedding-3-small`) |
| Archival/cold-storage tiering for data past active use but within the 6-year window | Not in Phase 1 scope; `retention_review_flag` reserved for future use |
| Exact CSV field template for `monitoring_data_upload` | Pending Sosinna's vendor sample reports (SumSub, Veritas) — schema above is representative, not final |
| Non-EU rule set ingestion (future) | Schema designed to allow a `jurisdiction_scope` extension on `requirement` later without a breaking migration, but not built now (per TAB v2.0 Section 20) |

---

# 14. Version History

| Version | Date | Notes |
|---------|------|------|
| 1.0 | Jul 2026 | Initial Database Architecture, built against TAB v2.0 and Domain Model v1.0. |
| 1.1 | Jul 2026 | Fixed embedding model-swap gap: replaced single fixed-dimension embedding tables with a generation-versioned pattern (`embedding_model_registry` + `..._genN` tables + routing views) to properly support switching embedding providers/models with different vector dimensions, not just same-dimension version bumps. |
| 1.2 | Jul 2026 | Added `slug` column to `firm_registry` and a slug-validation step to Tenant Provisioning, supporting the subdomain-per-tenant routing decision made in Backend Architecture v1.1. |
