<!--
  Markdown rendering of PRD.docx (same directory), for readable diffs on GitHub.
  The .docx remains the signed baseline; if the two disagree, the .docx wins.
  This file carries no version in its name — see the version field below, and
  git history for the revision record. Regenerate with scripts/docx2md.py.

  Markdown has no colour, so the document's own annotation legend is encoded as text:
    blue italic   -> trailing `[25 Jun FRD call]` tag
    orange italic -> trailing `[Sosinna's Drive comment]` tag
    grey           -> trailing `[status note]` tag
    green box      -> blockquote headed **CONFIRMED**
    amber box      -> blockquote headed **OPEN QUESTION**
    grey box       -> blockquote headed **DEVELOPER NOTE**
  Feature IDs ([FR-24] etc.) were blue in the source; the brackets already mark them.
  Verified lossless at word level against the .docx: 12,998 tokens, all 94 feature IDs.
-->

**ComplianceIQ**

*by SayOne Technologies*

**PRODUCT REQUIREMENTS DOCUMENT**

| **Field** | **Value** |
|---|---|
| Document | ComplianceIQ — Product Requirements Document (SRS v4.0) |
| Version | 4.0 · June 2026 |
| Prepared by | Jomin Johnson, Delivery Head — SayOne Technologies |
| Prepared for | Sosinna Degefu, Synergy Consulting Group / FinTech House Lisbon |
| Status | v4.0 — gap audit complete; 11 workflow gaps documented for pre-sprint resolution |
| Regulations covered | MiCA (EU 2023/1114) and DORA (EU 2022/2554) |
| Built for | Crypto Asset Service Providers (CASPs) licensed in the EU |

> **NOTE** *(blue)*
>
> **🗂 Annotation Legend — added 3 Jul 2026**
> - Version and status fields above are unchanged — this remains PRD v4.0, per the signed baseline.
> - **Blue italic text** = answer sourced from the 25 Jun 2026 FRD Review call (Fathom recording). `[25 Jun FRD call]`
> - **Orange italic text** = answer or addition sourced from Sosinna's comments on the Google Doc. `[Sosinna's Drive comment]`
> - Existing green (agreed) / amber (open question) / grey (note) boxes are unchanged conventions from earlier versions.

# How to Read This Document

This document describes everything ComplianceIQ is being built to do. It is written for three audiences at the same time:

| **Reader** | **What to focus on** |
|---|---|
| Sosinna (domain expert, client) | The plain-English feature descriptions. If something doesn't match your vision or you think something is missing, note it down — every section ends with open questions. You don't need to read the grey developer notes. |
| UI/UX designers | The workflow sections and role descriptions. These explain who does what, in what order, and what they need to see on screen at each point. |
| Developers and estimators | The feature IDs in blue (like [FR-24]) are the individual items to estimate. The grey developer notes flag technical decisions. Everything else gives you the context for why a feature exists. |

> **📌 Note**
> - Some technical terms appear in this document — for example, 'multi-tenant architecture' or 'OCR'. Each one is explained in plain English the first time it appears.
> - Confirmed decisions are shown in green boxes. Open questions are in yellow boxes. Everything else is agreed and in scope.
> - Feature IDs like [FR-24] or [SA-02] are reference tags for the development team. They do not affect the reading.
> - New: blue text marks answers from the 25 Jun call; orange text marks answers from Sosinna's Drive comments. See the legend on the title page.

# 1. What Is ComplianceIQ?

ComplianceIQ is a software platform that helps crypto companies stay on the right side of European financial regulation. It is built specifically for Crypto Asset Service Providers — companies that are licensed by a national financial regulator (such as the Banco de Portugal or the BaFin in Germany) to offer services involving crypto-assets.

Right now, most compliance work at these companies happens in spreadsheets, shared drives, and email threads. Testing is done manually. Evidence is scattered. Reports are produced by consultants at high cost and low frequency. If a regulator asks to see proof of compliance, pulling it all together takes weeks.

ComplianceIQ replaces that with a single, structured platform where the compliance team can plan tests, run them step by step, store evidence, record what they found, agree on how to fix problems, and produce a professional report — all in one place, continuously, not just at audit time.

The platform is built around two major EU regulations:

- MiCA (Markets in Crypto-Assets Regulation, EU 2023/1114) — the main licensing and conduct regulation for crypto companies operating in Europe.
- DORA (Digital Operational Resilience Act, EU 2022/2554) — the regulation that governs how financial firms manage their IT systems, deal with IT incidents, and oversee third-party technology providers.

ComplianceIQ is a B2B SaaS product. 'B2B' means it sells to businesses, not individuals. 'SaaS' (Software as a Service) means it runs in the cloud and is accessed through a web browser — there is nothing to install. Each client company pays a subscription fee to use it.

## 1.1 The Two Parts of the Platform

ComplianceIQ is made up of two separate but connected applications:

| **Application** | **Who uses it** | **What it is for** |
|---|---|---|
| The Firm Application | The compliance team at each crypto company (CCO, compliance officers, senior management, IT staff) | The day-to-day compliance platform. Running tests, managing findings, tracking remediation, generating reports. |
| The Platform Admin Portal | Sosinna's team at Synergy Consulting Group | The back-office tool where the compliance testing library is built and maintained. This is where test procedures are written, regulation changes are tracked, and client firms are managed. |

> **📌 Note**
> - The Platform Admin Portal is in scope for the initial build. Without it, there are no tests for firms to run.
> - The Portal is not visible to any firm's users. It is a separate login, separate interface, used only by Sosinna's team.
> - The compliance testing content in the Portal — the test procedures, the requirement IDs, the evidence checklists — is the core intellectual property of ComplianceIQ.
> - ***See Section 14, CC-03 for the full, now-confirmed IP ownership terms — the scope is broader than just this content.*** `[Sosinna's Drive comment]`

## 1.3 Marketing Website & Subscription Entry Point

***NEW — added following the 25 Jun FRD Review call, approved for scope by Jomin (3 Jul 2026)*** `[25 Jun FRD call]`

This was not part of earlier versions of this document. It surfaced as a gap during the FRD Review call: the platform needs a public-facing marketing website that introduces ComplianceIQ before a firm ever reaches the onboarding wizard in Section 5.

**[MKT-01]** A public marketing website introduces ComplianceIQ, explains the two-application structure at a high level, and describes the two indicative plan types (Enterprise vs. seat-based) without publishing fixed prices.

**[MKT-02]** The marketing site does not process payment or plan selection directly. There is no self-serve checkout. **📞 From the 25 Jun FRD Review call:** *Confirmed on the call — pricing is sales-assisted, not self-serve. Every prospective firm goes through a demo and scoping conversation with Sosinna's team before an account is created (see Section 14, CC-01). The site's job is lead capture — a 'request a demo' flow — not a shopping cart.* `[25 Jun FRD call]`

**[MKT-03]** Once a firm is qualified and a plan is agreed off-platform, Sosinna's team (or Jomin's team during onboarding support) creates the account and the firm proceeds through the Section 5 setup wizard.

> **OPEN QUESTION** *(amber — unresolved)*
>
> **💬 Questions still to confirm**
> - Hosting / CMS (MKT-04): should this be a simple static site, or does it need a CMS Sosinna's team can edit without a developer?
> - Domain (MKT-05): does this live on a SayOne-managed domain, a Synergy-owned domain, or the eventual ComplianceIQ product domain? Ties into the CC-02 branding question below.

# 2. The Data ComplianceIQ Stores

ComplianceIQ is the permanent record of a firm's compliance activity. This is important: regulators can ask a firm to produce evidence of their compliance programme going back years. Everything the platform stores must be kept securely, and most of it cannot be deleted.

Here is what the platform stores, and for how long:

| **What we store** | **Why** | **How long** |
|---|---|---|
| Firm profile | Jurisdiction, licence number, services offered, client base. This drives which tests the firm needs to run. | Kept for as long as the firm is a client |
| Regulatory requirement IDs and test procedures | The library of tests the firm runs — built and maintained by Sosinna's team. Not fixed: these are updated as regulations change. | Full history of every version kept forever |
| Test executions | A record of every test the firm has run: who ran it, when, what steps they completed, what they found. | Minimum 6 years |
| Test results | The formal outcome of each test — Pass, Fail, or Observation — with supporting rationale. | Minimum 6 years, and cannot be changed once signed off (only an amendment can be added on top) |
| Evidence files | Every document, screenshot, audio recording, video, spreadsheet, or other file uploaded as proof during a test. | Minimum 6 years, cannot be deleted by anyone |
| Sampling records | For tests that check a sample of transactions or records: how big the full set was, how many were checked, and why those specific ones were chosen. | Minimum 6 years |
| Findings | Every compliance issue identified during testing: what the problem is, how serious it is, which regulation it relates to, and what the root cause was. | Minimum 6 years |
| Remediation action items | The specific tasks assigned to fix each finding: who is responsible, when it is due, and what was done. | Minimum 6 years |
| Remediation evidence | The files uploaded to prove a fix has been implemented. | Minimum 6 years, cannot be deleted |
| Compliance reports | The formal reports generated at the end of each testing cycle. | Minimum 6 years, cannot be changed after they are issued |
| Staff records | The firm's employee list, their roles, their qualifications, their hardware, their place in the emergency contact chain. | Kept for the duration of employment plus retention period |
| Audit log | A complete, tamper-proof record of every action any user takes in the platform: what they did, when, from which device. | Minimum 6 years, cannot be modified by anyone |
| Notification log | A record of every alert the platform sent, to whom, and whether it was acknowledged. | Minimum 6 years |

> **🔧 For the development team**
> - All data encrypted at rest using AES-256 (a standard military-grade encryption method) and in transit using TLS 1.3. Evidence files stored in encrypted object storage with per-tenant encryption keys.
> - EU data residency required for all client data — EU data centres only.
> - ***Cloud provider and account ownership now confirmed — see Section 13, TI-01: AWS, EU-resident data centre, on an account owned solely by the Client.*** `[Sosinna's Drive comment]`
> - Multi-tenant architecture (each firm's data lives in a completely separate data partition — no firm can ever see another firm's data) from day one.
> - Audit log is immutable — append-only. No admin-level delete or modify capability.

