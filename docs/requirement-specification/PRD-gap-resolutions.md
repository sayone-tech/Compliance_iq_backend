# ComplianceIQ — Recommended Resolutions for the PRD v4.0 Gap Analysis

**Companion to:** [`PRD-gap-analysis.md`](PRD-gap-analysis.md) — 88 findings, G-01 to G-88
**Baseline:** [`PRD.md`](PRD.md) (PRD v4.0) remains the sole source of truth. Nothing in this document changes it.

## How to read this

One recommended resolution per gap, in the analysis's own order. Each carries a class:

| Class | Meaning |
|---|---|
| **PROPOSED** | An implementation recommendation that delivers something the PRD already requires. No new scope. Buildable once accepted |
| **SCOPE ADDITION** | Genuinely new scope. Solves a real problem, but it is not in the PRD and would need Client approval — and, under the fixed-price milestone model with a baseline-freeze clause, an amendment |
| **OPEN — CLIENT** | A product, commercial or domain decision only the Client can make. A recommendation is given; **no default is adopted** |
| **OPEN — LEGAL** | Needs qualified counsel before it is contracted or represented to a customer |
| **LIMITATION** | Recommended answer is to write it down as an explicit exclusion rather than build it |
| **ALREADY DESIGNED** | The security research set already answers this. Link given; nothing new to decide beyond accepting the design |

**No approval is asserted anywhere in this document.** Where the analysis itself recommends a solution, that recommendation is adopted unless it conflicts with the PRD — the three cases where it does are called out in §Conflicts at the end.

PRD requirements are named descriptively rather than by ID, for the same reason as the security research set: IDs move between PRD versions. The gap analysis quotes the IDs where you need them.

Security-side gaps link into `../research/Data And Document Security/`.

---

# A. Contradictions inside the document

### G-01 — Remediation Owner visibility is a three-way contradiction
**Recommended:** resolve to the **narrow** reading and amend all three places at once — the role table, the personal-view requirement, and the gap answer. A Remediation Owner sees their own milestones **plus the full context of the Findings they own** (finding text, severity, root cause, the requirement and the test result it came from), and nothing else. Not the firm-wide findings register.
**Why:** a Remediation Owner is frequently a business-line manager. Giving a trading desk head standing read access to every AML finding in the firm is an access-control decision, not a dashboard preference, and it works against least privilege. The "evidence of completion goes back to the tester" loop that motivated the broad reading is satisfied by the narrow one.
**Class:** OPEN — CLIENT. Interim engineering position: build the narrow reading behind a single policy switch so the broad reading remains a configuration change, not a rewrite. See [open-questions](../research/Data%20And%20Document%20Security/open-questions.md) A-6.

### G-02 — IT/Systems Admin cannot see tests but must upload evidence to them
**Recommended:** a **scoped step-level contributor grant**, not a ninth role. The Lead Tester or CCO grants a named user upload rights on a named test step; the grant confers visibility of that step only, never the result, findings, or other steps; it expires when the test is submitted; grant and use are both audited.
**Why:** preserves the eight-role model the PRD fixes while making the workflow it describes actually possible.
**Class:** PROPOSED.

### G-03 — Senior Management is "read-only" but performs three write actions
**Recommended:** rewrite the role definition as **"read-only on operational data; write on approvals, sign-offs and acknowledgements"**. Documentation correction; the permission model already has to support the writes because three requirements demand them.
**Class:** PROPOSED (no build impact).

### G-04 — AML Officer is a workflow actor but not a system role
**Recommended:** make **AML Officer an assignable attribute on a user**, independent of the eight system roles, assigned by the Firm Super Admin, changes audited. Enforce the PRD's constraint ("Senior Management or CCO-level") as a **warning at assignment rather than a hard block**, so a firm whose MLRO is a Compliance Officer is not permanently unable to generate a report.
**Why:** an attribute avoids a ninth role and its permission matrix, and it matches how firms actually allocate the MLRO function.
**Class:** OPEN — CLIENT on whether the constraint is hard or advisory; PROPOSED on the mechanism.

### G-05 — Two-person sign-off can deadlock at the target customer size
**Recommended:** two things together.
1. **Governance-capacity guard**, modelled on the existing two-Super-Admin guard: the platform knows the eligible approver pool for each approval type, warns when a pool reaches one, and blocks nothing silently.
2. **A documented exception path** — never a silent bypass. Where the pool is genuinely exhausted, the action proceeds only with a written justification, is flagged in the audit trail as an exception, and appears on the CCO dashboard and in the report.
The actual minima ("at least one CCO and two Senior Management users") are a Client decision.
**Class:** OPEN — CLIENT on the minima; PROPOSED on the guard and the exception path.

### G-06 — The only minimum-headcount guard protects a role that blocks nothing
**Recommended:** extend the same guard to the roles that actually block the workflow — CCO and Senior Management — using the G-05 mechanism. Warn on the dashboard and notify the Firm Super Admins.
**Class:** PROPOSED.

### G-07 — No delegation or deputy model; the CCO is a single point of failure
**Recommended:** **time-boxed delegation** as an explicit, audited grant: grantor, grantee, scope (which powers), start and end, reason. Every delegated action records "X acting for Y". Auto-expiry with no silent renewal. **Delegation may never collapse a two-person rule onto one person** — the exclusion rules are evaluated on the acting identity *and* the principal.
**Why:** the PRD concentrates test assignment, test approval, milestone confirmation, report generation and closure co-signature in one role. For a governance product this is a functional defect, not a nicety.
**Class:** SCOPE ADDITION — not in the PRD; recommend adding before freeze.

### G-08 — "Three findings = High" collides with "the officer confirms the rating"
**Recommended:** keep automatic rating as the default, add **severity weighting** so three trivial documentation findings do not outrank one control failure, and add an explicit **CCO downgrade with mandatory written justification**, recorded and shown in the report. Both the computed rating and the confirmed rating are retained.
**Class:** OPEN — CLIENT on the weighting rule (a domain judgement); PROPOSED on the override mechanism.

