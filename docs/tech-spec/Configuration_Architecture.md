# ComplianceIQ – Configuration Architecture

**Version:** 1.0
**Status:** Baseline
**Depends On:** Technical Architecture Baseline (TAB) v2.0, Database Architecture v1.2, Backend Architecture v1.1, AI & Document Intelligence v1.1
**Audience:** All Engineering, DevOps, Platform Administration

> This document defines how configuration itself works across ComplianceIQ — the one architectural concern that was previously scattered across AI, Backend, Infrastructure, Security, and Database documents without a shared model. It fixes where configuration lives, who can change what, how changes are versioned and rolled back, how changes propagate, and how they're audited.

---

# 1. Purpose

Prior documents each introduced configuration-like concepts independently: `embedding_model_registry` and `prompt_template` (AI & Document Intelligence), the `AnchorStrategy` interface (Backend Architecture), environment variables (Infrastructure & DevOps), MFA/password policy values (Security Architecture). Each is internally consistent, but nothing ties them together — which means the next configuration need (a report branding setting, a notification digest frequency, a rate-limit threshold) would get built as a sixth, slightly different pattern by whichever engineer picks it up first. This document fixes that by defining **one governance model** that every configuration concern in the platform follows, and retrofits the existing ones onto it by reference.

---

# 2. Configuration Taxonomy

| Type | Definition | Storage | Runtime Editable? |
|---|---|---|---|
| **System Configuration** | Platform-wide defaults (e.g., AI confidence threshold default, password minimum length) | Shared schema (`config_definition`/`config_value_version`) | Yes — Platform Super Admin only |
| **Tenant Configuration** | Per-firm overrides of a system default, where explicitly permitted | Shared schema, scoped by `tenant_id` | Yes — Firm Super Admin, only for definitions marked `tenant_override_allowed` |
| **Environment Configuration** | Infrastructure-level values (DB connection strings, AI provider API keys, region allowlists) | AWS Secrets Manager / Terraform variables / ECS task definition env vars (Infrastructure & DevOps §10.2) | **No** — deployment-time only, requires a new deployment |
| **Feature Flags** | Gradual/targeted rollout of new functionality | Same `config_definition`/`config_value_version` tables, `type = feature_flag` (Section 6) | Yes — Platform Super Admin |
| **AI Configuration** | Prompt/model/embedding versions, confidence thresholds | Existing `prompt_template`, `embedding_model_registry`, `model_config` (AI & Document Intelligence §7) — governed by *this* document's versioning/audit pattern, tables unchanged | Yes — Platform Super Admin, subject to the AI evaluation gate |
| **Workflow Configuration** | State machine transition rules | **Not runtime configurable in Phase 1** — see Section 7 | No (by design) |
| **Report Configuration** | Template versions, per-tenant branding overrides | `config_definition`/`config_value_version`, `scope = tenant`, `category = reporting` | Yes — tenant branding fields only; template structure itself is code-defined |
| **Notification Configuration** | Rule thresholds (e.g., reminder lead time), digest frequency | Same governed tables; the notification *rule engine* itself is defined in the Notification Architecture document | Yes — where marked tenant-editable |
| **Scheduled Jobs** | Recurring background job definitions | `scheduled_job_registry` (Section 8) | Enable/disable only — schedule expressions are code-reviewed changes |

---

# 3. Governance Model

## 3.1 Core Tables (shared schema)

**`config_definition`** — the catalog itself (Section 9)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| key | text, unique | dotted namespace, e.g. `ai.confidence_threshold`, `notification.reminder_lead_days` |
| value_type | enum | `float`, `int`, `bool`, `string`, `json`, `feature_flag` |
| default_value | jsonb | |
| scope | enum | `system`, `tenant`, `environment` |
| tenant_override_allowed | boolean | only meaningful when `scope = system` |
| validation_schema | jsonb | JSON Schema — a proposed value must validate before it can move from `draft` to `active` |
| category | text | `ai`, `workflow`, `reporting`, `notification`, `scheduling`, `security`, `general` |
| restart_required | boolean | true only for values consumed at process startup rather than read live |
| description | text | |

**`config_value_version`** — versioned actual values
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| config_definition_id | uuid, FK | |
| tenant_id | uuid, nullable | null for system-scoped values |
| value | jsonb | |
| version | integer | |
| status | enum | `draft`, `active`, `superseded` |
| changed_by | uuid, FK | |
| changed_at | timestamptz | |
| rollback_of | uuid, FK → config_value_version, nullable | set when this version is a rollback to a prior value, not a forward change |