# 3. Who Uses the Platform and What They Can Do

Everyone who uses ComplianceIQ has a role that determines what they can see and what they can do. There are two levels of roles:

- System roles — defined by SayOne and built into the platform. These carry fixed permissions. They cannot be changed by any firm.
- Firm roles — custom names that each firm creates to match their own job titles (for example, 'AML Analyst' or 'Head of IT'). Each firm role is linked to one system role, and that linkage determines the actual permissions.

This means a firm can call their roles whatever they like, but the underlying access rules are always controlled by the platform. For example, a firm might call someone 'VP of Compliance' — they link that title to the 'CCO / Compliance Manager' system role, and that person automatically gets CCO-level access.

## 3.1 The Eight System Roles

| **Role** | **Has login?** | **What this person can do** |
|---|---|---|
| Platform Super Admin (Sosinna's team) | Yes | Manages all regulatory content, builds test procedures, configures the platform globally. Works in a separate administration portal that firm users never see. |
| Firm Super Admin | Yes | Sets up the firm's account, invites users, creates custom job title roles, and manages firm settings. Each firm must always have at least two of these. |
| CCO / Compliance Manager | Yes | The most important role in the firm-side application. Assigns tests to compliance officers, reviews and approves all test results, initiates thematic or selective reviews, closes findings, and generates the final report. |
| Compliance Officer (Lead Tester) | Yes | Carries out tests day to day. Works through the test steps, uploads evidence, records what they found, and logs any issues. Cannot approve their own work — that always goes to the CCO. |
| Senior Management | Yes | Read-only access to dashboards and reports. Receives escalation alerts when a serious issue is found. Provides formal sign-off at the end of a testing cycle. |
| Remediation Owner | Yes | Receives action items when a compliance problem needs to be fixed. Sees only their own assigned tasks, updates the progress status, and uploads proof that the fix has been done. |
| IT / Systems Admin | Yes | Access limited to the Systems & ICT Risk section. Manages the inventory of IT systems and records any serious IT incidents. Cannot see compliance tests or findings. |
| Staff / Employee (no login) | No | Any team member who does not need to use the platform but still needs to appear in the org chart, BCP contact list, or Fit & Proper records. They are tracked in the system but cannot log in. |

## 3.2 How Firms Create Their Own Role Names

The Firm Super Admin (think: the person responsible for setting up the firm's account) can create as many custom job titles as they need. Each one must be mapped to a system role. The platform then uses that mapping to control access.

Example mapping:

| **Firm's custom role name** | **Maps to system role** | **What they can do** |
|---|---|---|
| Chief Compliance Officer | CCO / Compliance Manager | Full compliance access |
| AML Analyst | Compliance Officer (Lead Tester) | Runs tests, uploads evidence |
| Board Director | Senior Management | Read-only, receives alerts, approves reports |
| IT Security Manager | IT / Systems Admin | ICT risk module only |
| Risk & Controls Manager | Remediation Owner | Manages their assigned action items |

## 3.3 Access Requirements

**[FR-09]** Every user can only see and do what their role allows. This is enforced automatically by the platform — it is not up to individual users to self-police.

**[FR-10]** The Firm Super Admin can create, rename, and deactivate custom firm roles at any time. Deactivating a role does not lock out existing users immediately — the admin needs to reassign them first.

**[FR-11]** Every user logs in with an email address and password, plus a second verification step on their phone (this is called MFA, or multi-factor authentication — it means a stolen password alone is not enough to get in).

**[FR-12]** New users are added by invitation only. The Firm Super Admin sends an email invite. The new user sets up their account. The Super Admin assigns their role before they can access anything.

**[FR-13]** Every action any user takes is permanently recorded in an audit log — what they did, when, and from which device. This log cannot be altered or deleted by anyone, including administrators. It exists precisely to prove, to a regulator if needed, that the compliance process was followed correctly.

**[FR-14]** When a user leaves the firm, an admin deactivates their account. Everything they ever did in the platform stays in the system — tests, findings, uploads, approvals. Nothing is lost. **💬 Sosinna's comment:** *Any reassignment of that user's open work must be documented with reasoning (e.g. termination, transfer) and kept in an immutable audit trail. See GAP-11 in Section 16.* `[Sosinna's Drive comment]`

**[FR-15]** Each firm must always have at least two Firm Super Admins. If the account drops to one, the platform warns the remaining admin to add a second. This prevents a firm from being locked out if one admin leaves.

# 4. The Platform Admin Portal — Sosinna's Team

The Platform Admin Portal is the control centre for the compliance testing content. It is where Sosinna's team at Synergy Consulting Group builds and maintains the tests that every firm on the platform runs. This portal is completely separate from what firms see — a firm user logging into ComplianceIQ has no idea this portal exists.

The most important thing to understand about this portal is that the compliance tests are not hardcoded or fixed. The regulations they are based on — MiCA and DORA — are live, evolving legal texts published by the European Commission, the EBA (European Banking Authority), and the ESMA (European Securities and Markets Authority). When the regulators publish an update, the tests may need to change. The Portal is how those changes are made and pushed out to all firms.

## 4.1 Building and Managing Tests

**[SA-01]** Each compliance test in the platform is based on a Requirement ID — a short code that maps to a specific obligation in MiCA or DORA. For example, TM-01 maps to the transaction monitoring obligations under MiCA Art. 92. These IDs are not permanent: as the regulations evolve, new ones can be added, existing ones can be updated, and old ones can be retired. Sosinna's team manages this library through the Portal.

**[SA-02]** For each Requirement ID, Sosinna's team builds the step-by-step test procedure: the exact sequence of steps a compliance officer follows, what documents they need to collect at each step, whether they need to test a sample of transactions or review everything, and what the minimum sample size is. When a procedure is updated, a new version is created — the old version is never deleted.

**[SA-03]** The platform automatically watches the official publication pages of EUR-Lex, the EBA, the ESMA, and key national regulators for changes to the MiCA and DORA rules. When a change is detected, the Portal alerts Sosinna's team to review the affected tests before any update is pushed out to firms.

**💬 Sosinna's comment (already incorporated into scope):** *the Portal must also feature a structured manual input interface so the Client's team can enter regulatory changes by hand. Automated monitoring for the MVP is strictly limited to standard RSS feeds or official public API alerts from EUR-Lex, the EBA, and ESMA — no custom HTML web-scraping or brittle layout-parsing engines. Jomin acknowledged this on the doc ("Noted").* `[Sosinna's Drive comment]`

**📞 From the 25 Jun call:** *Sosinna wants the effective date and the date-of-download recorded against every fetched rule, so her team can confirm they're looking at the most recent version. If the API detects something new, her team gets an alert and confirms before it's published to firms — same human-in-the-loop pattern as SA-04.* `[25 Jun FRD call]`

**[SA-04]** Every change to a test procedure goes through a review step before it is published. Once published, firms are notified. Any firm that is currently mid-way through running that test continues with the version they started — they are not interrupted by the update.

## 4.2 The Sampling Methodology Library

Many compliance tests do not check every single transaction or record — they check a representative sample. The methodology used to select that sample matters: it needs to be defensible to a regulator. The Portal contains a library of pre-approved sampling methodology descriptions — plain-language explanations of how the sample was selected — that compliance officers can choose from when running a test.

Examples of methodologies in the library:

- Random statistical sampling — records are selected at random, with no judgement applied
- Risk-based judgement sampling — records are selected because they appear higher risk (for example, high-value transactions or flagged customers)
- Full population review — every single record is checked (used for small populations or critical tests)
- Stratified sampling — the population is divided into groups and a sample is taken from each group

**[SA-05]** The sampling methodology library is managed by Sosinna's team in the Portal. New methodologies can be added, existing ones can be edited, and guidance notes can be attached to each one. When a compliance officer runs a test, they select the methodology that best fits what they are doing — they do not write their own description from scratch.

## 4.3 Client Firm Management

**[SA-06]** The Portal shows a list of all registered firms: their name, jurisdiction, the services they offer, and when they last used the platform. Sosinna's team can see this overview but cannot access any firm's actual compliance data, test results, or findings — those belong to the firm. **📞 From the 25 Jun FRD Review call:** *This visibility boundary needs re-confirming — see the open question added below; Sosinna leaned toward wanting to see "pretty much everything" for MVP, which is broader than this paragraph currently states.* `[25 Jun FRD call]`

**[SA-07]** The Portal handles the configuration of which Requirement IDs apply to which service lines. When a firm uploads their revenue source file and their service lines are identified, the platform uses this configuration to automatically load the right set of tests for that firm.

**[SA-08]** System-wide settings are managed here: the list of approved evidence file types, the minimum sample rates for different test types, the regulation monitoring sources, and the notification schedules. **📞 From the 25 Jun FRD Review call:** *Add: month-end usage reporting (active users vs. subscribed seats, per firm) inside the Portal — but only for the specific data points each onboarded firm agrees to share. Firms won't want their uploaded evidence itself visible to the Portal team; this needs to be spelled out in the client agreement (an NDA-style visibility clause), not built as a granular in-platform toggle for MVP.* `[25 Jun FRD call]`

> **OPEN QUESTION** *(amber — unresolved)*
>
> **💬 Questions still to confirm**
> - **Portal visibility of firm data (new — from the 25 Jun call): should Sosinna's team see firm-level usage stats (active users, tests run) by default, formalised through the client agreement, or should this be a configurable toggle per firm? Bisrat's view was that toggles add complexity SayOne should avoid for MVP — default to visible, cover it contractually instead.** `[25 Jun FRD call]`

# 5. Setting Up a New Firm on the Platform

When a new crypto company joins ComplianceIQ, they go through a guided setup process — called a wizard — that walks them through everything the platform needs to know about their business. This setup is critical: the answers determine which compliance tests the firm needs to run. Getting it wrong means the wrong tests get loaded.

The wizard takes the firm through these steps in order:

| **Step** | **What the firm enters** | **Why it matters** |
|---|---|---|
| Legal details | Full legal name, registered address | Used on every report the platform generates |
| Regulator licence | Licence number (typed in) and optionally the licence document itself (uploaded as a file) | The licence number appears on report cover pages and triggers an annual licence review reminder |
| Home jurisdiction | Which EU country issued their CASP licence | Determines which national regulator's rules apply on top of base MiCA |
| Branch jurisdictions | Any other EU countries where they have offices or operate | Layers additional local rules on top of the base MiCA requirements |
| Revenue source file | An Excel file using the platform's template, showing the firm's revenue by business line | This is how the platform determines which CASP service lines the firm operates — which in turn determines which tests they need to run |
| Service line confirmation | A review screen showing the service lines the platform derived from the revenue file | The CCO confirms the derived service lines before tests are loaded |
| Client base | Whether the firm serves retail clients, institutional clients, or both | Relevant to the suitability and appropriateness tests and the AML risk approach |

> **📌 Note**
> - The firm does not manually tick a list of service lines. The platform reads the revenue source Excel file they upload and works out the service lines from that. The firm then confirms the result looks correct.
> - This revenue file is the platform's template — found in the onboarding section. The firm fills it in and uploads it. They can re-upload it any time their business changes.
> - If a firm adds a new service line later (for example, they start offering portfolio management), they upload a new revenue file. The platform detects the new service line and automatically loads the additional tests that come with it.
> - ***Service line list source: the DORA A–H activity list is maintained centrally at Super Admin level, is the same across every EU jurisdiction (one EU rule, not state-specific), and can be extended later as SayOne scales beyond crypto (e.g. non-crypto broker-dealers). Selection can't be fully automated 1:1 from the revenue file — a single revenue line can span two service lines — so the firm still confirms manually, guided by an informational pop-up ("what does your licence say?"). Sosinna is sourcing a sample regulatory line-item report (the EU equivalent of a US Form 1040) for the dev team to model the revenue template against.*** `[25 Jun FRD call]`
> - ***Multi-jurisdiction handling: for MVP, testing runs at the entity holding the EU licence (headquarters) — branch-level testing is not required for EU-only branches. The architecture should be built to eventually ingest non-EU rule sets (e.g. UK post-Brexit, or non-EU sectors entirely), but this must not be exposed in the UI for MVP — it's a later-phase toggle.*** `[25 Jun FRD call]`

**[FR-01]** Firm registration captures: legal name, registered address, home jurisdiction, and licence details.

**[FR-02]** NCA licence is captured as both a typed licence number and an optional uploaded PDF of the licence document itself.

**[FR-03]** Home jurisdiction and branch jurisdictions are both captured during setup.

**[FR-04]** The firm uploads their revenue source Excel file using the platform's template. The platform reads it to identify active service lines. **💬 Sosinna's comment:** *The onboarding process is what determines which rules and tests apply — a wallet-custody-only firm gets a much smaller test set than a full trading platform serving retail and institutional clients. Getting this mapping accurate is a governance priority, not just a convenience feature.* `[Sosinna's Drive comment]`

**[FR-05]** After processing the revenue file, the platform shows the CCO the derived service lines for confirmation. If something looks wrong, they re-upload a corrected file.

**[FR-06]** Client base composition (Retail / Institutional / both) is captured.

**[FR-07]** The platform automatically loads the correct Requirement IDs and testing schedule based on the confirmed service lines.

**[FR-08]** The firm can update their profile at any time — for example, after a business change. Uploading a new revenue file triggers a recalculation of applicable tests.

|   |
|---|
| **✅ What we have agreed** <br> • Service lines are derived from the revenue source Excel file — not from a manual selection screen. <br> • NCA licence: the firm provides both the licence number (text) and optionally the licence document (file upload). <br> • The onboarding flow is a step-by-step wizard. <br> • Branch jurisdictions are captured and affect which local regulatory rules apply. |
| **💬 Questions still to confirm** <br> • Client type (FO-02): Should this be a simple set of checkboxes (tick: Retail, Institutional, Non-Profit) or should the firm enter a percentage split (e.g. 60% Retail, 40% Institutional)? <br> • Who completes the setup (FO-07): Can any Firm Super Admin complete the onboarding, or should this be restricted to the CCO? <br> • Multi-entity firms (FO-08): If a company has multiple regulated subsidiaries (e.g. a parent group with separate CASPs in Ireland and France), do they get separate logins for each entity, or one group login with a consolidated view? [Deferred — not needed for the first version] |

# 6. Written Supervisory Procedures (WSP)

A Written Supervisory Procedure — WSP for short — is the firm's internal compliance manual. It describes, in the firm's own words, the policies and procedures they have in place to comply with each regulation. Regulators expect firms to have these procedures written down and kept up to date.

The WSP module in ComplianceIQ serves three purposes: it stores the firm's compliance manual, it checks that the manual actually covers all the rules the firm needs to comply with, and it alerts the firm when the manual needs to be updated because a regulation has changed.

## 6.1 Uploading the WSP

**[FR-30]** The firm uploads their entire compliance manual as a single document — not section by section. The platform accepts standard Word documents (.docx) and PDFs. It also accepts scanned PDFs (a scanned PDF is a photograph of a physical document — the platform uses OCR, which stands for Optical Character Recognition, to read the text from the scan automatically).

## 6.2 AI-Assisted Rule Mapping

Once the document is uploaded, the platform uses artificial intelligence to read through it and suggest which regulations each section of the manual is addressing. For example, it might suggest that pages 12–15 cover the firm's transaction monitoring obligations under MiCA Art. 92.

**[FR-31]** The AI suggestions are a starting point only — not a final determination. A compliance officer reviews each suggestion and either confirms it or adjusts it. The AI makes the process faster; the human makes the final call.

**💬 Sosinna's comment (accepted by Jomin, 3 Jul 2026):** *the AI-assisted mapping feature must achieve a minimum verified accuracy rate of 85% against pre-defined verification text vectors during UAT. All the work to hit and maintain that bar — prompt engineering, vector database indexing, algorithmic tuning — is inside the initial fixed-fee scope. It does not trigger additional development cost. This supersedes the note below, which previously left accuracy entirely up to SayOne's internal judgement.* `[Sosinna's Drive comment]`

> **DEVELOPER NOTE** *(grey)*
>
> **📌 Note**
> - *Superseded — kept for context only: this note previously said the acceptable accuracy rate was an internal SayOne decision, not something Sosinna's team needed to weigh in on. That is no longer the case — see the accepted 85% UAT threshold above.*

## 6.3 Sign-Off on Every Mapping

**[FR-32]** Before any rule mapping is confirmed — or changed — two senior people at the firm must independently approve it. The person who wrote the policy cannot be one of the two approvers. This two-person sign-off rule is there to prevent any single person from unilaterally confirming that the firm's manual is compliant when it may not be.

**[FR-33]** If a previously confirmed mapping is reversed — meaning a section of the manual is untagged from a rule it was previously mapped to — the same two-person approval process applies. The reversal, the two approvers, and the date are permanently recorded.

**💬 Sosinna's comment (GAP-09 answer):** *the mapping should re-run automatically whenever a new WSP version is uploaded and correctly labelled — it shouldn't rely on someone remembering to re-map. Manual override of an automatic mapping is allowed, but any manual change must carry a visible tag flagging that it was a human override, not an AI or system-generated mapping.* `[Sosinna's Drive comment]`

## 6.4 Gap Analysis

**[FR-34]** At any point, the platform shows a real-time gap analysis: which of the firm's required Requirement IDs have a corresponding section in their compliance manual, and which do not. Any gap is flagged on the firm's dashboard as a compliance gap that needs to be addressed.

## 6.5 Staying Up to Date

**[FR-35]** When the Platform Admin Portal detects a change to a regulation that the firm is subject to, the firm is immediately alerted. The specific sections of their compliance manual that were mapped to the affected rule are flagged for review. This review is not deferred to the next testing cycle — it is triggered straight away.

**[FR-36]** Regardless of whether anything changes, the platform triggers an annual review of the entire compliance manual. The CCO and designated approvers sign off that they have reviewed the document and either updated it or confirmed that no changes were needed.

**[FR-37]** Every version of the uploaded compliance manual, and every change to any rule mapping, is kept permanently with a complete version history. Nothing is overwritten.

> **CONFIRMED** *(green — agreed decision)*
>
> **✅ What we have agreed**
> - The firm uploads the complete compliance manual as one document — not section by section.
> - Scanned PDFs are supported — the platform reads them using OCR.
> - Any mapping, change, or reversal requires two-person sign-off. The policy author cannot be one of the approvers.
> - Regulation changes trigger an immediate alert and WSP review — not deferred to the next test cycle.
> - ***AI mapping accuracy: minimum 85% verified at UAT, tuning included in the fixed fee (accepted 3 Jul 2026).*** `[Sosinna's Drive comment]`
> - ***Re-mapping triggers automatically on new WSP upload; manual overrides are permitted but must be tagged as manual.*** `[Sosinna's Drive comment]`

# 7. Running Compliance Tests

This is the core of the platform. The compliance testing module is where the firm's compliance team actually does the work: running tests, collecting evidence, recording what they find, and feeding results into the reporting process.

Every test the firm runs is based on one of the Requirement IDs built by Sosinna's team in the Platform Admin Portal. The test procedure — the step-by-step instructions — comes from that portal. The compliance team's job is to follow those steps, upload the required evidence, and record an honest result.

## 7.1 The Full Testing Workflow — Step by Step

Here is the complete sequence of events from the moment a test is due to the moment the final report is distributed:

| **#** | **Who** | **What happens** |
|---|---|---|
| 1 | Platform | The platform's testing calendar automatically schedules all regulatory tests based on the firm's active Requirement IDs and their required frequencies — some tests happen every month, some every quarter, some once a year. The CCO can also manually create additional one-off reviews at any time. |
| 2 | CCO | The CCO assigns each test to a Compliance Officer — their Lead Tester. This is a formal step. The Lead Tester receives a notification and cannot start the test without this assignment. |
| 3 | Lead Tester | The Lead Tester opens the assigned test and works through it step by step. Each step shows what to do and what evidence to collect. The Lead Tester records their observation at each step and uploads the relevant files. Other team members (for example, the IT manager) can upload specialist evidence to specific steps, but only the Lead Tester records the formal findings. |
| 4 | Lead Tester | Where the test involves checking a sample of records (for example, reviewing a selection of KYC files rather than every single one), the Lead Tester records: how many records exist in total, how many were selected, how they were selected, and which sampling methodology from the platform's library they used. The platform enforces a minimum sample size. |
| 5 | Lead Tester | Evidence is uploaded during the test. This can be any type of file — a PDF, a screenshot, an Excel export, an audio recording, a video, a screen recording, a ZIP archive of files. All uploads are non-deletable and permanently linked to the test. |
| 6 | Lead Tester | Some tests can be run in partial scope — for example, testing only the KYC segment of the onboarding obligations in one quarter and the UBO (Ultimate Beneficial Owner) refresh in the next. The Lead Tester documents the scope at the start, and the platform tracks which parts of each Requirement ID have been covered across testing periods. |
| 7 | Lead Tester | Once all steps are complete, the Lead Tester records the overall result: Pass (everything is in order), Fail (something is non-compliant), or Observation (something needs attention but is not yet a breach). |
| 8 | Lead Tester | For every Fail or Observation, the Lead Tester creates a Finding. Each Finding is independent — one test can produce multiple Findings, each with its own description, seriousness rating, the specific regulation article it relates to, and a root cause category (for example: Process Gap, Control Failure, Missing Documentation, System Issue, or Training Gap). |
| 9 | Lead Tester / CCO | For each Finding, a remediation plan is created: a description of the corrective action needed, one or more milestones, each with a due date and a Remediation Owner assigned from the platform's registered users. The Remediation Owner is notified immediately. |
| 10 | CCO | The CCO reviews the entire test, all the Findings, and all the remediation plans. The CCO can send it back to the Lead Tester for corrections, or formally approve it. Approval is recorded in the audit log. |
| 11 | AML Officer | For tests involving AML obligations — such as transaction monitoring, customer risk ratings, or sanctions screening — the AML Officer (a Senior Management or CCO-level user) separately reviews and formally agrees to the Findings. This agreement is recorded in the audit log. |
| 12 | CCO | Before the report can be generated, all remediation milestone dates must be confirmed with the Remediation Owners and signed off by the CCO. This locks in the plan. The moment the report is issued, the clock starts running on every milestone. |
| 13 | CCO | The CCO generates the formal risk-based testing report for the testing period. The report includes every test result, every Finding, and the complete confirmed remediation plan. The report is branded with the ComplianceIQ logo. |
| 14 | Senior Management | Senior Management users receive a notification that the report is ready for sign-off. They review it and provide their formal approval within the platform. This sign-off is permanently recorded. |
| 15 | Platform | The signed-off report is automatically sent to the firm's configured email distribution lists. |
| 16 | Remediation Owners / CCO / Senior Management | After the report is issued, each Remediation Owner works through their assigned action items. They update the status as they go and upload evidence when each fix is complete. The CCO monitors all open items on the dashboard. Formally closing a Finding requires sign-off from both the CCO and one relevant Senior Management user — after the CCO has reviewed the Remediation Owner's uploaded evidence. |

**💬 Sosinna's comment:** *she suggested building a flow chart alongside this table to make the end-to-end process easier to follow. Recommend producing this as a companion diagram for the next client-facing review.* `[Sosinna's Drive comment]`

**💬 Sosinna's comment (on step 3, in-progress visibility — GAP-05 answer):** *the test should be accessible to whoever is assigned. Each new contribution should trigger an additional version, tagged to whoever recorded it. If someone is not assigned to the test, they get view-only — and only senior personnel with the right entitlements can view it at all. It is not open for anyone in the firm to browse.* `[Sosinna's Drive comment]`

**💬 Sosinna's comment (on step 1, scheduling — supports GAP-04):** *there should be a calendar for the CCO to schedule tests manually, and if any applicable test hasn't been scheduled, the platform should raise an alert or pending notification flagging that a required control has no scheduled test. New notification added to Section 12.* `[Sosinna's Drive comment]`

## 7.2 Scheduling and Assigning Tests

**[FR-16]** The testing calendar is generated automatically when a firm completes onboarding, and is updated any time their service lines change.

**[FR-17]** Thematic reviews (deep dives into a specific topic) and Selective reviews (tests triggered by a specific event or risk) are not automatically scheduled. The CCO manually creates these when needed.

**[FR-18]** The testing calendar on the dashboard shows every test in the system — whether it is Planned, Ongoing, or Completed — with filters so the CCO can quickly find what they are looking for.

**[FR-19]** Partial testing is supported. The scope of each test execution is documented at the start of the test. The platform tracks which parts of a Requirement ID have been covered across different testing periods.

**[FR-20]** Only the CCO can assign a test to a Lead Tester. A Compliance Officer cannot pick up a test and start it without that formal assignment.

**[FR-21]** Each test has one Lead Tester who is responsible for the formal result. Other team members can contribute evidence to specific steps, but the Lead Tester owns the outcome. Every action is timestamped and linked to the individual who performed it.

**[FR-21b]** If a test is marked Not Applicable — meaning the requirement does not apply to the firm for this period — the Lead Tester or CCO must document the reason before the N/A status can be set. The N/A response is then immutable, timestamped, and permanently retained. It cannot be changed after it is recorded.

**[FR-21c]** If the sample selection needs to be changed after it has been documented and locked at the start of a test, the change requires approval from one other senior team member and a written reason. The original selection is immutably retained in the audit log alongside the change.

## 7.3 Evidence

**[FR-24]** The platform accepts the following evidence file types: PDF, Word documents (.docx), Excel spreadsheets (.xlsx), images (PNG, JPG), audio recordings (MP3, WAV), video recordings (MP4, MOV, AVI), screen recordings, ZIP archives, and CSV data exports. The maximum file size is set by the development team in the platform configuration and can be adjusted without a code change.

**[FR-25]** Before a test begins, the platform generates a structured document checklist — a list of everything the Lead Tester will need to collect during the test. This checklist can be exported as a PDF and shared with the IT team, Finance team, or Legal team so they can gather the required documents in advance.

**[FR-27]** Once a test has been signed off by the CCO, the result is final. If a mistake was made or new information comes to light, the CCO is the only person who can add an amendment. The amendment must include a written explanation of why the result is being changed. The original result is never deleted — it stays in the audit log alongside the amendment.

**[FR-28]** Evidence files have a shelf life. For example, a Business Continuity Plan test report is only valid evidence if it is less than 12 months old. The platform tracks the age of evidence files linked to each test and proactively alerts the CCO and Lead Tester before the next test is due if any evidence is approaching its validity limit.

# 8. Findings and Fixing Problems

When a test uncovers a compliance problem — whether it is a clear breach, a gap in procedures, or something that just needs watching — it becomes a Finding. Every Finding needs to be tracked from discovery through to resolution. This section describes how that tracking works.

## 8.1 How Serious Is It?

| **Rating** | **What it means** | **What happens next** |
|---|---|---|
| High | Three or more findings in a test, OR any single finding that represents a direct breach of a regulation or the complete absence of a required control | The CCO and all Senior Management users are immediately alerted. Under DORA, this may also trigger a formal notification to the national regulator within four hours. The firm has five business days to formally acknowledge the escalation. |
| Moderate | One or two findings where some compensating measures are already in place | The CCO is notified. The issue is tracked to resolution. No immediate escalation to Senior Management. |
| Low | A minor observation — something to improve but not an immediate compliance risk | Recorded in the findings register. Tracked to closure. No escalation. |

## 8.2 Recording Findings

**[FR-38]** All Findings from all tests are collected in a central register. From this register, the CCO can see every open compliance issue across all tests — filtered by seriousness, status, who owns the fix, and which testing period it came from. **💬 Sosinna's comment:** *The overall sequence: all findings are communicated to control owners and management first. Once a consensus is reached on how to proceed, the remediation plan is documented and memorialised in the system with a timeline. See GAP-06 below for the full sequence.* `[Sosinna's Drive comment]`

**[FR-39]** One test can produce multiple independent Findings. There is no limit. Each Finding has its own life — its own seriousness rating, its own remediation plan, its own owner, its own closure.

**[FR-40]** Each Finding is linked to both the Requirement ID (the test it came from) and the specific regulation article it relates to — for example, MiCA Art. 92. This is important for producing regulator-ready reports that map every problem directly back to the legal obligation it relates to.

## 8.3 Fixing Problems — Remediation

For every Finding, the platform creates a remediation plan: a structured set of tasks that will resolve the issue. Each task is assigned to a Remediation Owner — a registered platform user who is responsible for carrying out the fix.

**[FR-41]** A Finding can have multiple remediation milestones if the fix involves several steps. For example, fixing a broken transaction monitoring process might involve: (1) a temporary manual review procedure by end of month, (2) a system configuration change by the following month, and (3) a full re-test by the end of the quarter. Each milestone has its own due date and its own owner.

**[FR-42]** When a Remediation Owner completes a milestone, they upload evidence to prove it — a screenshot, a policy update, a system report. This evidence is permanently stored against the milestone record.

**💬 Sosinna's comment (Remediation Owner visibility — GAP-07 answer, note this widens FR-52's dashboard scope in Section 9):** *the Remediation Owner should have view access to everything, not just their own assigned item. An audit trail must be maintained in case records are deleted. Evidence of completion, or any other remediation record, must be provided back to testers for validation — closing the loop between the Remediation Owner and the Lead Tester.* `[Sosinna's Drive comment]`

**[FR-43]** If a High-rated Finding is recorded, the platform immediately notifies the CCO and all Senior Management users. If the escalation is not formally acknowledged within five business days, it escalates further and appears as a Level 2 Alert on the CCO's dashboard.

**[FR-44]** Each Finding moves through a defined set of statuses: Open → In Remediation → Under Review → Closed. Formally closing a Finding requires two things: the CCO reviews and approves the Remediation Owner's uploaded evidence, and one relevant Senior Management user provides a second sign-off. Both approvals are recorded in the audit log.

**[FR-45]** The person who originally recorded the Finding cannot be one of the two closing approvers.

**[FR-46]** The platform checks whether a similar Finding was recorded in the previous testing period for the same Requirement ID. If so, it flags it as a Repeat Finding — a pattern that regulators treat as a significant concern because it suggests the underlying problem has not been properly addressed.

**[FR-47]** The remediation plan is agreed and confirmed before the report is generated — not after. The moment the CCO generates the report, every remediation milestone clock starts ticking. This is a deliberate design choice: the report is the formal record that the plan has been agreed, not a wish list created after the fact.

**💬 Sosinna's comment (deadline extensions — GAP-08 answer):** *if a remediation deadline passes, the reason must be documented and the deadline can be extended manually — by the CCO or one other Senior role, with a forced field requiring them to justify the extension. Since the testing schedule is methodical, if a deadline is missed the Remediation Owner and tasks should be reassigned rather than left open indefinitely.* `[Sosinna's Drive comment]`

> **CONFIRMED** *(green — agreed decision)*
>
> **✅ What we have agreed**
> - Multiple independent Findings per test, each with their own remediation plan — confirmed.
> - Each Finding is linked to both the Requirement ID and the specific regulation article.
> - Root cause category is required on every Finding (Process Gap / Control Failure / Documentation Missing / System Issue / Training Gap).
> - Closing a Finding requires sign-off from both the CCO and one relevant Senior Management user. The original recorder cannot be one of the two approvers.
> - Remediation plan is agreed and locked in before the report is issued — not after.
> - Issuing the report starts the milestone clocks.
> - Remediation Owners must be registered platform users to attach evidence of completion.
> - Risk rating is calculated automatically by the platform based on finding count and severity — the compliance officer confirms the rating, they do not manually enter it.
> - ***Deadline extensions: manual, by CCO or one other Senior role, with a mandatory written justification. Missed deadlines trigger reassignment.*** `[Sosinna's Drive comment]`
> - ***Remediation Owner sees more than just their own task — full view access, with an audit trail on any deletions.*** `[Sosinna's Drive comment]`

# 9. Reports and the Dashboard

## 9.1 The Dashboard — What the CCO Sees Every Day

The dashboard is the first thing a user sees when they log in. It is designed to answer the question: 'How is our compliance programme right now?' — without needing to open any individual test or report.

**[FR-48]** The home screen shows a set of at-a-glance metric cards. These include, at minimum: how many tests are due this quarter, how many High-rated Findings are still open, how many remediation deadlines have been missed, and how many compliance manual gaps have been detected. More metrics can be added based on the CCO's preferences.

**[FR-49]** The compliance testing section shows all tests in three columns: Planned (not started), Ongoing (in progress), and Completed. Each test card shows the test name, the assigned Lead Tester, the due date, and a progress indicator. The CCO can filter by risk level, regulatory body, or test type. **📞 From the 25 Jun FRD Review call:** *Sosinna specifically wants a visual (pie chart or bar graph) showing counts of tests planned vs. ongoing vs. completed, so the admin can see review status at a glance without opening the calendar.* `[25 Jun FRD call]`

**[FR-50]** The Regulatory Requirements section shows all the Requirement IDs the firm is subject to and their current compliance status — Compliant, Non-Compliant, Pending Review, or Not Applicable. Each rule shows its version history and links to the official regulation document.

**[FR-51]** The regulatory updates panel monitors the official MiCA and DORA publication pages automatically. When a change is detected and published by Sosinna's team, all affected firms are immediately notified, and the update is shown in this panel linked to the specific tests it affects.

**[FR-52]** Each Remediation Owner has their own personal view — a simple list of all the action items assigned to them, with due dates, current status, and the ability to update progress and upload evidence. This is the only compliance view they need.

**⚠ Flag — possible contradiction with Section 8.3:** ***this line says the Remediation Owner's personal view is "the only compliance view they need," but Sosinna's comment on FR-42 (Section 8.3) says Remediation Owners should have view access to everything. Worth resolving which one wins before this goes into a sprint — the dashboard scope for this role is materially different depending on the answer.*** `[Sosinna's Drive comment]`

**[FR-53]** The platform keeps a history of test results by period. The CCO can compare this quarter's results to last quarter's, or last year's, to see whether the firm's compliance position is improving, stable, or getting worse.

**[FR-54]** A live news feed shows recent regulatory announcements, enforcement actions, and fines from sources including the EBA, ESMA, and national regulators — giving the compliance team early visibility of what regulators are currently focusing on. **💬 Sosinna's comment:** *Public regulator sites can seed this — e.g. Banco de Portugal is the primary CASP licensing and AML/CFT supervisor in Portugal, publishing CASP registration updates, internal control reports, and DORA major-incident notifications on its official portal. Useful as a first source, but doesn't fully settle RE-05 (manual curation vs. automated vs. commercial feed) below.* `[Sosinna's Drive comment]`

## 9.2 The Formal Testing Report

At the end of a testing cycle, the CCO generates a formal risk-based testing report. This is the firm's documented record of what was tested, what was found, and what is being done about it. It is an internal document — it is not automatically sent to the regulator. It is designed for senior management and for the firm's files, at the standard required for regulatory inspection.

**[FR-55]** The CCO can only generate the report after two things have happened: the AML Officer has formally agreed to the AML-related findings, and all remediation milestone dates have been confirmed with the Remediation Owners.

**[FR-56]** The report contains these sections in this order: (1) Cover page with the firm's details and the testing period. (2) Why this review was conducted and what was in scope. (3) What the compliance team was looking to verify in each test. (4) What was reviewed — records, systems, documents, communications. (5) The tests performed — for each test, the sampling methodology used, how many records were checked, and what was found step by step. (6) A summary of all Findings with their seriousness ratings and regulation article references. (7) The complete remediation plan with all milestone dates and owners. (8) The senior management sign-off block.

**[FR-57]** Every report is branded with the ComplianceIQ logo and name. Reports are not re-branded with the client firm's own logo.

**[FR-58]** After the report is generated, Senior Management users receive a notification to review and sign off. Their sign-off is recorded in the platform as a permanent, auditable record.

**[FR-59]** Once signed off, the report is automatically sent to the firm's configured distribution lists.

**[FR-60]** Reports can be downloaded as PDFs. **📞 From the 25 Jun FRD Review call:** *Sosinna has a Word/PDF report template to send over — Jomin flagged this as not a blocker, just needs the template attached before the report layout is finalised. Doesn't fully close RP-04 (whether Excel export is also needed) — see Section 15.* `[25 Jun FRD call]`

**[FR-61]** Once a report has been generated and signed off, it is permanently archived exactly as it was. It cannot be changed. If a new issue is found afterwards, it goes into the next testing cycle's report.

|   |
|---|
| **✅ What we have agreed** <br> • Reports are ComplianceIQ-branded — not white-labelled with the client firm's own logo. <br> • The report is an internal document for senior management — it is not designed for direct submission to a national regulator. <br> • The remediation plan is embedded in the report as a confirmed section, agreed before the report is issued. <br> • Reports are immutable once signed off. |
| **💬 Questions still to confirm** <br> • **Report export (RP-04): PDF is confirmed and a template is coming from Sosinna. Word export is likely (for legal team commentary) but not explicitly confirmed; Excel export for data analysis is still undecided.** `[25 Jun FRD call]` <br> • Regulatory news feed (RE-05): Should this be curated manually by Sosinna's team, collected automatically by scanning official websites, or sourced from a commercial regulatory intelligence service? [Public regulator portals like Banco de Portugal are one candidate source — see Section 9.1 — but this doesn't decide the sourcing model.] |

# 10. Organisation and Staff

The Organisation and Staff module is the firm's governance directory. It is not a HR system — the firm will continue to manage HR elsewhere. What this module does is capture the specific governance information that MiCA and DORA require to be documented: who holds which compliance role, whether their qualifications are current, who reports to whom, what communication channels they are approved to use with clients, what hardware they have been issued, and who calls whom in an emergency.

There are two types of records here. The first is Platform Users — team members who have a login to ComplianceIQ. The second is Staff Members — any employee who needs to appear in the org chart, the emergency contact chain, or the qualifications register, but who does not have a platform login and cannot take any action in the system. Both types are tracked here.

## 10.1 Adding and Managing Staff

**[FR-62]** Staff can be added in bulk using a CSV upload (the platform provides the template, which follows the format of the source compliance spreadsheet). They can also be added one at a time manually. Integration with HR systems like Workday is not in scope for the first version.

**[FR-63]** Each staff record captures: name, job title, custom firm role, department, reporting line (who they report to), professional licences and certifications with their expiry dates, the communication channels they are approved to use with clients, the hardware devices they have been issued (device type, serial number, asset tag), and their alternate work location for Business Continuity purposes.

**[FR-64]** A single person can hold multiple roles — for example, in smaller firms it is common for one person to be both the CCO and the Money Laundering Reporting Officer (MLRO). The platform handles this without creating duplicate records.

## 10.2 The Org Chart

**[FR-65]** The platform generates a visual org chart — a proper interactive tree diagram showing who reports to whom — automatically from the reporting line fields in the staff records. The firm does not draw the org chart manually. They add their team members with their manager's name, and the platform builds the chart.

**[FR-66]** The CCO's reporting line is highlighted in the org chart. If the platform detects that the CCO reports to a revenue function (such as Sales or Trading) rather than directly to the Management Body or Board, it flags this as a governance red flag — because MiCA Art. 68(2) requires the compliance function to be independent.

## 10.3 Qualifications and Fit & Proper

**[FR-67]** Professional licences and certifications tracked in the system have expiry dates. The platform sends automatic reminders at 30 days, 14 days, and 1 day before any certification is due to lapse — to the individual, their manager, and the CCO. An expired certification marks the staff member's record as non-compliant in the system.

## 10.4 Communication Channels

**[FR-68]** MiCA requires firms to use only approved, monitorable communication channels when communicating with clients — and to record which channels each team member is using. Each staff record includes an assignment of their approved channels (for example: corporate email, Bloomberg Chat, recorded phone line). If a staff member has no channel assigned, the record is flagged as a compliance gap.

**📞 From the 25 Jun call (OS-02 answer):** *not a fixed platform-wide dropdown. Channel usage varies too much between roles (sales might use 20 different tools; back-office might only use email) to hardcode. Instead: the firm's IT team provides their channel list at onboarding, ingested via bulk CSV. On import, the platform validates entries against that firm-specific reference list and flags mismatches (e.g. "mail" vs "email", a misspelled tool name) so the admin can correct or explicitly override them. This resolves OS-02 in Section 15 below.* `[25 Jun FRD call]`

## 10.5 Hardware and Business Continuity

**[FR-69]** Each staff member's issued hardware is recorded — device type, serial number, and asset tag. This is required for DORA IT risk management.

**[FR-70]** Each staff member is assigned one 'next contact' in the Business Continuity call tree — meaning if an emergency occurs and the firm needs to reach everyone, there is a clear, unbroken chain of contacts. The platform flags if any link in the chain is missing.

## 10.6 Distribution Lists

The CCO configures six email distribution lists — these define who is automatically notified when specific events happen. These lists are managed here rather than in a notification settings screen, because they are governance decisions (who needs to know what) rather than personal preferences.

| **List** | **When it fires** |
|---|---|
| Compliance Testing Reports | When a completed report is issued |
| Regulatory Organisation Responses | When a regulator publishes a report identifying violations that require a formal firm response |
| Regulatory Organisation Requests | When a regulatory body requests records — typically ahead of or during an investigation |
| Remediation Plan Deadlines | When a remediation milestone is approaching or has been missed |
| New Rules or Guidance | When a regulatory update is detected and takes effect |
| Critical System Alerts | When a critical IT system issue starts the four-hour national regulator notification window under DORA |

> **CONFIRMED** *(green — agreed decision)*
>
> **✅ What we have agreed**
> - Staff import uses CSV upload with the platform's provided template. HR system integration is not in scope.
> - The org chart is a visual interactive tree — generated automatically from the staff reporting line data.
> - Both Platform Users (with logins) and Staff Members (governance records only, no login) are tracked.
> - ***Communication channel types are ingested per firm from their IT team via CSV, validated on import with a flag-and-override for mismatches — not a fixed platform-wide dropdown.*** `[25 Jun FRD call]`

# 11. Systems and IT Risk

The Systems and IT Risk module addresses the firm's obligations under DORA — the regulation that governs how financial firms manage their IT infrastructure. It is used primarily by the firm's IT or Systems Admin team, though the CCO has oversight visibility.

## 11.1 IT System Inventory

**[FR-72]** The firm maintains a complete inventory of all the IT systems it uses — from its core trading platform to its KYC provider, its transaction monitoring system, its sanctions screening tool, and its cloud infrastructure. Categories are drawn from a pre-defined list of standard CASP IT systems (which can be extended). DORA requires every system to be classified as Critical, Important, or Other — the platform enforces this classification and does not allow it to be left blank. **📞 From the 25 Jun FRD Review call:** *The call clarified how monitoring-system data actually enters the platform: no direct API integration to firms' AML/transaction-monitoring systems for MVP. Firms manually upload a CSV extract against a fixed field template SayOne defines — aggregated counts and comparatives only (e.g. how many Level 1/2/3 alerts this month vs. last), explicitly no PII and no individual customer-level data. Direct API integration is a later phase; Sosinna is collecting sample vendor reports (SumSub, Veritas) to help define the CSV template.* `[25 Jun FRD call]`

**[FR-73]** DORA makes an important distinction between two types of critical technology. The first is a Critical or Important Function — a business function within the firm itself that is critical to its operations (abbreviated CIF). The second is a Critical ICT Third-Party Provider — a technology vendor or service provider that is designated as systemically important by European regulators (abbreviated CTPP). These two categories are tracked separately in the platform, because the obligations that come with each are different.

**[FR-74]** All third-party IT vendors are registered with: vendor name, type of service provided, contract reference number, DORA tier classification, and the date the contract is next due for review.

## 11.2 When Something Goes Wrong — IT Incidents

**[FR-75]** When a serious IT incident occurs, the firm needs to decide quickly whether it qualifies as a 'major incident' under DORA — because major incidents require notification to the national regulator within a strict timeframe. The platform provides a guided checklist of criteria to help the IT team make this determination. This is not left to individual judgement.

**[FR-76]** If the incident qualifies as major, the four-hour notification clock starts. The platform automatically drafts a pre-filled notification based on the incident details that have been recorded. The CCO reviews it, edits it as needed, and submits it. The platform tracks whether the submission has been made.

**[FR-77]** All Business Continuity Plan and Disaster Recovery test reports are stored in this module and linked to the relevant DORA test procedures.

# 12. Notifications and Alerts

ComplianceIQ is designed to be proactive — it tells people what they need to know before a problem gets worse, not after. Below is the complete list of alerts the platform sends and why.

| **Alert** | **Who receives it** | **When it fires** |
|---|---|---|
| Test due soon | Assigned Lead Tester and CCO | 30, 14, 7, and 1 day before a test deadline |
| Test overdue | Lead Tester first; then CCO if still unresolved | From the moment a test deadline passes without completion — escalating over time |
| High-rated Finding | CCO and all Senior Management users | The moment a High-rated Finding is recorded |
| Escalation unacknowledged | CCO and Senior Management — Level 2 Alert on dashboard | If a High-rated Finding escalation is not acknowledged within 5 business days |
| Remediation action item assigned | The Remediation Owner | When a new action item is assigned to them |
| Remediation milestone overdue | Remediation Owner and CCO | When a remediation milestone deadline passes without completion |
| Certification expiring | The staff member, their manager, and the CCO | 30, 14, and 1 day before a professional certification expires |
| Regulation update published | All users at affected firms | When Sosinna's team publishes an update to a test procedure that the firm uses |
| WSP review needed | CCO and compliance team | When a regulation change affects a mapped section of the compliance manual |
| Evidence approaching expiry | Lead Tester and CCO | When evidence linked to an upcoming test is approaching its validity limit |
| Annual WSP review due | CCO | At the start of the annual WSP review cycle |
| Critical system incident | CCO and Level 2 Alerts list | When a major IT incident is confirmed and the four-hour notification window begins |
| **Required test not scheduled** `[25 Jun FRD call]` | CCO `[25 Jun FRD call]` | *NEW — from the 25 Jun call: if a mandated Requirement ID has no test instance scheduled within its expected period, the platform raises an alert flagging the gap.* `[25 Jun FRD call]` |
| **Outstanding request items (digest)** `[Sosinna's Drive comment]` | CCO (opt-in, weekly) `[Sosinna's Drive comment]` | *NEW — from the 25 Jun call: a weekly digest specifically for items sitting unactioned (e.g. a requested vulnerability-test report nobody has uploaded). This is separate from the general per-item overdue alerts — it targets business-side foot-dragging on deliverables.* `[Sosinna's Drive comment]` |

> **💬 Questions still to confirm**
> - **Channels (NT-01) — RESOLVED on the 25 Jun call:** *email and in-platform only, confirmed as the baseline and the ceiling for MVP. No SMS. Slack/Teams integration wasn't explicitly ruled out but wasn't raised as a requirement either — treat as out of scope for MVP unless it resurfaces.* `[25 Jun FRD call]`
> - **Preferences (NT-02) — RESOLVED on the 25 Jun call:** *configurable at the individual user level, but only for users who actually log in. Distribution-list-only recipients (no login) get no configuration — they always receive. The CCO is accountable for setting the baseline; this was framed explicitly as an accountability exercise, not just a UX nicety.* `[25 Jun FRD call]`
> - **Digest (NT-03) — RESOLVED on the 25 Jun call:** *no general daily/weekly summary of everything. Instead, a weekly digest specifically for outstanding/overdue request items (see the new alert row above), toggleable per firm. Repeated single-item overdue emails remain the escalation mechanism for urgency — the digest is for management visibility, not urgency.* `[25 Jun FRD call]`

# 13. Technical and Security Requirements

This section is primarily for the development team. It describes the non-negotiable technical standards the platform must meet.

## 13.1 Security and Data Protection

**[NFR-01]** Every client firm's data is held in complete isolation from every other firm. This is what 'multi-tenant architecture' means — one shared platform infrastructure, but each firm's data in a completely separate partition. No firm can ever access another firm's data, even accidentally.

**[NFR-02]** All data is encrypted at rest (meaning data stored on disk is unreadable without a decryption key) using AES-256 — a standard used by governments and banks. All data moving between the platform and users' browsers is encrypted using TLS 1.3. Each firm has its own encryption key.

**[NFR-03]** All client data must be stored in EU-based data centres. This is required by GDPR (the General Data Protection Regulation) and expected by the regulators that will be using this platform.

**[NFR-04]** Every action in the platform is permanently recorded in a tamper-proof audit log. Not even the system administrators at SayOne can modify or delete this log. It exists to provide irrefutable proof to a regulator that the compliance process was followed correctly.

**[NFR-06]** The platform is GDPR-compliant as a data processor — meaning SayOne processes personal data on behalf of client firms, under a Data Processing Agreement.

## 13.2 Performance and Availability

**[NFR-05]** Dashboard pages load within two seconds under normal load. The platform supports up to 100 simultaneous users per firm without performance degradation.

**[NFR-07]** All test results, findings, evidence, reports, and audit logs are retained for a minimum of six years. No user — including administrators — can delete them.

**[NFR-08]** The platform targets 99.5% availability (this means it can be down for no more than approximately 44 hours per year). Planned maintenance windows are communicated in advance.

**[NFR-09]** ISO 27001 (the international standard for information security management) and SOC 2 Type II (a US data security standard widely required by enterprise clients) are on the product roadmap. The timeline for achieving these certifications will be agreed with Sosinna's team.

**[NFR-10]** The platform runs in a web browser — Chrome, Firefox, Edge, and Safari on desktop. The browser version should work well enough on mobile for approval sign-offs. There is no dedicated mobile app in the first version.

**[NFR-11]** The maximum evidence file size is a configuration setting managed in the Platform Admin Portal. The development team will set an initial limit based on infrastructure cost modelling, and it can be adjusted without a code release.

> **OPEN QUESTION** *(amber — unresolved)*
>
> **💬 Questions still to confirm**
> - **Cloud provider (TI-01) — RESOLVED:** *AWS, deployed inside an EU-resident data centre, on an account owned solely by the Client (not SayOne). Note the ownership detail — this affects how your infra team provisions and hands over access.* `[Sosinna's Drive comment]`
> - Uptime SLA (TI-02): Is 99.5% availability sufficient, or do clients require 99.9% (approximately 9 hours downtime per year)? [No update from the 25 Jun call.]
> - Security certifications (TI-03): Are ISO 27001 or SOC 2 Type II required by clients as a condition of signing up? [No update.]
> - **API (TI-05) — partial:** *the call reinforced the existing 'later phase' framing — Bisrat suggested exposing an API for firms to build their own integrations eventually, but explicitly flagged it as "maybe not in scope now." Leaning confirms Section 1.2's existing exclusion; not a hard close.* `[25 Jun FRD call]`
> - **Scale (TI-06) — partial:** *no total firm count for Year 1 yet, but user-count guidance emerged: MVP-eligible firms are capped around 50 individuals, with a typical compliance/testing team of around 10 platform users per firm. Enterprise-tier firms (any size, org-chart based) are uncapped. Still missing: total number of firms expected in Year 1.* `[25 Jun FRD call]`

# 14. Commercial Questions

These are not product features — but the answers affect product decisions like pricing tiers, branding, and contract structure. They need to be resolved between Sosinna and SayOne before the build is finalised.

### CC-01 — Pricing model

How will clients be charged?

***Earlier note (Sosinna's Drive comment, 15 Jun):*** *~~a flat monthly SaaS subscription model per tenant.~~* `[status note]`

**📞 Superseded by the 25 Jun FRD Review call — decided by Jomin (3 Jul 2026): go with the call version.** *Not a fixed or self-serve tier. Two plan structures: an Enterprise plan (org-chart based, any number of users) and a smaller seat-based plan (e.g. 1–5, 5–10 users). No price is published to prospects — every signup goes through a demo and scoping conversation with Sosinna's team first, similar to how SumSub sells. The Super Admin portal configures pricing per seat count at onboarding (explicitly not by firm headcount — a firm like KPMG could have thousands of employees but only a handful of platform seats). No fixed number exists yet — Sosinna said directly on the call she doesn't have a definitive figure. The model is confirmed; the exact price points are not.* `[25 Jun FRD call]`

### CC-02 — Platform branding

The reports are ComplianceIQ-branded. What about the platform itself?

*Not resolved — no update from the call or new comments. "presented as a SayOne product" is ruled out (struck through by Sosinna). Still open between "a Synergy Consulting product" and "purely as 'ComplianceIQ'."* `[status note]`

### CC-03 — IP ownership

The test procedures and regulatory content built by Sosinna's team are the core intellectual property of the platform. Who holds the licence to this content?

**💬 Sosinna's comment — ACCEPTED by Jomin (3 Jul 2026):** *IP licence held by Sosinna / Synergy Consulting Group.* `[Sosinna's Drive comment]`

**💬 "Addition to the Note Section" (Sosinna's comment) — ACCEPTED by Jomin (3 Jul 2026):** *"For the avoidance of any doubt, all right, title, and interest in and to this regulatory content, alongside all platform source code, backend architectures, frontend user interfaces, and database schemas built by the Contractor, belong 100% exclusively to the Client from the moment of creation. The Contractor retains zero rights, ongoing claims, or implied licenses to any content or code within the platform."* `[Sosinna's Drive comment]`

### CC-04 — Engagement model

Is this a fixed-price development project, time and materials, a revenue-share arrangement, an equity arrangement, or a combination?

**💬 Sosinna's comment — confirmed, consistent with DH-02 below:** *strict fixed-price milestone contract.* `[Sosinna's Drive comment]`

### CC-05 — Demo Day presentation approach

At the FinTech House Demo Day in Lisbon, is SayOne named MVP Developer presenting alongside Sosinna, or is the product presented as Sosinna's solution with SayOne in the background?

*Not resolved — both options are still marked in the source document with no strikethrough to indicate a choice. No update from the call or new comments.* `[status note]`

### CC-06 — Client contracting

When a CASP firm subscribes to ComplianceIQ, does Sosinna / Synergy act as the reseller, or does the CASP firm contract directly with SayOne?

**💬 Sosinna's comment — confirmed:** *Sosinna / Synergy is the reseller, owning the client relationship and billing them directly. The CASP firm does not contract directly with SayOne.* `[Sosinna's Drive comment]`

> **CONFIRMED** *(green — agreed decision)*
>
> **✅ What we have agreed**
> - ***IP ownership (CC-03): 100% exclusive to Client — regulatory content AND all platform code/architecture/schemas. SayOne retains zero rights. Accepted 3 Jul 2026.*** `[Sosinna's Drive comment]`
> - ***Engagement model (CC-04): strict fixed-price milestone contract.*** `[Sosinna's Drive comment]`
> - ***Client contracting (CC-06): Sosinna/Synergy is the reseller — owns the client relationship and billing.*** `[Sosinna's Drive comment]`
> - ***Pricing model (CC-01): seat-based, two plan tiers, sales-assisted onboarding, no self-serve checkout. Exact price points still pending.*** `[25 Jun FRD call]`

# 15. All Open Questions — Summary

Every open question from the sections above is listed here in one place. The questions marked as 'Needed before estimation' must be resolved before the development team can produce a reliable project estimate. All others can be resolved during the build.

| **Ref** | **Topic** | **Question** | **Needed before estimation?** | **Status (updated 3 Jul 2026)** |
|---|---|---|---|---|
| FO-02 | Setup | Client type: checkboxes or percentage split? | No | ***Open — no update*** `[status note]` |
| FO-07 | Setup | Who completes the setup wizard — any Firm Super Admin or CCO only? | No | ***Open — no update*** `[status note]` |
| FO-08 | Setup | Multi-entity group accounts — one login or separate logins per entity? [Deferred] | No | ***Open — deferred*** `[status note]` |
| OS-02 | Staff | What is the full list of valid communication channel types? | No | ***RESOLVED — see Section 10.4*** `[25 Jun FRD call]` |
| OS-06 | Staff | Non-employee committee members — tracked anywhere in the platform? | No | ***Open — no update*** `[status note]` |
| NT-01 | Notifications | Additional channels beyond email: SMS? Slack/Teams? | No | ***RESOLVED — see Section 12*** `[25 Jun FRD call]` |
| NT-02 | Notifications | Notification preferences: per user or firm-wide? | No | ***RESOLVED — see Section 12*** `[25 Jun FRD call]` |
| NT-03 | Notifications | Real-time alerts plus digest email option? | No | ***RESOLVED — see Section 12*** `[25 Jun FRD call]` |
| RE-01 | Rules engine | Who maintains the regulatory content database ongoing — SayOne, Sosinna's team, or shared? | Yes | ***Still open — estimation blocker*** `[status note]` |
| RE-04 | Rules engine | APIAX jurisdictional rule mapping: first version or later phase? | Yes | ***Still open — estimation blocker*** `[status note]` |
| RE-05 | Rules engine | News feed sourcing: manual curation, automated scraping, or commercial API? | Yes | ***Partial — see Section 9.1. Still open.*** `[25 Jun FRD call]` |
| RP-04 | Reports | Additional export formats beyond PDF: Word and/or Excel? | No | ***Partial — see Section 9.2. Still open.*** `[25 Jun FRD call]` |
| TI-01 | Technical | Preferred cloud hosting provider? | Yes | ***RESOLVED — see Section 13.2*** `[Sosinna's Drive comment]` |
| TI-02 | Technical | Required uptime SLA: 99.5% or 99.9%? | Yes | ***Still open — estimation blocker*** `[status note]` |
| TI-03 | Technical | Security certifications required by clients? | No | ***Open — no update*** `[status note]` |
| TI-05 | Technical | Public API: first version or later phase? | Yes | ***Partial — see Section 13.2. Still open.*** `[25 Jun FRD call]` |
| TI-06 | Technical | Expected number of firms and concurrent users in Year 1? | Yes | ***Partial — see Section 13.2. Still open.*** `[25 Jun FRD call]` |
| CC-01 | Commercial | Pricing model? | Yes | ***Model confirmed — see Section 14. Exact figures still pending.*** `[25 Jun FRD call]` |
| CC-02 | Commercial | Platform branding? | No | ***Open — no update*** `[status note]` |
| CC-03 | Commercial | IP ownership of regulatory content? | Yes | ***RESOLVED — see Section 14*** `[Sosinna's Drive comment]` |
| CC-04 | Commercial | Engagement model? | Yes | ***RESOLVED — see Section 14*** `[Sosinna's Drive comment]` |
| CC-05 | Commercial | Demo Day presentation approach? | No | ***Open — no update*** `[status note]` |
| CC-06 | Commercial | Client contracting: reseller or direct? | Yes | ***RESOLVED — see Section 14*** `[Sosinna's Drive comment]` |

> **DEVELOPER NOTE** *(grey)*
>
> **📌 Note**
> - Four of the six 'needed before estimation' items are still open after this round: RE-01, RE-04, TI-02, and (with only partial movement) TI-05 / TI-06 / RE-05. CC-01's model is confirmed but the number isn't — worth deciding whether that's enough to estimate against or whether it still blocks a final number.

# 16. Gaps to Resolve Before Project Execution

The items below are not open questions about whether a feature is needed — all of them are features the platform will build. They are workflow design gaps: points in the product where we know what the outcome should be, but the exact sequence of steps, the exact rules, or the exact user experience has not yet been fully defined. They were identified through a cross-document audit of the RED v2.0, Narrative v3, and PRD v3.0.

None of these are blockers for producing a project estimate — the estimator can size these features based on their known complexity. However, every item in this list must be resolved and documented before the development sprint that covers the relevant feature begins.

> **DEVELOPER NOTE** *(grey)*
>
> **📌 Note**
> - Items marked with ⚠ have a direct impact on a workflow that touches multiple roles or multiple modules. These should be prioritised for resolution.
> - Items marked with ✏ are smaller UX or edge-case decisions that can be resolved in a short working session.

| **Ref** | **Module** | **Gap** | **Status (updated 3 Jul 2026)** |
|---|---|---|---|
| GAP-01 | Testing — Scheduling | ⚠ The calendar shows when tests are due, but the exact anchor-date logic (calendar quarter vs. 90 days from onboarding; mid-quarter onboarding handling; missed-test shifting) is not yet defined. <br> **💬 Partial answer:** *Sosinna's guidance is that each test area should be covered within the year, with firms free to prioritise sequencing based on their own risk controls. The specific anchor-date mechanics are still undefined.* `[Sosinna's Drive comment]` | Still partially open |
| GAP-02 | Testing — Scheduling | ✏ RES-01 (annual pen test + quarterly vulnerability scan) and BCP-01 (annual BCP drill + semi-annual DR failover) have split frequencies — one ID, two obligations. <br> **💬 RESOLVED:** *treat as different/separate test entries, grouped by ID family (RES-xx = resilience, BCP-xx = business continuity, AML-xx = anti-money laundering, etc.). The scheduler tells the tester which recurrence (annual vs. quarterly) is currently due.* `[Sosinna's Drive comment]` | Resolved |
| GAP-03 | Testing — Scheduling | ✏ RES-02 (advanced resilience testing) applies only to 'significant firms' under DORA. How is significance determined — manual Super Admin flag, or platform-calculated? | Still open |
| GAP-04 | Testing — Execution | ⚠ Does a due test auto-move to 'Ongoing', or does the CCO manually open each testing period? <br> **💬 Mostly resolved:** *there should be a CCO-facing calendar to schedule tests manually — supports the manual-trigger side. New: if a required test isn't scheduled at all, the platform should alert (added to Section 12).* `[Sosinna's Drive comment]` | Mostly resolved |
| GAP-05 | Testing — Execution | ✏ Can other team members see an in-progress test, or is it locked to the Lead Tester until submitted? <br> **💬 RESOLVED:** *accessible to those assigned; each new contribution versions the record and is tagged to the contributor. Non-assigned users get view-only, and only senior personnel with entitlements can view at all.* `[Sosinna's Drive comment]` | Resolved |
| GAP-06 | Testing — Remediation | ⚠ Who drafts the remediation plan (Lead Tester or CCO)? Can a Remediation Owner be assigned before CCO approval? Can the CCO edit the plan during review? <br> **💬 Mostly resolved:** *findings are communicated to control owners and management first; once consensus is reached, the plan is documented with a timeline. An owner and approver are assigned — the firm can assign a responsible group, and the CCO plus one or two others must approve. Still open: whether a Remediation Owner can be assigned pre-CCO-approval, and what happens to that assignment if the CCO rejects the test.* `[Sosinna's Drive comment]` | Mostly resolved |
| GAP-07 | Testing — Remediation | ✏ Does the Remediation Owner see the full Finding and risk rating, or only their own task? <br> **💬 RESOLVED (widens FR-52 — see flag in Section 9.1):** *view access to everything, not just their own item. Audit trail maintained in case records are deleted. Evidence of completion must be provided back to testers for validation.* `[Sosinna's Drive comment]` | Resolved — but creates a contradiction, see Section 9.1 |
| GAP-08 | Testing — Remediation | ✏ Is there a formal extension request flow for missed deadlines, and what happens if a Remediation Owner is deactivated mid-task? <br> **💬 RESOLVED:** *missed deadline requires documentation and can be manually extended by the CCO or one other Senior role, with a forced written justification field. Missed deadlines trigger reassignment of the owner/task.* `[Sosinna's Drive comment]` | Resolved |
| GAP-09 | WSP | ✏ Who can initiate a mapping override — CCO only, or any Compliance Officer with CCO approval? <br> **💬 Partial answer:** *mapping should re-run automatically on a new WSP upload; manual overrides are allowed but must carry a visible manual-change tag. Doesn't specify who is allowed to initiate an override.* `[Sosinna's Drive comment]` | Still partially open |
| GAP-10 | Regulatory Updates | ✏ When a regulation update is published mid-test, does the Lead Tester see a dismissable banner or a persistent notice? Does the system record which rule version the test was run under? | Still open |
| GAP-11 | User Management | ✏ When a user is deactivated, does the platform prompt the CCO to reassign their open items, or leave reassignment as a manual task? <br> **💬 Partial answer:** *any reassignment must be documented with reasoning (e.g. termination, transfer) and kept in an immutable audit trail. Doesn't specify whether the platform force-prompts reassignment or leaves it manual.* `[Sosinna's Drive comment]` | Still partially open |

> **DEVELOPER NOTE** *(grey)*
>
> **📌 Note**
> - GAP-01 and GAP-02 should be resolved together in a single session — they are both about how the scheduler works.
> - GAP-06, GAP-07, and GAP-08 should be resolved together — they are all about the remediation ownership flow.
> - GAP-10 is the smallest gap here and can likely be resolved by the UI designer without a client session.
> - ***6 of 11 gaps are now resolved or mostly resolved. GAP-03, GAP-10, and the remaining pieces of GAP-01/09/11 are what's left before Section 16 can be closed out entirely.*** `[25 Jun FRD call]`

> **NOTE** *(orange)*
>
> **📋 Baseline & IP Terms — Client Confirmation (Sosinna's comment, accepted by Jomin 3 Jul 2026)**
> - **Version supremacy:** *this v4.0 PRD is the final, complete, exhaustive technical baseline for the ComplianceIQ MVP and supersedes all prior BRD, RED, SRS, and Narrative documentation. No engineering choices, database designs, or scope exclusions may be justified by referencing legacy text from earlier versions.* `[Sosinna's Drive comment]`
> - **Dual-application delivery:** *the fixed fee covers parallel development, deployment, and security configuration of both the Firm Application and the Platform Admin Portal, both fully operational as defined by this document's functional requirements.* `[Sosinna's Drive comment]`
> - **Baseline freeze:** *upon formal sign-off of Section 18, this document is completely frozen. No further modifications, workflow adjustments, or structural changes may be initiated by the Contractor without an executed amendment to the master contract. Practical implication: this review needs to be finished and folded in before signature — not after.* `[Sosinna's Drive comment]`

# 17. Document History

| **Version** | **Date** | **What changed** |
|---|---|---|
| v1.0 — BRD | May 2026 | First document. Product concept, regulatory scope (MiCA + DORA), six-module structure. |
| v2.0 — RED v1.0 | May 2026 | Full requirement set across all six modules. 17 MiCA + DORA requirement IDs mapped. All open questions documented. |
| v3.0 — RED v2.0 | Jun 2026 | Incorporated Sosinna's 31 client comments. Remediation plan confirmed within the report before issuance. Senior management sign-off timing confirmed. 6-year retention confirmed. |
| v4.0 — Narrative v3 | Jun 2026 | Nine-scene walkthrough completed. Report repositioned as an internal senior management document — not for direct regulator submission. Regulator View removed. Distribution lists confirmed at six. Single WSP upload confirmed. NCA notification drafting confirmed. |
| v5.0 — SRS v1.0 | Jun 2026 | First consolidated requirements document. Full FR/NFR baseline with confirmed decisions and open questions structured per module. |
| v6.0 — SRS v2.0 | Jun 2026 | Two-application architecture confirmed. Platform Super Admin Portal brought into scope. Requirement IDs confirmed as dynamic (sourced from official websites). Revenue source Excel drives service line mapping. Two new roles added (Senior Management, Remediation Owner). Custom org-level roles mapped to system roles. Sampling methodologies as platform-configured library. Full evidence type list confirmed. Partial testing confirmed. Finding closure CCO-only. ComplianceIQ branding confirmed. |
| v7.0 — PRD v3.0 | Jun 2026 | Full rewrite in plain English for a non-technical audience. Feature descriptions explain what each feature does and why. All confirmed decisions and open questions retained. Technical terms explained on first use. FR-XX reference tags retained for development team. |
| v8.0 — PRD v4.0 | Jun 2026 | Cross-document gap audit completed. 11 workflow design gaps identified and documented in new Section 16 (Gaps to Resolve Before Execution). Finding closure corrected: now requires CCO + one Senior Management sign-off (was CCO-only — contradiction with Narrative v3 resolved). Two confirmed decisions added from Narrative v3: Not Applicable test process (documented reason required, immutable) and sample change approval flow (senior team member approval + written reason, original selection retained). Risk rating confirmed as auto-calculated by platform — compliance officer confirms, does not manually enter. |

> **DEVELOPER NOTE** *(grey)*
>
> **📌 Note**
> - Per instruction, the version label stays at v4.0 — this document history table is unchanged. All edits from the 25 Jun call and Sosinna's Drive comments are layered into the sections above in colour, not recorded as a new version row here.

# 18. Sign-Off

This document represents the agreed product baseline as of June 2026. Development estimation proceeds from this version. Open questions marked 'Needed before estimation' in Section 15 must be resolved first. Workflow gaps in Section 16 must be resolved before the relevant development sprint begins.

| **Role** | **Name** | **Organisation** | **Signature / Date** |
|---|---|---|---|
| Delivery Head | Jomin Johnson | SayOne Technologies |   |
| Client — Domain Expert | Sosinna Degefu | Synergy Consulting Group |   |

*ComplianceIQ · Product Requirements Document v4.0 · SayOne Technologies · Confidential · June 2026* `[status note]`
