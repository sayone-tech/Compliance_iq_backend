# ComplianceIQ – Cross-Document Traceability Matrix

**Version:** 1.0
**Status:** Living Document — extended incrementally, not a one-time deliverable
**Depends On:** All prior technical specification documents
**Audience:** All Engineering, QA, Architects, Product

> This document maps PRD requirements to every technical document, table, and module that implements them. Its purpose is narrow but high-value: when a requirement changes, this matrix tells you in seconds which documents, code modules, database objects, and tests need to be revisited — instead of that knowledge living only in the heads of whoever originally built each piece.

---

# 1. Purpose & Maintenance

This is **not** a complete enumeration of all ~76 PRD functional requirements on day one — building that exhaustively upfront would itself become stale the moment implementation reveals details no one anticipated. Instead:

- This document is seeded with a representative, fully-worked set of rows spanning every bounded context, demonstrating the pattern.
- **Every new PRD requirement gets a row added as part of implementation** — this is now a line item in the Definition of Done (Engineering Standards §12, updated alongside this document — see Section 5).
- **Every architectural change checklist entry** (TAB v2.0's new Change Checklist section) that touches a requirement updates that requirement's row.

A matrix that's 100% complete but frozen at this moment is less useful than one that's partial today but reliably maintained going forward.

---

# 2. How to Read This Matrix

Each row traces one requirement (or closely related requirement cluster) across every document that has a stake in it. A blank cell means that document genuinely has no bearing on this requirement — not that it was overlooked. The **Related ADR(s)** column points to the specific decision(s) that justify the design; if a requirement changes in a way that would invalidate that ADR, a new ADR is required (per ADR Governance), not a silent edit.

---

# 3. Matrix — Identity & Access

| Requirement | Domain Model | Database | Backend | Security | Config/Notification | Related ADR(s) | Tests (Engineering Standards §5) |
|---|---|---|---|---|---|---|---|
| FR-11 (MFA) | User §4 | `platform_user.mfa_enrolled` | Auth flow, §3 | Security Arch §3.2 (TOTP decision) | — | ADR-021 | Unit: enrollment flow; E2E: login+MFA (mandatory E2E per Eng Standards §5.1) |
| FR-12 (Invitation onboarding) | User lifecycle §4 | `platform_user.status` | Backend §3.3 | Security Arch §3.3 | Notification: `UserInvited` rule | ADR-021 | Unit: token expiry/single-use |
| FR-13 (Device/session visibility) | — | `tenant_audit_log.device_fingerprint` | Backend §4 (session mgmt) | Security Arch §4 | — | ADR-015 | Integration: audit log write on login |
| FR-14 (Forced logout on deactivation) | User lifecycle §4 | `platform_user.status` | Backend §4 (revocation triggers) | Security Arch §4 | — | — | Integration: token revocation |
| FR-09/FR-10 (Custom firm-role naming) | Role §4 | `firm_role` / `system_role` | — | Security Arch §5 (no privilege escalation) | — | — | Unit: role mapping cannot bypass system_role permissions |

---

# 4. Matrix — WSP Management & AI

| Requirement | Domain Model | Database | Backend | AI | Security | Related ADR(s) | Tests |
|---|---|---|---|---|---|---|---|
| FR-30 (OCR + parsing) | Document §3 | `wsp_version`, `wsp_section` | §9 (async job pattern) | §4 (pipeline stages 3–4) | — | ADR-012 | Integration: Docling/Textract merge |
| FR-31 (AI mapping suggestion, 85% accuracy) | AI Mapping §4 | `ai_mapping` | §9 | §5 (retrieval/ranking), §9 (eval harness) | §11 (EU residency) | ADR-025 | **Mandatory** unit + golden-dataset eval (Eng Standards §5.2) |
| FR-32 (Two-person mapping sign-off) | AI Mapping §4 | `ai_mapping.approver_1/2_id` | §8 (dual-control service) | §5.3 (confidence never gates auto-confirm) | — | — | **Mandatory**: dual-control policy test (Eng Standards §5.2) |
| FR-33 (Mapping reversal) | AI Mapping §4 | `ai_mapping` immutability trigger | §7 (state pattern) | — | — | — | Integration: trigger blocks direct update |
| FR-34 (Gap analysis) | Gap Analysis §3 | — (aggregation query) | — | §8 | — | — | Unit: set-difference logic |
| GAP-09 (who may initiate override) | — | — | §14 (open item) | — | — | — | *Blocked on product decision* |

---

# 5. Matrix — Compliance Testing & Findings

| Requirement | Domain Model | Database | Backend | Security | Config/Notification | Related ADR(s) | Tests |
|---|---|---|---|---|---|---|---|
| FR-17/19/20 (Test scheduling, scoping, assignment) | Test/Test Execution §4 | `test_schedule`, `test_execution` | §10 (Anchor Strategy) | — | Scheduled Jobs Registry (Config Arch §8) | ADR-014, GAP-01 (open) | Unit: `AnchorStrategy` swap doesn't break scheduling |
| FR-21b (N/A result + reason) | Test Execution §4 | `test_execution.na_reason` | §7 (transition table) | — | — | ADR-014 | **Mandatory**: transition test |
| FR-21c (Sampling change approval) | — | `sampling_record`, `sampling_record_amendment` | §8 (dual-control) | — | — | — | **Mandatory**: dual-control test |
| FR-27 (Test amendment chain) | Test Execution §4 | `test_execution.amended_from_id` | §7 | — | — | — | Integration: amendment never mutates original |
| FR-44/45 (Finding closure, dual control) | Finding §4 | `finding.closed_by_*` | §7, §8 | — | Notification: `FindingClosed` rule | — | **Mandatory**: dual-control + immutability trigger test |
| FR-46 (Repeat finding detection) | Finding §4 | `finding.is_repeat_finding` | — | — | — | — | Unit: prior-period comparison logic |
| FR-52 vs GAP-07 (Remediation Owner visibility — resolved to FR-52) | Remediation §4 | `remediation_milestone` query scope | §5.5 (query predicate, not a column) | — | Notification: `RemediationDeadlineApproaching` | — | Integration: owner cannot query others' items |
| GAP-08 (Deadline extension approval) | Remediation §4 | `remediation_milestone.extension_granted_by` | §8 (dual-control) | — | Notification: escalation lead time (Config Arch §5) | — | **Mandatory**: dual-control test |

---

# 6. Matrix — Reporting & Regulatory Monitoring

| Requirement | Domain Model | Database | Backend | Config | Related ADR(s) | Tests |
|---|---|---|---|---|---|---|
| FR-60/61 (Report generation + publication) | Report §4 | `report.report_data_snapshot`, immutability trigger | §11 (multi-format orchestration, TAB §11) | `reporting.default_branding_logo_url` | ADR-024 | E2E: generate → publish → immutability (mandatory per Eng Standards §5.1) |
| FR-55 (AML officer agreement gate) | — | `report.aml_officer_agreed_at` | §7 | — | — | Unit: publish blocked without gate |
| RP-04 (Word/Excel export) | — | `report.docx_ref`/`xlsx_ref` | §11 | — | ADR-024 | *Open — scope pending contract confirmation* |
| SA-03 (RSS/API-only monitoring) | Regulatory Update §3 | `regulation_version.source`/`fetched_at` | — | `regulatory_monitoring.poll_interval_minutes` | ADR-026 | Integration: scraping-pattern sources rejected |
| RE-01 (Auto-detect → admin approve) | Regulatory Update lifecycle §4 | `regulation_version.status` | §7 (transition table) | — | ADR-008, ADR-011 | Unit: publish requires human review status |

---

# 7. Matrix — Platform Administration & Cross-Cutting

| Requirement | Domain Model | Database | Backend | Security | Infra | Related ADR(s) | Tests |
|---|---|---|---|---|---|---|---|
| SA-06 (Portal cross-firm metadata visibility) | Entity Ownership §7 | `firm_registry` (excludes tenant data) | §5.2 (router enforcement) | §5 | — | — | **Mandatory** (elevated review, Eng Standards §6): Portal cannot query tenant schema |
| NFR-02 (Per-firm encryption keys) | — | Evidence/S3 refs | — | §6.1 (KMS hierarchy) | §6 (S3 structure) | — | Integration: DEK isolation per tenant |
| NFR-04/07 (Immutable audit, 6-year retention) | Audit Event §4 | §6 (trigger pattern), §7 (retention) | §7, §13 | §10 | §4 (Aurora backup) | ADR-015 | **Mandatory**: trigger blocks UPDATE/DELETE post-terminal-status |
| NFR-03 (EU data residency) | — | — | — | — | §2 (multi-account), §13 (DR region) | TI-01 | Integration: no non-EU region reachable |
| TI-02 (99.5% uptime SLA) | — | — | — | — | §4 (Aurora Multi-AZ), §13 (RTO/RPO) | — | *Operational — measured post-launch* |
| OS-02 (Per-firm communication channel CSV) | Bounded Context: Organization | `communication_channel_reference` | Import framework (future doc, Item 10 of gap review) | — | — | — | Integration: mismatch flagging on import |

---

# 8. Confirmed-Open Items Cross-Referenced

These rows exist specifically so an open item doesn't get lost across seven-plus documents — each links back to where it's tracked in detail:

| Item | Tracked In | Status |
|---|---|---|
| GAP-01 (test scheduling anchor logic) | Backend Architecture §10, §14 | Open — pluggable strategy built pending resolution |
| GAP-09 (WSP mapping override initiator) | Backend Architecture §14, AI & Document Intelligence §13 | Open |
| GAP-10 (mid-test regulation update UX) | Backend Architecture §14 | Open — backend emits event, UX pattern undecided |
| RP-04 (Word/Excel export contractual scope) | TAB v2.0 §21, Backend Architecture §14 | Architecture supports both; contract scope open |
| TI-03 (ISO 27001/SOC 2 requirement) | Security Architecture §15, §16 | Open — roadmap item |
| GDPR Art. 17(3)(b) legal sufficiency | Security Architecture §12.1, §16 | **Requires legal sign-off** |
| Remediation Owner visibility (FR-52 vs. GAP-07) | TAB v2.0 §21 | Resolved to FR-52; flagged for client reconciliation |

---

# 9. Maintenance Rule (Ties to Engineering Standards & TAB Change Checklist)

Every PR that adds or materially changes a PRD requirement's implementation must add or update the corresponding row in this matrix, as part of the Definition of Done (Engineering Standards §12) and the Architecture Change Checklist (TAB v2.0). A stale traceability matrix is worse than none — it creates false confidence — so this maintenance rule is treated as a hard requirement, not a suggestion, consistent with how this document set treats every other compliance-critical process.

---

# 10. Version History

| Version | Date | Notes |
|---------|------|------|
| 1.0 | Jul 2026 | Initial Cross-Document Traceability Matrix: representative rows across Identity & Access, WSP/AI, Compliance Testing/Findings, Reporting/Regulatory Monitoring, and Platform Administration bounded contexts; open-items cross-reference table; maintenance rule tying updates to the Definition of Done and Architecture Change Checklist. |