### G-09 — Compliance findings are wrongly wired to the DORA four-hour clock
**Recommended:** **decouple them.** The four-hour regulator notification path belongs only to the ICT incident module, triggered by an ICT-related incident. A compliance test finding — of any severity — never starts it. Correct the escalation table accordingly.
**Why:** as written, a documentation test with three trivial findings can put a firm on a path toward a spurious regulatory filing. The reputational cost of a wrong filing is borne by the customer.
**Class:** OPEN — CLIENT (domain confirmation from Sosinna), with the correction above as the recommendation.

### G-10 — Milestone confirmation vs. CCO rejection ordering
**Recommended:** define it explicitly — **CCO rejection returns confirmed milestone dates to "proposed"**, and the original confirmations are retained in the audit trail with the rejection reason. Owners are notified that their confirmation has been reopened. Nothing is silently voided and nothing silently survives.
**Class:** PROPOSED.

### G-11 — The account owner can technically see every tenant's data
**Recommended:** state the position honestly rather than paper over it. In an AWS account owned solely by the Client, **tenant isolation protects firms from each other; it does not protect them from the account owner.** What can be done inside the MVP:
- per-firm keys with the firm identifier bound into the encryption context, and **separation of key administration from data-plane decrypt rights**, so no single operator role both administers keys and reads plaintext;
- zero standing human access to production, with dual-approved, session-recorded break-glass;
- operator access to a firm's data surfaced in **that firm's own audit trail**, so access is visible to the party it affects.
A firm-held key would be the only complete answer. It is **out of MVP scope**, and it collides with the PRD's non-deletability rule — a firm could render its own six-year records unreadable. See [future-scope](../research/Data%20And%20Document%20Security/future-scope/future-and-optional-scope.md) §1.
**Class:** OPEN — CLIENT and LEGAL — the disclosed position and the contractual terms that go with it. Partly ALREADY DESIGNED: see [key-management](../research/Data%20And%20Document%20Security/key-management.md), [insider-threat-protection](../research/Data%20And%20Document%20Security/supporting-topics/insider-threat-protection.md).

---

# B. Regulatory and domain scope

### G-12 — AML content pervades a product scoped to MiCA and DORA
**Recommended:** decide explicitly, and price the decision. Two coherent positions:
- **(a) AML workflow, MiCA/DORA content.** Keep the AML Officer sign-off gate and AML-flavoured role names — they are governance workflow — but state that the requirement library covers MiCA and DORA instruments only. Any AML-derived test is out of scope until the library is extended.
- **(b) AML in scope.** Then the regulatory scope line is wrong, the content-authoring effort grows materially, and the AML instrument set (the 2024 AML package and the crypto Travel Rule regulation) must be named.
**Recommendation: (a) for MVP**, with (b) as a costed phase-2 content extension — it is a content problem, not an architecture problem, so deferring it costs little later.
**Class:** OPEN — CLIENT. Blocker. Do not let this be absorbed silently into a fixed fee.

### G-13 — Article citations need verification before they reach an inspection-grade report
**Recommended:** add **per-citation verification metadata** in the Portal — instrument, article, source URL, verified by, verified on — and **block publication of a requirement whose citation is unverified**. The formal report prints only verified citations. The initial mapping is signed off by the Client's domain expert before any of it is authored.
**Class:** PROPOSED (mechanism) + OPEN — CLIENT (the sign-off itself).

### G-14 — The DORA Register of Information is absent
**Recommended:** **explicitly exclude it from MVP** and say so in the exclusions section (G-84). It is a large, schema-driven artefact against a prescribed supervisory template — genuinely the thing CASPs most want software for, and therefore the strongest phase-2 candidate, but it cannot be absorbed into the current vendor register's five fields.
**Class:** OPEN — CLIENT; recommend LIMITATION for MVP with a costed phase-2 option.

### G-15 — DORA incident reporting is modelled as one report; it is three
**Recommended:** model an incident as a **case with a sequence of obligations** — initial notification, intermediate report, final report — each with its own due clock and content, plus reclassification handling when an incident later crosses the major threshold. If that is too large for MVP, then **track none of the clocks and say so**: partial tracking is worse than absent tracking, because the firm believes a deadline is being watched when it is not.
**Recommendation: include it.** A DORA-positioned product that silently drops two of three regulatory deadlines is a liability.
**Class:** OPEN — CLIENT; recommend in scope.

### G-16 — There is no submission channel for regulator notification
**Recommended:** state it as a **manual attestation**: the platform drafts and generates the notification, records the download, and the CCO confirms submission with a timestamp and an external reference number. No submission API is claimed anywhere in the product or the marketing site. This makes the requirement testable.
**Class:** PROPOSED (documentation and acceptance criteria).

### G-17 — Branch jurisdictions are captured but no jurisdiction content model exists
**Recommended:** minimal jurisdiction dimension — a **jurisdiction tag on each requirement version** (EU-wide, or a named national regulator), filtered by the firm's home jurisdiction at test loading. If that is not built, **drop the national-overlay promise from the onboarding section** rather than leave a promise the content model cannot keep.
**Class:** OPEN — CLIENT (build or drop); PROPOSED on the minimal design.

### G-18 — Threat-led penetration testing for "significant" firms
**Recommended:** the platform **tracks, never guides**: an evidence slot, a multi-year cycle, and a reminder. Threat-led testing is run by external specialists under a supervisory framework and cannot be reduced to a test procedure. State this.
**Class:** PROPOSED (as a stated limitation of the feature).

### G-19 — No handling of staged application dates
**Recommended:** **applies-from and applies-until dates on each requirement version**, with the scheduler filtering on them. A firm onboarding today is not scheduled tests for an obligation that starts next year, and retired obligations stop scheduling without deleting history.
**Why:** cheap to build now, expensive to retrofit into a scheduler and a six-year archive.
**Class:** PROPOSED.

---

# C. GDPR and data lifecycle

