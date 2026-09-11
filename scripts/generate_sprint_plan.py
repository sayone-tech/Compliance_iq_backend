#!/usr/bin/env python3
"""Generate the ControlIQ sprint-plan workbook.

Source of truth for scope: docs/requirement-specification/PRD.md (v9.0, 165 IDs)
and docs/tech-spec/*.md (module structure, stack, infrastructure).

Delivery model: the full PRD is committed inside 3 sprints. Engineers act as
orchestrators of parallel Claude Code agent streams rather than as typists, so
capacity is measured in agent-stream days, not person-days. See sheet 8.

Output: docs/planning/ControlIQ_Sprint_Plan.xlsx
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

OUT = Path(__file__).resolve().parent.parent / "docs" / "planning" / "ControlIQ_Sprint_Plan.xlsx"

# ---------------------------------------------------------------- styling ---

NAVY = "1F3864"
BLUE = "2F5496"
LIGHT = "D9E2F3"
AMBER = "FFF2CC"
GREEN = "E2EFDA"
RED = "FBE4E4"
GREY = "F2F2F2"

H1 = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
H2 = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
BOLD = Font(name="Calibri", size=11, bold=True)
BODY = Font(name="Calibri", size=10)
SMALL = Font(name="Calibri", size=9, italic=True, color="595959")

THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)

# ------------------------------------------------------- capacity constants --

PEOPLE = 5
DAYS_PER_SPRINT = 10
CEREMONY_DAYS = 1.5
EFFECTIVE_DAYS = DAYS_PER_SPRINT - CEREMONY_DAYS          # 8.5 per person per sprint
PARALLELISM = 2.0                                          # concurrent agent streams per orchestrator
STREAM_DAYS_PER_ROLE_SPRINT = EFFECTIVE_DAYS * PARALLELISM  # 17.0
SPRINT_CAPACITY = STREAM_DAYS_PER_ROLE_SPRINT * PEOPLE      # 85.0
TOTAL_CAPACITY = SPRINT_CAPACITY * 3                        # 255.0


def title_row(ws, text, span, row=1):
    ws.cell(row=row, column=1, value=text).font = H1
    ws.cell(row=row, column=1).fill = PatternFill("solid", fgColor=NAVY)
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=span)
    ws.cell(row=row, column=1).alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[row].height = 24


def header_row(ws, headers, row):
    for c, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=c, value=h)
        cell.font = H2
        cell.fill = PatternFill("solid", fgColor=BLUE)
        cell.alignment = CENTER
        cell.border = BORDER
    ws.row_dimensions[row].height = 30


def write_rows(ws, rows, start_row, fills=None):
    for r, data in enumerate(rows, start=start_row):
        for c, val in enumerate(data, start=1):
            cell = ws.cell(row=r, column=c, value=val)
            cell.font = BODY
            cell.alignment = WRAP
            cell.border = BORDER
        if fills:
            fill = fills(data)
            if fill:
                for c in range(1, len(data) + 1):
                    ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=fill)
    return start_row + len(rows)


def widths(ws, spec):
    for i, w in enumerate(spec, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


wb = Workbook()

# =========================================================== 1. OVERVIEW ===

ws = wb.active
ws.title = "1. Overview"
widths(ws, [28, 105])
title_row(ws, "ControlIQ — Sprint Plan & Delivery Roadmap (full scope, 3 sprints)", 2)

overview = [
    ("Product", "ControlIQ — MiCA/DORA compliance testing platform (ComplianceIQ up to PRD v4.0). Two applications on one backend: the Firm Application and the Platform Admin Portal, plus a public marketing site."),
    ("Scope basis", "PRD.md v9.0 — 128 FR + 25 SA + 12 NFR = 165 requirement IDs, ALL of them committed inside the 3-sprint window. v9.0 withdrew Section 11 (Systems and IT Risk) in full, retiring FR-72 to FR-77, and withdrew the IT / Systems Admin system role (eight system roles become seven). Tech baseline: docs/tech-spec/ (TAB v2.x, Backend Architecture, Database Architecture, Infrastructure & DevOps)."),
    ("Commitment", "The whole platform ships in 3 sprints. There is no MVP slice and no deferred module set. Sheet 6b lists only the three items that are outside the PRD commitment itself — one unapproved proposal, one withdrawn module, one post-launch certification programme."),
    ("Planning horizon", "3 sprints x 2 weeks = 6 weeks. No calendar start date fixed — all dates are relative (Sprint 1 = Weeks 1-2, Sprint 2 = Weeks 3-4, Sprint 3 = Weeks 5-6). Set the anchor date once and every sheet resolves."),
    ("Team", "1 Backend (Django/DRF/Celery), 1 AI (FastAPI/LangGraph), 1 Frontend (React/TS), 1 QA, 1 DevOps. 5 people. No headcount change."),
    ("", ""),
    ("DELIVERY MODEL", "Development is executed by Claude Code. The five engineers are orchestrators, not typists: they write the specification, drive parallel Claude Code agent streams against it, and own review, integration and merge. Throughput is therefore bounded by specification and review quality, not by keystrokes — which is what makes the full PRD fit into six weeks."),
    ("Capacity unit", "Agent-stream days, not person-days. One orchestrator sustains 2 concurrent Claude Code streams on average (peaking at 3 on well-specified CRUD and UI work, dropping to 1 on infrastructure and AI evaluation work). 5 people x 8.5 effective days x 2.0 parallelism = 85 agent-stream days per sprint, 255 over the three sprints."),
    ("Re-estimation", "Full-scope build effort is unchanged at 630 person-days. Each stream is divided by its Claude Code multiplier to give planned demand: Backend 4.0x, Frontend 4.0x, QA 3.5x, AI 2.5x, Infra/DevOps 2.0x. That yields 184 agent-stream days of demand against 255 available — a 28% buffer. Sheets 2 and 8 carry the arithmetic."),
    ("Why the multipliers differ", "Django models/serializers/services/migrations and React screens off a fixed design system are the most agent-amenable work in the plan, so they carry 4.0x. QA gains almost as much on test authoring but loses it back on triage, hence 3.5x. AI work carries 2.5x because prompt and eval tuning is bounded by domain-expert labelling, not code. Infrastructure carries 2.0x because Terraform apply, IAM, cloud state and DR drills are wall-clock bound and cannot be parallelised away."),
    ("The real constraint", "Review and merge throughput. A 400-line PR limit and a 4-hour review SLA are what keep trunk green while several agent streams land per person per day. If review slips, the plan slips — no amount of agent parallelism recovers it."),
    ("", ""),
    ("What ships in 3 sprints", "The complete platform: tenancy and identity; the Portal's regulatory and test libraries; enquiry to onboarding link to wizard to payment to tenant activation; WSP upload with AI-assisted mapping under dual control; the full compliance testing and evidence workflow including records requests and the business-owner surface; findings, remediation and closure; the formal testing report; dashboards, notifications, news feed and search; organisation, org chart and analytics; and the marketing site."),
    ("Sprint themes", "S1 Platform spine, libraries and AI core. S2 Commercial front door, WSP and test execution. S3 Findings, reporting, dashboards and launch hardening."),
    ("Module consolidation", "The 40 modules of the previous baseline are consolidated to 29 (sheet 2) — Portal API folded into the regulatory library, findings folded together with reporting, notifications with dashboards and search, the business-owner surface into the testing workspace, infrastructure from six modules to three. Fewer, fatter units of work: each sprint sheet carries 12-17 epics rather than 25 fragments, because an agent stream is briefed once against a whole capability, not per file."),
    ("", ""),
    ("Definition of Ready", "Requirement IDs cited; acceptance criteria written; API contract or screen agreed; dependencies merged to main or flagged; agent brief drafted (scope, contract, test expectations, files in play); test approach noted by QA."),
    ("Definition of Done", "Merged to main; CI green (lint, types, unit, contract, migration check); feature-flagged if user-visible and incomplete; unit + contract tests written; deployed to staging; acceptance criteria demonstrated; audit-log and tenant-isolation checks passing where the change touches tenant data; agent-generated code reviewed line by line by a named human, not skim-approved."),
    ("Sheets", "2. Modules | 3. Roadmap | 4-6. Sprint 1/2/3 tasks | 6b. Out of Scope | 7. Trunk-Based Dev | 8. Capacity | 9. Feature Flags | 10. RAID"),
]

r = 3
for label, text in overview:
    ws.cell(row=r, column=1, value=label).font = BOLD
    ws.cell(row=r, column=1).alignment = WRAP
    ws.cell(row=r, column=2, value=text).font = BODY
    ws.cell(row=r, column=2).alignment = WRAP
    if label in ("DELIVERY MODEL", "The real constraint"):
        for c in (1, 2):
            ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=AMBER)
    if label in ("What ships in 3 sprints", "Commitment"):
        for c in (1, 2):
            ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=GREEN)
    ws.row_dimensions[r].height = 56 if len(text) > 300 else (42 if len(text) > 150 else 28)
    r += 1

# ============================================================ 2. MODULES ===

ws = wb.create_sheet("2. Modules")
MOD_HEAD = ["Module ID", "Stream", "Module", "What it covers", "Key Requirement IDs", "Owner",
            "Full-scope est (person-days)", "Claude Code multiplier", "Planned est (agent-stream days)",
            "Sprint(s)", "Depends on"]
widths(ws, [11, 14, 26, 62, 34, 9, 13, 12, 14, 12, 20])
title_row(ws, "Module Breakdown — full PRD v9.0 scope, consolidated to 29 modules, all inside 3 sprints", len(MOD_HEAD))
header_row(ws, MOD_HEAD, 2)

MODULES = [
    # id, stream, name, covers, req ids, owner, full est, multiplier, planned, sprints, depends
    ("INF-1", "Infra/DevOps", "Cloud platform & data layer", "AWS accounts, VPC, subnets, security groups, ALB, DNS, WAF, TLS, ECS Fargate cluster; RDS PostgreSQL 16 + pgvector, ElastiCache Redis, S3 with versioning, KMS CMK and object-lock write-once retention for evidence.", "NFR-02, NFR-03, NFR-07", "DevOps", 18, "2.0x", 9.0, "S1, S2", "-"),
    ("INF-2", "Infra/DevOps", "Trunk CI/CD & environments", "GitHub Actions trunk pipeline (lint, types, tests, contract, migration check, image build), per-tenant migration step, auto-deploy to staging, blue-green ECS deploys with migration rollback, dev/staging/prod parity from one Terraform module set, independent AI service release.", "NFR-08", "DevOps", 13, "2.0x", 6.5, "S1, S2", "INF-1"),
    ("INF-3", "Infra/DevOps", "Security, observability & DR", "Secrets Manager with rotation, KMS, WAF rules, TLS and security headers; CloudWatch, Grafana Alloy, New Relic APM, SLO alerting; backups, PITR, restore drill, tenant provisioning hook, DR runbook, cost tagging and budget alarms.", "NFR-02, NFR-05, NFR-07, NFR-08", "DevOps", 14, "2.0x", 7.0, "S2, S3", "INF-1"),

    ("BE-1", "Backend", "Platform core & AI gateway", "Modular monolith scaffold, tenant middleware and context resolution, tenant schema provisioning and per-tenant migration runner, transactional outbox plus poller, dual-control (maker-checker) service, base permission classes, two-tier append-only audit log with DB-level immutability triggers, and the Django-side async client for the FastAPI AI service.", "FR-13, FR-31, FR-88, FR-112, NFR-01, NFR-04, NFR-07", "BE", 23, "4.0x", 5.75, "S1", "INF-1"),
    ("BE-2", "Backend", "Identity & access", "Email+password auth, MFA, invite-only user creation, 7 system roles, custom firm role names, deactivate-never-delete, two-Super-Admin rule, RBAC enforcement layering across the firm and portal namespaces.", "FR-09 to FR-15, FR-117", "BE", 15, "4.0x", 3.75, "S1", "BE-1"),
    ("BE-3", "Backend", "Organisation & staff", "Firm profile, service lines, staff records by spreadsheet upload, multi-role holders, org chart and CCO-independence flag, qualifications and expiry, communication channels, hardware register, BCP call tree, org analytics, employee directory, distribution lists.", "FR-01 to FR-08, FR-62 to FR-70, FR-101 to FR-103, FR-116, FR-120 to FR-122, FR-139", "BE", 25, "4.0x", 6.25, "S1, S2", "BE-1"),
    ("BE-4", "Backend", "Regulatory library & Portal API", "Regulation/version/article/requirement models, test definitions, step templates, evidence checklist templates, sampling methodology library, priority and risk config, test cloning, versioned publish workflow; plus the Portal API: enquiry pipeline, onboarding link lifecycle, firm registry, regulatory draft queue and publishing with provenance, glossary and guidance library, associate admin roles, system settings.", "SA-01 to SA-25", "BE", 40, "4.0x", 10.0, "S1, S2", "BE-1"),
    ("BE-5", "Backend", "Onboarding, payment & activation", "Resumable onboarding wizard state machine, licence capture, revenue template parsing, financial-report derivation, regulatory perimeter derivation, call-tree and org gap review, hosted-checkout payment with no card data on platform, payment records per attempt, retry without data loss, tenant activation and pending-pool seeding, login gating.", "FR-92, FR-93, FR-104, FR-117 to FR-128, NFR-12", "BE", 25, "4.0x", 6.25, "S2", "BE-2, BE-3, BE-4"),
    ("BE-6", "Backend", "WSP management", "WSP upload (docx/pdf/scanned), immutable version history, AI mapping review, two-person dual approval including reversal, gap analysis wiring, regulation-change impact alerts on mapped sections, annual review cycle.", "FR-30 to FR-37", "BE", 20, "4.0x", 5.0, "S2", "BE-1, AI-3"),
    ("BE-7", "Backend", "Compliance testing & evidence", "Pending-item pool, manual assignment and article-level fan-out, scope period, partial testing, execution steps, evidence store with shelf life and immutability, sampling records, request lists and supplementary requests, announcement letters with auto-populated distribution, business-owner request items per unit, turnaround metrics and escalation, N/A register, sign-off and amendment.", "FR-16 to FR-28, FR-78 to FR-91, FR-94, FR-105 to FR-111, FR-129 to FR-135", "BE", 45, "4.0x", 11.25, "S2, S3", "BE-4, BE-5"),
    ("BE-8", "Backend", "Findings, remediation & reporting", "Findings register, severity, High-finding escalation with the five-business-day acknowledgement clock, remediation plans and milestones, milestone evidence, dual-approval closure with recorder exclusion, repeat-finding detection, CCO three review outcomes; report generation gating, fixed section structure, health score, N/A appendix, scope periods, sign-off, distribution, immutable archive, PDF/DOCX/XLSX rendering.", "FR-38 to FR-47, FR-55 to FR-61, FR-98 to FR-100, FR-136", "BE", 38, "4.0x", 9.5, "S3", "BE-7"),
    ("BE-9", "Backend", "Notifications, dashboards & search", "Notification engine, templates, in-app and email dispatch, per-user preferences, weekly outstanding-items digest, escalation timers; metric cards, Kanban and calendar views, records-request metrics, tester-progress view, remediation dashboards, period comparison, regulatory news feed with AML vendor sources, application search.", "Section 12, FR-43, FR-48 to FR-54, FR-67, FR-87, FR-95 to FR-97, FR-113 to FR-115, FR-138", "BE", 32, "4.0x", 8.0, "S3", "BE-1, BE-7"),

    ("AI-1", "AI", "AI service platform & evals", "FastAPI service scaffold, LangGraph runtime, async job queue and contract, provider abstraction (ADR-007), prompt template registry; golden dataset schema, offline eval runs, per-dimension scoring, CI regression gate (ADR-025).", "ADR-007, ADR-025", "AI", 16, "2.5x", 6.4, "S1", "-"),
    ("AI-2", "AI", "Document intelligence & retrieval", "Docling parsing, AWS Textract OCR for scanned documents, layout-aware chunking, extraction quality checks; pgvector storage split by ownership, embedding model registry, dimension-safe versioned tables, hybrid retrieval.", "FR-24, FR-30, ADR-006", "AI", 22, "2.5x", 8.8, "S1", "AI-1, INF-1"),
    ("AI-3", "AI", "WSP mapping & gap analysis", "Requirement-to-WSP-section mapping suggestions with confidence and citations under a human-in-the-loop output contract; real-time WSP coverage gaps and step-level gaps surfaced during test execution; quality tuning to the golden-set threshold.", "FR-31, FR-34, FR-112, FR-135", "AI", 22, "2.5x", 8.8, "S2, S3", "AI-2"),
    ("AI-4", "AI", "Evidence match verification", "Upload-time check that a document matches the request item, mismatch flagging with retention not rejection, cost gating of downstream processing, mandatory human verification gate for financial systems and critical controls.", "FR-88 to FR-91, FR-110", "AI", 10, "2.5x", 4.0, "S2", "AI-2"),
    ("AI-5", "AI", "Regulatory ingestion & diffing", "EUR-Lex / EBA / ESMA fetch, provenance capture, house-format rendering, change detection against carried regulations with affected Requirement IDs, execution frequency and priority capture, AML vendor feed.", "SA-03, SA-12 to SA-15, SA-23, FR-35, FR-51, FR-138", "AI", 15, "2.5x", 6.0, "S2", "AI-1"),

    ("FE-1", "Frontend", "Design system & app shells", "React + TS shells for both SPAs, routing, React Query, react-i18next, design tokens, base component library in a shared package, API client with auth and tenant headers, standard error envelope handling, pagination.", "NFR-10", "FE", 12, "4.0x", 3.0, "S1", "-"),
    ("FE-2", "Frontend", "Onboarding wizard UI", "Multi-step resumable wizard, per-step validation, revenue upload, service-line confirmation, gap review, payment step with failure and retry states, activation and first-login transition.", "FR-104, FR-117 to FR-128", "FE", 15, "4.0x", 3.75, "S2", "FE-1, BE-5"),
    ("FE-3", "Frontend", "WSP UI", "Upload, version history, AI mapping review with confirm/adjust, dual-approval flow with author exclusion, gap analysis view.", "FR-30 to FR-37", "FE", 12, "4.0x", 3.0, "S2", "FE-1, BE-6"),
    ("FE-4", "Frontend", "Testing workspace & owner surface", "Pending pool, assignment and article fan-out, Kanban and calendar, test execution steps, evidence upload, request lists, N/A register; plus the business-owner scoped expiring-link surface with their unit's request items, upload and reason-for-no-document capture.", "FR-78 to FR-91, FR-113, FR-114, FR-129 to FR-134", "FE", 38, "4.0x", 9.5, "S2, S3", "FE-1, BE-7"),
    ("FE-5", "Frontend", "Findings, dashboards & reports UI", "Findings register, severity views, remediation plans and milestones, owner action list; CCO dashboard metric cards, regulatory updates panel, news feed, report generation, sign-off and download.", "FR-38 to FR-61, FR-95 to FR-100", "FE", 35, "4.0x", 8.75, "S3", "FE-1, BE-8"),
    ("FE-6", "Frontend", "Organisation & staff UI", "Staff spreadsheet import, interactive org chart, qualifications, communication channels, hardware, call tree capture, org analytics and employee directory.", "FR-62 to FR-70, FR-101 to FR-103, FR-116", "FE", 15, "4.0x", 3.75, "S1", "FE-1, BE-3"),
    ("FE-7", "Frontend", "Admin Portal SPA", "Portal shell, enquiry queue and detail, agreement record, onboarding link issue/revoke, firm registry, regulation and test authoring, priority config, sampling library, glossary, settings.", "SA-01 to SA-25", "FE", 30, "4.0x", 7.5, "S1, S2", "FE-1, BE-4"),
    ("FE-8", "Frontend", "Marketing site", "Next.js site plus headless CMS, pricing and plan pages, public enquiry capture feeding the SA-16 pipeline.", "Section 1.3, SA-16", "FE", 12, "4.0x", 3.0, "S3", "BE-4"),

    ("QA-1", "QA", "Strategy, framework & CI gates", "Test strategy, DoR/DoD, CI quality gates and coverage thresholds, pytest and factories, Playwright scaffold, tenant-isolation harness, seed data for two demo tenants.", "NFR-01", "QA", 8, "3.5x", 2.25, "S1", "INF-2"),
    ("QA-2", "QA", "API & contract testing", "OpenAPI publication and contract-test harness, per-module API regression suites across every capability shipped, negative and validation coverage, versioning behaviour assertions.", "-", "QA", 20, "3.5x", 5.75, "S1-S3", "QA-1"),
    ("QA-3", "QA", "E2E automation", "Playwright journeys: auth and MFA, enquiry to activation, WSP mapping under dual control, test execution with evidence, records requests, finding to signed-off report.", "-", "QA", 25, "3.5x", 7.0, "S2, S3", "QA-1"),
    ("QA-4", "QA", "Security, performance & UAT", "Tenant-isolation audit, RBAC authorisation matrix across 7 roles, load tests to NFR-05, evidence immutability and six-year retention verification, penetration-test remediation, UAT with Sosinna's team.", "NFR-01, NFR-05, NFR-07", "QA", 15, "3.5x", 4.5, "S3", "QA-1"),
]

r = write_rows(ws, MODULES, 3, fills=lambda d: GREEN)

ws.cell(row=r, column=3, value="TOTAL — full platform scope, all in 3 sprints").font = BOLD
ws.cell(row=r, column=7, value=sum(m[6] for m in MODULES)).font = BOLD
ws.cell(row=r, column=9, value=round(sum(m[8] for m in MODULES), 2)).font = BOLD
for c in range(1, 12):
    ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=LIGHT)
    ws.cell(row=r, column=c).border = BORDER
r += 2
ws.cell(row=r, column=3, value="Stream").font = BOLD
ws.cell(row=r, column=7, value="Full-scope").font = BOLD
ws.cell(row=r, column=9, value="Planned").font = BOLD
r += 1
for stream in ["Backend", "Frontend", "AI", "Infra/DevOps", "QA"]:
    ws.cell(row=r, column=3, value=f"{stream} subtotal").font = BODY
    ws.cell(row=r, column=7, value=sum(m[6] for m in MODULES if m[1] == stream)).font = BODY
    ws.cell(row=r, column=9, value=round(sum(m[8] for m in MODULES if m[1] == stream), 2)).font = BODY
    r += 1
ws.cell(row=r + 1, column=3, value="Column G is unchanged build effort in person-days. Column I is that effort divided by the stream's Claude Code multiplier — the orchestrator-supervised agent-stream days the plan actually budgets. 255 agent-stream days are available across the 3 sprints (sheet 8).").font = SMALL

ws.freeze_panes = "A3"
ws.auto_filter.ref = f"A2:K{2 + len(MODULES)}"

# ============================================================ 3. ROADMAP ===

ws = wb.create_sheet("3. Roadmap")
RM_HEAD = ["Sprint", "Weeks (relative)", "Theme", "Goal / demo statement", "Modules in play",
           "Key deliverables", "Exit criteria", "Status"]
widths(ws, [10, 16, 30, 52, 26, 62, 58, 12])
title_row(ws, "Project Roadmap — full PRD v9.0 delivered across 3 sprints", len(RM_HEAD))
header_row(ws, RM_HEAD, 2)

ROADMAP = [
    ("Sprint 0", "Pre-start (3-5 days)", "Mobilisation & specification", "Every Sprint 1 epic has an agent brief good enough to run against on day 1.",
     "INF-1, INF-2",
     "Repos created; AWS accounts opened; access and licences granted; Claude Code agent conventions agreed (brief format, review checklist, PR size limit, commit convention); PRD open questions triaged into blocking and non-blocking; branch protection and CODEOWNERS set; backlog loaded into the tracker; agent briefs written for all Sprint 1 epics.",
     "Every engineer has push access to main behind a green CI; every Sprint 1 epic meets Definition of Ready including its agent brief; the blocking open questions have a client decision slot booked.",
     "Not started"),
    ("Sprint 1", "Weeks 1-2", "Platform spine, libraries & AI core",
     "A user logs in with MFA into a tenant-isolated app; the Portal authors and publishes a regulation and a test; a WSP-shaped document is parsed, chunked and embedded.",
     "INF-1, INF-2, BE-1 to BE-4, AI-1, AI-2, FE-1, FE-6, FE-7, QA-1, QA-2",
     "AWS baseline plus RDS/pgvector/Redis/S3 with write-once evidence storage; trunk CI/CD to staging with the per-tenant migration step; tenant middleware, schema provisioning and migration runner; auth, MFA and 7-role RBAC; append-only audit log with DB triggers; regulatory and test libraries with versioned publish; organisation and staff core with org chart; FastAPI AI service with eval harness and CI regression gate; Docling + Textract ingestion, chunking and pgvector retrieval; design system and both SPA shells; Portal authoring screens; organisation UI; test framework, tenant-isolation harness and contract tests.",
     "Green pipeline deploys main to staging automatically; two tenants provisioned with proven data isolation; login+MFA works end to end; audit rows are provably non-deletable; a regulation and a test are published from the Portal and visible firm-side; a scanned PDF and a .docx both produce ordered, section-attributed, embedded chunks.",
     "Not started"),
    ("Sprint 2", "Weeks 3-4", "Commercial front door, WSP & test execution",
     "An enquiry becomes a paying, activated tenant; that tenant uploads a WSP, has it AI-mapped and dual-approved, and its CCO assigns an article-scoped test that a tester executes with evidence.",
     "INF-1 to INF-3, BE-3 to BE-7, AI-3 to AI-5, FE-2, FE-3, FE-4, FE-7, QA-2, QA-3",
     "Enquiry pipeline and onboarding link lifecycle; resumable wizard with revenue parsing, perimeter derivation and gap review; hosted-checkout payment, payment records and tenant activation with pool seeding; WSP upload, immutable versions and dual-control mapping approval; compliance testing core with pool, assignment, article fan-out, execution steps and immutable evidence store; organisation depth (qualifications, channels, hardware, call tree, analytics, distribution lists); AI mapping and gap analysis v1; regulatory ingestion and diffing with provenance; evidence match verification; onboarding, WSP and testing UIs; Portal enquiry and firm-registry screens; blue-green deploys, secrets rotation, WAF, observability and SLO alerts.",
     "An enquiry is walked New to Active in staging with payment taken through hosted checkout and no card data on the platform; a WSP mapping is approved under two-person control with the author excluded; one test is fanned out across two testers by article and executed step by step with evidence written to write-once storage.",
     "Not started"),
    ("Sprint 3", "Weeks 5-6", "Findings, reporting, dashboards & launch",
     "A completed test produces a finding, the finding is escalated, remediated and closed under dual control, and the CCO generates, signs off and distributes the formal testing report.",
     "INF-3, BE-7 to BE-9, AI-3, FE-4, FE-5, FE-8, QA-2 to QA-4",
     "Records requests end to end: announcement letters, auto-populated distribution with justified edits, request items per business unit, supplementary requests, turnaround tracking and escalation, N/A register, sign-off and amendment; business-owner scoped-link surface; findings register with the five-day High-finding clock, remediation milestones and dual-approval closure with repeat detection; report generation, health score, N/A appendix, sign-off, distribution, immutable archive and PDF/DOCX/XLSX rendering; notifications with preferences, digests and escalation timers; dashboards, Kanban, calendar, period comparison, news feed and application search; step-level gap surfacing; marketing site with the public enquiry form; tenant provisioning automation, DR drill, load test to NFR-05, RBAC matrix, retention verification and UAT.",
     "The full journey runs on staging in one demo: enquiry to activation to WSP mapping to test execution to finding to remediation closure to a signed, archived, distributed report; a public enquiry submitted on the marketing site appears in the Portal queue; DR drill passed and UAT signed off by Sosinna's team.",
     "Not started"),
    ("Launch", "End of Week 6", "Production cutover", "The first paying firm is onboarded on production.",
     "All",
     "Production deploy executed from main as a tagged promotion of the staged image; cutover runbook followed; monitoring and on-call live.",
     "Production serving; rollback rehearsed and timed under 10 minutes.",
     "Not started"),
]

r = write_rows(ws, ROADMAP, 3, fills=lambda d: (GREEN if d[0] in ("Sprint 1", "Sprint 2", "Sprint 3")
                                                else LIGHT))
r += 1
ws.cell(row=r, column=1, value="Every PRD v9.0 requirement ID is carried by a module in sheet 2 and a sprint here. Sheet 6b lists the only three exclusions, none of which is a committed PRD requirement.").font = SMALL
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
ws.freeze_panes = "A3"

# ====================================================== 4-6. SPRINT SHEETS ==

SPRINT_HEAD = ["Task ID", "Module", "Role", "Epic", "Requirement IDs", "Est (agent-stream days)",
               "Priority", "Depends on", "Feature flag", "Acceptance criteria", "Status"]
SPRINT_WIDTHS = [10, 12, 8, 52, 30, 9, 9, 14, 24, 62, 11]

SPRINT1 = [
    ("S1-01", "INF-1", "DevOps", "AWS baseline and data layer: VPC, subnets, security groups, ALB, Route 53, TLS, WAF, ECS Fargate cluster; RDS PostgreSQL 16 with pgvector, ElastiCache Redis, S3 buckets with versioning, KMS CMK and object-lock write-once retention", "NFR-02, NFR-03, NFR-07", 6, "Must", "-", "-", "terraform apply provisions dev and staging from code with no console-created resource; the app reaches RDS and Redis from ECS; an object written to the evidence bucket cannot be deleted or overwritten by the application role", "To do"),
    ("S1-02", "INF-2", "DevOps", "Trunk CI/CD: GitHub Actions gates (lint, types, unit, contract, migration check), image build, per-tenant migration step, automatic staging deploy on every green main; dev/staging parity from one Terraform module set", "NFR-08", 4, "Must", "S1-01", "-", "A merge to main reaches staging with no manual step; a red gate blocks the merge; the pipeline finishes under 12 minutes; migrations apply across every tenant schema idempotently", "To do"),
    ("S1-03", "BE-1", "BE", "Platform core: modular monolith scaffold with bounded-context apps, tenant middleware and context resolution, tenant schema provisioning and migration runner, transactional outbox plus poller, maker-checker service, base permission classes, two-tier append-only audit log with DB-level immutability triggers, and the async ai_gateway client", "FR-13, FR-31, NFR-01, NFR-04, NFR-07", 5.75, "Must", "S1-01", "-", "A request resolves search_path to its tenant schema and a mismatched subdomain/JWT pair is rejected 403; provisioning a firm creates tenant_<uuid> with the full table set; import-linter forbids cross-app ORM imports; UPDATE and DELETE on the audit table are rejected by trigger even for the DB owner", "To do"),
    ("S1-04", "BE-2", "BE", "Identity and access: user model, email+password auth, JWT issuance, MFA enrolment and verification, invite-only account creation, 7 system roles, custom firm role names, deactivate-never-delete, two-Super-Admin rule, RBAC enforcement across the firm and portal namespaces", "FR-09 to FR-15, FR-117", 3.75, "Must", "S1-03", "flag.mfa_enforced", "A new user accepts an invite, sets a password, enrols MFA and cannot reach any API without the second factor; a role lacking a permission gets 403, not a filtered response; a Portal view has no import path to a tenant-scoped manager", "To do"),
    ("S1-05", "BE-4", "BE", "Regulatory and test library in the shared schema: regulation/version/article/requirement models, test definitions, step templates, evidence checklist templates, sampling methodology library, priority and risk configuration, test cloning with clone history, review-before-publish workflow", "SA-01 to SA-05, SA-09 to SA-11, SA-22, SA-23", 6, "Must", "S1-03", "-", "A regulation and a test are created, versioned, cloned, reviewed and published; earlier versions remain readable and unmodified; a firm mid-way through an earlier test version keeps that version", "To do"),
    ("S1-06", "BE-3", "BE", "Organisation core: firm profile, registered address, jurisdictions, NCA licence, service lines, staff records by spreadsheet upload only, multi-role holders, reporting lines, org chart model and CCO-independence flag", "FR-01 to FR-08, FR-62 to FR-66, FR-101, FR-139", 4, "Must", "S1-03", "-", "A spreadsheet upload creates the staff set with reporting lines and returns actionable per-row errors on malformed input; the org chart renders from reporting lines; a CCO reporting into a revenue line raises the independence flag", "To do"),
    ("S1-07", "AI-1", "AI", "AI service platform: FastAPI scaffold, LangGraph runtime, async job contract consumed by ai_gateway, provider abstraction, prompt template registry, eval harness with golden-dataset schema, per-dimension scoring and the CI regression gate", "ADR-007, ADR-025", 6.4, "Must", "-", "-", "Django submits a job, polls status and receives a completion callback, idempotent on retry; swapping the model provider is a configuration change with no call-site edit; a seed golden set runs offline, prints per-dimension scores and fails CI on regression", "To do"),
    ("S1-08", "AI-2", "AI", "Document intelligence and retrieval: Docling parsing for docx/pdf, Textract OCR for scanned documents, layout-aware chunking with page and section attribution, pgvector storage split by ownership, embedding model registry, dimension-safe versioned tables, hybrid retrieval", "FR-24, FR-30, ADR-006", 8.8, "Must", "S1-07, S1-01", "-", "A scanned PDF and a .docx both produce ordered, section-attributed chunks with page references; embeddings write to the versioned table for the active model and a dimension change creates a new table rather than an ALTER; hybrid retrieval returns citable chunks", "To do"),
    ("S1-09", "FE-1", "FE", "Design system and both SPA shells: tokens, typography, buttons, forms, tables, modals, toasts in a shared package; routing, React Query, react-i18next, API client with auth and tenant headers, standard error envelope and pagination helpers", "NFR-10", 3, "Must", "S1-03", "-", "Both SPAs build from one shared component package; Storybook renders the base set; a 403 tenant mismatch and a validation error render distinct, actionable UI states", "To do"),
    ("S1-10", "FE-7", "FE", "Admin Portal: shell and authoring surface — regulation and test authoring screens, step and checklist templates, priority and risk configuration, sampling methodology library, publish workflow", "SA-01 to SA-05, SA-09 to SA-13, SA-22", 4, "Must", "S1-09, S1-05", "-", "A test is authored, cloned, priority set, reviewed and published without leaving the Portal; portal auth points at the portal namespace only", "To do"),
    ("S1-11", "FE-6", "FE", "Organisation and staff UI: spreadsheet import with row-level error reporting, interactive org chart, qualifications, communication channels, hardware register, call tree capture, employee directory", "FR-62 to FR-70, FR-116", 3.75, "Must", "S1-09, S1-06", "-", "Staff import surfaces per-row errors; the org chart renders and is navigable; every employee shows a call contact and a reporting manager or is flagged as a gap", "To do"),
    ("S1-12", "QA-1", "QA", "Test strategy, DoR/DoD including the agent-brief and human-review rule, CI quality gates and coverage thresholds, pytest and factories, Playwright scaffold, tenant-isolation harness, seed data for two demo tenants", "NFR-01", 2.25, "Must", "S1-02", "-", "Gates are enforced in the pipeline rather than by convention; a test asserts tenant A's session cannot read tenant B's rows through any API path; one command produces two provisioned tenants with users in every system role", "To do"),
    ("S1-13", "QA-2", "QA", "OpenAPI publication and contract-test harness covering core, identity, library and organisation APIs, with negative and validation coverage", "-", 1.5, "Must", "S1-05", "-", "A breaking API change fails contract tests before it reaches the frontend; publishing a new test version does not mutate any prior version's payload", "To do"),
]

SPRINT2 = [
    ("S2-01", "INF-1", "DevOps", "Evidence storage hardening and data protection: KMS CMK policy, object-lock retention proof, access logging, automated backups, point-in-time recovery and a timed restore drill", "NFR-02, NFR-07", 3, "Must", "S1-01", "-", "A restore to a new instance is executed and timed with RPO and RTO recorded in the runbook; the evidence bucket rejects delete and overwrite for the retention period", "To do"),
    ("S2-02", "INF-2", "DevOps", "Blue-green ECS deployment with migration failure handling and automatic rollback; independent release pipeline and autoscaling for the AI service", "NFR-08", 2.5, "Must", "S1-02", "-", "A failing migration halts the deploy and leaves the previous task set serving traffic; the AI service releases independently of Django from the same trunk", "To do"),
    ("S2-03", "INF-3", "DevOps", "Security and observability: Secrets Manager rotation, WAF rule set, TLS policy and security headers at the ALB; CloudWatch and Grafana dashboards, New Relic APM, SLO alerts on latency, errors, Celery queue depth and AI job duration", "NFR-02, NFR-05, NFR-08", 3.5, "Must", "S2-02", "-", "Rotation runs without a deploy; WAF blocks the OWASP baseline in staging; dashboards show request latency, queue depth and AI job duration and alerts page on breach", "To do"),
    ("S2-04", "BE-4", "BE", "Portal API: enquiry model and status pipeline, onboarding link lifecycle (generation, delivery, expiry, re-send, revoke, full audit), firm registry, regulatory draft queue and publishing with provenance, glossary and guidance library, associate admin roles, system settings", "SA-06 to SA-08, SA-14 to SA-21, SA-24, SA-25", 4, "Must", "S1-05", "-", "Statuses advance only along legal transitions and the queue ages an enquiry; a link is unique to one enquiry, carries no credentials, and every issue, re-issue and revocation is recorded with actor and time", "To do"),
    ("S2-05", "BE-5", "BE", "Onboarding, payment and activation: resumable wizard state machine with per-step validation, licence capture, revenue template parsing to service lines, financial-report derivation, regulatory perimeter derivation, call-tree and org gap review, hosted-checkout payment with payment record per attempt, retry without data loss, tenant activation with pool seeding, login gating", "FR-92, FR-93, FR-104, FR-117 to FR-128, NFR-12", 6.25, "Must", "S2-04, S1-06", "flag.onboarding_wizard, flag.payments", "A firm leaves mid-wizard and resumes at the same step with data intact; no card data reaches ControlIQ logs or storage; a failed payment retains everything and allows retry; success activates the tenant, seeds the pool with the derived Requirement IDs and only then permits login", "To do"),
    ("S2-06", "BE-6", "BE", "WSP management: upload of docx, pdf and scanned documents, immutable version history, AI mapping review, two-person dual approval including reversal with author exclusion, gap analysis wiring, regulation-change impact alerts on mapped sections, annual review cycle", "FR-30 to FR-37", 5, "Must", "S2-09", "flag.wsp_ai_mapping", "A mapping requires two independent senior approvals and excludes the policy author; every version is retained and readable; an amended article raises an alert naming the affected mapped sections", "To do"),
    ("S2-07", "BE-7", "BE", "Compliance testing core: requirement-to-service-line applicability, pending-item pool generation, assignment with scope period and article-level fan-out, partial testing coverage, execution step instances and progress, evidence store with accepted types, shelf life and immutability, sampling records", "FR-16 to FR-28, FR-78 to FR-82, FR-105, FR-106, FR-129", 6, "Must", "S2-05", "flag.pending_pool, flag.test_assignment", "Confirming service lines loads exactly the applicable Requirement IDs at the correct frequency; one test is split by article across two testers and each sees only their articles; only the CCO can assign; a test moves Planned to Ongoing with evidence attached to each step", "To do"),
    ("S2-08", "BE-3", "BE", "Organisation depth: qualifications and expiry reminders, communication channels, hardware register, BCP call tree with gap evaluation, org analytics, distribution lists", "FR-67 to FR-70, FR-102, FR-103, FR-137", 2.25, "Must", "S1-06", "-", "Certification expiry raises a reminder on schedule; analytics counts surface staff without managers, staff without channels and total hardware; a distribution list resolves to the units it names", "To do"),
    ("S2-09", "AI-3", "AI", "WSP mapping suggestions and gap analysis v1: retrieval over regulation embeddings, LangGraph mapping chain, confidence scores and citations under the human-in-the-loop output contract, requirement coverage against confirmed mappings", "FR-31, FR-34, FR-112", 6, "Must", "S1-08", "flag.wsp_ai_mapping, flag.gap_analysis", "A sample WSP returns ranked requirement-to-section suggestions each citing its source chunk; the firm sees which required Requirement IDs have no WSP section, updating as mappings are confirmed", "To do"),
    ("S2-10", "AI-5", "AI", "Regulatory ingestion and diffing: EUR-Lex, EBA and ESMA connectors with full provenance, house-format rendering, change detection against carried regulations, execution frequency and priority capture, AML vendor feed", "SA-03, SA-12 to SA-15, SA-23, FR-35, FR-51, FR-138", 6, "Must", "S1-07", "flag.reg_ingestion", "A fetched item lands in the draft queue with source API, retrieval timestamp, effective date, execution frequency and priority; an amended article produces a diff and a Portal notification naming the affected Requirement IDs", "To do"),
    ("S2-11", "AI-4", "AI", "Evidence match verification: upload-time check that a document matches the request item, mismatch flagging with retention not rejection, cost gating of downstream processing, mandatory human verification gate for financial systems and critical controls", "FR-88 to FR-91, FR-110", 4, "Must", "S1-08", "flag.evidence_ai_check", "A mismatched upload is flagged, retained and notified to both uploader and Lead Tester; a mismatched file never consumes a full AI test run; critical-control evidence still requires a human sign-off", "To do"),
    ("S2-12", "FE-2", "FE", "Onboarding wizard UI: step navigation, resumable progress, per-step validation, revenue upload and service-line confirmation with derivation comparison, gap review, payment step with failure and retry states, activation and first-login transition", "FR-104, FR-117 to FR-128", 3.75, "Must", "S2-05", "flag.onboarding_wizard, flag.payments", "The wizard resumes from the link at the correct step and loses nothing on refresh; derived service lines are shown for confirmation with a clear re-upload path; a failed payment shows a plain explanation and a retry that works", "To do"),
    ("S2-13", "FE-3", "FE", "WSP UI: upload, version history, AI mapping review with confirm and adjust per suggestion, dual-approval flow, gap analysis view", "FR-30 to FR-37", 3, "Must", "S2-06", "flag.wsp_ai_mapping", "A reviewer confirms or adjusts each suggestion and a second approver signs off in a separate session; the gap view updates as mappings are confirmed", "To do"),
    ("S2-14", "FE-4", "FE", "Testing workspace v1: pending pool, assignment and article fan-out, Kanban and calendar views, test execution steps with progress, evidence upload", "FR-78 to FR-82, FR-105, FR-106, FR-113, FR-114, FR-129", 5, "Must", "S2-07", "flag.test_assignment", "The CCO assigns articles to testers by drag or form with priority and scope period on every card; a tester walks a test step by step and attaches evidence to each", "To do"),
    ("S2-15", "FE-7", "FE", "Portal: enquiry queue and detail, agreement record, onboarding link issue and revoke, firm registry, glossary and settings screens", "SA-06 to SA-08, SA-16 to SA-21, SA-24, SA-25", 3.5, "Must", "S2-04", "-", "An enquiry is walked New to Link Issued in the browser with each transition visible in its history; the firm registry shows every firm's onboarding checklist state", "To do"),
    ("S2-16", "QA-2", "QA", "Contract and regression coverage for the Portal, onboarding, payment, WSP and testing APIs including versioning behaviour and cross-tenant probes on every endpoint added this sprint", "NFR-01, SA-01 to SA-04", 2.5, "Must", "S2-07", "-", "A cross-tenant identifier returns 404 or 403, never data; illegal enquiry transitions and malformed revenue files are rejected with actionable errors", "To do"),
    ("S2-17", "QA-3", "QA", "E2E: onboarding link to wizard to payment to activation, and WSP upload to AI mapping to dual approval", "FR-117 to FR-128, FR-30 to FR-33", 3.5, "Must", "S2-12, S2-13", "-", "Both suites run on every green main; resume-after-abandon and the author-exclusion rule are covered; the payment sandbox asserts every provider outcome with no card data in logs or database", "To do"),
]

SPRINT3 = [
    ("S3-01", "INF-3", "DevOps", "Tenant provisioning automation hook off the activation event, DR runbook with a rehearsed schema-level restore, performance and load test environment, cost tagging, budget alarms, release and rollback runbook", "NFR-01, NFR-05, NFR-07, NFR-08", 3.5, "Must", "S2-03", "-", "Tenant creation is triggered by activation with no manual step; the DR drill is rehearsed and timed; a 100-concurrent-user run is recorded against the two-second p95 target; a rollback is executed under 10 minutes in a drill", "To do"),
    ("S3-02", "BE-7", "BE", "Records requests and business-owner surface: announcement letters to auto-populated distribution lists with justified edits, request items mapped to business units, supplementary requests, request and receipt dates with a two-week default window, ageing, escalation and reportable turnaround metrics, N/A register with mandatory justification file, sign-off and amendment", "FR-83 to FR-87, FR-94, FR-96, FR-107 to FR-109, FR-130 to FR-135", 5.25, "Must", "S2-07", "-", "Editing the auto-populated distribution list is itself an audited decision with a recorded justification; every request item records when it was asked, when it was received and who uploaded it; evidence has no channel outside the platform; turnaround metrics are reportable across a testing period", "To do"),
    ("S3-03", "BE-8", "BE", "Findings and remediation: findings register with severity and article linkage, multiple findings per test, High-finding escalation with the five-business-day acknowledgement clock, remediation plans and milestones with evidence, dual-approval closure excluding the recorder, repeat-finding detection, the CCO's three review outcomes", "FR-38 to FR-47, FR-136", 5, "Must", "S3-02", "flag.findings_remediation", "A finding moves Open to Closed with the recorder excluded from the approvers; a High finding starts the five-day clock and escalates on breach; only the CCO assigns a remediation owner; a recurrence is detected against prior periods", "To do"),
    ("S3-04", "BE-8", "BE", "Reporting: generation gating, fixed section structure, calculated health score and risk rating, N/A appendix, scope periods, sign-off, distribution, immutable archive, PDF, DOCX and XLSX rendering", "FR-55 to FR-61, FR-98 to FR-100", 4.5, "Must", "S3-03", "flag.reporting", "A report cannot be generated before its gating conditions are met; a signed-off report is archived unchangeably and distributed to its list; all three formats render the same content", "To do"),
    ("S3-05", "BE-9", "BE", "Notifications, dashboards and search: notification engine with templates, in-app and email dispatch, per-user preferences, weekly outstanding-items digest, escalation timers; metric cards, Kanban and calendar, records-request metrics, tester-progress view, remediation dashboards, period comparison, regulatory news feed with AML vendor sources, tenant-scoped application search", "Section 12, FR-43, FR-48 to FR-54, FR-67, FR-87, FR-95 to FR-97, FR-113 to FR-115, FR-138", 8, "Must", "S3-03", "flag.news_feed", "Digests and escalation timers fire on schedule; dashboard cards read live counts for tests due, open findings and outstanding requests; search returns tenant-scoped results only", "To do"),
    ("S3-06", "AI-3", "AI", "Step-level gap surfacing inside test execution and mapping quality tuning to the agreed golden-set threshold with the regression gate enforced", "FR-31, FR-135", 2.8, "Must", "S2-09", "flag.gap_analysis", "The Lead Tester sees AI-identified gaps against each test step and records a status per step; mapping precision and recall are measured on the golden set and a regression fails CI", "To do"),
    ("S3-07", "FE-4", "FE", "Testing workspace completion: request lists and supplementary requests, N/A register, and the business-owner scoped expiring-link surface showing that unit's request items with upload and reason-for-no-document capture", "FR-129 to FR-134", 4.5, "Must", "S3-02", "-", "A business owner opens the link from the announcement letter, sees only their unit's items, uploads a document or records a reason, and cannot reach anything else; the link expires and is revocable", "To do"),
    ("S3-08", "FE-5", "FE", "Findings, remediation, dashboards and reports UI: findings register and severity views, remediation plans, milestones and owner action list, CCO dashboard metric cards, regulatory updates panel, news feed, report generation, sign-off and download", "FR-38 to FR-61, FR-95 to FR-100", 8.75, "Must", "S3-04, S3-05", "flag.findings_remediation, flag.reporting", "A finding is raised, escalated, remediated and closed in the browser; the CCO generates, signs off and downloads the report in all three formats from the dashboard", "To do"),
    ("S3-09", "FE-8", "FE", "Marketing site: Next.js build with a headless CMS, pricing and plan pages, public enquiry form wired to the enquiry pipeline", "Section 1.3, SA-16", 3, "Must", "S2-04", "flag.marketing_site", "A public enquiry submitted on the site appears in the Portal queue with source attribution; content is editable in the CMS without a deploy", "To do"),
    ("S3-10", "QA-2", "QA", "Contract and regression coverage for the findings, reporting, notification and dashboard APIs, plus cross-tenant probes on every endpoint added this sprint", "NFR-01", 1.75, "Must", "S3-05", "-", "Every endpoint shipped in Sprint 3 has a contract test and a cross-tenant probe; an archived report is proven immutable through the API", "To do"),
    ("S3-11", "QA-3", "QA", "E2E: test execution to evidence to finding to remediation closure to signed-off report, and the records-request journey from announcement letter to business-owner upload", "FR-83 to FR-87, FR-38 to FR-61", 3.5, "Must", "S3-08", "-", "The full compliance cycle runs green on staging in one journey; the records-request journey covers both the upload and the no-document-reason path", "To do"),
    ("S3-12", "QA-4", "QA", "Launch hardening: tenant-isolation audit, RBAC authorisation matrix across all 7 system roles for every endpoint, load test to NFR-05, evidence immutability and six-year retention verification, penetration-test remediation, UAT with Sosinna's team and the cutover demo script", "NFR-01, NFR-05, NFR-07", 4.5, "Must", "S3-10", "-", "Each role-endpoint pair has an expected verdict and the suite fails on any drift; retention and immutability are evidenced not asserted; UAT is signed off and the production cutover runbook is rehearsed", "To do"),
]

for idx, (name, rows, theme) in enumerate([
    ("4. Sprint 1", SPRINT1, "Sprint 1 (Weeks 1-2) — Platform Spine, Libraries & AI Core"),
    ("5. Sprint 2", SPRINT2, "Sprint 2 (Weeks 3-4) — Commercial Front Door, WSP & Test Execution"),
    ("6. Sprint 3", SPRINT3, "Sprint 3 (Weeks 5-6) — Findings, Reporting, Dashboards & Launch"),
], start=1):
    ws = wb.create_sheet(name)
    widths(ws, SPRINT_WIDTHS)
    title_row(ws, theme, len(SPRINT_HEAD))
    header_row(ws, SPRINT_HEAD, 2)
    r = write_rows(ws, rows, 3, fills=lambda d: LIGHT if d[2] == "BE" else None)
    r += 1
    ws.cell(row=r, column=4, value="Load by role (agent-stream days)").font = BOLD
    r += 1
    sprint_total = 0.0
    for role in ["BE", "AI", "FE", "QA", "DevOps"]:
        total = round(sum(t[5] for t in rows if t[2] == role), 2)
        sprint_total += total
        ws.cell(row=r, column=4, value=role).font = BODY
        ws.cell(row=r, column=5, value="allocated").font = BODY
        ws.cell(row=r, column=6, value=total).font = BODY
        ws.cell(row=r, column=7, value=f"of {STREAM_DAYS_PER_ROLE_SPRINT} own capacity").font = SMALL
        if total > STREAM_DAYS_PER_ROLE_SPRINT:
            ws.cell(row=r, column=6).fill = PatternFill("solid", fgColor=AMBER)
            ws.cell(row=r, column=8, value="overflow orchestrated by QA / DevOps / AI — see sheet 8").font = SMALL
        r += 1
    ws.cell(row=r, column=4, value="Sprint total").font = BOLD
    ws.cell(row=r, column=6, value=round(sprint_total, 2)).font = BOLD
    ws.cell(row=r, column=7, value=f"of {SPRINT_CAPACITY} team capacity").font = SMALL
    ws.cell(row=r + 2, column=4, value="One agent-stream day is one day of one Claude Code stream under one orchestrator. Each engineer sustains 2 concurrent streams; a role over its own 17-day line has the excess orchestrated by a colleague with slack, per the overflow pool in sheet 8.").font = SMALL
    ws.freeze_panes = "A3"
    ws.auto_filter.ref = f"A2:K{2 + len(rows)}"

# ====================================================== 6b. OUT OF SCOPE ===

ws = wb.create_sheet("6b. Out of Scope")
BL_HEAD = ["ID", "Item", "Requirement IDs", "Est (person-days)", "Why it is not in the 3 sprints", "Decision needed by"]
widths(ws, [10, 56, 26, 14, 72, 22])
title_row(ws, "Out of Scope — the only exclusions from the 3-sprint commitment", len(BL_HEAD))
header_row(ws, BL_HEAD, 2)

BACKLOG = [
    ("OS-01", "Request portal for structured tester / business-unit back-and-forth on missing or incorrect documents", "FR-111", 6, "The PRD marks FR-111 as PROPOSED and explicitly not approved for scope — the client asked for a development-effort assessment first. It is excluded because it was never committed, not because the window is short. The Sprint 3 business-owner surface (S3-07) covers upload and reason capture without it.", "Sprint 2 planning, if it is to be added"),
    ("OS-02", "Systems and IT Risk module: IT system inventory and IT incident management", "FR-72 to FR-77 (retired)", 25, "Withdrawn from scope by PRD v9.0, which also retired the IT / Systems Admin system role. Listed here so nobody rebuilds it from an older tech-spec document. Any reversal is a change request, not a re-plan, and adds roughly 25 person-days.", "Only on a client change request"),
    ("OS-03", "ISO 27001 and SOC 2 Type II evidence programme", "NFR-09", 8, "The PRD places certification on the roadmap rather than as a launch blocker. The platform controls the certifications depend on — encryption, audit trails, RLS-equivalent isolation, retention, DR — all ship inside the 3 sprints; the evidence-collection programme itself starts post-launch.", "First month after launch"),
]
r = write_rows(ws, BACKLOG, 3, fills=lambda d: AMBER)
ws.cell(row=r + 1, column=2, value="Everything else in PRD v9.0 — all 165 requirement IDs that are committed — is carried by a module in sheet 2 and an epic in sheets 4 to 6.").font = BOLD
ws.freeze_panes = "A3"

# ==================================================== 7. TRUNK-BASED DEV ===

ws = wb.create_sheet("7. Trunk-Based Dev")
TB_HEAD = ["Area", "Rule", "Why", "Enforced by"]
widths(ws, [24, 74, 60, 34])
title_row(ws, "Trunk-Based Development with Claude Code — working agreement", len(TB_HEAD))
header_row(ws, TB_HEAD, 2)

TRUNK = [
    ("Branching", "One long-lived branch: main. It is always releasable. No develop branch, no release branches, no long-lived feature branches.", "Removes merge debt and the integration crunch that a 3-sprint window cannot absorb.", "Branch protection on main"),
    ("Agent briefs", "Every epic gets a written brief before an agent runs: scope, API or screen contract, files in play, test expectations, and the acceptance criteria copied from the sprint sheet. No brief, no stream.", "The brief is the actual unit of work in this delivery model. A vague brief costs more review time than it saves in typing.", "Definition of Ready"),
    ("Stream isolation", "One agent stream owns one epic and one short-lived branch. Two streams never edit the same module in the same day — sequence them or split the module boundary first.", "Concurrent agents on shared files produce conflicts that cost more than the parallelism gains.", "Board WIP limit; module ownership column"),
    ("Human review", "Every agent-generated line is read by a named human before merge. Review is line-by-line, not skim-approval, and the reviewer is accountable for the code as if they wrote it.", "Agent throughput only converts into delivery if review keeps up. This is the plan's binding constraint, stated as a rule.", "CODEOWNERS; PR checklist"),
    ("Branch lifetime", "Short-lived branches only — under 24 hours from first commit to merge. If work will take longer, split it or hide it behind a flag and merge the incomplete slice.", "Keeps every integration small enough to review and revert cheaply.", "Stale-branch report in CI"),
    ("Pull requests", "Small PRs, target under 400 changed lines. One reviewer. Review turnaround within 4 business hours. Squash merge, linear history.", "Small diffs get real review; big diffs get rubber-stamped — and an agent can generate a big diff in minutes.", "PR size check in CI"),
    ("Feature flags", "Anything user-visible and incomplete merges behind a flag, default off. Flags are registered in sheet 9 with an owner and a removal sprint.", "Lets unfinished work ship to main without shipping to users.", "Flag registry review at sprint review"),
    ("Flag hygiene", "A flag is removed in the sprint after it reaches 100% rollout, and every flag is removed before launch. Removal is a planned task, not a good intention.", "Stale flags become permanent branching in the code, and this plan has no fourth sprint to clean up in.", "Cleanup task in the next sprint"),
    ("CI on every push", "Lint, type check, unit tests, contract tests, migration check, image build. Under 12 minutes. A red pipeline blocks the merge.", "Trunk only works if main is provably green, and it is being written to many times a day.", "GitHub Actions required checks"),
    ("Continuous deployment", "Every green main deploys automatically to staging. Production deploys are a tagged, approved promotion of an already-staged image — never a rebuild.", "What is tested is what ships.", "Pipeline stages (S1-02)"),
    ("Database migrations", "Expand/contract only. Phase 1 adds the new nullable column or table and deploys; phase 2 backfills; phase 3 removes the old shape in a later deploy. Never a destructive migration in the same deploy as the code that needs it.", "Blue-green deploys run old and new code against one schema; a destructive migration breaks the old tasks mid-deploy.", "Migration review checklist"),
    ("Tenant migrations", "Every migration runs across all tenant schemas through the tenant migration runner and must be idempotent and re-runnable.", "One firm per schema means a migration is applied N times, not once.", "Migration runner (S1-03)"),
    ("Reverting", "Fix forward for small defects; revert the merge commit for anything that breaks staging. Reverting is normal, not a failure.", "A revertable trunk is what makes continuous merge safe at this cadence.", "Runbook (S3-01)"),
    ("Commit convention", "Conventional commits with the requirement ID in the subject, e.g. feat(onboarding): resumable wizard state machine [FR-118].", "Ties every commit back to the PRD for the traceability matrix.", "commitlint in CI"),
    ("Work in progress", "One epic in progress per orchestrator, with up to two agent streams inside it. Swarm on a blocker rather than opening a third stream.", "WIP is what turns a 6-week plan into an 8-week plan, and agents make it cheap to start too much.", "Board WIP limit"),
    ("Definition of Done", "See sheet 1. Merged to main, green in CI, flagged if incomplete, tested, demonstrated on staging, and human-reviewed line by line.", "Done-on-a-branch is not done under trunk-based development.", "Sprint review"),
]
write_rows(ws, TRUNK, 3)
ws.freeze_panes = "A3"

# ========================================================== 8. CAPACITY ====

ws = wb.create_sheet("8. Capacity")
CAP_HEAD = ["Stream", "People", "Full-scope est (person-days)", "Claude Code multiplier",
            "Planned demand (agent-stream days)", "Own capacity over 3 sprints", "Balance", "Verdict"]
widths(ws, [14, 8, 15, 13, 16, 15, 11, 56])
title_row(ws, "Capacity vs Scope — orchestrator model", len(CAP_HEAD))
header_row(ws, CAP_HEAD, 2)

STREAMS = ["Backend", "Frontend", "AI", "Infra/DevOps", "QA"]
OWNER_OF = {"Backend": "BE", "Frontend": "FE", "AI": "AI", "Infra/DevOps": "DevOps", "QA": "QA"}
MULT = {"Backend": "4.0x", "Frontend": "4.0x", "AI": "2.5x", "Infra/DevOps": "2.0x", "QA": "3.5x"}

cap_rows = []
for stream in STREAMS:
    full = sum(m[6] for m in MODULES if m[1] == stream)
    planned = round(sum(m[8] for m in MODULES if m[1] == stream), 2)
    own = STREAM_DAYS_PER_ROLE_SPRINT * 3
    balance = round(own - planned, 2)
    if balance < 0:
        verdict = (f"Over its own line by {abs(balance)} stream-days. Covered by the overflow pool below — "
                   "QA, DevOps and AI orchestrate backend streams in the sprints where they have slack.")
    elif balance > 20:
        verdict = "Large slack. This is the reserve the overflow pool draws on."
    else:
        verdict = "Fits within its own orchestration capacity."
    cap_rows.append((stream, 1, full, MULT[stream], planned, own, balance, verdict))

r = write_rows(ws, cap_rows, 3, fills=lambda d: AMBER if d[6] < 0 else GREEN)
total_planned = round(sum(c[4] for c in cap_rows), 2)
ws.cell(row=r, column=1, value="TOTAL").font = BOLD
ws.cell(row=r, column=2, value=PEOPLE).font = BOLD
ws.cell(row=r, column=3, value=sum(c[2] for c in cap_rows)).font = BOLD
ws.cell(row=r, column=5, value=total_planned).font = BOLD
ws.cell(row=r, column=6, value=TOTAL_CAPACITY).font = BOLD
ws.cell(row=r, column=7, value=round(TOTAL_CAPACITY - total_planned, 2)).font = BOLD
ws.cell(row=r, column=8, value=f"630 person-days of build effort becomes {total_planned} agent-stream days against {TOTAL_CAPACITY} available — a {round((TOTAL_CAPACITY - total_planned) / TOTAL_CAPACITY * 100)}% buffer. The full PRD fits in 3 sprints under this model and does not fit without it.").font = BOLD
for c in range(1, 9):
    ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=LIGHT)
    ws.cell(row=r, column=c).border = BORDER
    ws.cell(row=r, column=c).alignment = WRAP

# --- per-sprint loading grid ---
r += 2
ws.cell(row=r, column=1, value="Per-sprint loading (agent-stream days)").font = BOLD
r += 1
grid_head = ["Stream", "Sprint 1", "Sprint 2", "Sprint 3", "Total", "Capacity per sprint", "Peak sprint"]
for c, h in enumerate(grid_head, start=1):
    cell = ws.cell(row=r, column=c, value=h)
    cell.font = H2
    cell.fill = PatternFill("solid", fgColor=BLUE)
    cell.alignment = CENTER
    cell.border = BORDER
r += 1

SPRINT_LOAD = {
    "Backend":      (19.5, 23.5, 22.75),
    "Frontend":     (10.75, 15.25, 16.25),
    "AI":           (15.2, 16.0, 2.8),
    "Infra/DevOps": (10.0, 9.0, 3.5),
    "QA":           (3.75, 6.0, 9.75),
}
grid_rows = []
for stream in STREAMS:
    s1, s2, s3 = SPRINT_LOAD[stream]
    peak = max(s1, s2, s3)
    grid_rows.append((stream, s1, s2, s3, round(s1 + s2 + s3, 2), STREAM_DAYS_PER_ROLE_SPRINT,
                      "over own line" if peak > STREAM_DAYS_PER_ROLE_SPRINT else "within own line"))
r = write_rows(ws, grid_rows, r, fills=lambda d: AMBER if d[6] == "over own line" else GREEN)
totals = [round(sum(SPRINT_LOAD[s][i] for s in STREAMS), 2) for i in range(3)]
ws.cell(row=r, column=1, value="TEAM").font = BOLD
for i, t in enumerate(totals):
    ws.cell(row=r, column=2 + i, value=t).font = BOLD
ws.cell(row=r, column=5, value=round(sum(totals), 2)).font = BOLD
ws.cell(row=r, column=6, value=SPRINT_CAPACITY).font = BOLD
ws.cell(row=r, column=7, value="all three sprints inside team capacity").font = BOLD
for c in range(1, 8):
    ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=LIGHT)
    ws.cell(row=r, column=c).border = BORDER
    ws.cell(row=r, column=c).alignment = WRAP

# --- overflow pool ---
r += 2
ws.cell(row=r, column=1, value="Backend overflow pool — who orchestrates the excess backend streams").font = BOLD
r += 1
pool_head = ["Sprint", "Backend load", "Backend own capacity", "Excess", "Absorbed by", "Note"]
for c, h in enumerate(pool_head, start=1):
    cell = ws.cell(row=r, column=c, value=h)
    cell.font = H2
    cell.fill = PatternFill("solid", fgColor=BLUE)
    cell.alignment = CENTER
    cell.border = BORDER
r += 1
POOL = [
    ("Sprint 1", 19.5, 17.0, 2.5, "QA (2.5)", "QA is at 3.75 of 17 in Sprint 1 — the framework work finishes early and the tenant-isolation harness is itself backend-adjacent."),
    ("Sprint 2", 23.5, 17.0, 6.5, "DevOps (4.0), QA (2.5)", "DevOps is at 9.0 of 17 once the platform is standing; both orchestrate backend streams under backend review."),
    ("Sprint 3", 22.75, 17.0, 5.75, "AI (4.0), DevOps (1.75)", "AI drops to 2.8 in Sprint 3 once mapping tuning closes, freeing the largest single block of slack in the plan."),
]
r = write_rows(ws, POOL, r, fills=lambda d: GREY)

r += 2
notes = [
    "Capacity model: 5 people, 10 working days per sprint, minus 1.5 days of ceremonies (planning 0.5, refinement 0.5, review + retro 0.5) = 8.5 effective days per person per sprint. Each person sustains 2.0 concurrent Claude Code agent streams, so the unit is 17 agent-stream days per person per sprint, 85 per sprint across the team, 255 over the three sprints.",
    "The 2.0 parallelism figure is an average, not a target. Well-specified CRUD and UI work sustains 3 concurrent streams; Terraform apply, IAM changes, DR drills and AI eval labelling sustain 1. The multipliers in column D already carry that difference — do not apply it twice.",
    "Multipliers are applied to build effort only. They do not shorten client decision time, domain-expert labelling, provider sandbox access, or any wall-clock external dependency. Those live in sheet 10 as risks and issues.",
    "The overflow pool is real work assignment, not an accounting device: a QA or DevOps engineer orchestrating a backend stream still ships through backend review and CODEOWNERS. Book it in planning, not at the sprint's midpoint.",
    "No allowance is made for public holidays or leave. Subtract those from the sprint's capacity line directly once the start date is fixed. With a 28% buffer the plan absorbs roughly one person-week of loss per sprint before scope has to move.",
    "Review throughput is the constraint that is not in this arithmetic. Five orchestrators landing two streams each means up to 10 reviewable PRs a day. The 400-line PR limit and the 4-hour review SLA in sheet 7 are what keep that survivable; if either slips the plan slips with it.",
    "PRD v9.0 (Sep 2026) removed 25 person-days: the Systems & IT Risk backend (15) and its UI (10). It also closed EV-03 and UM-01. Those removals are already reflected in the 630 figure.",
]
for n in notes:
    ws.cell(row=r, column=1, value=n).font = SMALL
    ws.cell(row=r, column=1).alignment = WRAP
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
    ws.row_dimensions[r].height = 30
    r += 1
ws.freeze_panes = "A3"

# ====================================================== 9. FEATURE FLAGS ===

ws = wb.create_sheet("9. Feature Flags")
FF_HEAD = ["Flag", "Introduced", "Owner role", "Guards", "Default", "Rollout trigger", "Removal"]
widths(ws, [26, 12, 11, 56, 10, 46, 16])
title_row(ws, "Feature Flag Register — every flag removed before launch", len(FF_HEAD))
header_row(ws, FF_HEAD, 2)

FLAGS = [
    ("flag.mfa_enforced", "Sprint 1", "BE", "Hard MFA requirement on every authenticated route", "off", "Enabled once the enrolment flow is E2E-covered", "Sprint 2"),
    ("flag.onboarding_wizard", "Sprint 2", "BE", "Onboarding wizard routes and the firm-side onboarding API", "off", "Enabled for the first pilot firm on staging", "Sprint 3"),
    ("flag.payments", "Sprint 2", "BE", "Hosted checkout, payment records and tenant activation", "off", "Enabled after the provider sandbox suite passes", "Sprint 3"),
    ("flag.reg_ingestion", "Sprint 2", "AI", "Automated EUR-Lex / EBA / ESMA fetch and the draft queue", "off", "Enabled after a week of shadow runs with no false publishes", "Sprint 3"),
    ("flag.wsp_ai_mapping", "Sprint 2", "AI", "AI mapping suggestions surfaced in the WSP review UI", "off", "Enabled when golden-set precision clears the agreed threshold", "Sprint 3"),
    ("flag.pending_pool", "Sprint 2", "BE", "Pending-item pool generation and its firm-side views", "off", "Enabled with the first activated tenant", "Sprint 3"),
    ("flag.test_assignment", "Sprint 2", "BE", "Assignment, scope period and article fan-out", "off", "Enabled at the Sprint 2 review demo", "Sprint 3"),
    ("flag.evidence_ai_check", "Sprint 2", "AI", "Upload-time evidence match check and mismatch flagging", "off", "Enabled once the human verification gate is proven mandatory in the flow", "Sprint 3"),
    ("flag.gap_analysis", "Sprint 2", "AI", "WSP coverage gaps and step-level gap surfacing", "off", "Enabled when mapping approvals produce stable coverage data", "Sprint 3"),
    ("flag.findings_remediation", "Sprint 3", "BE", "Findings register, escalation clock and remediation closure", "off", "Enabled once the dual-approval exclusion rule is E2E-covered", "Before launch"),
    ("flag.reporting", "Sprint 3", "BE", "Report generation, sign-off, distribution and the immutable archive", "off", "Enabled when all three render formats match on the same content", "Before launch"),
    ("flag.news_feed", "Sprint 3", "BE", "Regulatory news feed including AML vendor sources", "off", "Enabled after a shadow run against the vendor source", "Before launch"),
    ("flag.marketing_site", "Sprint 3", "FE", "Public enquiry form posting into the SA-16 pipeline", "off", "Enabled at DNS cutover for the public domain", "Before launch"),
]
write_rows(ws, FLAGS, 3, fills=lambda d: AMBER if d[6] == "Before launch" else None)
ws.cell(row=3 + len(FLAGS) + 1, column=1, value="Sprint 3 flags are removed as part of launch hardening (S3-12). There is no fourth sprint to clean up in — a flag left in main at cutover is a defect, not debt.").font = SMALL
ws.freeze_panes = "A3"

# ============================================================== 10. RAID ===

ws = wb.create_sheet("10. RAID")
RAID_HEAD = ["ID", "Type", "Item", "Impact", "Likelihood", "Response", "Owner", "Status"]
widths(ws, [8, 12, 62, 12, 12, 62, 11, 11])
title_row(ws, "Risks, Assumptions, Issues, Dependencies", len(RAID_HEAD))
header_row(ws, RAID_HEAD, 2)

RAID = [
    ("R-01", "Risk", "Human review becomes the bottleneck. Five orchestrators landing two agent streams each can generate more reviewable code per day than five people can read properly, and skim-approval of agent output is how defects reach main at speed.", "High", "High", "Hold the 400-line PR limit and the 4-hour review SLA as hard rules; make review the first thing in the day, not the last; if the queue ages past four hours for two days running, cut concurrent streams from two to one and re-plan scope at the sprint boundary rather than lowering the review bar.", "Tech lead", "Open"),
    ("R-02", "Risk", "The Claude Code multipliers (4.0x backend and frontend, 3.5x QA, 2.5x AI, 2.0x infra) are estimates, not measurements. If real throughput lands at 3.0x across the board, demand rises from 184 to roughly 240 stream-days against 255 available and the buffer is gone.", "High", "Medium", "Measure actual multiplier per stream at the end of Sprint 1 against the sheet-2 full-scope figures. If it lands below 3.0x, the decision at the Sprint 1 review is to add orchestrators or move a Sprint 3 module out — not to absorb it silently in Sprint 2.", "PM", "Open"),
    ("R-03", "Risk", "PRD Sections 15 and 16 carry 40+ unresolved open questions. In a 6-week plan they are the true critical path: an unanswered question stalls an epic that agents could otherwise finish in a day.", "High", "High", "Triage all of them in Sprint 0 into blocking and non-blocking. Book a daily 30-minute client decision slot for the whole 6 weeks, not a weekly one. Ship behind a flag with a documented assumption where a decision is pending, and record the assumption in the epic.", "PM", "Open"),
    ("R-04", "Risk", "Agent-generated code is plausible-looking and locally consistent, which makes subtle defects in tenancy, permissions and audit trails harder to catch by eye than hand-written equivalents.", "High", "Medium", "Never rely on review alone for the three cross-cutting invariants. The tenant-isolation harness, the RBAC matrix and the audit-immutability triggers are all built in Sprint 1 and run in CI from that point, so a regression fails the build rather than the review.", "QA", "Open"),
    ("R-05", "Risk", "AI mapping quality (FR-31) may not reach usable precision inside the tuning window, and golden-set labelling depends on client domain experts who are not on the delivery team.", "Medium", "Medium", "The PRD already treats suggestions as a starting point with mandatory human review. Ship the review workflow first and let quality improve behind flag.wsp_ai_mapping. Book the labelling sessions in Sprint 1 for use in Sprint 2.", "AI", "Open"),
    ("R-06", "Risk", "EUR-Lex, EBA and ESMA endpoints are rate-limited and change shape without notice; ingestion may break silently.", "Medium", "Medium", "Store provenance on every fetch, alarm on zero-result runs, and keep the manual input interface from TAB s9.4 as the fallback path.", "AI", "Open"),
    ("R-07", "Risk", "Evidence immutability and six-year retention (NFR-07) are expensive to retrofit if the storage design is wrong, and in this plan evidence starts being written in Sprint 2.", "High", "Low", "Object-lock write-once storage and DB-level immutability triggers land in Sprint 1 (S1-01, S1-03), before any evidence endpoint exists. QA-4 verifies retention with evidence, not assertion, in Sprint 3.", "DevOps", "Open"),
    ("R-08", "Risk", "Tenant-per-schema migrations get slow and fragile as firm count grows, and the migration runner is exercised many times a day under this cadence.", "Medium", "Medium", "Build the runner for idempotency and parallelism in Sprint 1 and load-test it against 50 synthetic schemas before Sprint 2 opens.", "BE", "Open"),
    ("R-09", "Risk", "Six weeks leaves no recovery sprint. A single lost person-week in Sprint 1 propagates through every dependency in Sprints 2 and 3.", "High", "Medium", "The 28% buffer absorbs roughly one person-week per sprint. Protect Sprint 1 scope absolutely — it is the foundation the other two stand on — and escalate any Sprint 1 slippage at the daily, not at the review.", "PM", "Open"),
    ("A-01", "Assumption", "Development is executed by Claude Code with the five engineers acting as orchestrators and reviewers, at an average of 2.0 concurrent agent streams each. This is the assumption the whole 3-sprint commitment rests on.", "-", "-", "If the team reverts to hand-writing code, the plan reverts to the 630-person-day, ~15-sprint shape. Treat that as a re-plan, not a slip.", "Tech lead", "Open"),
    ("A-02", "Assumption", "The team is 5 people at 100% allocation to ControlIQ for all 3 sprints. No headcount change is planned or required.", "-", "-", "Any part-time allocation reduces the sprint's stream-day line proportionally; re-plan rather than absorb.", "PM", "Open"),
    ("A-03", "Assumption", "No calendar start date is fixed. All dates are relative to Sprint 1 Day 1.", "-", "-", "Fix the anchor date and re-derive the roadmap; subtract holidays from sheet 8 capacity.", "PM", "Open"),
    ("A-04", "Assumption", "Scope is PRD v9.0, all 165 committed requirement IDs. Any return of the Systems & IT Risk module re-adds roughly 25 person-days.", "-", "-", "Treat a reversal as a change request against a full-scope commitment, which means something else leaves the 3 sprints.", "PM", "Open"),
    ("A-05", "Assumption", "The stack is fixed as per TAB v2.x: Django/DRF/Celery, FastAPI/LangGraph, React/TS, PostgreSQL 16 + pgvector, AWS ECS Fargate. Agent throughput assumes conventional, well-documented framework usage.", "-", "-", "Any stack change invalidates the multipliers as well as the Sprint 1 estimates.", "Tech lead", "Open"),
    ("A-06", "Assumption", "Sosinna's team is available for regulatory content review, golden-set labelling, open-question decisions and UAT throughout all 3 sprints — not only at the end.", "-", "-", "Book the time in Sprint 0. Client availability is the one input no multiplier improves.", "PM", "Open"),
    ("A-07", "Assumption", "AWS is the target cloud with EU-region residency (NFR-03) and the account structure exists or can be created in Sprint 0.", "-", "-", "Confirm account ownership and billing before Sprint 1.", "DevOps", "Open"),
    ("I-01", "Issue", "The payment provider is not selected, yet payment now sits on the Sprint 2 critical path (FR-123, NFR-12) rather than Sprint 3.", "High", "-", "Decide by the end of Sprint 1 week 1. Requirement is a hosted checkout or hosted fields so no card data touches ControlIQ. Sandbox credentials are needed before S2-05 opens.", "PM", "Open"),
    ("I-02", "Issue", "The client's Word/PDF report template (FR-60) has not been supplied, and reporting is now in Sprint 3 rather than Sprint 7.", "High", "-", "Needed by the end of Sprint 2. Without it, S3-04 builds to a house template and re-skins later, which is rework the window cannot absorb twice.", "PM", "Open"),
    ("I-03", "Issue", "The headless CMS for the marketing site is undecided (Sanity vs Payload), and the site is now in Sprint 3.", "Medium", "-", "Decide by the end of Sprint 2. The enquiry form contract (SA-16) is CMS-independent, so S3-09 can start against a stub if the decision runs late.", "FE", "Open"),
    ("I-04", "Issue", "FR-111 (request portal) is marked PROPOSED and not approved for scope. It is excluded (OS-01) but adjacent Sprint 3 work assumes the exclusion holds.", "Medium", "-", "Get an explicit in-or-out decision before Sprint 2 planning. Adding it costs roughly 6 person-days and something else leaves the window.", "PM", "Open"),
    ("I-05", "Issue", "PRD v9.0 withdrew Section 11 and retired FR-72 to FR-77, but the tech-spec set is not re-baselined. Agents briefed off stale specs will build withdrawn scope.", "High", "-", "Update Security_Architecture.md (seven system roles), Domain_Model, Database_Architecture (IT systems tables) and the Cross-Document Traceability Matrix in Sprint 0, before any agent brief cites them.", "Tech lead", "Open"),
    ("I-06", "Issue", "The tech-spec set commits to schema-per-tenant (ADR-005, TAB s16) while the WSP research blueprint rejects it in favour of shared-schema RLS. Database_Architecture.md also cites it as ADR-004.", "Medium", "-", "Settle in Sprint 0. S1-03 builds the tenancy model and everything else sits on it; this cannot be revisited after Sprint 1.", "Tech lead", "Open"),
    ("D-01", "Dependency", "Sprint 2 and 3 both stand on identity, tenancy, audit and the libraries landing in Sprint 1.", "High", "-", "Protect Sprint 1 scope. It is the only sprint with no upstream dependency and the only one whose slippage compounds twice.", "BE", "Open"),
    ("D-02", "Dependency", "Sprint 2 pool generation depends on the regulatory and test libraries published in Sprint 1 (S1-05).", "High", "-", "Keep S1-05 ahead of the Sprint 1 frontend work; the Portal authoring UI can build against a stub if needed.", "BE", "Open"),
    ("D-03", "Dependency", "Sprint 3 findings, reporting and dashboards all depend on completed test executions from Sprint 2 (S2-07, S3-02).", "High", "-", "Freeze the execution and evidence contracts by the end of Sprint 2 week 1 so the Sprint 3 streams can be briefed against them.", "BE", "Open"),
    ("D-04", "Dependency", "WSP mapping UI (S2-13) depends on the AI mapping output contract (S2-09) being frozen early in Sprint 2.", "Medium", "-", "Freeze the response schema in Sprint 2 day 2 so the frontend agent stream builds against a stub rather than waiting.", "AI", "Open"),
    ("D-05", "Dependency", "Evidence upload work depends on the write-once bucket configuration (S1-01, S2-01).", "Medium", "-", "DevOps delivers the bucket policy before any evidence endpoint is written.", "DevOps", "Open"),
    ("D-06", "Dependency", "Golden-set labelling depends on client domain-expert availability and gates the AI regression thresholds.", "Medium", "-", "Schedule the sessions in Sprint 1 for use in Sprint 2. This is the one dependency no multiplier shortens.", "PM", "Open"),
]
write_rows(ws, RAID, 3, fills=lambda d: RED if d[3] == "High" else (AMBER if d[3] == "Medium" else None))
ws.freeze_panes = "A3"
ws.auto_filter.ref = f"A2:H{2 + len(RAID)}"

OUT.parent.mkdir(parents=True, exist_ok=True)
wb.save(OUT)
print(f"written: {OUT}")
print(f"sheets: {', '.join(wb.sheetnames)}")
print(f"planned demand: {round(sum(m[8] for m in MODULES), 2)} agent-stream days "
      f"vs {TOTAL_CAPACITY} capacity")
