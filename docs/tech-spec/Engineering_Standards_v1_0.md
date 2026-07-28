# ComplianceIQ – Engineering Standards

**Version:** 1.0
**Status:** Baseline
**Depends On:** Technical Architecture Baseline (TAB) v2.0, Database Architecture v1.2, Backend Architecture v1.1, AI & Document Intelligence v1.1, Security Architecture v1.0, Infrastructure & DevOps v1.0
**Audience:** All Engineering, QA, DevOps

> This document defines the day-to-day engineering conventions for ComplianceIQ: branching and release process, code style and static analysis, testing standards, code review gating, API contract discipline, documentation and ADR governance, accessibility, dependency management, and the Definition of Done. It closes the final gap the TAB v2.0 follow-up specification list identified and operationalizes several standards that prior documents named as targets without specifying ownership or process.

---

# 1. Purpose

Every prior document in this set fixed *what* to build and *why*. This document fixes *how the team works day to day* — the conventions that keep six months of contributions from six different engineers looking like one coherent, auditable codebase, which matters more than usual here given how much of this system's value depends on its compliance defensibility, not just its functionality.

---

# 2. Guiding Principles (Reaffirmed from TAB v2.0 §4)

- Modular Monolith for Phase 1; Hexagonal (Ports & Adapters) internally.
- Configuration over hardcoding.
- Version everything that impacts compliance.
- Every compliance-critical write goes through a service layer, never a bare ORM call from a view (Backend Architecture §2) — this document's review and testing standards exist specifically to keep that rule enforced in practice, not just in theory.

---

# 3. Branching & Release Strategy

**Trunk-based development.** Feature branches are short-lived (target: merged within 2 working days of creation), branched from `main`, and merged back via pull request after passing the full CI gate sequence (Infrastructure & DevOps §10.1).

- **Feature flags**, not long-lived branches, are the mechanism for shipping incomplete work safely — a half-built feature merges to `main` behind a flag rather than living on a divergent branch that accumulates merge conflicts.
- **No direct commits to `main`.** Every change, including hotfixes, goes through a PR — even an emergency fix gets a (possibly expedited, but not skipped) review.
- **Release tagging:** every deployment to Production is tagged (`vYYYY.MM.DD-N`), giving a clean rollback point independent of the ECS automatic-rollback mechanism (Infrastructure & DevOps §11).

---

# 4. Code Style & Static Analysis

## 4.1 Python (Django, FastAPI AI Service)

- Formatting: `black`, enforced pre-commit and in CI (non-negotiable, not a style preference — eliminates an entire category of PR review comments).
- Linting: `ruff`.
- **Type checking: `mypy --strict`, enforced as a hard CI gate**, not advisory. A type error fails the build at the same severity as a failing test.

**Rationale for strictness here specifically:** a meaningful share of this system's correctness lives in typed service-layer logic (state-machine transitions, Backend Architecture §7; dual-control policies, Backend Architecture §8) where a type error could mean an invalid state transition compiles and ships. Advisory type-checking is not sufficient given what's riding on that code being correct.

## 4.2 TypeScript (Firm App, Admin Portal, Marketing Site)

- Formatting/linting: `eslint` + `prettier`, pre-commit and CI-enforced.
- `tsconfig.json`: `strict: true` across all three frontend codebases, no per-file `// @ts-ignore` without an inline justification comment and a linked ticket to remove it.

## 4.3 SQL / Migrations

- Django migrations are reviewed with the same rigor as application code — a migration that runs against every tenant schema (Database Architecture §8) is not a low-stakes change.
- Any migration adding a PostgreSQL trigger (immutability enforcement, Database Architecture §6) requires an accompanying test that verifies the trigger actually blocks the forbidden operation, not just that the migration applies cleanly.

---

# 5. Testing Standards

## 5.1 Test Pyramid

- **Unit tests (majority):** service-layer logic in isolation — state machine transitions, dual-control policy evaluation, gap analysis set-difference logic, retrieval/ranking scoring (BM25/RRF fusion, AI & Document Intelligence §5).
- **Integration tests:** against a real (test-environment) PostgreSQL instance via testcontainers — critical for anything touching the immutability triggers or cross-schema reference validation (Database Architecture §9), since these are exactly the behaviors that are easy to get subtly wrong in a mocked-database unit test.
- **End-to-end tests (minimal, targeted):** Playwright/Cypress, reserved for the highest-value user flows only — login + MFA, WSP mapping confirmation (dual-control), test execution approval, finding closure, report generation and publication. Not a goal to E2E-test every screen; E2E tests are the slowest and most brittle layer and should be spent deliberately.