Only one `(config_definition_id, tenant_id)` pair may have `status = 'active'` at a time — enforced by a partial unique index, the same convention already used for `embedding_model_registry` and `prompt_template`.

## 3.2 Change Lifecycle

1. **Propose:** a new `config_value_version` row is inserted with `status = 'draft'`.
2. **Validate:** the proposed `value` is checked against `validation_schema`. Invalid values are rejected before ever reaching `active`.
3. **Activate:** on approval, the new version's status flips to `active`; the previously active version (if any) flips to `superseded` — atomic, single transaction.
4. **Propagate:** activation emits a `ConfigurationChanged` domain event via the outbox (Backend Architecture §6). Subscribers (primarily a Redis-backed config cache, Section 5) invalidate/refresh on receipt — no service ever polls the database directly for a hot-path config read.
5. **Audit:** every activation is written to the Platform Audit Log (Database Architecture §4.5) with actor, old value, new value, and timestamp — configuration changes are exactly the kind of "who changed what and when" question that shows up in a client or regulator conversation.
6. **Rollback:** reactivating a `superseded` version creates a **new** version row (`rollback_of` pointing at the version being restored) rather than mutating history — consistent with the platform-wide insert-only versioning pattern (Database Architecture §6). A rollback is itself a change, auditable the same way.

## 3.3 Who Can Change What

| Config Type | Who |
|---|---|
| System Configuration | Platform Super Admin only |
| Tenant Configuration (override) | Firm Super Admin, for definitions marked `tenant_override_allowed` |
| Feature Flags | Platform Super Admin |
| AI Configuration | Platform Super Admin, gated by the AI evaluation harness (AI & Document Intelligence §9) — a config change here isn't just a value swap, it re-triggers the accuracy gate |
| Environment Configuration | Not runtime-editable by anyone — requires a Terraform PR and deployment (Infrastructure & DevOps §10) |

---

# 4. Django Access Pattern

A single `config.get(key, tenant_id=None)` service function is the **only** sanctioned way any application code reads a configuration value — no module reads `config_value_version` directly via the ORM, and no module hardcodes a value that belongs in this system. Resolution order: tenant override (if `tenant_override_allowed` and a tenant-scoped active version exists) → system default. This mirrors the same "one shared service, not five ad hoc reads" philosophy already applied to the dual-control pattern (Backend Architecture §8).

---

# 5. Caching & Propagation

Configuration values are read far more often than they change, so they're cached in Redis (already provisioned per TAB v2.0/Infrastructure & DevOps §5) with the `ConfigurationChanged` outbox event as the invalidation signal — not a TTL-based expiry, which would allow a stale value to linger for up to the TTL window after an intentional change. A config change is expected to take effect within one outbox poll cycle (2–5 seconds, Backend Architecture §6.2) across all running instances, without a restart, **except** for values marked `restart_required = true` (Section 3.1), which are deliberately excluded from live propagation because they're consumed at process bootstrap (e.g., a connection pool size).

---

# 6. Feature Flags

Feature flags reuse the same `config_definition`/`config_value_version` tables (`value_type = feature_flag`), with the `value` JSON carrying:

```json
{ "enabled": true, "rollout_percentage": 25, "tenant_allowlist": ["uuid1", "uuid2"] }
```

- **Global flags:** `scope = system`, no tenant targeting.
- **Percentage rollout:** deterministic hashing of `tenant_id` (or `user_id` for finer-grained flags) against `rollout_percentage`, so a given tenant's flag state is stable across requests rather than flipping randomly.
- **Explicit allowlist:** for controlled early access (e.g., a specific pilot firm testing a new report format ahead of general availability).

Flags follow the same audit/versioning/rollback lifecycle as any other configuration — a flag flip is not a special, unaudited code path.

---

# 7. Workflow Configuration — Explicit Boundary Statement

**Decision (reaffirmed from Backend Architecture §7): state machine transitions are code-defined in Phase 1, not tenant-configurable.** The PRD does not currently confirm workflow customization (e.g., a client wanting a custom Finding lifecycle with an added review stage) as a roadmap commitment, and building a general-purpose configurable workflow engine against a hypothetical requirement would be speculative over-engineering.