### G-20 — Immutable retention conflicts with the GDPR erasure right
**Recommended — and this differs from the analysis's own suggestion.** The analysis proposes crypto-shredding as the technical erasure mechanism. **Do not adopt it.** Destroying a firm's key makes six-year records unreadable, which is deletion by another name and contradicts the PRD's rule that evidence, results, reports and audit records cannot be deleted by anyone including administrators. The same applies to deletion sagas and soft-delete grace periods.

What to do instead:
1. **Build no deletion path** for the protected record classes, and block key deletion while any record is inside its retention period.
2. **Minimise personal data at source** — see G-21. The cheapest erasure request to answer is the one about data that was never uploaded.
3. **Maintain a lawful-basis and retention register per data category**, so an Art. 17(3)(b) legal-obligation position is documented and scoped rather than assumed.
4. **Complete a data protection impact assessment** before real client data.
5. **Provide a documented refusal/restriction path** the controller can use, with the platform recording the request and the response.
6. **Escalate the residual conflict as a legal decision.** It is genuine, and it is not this project's to resolve unilaterally.
**Class:** OPEN — LEGAL. Blocker. ALREADY DESIGNED on the engineering side: [immutable-evidence-retention](../research/Data%20And%20Document%20Security/immutable-evidence-retention.md), [key-management](../research/Data%20And%20Document%20Security/key-management.md).

### G-21 — "No PII" is enforced on CSV imports and ignored on evidence uploads
**Recommended:** an **evidence-handling policy** with three parts — redaction guidance for testers, a **"contains personal data" flag per upload** that drives access treatment and appears in the retention register, and a mandatory field prompting the uploader to confirm minimisation. The platform cannot inspect intent, so pair the technical flag with a contractual allocation of responsibility to the firm as controller.
**Class:** PROPOSED.

### G-22 — No disposal process at the end of retention
**Recommended:** a **retention service as the single source of truth** — per-class minimums, legal hold, and extension supported. Build it so a retention *ceiling* can be added later without data migration. **When retention ends is a Client and counsel decision**: the PRD states a six-year floor and no ceiling, and indefinite retention is in tension with storage limitation.
**Class:** OPEN — LEGAL (when it ends) + PROPOSED (the mechanism). ALREADY DESIGNED: [immutable-evidence-retention](../research/Data%20And%20Document%20Security/immutable-evidence-retention.md).

### G-23 — No firm offboarding or contract-termination path
**Recommended:** define exit as a first-class flow before signature, because it changes the storage cost model, the contract and the architecture:
- **Full export** — records, evidence files, and the firm's audit trail, in documented formats, obtainable without assistance.
- **Custody of non-deletable records after exit** — who is controller, where they sit, on what lawful basis, and **who pays for six more years of storage**.
- **Access downgrade** rather than deletion: the firm's users lose operational access; the records persist.
- **A written exit-assistance statement** the customer can drop into its own vendor exit plan — its own regulator expects it to have one.
**Class:** OPEN — CLIENT and LEGAL. Blocker.

### G-24 — The platform is itself an ICT third-party provider to every customer
**Recommended:** assemble the **assurance pack** procurement will ask for, and treat it as a deliverable rather than an afterthought: security architecture overview, sub-processor list, data location statement, incident-notification commitment, audit and inspection posture, exit assistance, and a control summary. Most of the technical content already exists in the security research set; what is missing is the **commitments**, which are contractual and unpriced.
**Class:** PROPOSED (the pack) + OPEN — CLIENT (each commitment). Partly ALREADY DESIGNED: [security-control-matrix](../research/Data%20And%20Document%20Security/security-control-matrix.md), [regulatory-obligations](../research/Data%20And%20Document%20Security/regulatory-obligations.md).

### G-25 — No DPA, no sub-processor list, no transfer position
**Recommended:** the DPA is a **named deliverable** with defined contents (scope, instructions, security measures, sub-processing, assistance, deletion/return, audit). Publish a sub-processor list with advance notice of changes. The transfer position can only be settled once the delivery topology is settled — where development, support and production administration are performed is not stated in the PRD.
**Class:** PROPOSED (artefacts) + OPEN — LEGAL (transfer position). See [cross-border-data-processing](../research/Data%20And%20Document%20Security/supporting-topics/cross-border-data-processing.md).

### G-26 — The revenue source file gets no special treatment
**Recommended:** classify it in the **most restricted class alongside evidence** — firm key, restricted-role access, watermarked preview rather than raw download by default, every access audited. The classification machinery already exists for evidence; this is applying it, not building it.
**Why:** it is a competitor-relevant financial breakdown sitting in an account owned by a consulting group that sells into the same market.
**Class:** PROPOSED.

---

# D. AI, OCR and regulatory monitoring

### G-27 — The 85% accuracy commitment has no measurable definition
**Recommended:** define the measurement **in writing before build starts**, covering five things:
1. **The metric.** Recommend per-requirement **recall at a stated precision floor** — it is the number that matters for a gap-analysis feature, and it prevents a mapper scoring well by abstaining. F1 is an acceptable alternative. Pick one; the same model scores very differently under each.
2. **Who supplies the verification vectors, and when.** They must come from the Client's domain team and be **frozen before UAT**. A target defined after the build is unbounded.
3. **The corpus** — how many vectors, from how many distinct WSP documents, in which languages, including at least one scanned document if scanned PDFs are in scope.
4. **Abstention handling** — whether "no mapping suggested" counts as a miss.
5. **A bounded remediation window and a defined fallback** if UAT lands below the bar — for example, ship with human-only mapping plus a documented accuracy disclosure. Fixed fee plus unlimited tuning plus no exit criterion is an open-ended obligation.
**Class:** OPEN — CLIENT. Blocker, and the single largest contractual exposure in the document.

### G-28 — Using an LLM appears to breach EU residency, and no AI stack is specified
**Recommended:** **EU-resident inference under contractual no-training and no-retention terms.** No carve-out to the residency requirement — the residency promise is one of the product's load-bearing claims and trading it for model convenience is a bad exchange. The provider and model stay **unselected** and are chosen against stated criteria (residency, contractual terms, accuracy against the frozen vectors, cost, exit).

The analysis names one candidate; the security research deliberately names none, because the PRD names none. Treat provider selection as an open decision, not a design constant.