## 5.2 Coverage Targets

- Service/domain layer: minimum 80% line coverage, enforced in CI.
- Adapters/glue code (serializers, thin views): no hard threshold — coverage here is a byproduct of integration tests, not a target to chase directly.
- **Mandatory, non-negotiable coverage regardless of the 80% average:** every state machine transition path (Backend Architecture §7), every dual-control policy (Backend Architecture §8), every database immutability trigger (Database Architecture §6), and the AI evaluation gate logic itself (AI & Document Intelligence §9) — these are the modules where a gap in test coverage has outsized consequences given the compliance stakes riding on them.

## 5.3 Test Data

Per the environment strategy (TAB v2.0 §4a.3), Dev and Staging use synthetic data only — no production tenant data is ever copied down for testing, consistent with the tenant-isolation and data-residency guarantees the platform makes to its clients.

---

# 6. Code Review Standards

- **Standard PRs:** minimum 1 approval before merge.
- **Elevated review (minimum 2 approvals, at least one from a senior engineer):** any PR touching:
  - The tenant audit log or platform audit log (Database Architecture §5.9, §4.5)
  - State machine transition tables (Backend Architecture §7)
  - The dual-control service (Backend Architecture §8)
  - Encryption/key management code (Security Architecture §6)
  - Tenant-context resolution middleware (Backend Architecture §5)
  - Database immutability triggers (Database Architecture §6)

  These are the specific modules that every prior document independently flagged as the highest-stakes boundaries in the system — code review effort is deliberately concentrated where the earlier architecture work identified the real risk, not spread evenly across all code.
- **No self-approval**, even for a single-approval-tier PR, even from the most senior engineer on the team.
- Review turnaround target: same working day for standard PRs, to keep trunk-based development's short-lived-branch assumption realistic in practice.

---

# 7. API Contract & Versioning Discipline

- OpenAPI schema auto-generated from DRF via `drf-spectacular`, checked into CI output on every build.
- **CI diff-check:** the generated schema is automatically diffed against the previous released version. A detected breaking change (removed field, changed type, removed endpoint, changed required-ness) **fails the build** unless the PR is explicitly introducing a new `/api/v2/` surface (Backend Architecture §4.1) rather than modifying `v1` in place.
- This closes a real gap: without this check, nothing stops an engineer from quietly changing a `v1` response shape and breaking the Firm App or Admin Portal frontend without anyone noticing until a runtime error.

---

# 8. Documentation Standards

## 8.1 ADR Governance (Recap, ADR document's own governance section)

Every future architectural decision is recorded as a new ADR, never by editing a historical one. This applies to any decision at the level of the seven documents in this set (TAB, Database, Backend, AI, Security, Infrastructure, this document) — a change significant enough to affect one of those documents gets a new ADR entry and a version-history line in the affected document(s), following the exact pattern already used throughout this document set (e.g., the subdomain-per-tenant change, ADR-023 amendment).

## 8.2 Code-Level Documentation

- Every service-layer public function has a docstring explaining *why*, not just *what* — the *what* should be evident from well-named code; the *why* (particularly for compliance-logic functions) is what a future engineer actually needs and can't infer from the code alone.
- Module-level README for each Django app (Backend Architecture §3) explaining its bounded-context responsibility and its public service interface.

## 8.3 API Documentation

Auto-generated from the OpenAPI schema (Section 7) — not hand-maintained separately, to avoid the two drifting apart.

---

# 9. Accessibility Standards

**WCAG 2.1 AA** baseline for the Firm Application and Platform Admin Portal (the Marketing Site, being public-facing, is held to the same standard for the same reason — first impression and genuine reach). This isn't a strict legal requirement for this specific product category today, but the European Accessibility Act (effective June 2025) is pushing digital services broadly in this direction, and building to AA from the start is materially cheaper than a retrofit once hundreds of screens exist. Concretely: semantic HTML, keyboard navigability for every interactive element (including the dual-control approval flows and the test execution workflow), sufficient color contrast, and screen-reader-compatible form labeling throughout.

---

# 10. Dependency Management