**What this document adds that Backend Architecture didn't:** an explicit extension point. If workflow customization is confirmed on the roadmap in the future, the transition table already lives in a single, well-isolated location per entity (`TEST_EXECUTION_TRANSITIONS`, etc., Backend Architecture §7.1) — migrating that from a Python dict to a `config_definition`-governed, versioned, tenant-scoped table is a bounded, well-understood piece of work, not a rewrite. This section exists so that if/when that day comes, nobody has to first figure out where the boundary is — it's here.

---

# 8. Scheduled Jobs Registry

**`scheduled_job_registry`** (shared schema)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| job_key | text, unique | e.g. `quarterly_test_generation`, `regulatory_monitoring_poll` |
| schedule_expression | text | cron syntax |
| queue | text | maps to a Celery queue (Backend Architecture §11) |
| enabled | boolean | toggle only — the schedule expression itself is a code-reviewed change, not runtime-editable |
| owner_module | text | which Django app owns this job, for on-call routing |
| last_run_at | timestamptz, nullable | |
| next_run_at | timestamptz, nullable | |

**Rationale:** recurring jobs (test scheduling recomputation, AI evaluation triggers, regulatory monitoring polls, reminder emails, evidence expiry checks, SLA monitoring) currently exist scattered across Celery Beat configuration in each owning app. Centralizing them in one registry table — even though the *schedule itself* stays code-defined — gives operations a single place to see "everything that runs on a timer," which matters for on-call diagnosis ("is the reminder job even scheduled to run?") without grepping through five apps' `celery.py` configs.

This is deliberately lighter-weight than a full Scheduling Architecture document: it's a visibility/registry mechanism, not a new execution engine — the actual execution still goes through the existing Celery/outbox infrastructure (Backend Architecture §6, §11).

---

# 9. Configuration Catalog (Representative)

This is not exhaustive — it's seeded with the values already implied by prior documents, and grows as an appendix maintained alongside each new config need, per the Definition of Done (Engineering Standards §12).

| Key | Type | Default | Scope | Tenant Override | Versioned | Restart Required | Source |
|---|---|---|---|---|---|---|---|
| `ai.confidence_threshold` | float | 0.40 | System | Yes | Yes | No | AI & Document Intelligence §5.3 |
| `ai.evaluation_gate_threshold` | float | 0.85 | System | No | Yes | No | ADR-025 |
| `security.password_min_length` | int | 12 | System | No | Yes | No | Security Architecture §3.1 |
| `security.mfa_backup_code_count` | int | 10 | System | No | Yes | No | Security Architecture §3.2 |
| `evidence.max_file_size_mb` | int | 500 | System | Yes | Yes | No | PRD FR-24 (implementation detail) |
| `regulatory_monitoring.poll_interval_minutes` | int | 60 | System | No | Yes | No | TAB v2.0 §9 |
| `notification.reminder_lead_days` | int | 5 | System | Yes | Yes | No | Notification Architecture §5 |
| `notification.digest_frequency` | enum | `immediate` | Tenant | Yes | Yes | No | Notification Architecture §6 |
| `reporting.default_branding_logo_url` | string | null | Tenant | Yes | Yes | No | TAB v2.0 §11 |
| `sampling.default_methodology_id` | uuid | (seeded value) | System | Yes | Yes | No | PRD SA-05 |
| `outbox.poll_interval_seconds` | int | 3 | Environment | No | No | Yes | Backend Architecture §6.2 |
| `api.rate_limit_per_minute` | int | 120 | System | No | Yes | No | Security Architecture §8 |

---

# 10. Open Items Carried Forward

| Item | Status |
|---|---|
| Full report-branding field set (logo, color scheme, footer text) | To be finalized alongside the Reporting section of a future Localization Architecture pass |
| Whether any config category needs a client-facing self-service UI (vs. Platform Admin-only) | Product decision, not an architectural blocker — the governance model supports either |
| Workflow configurability roadmap confirmation | Tracked here (Section 7) pending product/contract confirmation |

---

# 11. Version History

| Version | Date | Notes |
|---------|------|------|
| 1.0 | Jul 2026 | Initial Configuration Architecture: unified taxonomy across System/Tenant/Environment/Feature Flag/AI/Workflow/Report/Notification/Scheduling configuration; versioned governance model with rollback and audit; Redis propagation via the outbox pattern; explicit workflow-configuration boundary statement; Scheduled Jobs Registry; representative configuration catalog. |