Prompt injection is already treated as a live threat — uploaded WSPs are untrusted input — with delimiting, schema-constrained output, and **deterministic verification that every cited span exists at the stated offset in the source document**.
**Class:** OPEN — CLIENT (provider) + ALREADY DESIGNED (the properties and the injection/hallucination controls): [ai-governance](../research/Data%20And%20Document%20Security/ai-governance.md).

### G-29 — OCR has no accuracy target, language scope, or failure path
**Recommended:** three decisions — **declare the supported languages**, **measure OCR quality separately from mapping accuracy** (otherwise a bad scan silently consumes the 85% budget), and **define the failure path**: when OCR confidence is low the document is flagged for manual text supply and the mapping does not run. Never map silently against garbage.
**Class:** PROPOSED (separation and failure path) + OPEN — CLIENT (language scope).

### G-30 — No internationalisation position
**Recommended:** state **English-only UI and reports for MVP** as an explicit limitation — but separate that from **document language**. A Portuguese or German WSP is the normal case for an EU CASP even where the UI is English, so OCR and model language coverage is a different question and must be answered under G-29. Conflating the two produces a product that cannot read its customers' manuals.
**Class:** OPEN — CLIENT; recommend LIMITATION for the UI, with document language answered separately.

### G-31 — Regulatory monitoring has no latency target and no feed-failure path
**Recommended:** a **feed heartbeat** — every source is expected to produce something within a defined interval, and silence or a format change raises an alert to the Portal team. Silent feed death is the failure mode that makes the whole feature untrustworthy, and it is invisible without a heartbeat. Detection and human-review targets are Client decisions; "immediately alerted" should be restated as "on publication of a reviewed update".
**Class:** PROPOSED (heartbeat) + OPEN — CLIENT (targets).

### G-32 — Republishing regulator content has no licensing position
**Recommended:** default to **link and summarise rather than store and republish** third-party regulator text, which sidesteps most of the question. Confirm reuse rights with counsel before storing any full text, and before any commercial feed is contracted.
**Class:** OPEN — LEGAL + PROPOSED (the default).

---

# E. Testing module

### G-33 — Does the platform select the sample or only record it?
**Recommended: record-keeping for MVP**, stated plainly. The platform records population size, sample size, selection method, methodology reference and rationale. It does not draw the sample, because drawing one requires customer-level identifiers in the platform — which collides directly with the no-personal-data position taken elsewhere.

If defensibility is genuinely required, the middle path is: the firm uploads a **de-identified population identifier list** (opaque IDs only, no attributes), the platform draws with a **seeded, reproducible algorithm and stores the seed**, and the firm resolves the IDs back in its own system. That is genuinely defensible and keeps personal data out.

The onboarding and sampling text should be corrected either way — as written it reads like generation and is scoped like recording.
**Class:** OPEN — CLIENT. Blocker. Recommend record-keeping, with the pseudonymous variant as a costed option.

### G-34 — Minimum sample size is enforced but never specified
**Recommended:** a **Portal-authored lookup per test type**, maintained by the Client's domain team, with an optional statistical calculator (confidence level, expected error rate, population size) offered as guidance. This is content, not code — which means it can be tuned without a release.
**Class:** PROPOSED (mechanism) + OPEN — CLIENT (the values).

### G-35 — "Testing period" is never defined as an object
**Recommended:** make the **testing period a first-class object** — dates, state, who opens and closes it, whether overlap is permitted. Repeat-finding detection, period comparison and partial-coverage tracking are all defined in terms of it and are unimplementable without it.
**Class:** PROPOSED — required to make existing PRD features buildable, not new scope.

### G-36 — Repeat Finding detection has no matching rule and a one-period lookback
**Recommended:** match on **requirement plus root cause category over a rolling window** (window length a Client decision; 24 months is a reasonable starting point), with the CCO confirming or dismissing each flag and the decision recorded. A strict one-period lookback misses the fail–untested–fail pattern, which is the pattern supervisors care most about.
**Class:** PROPOSED (rule shape) + OPEN — CLIENT (window length).

### G-37 — The consensus conversation happens outside the platform
**Recommended:** an **append-only comment thread** on Findings and test executions — participants, timestamps, no edit and no delete, included in the audit trail and in the Finding's history. Optionally surfaced in the report appendix.
**Why:** the negotiation that determines the remediation plan is the most contested step in the process. Recording only its outcome leaves the audit trail materially incomplete and contradicts the "all in one place" promise.
**Class:** SCOPE ADDITION — recommend adding; it is small relative to its evidentiary value.

### G-38 — Requirement-level "Not Applicable" has no owner
**Recommended:** requirement-level N/A **requires dual sign-off** — it removes an obligation from the programme, which is a heavier act than marking one execution N/A — with a documented reason, an immutable record, and **re-surfacing for confirmation whenever the revenue-file derivation changes**. It survives a re-upload rather than being silently cleared or silently retained.
**Class:** PROPOSED.

### G-39 — No rule for in-flight and historical work when service lines change
**Recommended:** **removal never deletes.**
- A removed requirement moves to *no longer applicable from `<date>`*; it stops scheduling.
- **Open findings and open milestones under it stay open and visible.** A supervisor will still ask about them.
- Historical results are retained and shown in comparison views, annotated with the applicability change.
- Added requirements schedule **from the next period** by default, with the CCO able to start immediately. No retroactive non-compliance is asserted for periods before the service line was declared.
**Class:** PROPOSED.

### G-40 — Re-uploading the revenue file changes obligations with no approval gate
**Recommended:** a re-upload produces a **diff screen** ("these 15 tests will stop being scheduled; these 6 will start") and requires **CCO confirmation with a justification**, audited — the same gate the PRD already applies at onboarding.
**Class:** PROPOSED.

### G-41 — The revenue file template does not exist and is on the critical path
**Recommended:** treat the template as a **versioned artefact**: column specification, validation rules, error reporting, a template version stamped on every upload, and rejection of unrecognised versions with a clear message. Correct the onboarding wording from automatic derivation to **"derived, then confirmed"** — the Client's own note says a single revenue line can span two service lines, so the derivation is a suggestion.
**Class:** PROPOSED (mechanism) + OPEN — CLIENT (template content, which blocks the sprint).

