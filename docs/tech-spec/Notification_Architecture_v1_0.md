# ComplianceIQ – Notification Architecture

**Version:** 1.0
**Status:** Baseline
**Depends On:** Technical Architecture Baseline (TAB) v2.0, Database Architecture v1.2, Backend Architecture v1.1, Configuration Architecture v1.0
**Audience:** Backend Engineers, Architects, QA

> This document defines the orchestration layer between a domain event and a delivered notification — the piece prior documents left implicit. Database Architecture defines the notification tables; Backend Architecture defines the outbox event mechanism that triggers notifications; this document defines the Domain Event → Notification Rule → Channel Selection → Delivery pipeline that connects them.

---

# 1. Purpose

`notification`, `notification_preference`, `distribution_list`, and `distribution_list_member` (Database Architecture §5.7) describe *what a notification looks like once it exists*. Nothing previously defined *how a domain event becomes a notification* — which events trigger which notifications, how the audience is resolved, how channel selection works, or how delivery failure is handled. Given the PRD ties several regulatory-timeliness obligations to notifications (deadline reminders, critical system alerts, remediation escalations), this is a real gap, not a cosmetic one — a client could reasonably ask "prove this person was notified," and the architecture needs to support that answer.

---

# 2. Pipeline Overview

```
Domain Event (outbox, Backend Architecture §6)
        │
        ▼
Notification Rule Match (event_type → rule lookup)
        │
        ▼
Audience Resolution (who gets notified)
        │
        ▼
Template Rendering (content, localized)
        │
        ▼
Channel Selection (per-recipient preference × rule-mandated channels)
        │
        ▼
Delivery (Email today; In-App today; SMS/Teams future — Section 7)
        │
        ▼
Delivery Record + Audit
```

---

# 3. Notification Rule Table

**`notification_rule`** (shared schema — rules are platform-defined; tenant-editable thresholds live in Configuration Architecture, not here)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| event_type | text | matches an outbox `event_type` (Backend Architecture §6.1), e.g. `FindingCreated`, `RemediationDeadlineApproaching`, `RegulatoryUpdateDetected`, `ReportPublished`, `MajorITIncidentDetected` |
| audience_resolver | text | identifies which resolution strategy to use (Section 4) |
| distribution_list_type | text, nullable | one of the six fixed types (Database Architecture §5.7) when audience is list-based |
| mandatory_channels | text[] | channels that cannot be opted out of for this rule (e.g., `critical_system_alerts` is never email-optional) |
| optional_channels | text[] | channels subject to per-user preference |
| template_key | text | resolves to a versioned template (Section 6) |
| is_digestible | boolean | whether this notification type can be batched into a digest (Section 6.3) or must always be immediate |

Not every domain event has a notification rule — most (e.g., routine `TestAssigned`) do; some outbox events exist purely for audit/re-indexing purposes and have no corresponding rule. The absence of a matching rule is a normal, silent no-op, not an error.

---

# 4. Audience Resolution

Three resolution strategies, selected per rule via `audience_resolver`:

1. **Distribution-list-based:** resolves to every member of the matching `distribution_list` (the six fixed types — Database Architecture §5.7). Used for regulatory-content and reporting-type notifications where the audience is a standing group, not derived from the triggering entity.
2. **Role-based, derived from the event:** e.g., `FindingCreated` notifies the CCO role for that firm, regardless of which specific person holds it today. Resolves via the tenant's `firm_role`/`system_role` mapping (Database Architecture §5.1) at delivery time, not at rule-definition time — so a role reassignment automatically redirects future notifications without a rule change.
3. **Entity-owner-based:** e.g., `RemediationDeadlineApproaching` notifies the specific `remediation_milestone.owner_id` — resolved directly from the triggering entity's own foreign key, not a role or list lookup.

A single event can match multiple rules with different resolvers (e.g., `FindingCreated` might notify both the assigned CCO *and* the `compliance_testing_reports` distribution list) — rules are independent, not mutually exclusive.

---

# 5. Configuration-Governed Thresholds

Several notification behaviors are genuinely tenant-tunable and therefore live in Configuration Architecture (not hardcoded in `notification_rule`), per that document's taxonomy:

- `notification.reminder_lead_days` (default 5) — how far ahead of a remediation deadline the first reminder fires.
- `notification.escalation_lead_days` — a second, more urgent reminder threshold as a deadline nears, potentially notifying a role above the original owner.
- `notification.digest_frequency` (default `immediate`, tenant-overridable to `daily`/`weekly` for non-critical categories).

The `notification_rule` table references these by key rather than embedding a literal number, so a threshold change is a Configuration Architecture change (versioned, audited, live-propagated — Configuration Architecture §3, §5), not a code deployment.

---

# 6. Template Rendering

## 6.1 Template Registry

