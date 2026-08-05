# ComplianceIQ PRD v4.0 — Gap Analysis and Recommended Resolutions

**Findings and recommended resolutions, one entry per gap.**

| | |
|---|---|
| **Baseline reviewed** | [`PRD.md`](PRD.md) — PRD v4.0, 791 lines (PRD v4.0 + 25 Jun call + Sosinna Drive comments layered in) |
| **Analysis date** | 2026-07-29 |
| **Merged** | 2026-08-05 — supersedes the separate gap-analysis and gap-resolutions documents |
| **Total findings** | 88 (G-01 … G-88) |
| **Status** | **Nothing in this document is approved.** It is the decision agenda, not the decision |

[`PRD.md`](PRD.md) remains the sole source of truth. Nothing here changes it.

---

## How to read this

Each entry states the **finding** (what the PRD gets wrong, omits, or contradicts) and the
**recommended resolution** (what to do about it), with a severity and a class.

These are findings the PRD does **not** already track. Section 15 (open questions) and Section 16
(11 workflow gaps) are the document's own self-declared gap list — items already listed there are
excluded unless the PRD's stated resolution is itself wrong, incomplete, or in conflict with
something else.

Entries are ordered by subject area, most product-critical first; document integrity and versioning
hygiene is last (Section K).

### Severity

| Severity | Meaning |
|---|---|
| **BLOCKER** | Cannot be safely estimated, signed, or frozen without an answer |
| **HIGH** | Will cause rework, contract dispute, or regulatory exposure if left |
| **MEDIUM** | Needs a decision before the relevant sprint |
| **LOW** | Clarification / hygiene |

### Resolution class

| Class | Meaning |
|---|---|
| **PROPOSED** | An implementation recommendation that delivers something the PRD already requires. No new scope. Buildable once accepted |
| **SCOPE ADDITION** | Genuinely new scope. Solves a real problem, but it is not in the PRD and would need Client approval — and, under the fixed-price milestone model with a baseline-freeze clause, an amendment |
| **OPEN — CLIENT** | A product, commercial or domain decision only the Client can make. A recommendation is given; **no default is adopted** |
| **OPEN — LEGAL** | Needs qualified counsel before it is contracted or represented to a customer |
| **LIMITATION** | Recommended answer is to write it down as an explicit exclusion rather than build it |
| **ALREADY DESIGNED** | The security research set already answers this. Link given; nothing new to decide beyond accepting the design |

### Conventions

- PRD requirement IDs are quoted in findings where you need them; resolutions name requirements
  descriptively, because IDs move between PRD versions.