### G-42 — The important half of the mid-test regulation-update gap is being under-weighted
**Recommended:** **split it.** The banner-versus-notice question is a design decision. **Pinning the requirement and procedure version on the test execution record is mandatory** — it is the only thing that makes the "in-flight tests continue on the version they started" promise provable to an inspector.
**Class:** PROPOSED (data model).

### G-43 — No behaviour defined for retiring a requirement mid-cycle
**Recommended:** retirement is a **version event with an effective date**. In-flight tests finish on their pinned version. Scheduled-but-not-started tests are withdrawn with an audit note. Open findings persist. Nothing is force-migrated mid-test.
**Class:** PROPOSED.

### G-44 — Trend comparison is invalid across procedure versions
**Recommended:** **annotate** comparison views wherever the underlying procedure version differs, and never present a silent like-for-like comparison. Cheap, and it protects the credibility of the one screen most likely to be shown to a board.
**Class:** PROPOSED.

### G-45 — Partial testing has no coverage model
**Recommended:** the Portal authors **named sub-scopes per requirement**, and coverage is computed against that set. Without an authored set, "fully covered" is unknowable and coverage tracking is free text that cannot be reported on.
**Class:** PROPOSED (Portal content model addition — feeds the Portal scope decision in G-79).

### G-46 — Evidence shelf life has no source of truth, and there is no evidence library
**Recommended:** validity period **authored per evidence type in the Portal**, overridable per test procedure. Add an **evidence library** so one artefact — a business continuity test report, say — serves several tests with a single tracked age, rather than being re-uploaded per test and ageing independently in three places.
**Class:** PROPOSED (validity source) + SCOPE ADDITION (library).

### G-47 — No historical data import at onboarding
**Recommended:** state as an **accepted limitation**, and soften it cheaply by allowing prior-period reports to be attached as evidence so a new firm's archive is not empty. Note the demo consequence honestly: period comparison and repeat-finding detection produce nothing useful for a customer's first year, and those are the two features most likely to be demonstrated in a sales cycle.
**Class:** LIMITATION (recommended) or a costed import.

### G-48 — No cloning, bulk assignment, or carry-forward
**Recommended:** carry-forward of prior-period setup plus bulk assignment. A CCO assigning forty quarterly tests individually will ask for this in the first week of use.
**Class:** SCOPE ADDITION — small, high adoption value.

### G-49 — No global search
**Recommended:** permission-filtered search across findings, tests and evidence **metadata** (not full evidence content for MVP). It must respect tenant isolation and per-record permissions, be rate-limited, and be audited — an unrestricted search box over a six-year multi-tenant evidence archive is also an exfiltration path.
**Class:** SCOPE ADDITION — recommend including; a six-year archive without search degrades badly.

---

# F. Reports, notifications, dashboard

### G-50 — Reports are auto-emailed with every open compliance failure in them
**Recommended:** **authenticated expiring link as the default**, not an attachment. Attachments only where a list has explicitly enabled them. Recipients must be known platform users unless explicitly approved as external. **Periodic list re-validation by the CCO**, and an audit entry per delivery.
**Why:** this is the highest-impact data-leak path in the product — an automated send, with no human in the loop, of a document listing every unremediated control failure, to a list that decays quietly as people leave.
**Class:** PROPOSED + OPEN — CLIENT (confirmation). Matches [open-questions](../research/Data%20And%20Document%20Security/open-questions.md) P-7.

### G-51 — Six fixed distribution lists, no external-recipient model
**Recommended:** keep six fixed for MVP; add an **external-recipient flag requiring CCO approval per address**, with the approval audited and the address re-validated on the same cycle as G-50. Custom lists are a later feature.
**Class:** OPEN — CLIENT.

### G-52 — "Acknowledged" is tracked but never defined
**Recommended:** define acknowledgement as an **authenticated in-app action by the named recipient**, recorded with actor and timestamp. No acknowledgement by proxy unless an explicit delegated grant exists (G-07). Without a defined act, the five-business-day escalation cannot be built or tested.
**Class:** PROPOSED.

### G-53 — Clocks have no calendar or timezone definition
**Recommended:** a **firm-level timezone and working calendar**, with jurisdiction public holidays maintained as Portal content. State per clock whether it is calendar-time or business-time: **the ICT incident four-hour clock is wall-clock**; the five-business-day escalation and the reminder ladders are business-time.
**Class:** PROPOSED (model) + OPEN — CLIENT (holiday calendar source).

### G-54 — No deliverability, bounce or provider requirement
**Recommended:** an authenticated sending domain with SPF, DKIM and DMARC; bounce and complaint handling; and **delivery status recorded honestly** — a hard bounce must never be recorded as delivered. A silently bounced report logged as distributed is an audit-trail falsehood in a product whose value is its audit trail.
**Class:** PROPOSED.

### G-55 — No report generation performance target
**Recommended:** **asynchronous generation** with progress feedback, failure handling and retry. The two-second target applies to dashboards; a multi-hundred-page report with embedded evidence references is a background job and should be specified as one.
**Class:** PROPOSED.

### G-56 — No draft, preview or regeneration path, and the clock trigger is fragile
**Recommended:** drafts exist and are discardable; **only the signed-off report is immutable**; a rejected report is retained as a rejected artefact with the rejection reason. **Start the milestone clocks on sign-off rather than on first generation** — otherwise a wording rejection silently consumes a week of every remediation deadline.
**Note:** this adjusts a statement the PRD makes explicitly ("the moment the CCO generates the report, every milestone clock starts"). Flag it rather than change it unilaterally.
**Class:** OPEN — CLIENT (it touches a stated PRD rule); PROPOSED on drafts and rejection handling.

### G-57 — "More metrics can be added based on preferences" is unbounded
**Recommended:** **fix the initial metric set** in the acceptance criteria. Anything further is either an amendment or a properly scoped configurable-widget feature. Open-ended wording in a fixed-price contract is a dispute generator.
**Class:** PROPOSED.