Mirrors the `prompt_template`/`embedding_model_registry` governance pattern (AI & Document Intelligence §7.1, Configuration Architecture §3):

**`notification_template`** (shared schema)
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| template_key | text | referenced by `notification_rule.template_key` |
| locale | text | `en`, `de`, `fr` — content is localized (ties to the forthcoming Localization Architecture); Requirement IDs embedded in a notification body remain language-independent per Domain Model §10 |
| channel | enum | `email`, `in_app` (extensible — Section 7) |
| subject_template | text, nullable | email only |
| body_template | text | Jinja2-style, variable slots (e.g., `{{ finding.requirement_code }}`, `{{ deadline_date }}`) |
| version | integer | |
| status | enum | `draft`, `active`, `deprecated` |

Only one `(template_key, locale, channel)` combination may be `active` at a time.

## 6.2 Rendering

At delivery time, the resolved recipient's locale preference (`platform_user` — a locale field, extending the schema minimally) selects which `notification_template` row to render against. A missing locale-specific template falls back to `en` rather than failing delivery outright.

## 6.3 Digesting

For rules marked `is_digestible = true` and a recipient whose `notification.digest_frequency` resolves to non-immediate, individual notification instances are queued into a per-recipient digest buffer and rendered as a single batched digest template on the configured cadence, rather than delivered one at a time. **Mandatory-channel, non-digestible notifications (critical system alerts, regulatory deadlines) are never batched, regardless of preference** — this is enforced by `notification_rule.is_digestible = false` for those rule rows, not left to user preference to accidentally suppress.

---

# 7. Channel Abstraction

A single `NotificationChannel` interface, mirroring the AI provider abstraction philosophy (ADR-007/009, AI & Document Intelligence §6.1) — **no module sends a notification directly to a delivery mechanism**; every send goes through this interface:

```python
class NotificationChannel(Protocol):
    def send(self, recipient, rendered_content) -> DeliveryResult: ...
```

- **Phase 1 implementations:** `EmailChannel` (via a transactional email provider), `InAppChannel` (writes to the `notification` table, Database Architecture §5.7, surfaced in the platform UI).
- **Future extension points (not built now):** `SMSChannel`, `TeamsChannel` — adding either is a new implementation of the same interface, not a redesign, consistent with how ADR-007's provider abstraction was designed to absorb new AI providers without touching calling code.

---

# 8. Delivery, Retry, and Failure Handling

- Delivery runs on the `notifications` Celery queue (Backend Architecture §11), isolated from other background work.
- Standard transient failures (e.g., email provider timeout) retry with exponential backoff, consistent with the platform's general Celery retry policy (Backend Architecture §11).
- **Mandatory-channel notifications that exhaust retries escalate**, rather than silently failing: a failed `critical_system_alerts` delivery, after retry exhaustion, triggers a fallback attempt via the recipient's alternate channel (if configured) and, failing that, raises an internal alert to on-call (Infrastructure & DevOps §12) — a notification that's supposed to be guaranteed shouldn't be able to just quietly disappear.
- Every delivery attempt (success or failure) is recorded — this is what lets the platform answer "was this person notified, and when" for a regulatory-deadline or critical-alert dispute, tying back to the same evidentiary posture the rest of the system maintains for compliance records.

---

# 9. Relationship to Distribution Lists (Recap)

The six fixed distribution list types (Database Architecture §5.7 — `compliance_testing_reports`, `regulatory_org_responses`, `regulatory_org_requests`, `remediation_deadlines`, `new_rules_guidance`, `critical_system_alerts`) map directly to `notification_rule.distribution_list_type` for list-based audience resolution (Section 4, strategy 1). This document doesn't change that table structure — it defines how those lists actually get used by the event pipeline, which was previously undefined.

---

# 10. Open Items Carried Forward

| Item | Status |
|---|---|
| Full `event_type` → `notification_rule` mapping table (every PRD notification requirement enumerated) | To be populated as an implementation-phase artifact, following the pattern established here — not exhaustively listed in this baseline document |
| `platform_user.locale` field addition | Minor schema addition, tracked here pending Localization Architecture |
| SMS/Teams channel implementation | Explicit future extension point (Section 7), not Phase 1 scope |
| Escalation-to-alternate-channel logic detail for mandatory notifications (Section 8) | Implementation-phase detail; the requirement (never silently fail) is fixed here, the exact escalation path is not |

---

# 11. Version History

| Version | Date | Notes |
|---------|------|------|
| 1.0 | Jul 2026 | Initial Notification Architecture: Domain Event → Rule → Audience → Template → Channel → Delivery pipeline; three audience resolution strategies; configuration-governed thresholds tying to Configuration Architecture; versioned/localized template registry with digest support; channel abstraction interface with SMS/Teams as defined future extension points; mandatory-channel delivery guarantees with escalation on retry exhaustion. |
