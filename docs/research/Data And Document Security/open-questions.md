# Open Questions

> **Baseline:** PRD v4.0. Questions this research **cannot** settle. Nothing here is answered by adopting a default. Where an "interim engineering position" is given, it is the least-committal way to keep work moving and it is **explicitly not a decision** — it is reversible and must be replaced by an answer.

Grouped by who must answer. **PRD-flagged** items are questions the PRD itself records as open; they are repeated here so this set stays consistent with the baseline.

---

## A. Questions the PRD already records as open, which affect security architecture

| # | PRD ref | Question | Why it matters here | Blocks | Interim engineering position (not a decision) |
|---|---|---|---|---|---|
| A-1 | **TI-02** | Uptime SLA: 99.5% or 99.9%? *(PRD: "still open — estimation blocker")* | Determines the recovery architecture and its cost (`disaster-recovery`) | Recovery design; any customer commitment | Build off-domain record copies to protect NFR-07; commit no availability or recovery figure |
| A-2 | **TI-03** | Are ISO 27001 or SOC 2 Type II required by clients as a condition of signing? *(PRD: open)* | NFR-09 puts them on the roadmap with the timeline "to be agreed" | Assurance planning | Operate controls in a way that would support certification later; assume no date |
| A-3 | **TI-05** | Public API: first version or later phase? *(PRD: partial, leaning later)* | An API is a new authenticated surface with its own authorisation and rate-limiting model | API security design | Treat as out of MVP scope |
| A-4 | **TI-06** | Expected number of firms and concurrent users in Year 1? *(PRD: partial — roughly 10 platform users per firm, firm total unknown)* | Drives key-service volume, storage growth and monitoring cost | Cost modelling; NFR-05 load testing | Load test at the NFR-05 figure of 100 concurrent users per firm |
| A-5 | **SA-06 / SA-08** | How much firm data may the Platform Admin Portal team see? *(PRD: open; leaning broad, with evidence visibility handled contractually)* | **This is an authorisation boundary. It cannot be built twice cheaply.** | Portal data layer; audit design | Deny by default; expose only the firm list, jurisdiction, services and last-use date stated in SA-06 |
| A-6 | **FR-52 vs GAP-07** | Remediation Owner: own tasks only, or view access to everything? *(PRD explicitly flags the contradiction)* | Determines the permission set for one of the eight system roles | Role permission model | Implement the narrower FR-52 reading behind a single policy switch |
| A-7 | **GAP-09** | Who may initiate a manual override of a WSP mapping? *(PRD: partially open)* | Determines who can change a mapping that two people must then approve | Mapping workflow | Restrict to the CCO pending an answer |
| A-8 | **GAP-11** | Does the platform force-prompt reassignment of a deactivated user's open items? *(PRD: partially open)* | Affects the FR-14 deactivation flow and its audit trail | Deactivation workflow | Surface open items on deactivation without blocking the deactivation |
| A-9 | **FO-07** | Who may complete the onboarding wizard — any Firm Super Admin or the CCO only? *(PRD: open)* | An authorisation question on a high-impact flow | Onboarding permissions | Allow Firm Super Admin, log the actor |
| A-10 | **RE-05** | Regulatory news feed sourcing: manual, automated, or commercial? *(PRD: open)* | Any automated source is an outbound integration needing an egress allowlist entry and a residency review | Egress allowlist | Treat the SA-03 sources (EUR-Lex, EBA, ESMA) as the only allowlisted feeds |

---

## B. Legal questions — require qualified counsel