### G-58 — No external auditor or regulator access
**Recommended:** record as a **deliberate limitation**. Firms export what their auditors need. An auditor role would add a ninth role, a new authorisation surface, and a cross-firm access question — real scope, not a toggle.
**Class:** LIMITATION.

---

# G. Organisation and staff

### G-59 — The compliance-independence check has no data to run on
**Recommended:** a **controlled department taxonomy** with a revenue-generating vs. control classification, maintained in the Portal and mapped during onboarding. Where a department is unmapped, the platform reports **"cannot evaluate"** rather than passing silently.
**Why:** a firm that names its trading desk "Markets Group" gets no flag and believes the check ran. A silent false negative in a governance control is worse than no control.
**Class:** PROPOSED.

### G-60 — The org chart has no rules for malformed hierarchies
**Recommended:** **validation at import** with a specific, actionable error report — cycles, multiple roots, orphans, unknown managers — plus a defined rendering rule for structures that cannot be resolved. Decide explicitly whether dual reporting is supported or rejected. A CSV import will produce all of these on day one.
**Class:** PROPOSED.

### G-61 — The call tree is a single linear chain
**Recommended:** an **alternate contact per person**, plus **cycle detection and a reachability check** — every person must be reachable from the root, not merely have a populated next-contact field. The current model reports a chain as complete when one unreachable person has silently orphaned everyone after them.
**Class:** PROPOSED.

### G-62 — Staff and Platform User records have no identity-matching rule
**Recommended:** a **stable external ID column in the CSV template** as the natural key, a defined merge and conflict flow with a review screen, and **never a silent overwrite**. Promoting a Staff Member to a Platform User links the records rather than creating a second one.
**Class:** PROPOSED.

### G-63 — Certification expiry has no defined consequence
**Recommended:** warn and flag; **do not retroactively invalidate completed work** — a result signed off while the certification was valid stays valid. Whether an expired certification blocks *new* test assignment is a Client decision. Add a certification-type library (free text makes the register unreportable) and allow the certificate document to be attached.
**Class:** OPEN — CLIENT (blocking or not) + PROPOSED (the rest).

### G-64 — The hardware register is too thin for the DORA claim
**Recommended:** **soften the claim for MVP** — three fields are a device list, not an ICT asset register. List the extension (location, criticality, lifecycle and end-of-support status, owner, linked systems and functions) as a costed option rather than implying the current fields satisfy the obligation.
**Class:** OPEN — CLIENT; recommend softening.

### G-65 — Non-employee committee members
**Recommended:** support **non-employee governance records**, and platform logins for them where they sit in an approval path. Small firms rely on external non-executive directors for exactly the second senior sign-off the workflow demands — excluding them makes the approver-pool problem in G-05 materially worse.
**Class:** OPEN — CLIENT; recommend supporting.

---

# H. Non-functional, security, operations

### G-66 — No backup, recovery point or recovery time requirement
**Recommended:** the capability is designed; the **targets are not proposed**. Buildable and committable now: a backup account with no trust path from production, immutable retention on the longer-retention copies, **automated restore verification** including decryption with the correct firm key, and record copies outside the primary failure domain within the EU. **No recovery time or recovery point figure should be committed until it has been measured** — and the availability target itself is recorded as an open question in the PRD, so the investment question is open too.
**Class:** ALREADY DESIGNED (capability): [secure-backups](../research/Data%20And%20Document%20Security/secure-backups.md), [disaster-recovery](../research/Data%20And%20Document%20Security/disaster-recovery.md). OPEN — CLIENT (targets).

### G-67 — The client-owned AWS account has no operating model
**Recommended:** settle six things before build: **root and billing custody**, **who pays the infrastructure bill** (it is not in the build fee as described), **how deploy access is granted and revoked**, **the environment inventory and whose accounts they live in**, **who operates CI/CD and responds out of hours**, and **what happens to delivery-team access at project end**.

Design position to bring to that conversation: zero standing human access to production, dual-approved and session-recorded break-glass, split custody of root.

Also state the honest limit: **the immutability guarantee is bounded by the account owner's own controls.** "Not even SayOne's administrators can modify the log" is true and insufficient — the account owner's root can. Ties to G-11 and G-68.
**Class:** OPEN — CLIENT. Blocker. See [reference-cloud-architecture](../research/Data%20And%20Document%20Security/reference-cloud-architecture.md).

### G-68 — Audit-log immutability has no technical mechanism
**Recommended:** already designed — **hash-chained audit events written to a dedicated write-only log archive account** with write-once retention, deletion denied to every principal including root, key deletion blocked while records are in retention, and scheduled verification of the chain. Plus a **documented verification procedure** an auditor can actually run.
**Class:** ALREADY DESIGNED: [audit-logging](../research/Data%20And%20Document%20Security/audit-logging.md), [immutable-evidence-retention](../research/Data%20And%20Document%20Security/immutable-evidence-retention.md).

### G-69 — No malware scanning of uploads
**Recommended:** already designed — **quarantine, scan, promote**: multi-engine scanning, structural and archive-bomb checks, content type determined by inspection rather than declaration, **fail closed** on scanner error, parsing in an isolated account with no credentials and no network egress, and a watermarked server-side preview as the default access mode rather than raw download.
**Class:** ALREADY DESIGNED: [secure-media-storage](../research/Data%20And%20Document%20Security/secure-media-storage.md).

### G-70 — Storage cost is unbounded on a fixed-price contract
**Recommended:** three things — **per-plan storage allowances with a stated overage policy**, **lifecycle tiering to colder storage that preserves the write-once retention lock**, and an explicit statement of **who absorbs storage cost** in a client-owned account. Model the cost before setting the maximum file size, not after: video and screen recordings are accepted evidence types and nothing can ever be deleted.
**Class:** OPEN — CLIENT (commercial) + PROPOSED (tiering and allowances).