- Automated dependency update PRs (Dependabot, per Security Architecture §14) generated weekly.
- **Triage ownership:** a rotating on-call engineer (weekly rotation) is responsible for reviewing and merging routine dependency PRs, and for triaging any critical/high CVE alert **within 24 hours** of it appearing — operationalizing the 7-day patch SLA that Security Architecture §14 set as a target but didn't assign an owner or a triage timeline to.
- Major version bumps (as opposed to patch/minor) go through standard PR review, not auto-merge, given the risk of behavioral change.

---

# 11. Error Handling & Logging Conventions

## 11.1 Error Handling

Every service-layer function that can fail in an expected way (e.g., "finding already closed," Backend Architecture §4.3) raises a specific, named exception type mapped to the JSON error envelope — never a bare `Exception` or an unhandled 500 for a foreseeable business-rule violation. Unhandled exceptions are logged with full context server-side but never leak internal detail (stack traces, query text) into the client-facing error response.

## 11.2 Logging

- Structured JSON logging throughout (ADR-019), consistent field naming across Django and FastAPI (`request_id`, `tenant_id` where applicable, `actor_id`, `action`).
- **The content boundary established in AI & Document Intelligence §11 (no raw WSP/prompt content in observability tooling) applies platform-wide, not just to AI calls** — no evidence content, no raw compliance-text fields, no personal data beyond what's operationally necessary (e.g., `actor_id` is fine; a user's full profile is not) ever gets logged to CloudWatch/New Relic. Logs are for engineering diagnostics; the database (with its own access controls and retention rules) is the system of record for tenant content.

---

# 12. Definition of Done

A feature/PR is not "done" until:

1. Code passes all CI gates (lint, type-check, tests, SCA scan, OpenAPI diff-check).
2. Required review approvals obtained (Section 6).
3. Test coverage meets the applicable target (Section 5.2), including mandatory coverage for any high-risk module touched.
4. Documentation updated (docstrings, module README if the bounded-context responsibility changed, ADR if an architectural decision was made).
5. **Cross-Document Traceability Matrix row added or updated**, and the Architecture Change Checklist (TAB v2.1 §21a) answered, for any change affecting a PRD requirement's implementation.
6. No new accessibility regressions (automated axe-core check in CI, minimum).
7. Deployed successfully to Staging and passed smoke tests (Infrastructure & DevOps §10.1) before being considered ready for UAT/Production promotion.

---

# 13. Commit & PR Conventions

- **Conventional Commits** format (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`) — enables automated changelog generation and keeps commit history genuinely useful for future archaeology, which matters more than usual given the audit/compliance context of this codebase.
- Every PR links to its tracking ticket (Jira or equivalent).
- PR template requires: what changed, why, how it was tested, and — for any PR touching an elevated-review module (Section 6) — an explicit note confirming which compliance/security property the change preserves.

---

# 14. Performance Budgets

- **API p95 latency target:** under 500ms for standard read endpoints, under 1s for write endpoints involving a state transition + audit log write + outbox event. AI-dependent endpoints (mapping suggestions) are explicitly exempt from this budget since they're async by design (Backend Architecture §9) — the budget applies to the synchronous request/response endpoints, not the background job itself.
- **Frontend bundle size budget:** tracked in CI (e.g., via a bundle-analyzer step); a PR that significantly grows the initial bundle size triggers a review flag rather than silently shipping a slower-loading app over time.

---

# 15. Open Items Carried Forward

| Item | Status |
|---|---|
| Exact tooling for automated axe-core/accessibility CI checks | Implementation-phase tooling selection, not an architectural blocker |
| Formal on-call rotation tooling for dependency triage (Section 10) | Ties to the same open item in Infrastructure & DevOps §15 (PagerDuty vs. alternative) |
| Bundle size budget specific numeric thresholds | To be set from an initial baseline measurement once the Firm App reaches a representative feature set, not guessed upfront |

---

# 16. Version History

| Version | Date | Notes |
|---------|------|------|
| 1.0 | Jul 2026 | Initial Engineering Standards: trunk-based branching with feature flags, strict type-checking as a hard CI gate, layered testing standards with mandatory coverage for compliance-critical modules, elevated code review gating for the highest-risk modules identified across the full document set, OpenAPI contract diff-checking, ADR governance recap, WCAG 2.1 AA accessibility baseline, operationalized dependency-triage ownership, platform-wide logging content boundaries, Definition of Done, and performance budgets. |
| 1.1 | Jul 2026 | Definition of Done updated to require Cross-Document Traceability Matrix maintenance and Architecture Change Checklist completion, per the TAB v2.1 governance addition. |