| # | Question | Why it matters | Blocks | Interim engineering position (not a decision) |
|---|---|---|---|---|
| L-1 | **Where will development, support and production administration be performed?** The PRD does not say | If any is outside the EU/EEA, remote access to production personal data is a restricted transfer (`cross-border-data-processing`) | Operating model; sub-processor disclosure; DPA annexes | Build so that no production personal data is reachable from outside the EU/EEA at all |
| L-2 | If any delivery is non-EU: **is the transfer position defensible**, and what supplementary measures are required? | Determines whether the operating model is lawful | Contractual commitments to firms | Zero standing production access plus EU-held keys |
| L-3 | **How do GDPR erasure requests interact with the PRD's non-deletability rule?** (PRD §2, NFR-07 vs GDPR Art. 17) | The PRD says evidence, results, reports and audit records cannot be deleted by anyone. This is a genuine conflict | DPA wording; any deletion capability at all | Implement no deletion path for protected classes; provide a documented refusal path for the controller to use. **Do not adopt crypto-shredding or soft-delete** |
| L-4 | **When, if ever, does retention end after the six-year minimum?** | NFR-07 sets a floor and no ceiling; indefinite retention is in tension with storage limitation | Retention service; storage cost model | Retain; build the retention service so a ceiling can be added later without migration |
| L-5 | **Is the platform in scope of NIS2**, and in which member state? | Would create direct incident-reporting and registration obligations | Incident procedure; management accountability | Make no NIS2 commitment; keep the incident process capable of supporting one |
| L-6 | **AI Act classification of AI-assisted WSP mapping** | Determines documentation and transparency obligations | Product documentation | Label AI-suggested mappings; make no classification claim |
| L-7 | **Does the platform ship anything that would trigger CRA scope?** | CE marking and a support-period update commitment on an unplanned product | Product decisions | The PRD ships no installable artefact; gate any future one |
| L-8 | **Employment-law constraints on security monitoring** in each jurisdiction where staff are employed | Session recording and behavioural monitoring may require consultation or be unlawful without it | Monitoring deployment | Deploy prevention-side controls only until advice is obtained |
| L-9 | **What incident-notification deadline to client firms will be contracted?** | GDPR requires "without undue delay" from a processor; a number is contractual, and firms need time for their own filings | Contract; incident runbook | Notify as fast as the process allows; commit to no number |
| L-10 | **Will any customer contractually impose DORA Chapter V terms** — audit rights, exit assistance, subcontractor inspection? | Would create obligations the fixed-fee scope does not currently price | Contract templates | Assume none until a contract says otherwise |

---

## C. Client and product decisions

| # | Question | Why it matters | Blocks | Interim engineering position (not a decision) |
|---|---|---|---|---|
| P-1 | **Which EU region?** | Everything inherits it; some services differ by region | Foundation build | None — this must be answered before Phase 0 completes |
| P-2 | **How is infrastructure provisioned into, and handed over inside, a Client-owned AWS account (TI-01)?** Who holds root credentials and break-glass custody? | Determines the whole privileged-access model | Foundation build; break-glass design | Design for split custody; confirm before go-live |
| P-3 | **Is a second EU region funded** for record copies and/or recovery? | Protects NFR-07 against regional loss; costs money | Recovery design | Cost it and present it; assume nothing |
| P-4 | **What is the configured maximum evidence file size (NFR-11)?** | Drives storage cost across a six-year non-deletable horizon, and the upload denial-of-service surface | Storage cost model; WAF limits | Set a conservative initial value; it is changeable without a release by design |
| P-5 | **What concrete second factor satisfies FR-11's "verification step on their phone"?** SMS code, authenticator app, or push approval | SMS is subject to SIM-swap, a live risk for crypto-sector staff | Authentication build | Implement authenticator-app TOTP, which satisfies "on their phone" and is the stronger reading |
| P-6 | **Which AI inference provider and model?** | Residency, no-training and no-retention terms must be contractual; accuracy against the 85% bar must be measured | Mapping pipeline | Build behind an abstraction; evaluate candidates against the `ai-governance` criteria |
| P-7 | **Does FR-59 send the report as an attachment or as an authenticated link?** | An attachment puts confidential content outside the audited boundary | Notification design | Send a link; confirm with the Client |
| P-8 | **Is out-of-hours alert response funded**, and in what form? | Detection without response is decorative | Monitoring operating model | Automate containment for unambiguous cases; escalate the gap |
| P-9 | **Who is the named owner accountable for platform security?** | Somebody must own the control matrix, risk register and customer security responses | Governance | Escalate; do not assume a role exists |
| P-10 | **Is a coordinated vulnerability disclosure policy published**, given CC-03 assigns all material to the Client? | Publication is the Client's call | Disclosure policy | Prepare it; do not publish without approval |
| P-11 | **Are firms' own auditors or regulators expected to be given direct, scoped access?** | Would add a ninth role and a new authorisation surface | Role model | Out of scope; firms export what they need |