### G-71 — Authentication is under-specified for the enterprise buyer
**Recommended:**
- **Second factor:** an authenticator app or push approval rather than SMS. Both satisfy the PRD's "verification step on their phone", and SMS carries SIM-swap risk that is elevated for crypto-sector staff. **The choice is an open decision** — this is the recommendation, not a selection.
- **Add explicitly:** password policy, account lockout and brute-force protection, session lifetime and idle timeout, concurrent-session policy.
- **MFA recovery** with dual approval and full audit. The two-Super-Admin rule prevents role lockout, not device loss — if both admins lose their phones there is currently no path, and the Portal team recovering it collides with the Portal visibility boundary.
- **SSO, SCIM provisioning and IP allowlisting: state as out of MVP.** They are common procurement gates, so the exclusion needs to be visible rather than discovered.
**Class:** OPEN — CLIENT (factor) + PROPOSED (policies and recovery) + LIMITATION (SSO/SCIM). See [identity-and-access-management](../research/Data%20And%20Document%20Security/identity-and-access-management.md).

### G-72 — The concurrency figure contradicts the sizing guidance
**Recommended:** treat the stated per-firm concurrency figure as a **ceiling for load testing**, not an expectation, and note the contradiction so nobody sizes infrastructure from it. The number that actually drives cost — total firms and total concurrent users in year one — is still unanswered and is already an estimation blocker in the PRD. Add data-volume targets (tests per firm per year, evidence GB per firm per year, findings per period) at the same time.
**Class:** OPEN — CLIENT.

### G-73 — No observability or platform incident-response requirement
**Recommended:** already designed — detections as code with tests, log-source heartbeats, priority alerts including cross-firm and protected-record tripwires, and an incident procedure that includes **notifying affected firms**, which their own regulatory obligations require them to receive. The **notification deadline is contractual** and is not proposed here as a number.
**Class:** ALREADY DESIGNED: [security-monitoring](../research/Data%20And%20Document%20Security/security-monitoring.md). OPEN — CLIENT (the deadline).

### G-74 — No environment or test-data strategy, though UAT carries a contractual obligation
**Recommended:** a **synthetic data fixture factory covering every accepted evidence type**, no production data outside production under any circumstance, a seeded demo tenant, and a **named UAT environment as a deliverable** — the accuracy commitment is measured there, so it cannot be improvised.
**Class:** PROPOSED. See [secure-sdlc](../research/Data%20And%20Document%20Security/secure-sdlc.md).

### G-75 — No accessibility requirement
**Recommended:** make it an explicit decision — **target WCAG 2.2 AA, or state the exclusion**. Recommend stating a target: EU-market B2B procurement will ask, and retrofitting accessibility is far more expensive than building to it.
**Class:** OPEN — CLIENT.

### G-76 — Unmeasurable wording in a fixed-price contract
**Recommended:** convert each vague phrase into a **testable acceptance criterion** — named target viewports and the specific flows that must work on mobile (report sign-off, escalation acknowledgement, closure sign-off) and those that need not; a defined metric set for the dashboard; defined lead times for proactive alerts; a stated load profile for performance. Do this for every such phrase before signature; each one is a future dispute.
**Class:** PROPOSED (acceptance criteria).

### G-77 — No support, maintenance or warranty terms
**Recommended:** a **separate services agreement** covering defect warranty and its definition, support hours, response and resolution targets, **who operates production**, ongoing regulatory-content maintenance, and any service credits. None of this is inside the build fee as described, and it has direct architectural consequences via G-67.
**Class:** OPEN — CLIENT (commercial).

### G-78 — No secure SDLC, penetration testing or rate limiting requirement
**Recommended:** already designed — blocking CI gates for secrets and critical vulnerabilities and tenant-isolation test failures, dependency and secret scanning, signed artefacts with provenance verified at admission, per-role and per-endpoint rate limiting, and an **independent penetration test with Critical and High findings remediated before real client data is accepted**.
**Class:** ALREADY DESIGNED: [secure-sdlc](../research/Data%20And%20Document%20Security/secure-sdlc.md), [supply-chain-security](../research/Data%20And%20Document%20Security/supply-chain-security.md), [secure-cicd](../research/Data%20And%20Document%20Security/secure-cicd.md).

---

# I. Platform Admin Portal

### G-79 — The Portal is under-specified but carries equal weight in the fixed fee
**Recommended: bound the deliverable explicitly.** Proposed MVP Portal scope, to be accepted or trimmed as a whole:
- Content authoring for requirements and multi-step procedures, with evidence checklists, sampling rules and minimum sizes.
- **Version history and a review-and-publish workflow** with named approvers, defined states, and a rollback or unpublish path for a bad publication.
- **Draft and preview** before publication.
- **Portal user management, Portal roles beyond a single super admin, and Portal MFA.**
- **A Portal audit log.** A change to a test procedure changes every firm's obligations; if any action needs auditing, this one does.
- Bulk import and export, because the initial library is dozens of procedures and authoring them one at a time in a web form is not viable.
- Firm list, system settings, usage report.
Anything beyond this list is an amendment. Per-jurisdiction content variants (G-17) and requirement sub-scopes (G-45) should be decided as part of this scoping, since both are Portal content model changes.
**Class:** OPEN — CLIENT. Blocker.

### G-80 — No seat enforcement despite seat-based pricing
**Recommended:** **allow with a warning and report**, rather than blocking invitations. Blocking can lock a firm out of the very governance actions the product exists to enforce, and it worsens the approver-pool problem in G-05. Notify both the Firm Super Admin and the Portal team; commercial follow-up happens off-platform through the reseller.
**Class:** OPEN — CLIENT.

### G-81 — The marketing site is three sentences on the critical path
**Recommended:** bound it before it is built — page inventory, who writes the copy, where leads land, **consent and cookie compliance** (mandatory for an EU-facing site and currently unmentioned anywhere), analytics choice with a residency check, and SEO basics. **Resolve the domain and branding questions first**: they block the site and each other.
**Class:** OPEN — CLIENT.

---

# J. Commercial and contractual