- Security-side resolutions link into [`../research/Data And Document Security/`](../research/Data%20And%20Document%20Security/).
- Where a resolution deliberately departs from the finding's own suggested fix, it says so, and the
  three such cases are collected in [Conflicts](#conflicts-between-finding-and-resolution).

---

## Index

| ID | Sev | Class | Subject |
|---|---|---|---|
| **A. Contradictions inside the document** | | | |
| [G-01](#g-01--high--remediation-owner-visibility-is-a-three-way-contradiction-not-two-way) | HIGH | OPEN — CLIENT | Remediation Owner visibility |
| [G-02](#g-02--high--itsystems-admin-cannot-see-tests-but-the-workflow-requires-them-to) | HIGH | PROPOSED | IT Admin cannot see tests it must upload to |
| [G-03](#g-03--high--senior-management-is-defined-as-read-only-but-performs-three-write-actions) | HIGH | PROPOSED | Senior Management read-only vs. sign-off |
| [G-04](#g-04--high--the-aml-officer-is-an-actor-in-the-workflow-but-not-one-of-the-eight-system-roles) | HIGH | OPEN — CLIENT · PROPOSED | AML Officer is not a system role |
| [G-05](#g-05--high--two-person-sign-off-rules-can-deadlock-in-the-target-customer-size) | HIGH | OPEN — CLIENT · PROPOSED | Two-person sign-off deadlock |
| [G-06](#g-06--high--only-fr-15-has-a-minimum-headcount-guard-and-it-guards-the-wrong-role) | HIGH | PROPOSED | Minimum-headcount guard on wrong role |
| [G-07](#g-07--high--no-delegation-deputy-or-out-of-office-model-the-cco-is-a-single-point-of-failure) | HIGH | SCOPE ADDITION | No delegation / deputy model |
| [G-08](#g-08--medium--the-three-findings--high-rule-collides-with-officer-confirms-the-rating) | MEDIUM | OPEN — CLIENT · PROPOSED | Auto-rating vs. officer confirmation |
| [G-09](#g-09--high--section-81-wrongly-ties-compliance-test-findings-to-the-dora-4-hour-clock) | HIGH | OPEN — CLIENT | Findings wrongly wired to DORA 4-hour clock |
| [G-10](#g-10--medium--fr-47-plan-locked-before-report-and-gap-06-owner-assigned-after-consensus-may-be-circular) | MEDIUM | PROPOSED | Milestone confirmation vs. CCO rejection |
| [G-11](#g-11--medium--sa-06-portal-cannot-see-firm-data-vs-the-25-jun-call-vs-nfr-01) | MEDIUM | OPEN — CLIENT + LEGAL · ALREADY DESIGNED | Account owner sees every tenant's data |
| **B. Regulatory / domain scope** | | | |
| [G-12](#g-12--blocker--the-stated-regulatory-scope-is-mica--dora-but-the-product-is-full-of-aml-content) | BLOCKER | OPEN — CLIENT | AML content vs. MiCA/DORA scope |
| [G-13](#g-13--high--article-citations-need-domain-expert-verification-before-they-are-hardcoded-into-the-report) | HIGH | PROPOSED · OPEN — CLIENT | Unverified article citations |
| [G-14](#g-14--high--the-dora-register-of-information-is-entirely-absent) | HIGH | OPEN — CLIENT (recommend LIMITATION) | DORA Register of Information absent |
| [G-15](#g-15--high--dora-incident-reporting-is-modelled-as-one-report-it-is-three) | HIGH | OPEN — CLIENT | DORA incident reporting is three reports |
| [G-16](#g-16--medium--fr-76-submits-it--there-is-no-submission-channel) | MEDIUM | PROPOSED | No regulator submission channel |
| [G-17](#g-17--medium--branch-jurisdictions-are-captured-but-no-jurisdiction-specific-content-model-exists) | MEDIUM | OPEN — CLIENT · PROPOSED | No jurisdiction content model |
| [G-18](#g-18--medium--res-02-significant-firm-gap-03-has-a-knock-on-the-prd-does-not-note) | MEDIUM | PROPOSED | Threat-led testing for significant firms |
| [G-19](#g-19--low--no-handling-of-regulatory-instruments-with-staged-application-dates) | LOW | PROPOSED | Staged application dates |
| **C. GDPR and data lifecycle** | | | |
| [G-20](#g-20--blocker--immutable-evidence-retention-directly-conflicts-with-gdpr-erasure-and-the-prd-never-mentions-it) | BLOCKER | OPEN — LEGAL · ALREADY DESIGNED | Immutability vs. GDPR erasure |
| [G-21](#g-21--high--no-pii-is-asserted-for-csv-imports-but-ignored-for-evidence-uploads) | HIGH | PROPOSED | PII controlled on CSV, open on uploads |
| [G-22](#g-22--high--there-is-no-data-disposal-process-at-end-of-retention) | HIGH | OPEN — LEGAL · PROPOSED | No disposal at end of retention |
| [G-23](#g-23--blocker--no-firm-offboarding--contract-termination-data-path) | BLOCKER | OPEN — CLIENT + LEGAL | No firm offboarding path |
| [G-24](#g-24--high--sayonesynergy-is-itself-an-ict-third-party-provider-under-dora-and-the-prd-never-treats-it-as-one) | HIGH | PROPOSED · OPEN — CLIENT | Platform is itself a DORA ICT provider |
| [G-25](#g-25--medium--no-dpa-no-sub-processor-list-no-international-transfer-position) | MEDIUM | PROPOSED · OPEN — LEGAL | No DPA / sub-processor / transfer position |
| [G-26](#g-26--medium--the-revenue-source-file-is-highly-commercially-sensitive-and-gets-no-special-treatment) | MEDIUM | PROPOSED | Revenue file untreated |
| **D. AI / OCR / regulatory monitoring** | | | |
| [G-27](#g-27--blocker--the-85-accuracy-commitment-has-no-measurable-definition) | BLOCKER | OPEN — CLIENT | 85% accuracy undefined |
| [G-28](#g-28--blocker--using-an-llm-appears-to-violate-nfr-03-as-written-and-no-ai-stack-is-specified) | BLOCKER | OPEN — CLIENT · ALREADY DESIGNED | LLM vs. EU residency; no AI stack |
| [G-29](#g-29--high--ocr-is-promised-with-no-accuracy-target-no-language-scope-and-no-failure-path) | HIGH | PROPOSED · OPEN — CLIENT | OCR undefined |
| [G-30](#g-30--high--the-entire-product-has-no-internationalisation-position) | HIGH | OPEN — CLIENT (recommend LIMITATION) | No i18n position |
| [G-31](#g-31--medium--sa-03-regulatory-monitoring-has-no-latency-sla-and-no-feed-failure-path) | MEDIUM | PROPOSED · OPEN — CLIENT | Feed latency and failure path |
| [G-32](#g-32--medium--fr-51fr-54-republish-third-party-regulator-content-with-no-licensing-position) | MEDIUM | OPEN — LEGAL · PROPOSED | Regulator content licensing |
| **E. Testing module** | | | |
| [G-33](#g-33--blocker--it-is-not-defined-whether-the-platform-selects-the-sample-or-merely-records-it) | BLOCKER | OPEN — CLIENT | Sample generation vs. record-keeping |
| [G-34](#g-34--high--minimum-sample-size-is-enforced-but-never-specified) | HIGH | PROPOSED · OPEN — CLIENT | Minimum sample size unspecified |
| [G-35](#g-35--high--testing-period--testing-cycle-is-never-defined-as-an-object) | HIGH | PROPOSED | Testing period is not an object |
| [G-36](#g-36--high--repeat-finding-detection-fr-46-has-no-matching-rule-and-only-a-one-period-lookback) | HIGH | PROPOSED · OPEN — CLIENT | Repeat-finding matching rule |
| [G-37](#g-37--high--findings-consensus-happens-outside-the-platform-breaking-the-single-source-of-truth-claim) | HIGH | SCOPE ADDITION | Consensus happens off-platform |
| [G-38](#g-38--high--requirement-level-not-applicable-has-no-owner-and-conflicts-with-automatic-test-loading) | HIGH | PROPOSED | Requirement-level N/A has no owner |
| [G-39](#g-39--high--no-rule-for-what-happens-to-in-flight-and-historical-work-when-service-lines-change) | HIGH | PROPOSED | Service-line change handling |
| [G-40](#g-40--medium--re-uploading-the-revenue-file-changes-the-firms-regulatory-obligations-with-no-approval-gate) | MEDIUM | PROPOSED | Revenue re-upload has no gate |
| [G-41](#g-41--medium--the-revenue-file-template-does-not-exist-and-is-on-the-critical-path) | MEDIUM | PROPOSED · OPEN — CLIENT | Revenue template missing |
| [G-42](#g-42--medium--gap-10s-second-half-is-the-more-important-half-and-is-being-under-weighted) | MEDIUM | PROPOSED | Rule-version pinning under-weighted |
| [G-43](#g-43--medium--no-behaviour-defined-for-retiring-a-requirement-id-or-a-test-procedure-mid-cycle) | MEDIUM | PROPOSED | Mid-cycle requirement retirement |
| [G-44](#g-44--medium--fr-53-trend-comparison-is-invalid-across-procedure-versions) | MEDIUM | PROPOSED | Trend comparison across versions |
| [G-45](#g-45--medium--partial-testing-fr-19-has-no-coverage-model) | MEDIUM | PROPOSED | Partial testing has no coverage model |
| [G-46](#g-46--medium--evidence-shelf-life-fr-28-has-no-source-of-truth) | MEDIUM | PROPOSED · SCOPE ADDITION | Evidence shelf life; no evidence library |
| [G-47](#g-47--medium--no-historical-data-import-at-onboarding) | MEDIUM | LIMITATION | No historical import |
| [G-48](#g-48--low--no-test-cloning-bulk-assignment-or-carry-forward-of-prior-period-setup) | LOW | SCOPE ADDITION | No cloning / bulk assignment |
| [G-49](#g-49--low--no-global-search) | LOW | SCOPE ADDITION | No global search |
| **F. Reports, notifications, dashboard** | | | |
| [G-50](#g-50--high--fr-59-auto-emails-an-unencrypted-report-containing-every-open-compliance-failure) | HIGH | PROPOSED · OPEN — CLIENT | Report auto-email leak path |
| [G-51](#g-51--medium--exactly-six-distribution-lists-fixed-with-no-external-recipient-model) | MEDIUM | OPEN — CLIENT | Six fixed distribution lists |
| [G-52](#g-52--medium--acknowledged-is-tracked-but-never-defined) | MEDIUM | PROPOSED | "Acknowledged" undefined |
| [G-53](#g-53--medium--five-business-days-and-four-hours-have-no-calendar-or-timezone-definition) | MEDIUM | PROPOSED · OPEN — CLIENT | Clocks have no calendar model |
| [G-54](#g-54--medium--no-email-deliverability-bounce-or-provider-requirement) | MEDIUM | PROPOSED | No deliverability / bounce handling |
| [G-55](#g-55--medium--no-report-generation-performance-target-and-the-dashboard-target-is-the-easy-path) | MEDIUM | PROPOSED | No report generation target |
| [G-56](#g-56--medium--no-report-preview-draft-or-regeneration-path) | MEDIUM | OPEN — CLIENT · PROPOSED | No draft/preview; fragile clock trigger |
| [G-57](#g-57--low--fr-48-more-metrics-can-be-added-based-on-the-ccos-preferences-is-unbounded) | LOW | PROPOSED | Unbounded metric set |
| [G-58](#g-58--low--no-externalregulatorauditor-read-only-access) | LOW | LIMITATION | No external auditor access |
| **G. Organisation & staff module** | | | |
| [G-59](#g-59--high--fr-66s-revenue-function-test-has-no-data-to-run-on) | HIGH | PROPOSED | Independence check has no data |
| [G-60](#g-60--high--the-org-chart-has-no-requirements-for-malformed-hierarchies) | HIGH | PROPOSED | Malformed org hierarchies |
| [G-61](#g-61--high--the-bcp-call-tree-is-a-single-linear-chain-with-no-branch-and-no-break-handling) | HIGH | PROPOSED | Call tree is a single chain |
| [G-62](#g-62--medium--staff-member-and-platform-user-records-have-no-linkage-or-identity-matching-rule) | MEDIUM | PROPOSED | No identity-matching rule |
| [G-63](#g-63--medium--certification-expiry-marks-a-record-non-compliant-with-no-defined-consequence) | MEDIUM | OPEN — CLIENT · PROPOSED | Certification expiry consequence |
| [G-64](#g-64--medium--hardware-inventory-is-too-thin-for-the-dora-claim-it-is-making) | MEDIUM | OPEN — CLIENT | Hardware register too thin |
| [G-65](#g-65--low--os-06-non-employee-committee-members-is-marked-no-update-but-interacts-with-g-05) | LOW | OPEN — CLIENT | Non-employee committee members |
| **H. Non-functional, security, operations** | | | |
| [G-66](#g-66--blocker--no-backup-rpo-or-rto-requirement--in-a-resilience-compliance-product) | BLOCKER | ALREADY DESIGNED · OPEN — CLIENT | No backup / RPO / RTO |
| [G-67](#g-67--blocker--ti-01-client-owned-aws-account-has-no-operating-model-attached) | BLOCKER | OPEN — CLIENT | AWS account operating model |
| [G-68](#g-68--high--audit-log-immutability-has-no-technical-mechanism) | HIGH | ALREADY DESIGNED | Audit-log immutability mechanism |
| [G-69](#g-69--high--no-malware-scanning-of-uploads) | HIGH | ALREADY DESIGNED | No malware scanning |
| [G-70](#g-70--high--no-storage-quota-and-the-cost-model-is-unbounded-on-a-fixed-price-contract) | HIGH | OPEN — CLIENT · PROPOSED | Unbounded storage cost |
| [G-71](#g-71--high--authentication-is-under-specified-for-the-enterprise-buyer) | HIGH | OPEN — CLIENT · PROPOSED · LIMITATION | Authentication under-specified |
| [G-72](#g-72--high--nfr-05s-concurrency-figure-contradicts-ti-06s-sizing) | HIGH | OPEN — CLIENT | Concurrency figure contradicts sizing |
| [G-73](#g-73--medium--no-observability-monitoring-or-platform-incident-response-requirement) | MEDIUM | ALREADY DESIGNED · OPEN — CLIENT | No observability / incident response |
| [G-74](#g-74--medium--no-environment-or-test-data-strategy-though-uat-carries-a-contractual-obligation) | MEDIUM | PROPOSED | No environment / test-data strategy |
| [G-75](#g-75--medium--no-accessibility-requirement) | MEDIUM | OPEN — CLIENT | No accessibility requirement |
| [G-76](#g-76--medium--nfr-10s-mobile-requirement-is-unmeasurable-and-therefore-unacceptable-in-a-fixed-price-contract) | MEDIUM | PROPOSED | Unmeasurable wording |
| [G-77](#g-77--medium--no-support-maintenance-warranty-or-hypercare-terms) | MEDIUM | OPEN — CLIENT | No support / maintenance terms |
| [G-78](#g-78--medium--no-rate-limiting-penetration-testing-or-secure-sdlc-requirement-for-the-platform-itself) | MEDIUM | ALREADY DESIGNED | No secure SDLC / pen test |
| **I. Platform Admin Portal** | | | |
| [G-79](#g-79--blocker--the-portal-has-8-requirements-against-74-for-the-firm-application-yet-the-fixed-fee-covers-both-equally) | BLOCKER | OPEN — CLIENT | Portal under-specified |
| [G-80](#g-80--high--no-seat-enforcement-despite-seat-based-pricing) | HIGH | OPEN — CLIENT | No seat enforcement |
| [G-81](#g-81--medium--no-marketing-site-requirements-beyond-three-sentences) | MEDIUM | OPEN — CLIENT | Marketing site unspecified |
| **J. Commercial and contractual** | | | |
| [G-82](#g-82--blocker--the-cc-03-ip-clause-as-accepted-has-no-background-ip-or-oss-carve-out-and-is-probably-unperformable) | BLOCKER | OPEN — LEGAL | IP clause unperformable |
| [G-83](#g-83--blocker--the-baseline-freeze-clause-is-logically-incompatible-with-sections-15-and-16) | BLOCKER | OPEN — CLIENT + LEGAL | Freeze clause vs. open gaps |
| **K. Document integrity** | | | |
| [G-84](#g-84--blocker--section-12-does-not-exist) | BLOCKER | OPEN — CLIENT | Exclusions section missing |
| [G-85](#g-85--high--five-fr-ids-are-missing-with-no-explanation-fr-22-fr-23-fr-26-fr-29-fr-71) | HIGH | PROPOSED | Five FR IDs missing |
| [G-86](#g-86--medium--two-conflicting-version-schemes-in-one-document) | MEDIUM | PROPOSED | Two version schemes |
| [G-87](#g-87--medium--section-16s-evidence-base-has-been-declared-void-by-section-16s-own-note) | MEDIUM | OPEN — CLIENT | Gap list's evidence base voided |
| [G-88](#g-88--low--docx-is-the-signed-baseline-md-is-the-readable-copy-and-they-can-drift) | LOW | PROPOSED | `.docx` / `.md` drift |

---

# A. Contradictions inside the document

### G-01 — HIGH — Remediation Owner visibility is a THREE-way contradiction, not two-way
**Class:** OPEN — CLIENT

**Finding.** The PRD flags this as two-way (Section 9.1 flag: FR-52 vs. FR-42 comment). It is three-way:
1. Section 3.1 role table: "Sees only their own assigned tasks."
2. FR-52: personal view is "the only compliance view they need".
3. GAP-07 / FR-42 comment: "view access to everything, not just their own assigned item."

Resolving 2 vs. 3 without also amending 1 leaves the role definition table wrong.
*Also unanswered inside option 3:* "everything" — everything in the firm, or everything on Findings
they own a milestone for? A Remediation Owner is often a business-line manager, not compliance
staff. Giving a Trading desk head read access to every AML finding in the firm is a material
access-control decision, not a dashboard tweak.

**Recommended resolution.** Resolve to the **narrow** reading and amend all three places at once —
the role table, the personal-view requirement, and the gap answer. A Remediation Owner sees their
own milestones **plus the full context of the Findings they own** (finding text, severity, root
cause, the requirement and the test result it came from), and nothing else. Not the firm-wide
findings register.

**Why.** A Remediation Owner is frequently a business-line manager. Giving a trading desk head
standing read access to every AML finding in the firm is an access-control decision, not a dashboard
preference, and it works against least privilege. The "evidence of completion goes back to the
tester" loop that motivated the broad reading is satisfied by the narrow one.

**Interim engineering position.** Build the narrow reading behind a single policy switch so the broad
reading remains a configuration change, not a rewrite. See
[open-questions](../research/Data%20And%20Document%20Security/open-questions.md) A-6.

### G-02 — HIGH — IT/Systems Admin cannot see tests, but the workflow requires them to
**Class:** PROPOSED

**Finding.** Section 3.1: IT/Systems Admin "Cannot see compliance tests or findings."
Section 7.1 step 3: "Other team members (for example, the IT manager) can upload specialist evidence
to specific steps."
These cannot both be true. Uploading evidence to a test step requires seeing the test step. Needs a
scoped "contributor on assigned test step" permission that is not in the eight-role model.

**Recommended resolution.** A **scoped step-level contributor grant**, not a ninth role. The Lead
Tester or CCO grants a named user upload rights on a named test step; the grant confers visibility
of that step only, never the result, findings, or other steps; it expires when the test is
submitted; grant and use are both audited.

**Why.** Preserves the eight-role model the PRD fixes while making the workflow it describes actually
possible.

### G-03 — HIGH — Senior Management is defined as read-only but performs three write actions
**Class:** PROPOSED (no build impact)

**Finding.** Section 3.1: "Read-only access to dashboards and reports." Yet FR-44 requires their
sign-off to close a Finding, FR-58 requires their report sign-off, and Section 8.1 requires them to
acknowledge escalations within five business days. Sign-off is a write.

**Recommended resolution.** Rewrite the role definition as **"read-only on operational data; write on
approvals, sign-offs and acknowledgements"**. Documentation correction; the permission model already
has to support the writes because three requirements demand them.

### G-04 — HIGH — The AML Officer is an actor in the workflow but not one of the eight system roles
**Class:** OPEN — CLIENT on whether the constraint is hard or advisory; PROPOSED on the mechanism

**Finding.** Section 7.1 step 11 makes the AML Officer a mandatory gate ("separately reviews and
formally agrees"), and FR-55 makes the report un-generatable without it. The role is described only
as "a Senior Management or CCO-level user". FR-64 separately names the MLRO.
*Scenario:* a firm's MLRO is a Compliance Officer by system role, not Senior Management or CCO. The
AML sign-off gate cannot be satisfied, and no report can ever be generated.
Either add a ninth system role, or make AML Officer an assignable flag on a user.

**Recommended resolution.** Make **AML Officer an assignable attribute on a user**, independent of the
eight system roles, assigned by the Firm Super Admin, changes audited. Enforce the PRD's constraint
("Senior Management or CCO-level") as a **warning at assignment rather than a hard block**, so a firm
whose MLRO is a Compliance Officer is not permanently unable to generate a report.

**Why.** An attribute avoids a ninth role and its permission matrix, and it matches how firms actually
allocate the MLRO function.

### G-05 — HIGH — Two-person sign-off rules can deadlock in the target customer size
**Class:** OPEN — CLIENT on the minima; PROPOSED on the guard and the exception path

**Finding.** TI-06 says MVP firms are capped around 50 people with ~10 platform users. FR-64 confirms
one person often holds two roles (CCO + MLRO). Against that:
- FR-32: two senior approvers on every WSP mapping, excluding the policy author.
- FR-44 + FR-45: CCO + one Senior Management to close a Finding, excluding the recorder.
- FR-21c: sample change needs "one other senior team member".

*Scenario:* a 12-person CASP with one CCO, one compliance officer, and a two-person board where one
board member wrote the policy. The remaining approver pool is size 1. Every closure blocks.
The PRD never states a minimum viable governance headcount, nor a documented break-glass path.

**Recommended resolution.** Two things together.
1. **Governance-capacity guard**, modelled on the existing two-Super-Admin guard: the platform knows
   the eligible approver pool for each approval type, warns when a pool reaches one, and blocks
   nothing silently.
2. **A documented exception path** — never a silent bypass. Where the pool is genuinely exhausted,
   the action proceeds only with a written justification, is flagged in the audit trail as an
   exception, and appears on the CCO dashboard and in the report.

The actual minima ("at least one CCO and two Senior Management users") are a Client decision.

### G-06 — HIGH — Only FR-15 has a minimum-headcount guard, and it guards the wrong role
**Class:** PROPOSED

**Finding.** FR-15 requires two Firm Super Admins. Firm Super Admin does not appear in any approval
path. The roles that actually block the workflow if vacant — CCO, Senior Management — have no
minimum.
*Scenario:* the sole Senior Management user resigns. Every Finding in the firm becomes uncloseable
and no report can be signed off. Nothing in the platform warns of this.

**Recommended resolution.** Extend the same guard to the roles that actually block the workflow — CCO
and Senior Management — using the G-05 mechanism. Warn on the dashboard and notify the Firm Super
Admins.

### G-07 — HIGH — No delegation, deputy, or out-of-office model. The CCO is a single point of failure
**Class:** SCOPE ADDITION — not in the PRD; recommend adding before freeze

**Finding.** Only the CCO can: assign tests (FR-20), approve tests (step 10), confirm milestone dates
(step 12), generate the report (FR-55), and co-sign closures (FR-44).
*Scenario:* CCO takes three weeks' leave at quarter end. No test can be assigned, no test approved,
no report generated. There is no "acting CCO" concept and no delegation-with-audit-trail feature.
This is a mandatory feature for a governance product, and it is absent entirely.

**Recommended resolution.** **Time-boxed delegation** as an explicit, audited grant: grantor, grantee,
scope (which powers), start and end, reason. Every delegated action records "X acting for Y".
Auto-expiry with no silent renewal. **Delegation may never collapse a two-person rule onto one
person** — the exclusion rules are evaluated on the acting identity *and* the principal.

**Why.** The PRD concentrates test assignment, test approval, milestone confirmation, report
generation and closure co-signature in one role. For a governance product this is a functional
defect, not a nicety.

### G-08 — MEDIUM — The "three findings = High" rule collides with "officer confirms the rating"
**Class:** OPEN — CLIENT on the weighting rule (a domain judgement); PROPOSED on the override mechanism

**Finding.** Section 8.1 makes any test with 3+ findings automatically High. Section 8.3 confirmed
decision: "Risk rating is calculated automatically ... the compliance officer confirms the rating,
they do not manually enter it." No downgrade path is defined.
*Scenario:* a documentation test produces three trivial findings (three policies with a stale version
date in the footer). It is auto-rated High, which fires immediate alerts to the CCO and every Senior
Management user, opens a five-business-day acknowledgement clock, and per Section 8.1 "may also
trigger a formal notification to the national regulator within four hours".

**Recommended resolution.** Keep automatic rating as the default, add **severity weighting** so three
trivial documentation findings do not outrank one control failure, and add an explicit **CCO
downgrade with mandatory written justification**, recorded and shown in the report. Both the computed
rating and the confirmed rating are retained.

### G-09 — HIGH — Section 8.1 wrongly ties compliance-test findings to the DORA 4-hour clock
**Class:** OPEN — CLIENT (domain confirmation from Sosinna), with the correction below as the recommendation

**Finding.** "Three or more findings in a test ... Under DORA, this may also trigger a formal
notification to the national regulator within four hours." The DORA major-incident notification
obligation is triggered by an *ICT-related incident*, not by the outcome of a compliance testing
exercise. Wiring a finding count to a regulator-notification workflow risks generating spurious
regulatory filings. The 4-hour path belongs only in Section 11 (FR-75/FR-76), and Section 8.1 should
be corrected.

**Recommended resolution.** **Decouple them.** The four-hour regulator notification path belongs only
to the ICT incident module, triggered by an ICT-related incident. A compliance test finding — of any
severity — never starts it. Correct the escalation table accordingly.

**Why.** As written, a documentation test with three trivial findings can put a firm on a path toward
a spurious regulatory filing. The reputational cost of a wrong filing is borne by the customer.

### G-10 — MEDIUM — FR-47 (plan locked before report) and GAP-06 (owner assigned after consensus) may be circular
**Class:** PROPOSED

**Finding.** FR-47/step 12: milestone dates must be confirmed with Remediation Owners before the
report can be generated. GAP-06 remains open on "whether a Remediation Owner can be assigned
pre-CCO-approval, and what happens to that assignment if the CCO rejects the test." If assignment is
only permitted post-approval, and approval is required before the report, and the report requires
confirmed owner dates, the ordering is tight but workable — but if the CCO rejects a test after
owners have already confirmed dates, the PRD does not say whether those confirmations are voided or
retained.

**Recommended resolution.** Define it explicitly — **CCO rejection returns confirmed milestone dates to
"proposed"**, and the original confirmations are retained in the audit trail with the rejection
reason. Owners are notified that their confirmation has been reopened. Nothing is silently voided and
nothing silently survives.

### G-11 — MEDIUM — SA-06 (Portal cannot see firm data) vs. the 25 Jun call vs. NFR-01
**Class:** OPEN — CLIENT and LEGAL — the disclosed position and the contractual terms that go with it.
Partly ALREADY DESIGNED: [key-management](../research/Data%20And%20Document%20Security/key-management.md),
[insider-threat-protection](../research/Data%20And%20Document%20Security/supporting-topics/insider-threat-protection.md)

**Finding.** The PRD flags this as an open question but does not surface the architectural
consequence: NFR-01 promises "No firm can ever access another firm's data, even accidentally", and
TI-01 puts the whole platform in an **AWS account owned solely by the Client (Synergy)**. Synergy is
also the reseller (CC-06) and a consulting firm that may compete with, or advise, the firms on the
platform. So the tenant-isolation guarantee protects firms from *each other* but grants the account
owner infrastructure-level access to every tenant's evidence, including sampled KYC records. A
contractual NDA clause (the SA-08 approach) is not a technical control.

**Recommended resolution.** State the position honestly rather than paper over it. In an AWS account
owned solely by the Client, **tenant isolation protects firms from each other; it does not protect
them from the account owner.** What can be done inside the MVP:
- per-firm keys with the firm identifier bound into the encryption context, and **separation of key
  administration from data-plane decrypt rights**, so no single operator role both administers keys
  and reads plaintext;
- zero standing human access to production, with dual-approved, session-recorded break-glass;
- operator access to a firm's data surfaced in **that firm's own audit trail**, so access is visible
  to the party it affects.

A firm-held key would be the only complete answer. It is **out of MVP scope**, and it collides with
the PRD's non-deletability rule — a firm could render its own six-year records unreadable. See
[future-scope](../research/Data%20And%20Document%20Security/future-scope/future-and-optional-scope.md) §1.

---

# B. Regulatory / domain scope

### G-12 — BLOCKER — The stated regulatory scope is MiCA + DORA, but the product is full of AML content
**Class:** OPEN — CLIENT. Do not let this be absorbed silently into a fixed fee

**Finding.** Named throughout: AML Officer sign-off gate (step 11), AML Analyst role, transaction
monitoring, customer risk ratings, sanctions screening, KYC file sampling, UBO refresh, AML/CFT
supervision, "AML-xx" test ID family (GAP-02). For an EU CASP, these obligations come from
**AMLD5/AMLD6, the 2024 AML package (AMLR/AMLD6 recast, AMLA), and the Transfer of Funds Regulation
(EU 2023/1113, the crypto Travel Rule)** — not from MiCA and not from DORA.
*Consequence:* either (a) the requirement library must cover AML instruments, in which case the scope
line "Regulations covered: MiCA and DORA" is wrong and the content-authoring effort is much larger
than estimated, or (b) AML tests are out of scope, in which case the AML Officer gate, the AML
sign-off, and the AML test family must be removed from the workflow.
This is the single largest scope ambiguity in the document and it is not in Section 15.

**Recommended resolution.** Decide explicitly, and price the decision. Two coherent positions:
- **(a) AML workflow, MiCA/DORA content.** Keep the AML Officer sign-off gate and AML-flavoured role
  names — they are governance workflow — but state that the requirement library covers MiCA and DORA
  instruments only. Any AML-derived test is out of scope until the library is extended.
- **(b) AML in scope.** Then the regulatory scope line is wrong, the content-authoring effort grows
  materially, and the AML instrument set (the 2024 AML package and the crypto Travel Rule regulation)
  must be named.

**Recommendation: (a) for MVP**, with (b) as a costed phase-2 content extension — it is a content
problem, not an architecture problem, so deferring it costs little later.

### G-13 — HIGH — Article citations need domain-expert verification before they are hardcoded into the report
**Class:** PROPOSED (mechanism) + OPEN — CLIENT (the sign-off itself)

**Finding.** SA-01: "TM-01 maps to the transaction monitoring obligations under MiCA Art. 92."
FR-66: "MiCA Art. 68(2) requires the compliance function to be independent."
MiCA Art. 92 concerns the prevention, detection and reporting of **market abuse**, and Art. 68
concerns **governance arrangements** for CASPs generally. AML transaction monitoring is not a MiCA
Art. 92 obligation. FR-40 makes every Finding carry a regulation article reference, and FR-56 puts
those references in the formal report given to senior management and shown to inspectors.
*Consequence:* a wrong article reference in an inspection-grade report is a reputational and liability
issue for both SayOne and Synergy.

**Recommended resolution.** Add **per-citation verification metadata** in the Portal — instrument,
article, source URL, verified by, verified on — and **block publication of a requirement whose
citation is unverified**. The formal report prints only verified citations. The initial mapping is
signed off by the Client's domain expert before any of it is authored.

### G-14 — HIGH — The DORA Register of Information is entirely absent
**Class:** OPEN — CLIENT; recommend LIMITATION for MVP with a costed phase-2 option

**Finding.** FR-73/FR-74 track CIFs, CTPPs, and vendors with five fields (name, service type, contract
ref, tier, next review date). DORA Art. 28(3) requires firms to maintain and annually submit to their
NCA a **Register of Information** on all ICT third-party arrangements, in a prescribed ESA template
with a large fixed schema (LEIs, function identifiers, contract dates, data locations, subcontracting
chains, substitutability assessments, exit plans). This is the most operationally demanding DORA
artefact and the one CASPs most need software for.
Either it is in scope — in which case FR-74's five fields are a fraction of the work — or it is
excluded, which needs stating (see G-84: there is no exclusions section to state it in).

**Recommended resolution.** **Explicitly exclude it from MVP** and say so in the exclusions section
(G-84). It is a large, schema-driven artefact against a prescribed supervisory template — genuinely
the thing CASPs most want software for, and therefore the strongest phase-2 candidate, but it cannot
be absorbed into the current vendor register's five fields.

### G-15 — HIGH — DORA incident reporting is modelled as one report; it is three
**Class:** OPEN — CLIENT; recommend in scope

**Finding.** FR-76 covers the initial notification and its clock. DORA requires an **initial
notification, an intermediate report, and a final report**, each with its own deadline and content,
plus reclassification handling if an incident later crosses the major threshold.
*Scenario:* an incident is classified as major on day 1, the initial notification fires, and the
platform then has nothing to track the intermediate report due days later or the final report due
weeks later. The firm misses a regulatory deadline while believing the platform is tracking it. That
is worse than not having the feature.

**Recommended resolution.** Model an incident as a **case with a sequence of obligations** — initial
notification, intermediate report, final report — each with its own due clock and content, plus
reclassification handling when an incident later crosses the major threshold. If that is too large
for MVP, then **track none of the clocks and say so**: partial tracking is worse than absent
tracking, because the firm believes a deadline is being watched when it is not.

**Recommendation: include it.** A DORA-positioned product that silently drops two of three regulatory
deadlines is a liability.

### G-16 — MEDIUM — FR-76 "submits it" — there is no submission channel
**Class:** PROPOSED (documentation and acceptance criteria)

**Finding.** NCA incident notification is per-country and generally via a national portal or secure
email; there is no pan-EU submission API. So "the CCO reviews it, edits it as needed, and submits it"
must mean *downloads it and submits it elsewhere*, and "the platform tracks whether the submission
has been made" must mean *the CCO ticks a box*. State this as a manual attestation, or the acceptance
test for FR-76 is unwritable.

**Recommended resolution.** State it as a **manual attestation**: the platform drafts and generates the
notification, records the download, and the CCO confirms submission with a timestamp and an external
reference number. No submission API is claimed anywhere in the product or the marketing site. This
makes the requirement testable.

### G-17 — MEDIUM — Branch jurisdictions are captured but no jurisdiction-specific content model exists
**Class:** OPEN — CLIENT (build or drop); PROPOSED on the minimal design

**Finding.** Section 5 says home jurisdiction "determines which national regulator's rules apply on
top of base MiCA" and branch jurisdictions "layer additional local rules". SA-07 only maps **service
lines** to Requirement IDs — nothing maps jurisdictions to Requirement IDs.
The 25 Jun note partly cuts this ("testing runs at the entity holding the EU licence; branch-level
testing not required for EU-only branches"), but that removes branch testing, not the
home-jurisdiction national overlay, which is still promised.

**Recommended resolution.** Minimal jurisdiction dimension — a **jurisdiction tag on each requirement
version** (EU-wide, or a named national regulator), filtered by the firm's home jurisdiction at test
loading. If that is not built, **drop the national-overlay promise from the onboarding section**
rather than leave a promise the content model cannot keep.

### G-18 — MEDIUM — RES-02 "significant firm" (GAP-03) has a knock-on the PRD does not note
**Class:** PROPOSED (as a stated limitation of the feature)

**Finding.** Beyond "who flags it", DORA advanced/threat-led testing (TLPT) is a specialist exercise
run by external red teams under a supervisory framework. If a firm is flagged significant, the
platform needs at minimum an evidence slot and a multi-year cycle, not a normal test procedure.

**Recommended resolution.** The platform **tracks, never guides**: an evidence slot, a multi-year cycle,
and a reminder. Threat-led testing is run by external specialists under a supervisory framework and
cannot be reduced to a test procedure. State this.

### G-19 — LOW — No handling of regulatory instruments with staged application dates
**Class:** PROPOSED

**Finding.** MiCA and DORA both have transitional/grandfathering provisions and RTS/ITS that land
after the base text. SA-03's monitoring records "effective date and date-of-download" (25 Jun note),
but nothing models "this requirement applies from date X" or "this requirement no longer applies
after date Y". A firm onboarding today should not be scheduled tests for a requirement that applies
next year.

**Recommended resolution.** **Applies-from and applies-until dates on each requirement version**, with
the scheduler filtering on them. A firm onboarding today is not scheduled tests for an obligation
that starts next year, and retired obligations stop scheduling without deleting history.

**Why.** Cheap to build now, expensive to retrofit into a scheduler and a six-year archive.

---

# C. GDPR and data lifecycle

### G-20 — BLOCKER — Immutable evidence retention directly conflicts with GDPR erasure, and the PRD never mentions it
**Class:** OPEN — LEGAL. ALREADY DESIGNED on the engineering side:
[immutable-evidence-retention](../research/Data%20And%20Document%20Security/immutable-evidence-retention.md),
[key-management](../research/Data%20And%20Document%20Security/key-management.md)

**Finding.** Section 2 and NFR-07: evidence files "cannot be deleted by anyone", audit log "cannot be
modified by anyone", six-year minimum, no user including administrators can delete. NFR-06: the
platform is GDPR-compliant as a data processor. Section 7.1 step 4 explicitly contemplates evidence
that is **sampled KYC files** — i.e. identity documents, addresses, and dates of birth of the CASP's
retail customers, who are data subjects with Art. 17 erasure rights and Art. 16 rectification rights.
*Scenario:* a retail customer of a CASP exercises the right to erasure. The CASP (controller) is
obliged to act, and instructs SayOne (processor). The platform is architecturally incapable of
deleting the file. The CASP cannot comply, and the platform is the reason.
The usual answer is a legal-obligation retention exemption under Art. 17(3)(b) — but that must be
*documented, scoped, and defensible*, and it is not automatic for every file a tester happens to
upload. None of this exists in the PRD, and NFR-06 is a single sentence.

**Recommended resolution — and this differs from the finding's own suggestion.** The finding proposes
crypto-shredding as the technical erasure mechanism. **Do not adopt it.** Destroying a firm's key
makes six-year records unreadable, which is deletion by another name and contradicts the PRD's rule
that evidence, results, reports and audit records cannot be deleted by anyone including
administrators. The same applies to deletion sagas and soft-delete grace periods.

What to do instead:
1. **Build no deletion path** for the protected record classes, and block key deletion while any
   record is inside its retention period.
2. **Minimise personal data at source** — see G-21. The cheapest erasure request to answer is the one
   about data that was never uploaded.
3. **Maintain a lawful-basis and retention register per data category**, so an Art. 17(3)(b)
   legal-obligation position is documented and scoped rather than assumed.
4. **Complete a data protection impact assessment** before real client data.
5. **Provide a documented refusal/restriction path** the controller can use, with the platform
   recording the request and the response.
6. **Escalate the residual conflict as a legal decision.** It is genuine, and it is not this
   project's to resolve unilaterally.

### G-21 — HIGH — "No PII" is asserted for CSV imports but ignored for evidence uploads
**Class:** PROPOSED

**Finding.** FR-72's 25 Jun note is explicit: monitoring extracts are "aggregated counts and
comparatives only, explicitly no PII and no individual customer-level data". Meanwhile FR-24 permits
arbitrary PDFs, images, video, audio and ZIPs, and the workflow expects KYC file review. The
controlled channel is locked down; the uncontrolled channel is wide open.

**Recommended resolution.** An **evidence-handling policy** with three parts — redaction guidance for
testers, a **"contains personal data" flag per upload** that drives access treatment and appears in
the retention register, and a mandatory field prompting the uploader to confirm minimisation. The
platform cannot inspect intent, so pair the technical flag with a contractual allocation of
responsibility to the firm as controller.

### G-22 — HIGH — There is no data disposal process at end of retention
**Class:** OPEN — LEGAL (when it ends) + PROPOSED (the mechanism). ALREADY DESIGNED:
[immutable-evidence-retention](../research/Data%20And%20Document%20Security/immutable-evidence-retention.md)

**Finding.** Everything says "minimum 6 years". Nothing says what happens at 6 years and one day.
Under GDPR storage limitation, indefinite retention is not the safe default it appears to be. Needed:
a retention-expiry job, a legal-hold override, and a disposal certificate for the firm's records.

**Recommended resolution.** A **retention service as the single source of truth** — per-class minimums,
legal hold, and extension supported. Build it so a retention *ceiling* can be added later without
data migration. **When retention ends is a Client and counsel decision**: the PRD states a six-year
floor and no ceiling, and indefinite retention is in tension with storage limitation.

### G-23 — BLOCKER — No firm offboarding / contract-termination data path
**Class:** OPEN — CLIENT and LEGAL

**Finding.** The PRD covers onboarding in detail (Section 5) and never covers exit. Open questions:
- A firm cancels. Data cannot be deleted (6-year rule). Who stores it, and who pays for the storage?
- Does the firm get a full export? In what format? Is the audit log included?
- CC-06 makes Synergy the reseller and contract owner — does the firm's data stay in Synergy's AWS
  account after the relationship ends, and on what lawful basis?
- Under DORA Art. 28, the *firm* must have a documented exit strategy for its ICT providers —
  ComplianceIQ is one. A compliance product that cannot support its own customer's exit plan will
  fail the customer's own vendor due diligence.

This is a blocker because it changes the storage cost model, the contract, and the architecture.

**Recommended resolution.** Define exit as a first-class flow before signature:
- **Full export** — records, evidence files, and the firm's audit trail, in documented formats,
  obtainable without assistance.
- **Custody of non-deletable records after exit** — who is controller, where they sit, on what lawful
  basis, and **who pays for six more years of storage**.
- **Access downgrade** rather than deletion: the firm's users lose operational access; the records
  persist.
- **A written exit-assistance statement** the customer can drop into its own vendor exit plan — its
  own regulator expects it to have one.

### G-24 — HIGH — SayOne/Synergy is itself an ICT third-party provider under DORA, and the PRD never treats it as one
**Class:** PROPOSED (the pack) + OPEN — CLIENT (each commitment). Partly ALREADY DESIGNED:
[security-control-matrix](../research/Data%20And%20Document%20Security/security-control-matrix.md),
[regulatory-obligations](../research/Data%20And%20Document%20Security/regulatory-obligations.md)

**Finding.** Every customer is a DORA-regulated financial entity. Onboarding ComplianceIQ triggers,
for them: Art. 28 due diligence, mandatory contractual clauses (Art. 30) covering data location,
access, audit rights, incident reporting to the client, subcontracting limits, exit assistance and
service levels, plus entry in their Register of Information.
The PRD has no requirement to support any of it — no audit-rights clause, no client-facing incident
notification commitment, no subcontractor disclosure, no right-to-inspect.
*Consequence:* the first enterprise CASP's procurement team will block signature. This is a sales
blocker disguised as a documentation gap.

**Recommended resolution.** Assemble the **assurance pack** procurement will ask for, and treat it as a
deliverable rather than an afterthought: security architecture overview, sub-processor list, data
location statement, incident-notification commitment, audit and inspection posture, exit assistance,
and a control summary. Most of the technical content already exists in the security research set;
what is missing is the **commitments**, which are contractual and unpriced.

### G-25 — MEDIUM — No DPA, no sub-processor list, no international-transfer position
**Class:** PROPOSED (artefacts) + OPEN — LEGAL (transfer position). See
[cross-border-data-processing](../research/Data%20And%20Document%20Security/supporting-topics/cross-border-data-processing.md)

**Finding.** NFR-06 references "a Data Processing Agreement" that does not exist as an artefact and
has no required contents. With a US-hosted LLM (see G-28) or any US-headquartered sub-processor,
Chapter V transfer mechanisms become relevant despite EU data residency.

**Recommended resolution.** The DPA is a **named deliverable** with defined contents (scope,
instructions, security measures, sub-processing, assistance, deletion/return, audit). Publish a
sub-processor list with advance notice of changes. The transfer position can only be settled once the
delivery topology is settled — where development, support and production administration are performed
is not stated in the PRD.

### G-26 — MEDIUM — The revenue source file is highly commercially sensitive and gets no special treatment
**Class:** PROPOSED

**Finding.** FR-04 has each firm upload revenue by business line — that is competitively sensitive
financial data, sitting in an AWS account owned by a consulting group (TI-01) that also sells to that
market (G-11). It has no distinct access-control, retention, or encryption treatment anywhere in the
PRD.

**Recommended resolution.** Classify it in the **most restricted class alongside evidence** — firm key,
restricted-role access, watermarked preview rather than raw download by default, every access
audited. The classification machinery already exists for evidence; this is applying it, not building
it.

---

# D. AI / OCR / regulatory monitoring

### G-27 — BLOCKER — The 85% accuracy commitment has no measurable definition
**Class:** OPEN — CLIENT. The single largest contractual exposure in the document

**Finding.** Section 6.2 commits to "a minimum verified accuracy rate of 85% against pre-defined
verification text vectors during UAT", with all tuning inside the fixed fee. Undefined:
- **Which metric?** Precision, recall, F1, or top-k? These give wildly different numbers on the same
  model. A mapper that maps only the 20 most obvious sections and abstains elsewhere scores ~100%
  precision and ~15% recall.
- **Who supplies the verification vectors, and when?** If Sosinna supplies them after the build,
  SayOne is committing to an unbounded target. If SayOne supplies them, the client will reject
  self-marking.
- **How many vectors, from how many distinct WSP documents, in which languages?**
- **What happens if UAT lands at 82%?** Fixed fee + "all tuning included" + no exit criterion is an
  open-ended obligation.

*Scenario:* UAT returns 79% recall on a Portuguese-language scanned WSP nobody had seen. Under the
clause as written, SayOne owes unlimited tuning at no cost, with no defined stop.

**Recommended resolution.** Define the measurement **in writing before build starts**, covering five
things:
1. **The metric.** Recommend per-requirement **recall at a stated precision floor** — it is the number
   that matters for a gap-analysis feature, and it prevents a mapper scoring well by abstaining. F1
   is an acceptable alternative. Pick one; the same model scores very differently under each.
2. **Who supplies the verification vectors, and when.** They must come from the Client's domain team
   and be **frozen before UAT**. A target defined after the build is unbounded.
3. **The corpus** — how many vectors, from how many distinct WSP documents, in which languages,
   including at least one scanned document if scanned PDFs are in scope.
4. **Abstention handling** — whether "no mapping suggested" counts as a miss.
5. **A bounded remediation window and a defined fallback** if UAT lands below the bar — for example,
   ship with human-only mapping plus a documented accuracy disclosure.

### G-28 — BLOCKER — Using an LLM appears to violate NFR-03 as written, and no AI stack is specified
**Class:** OPEN — CLIENT (provider) + ALREADY DESIGNED (the properties and the injection/hallucination
controls): [ai-governance](../research/Data%20And%20Document%20Security/ai-governance.md)

**Finding.** NFR-03: "All client data must be stored in EU-based data centres." FR-31 requires an AI
to read the firm's entire compliance manual — a document containing the firm's confidential controls
and often personal data. Sending it to a model endpoint outside the EU breaches NFR-03 and the
EU-residency promise made to the client. The PRD names no model, no vendor, no hosting mode, no
fallback, and carries no inference cost line. Also missing: prompt-injection defence. The WSP is an
untrusted uploaded document being fed to a model whose output drives compliance mappings.

**Recommended resolution.** **EU-resident inference under contractual no-training and no-retention
terms.** No carve-out to the residency requirement — the residency promise is one of the product's
load-bearing claims and trading it for model convenience is a bad exchange. The provider and model
stay **unselected** and are chosen against stated criteria (residency, contractual terms, accuracy
against the frozen vectors, cost, exit).

The finding names one candidate; the security research deliberately names none, because the PRD names
none. Treat provider selection as an open decision, not a design constant.

Prompt injection is already treated as a live threat — uploaded WSPs are untrusted input — with
delimiting, schema-constrained output, and **deterministic verification that every cited span exists
at the stated offset in the source document**.

### G-29 — HIGH — OCR is promised with no accuracy target, no language scope, and no failure path
**Class:** PROPOSED (separation and failure path) + OPEN — CLIENT (language scope)

**Finding.** FR-30 accepts scanned PDFs via OCR. The customers are EU CASPs; a Portuguese, German, or
French WSP is the normal case, not the edge case. Undefined: supported languages, minimum scan
quality, what the platform does when OCR fails or returns garbage, and whether OCR output errors
count against the 85% mapping accuracy bar (they will, if measured end to end).

**Recommended resolution.** Three decisions — **declare the supported languages**, **measure OCR quality
separately from mapping accuracy** (otherwise a bad scan silently consumes the 85% budget), and
**define the failure path**: when OCR confidence is low the document is flagged for manual text supply
and the mapping does not run. Never map silently against garbage.

### G-30 — HIGH — The entire product has no internationalisation position
**Class:** OPEN — CLIENT; recommend LIMITATION for the UI, with document language answered separately

**Finding.** An EU multi-jurisdiction compliance product with: no UI language requirement, no report
language requirement, no statement of which language regulatory content is authored in, no date/number
locale rule, and no currency handling for the multi-line revenue file. If the answer is "English only
for MVP", that is a legitimate limitation — but it must be written down, because it constrains the
addressable market and the marketing site (MKT-01).

**Recommended resolution.** State **English-only UI and reports for MVP** as an explicit limitation —
but separate that from **document language**. A Portuguese or German WSP is the normal case for an EU
CASP even where the UI is English, so OCR and model language coverage is a different question and
must be answered under G-29. Conflating the two produces a product that cannot read its customers'
manuals.

### G-31 — MEDIUM — SA-03 regulatory monitoring has no latency SLA and no feed-failure path
**Class:** PROPOSED (heartbeat) + OPEN — CLIENT (targets)

**Finding.** FR-35 says affected firms are "immediately alerted" when a regulation changes. SA-03's
confirmed constraint is RSS feeds and official public APIs only, polled. "Immediately" is bounded by
the poll interval plus the mandatory human review step (SA-04), which may be days. Needed: a stated
detection target ("within 24h of publication"), a stated review SLA for Sosinna's team, and behaviour
when a feed goes stale or changes format.

**Recommended resolution.** A **feed heartbeat** — every source is expected to produce something within
a defined interval, and silence or a format change raises an alert to the Portal team. Silent feed
death is the failure mode that makes the whole feature untrustworthy, and it is invisible without a
heartbeat. Detection and human-review targets are Client decisions; "immediately alerted" should be
restated as "on publication of a reviewed update".

### G-32 — MEDIUM — FR-51/FR-54 republish third-party regulator content with no licensing position
**Class:** OPEN — LEGAL + PROPOSED (the default)

**Finding.** EUR-Lex content is broadly reusable with attribution; EBA/ESMA and national regulator
content, and any commercial feed under RE-05, are not uniformly so. Confirm reuse rights before
building a news panel that stores and redisplays third-party text.

**Recommended resolution.** Default to **link and summarise rather than store and republish**
third-party regulator text, which sidesteps most of the question. Confirm reuse rights with counsel
before storing any full text, and before any commercial feed is contracted.

---

# E. Testing module — functional gaps

### G-33 — BLOCKER — It is not defined whether the platform *selects* the sample or merely *records* it
**Class:** OPEN — CLIENT. Recommend record-keeping, with the pseudonymous variant as a costed option

**Finding.** Section 7.1 step 4 has the Lead Tester record population size, sample size, selection
method and methodology. FR-72's note confirms **no customer-level data enters the platform** — only
aggregated counts. Therefore the platform cannot draw a sample: it has no population to draw from.
*Consequence:* "Random statistical sampling" becomes an unverifiable self-declaration. The tester
picks records in their own KYC system and types "50 of 4,000, random" into ComplianceIQ. The stated
purpose of the sampling library — "it needs to be defensible to a regulator" (Section 4.2) — is not
achieved by recording a label.
Two very different products follow:
- (a) *Record-keeping* (cheap): the platform stores the assertion and the methodology reference.
- (b) *Sample generation* (expensive): the firm uploads a population identifier list, the platform
  draws the sample with a seeded, reproducible algorithm and stores the seed — genuinely defensible,
  but it means customer-level identifiers enter the platform, colliding with G-21.

The PRD reads as (b) and is scoped as (a). Must be decided before estimation.

**Recommended resolution.** **Record-keeping for MVP**, stated plainly. The platform records population
size, sample size, selection method, methodology reference and rationale. It does not draw the
sample, because drawing one requires customer-level identifiers in the platform — which collides
directly with the no-personal-data position taken elsewhere.

If defensibility is genuinely required, the middle path is: the firm uploads a **de-identified
population identifier list** (opaque IDs only, no attributes), the platform draws with a **seeded,
reproducible algorithm and stores the seed**, and the firm resolves the IDs back in its own system.
That is genuinely defensible and keeps personal data out.

The onboarding and sampling text should be corrected either way — as written it reads like generation
and is scoped like recording.

### G-34 — HIGH — "Minimum sample size" is enforced but never specified
**Class:** PROPOSED (mechanism) + OPEN — CLIENT (the values)

**Finding.** Step 4 and SA-08 say the platform enforces a minimum sample rate configured per test
type. No formula, no defaults, no source. Statistical sample sizing (confidence level, expected error
rate, population size) is a real algorithm, not a percentage.

**Recommended resolution.** A **Portal-authored lookup per test type**, maintained by the Client's
domain team, with an optional statistical calculator (confidence level, expected error rate,
population size) offered as guidance. This is content, not code — which means it can be tuned without
a release.

### G-35 — HIGH — "Testing period" / "testing cycle" is never defined as an object
**Class:** PROPOSED — required to make existing PRD features buildable, not new scope

**Finding.** The report is per period (FR-56), comparison is per period (FR-53), partial testing is
tracked "across testing periods" (FR-19), and repeat findings look at "the previous testing period"
(FR-46). Yet no requirement defines what a period is, who opens or closes one, whether periods can
overlap, or whether a report can be generated mid-period. GAP-01 covers anchor dates for individual
tests, which is a narrower question. Without a period object, FR-46 and FR-53 are unimplementable.

**Recommended resolution.** Make the **testing period a first-class object** — dates, state, who opens
and closes it, whether overlap is permitted. Repeat-finding detection, period comparison and
partial-coverage tracking are all defined in terms of it and are unimplementable without it.

### G-36 — HIGH — Repeat Finding detection (FR-46) has no matching rule and only a one-period lookback
**Class:** PROPOSED (rule shape) + OPEN — CLIENT (window length)

**Finding.** "Checks whether a similar Finding was recorded in the previous testing period for the
same Requirement ID." Undefined: what "similar" means (same requirement ID alone? same root cause
category? text similarity?), and what happens for finding patterns that skip a period.
*Scenario:* the same control fails in Q1, is clean in Q2 because it was not tested, and fails again in
Q3. Under a strict one-period lookback it is never flagged as repeat — which is exactly the pattern
regulators care most about.

**Recommended resolution.** Match on **requirement plus root cause category over a rolling window**
(window length a Client decision; 24 months is a reasonable starting point), with the CCO confirming
or dismissing each flag and the decision recorded.

### G-37 — HIGH — Findings consensus happens outside the platform, breaking the single-source-of-truth claim
**Class:** SCOPE ADDITION — recommend adding; it is small relative to its evidentiary value

**Finding.** GAP-06's answer: "findings are communicated to control owners and management first; once
consensus is reached, the plan is documented with a timeline." There is no requirement anywhere for
in-platform commenting, discussion threads, @-mentions, or a review conversation on a Finding. So the
negotiation that determines what goes in the remediation plan happens by email, and the platform
records only the outcome. That contradicts Section 1's promise ("all in one place") and leaves the
audit trail materially incomplete for the most contested step in the process.

**Recommended resolution.** An **append-only comment thread** on Findings and test executions —
participants, timestamps, no edit and no delete, included in the audit trail and in the Finding's
history. Optionally surfaced in the report appendix.

### G-38 — HIGH — Requirement-level "Not Applicable" has no owner, and conflicts with automatic test loading
**Class:** PROPOSED

**Finding.** FR-21b defines N/A at *test execution* level (immutable, reason required). FR-50 shows
N/A as a status at *Requirement ID* level on the dashboard. Nobody sets the latter. FR-07 loads
requirements automatically from confirmed service lines, so marking a whole requirement N/A
contradicts the derivation.

**Recommended resolution.** Requirement-level N/A **requires dual sign-off** — it removes an obligation
from the programme, which is a heavier act than marking one execution N/A — with a documented reason,
an immutable record, and **re-surfacing for confirmation whenever the revenue-file derivation
changes**. It survives a re-upload rather than being silently cleared or silently retained.

### G-39 — HIGH — No rule for what happens to in-flight and historical work when service lines change
**Class:** PROPOSED

**Finding.** FR-08: re-uploading a revenue file "triggers a recalculation of applicable tests".
Undefined:
- Requirements added: are tests scheduled immediately, or from next period? Is the firm retroactively
  non-compliant for the periods before the service line was declared?
- Requirements removed: what happens to a Planned test, an Ongoing test with evidence already
  uploaded, an open Finding, and an open remediation milestone under that requirement?

*Scenario:* a firm exits portfolio management in month 7. Two open High findings sit under
portfolio-management requirements with unmet milestones. Do they close? Stay open forever? Move to an
"orphaned" state? Regulators will still ask about them.

**Recommended resolution.** **Removal never deletes.**
- A removed requirement moves to *no longer applicable from `<date>`*; it stops scheduling.
- **Open findings and open milestones under it stay open and visible.** A supervisor will still ask
  about them.
- Historical results are retained and shown in comparison views, annotated with the applicability
  change.
- Added requirements schedule **from the next period** by default, with the CCO able to start
  immediately. No retroactive non-compliance is asserted for periods before the service line was
  declared.

### G-40 — MEDIUM — Re-uploading the revenue file changes the firm's regulatory obligations with no approval gate
**Class:** PROPOSED

**Finding.** FR-08 lets the firm update the profile "at any time". FR-05 has the CCO confirm derived
service lines at onboarding, but FR-08 does not restate that gate for updates.
*Scenario:* a Firm Super Admin uploads a corrected spreadsheet and silently removes a service line,
dropping 15 tests off the programme. That is a governance event.

**Recommended resolution.** A re-upload produces a **diff screen** ("these 15 tests will stop being
scheduled; these 6 will start") and requires **CCO confirmation with a justification**, audited — the
same gate the PRD already applies at onboarding.

### G-41 — MEDIUM — The revenue file template does not exist and is on the critical path
**Class:** PROPOSED (mechanism) + OPEN — CLIENT (template content, which blocks the sprint)

**Finding.** FR-04 depends on "the platform's template", which the 25 Jun note says Sosinna is still
sourcing ("the EU equivalent of a US Form 1040"). No column spec, no validation rules, no
error-handling behaviour, no versioning of the template, and no rule for what happens when a firm
uploads against an old template version. The same note also states selection "can't be fully
automated 1:1 — a single revenue line can span two service lines", which means the derivation is a
*suggestion* requiring manual confirmation — closer to a guided picker than the automatic derivation
Section 5 describes.

**Recommended resolution.** Treat the template as a **versioned artefact**: column specification,
validation rules, error reporting, a template version stamped on every upload, and rejection of
unrecognised versions with a clear message. Correct the onboarding wording from automatic derivation
to **"derived, then confirmed"**.

### G-42 — MEDIUM — GAP-10's second half is the more important half and is being under-weighted
**Class:** PROPOSED (data model)

**Finding.** GAP-10 asks about a banner vs. persistent notice (a UI question, and the note says the UI
designer can decide alone) *and* "does the system record which rule version the test was run under".
The second is a data-model requirement with direct audit consequence: SA-04 promises in-flight tests
continue on the version they started, which is only provable if the version is pinned on the test
execution record.

**Recommended resolution.** **Split it.** The banner-versus-notice question is a design decision.
**Pinning the requirement and procedure version on the test execution record is mandatory** — it is
the only thing that makes the "in-flight tests continue on the version they started" promise provable
to an inspector.

### G-43 — MEDIUM — No behaviour defined for retiring a Requirement ID or a test procedure mid-cycle
**Class:** PROPOSED

**Finding.** SA-01 says IDs can be retired. Undefined: what happens to scheduled tests, in-flight
tests, and open findings under a retired ID; whether the retirement propagates to all firms at once;
whether a firm mid-test is force-migrated at period end.

**Recommended resolution.** Retirement is a **version event with an effective date**. In-flight tests
finish on their pinned version. Scheduled-but-not-started tests are withdrawn with an audit note.
Open findings persist. Nothing is force-migrated mid-test.

### G-44 — MEDIUM — FR-53 trend comparison is invalid across procedure versions
**Class:** PROPOSED

**Finding.** The CCO compares this quarter to last quarter to see if compliance is improving. If the
test procedure changed between them (which SA-01/SA-04 make routine), the comparison is apples to
oranges and nothing warns the user.

**Recommended resolution.** **Annotate** comparison views wherever the underlying procedure version
differs, and never present a silent like-for-like comparison. Cheap, and it protects the credibility
of the one screen most likely to be shown to a board.

### G-45 — MEDIUM — Partial testing (FR-19) has no coverage model
**Class:** PROPOSED (Portal content model addition — feeds the Portal scope decision in G-79)

**Finding.** "The platform tracks which parts of a Requirement ID have been covered across different
testing periods." There is no definition of "parts" — a requirement is not decomposed into sub-scopes
anywhere in the Portal content model (SA-02 defines steps, not scope segments). Without a defined
sub-scope taxonomy authored in the Portal, coverage tracking is free text and cannot be reported on.
*Scenario:* Q1 covers KYC, Q2 covers UBO refresh (the PRD's own example). To say "the requirement is
now fully covered", the platform must know that {KYC, UBO refresh} is the complete set. Nothing
defines that set.

**Recommended resolution.** The Portal authors **named sub-scopes per requirement**, and coverage is
computed against that set. Without an authored set, "fully covered" is unknowable and coverage
tracking is free text that cannot be reported on.

### G-46 — MEDIUM — Evidence shelf life (FR-28) has no source of truth
**Class:** PROPOSED (validity source) + SCOPE ADDITION (library)

**Finding.** "For example, a BCP test report is only valid evidence if it is less than 12 months old."
Who sets the validity period — per evidence type in the Portal, per test procedure, or per upload?
Not stated. Also no requirement for an evidence library: one BCP report is valid evidence for several
tests, but the model implies re-upload per test, producing duplicates with independently tracked
ages.

**Recommended resolution.** Validity period **authored per evidence type in the Portal**, overridable
per test procedure. Add an **evidence library** so one artefact — a business continuity test report,
say — serves several tests with a single tracked age, rather than being re-uploaded per test and
ageing independently in three places.

### G-47 — MEDIUM — No historical data import at onboarding
**Class:** LIMITATION (recommended) or a costed import

**Finding.** Firms arrive from spreadsheets with years of prior testing history. Nothing supports
importing it.
*Consequence:* FR-53 (period comparison) and FR-46 (repeat findings) produce nothing useful for the
first 12 months of every customer — the two features most likely to be demoed.

**Recommended resolution.** State as an **accepted limitation**, and soften it cheaply by allowing
prior-period reports to be attached as evidence so a new firm's archive is not empty. Note the demo
consequence honestly: period comparison and repeat-finding detection produce nothing useful for a
customer's first year, and those are the two features most likely to be demonstrated in a sales
cycle.

### G-48 — LOW — No test cloning, bulk assignment, or carry-forward of prior-period setup
**Class:** SCOPE ADDITION — small, high adoption value

**Finding.** A CCO assigning 40 quarterly tests one at a time will ask for this in week one.

**Recommended resolution.** Carry-forward of prior-period setup plus bulk assignment.

### G-49 — LOW — No global search
**Class:** SCOPE ADDITION — recommend including; a six-year archive without search degrades badly

**Finding.** "Find every finding mentioning sanctions screening" / "find the evidence file we uploaded
last March" is unsupported anywhere in the document. For a six-year evidence archive this is not
optional.

**Recommended resolution.** Permission-filtered search across findings, tests and evidence
**metadata** (not full evidence content for MVP). It must respect tenant isolation and per-record
permissions, be rate-limited, and be audited — an unrestricted search box over a six-year
multi-tenant evidence archive is also an exfiltration path.

---

# F. Reports, notifications, dashboard

### G-50 — HIGH — FR-59 auto-emails an unencrypted report containing every open compliance failure
**Class:** PROPOSED + OPEN — CLIENT (confirmation). Matches
[open-questions](../research/Data%20And%20Document%20Security/open-questions.md) P-7

**Finding.** "Once signed off, the report is automatically sent to the firm's configured distribution
lists." No requirement covers: attachment vs. expiring secure link, encryption, recipient
verification, whether external (non-user) email addresses can be on a list, or what happens when a
recipient leaves the firm and the list is stale.
*Scenario:* a distribution list still contains a former board member's personal Gmail. The Q3 report —
every High finding, every unremediated control failure — is emailed there automatically with no human
in the loop. This is the highest-impact data-leak path in the product.

**Recommended resolution.** **Authenticated expiring link as the default**, not an attachment.
Attachments only where a list has explicitly enabled them. Recipients must be known platform users
unless explicitly approved as external. **Periodic list re-validation by the CCO**, and an audit entry
per delivery.

### G-51 — MEDIUM — Exactly six distribution lists, fixed, with no external-recipient model
**Class:** OPEN — CLIENT

**Finding.** Section 10.6 fixes the list count at six. No custom lists, no per-report override, no
statement on whether external auditors, outside counsel, or non-login board members can be
recipients. Real firms will need at least the external-auditor case.

**Recommended resolution.** Keep six fixed for MVP; add an **external-recipient flag requiring CCO
approval per address**, with the approval audited and the address re-validated on the same cycle as
G-50. Custom lists are a later feature.

### G-52 — MEDIUM — "Acknowledged" is tracked but never defined
**Class:** PROPOSED

**Finding.** Section 2 logs whether each alert was acknowledged; FR-43 escalates if a High-finding
escalation is "not formally acknowledged within five business days". No requirement describes the
acknowledgement action — clicking an email link, logging in, or an explicit in-app button — nor who
can do it on whose behalf. Without a defined act, FR-43's escalation cannot be built or tested.

**Recommended resolution.** Define acknowledgement as an **authenticated in-app action by the named
recipient**, recorded with actor and timestamp. No acknowledgement by proxy unless an explicit
delegated grant exists (G-07).

### G-53 — MEDIUM — "Five business days" and "four hours" have no calendar or timezone definition
**Class:** PROPOSED (model) + OPEN — CLIENT (holiday calendar source)

**Finding.** Firms operate across EU jurisdictions with different public holidays; the platform stores
one jurisdiction per firm but no working calendar.
*Scenario:* a High finding is raised at 17:00 on 23 December. In Portugal 24–26 December are
effectively non-working; in another Member State the pattern differs. The escalation fires on a
different real-world date depending on an unstated rule. Same problem for the DORA 4-hour clock and
for every "30/14/7/1 day before" reminder.

**Recommended resolution.** A **firm-level timezone and working calendar**, with jurisdiction public
holidays maintained as Portal content. State per clock whether it is calendar-time or business-time:
**the ICT incident four-hour clock is wall-clock**; the five-business-day escalation and the reminder
ladders are business-time.

### G-54 — MEDIUM — No email deliverability, bounce, or provider requirement
**Class:** PROPOSED

**Finding.** The whole notification model (NT-01 resolved: email and in-platform only) rests on email
arriving. Nothing covers the sending provider, SPF/DKIM/DMARC, bounce and complaint handling, or what
the platform does when a report delivery hard-bounces. A silently bounced report that the platform
records as "distributed" is an audit-trail falsehood.

**Recommended resolution.** An authenticated sending domain with SPF, DKIM and DMARC; bounce and
complaint handling; and **delivery status recorded honestly** — a hard bounce must never be recorded
as delivered.

### G-55 — MEDIUM — No report generation performance target, and the dashboard target is the easy path
**Class:** PROPOSED

**Finding.** NFR-05 targets two-second dashboard loads. The genuinely hard operation is generating a
multi-hundred-page PDF (FR-56, eight sections, every test, every finding, embedded evidence
references) — potentially minutes, needing async generation, progress feedback, and failure handling.
None of that is described; FR-60 reads as a synchronous download.

**Recommended resolution.** **Asynchronous generation** with progress feedback, failure handling and
retry. The two-second target applies to dashboards; a multi-hundred-page report with embedded
evidence references is a background job and should be specified as one.

### G-56 — MEDIUM — No report preview, draft, or regeneration path
**Class:** OPEN — CLIENT (it touches a stated PRD rule); PROPOSED on drafts and rejection handling

**Finding.** FR-61 makes reports immutable once signed off. Nothing describes the state before that:
can the CCO preview a draft, discard it, and regenerate? What happens if the CCO generates the report,
then Senior Management refuses to sign — is that report void, does it persist as a rejected artefact,
and what does the milestone clock (FR-47, started at generation) do in the meantime?
*Scenario:* CCO generates on 1 Oct, milestone clocks start. Senior Management rejects on 5 Oct over a
wording issue. A corrected report is generated on 8 Oct. Do the milestone clocks restart, or is the
firm now seven days into deadlines against a void report?

**Recommended resolution.** Drafts exist and are discardable; **only the signed-off report is
immutable**; a rejected report is retained as a rejected artefact with the rejection reason. **Start
the milestone clocks on sign-off rather than on first generation** — otherwise a wording rejection
silently consumes a week of every remediation deadline.

**Note.** This adjusts a statement the PRD makes explicitly ("the moment the CCO generates the report,
every milestone clock starts"). Flag it rather than change it unilaterally.

### G-57 — LOW — FR-48 "more metrics can be added based on the CCO's preferences" is unbounded
**Class:** PROPOSED

**Finding.** In a fixed-price contract, this needs a fixed initial metric set with anything further
via amendment, or a configurable-widget feature that is properly scoped and estimated.

**Recommended resolution.** **Fix the initial metric set** in the acceptance criteria. Anything further
is either an amendment or a properly scoped configurable-widget feature. Open-ended wording in a
fixed-price contract is a dispute generator.

### G-58 — LOW — No external/regulator/auditor read-only access
**Class:** LIMITATION

**Finding.** "Regulator View" was removed in Narrative v3, and reports go out by email instead.
External auditors are a routine need for these firms. Record as a deliberate limitation so it is not
re-litigated.

**Recommended resolution.** Record as a **deliberate limitation**. Firms export what their auditors
need. An auditor role would add a ninth role, a new authorisation surface, and a cross-firm access
question — real scope, not a toggle.

---

# G. Organisation & staff module

### G-59 — HIGH — FR-66's "revenue function" test has no data to run on
**Class:** PROPOSED

**Finding.** The platform is to flag a governance red flag if the CCO reports into a revenue function
such as Sales or Trading. FR-63 captures `department` as a free-text-style field. Nothing classifies a
department as revenue-generating vs. control.
*Scenario:* a firm names its trading desk "Markets Group". No match on "Sales" or "Trading", no flag
raised, and the firm believes the platform checked. A silent false negative in a governance control is
worse than no control.

**Recommended resolution.** A **controlled department taxonomy** with a revenue-generating vs. control
classification, maintained in the Portal and mapped during onboarding. Where a department is
unmapped, the platform reports **"cannot evaluate"** rather than passing silently.

### G-60 — HIGH — The org chart has no requirements for malformed hierarchies
**Class:** PROPOSED

**Finding.** FR-65 builds the tree automatically from reporting-line fields. Undefined: cycles (A
reports to B reports to A), multiple roots, orphans with no manager, matrix/dual reporting, and how
FR-64's multi-role person renders as a node. A CSV import (FR-62) will produce all of these on day
one.

**Recommended resolution.** **Validation at import** with a specific, actionable error report — cycles,
multiple roots, orphans, unknown managers — plus a defined rendering rule for structures that cannot
be resolved. Decide explicitly whether dual reporting is supported or rejected.

### G-61 — HIGH — The BCP call tree is a single linear chain with no branch and no break handling
**Class:** PROPOSED

**Finding.** FR-70 assigns each staff member exactly one "next contact" and flags missing links. A
single chain means one unreachable person stops the cascade — the exact failure mode a call tree
exists to prevent.
*Scenario:* person 7 of 40 is on a flight. Persons 8–40 are never contacted. The platform reports the
chain as complete because every link is populated.

**Recommended resolution.** An **alternate contact per person**, plus **cycle detection and a
reachability check** — every person must be reachable from the root, not merely have a populated
next-contact field.

### G-62 — MEDIUM — Staff Member and Platform User records have no linkage or identity-matching rule
**Class:** PROPOSED

**Finding.** Section 10 defines the two record types; FR-64 says one person holding multiple roles is
handled "without creating duplicate records" but no mechanism is given. Undefined: the natural key for
CSV re-import (email? name? employee ID?), what happens when a Staff Member later receives a login,
and what happens on a name change.
*Scenario:* the second monthly CSV upload uses "Rob Silva" instead of "Roberto Silva". Either a
duplicate staff record appears in the org chart and call tree, or an existing record is silently
overwritten.

**Recommended resolution.** A **stable external ID column in the CSV template** as the natural key, a
defined merge and conflict flow with a review screen, and **never a silent overwrite**. Promoting a
Staff Member to a Platform User links the records rather than creating a second one.

### G-63 — MEDIUM — Certification expiry marks a record "non-compliant" with no defined consequence
**Class:** OPEN — CLIENT (blocking or not) + PROPOSED (the rest)

**Finding.** FR-67 flags the staff member. Nothing says whether that blocks anything — e.g. whether a
Lead Tester with a lapsed certification can still be assigned tests and sign results, and whether an
expiry mid-test invalidates work already done. Also missing: a certification-type library (free text
will make the register unreportable) and the ability to attach the certificate document itself as
evidence.

**Recommended resolution.** Warn and flag; **do not retroactively invalidate completed work** — a
result signed off while the certification was valid stays valid. Whether an expired certification
blocks *new* test assignment is a Client decision. Add a certification-type library and allow the
certificate document to be attached.

### G-64 — MEDIUM — Hardware inventory is too thin for the DORA claim it is making
**Class:** OPEN — CLIENT; recommend softening

**Finding.** FR-69 captures device type, serial number, asset tag. A DORA-grade ICT asset register
generally also needs location, criticality, supported/EOL status, ownership, and the link to the ICT
systems and functions the asset supports.

**Recommended resolution.** **Soften the claim for MVP** — three fields are a device list, not an ICT
asset register. List the extension (location, criticality, lifecycle and end-of-support status,
owner, linked systems and functions) as a costed option rather than implying the current fields
satisfy the obligation.

### G-65 — LOW — OS-06 (non-employee committee members) is marked "no update" but interacts with G-05
**Class:** OPEN — CLIENT; recommend supporting

**Finding.** External NEDs and advisory committee members are exactly the people small firms rely on
for the second Senior Management sign-off. If they cannot exist in the system, G-05's deadlock gets
worse.

**Recommended resolution.** Support **non-employee governance records**, and platform logins for them
where they sit in an approval path.

---

# H. Non-functional, security, operations

### G-66 — BLOCKER — No backup, RPO, or RTO requirement — in a resilience-compliance product
**Class:** ALREADY DESIGNED (capability):
[secure-backups](../research/Data%20And%20Document%20Security/secure-backups.md),
[disaster-recovery](../research/Data%20And%20Document%20Security/disaster-recovery.md).
OPEN — CLIENT (targets)

**Finding.** NFR-08 gives an availability target (99.5%) and nothing else. Missing: backup frequency,
backup retention, restore-time objective, recovery-point objective, restore testing cadence, and a DR
region or strategy. Every customer is a DORA-regulated entity that must assess exactly these
attributes in its provider due diligence (G-24). Shipping a DORA product without stated RPO/RTO is
both an operational risk and a sales blocker.

**Recommended resolution.** The capability is designed; the **targets are not proposed**. Buildable and
committable now: a backup account with no trust path from production, immutable retention on the
longer-retention copies, **automated restore verification** including decryption with the correct firm
key, and record copies outside the primary failure domain within the EU. **No recovery time or
recovery point figure should be committed until it has been measured** — and the availability target
itself is recorded as an open question in the PRD, so the investment question is open too.

### G-67 — BLOCKER — TI-01 (client-owned AWS account) has no operating model attached
**Class:** OPEN — CLIENT. See
[reference-cloud-architecture](../research/Data%20And%20Document%20Security/reference-cloud-architecture.md)

**Finding.** "AWS, EU-resident data centre, on an account owned solely by the Client." Unresolved: who
holds root and billing; who pays the AWS bill (it is not in the fixed fee as described); how SayOne
obtains and retains deploy access; how many environments exist (dev/staging/UAT/prod) and in whose
accounts; who runs CI/CD; who is on call; what happens to SayOne's access at project end.
This also breaks two other statements:
- NFR-04 "not even the system administrators at SayOne can modify or delete this log" — true, but the
  *Client's* root admin can drop the database. The immutability claim is only as strong as the account
  owner's own controls, which the PRD never specifies.
- NFR-02 "each firm has its own encryption key" — with no KMS design, no rotation policy, no
  statement of who can use the keys, and no BYOK option. In a client-owned account, the client
  controls the keys for every tenant.

**Recommended resolution.** Settle six things before build: **root and billing custody**, **who pays the
infrastructure bill** (it is not in the build fee as described), **how deploy access is granted and
revoked**, **the environment inventory and whose accounts they live in**, **who operates CI/CD and
responds out of hours**, and **what happens to delivery-team access at project end**.

Design position to bring to that conversation: zero standing human access to production,
dual-approved and session-recorded break-glass, split custody of root.

Also state the honest limit: **the immutability guarantee is bounded by the account owner's own
controls.** "Not even SayOne's administrators can modify the log" is true and insufficient — the
account owner's root can. Ties to G-11 and G-68.

### G-68 — HIGH — Audit-log immutability has no technical mechanism
**Class:** ALREADY DESIGNED: [audit-logging](../research/Data%20And%20Document%20Security/audit-logging.md),
[immutable-evidence-retention](../research/Data%20And%20Document%20Security/immutable-evidence-retention.md)

**Finding.** NFR-04 and FR-13 promise a tamper-proof, append-only log that no administrator can alter.
A normal relational table does not deliver that. As written this is an unbacked claim in a document
whose entire value proposition is provability.

**Recommended resolution.** **Hash-chained audit events written to a dedicated write-only log archive
account** with write-once retention, deletion denied to every principal including root, key deletion
blocked while records are in retention, and scheduled verification of the chain. Plus a **documented
verification procedure** an auditor can actually run.

### G-69 — HIGH — No malware scanning of uploads
**Class:** ALREADY DESIGNED:
[secure-media-storage](../research/Data%20And%20Document%20Security/secure-media-storage.md)

**Finding.** FR-24 permits arbitrary PDF, Office, image, audio, video, ZIP and CSV uploads into a
multi-tenant platform, retained for six years, redistributed to other users, and referenced from
emailed reports. Nothing in Section 13 requires virus/malware scanning, archive-bomb protection,
content-type verification, or safe rendering. ZIP archives are called out explicitly as an accepted
type.

**Recommended resolution.** **Quarantine, scan, promote**: multi-engine scanning, structural and
archive-bomb checks, content type determined by inspection rather than declaration, **fail closed** on
scanner error, parsing in an isolated account with no credentials and no network egress, and a
watermarked server-side preview as the default access mode rather than raw download.

### G-70 — HIGH — No storage quota, and the cost model is unbounded on a fixed-price contract
**Class:** OPEN — CLIENT (commercial) + PROPOSED (tiering and allowances)

**Finding.** FR-24/NFR-11 make max *file* size configurable but set no per-tenant or per-firm storage
cap. Video and screen recordings are accepted evidence types and must be retained six years,
undeletable.
*Scenario:* 30 firms × 40 GB/year of video evidence × 6 years ≈ 7 TB of undeletable EU-region storage,
plus per-tenant encryption and backups. Under a fixed-fee build in a client-owned account (G-67), it
is not even stated who absorbs that.

**Recommended resolution.** Three things — **per-plan storage allowances with a stated overage policy**,
**lifecycle tiering to colder storage that preserves the write-once retention lock**, and an explicit
statement of **who absorbs storage cost** in a client-owned account. Model the cost before setting the
maximum file size, not after.

### G-71 — HIGH — Authentication is under-specified for the enterprise buyer
**Class:** OPEN — CLIENT (factor) + PROPOSED (policies and recovery) + LIMITATION (SSO/SCIM). See
[identity-and-access-management](../research/Data%20And%20Document%20Security/identity-and-access-management.md)

**Finding.** FR-11 says email + password + "a second verification step on their phone". Missing:
whether MFA is TOTP, push, or SMS (SMS is explicitly out of scope for notifications under NT-01 — a
probable contradiction if SMS OTP was intended); password policy; account lockout and brute-force
protection; session lifetime and idle timeout; concurrent-session policy; MFA recovery.
*Scenario:* both Firm Super Admins lose their phones. FR-15 exists to prevent lockout, but nothing
describes an MFA reset path — and the Portal team recovering it for them (SA-06 says they cannot see
firm data) is undefined.
Also absent and expected by enterprise CASPs: SSO/SAML/OIDC, SCIM provisioning, IP allowlisting.

**Recommended resolution.**
- **Second factor:** an authenticator app or push approval rather than SMS. Both satisfy the PRD's
  "verification step on their phone", and SMS carries SIM-swap risk that is elevated for crypto-sector
  staff. **The choice is an open decision** — this is the recommendation, not a selection.
- **Add explicitly:** password policy, account lockout and brute-force protection, session lifetime
  and idle timeout, concurrent-session policy.
- **MFA recovery** with dual approval and full audit. The two-Super-Admin rule prevents role lockout,
  not device loss — if both admins lose their phones there is currently no path, and the Portal team
  recovering it collides with the Portal visibility boundary.
- **SSO, SCIM provisioning and IP allowlisting: state as out of MVP.** They are common procurement
  gates, so the exclusion needs to be visible rather than discovered.

### G-72 — HIGH — NFR-05's concurrency figure contradicts TI-06's sizing
**Class:** OPEN — CLIENT

**Finding.** NFR-05: "up to 100 simultaneous users per firm". TI-06: MVP firms cap around 50
individuals with typically ~10 platform users. 100 concurrent per firm is 10× the stated realistic
ceiling, while the figure that actually drives infrastructure — total concurrent users across all
firms, and total number of firms in Year 1 — is still unanswered (TI-06, estimation blocker). No
data-volume targets either (tests/firm/year, evidence GB/firm/year, findings/period). Load testing
cannot be specified.

**Recommended resolution.** Treat the stated per-firm concurrency figure as a **ceiling for load
testing**, not an expectation, and note the contradiction so nobody sizes infrastructure from it. The
number that actually drives cost — total firms and total concurrent users in year one — is still
unanswered and is already an estimation blocker in the PRD. Add data-volume targets (tests per firm
per year, evidence GB per firm per year, findings per period) at the same time.

### G-73 — MEDIUM — No observability, monitoring, or platform-incident-response requirement
**Class:** ALREADY DESIGNED:
[security-monitoring](../research/Data%20And%20Document%20Security/security-monitoring.md).
OPEN — CLIENT (the deadline)

**Finding.** Nothing on application logging, metrics, alerting, error tracking, log retention, or what
SayOne does when the platform itself has an outage — including whether affected firms are notified,
which their own DORA obligations require them to receive (G-24).

**Recommended resolution.** Detections as code with tests, log-source heartbeats, priority alerts
including cross-firm and protected-record tripwires, and an incident procedure that includes
**notifying affected firms**, which their own regulatory obligations require them to receive. The
**notification deadline is contractual** and is not proposed here as a number.

### G-74 — MEDIUM — No environment or test-data strategy, though UAT carries a contractual obligation
**Class:** PROPOSED. See [secure-sdlc](../research/Data%20And%20Document%20Security/secure-sdlc.md)

**Finding.** Section 6.2 makes UAT the acceptance gate for the 85% AI accuracy commitment, but no UAT
environment, no seeded demo tenant, and no synthetic test data are specified. Realistic compliance
test data cannot be borrowed from production (it is customer PII).

**Recommended resolution.** A **synthetic data fixture factory covering every accepted evidence type**,
no production data outside production under any circumstance, a seeded demo tenant, and a **named UAT
environment as a deliverable** — the accuracy commitment is measured there, so it cannot be
improvised.

### G-75 — MEDIUM — No accessibility requirement
**Class:** OPEN — CLIENT

**Finding.** No WCAG target anywhere. For an EU-market B2B SaaS sold to regulated financial entities —
several of which will have their own accessibility procurement requirements, and with the European
Accessibility Act now in force for in-scope services — this should be an explicit decision (target
level, or a stated exclusion), not silence.

**Recommended resolution.** Make it an explicit decision — **target WCAG 2.2 AA, or state the
exclusion**. Recommend stating a target: EU-market B2B procurement will ask, and retrofitting
accessibility is far more expensive than building to it.

### G-76 — MEDIUM — NFR-10's mobile requirement is unmeasurable and therefore unacceptable in a fixed-price contract
**Class:** PROPOSED (acceptance criteria)

**Finding.** "The browser version should work well enough on mobile for approval sign-offs." Needed:
named target viewports, the specific flows that must work (Senior Management report sign-off,
escalation acknowledgement, finding closure sign-off), and the flows that explicitly need not.
Same defect class elsewhere: "professional report" (Section 1), "at-a-glance" (FR-48), "proactively
alerts" (FR-28), "without performance degradation" (NFR-05).

**Recommended resolution.** Convert each vague phrase into a **testable acceptance criterion** — named
target viewports and the specific flows that must work on mobile (report sign-off, escalation
acknowledgement, closure sign-off) and those that need not; a defined metric set for the dashboard;
defined lead times for proactive alerts; a stated load profile for performance. Do this for every such
phrase before signature; each one is a future dispute.

### G-77 — MEDIUM — No support, maintenance, warranty, or hypercare terms
**Class:** OPEN — CLIENT (commercial)

**Finding.** CC-04 confirms a fixed-price milestone contract for the build. Nothing covers what
happens after go-live: defect warranty period and definition, support hours, response/resolution
targets, who runs production, regulatory-content updates as an ongoing service (RE-01 is still an open
estimation blocker), or SLA credits against the 99.5% target. This is a commercial gap with direct
architectural consequences (see G-67 on who operates the environment).

**Recommended resolution.** A **separate services agreement** covering defect warranty and its
definition, support hours, response and resolution targets, **who operates production**, ongoing
regulatory-content maintenance, and any service credits. None of this is inside the build fee as
described.

### G-78 — MEDIUM — No rate limiting, penetration testing, or secure-SDLC requirement for the platform itself
**Class:** ALREADY DESIGNED: [secure-sdlc](../research/Data%20And%20Document%20Security/secure-sdlc.md),
[supply-chain-security](../research/Data%20And%20Document%20Security/supply-chain-security.md),
[secure-cicd](../research/Data%20And%20Document%20Security/secure-cicd.md)

**Finding.** NFR-09 defers ISO 27001 and SOC 2 to a roadmap, TI-03 asks whether clients require them.
Independent of certification, a product that stores six years of regulated firms' compliance evidence
should carry explicit requirements for pre-launch penetration testing, dependency/vulnerability
scanning, secret management, and rate limiting. None are present.

**Recommended resolution.** Blocking CI gates for secrets and critical vulnerabilities and
tenant-isolation test failures, dependency and secret scanning, signed artefacts with provenance
verified at admission, per-role and per-endpoint rate limiting, and an **independent penetration test
with Critical and High findings remediated before real client data is accepted**.

---

# I. Platform Admin Portal — under-specification

### G-79 — BLOCKER — The Portal has 8 requirements against ~74 for the Firm Application, yet the fixed fee covers both equally
**Class:** OPEN — CLIENT

**Finding.** The IP/baseline note commits the fixed fee to "parallel development, deployment, and
security configuration of both the Firm Application and the Platform Admin Portal, both fully
operational as defined by this document's functional requirements". SA-01 to SA-08 do not come close
to defining a fully operational back office. Entirely absent:
- Portal user management, Portal roles beyond a single "Super Admin", and Portal MFA.
- A Portal audit log. NFR-04 says "every action in the platform" — is content authoring in scope? It
  must be: a change to a test procedure changes every firm's obligations.
- Content-authoring UX: how a multi-step procedure with evidence checklists, sampling rules and
  minimum sizes is actually built (SA-02 is one sentence).
- The review-and-publish workflow: SA-04 says "a review step" — by whom, how many approvers, what
  states, and is there a rollback/unpublish for a bad publication?
- Draft/staging content and preview before publication.
- Content import/export, and bulk authoring (the initial library is dozens of procedures).
- Per-jurisdiction content variants (see G-17).
- Cross-tenant content migration when a procedure version is superseded.
- Portal-side reporting beyond SA-08's usage report.

**Recommended resolution. Bound the deliverable explicitly.** Proposed MVP Portal scope, to be accepted
or trimmed as a whole:
- Content authoring for requirements and multi-step procedures, with evidence checklists, sampling
  rules and minimum sizes.
- **Version history and a review-and-publish workflow** with named approvers, defined states, and a
  rollback or unpublish path for a bad publication.
- **Draft and preview** before publication.
- **Portal user management, Portal roles beyond a single super admin, and Portal MFA.**
- **A Portal audit log.** A change to a test procedure changes every firm's obligations; if any action
  needs auditing, this one does.
- Bulk import and export, because the initial library is dozens of procedures and authoring them one
  at a time in a web form is not viable.
- Firm list, system settings, usage report.

Anything beyond this list is an amendment. Per-jurisdiction content variants (G-17) and requirement
sub-scopes (G-45) should be decided as part of this scoping, since both are Portal content model
changes.

### G-80 — HIGH — No seat enforcement, despite seat-based pricing
**Class:** OPEN — CLIENT

**Finding.** CC-01 confirms seat-based plans configured per firm in the Portal at onboarding. SA-08's
25 Jun addition gives month-end usage reporting (active users vs. subscribed seats). Nothing says what
the platform *does* when a firm exceeds its seats — block the invite, allow with a warning, allow and
report? Billing is off-platform via the reseller (CC-06), so there is no payment integration to scope,
but seat *enforcement* is a product behaviour that has to be decided.

**Recommended resolution.** **Allow with a warning and report**, rather than blocking invitations.
Blocking can lock a firm out of the very governance actions the product exists to enforce, and it
worsens the approver-pool problem in G-05. Notify both the Firm Super Admin and the Portal team;
commercial follow-up happens off-platform through the reseller.

### G-81 — MEDIUM — No marketing-site requirements beyond three sentences
**Class:** OPEN — CLIENT

**Finding.** MKT-01 to MKT-03 define the site in three lines, and two open questions (MKT-04, MKT-05)
sit on the delivery critical path. Undefined: page inventory, who writes the copy, lead-capture
destination (a CRM? an email inbox?), GDPR consent/cookie banner for an EU-facing site (mandatory, and
currently unmentioned anywhere), analytics, and SEO. MKT-05 (domain) also blocks CC-02 (branding),
which is still open. If Demo Day (CC-05) is a real date, this is the most visible deliverable with the
least specification.

**Recommended resolution.** Bound it before it is built — page inventory, who writes the copy, where
leads land, **consent and cookie compliance** (mandatory for an EU-facing site and currently
unmentioned anywhere), analytics choice with a residency check, and SEO basics. **Resolve the domain
and branding questions first**: they block the site and each other.

---

# J. Commercial and contractual

### G-82 — BLOCKER — The CC-03 IP clause as accepted has no background-IP or OSS carve-out, and is probably unperformable
**Class:** OPEN — LEGAL. Flag before signature

**Finding.** Accepted text: "all right, title, and interest in and to this regulatory content,
alongside all platform source code, backend architectures, frontend user interfaces, and database
schemas built by the Contractor, belong 100% exclusively to the Client from the moment of creation.
The Contractor retains zero rights, ongoing claims, or implied licenses to any content or code within
the platform."
Three problems:
1. **Third-party open source.** Any real build includes OSS under licences (MIT, Apache-2.0, and
   especially any copyleft component) whose terms cannot be overridden by this contract. "100%
   exclusive ownership of any code within the platform" is not achievable for those components, and
   the clause as written contains no carve-out.
2. **Background IP.** SayOne's pre-existing frameworks, boilerplate, and internal libraries would be
   assigned on first use. There is no reservation of pre-existing materials with a licence grant to
   the Client — the standard construction.
3. **"Zero implied licenses"** means SayOne arguably has no right to hold or run the code it wrote,
   which conflicts with SayOne operating the deployment (G-67) and with any post-launch maintenance
   (G-77).

**Recommended resolution — redraft, for counsel to finalise:**
- **Full assignment of purpose-built deliverables** to the Client — this is the intent and it is
  achievable.
- **Background IP retained** by the contractor, with a perpetual, irrevocable, worldwide,
  sublicensable licence to the Client to use it as embedded in the platform.
- **Third-party open-source components governed by their own licences**, with a delivered software
  bill of materials. No contract can override an upstream licence, and "100% exclusive ownership of
  any code within the platform" is unperformable while any open-source component exists — which is
  always.
- **An operating licence back** to the contractor for as long as it deploys, operates or maintains the
  platform. "Zero implied licenses" as drafted arguably prevents the contractor from running the code
  it wrote.

Note the security research already derives a **licence deny-list** from this clause, so the redraft
feeds directly into the dependency policy.

### G-83 — BLOCKER — The baseline-freeze clause is logically incompatible with Sections 15 and 16
**Class:** OPEN — CLIENT and LEGAL

**Finding.** The freeze note: "upon formal sign-off of Section 18, this document is completely frozen.
No further modifications, workflow adjustments, or structural changes may be initiated by the
Contractor without an executed amendment to the master contract."
Section 16 states the opposite process: 11 workflow gaps (5 still open or partly open) "must be
resolved and documented before the development sprint that covers the relevant feature begins" — i.e.
after signature. Section 15 likewise leaves four estimation-blocking questions open (RE-01, RE-04,
TI-02, plus partials on TI-05/TI-06/RE-05).
*Consequence as written:* every gap resolution after signature is a document modification requiring a
contract amendment. Either the project runs on a permanent amendment treadmill, or the freeze clause
is quietly ignored — and an ignored clause in a fixed-price contract is a dispute waiting to happen.

Related and also missing: no project timeline, no milestone list (despite CC-04's "milestone
contract"), no launch date, no per-FR acceptance criteria (UAT is only mentioned for the AI accuracy
bar), no change-control process, and no definition of done.

**Recommended resolution.** Add a **carve-out**: resolutions of the named open questions and workflow
gaps, recorded in a **controlled decision log**, are deemed part of the baseline and do not require a
contract amendment. Define what counts as a "structural change" and name who arbitrates. The
alternative — resolving everything before signature — is cleaner but is unlikely to be achievable on
the current timeline.

**Also worth producing as contract annexes:** project timeline, the milestone list the milestone
contract refers to, per-requirement acceptance criteria (UAT is currently defined only for the
accuracy bar), a change-control process, and a definition of done.

---

# K. Document integrity

### G-84 — BLOCKER — Section 1.2 does not exist
**Class:** OPEN — CLIENT

**Finding.** The document jumps from `## 1.1 The Two Parts of the Platform` to
`## 1.3 Marketing Website`. Section 1.2 is referenced elsewhere as the place where scope exclusions
live: TI-05 says the API leaning "confirms Section 1.2's existing exclusion". So the PRD's
**out-of-scope list is missing from the PRD**. On a strict fixed-price contract (CC-04) with a
baseline-freeze clause (Section 16 note), a document with no exclusions section means everything not
explicitly excluded is arguably in scope.
*Scenario:* client asks for a public API in month 4. SayOne points to "Section 1.2 exclusion". That
section does not exist in the signed baseline. There is no defence.

**Recommended resolution.** **Write it before signature.** Seed it from the items this document
recommends as limitations, so the exclusions list is evidence-based rather than improvised:

> English-only UI and reports · no historical data import · no external auditor or regulator access ·
> no SSO, SCIM or IP allowlisting · manual attestation for regulator submission (no submission API) ·
> no public API · no HR system integration · no dedicated mobile app · no DORA Register of Information
> · no AML instrument content in the requirement library *(subject to G-12)* · no sample generation
> *(subject to G-33)*

### G-85 — HIGH — Five FR IDs are missing with no explanation: FR-22, FR-23, FR-26, FR-29, FR-71
**Class:** PROPOSED

**Finding.** FR-21 is followed by FR-21b, FR-21c, then FR-24. FR-25 is followed by FR-27. FR-28 by
FR-30. FR-70 by FR-72. Estimators cannot tell whether these were deliberately deleted (and if so, what
they were) or lost in the rewrite from SRS v2.0. FR-71 sits exactly at the Section 10 → Section 11
boundary (communication channels → IT inventory), the highest-risk place for a dropped requirement.

**Recommended resolution.** Publish a **reconciliation table** mapping SRS v2.0 IDs to PRD v4.0 IDs,
marking each missing ID *withdrawn* or *merged into `FR-xx`*.

### G-86 — MEDIUM — Two conflicting version schemes in one document
**Class:** PROPOSED (documentation)

**Finding.** Header says "Version 4.0 · June 2026" and "SRS v4.0". Section 17 history calls this same
document "v8.0 — PRD v4.0". Content carries edits dated 3 Jul 2026 while the version stays June 2026.
Sign-off (Section 18) says "agreed product baseline as of June 2026". If the signed artefact is dated
June 2026 but contains July 2026 commitments (the 85% AI accuracy clause, the IP clause), the scope of
the signature is ambiguous.

**Recommended resolution.** **One version identifier and one date on the signed artefact.** If July
commitments are inside it — and they are, including the accuracy bar and the IP clause — then it is
not "as of June 2026", and the signature's scope is ambiguous until that is fixed.

### G-87 — MEDIUM — Section 16's evidence base has been declared void by Section 16's own note
**Class:** OPEN — CLIENT

**Finding.** Section 16 states the 11 gaps "were identified through a cross-document audit of the RED
v2.0, Narrative v3, and PRD v3.0". The Version Supremacy note in the same section says no engineering
choice "may be justified by referencing legacy text from earlier versions". So the source documents
needed to resolve GAP-01/03/09/10/11 cannot legally be cited when resolving them.

**Recommended resolution.** **Pull the residual detail forward** into the PRD before freeze. That is
cleaner than carving out an exception to the version-supremacy rule, and it removes the awkwardness of
resolving gaps by citing documents the same section forbids citing.

### G-88 — LOW — `.docx` is the signed baseline, `.md` is the readable copy, and they can drift
**Class:** PROPOSED

**Finding.** The header note says "if the two disagree, the .docx wins", but there is no automated
check.

**Recommended resolution.** A **CI check** that regenerates the markdown from the `.docx`
(`scripts/docx2md.py` output vs. the committed `.md`) and fails the build on any difference. The
convention that the `.docx` wins is only safe if divergence is detected.

---

# Conflicts between finding and resolution

Three places where the recommended resolution deliberately does **not** adopt the finding's own
suggested fix:

| Gap | Finding suggests | Recommended instead | Why |
|---|---|---|---|
| **G-20** | Crypto-shredding as the erasure mechanism ("delete the key, keep the audit stub") | **Do not adopt it.** No deletion path for protected classes; minimise personal data at source; document the retention position; escalate the residual conflict as a legal decision | Destroying a firm's key renders six-year records unreadable. That is deletion by another route, and it contradicts the PRD's rule that these records cannot be deleted by anyone including administrators |
| **G-11** | A firm-held key as the answer to account-owner visibility | **Out of MVP.** Use per-firm keys with bound encryption context, separation of key administration from decrypt rights, zero standing access, and operator access surfaced in the firm's audit trail. Disclose the residual position | A firm-held key lets a firm make its own non-deletable records unreadable — the same collision as G-20, moved to the customer side |
| **G-28** | Names a specific managed model service as the example resolution | **Provider and model stay unselected**, chosen against stated criteria (EU residency, no-training and no-retention terms, measured accuracy, cost, exit) | The PRD names no provider. Recording one as the answer converts an open decision into an assumed commitment |

---

# Decision sequencing

**Before signature — contract and scope integrity**
G-84 exclusions section · G-83 freeze carve-out · G-82 IP redraft · G-12 AML scope · G-79 Portal scope
boundary · G-67 AWS operating model · G-77 support and maintenance terms.

**Before estimation — materially changes cost**
G-33 sampling model · G-28 inference hosting · G-27 accuracy definition · G-20 erasure position ·
G-23 offboarding · G-70 storage and cost model · G-14 Register of Information in or out · G-72 real
scale figures.

**Before the relevant sprint**
All of Section A (the role contradictions — most close in a single workshop) · G-35 period object ·
G-39 service-line change handling · G-50 report distribution · G-53 clocks and calendars ·
G-59/G-60/G-61 department taxonomy, org chart validation, call tree · G-42 version pinning.

**Write down as limitations rather than build**
G-30 English-only UI · G-47 no historical import · G-58 no auditor access · G-71 no SSO · G-16 manual
submission attestation · G-14 no Register of Information · G-64 softened hardware-register claim.

**Scope additions recommended for approval**
G-07 delegation · G-37 finding comment thread · G-46 evidence library · G-48 bulk assignment · G-49
global search.

---

**Nothing in this document has been approved.** Each resolution is a recommendation with its class
stated. Where a resolution would add scope to a fixed-price milestone contract, it says so.