---

## D. Technical questions — require a spike or benchmark

| # | Question | Why it matters | Interim engineering position |
|---|---|---|---|
| T-1 | Key-service cost and latency with per-firm keys and per-object data keys at target volume | Could force a change in key granularity | Proceed; benchmark at multiples of projected load; use bounded caching |
| T-2 | Latency of synchronous audit writes on evidence reads, against the NFR-05 two-second target | May require reclassifying which actions are synchronous | Implement synchronously; measure; adjust the classification empirically |
| T-3 | Overhead of five authorisation enforcement layers at NFR-05's 100 concurrent users per firm | Could breach the performance requirement | Benchmark early; evaluate policy locally |
| T-4 | What retrieval and prompting architecture actually reaches 85% on the agreed verification vectors | **This is a contractual commitment, not a stretch goal** | Spike against real WSP documents before the approach is fixed |
| T-5 | Achievable false-positive rate for prompt-injection detection on real compliance manuals | Determines whether detection can block a suggestion or only flag it | Flag and review initially |
| T-6 | Scanning and processing cost for the media formats FR-24 admits (video, audio, screen recordings, archives) | Drives the NFR-11 ceiling and the pipeline design | Benchmark with a realistic file mix |
| T-7 | Cross-store point-in-time consistency for firm-granular restore | Harder than it appears; determines the guarantee that can be offered | Spike; document the achievable guarantee honestly |
| T-8 | Monitoring ingestion cost at realistic log volumes over a six-year audit retention | The most common budget overrun in this area | Model at multiples of projection; keep audit events out of the expensive tier |
| T-9 | Whether an externalised policy engine or a disciplined in-application policy module fits better at this team size | Migration later is costly | Keep authorisation centralised and fully test-covered either way |

---

## E. Assumptions made in this research that should be validated

| # | Assumption | Impact if wrong |
|---|---|---|
| E-1 | Clients are MiCA-licensed CASPs, as the PRD states | Different regulatory overlay for the customer; platform controls largely unchanged |
| E-2 | SayOne is a processor, not a joint controller, for firm data (NFR-06) | Joint controllership would change liability and require a different arrangement |
| E-3 | AI-assisted WSP mapping remains advisory, human-confirmed and two-person-approved (FR-31, FR-32) | Any weakening would raise automated-decision and AI Act questions that do not currently arise |
| E-4 | AWS is the platform, on a Client-owned account (TI-01) | Component choices would change; the control model would not |
| E-5 | No installable or embeddable artefact ships | Would raise CRA scope |
| E-6 | The Platform Admin Portal is delivered in the same build as the Firm Application (PRD §1.1, §16) | Sequencing and the Portal authorisation boundary would change |
| E-7 | Notifications remain email and in-platform only (NT-01) | Any additional channel is a new egress path and residency question |
| E-8 | No self-service registration exists anywhere, including the marketing site (FR-12, MKT-02) | Self-registration would break the invitation-only access model |

---

## How to use this document

1. **Before Phase 0 completes:** answer P-1, P-2, L-1, and name an owner (P-9).
2. **Before the sprints they block:** answer A-5, A-6, A-7, P-5, P-6.
3. **Before accepting real client data:** answer L-2, L-3, L-9, P-3, P-8, and complete T-4.
4. **Before quoting any figure to a customer:** answer A-1 and complete the measurements in `deployment-recommendations` §7.
5. **Review periodically.** Answered questions move into the decision record (`architecture-decision-records`) with their status upgraded from OPEN to a stated decision and the approver named. **Do not upgrade a status without a real approval.**