### G-82 — The IP clause has no background-IP or open-source carve-out
**Recommended redraft, for counsel to finalise:**
- **Full assignment of purpose-built deliverables** to the Client — this is the intent and it is achievable.
- **Background IP retained** by the contractor, with a perpetual, irrevocable, worldwide, sublicensable licence to the Client to use it as embedded in the platform.
- **Third-party open-source components governed by their own licences**, with a delivered software bill of materials. No contract can override an upstream licence, and "100% exclusive ownership of any code within the platform" is unperformable while any open-source component exists — which is always.
- **An operating licence back** to the contractor for as long as it deploys, operates or maintains the platform. "Zero implied licenses" as drafted arguably prevents the contractor from running the code it wrote, which conflicts with it operating the deployment.
Note the security research already derives a **licence deny-list** from this clause, so the redraft feeds directly into the dependency policy.
**Class:** OPEN — LEGAL. Blocker; flag before signature.

### G-83 — The baseline-freeze clause is incompatible with the open-gaps process
**Recommended:** add a **carve-out**: resolutions of the named open questions and workflow gaps, recorded in a **controlled decision log**, are deemed part of the baseline and do not require a contract amendment. Define what counts as a "structural change" and name who arbitrates. The alternative — resolving everything before signature — is cleaner but is unlikely to be achievable on the current timeline.

**Also missing and worth producing as contract annexes:** project timeline, the milestone list the milestone contract refers to, per-requirement acceptance criteria (UAT is currently defined only for the accuracy bar), a change-control process, and a definition of done.
**Class:** OPEN — CLIENT and LEGAL. Blocker.

---

# K. Document integrity

### G-84 — The exclusions section does not exist
**Recommended:** **write it before signature.** Seed it from the items this document recommends as limitations, so the exclusions list is evidence-based rather than improvised:

> English-only UI and reports · no historical data import · no external auditor or regulator access · no SSO, SCIM or IP allowlisting · manual attestation for regulator submission (no submission API) · no public API · no HR system integration · no dedicated mobile app · no DORA Register of Information · no AML instrument content in the requirement library *(subject to G-12)* · no sample generation *(subject to G-33)*

Under a strict fixed-price contract with a freeze clause, a document with no exclusions section means everything not explicitly excluded is arguably in scope.
**Class:** OPEN — CLIENT. Blocker.

### G-85 — Five requirement IDs are missing with no explanation
**Recommended:** publish a **reconciliation table** mapping the previous requirement set to the current one, marking each missing ID *withdrawn* or *merged into `<id>`*. Estimators currently cannot tell whether a requirement was deleted or lost, and one of the gaps sits exactly on a section boundary — the highest-risk place for a dropped requirement.
**Class:** PROPOSED.

### G-86 — Two conflicting version schemes in one document
**Recommended:** **one version identifier and one date on the signed artefact.** If July commitments are inside it — and they are, including the accuracy bar and the IP clause — then it is not "as of June 2026", and the signature's scope is ambiguous until that is fixed.
**Class:** PROPOSED (documentation).

### G-87 — The gap list's evidence base is voided by its own supremacy clause
**Recommended:** **pull the residual detail forward** into the PRD before freeze. That is cleaner than carving out an exception to the version-supremacy rule, and it removes the awkwardness of resolving gaps by citing documents the same section forbids citing.
**Class:** OPEN — CLIENT.

### G-88 — The signed `.docx` and the readable `.md` can drift
**Recommended:** a **CI check** that regenerates the markdown from the `.docx` and fails the build on any difference. The convention that the `.docx` wins is only safe if divergence is detected.
**Class:** PROPOSED.

---

# Conflicts with the gap analysis's own recommendations

Three places where this document deliberately does **not** adopt the analysis's suggested fix:

| Gap | Analysis suggests | Recommended here instead | Why |
|---|---|---|---|
| **G-20** | Crypto-shredding as the erasure mechanism ("delete the key, keep the audit stub") | **Do not adopt it.** No deletion path for protected classes; minimise personal data at source; document the retention position; escalate the residual conflict as a legal decision | Destroying a firm's key renders six-year records unreadable. That is deletion by another route, and it contradicts the PRD's rule that these records cannot be deleted by anyone including administrators |
| **G-11** | A firm-held key as the answer to account-owner visibility | **Out of MVP.** Use per-firm keys with bound encryption context, separation of key administration from decrypt rights, zero standing access, and operator access surfaced in the firm's audit trail. Disclose the residual position | A firm-held key lets a firm make its own non-deletable records unreadable — the same collision as G-20, moved to the customer side |
| **G-28** | Names a specific managed model service as the example resolution | **Provider and model stay unselected**, chosen against stated criteria (EU residency, no-training and no-retention terms, measured accuracy, cost, exit) | The PRD names no provider. Recording one as the answer converts an open decision into an assumed commitment |

---

# Decision sequencing

Following the analysis's own priority order, with the resolutions attached:

**Before signature — contract and scope integrity**
G-84 exclusions section · G-83 freeze carve-out · G-82 IP redraft · G-12 AML scope · G-79 Portal scope boundary · G-67 AWS operating model · G-77 support and maintenance terms.

**Before estimation — materially changes cost**
G-33 sampling model · G-28 inference hosting · G-27 accuracy definition · G-20 erasure position · G-23 offboarding · G-70 storage and cost model · G-14 Register of Information in or out · G-72 real scale figures.

**Before the relevant sprint**
All of Section A (the role contradictions — most close in a single workshop) · G-35 period object · G-39 service-line change handling · G-50 report distribution · G-53 clocks and calendars · G-59/G-60/G-61 department taxonomy, org chart validation, call tree · G-42 version pinning.

**Write down as limitations rather than build**
G-30 English-only UI · G-47 no historical import · G-58 no auditor access · G-71 no SSO · G-16 manual submission attestation · G-14 no Register of Information · G-64 softened hardware-register claim.

**Scope additions recommended for approval**
G-07 delegation · G-37 finding comment thread · G-46 evidence library · G-48 bulk assignment · G-49 global search.

---

**Nothing in this document has been approved.** Each resolution is a recommendation with its class stated. Where a resolution would add scope to a fixed-price milestone contract, it says so.
