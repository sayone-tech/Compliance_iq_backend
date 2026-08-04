# ComplianceIQ PRD v4.0 — Architectural Gap Analysis

Source reviewed: `docs/requirement-specification/PRD.md` (791 lines, PRD v4.0 + 25 Jun call + Sosinna Drive comments layered in)
Date: 2026-07-29

## How to read this

These are findings the PRD does **not** already track. Section 15 (open questions) and
Section 16 (11 workflow gaps) are the document's own self-declared gap list — items already
listed there are excluded unless the PRD's stated resolution is itself wrong, incomplete or
in conflict with something else.

Severity:
- **BLOCKER** — cannot be safely estimated, signed, or frozen without an answer.
- **HIGH** — will cause rework, contract dispute, or regulatory exposure if left.
- **MEDIUM** — needs a decision before the relevant sprint.
- **LOW** — clarification / hygiene.

Total findings: 88. Ordered by subject area, most product-critical first; document integrity
and versioning hygiene is last (Section K).

---

# A. Contradictions inside the document

**G-01 — HIGH — Remediation Owner visibility is a THREE-way contradiction, not two-way.**
The PRD flags this as two-way (Section 9.1 flag: FR-52 vs. FR-42 comment). It is three-way:
1. Section 3.1 role table: "Sees only their own assigned tasks."
2. FR-52: personal view is "the only compliance view they need".
3. GAP-07 / FR-42 comment: "view access to everything, not just their own assigned item."
Resolving 2 vs. 3 without also amending 1 leaves the role definition table wrong.
*Also unanswered inside option 3:* "everything" — everything in the firm, or everything on
Findings they own a milestone for? A Remediation Owner is often a business-line manager, not
compliance staff. Giving a Trading desk head read access to every AML finding in the firm is a
material access-control decision, not a dashboard tweak.

**G-02 — HIGH — IT/Systems Admin cannot see tests, but the workflow requires them to.**
Section 3.1: IT/Systems Admin "Cannot see compliance tests or findings."
Section 7.1 step 3: "Other team members (for example, the IT manager) can upload specialist
evidence to specific steps."
These cannot both be true. Uploading evidence to a test step requires seeing the test step.
Needs a scoped "contributor on assigned test step" permission that is not in the eight-role model.

**G-03 — HIGH — Senior Management is defined as read-only but performs three write actions.**
Section 3.1: "Read-only access to dashboards and reports." Yet FR-44 requires their sign-off to
close a Finding, FR-58 requires their report sign-off, and Section 8.1 requires them to
acknowledge escalations within five business days. Sign-off is a write. The role definition
needs rewriting as "read-only on operational data, write on approvals".

**G-04 — HIGH — The AML Officer is an actor in the workflow but not one of the eight system roles.**
Section 7.1 step 11 makes the AML Officer a mandatory gate ("separately reviews and formally
agrees"), and FR-55 makes the report un-generatable without it. The role is described only as
"a Senior Management or CCO-level user". FR-64 separately names the MLRO.
*Scenario:* a firm's MLRO is a Compliance Officer by system role, not Senior Management or CCO.
The AML sign-off gate cannot be satisfied, and no report can ever be generated.
Either add a ninth system role, or make AML Officer an assignable flag on a user.

**G-05 — HIGH — Two-person sign-off rules can deadlock in the target customer size.**
TI-06 says MVP firms are capped around 50 people with ~10 platform users. FR-64 confirms one
person often holds two roles (CCO + MLRO). Against that:
- FR-32: two senior approvers on every WSP mapping, excluding the policy author.
- FR-44 + FR-45: CCO + one Senior Management to close a Finding, excluding the recorder.
- FR-21c: sample change needs "one other senior team member".
*Scenario:* a 12-person CASP with one CCO, one compliance officer, and a two-person board where
one board member wrote the policy. The remaining approver pool is size 1. Every closure blocks.
The PRD never states a minimum viable governance headcount, nor a documented break-glass path.
Needed: either a stated minimum (e.g. "the platform requires at least 1 CCO + 2 Senior Management
users") enforced like FR-15, or an exception flow with mandatory justification.

**G-06 — HIGH — Only FR-15 has a minimum-headcount guard, and it guards the wrong role.**
FR-15 requires two Firm Super Admins. Firm Super Admin does not appear in any approval path.
The roles that actually block the workflow if vacant — CCO, Senior Management — have no minimum.
*Scenario:* the sole Senior Management user resigns. Every Finding in the firm becomes
uncloseable and no report can be signed off. Nothing in the platform warns of this.

**G-07 — HIGH — No delegation, deputy, or out-of-office model. The CCO is a single point of failure.**
Only the CCO can: assign tests (FR-20), approve tests (step 10), confirm milestone dates (step 12),
generate the report (FR-55), and co-sign closures (FR-44).
*Scenario:* CCO takes three weeks' leave at quarter end. No test can be assigned, no test approved,
no report generated. There is no "acting CCO" concept and no delegation-with-audit-trail feature.
This is a mandatory feature for a governance product, and it is absent entirely.

**G-08 — MEDIUM — The "three findings = High" rule collides with "officer confirms the rating".**
Section 8.1 makes any test with 3+ findings automatically High. Section 8.3 confirmed decision:
"Risk rating is calculated automatically ... the compliance officer confirms the rating, they do
not manually enter it." No downgrade path is defined.
*Scenario:* a documentation test produces three trivial findings (three policies with a stale
version date in the footer). It is auto-rated High, which fires immediate alerts to the CCO and
every Senior Management user, opens a five-business-day acknowledgement clock, and per Section 8.1
"may also trigger a formal notification to the national regulator within four hours".
Needed: either an explicit CCO override with mandatory justification, or a severity-weighted
count instead of a raw count.

**G-09 — HIGH — Section 8.1 wrongly ties compliance-test findings to the DORA 4-hour clock.**
"Three or more findings in a test ... Under DORA, this may also trigger a formal notification to
the national regulator within four hours." The DORA major-incident notification obligation is
triggered by an *ICT-related incident*, not by the outcome of a compliance testing exercise.
Wiring a finding count to a regulator-notification workflow risks generating spurious regulatory
filings. Recommend: the 4-hour path belongs only in Section 11 (FR-75/FR-76), and Section 8.1
should be corrected. Flag for Sosinna to confirm as domain expert.

**G-10 — MEDIUM — FR-47 (plan locked before report) and GAP-06 (owner assigned after consensus) may be circular.**
FR-47/step 12: milestone dates must be confirmed with Remediation Owners before the report can be
generated. GAP-06 remains open on "whether a Remediation Owner can be assigned pre-CCO-approval,
and what happens to that assignment if the CCO rejects the test." If assignment is only permitted
post-approval, and approval is required before the report, and the report requires confirmed owner
dates, the ordering is tight but workable — but if the CCO rejects a test after owners have already
confirmed dates, the PRD does not say whether those confirmations are voided or retained.

**G-11 — MEDIUM — SA-06 (Portal cannot see firm data) vs. the 25 Jun call ("pretty much everything") vs. NFR-01.**
The PRD flags this as an open question but does not surface the architectural consequence:
NFR-01 promises "No firm can ever access another firm's data, even accidentally", and TI-01 puts
the whole platform in an **AWS account owned solely by the Client (Synergy)**. Synergy is also the
reseller (CC-06) and a consulting firm that may compete with, or advise, the firms on the platform.
So the tenant-isolation guarantee protects firms from *each other* but grants the account owner
infrastructure-level access to every tenant's evidence, including sampled KYC records.
A contractual NDA clause (the SA-08 approach) is not a technical control.
*Needed:* explicit statement of what the account owner can technically see, and whether any
cryptographic control (per-tenant keys held outside the account, envelope encryption with a
firm-held key) is in scope. This is a sales objection waiting to happen.

---

# B. Regulatory / domain scope

**G-12 — BLOCKER — The stated regulatory scope is MiCA + DORA, but the product is full of AML content.**
Named throughout: AML Officer sign-off gate (step 11), AML Analyst role, transaction monitoring,
customer risk ratings, sanctions screening, KYC file sampling, UBO refresh, AML/CFT supervision,
"AML-xx" test ID family (GAP-02). For an EU CASP, these obligations come from **AMLD5/AMLD6, the
2024 AML package (AMLR/AMLD6 recast, AMLA), and the Transfer of Funds Regulation (EU 2023/1113,
the crypto Travel Rule)** — not from MiCA and not from DORA.
*Consequence:* either (a) the requirement library must cover AML instruments, in which case the
scope line "Regulations covered: MiCA and DORA" is wrong and the content-authoring effort is much
larger than estimated, or (b) AML tests are out of scope, in which case the AML Officer gate, the
AML sign-off, and the AML test family must be removed from the workflow.
This is the single largest scope ambiguity in the document and it is not in Section 15.

**G-13 — HIGH — Article citations need domain-expert verification before they are hardcoded into the report.**
SA-01: "TM-01 maps to the transaction monitoring obligations under MiCA Art. 92."
FR-66: "MiCA Art. 68(2) requires the compliance function to be independent."
MiCA Art. 92 concerns the prevention, detection and reporting of **market abuse**, and Art. 68
concerns **governance arrangements** for CASPs generally. AML transaction monitoring is not a MiCA
Art. 92 obligation. FR-40 makes every Finding carry a regulation article reference, and FR-56 puts
those references in the formal report given to senior management and shown to inspectors.
*Consequence:* a wrong article reference in an inspection-grade report is a reputational and
liability issue for both SayOne and Synergy. Needed: a verified requirement-to-article mapping,
signed off by Sosinna, before any is hardcoded, plus a per-citation "verified by / verified on"
field in the Portal.

**G-14 — HIGH — The DORA Register of Information is entirely absent.**
FR-73/FR-74 track CIFs, CTPPs, and vendors with five fields (name, service type, contract ref,
tier, next review date). DORA Art. 28(3) requires firms to maintain and annually submit to their
NCA a **Register of Information** on all ICT third-party arrangements, in a prescribed ESA
template with a large fixed schema (LEIs, function identifiers, contract dates, data locations,
subcontracting chains, substitutability assessments, exit plans). This is the most operationally
demanding DORA artefact and the one CASPs most need software for.
Either it is in scope — in which case FR-74's five fields are a fraction of the work — or it is
excluded, which needs stating (see G-84: there is no exclusions section to state it in).

**G-15 — HIGH — DORA incident reporting is modelled as one report; it is three.**
FR-76 covers the initial notification and its clock. DORA requires an **initial notification, an
intermediate report, and a final report**, each with its own deadline and content, plus
reclassification handling if an incident later crosses the major threshold.
*Scenario:* an incident is classified as major on day 1, the initial notification fires, and the
platform then has nothing to track the intermediate report due days later or the final report due
weeks later. The firm misses a regulatory deadline while believing the platform is tracking it.
That is worse than not having the feature.

**G-16 — MEDIUM — FR-76 "submits it" — there is no submission channel.**
NCA incident notification is per-country and generally via a national portal or secure email; there
is no pan-EU submission API. So "the CCO reviews it, edits it as needed, and submits it" must mean
*downloads it and submits it elsewhere*, and "the platform tracks whether the submission has been
made" must mean *the CCO ticks a box*. State this as a manual attestation, or the acceptance test
for FR-76 is unwritable.

**G-17 — MEDIUM — Branch jurisdictions are captured but no jurisdiction-specific content model exists.**
Section 5 says home jurisdiction "determines which national regulator's rules apply on top of base
MiCA" and branch jurisdictions "layer additional local rules". SA-07 only maps **service lines** to
Requirement IDs — nothing maps jurisdictions to Requirement IDs.
The 25 Jun note partly cuts this ("testing runs at the entity holding the EU licence; branch-level
testing not required for EU-only branches"), but that removes branch testing, not the home-jurisdiction
national overlay, which is still promised. Either build a jurisdiction dimension in the Portal
content model, or drop the national-overlay promise from Section 5.

**G-18 — MEDIUM — RES-02 "significant firm" (GAP-03) has a knock-on the PRD does not note.**
Beyond "who flags it", DORA advanced/threat-led testing (TLPT) is a specialist exercise run by
external red teams under a supervisory framework. If a firm is flagged significant, the platform
needs at minimum an evidence slot and a multi-year cycle, not a normal test procedure. Confirm the
platform only *tracks* TLPT rather than *guiding* it.

**G-19 — LOW — No handling of regulatory instruments with staged application dates.**
MiCA and DORA both have transitional/grandfathering provisions and RTS/ITS that land after the base
text. SA-03's monitoring records "effective date and date-of-download" (25 Jun note), but nothing
models "this requirement applies from date X" or "this requirement no longer applies after date Y".
A firm onboarding today should not be scheduled tests for a requirement that applies next year.

---

# C. GDPR and data lifecycle

**G-20 — BLOCKER — Immutable evidence retention directly conflicts with GDPR erasure, and the PRD never mentions it.**
Section 2 and NFR-07: evidence files "cannot be deleted by anyone", audit log "cannot be modified
by anyone", six-year minimum, no user including administrators can delete.
NFR-06: the platform is GDPR-compliant as a data processor.
Section 7.1 step 4 explicitly contemplates evidence that is **sampled KYC files** — i.e. identity
documents, addresses, and dates of birth of the CASP's retail customers, who are data subjects with
Art. 17 erasure rights and Art. 16 rectification rights.
*Scenario:* a retail customer of a CASP exercises the right to erasure. The CASP (controller) is
obliged to act, and instructs SayOne (processor). The platform is architecturally incapable of
deleting the file. The CASP cannot comply, and the platform is the reason.
The usual answer is a legal-obligation retention exemption under Art. 17(3)(b) — but that must be
*documented, scoped, and defensible*, and it is not automatic for every file a tester happens to
upload. Needed before build:
  - a lawful-basis and retention register per data category,
  - crypto-shredding or field-level redaction as the technical erasure mechanism, distinct from
    record deletion (delete the key, keep the audit stub),
  - a documented DPIA,
  - guidance to testers on minimising PII in uploads (see G-21).
None of this exists in the PRD, and NFR-06 is a single sentence.

**G-21 — HIGH — "No PII" is asserted for CSV imports but ignored for evidence uploads.**
FR-72's 25 Jun note is explicit: monitoring extracts are "aggregated counts and comparatives only,
explicitly no PII and no individual customer-level data". Meanwhile FR-24 permits arbitrary PDFs,
images, video, audio and ZIPs, and the workflow expects KYC file review. The controlled channel is
locked down; the uncontrolled channel is wide open.
Needed: an evidence-handling policy (redaction guidance, a "contains personal data" flag per upload
driving retention and access rules), or an explicit accepted-risk statement.

**G-22 — HIGH — There is no data disposal process at end of retention.**
Everything says "minimum 6 years". Nothing says what happens at 6 years and one day. Under GDPR
storage limitation, indefinite retention is not the safe default it appears to be. Needed: a
retention-expiry job, a legal-hold override, and a disposal certificate for the firm's records.

**G-23 — BLOCKER — No firm offboarding / contract-termination data path.**
The PRD covers onboarding in detail (Section 5) and never covers exit. Open questions:
- A firm cancels. Data cannot be deleted (6-year rule). Who stores it, and who pays for the storage?
- Does the firm get a full export? In what format? Is the audit log included?
- CC-06 makes Synergy the reseller and contract owner — does the firm's data stay in Synergy's AWS
  account after the relationship ends, and on what lawful basis?
- Under DORA Art. 28, the *firm* must have a documented exit strategy for its ICT providers —
  ComplianceIQ is one. A compliance product that cannot support its own customer's exit plan will
  fail the customer's own vendor due diligence.
This is a blocker because it changes the storage cost model, the contract, and the architecture.

**G-24 — HIGH — SayOne/Synergy is itself an ICT third-party provider under DORA, and the PRD never treats it as one.**
Every customer is a DORA-regulated financial entity. Onboarding ComplianceIQ triggers, for them:
Art. 28 due diligence, mandatory contractual clauses (Art. 30) covering data location, access,
audit rights, incident reporting to the client, subcontracting limits, exit assistance and service
levels, plus entry in their Register of Information.
The PRD has no requirement to support any of it — no audit-rights clause, no client-facing incident
notification commitment, no subcontractor disclosure, no right-to-inspect.
*Consequence:* the first enterprise CASP's procurement team will block signature. This is a sales
blocker disguised as a documentation gap.

**G-25 — MEDIUM — No DPA, no sub-processor list, no international-transfer position.**
NFR-06 references "a Data Processing Agreement" that does not exist as an artefact and has no
required contents. With a US-hosted LLM (see G-28) or any US-headquartered sub-processor, Chapter V
transfer mechanisms become relevant despite EU data residency.

**G-26 — MEDIUM — The revenue source file is highly commercially sensitive and gets no special treatment.**
FR-04 has each firm upload revenue by business line — that is competitively sensitive financial data,
sitting in an AWS account owned by a consulting group (TI-01) that also sells to that market (G-11).
It has no distinct access-control, retention, or encryption treatment anywhere in the PRD.

---

# D. AI / OCR / regulatory monitoring

**G-27 — BLOCKER — The 85% accuracy commitment has no measurable definition.**
Section 6.2 commits to "a minimum verified accuracy rate of 85% against pre-defined verification
text vectors during UAT", with all tuning inside the fixed fee. Undefined:
- **Which metric?** Precision, recall, F1, or top-k? These give wildly different numbers on the
  same model. A mapper that maps only the 20 most obvious sections and abstains elsewhere scores
  ~100% precision and ~15% recall.
- **Who supplies the verification vectors, and when?** If Sosinna supplies them after the build,
  SayOne is committing to an unbounded target. If SayOne supplies them, the client will reject
  self-marking.
- **How many vectors, from how many distinct WSP documents, in which languages?**
- **What happens if UAT lands at 82%?** Fixed fee + "all tuning included" + no exit criterion is an
  open-ended obligation. There must be a bounded remediation window and a fallback (e.g. ship with
  human-only mapping and a documented accuracy disclosure).
*Scenario:* UAT returns 79% recall on a Portuguese-language scanned WSP nobody had seen. Under the
clause as written, SayOne owes unlimited tuning at no cost, with no defined stop.

**G-28 — BLOCKER — Using an LLM appears to violate NFR-03 as written, and no AI stack is specified.**
NFR-03: "All client data must be stored in EU-based data centres." FR-31 requires an AI to read the
firm's entire compliance manual — a document containing the firm's confidential controls and often
personal data. Sending it to a model endpoint outside the EU breaches NFR-03 and the EU-residency
promise made to the client. The PRD names no model, no vendor, no hosting mode, no fallback, and
carries no inference cost line.
Needed decision before estimate: EU-region managed model (e.g. an EU-region Bedrock deployment),
self-hosted open-weights model, or an explicit carve-out to NFR-03 accepted in writing. Each has a
very different cost and accuracy profile — and the accuracy profile feeds directly into G-27's 85%.
Also missing: prompt-injection defence. The WSP is an untrusted uploaded document being fed to a
model whose output drives compliance mappings.

**G-29 — HIGH — OCR is promised with no accuracy target, no language scope, and no failure path.**
FR-30 accepts scanned PDFs via OCR. The customers are EU CASPs; a Portuguese, German, or French
WSP is the normal case, not the edge case. Undefined: supported languages, minimum scan quality,
what the platform does when OCR fails or returns garbage, and whether OCR output errors count
against the 85% mapping accuracy bar (they will, if measured end to end). Recommend measuring
mapping accuracy on clean text and OCR quality separately.

**G-30 — HIGH — The entire product has no internationalisation position.**
An EU multi-jurisdiction compliance product with: no UI language requirement, no report language
requirement, no statement of which language regulatory content is authored in, no date/number
locale rule, and no currency handling for the multi-line revenue file. If the answer is
"English only for MVP", that is a legitimate limitation — but it must be written down, because
it constrains the addressable market and the marketing site (MKT-01).

**G-31 — MEDIUM — SA-03 regulatory monitoring has no latency SLA and no feed-failure path.**
FR-35 says affected firms are "immediately alerted" when a regulation changes. SA-03's confirmed
constraint is RSS feeds and official public APIs only, polled. "Immediately" is bounded by the poll
interval plus the mandatory human review step (SA-04), which may be days. Needed: a stated detection
target ("within 24h of publication"), a stated review SLA for Sosinna's team, and behaviour when a
feed goes stale or changes format — with an alert to Sosinna's team, since silent feed death is the
failure mode that makes the whole feature untrustworthy.

**G-32 — MEDIUM — FR-51/FR-54 republish third-party regulator content with no licensing position.**
EUR-Lex content is broadly reusable with attribution; EBA/ESMA and national regulator content, and
any commercial feed under RE-05, are not uniformly so. Confirm reuse rights before building a news
panel that stores and redisplays third-party text.

---

# E. Testing module — functional gaps

**G-33 — BLOCKER — It is not defined whether the platform *selects* the sample or merely *records* it.**
Section 7.1 step 4 has the Lead Tester record population size, sample size, selection method and
methodology. FR-72's note confirms **no customer-level data enters the platform** — only aggregated
counts. Therefore the platform cannot draw a sample: it has no population to draw from.
*Consequence:* "Random statistical sampling" becomes an unverifiable self-declaration. The tester
picks records in their own KYC system and types "50 of 4,000, random" into ComplianceIQ. The stated
purpose of the sampling library — "it needs to be defensible to a regulator" (Section 4.2) — is not
achieved by recording a label.
Two very different products follow:
  (a) *Record-keeping* (cheap): the platform stores the assertion and the methodology reference.
  (b) *Sample generation* (expensive): the firm uploads a population identifier list, the platform
      draws the sample with a seeded, reproducible algorithm and stores the seed — genuinely
      defensible, but it means customer-level identifiers enter the platform, colliding with G-21.
The PRD reads as (b) and is scoped as (a). Must be decided before estimation.

**G-34 — HIGH — "Minimum sample size" is enforced but never specified.**
Step 4 and SA-08 say the platform enforces a minimum sample rate configured per test type. No
formula, no defaults, no source. Statistical sample sizing (confidence level, expected error rate,
population size) is a real algorithm, not a percentage. Confirm whether it is a flat percentage
floor, a lookup table authored by Sosinna's team, or a computed statistical sample.

**G-35 — HIGH — "Testing period" / "testing cycle" is never defined as an object.**
The report is per period (FR-56), comparison is per period (FR-53), partial testing is tracked
"across testing periods" (FR-19), and repeat findings look at "the previous testing period"
(FR-46). Yet no requirement defines what a period is, who opens or closes one, whether periods can
overlap, or whether a report can be generated mid-period. GAP-01 covers anchor dates for individual
tests, which is a narrower question. Without a period object, FR-46 and FR-53 are unimplementable.

**G-36 — HIGH — Repeat Finding detection (FR-46) has no matching rule and only a one-period lookback.**
"Checks whether a similar Finding was recorded in the previous testing period for the same
Requirement ID." Undefined: what "similar" means (same requirement ID alone? same root cause
category? text similarity?), and what happens for finding patterns that skip a period.
*Scenario:* the same control fails in Q1, is clean in Q2 because it was not tested, and fails again
in Q3. Under a strict one-period lookback it is never flagged as repeat — which is exactly the
pattern regulators care most about. Recommend: match on Requirement ID + root cause category over a
rolling window (e.g. 8 periods or 24 months) with the CCO confirming or dismissing the flag.

**G-37 — HIGH — Findings consensus happens outside the platform, breaking the single-source-of-truth claim.**
GAP-06's answer: "findings are communicated to control owners and management first; once consensus
is reached, the plan is documented with a timeline." There is no requirement anywhere for
in-platform commenting, discussion threads, @-mentions, or a review conversation on a Finding.
So the negotiation that determines what goes in the remediation plan happens by email, and the
platform records only the outcome. That contradicts Section 1's promise ("all in one place") and
leaves the audit trail materially incomplete for the most contested step in the process.
Recommend an append-only comment thread on Findings and tests, participants and timestamps recorded.

**G-38 — HIGH — Requirement-level "Not Applicable" has no owner, and conflicts with automatic test loading.**
FR-21b defines N/A at *test execution* level (immutable, reason required). FR-50 shows N/A as a
status at *Requirement ID* level on the dashboard. Nobody sets the latter. FR-07 loads requirements
automatically from confirmed service lines, so marking a whole requirement N/A contradicts the
derivation. Needed: who can mark a requirement N/A, whether it needs dual sign-off (it should — it
removes an obligation from the programme), and whether it survives a revenue-file re-upload.

**G-39 — HIGH — No rule for what happens to in-flight and historical work when service lines change.**
FR-08: re-uploading a revenue file "triggers a recalculation of applicable tests". Undefined:
- Requirements added: are tests scheduled immediately, or from next period? Is the firm retroactively
  non-compliant for the periods before the service line was declared?
- Requirements removed: what happens to a Planned test, an Ongoing test with evidence already
  uploaded, an open Finding, and an open remediation milestone under that requirement?
*Scenario:* a firm exits portfolio management in month 7. Two open High findings sit under
portfolio-management requirements with unmet milestones. Do they close? Stay open forever? Move to
an "orphaned" state? Regulators will still ask about them.
Recommend: removal never deletes; requirements move to `no longer applicable from <date>`, open
findings stay open and visible, historical results are retained and shown in comparison views.

**G-40 — MEDIUM — Re-uploading the revenue file changes the firm's regulatory obligations with no approval gate.**
FR-08 lets the firm update the profile "at any time". FR-05 has the CCO confirm derived service
lines at onboarding, but FR-08 does not restate that gate for updates.
*Scenario:* a Firm Super Admin uploads a corrected spreadsheet and silently removes a service line,
dropping 15 tests off the programme. That is a governance event and must require CCO confirmation,
a diff screen ("these 15 tests will stop being scheduled"), and an audit entry with justification.

**G-41 — MEDIUM — The revenue file template does not exist and is on the critical path.**
FR-04 depends on "the platform's template", which the 25 Jun note says Sosinna is still sourcing
("the EU equivalent of a US Form 1040"). No column spec, no validation rules, no error-handling
behaviour, no versioning of the template, and no rule for what happens when a firm uploads against
an old template version. The same note also states selection "can't be fully automated 1:1 — a
single revenue line can span two service lines", which means the derivation is a *suggestion*
requiring manual confirmation — closer to a guided picker than the automatic derivation Section 5
describes. Section 5's note ("The firm does not manually tick a list of service lines") should be
corrected.

**G-42 — MEDIUM — GAP-10's second half is the more important half and is being under-weighted.**
GAP-10 asks about a banner vs. persistent notice (a UI question, and the note says the UI designer
can decide alone) *and* "does the system record which rule version the test was run under". The
second is a data-model requirement with direct audit consequence: SA-04 promises in-flight tests
continue on the version they started, which is only provable if the version is pinned on the test
execution record. Split GAP-10 into a UI item and a mandatory data-model item.

**G-43 — MEDIUM — No behaviour defined for retiring a Requirement ID or a test procedure mid-cycle.**
SA-01 says IDs can be retired. Undefined: what happens to scheduled tests, in-flight tests, and open
findings under a retired ID; whether the retirement propagates to all firms at once; whether a firm
mid-test is force-migrated at period end.

**G-44 — MEDIUM — FR-53 trend comparison is invalid across procedure versions.**
The CCO compares this quarter to last quarter to see if compliance is improving. If the test
procedure changed between them (which SA-01/SA-04 make routine), the comparison is apples to
oranges and nothing warns the user. Recommend annotating comparison views where the underlying
procedure version differs.

**G-45 — MEDIUM — Partial testing (FR-19) has no coverage model.**
"The platform tracks which parts of a Requirement ID have been covered across different testing
periods." There is no definition of "parts" — a requirement is not decomposed into sub-scopes
anywhere in the Portal content model (SA-02 defines steps, not scope segments). Without a defined
sub-scope taxonomy authored in the Portal, coverage tracking is free text and cannot be reported on.
*Scenario:* Q1 covers KYC, Q2 covers UBO refresh (the PRD's own example). To say "the requirement is
now fully covered", the platform must know that {KYC, UBO refresh} is the complete set. Nothing
defines that set.

**G-46 — MEDIUM — Evidence shelf life (FR-28) has no source of truth.**
"For example, a BCP test report is only valid evidence if it is less than 12 months old." Who sets
the validity period — per evidence type in the Portal, per test procedure, or per upload? Not stated.
Also no requirement for an evidence library: one BCP report is valid evidence for several tests, but
the model implies re-upload per test, producing duplicates with independently tracked ages.

**G-47 — MEDIUM — No historical data import at onboarding.**
Firms arrive from spreadsheets with years of prior testing history. Nothing supports importing it.
*Consequence:* FR-53 (period comparison) and FR-46 (repeat findings) produce nothing useful for the
first 12 months of every customer — the two features most likely to be demoed. State as an accepted
limitation, or scope a historical import.

**G-48 — LOW — No test cloning, bulk assignment, or carry-forward of prior-period setup.**
A CCO assigning 40 quarterly tests one at a time will ask for this in week one.

**G-49 — LOW — No global search.**
"Find every finding mentioning sanctions screening" / "find the evidence file we uploaded last
March" is unsupported anywhere in the document. For a six-year evidence archive this is not optional.

---

# F. Reports, notifications, dashboard

**G-50 — HIGH — FR-59 auto-emails an unencrypted report containing every open compliance failure.**
"Once signed off, the report is automatically sent to the firm's configured distribution lists."
No requirement covers: attachment vs. expiring secure link, encryption, recipient verification,
whether external (non-user) email addresses can be on a list, or what happens when a recipient
leaves the firm and the list is stale.
*Scenario:* a distribution list still contains a former board member's personal Gmail. The Q3
report — every High finding, every unremediated control failure — is emailed there automatically
with no human in the loop. This is the highest-impact data-leak path in the product.
Recommend: secure link with authenticated access as the default, attachments only if explicitly
enabled per list, mandatory periodic list re-validation by the CCO, and an audit entry per delivery.

**G-51 — MEDIUM — Exactly six distribution lists, fixed, with no external-recipient model.**
Section 10.6 fixes the list count at six. No custom lists, no per-report override, no statement on
whether external auditors, outside counsel, or non-login board members can be recipients. Real firms
will need at least the external-auditor case.

**G-52 — MEDIUM — "Acknowledged" is tracked but never defined.**
Section 2 logs whether each alert was acknowledged; FR-43 escalates if a High-finding escalation is
"not formally acknowledged within five business days". No requirement describes the acknowledgement
action — clicking an email link, logging in, or an explicit in-app button — nor who can do it on
whose behalf. Without a defined act, FR-43's escalation cannot be built or tested.

**G-53 — MEDIUM — "Five business days" and "four hours" have no calendar or timezone definition.**
Firms operate across EU jurisdictions with different public holidays; the platform stores one
jurisdiction per firm but no working calendar.
*Scenario:* a High finding is raised at 17:00 on 23 December. In Portugal 24–26 December are
effectively non-working; in another Member State the pattern differs. The escalation fires on a
different real-world date depending on an unstated rule. Same problem for the DORA 4-hour clock
(is it wall-clock? it should be — but say so) and for every "30/14/7/1 day before" reminder.
Needed: firm-level timezone, working-calendar source, and an explicit statement of which clocks are
calendar-time and which are business-time.

**G-54 — MEDIUM — No email deliverability, bounce, or provider requirement.**
The whole notification model (NT-01 resolved: email and in-platform only) rests on email arriving.
Nothing covers the sending provider, SPF/DKIM/DMARC, bounce and complaint handling, or what the
platform does when a report delivery hard-bounces. A silently bounced report that the platform
records as "distributed" is an audit-trail falsehood.

**G-55 — MEDIUM — No report generation performance target, and the dashboard target is the easy path.**
NFR-05 targets two-second dashboard loads. The genuinely hard operation is generating a
multi-hundred-page PDF (FR-56, eight sections, every test, every finding, embedded evidence
references) — potentially minutes, needing async generation, progress feedback, and failure
handling. None of that is described; FR-60 reads as a synchronous download.

**G-56 — MEDIUM — No report preview, draft, or regeneration path.**
FR-61 makes reports immutable once signed off. Nothing describes the state before that: can the CCO
preview a draft, discard it, and regenerate? What happens if the CCO generates the report, then
Senior Management refuses to sign — is that report void, does it persist as a rejected artefact,
and what does the milestone clock (FR-47, started at generation) do in the meantime?
*Scenario:* CCO generates on 1 Oct, milestone clocks start. Senior Management rejects on 5 Oct over
a wording issue. A corrected report is generated on 8 Oct. Do the milestone clocks restart, or is
the firm now seven days into deadlines against a void report?

**G-57 — LOW — FR-48 "more metrics can be added based on the CCO's preferences" is unbounded.**
In a fixed-price contract, this needs a fixed initial metric set with anything further via
amendment, or a configurable-widget feature that is properly scoped and estimated.

**G-58 — LOW — No external/regulator/auditor read-only access.**
"Regulator View" was removed in Narrative v3, and reports go out by email instead. External auditors
are a routine need for these firms. Record as a deliberate limitation so it is not re-litigated.

---

# G. Organisation & staff module

**G-59 — HIGH — FR-66's "revenue function" test has no data to run on.**
The platform is to flag a governance red flag if the CCO reports into a revenue function such as
Sales or Trading. FR-63 captures `department` as a free-text-style field. Nothing classifies a
department as revenue-generating vs. control.
*Scenario:* a firm names its trading desk "Markets Group". No match on "Sales" or "Trading", no flag
raised, and the firm believes the platform checked. A silent false negative in a governance control
is worse than no control. Needed: a controlled department taxonomy with a revenue/control
classification maintained in the Portal, mapped at onboarding.

**G-60 — HIGH — The org chart has no requirements for malformed hierarchies.**
FR-65 builds the tree automatically from reporting-line fields. Undefined: cycles (A reports to B
reports to A), multiple roots, orphans with no manager, matrix/dual reporting, and how FR-64's
multi-role person renders as a node. A CSV import (FR-62) will produce all of these on day one.
Needed: validation on import with a specific error report, and a defined rendering rule for
unresolvable structures.

**G-61 — HIGH — The BCP call tree is a single linear chain with no branch and no break handling.**
FR-70 assigns each staff member exactly one "next contact" and flags missing links. A single chain
means one unreachable person stops the cascade — the exact failure mode a call tree exists to
prevent.
*Scenario:* person 7 of 40 is on a flight. Persons 8–40 are never contacted. The platform reports
the chain as complete because every link is populated.
Needed at minimum: an alternate contact per person, or a tree/fan-out model, plus cycle detection
(A→B→A satisfies "every link populated" while contacting nobody else).

**G-62 — MEDIUM — Staff Member and Platform User records have no linkage or identity-matching rule.**
Section 10 defines the two record types; FR-64 says one person holding multiple roles is handled
"without creating duplicate records" but no mechanism is given. Undefined: the natural key for CSV
re-import (email? name? employee ID?), what happens when a Staff Member later receives a login,
and what happens on a name change.
*Scenario:* the second monthly CSV upload uses "Rob Silva" instead of "Roberto Silva". Either a
duplicate staff record appears in the org chart and call tree, or an existing record is silently
overwritten. Needed: a stable external ID column in the template and a defined merge/conflict flow.

**G-63 — MEDIUM — Certification expiry marks a record "non-compliant" with no defined consequence.**
FR-67 flags the staff member. Nothing says whether that blocks anything — e.g. whether a Lead Tester
with a lapsed certification can still be assigned tests and sign results, and whether an expiry
mid-test invalidates work already done. Also missing: a certification-type library (free text will
make the register unreportable) and the ability to attach the certificate document itself as evidence.

**G-64 — MEDIUM — Hardware inventory is too thin for the DORA claim it is making.**
FR-69 captures device type, serial number, asset tag. A DORA-grade ICT asset register generally also
needs location, criticality, supported/EOL status, ownership, and the link to the ICT systems and
functions the asset supports. Either extend FR-69 or soften the claim that it satisfies DORA IT risk
management.

**G-65 — LOW — OS-06 (non-employee committee members) is marked "no update" but interacts with G-05.**
External NEDs and advisory committee members are exactly the people small firms rely on for the
second Senior Management sign-off. If they cannot exist in the system, G-05's deadlock gets worse.

---

# H. Non-functional, security, operations

**G-66 — BLOCKER — No backup, RPO, or RTO requirement — in a resilience-compliance product.**
NFR-08 gives an availability target (99.5%) and nothing else. Missing: backup frequency, backup
retention, restore-time objective, recovery-point objective, restore testing cadence, and a DR
region or strategy. Every customer is a DORA-regulated entity that must assess exactly these
attributes in its provider due diligence (G-24). Shipping a DORA product without stated RPO/RTO is
both an operational risk and a sales blocker.

**G-67 — BLOCKER — TI-01 (client-owned AWS account) has no operating model attached.**
"AWS, EU-resident data centre, on an account owned solely by the Client." Unresolved: who holds root
and billing; who pays the AWS bill (it is not in the fixed fee as described); how SayOne obtains and
retains deploy access; how many environments exist (dev/staging/UAT/prod) and in whose accounts;
who runs CI/CD; who is on call; what happens to SayOne's access at project end.
This also breaks two other statements:
- NFR-04 "not even the system administrators at SayOne can modify or delete this log" — true, but
  the *Client's* root admin can drop the database. The immutability claim is only as strong as the
  account owner's own controls, which the PRD never specifies.
- NFR-02 "each firm has its own encryption key" — with no KMS design, no rotation policy, no
  statement of who can use the keys, and no BYOK option. In a client-owned account, the client
  controls the keys for every tenant.

**G-68 — HIGH — Audit-log immutability has no technical mechanism.**
NFR-04 and FR-13 promise a tamper-proof, append-only log that no administrator can alter. A normal
relational table does not deliver that. Needed: an explicit design — WORM object storage
(e.g. S3 Object Lock in compliance mode), a hash-chained log with periodic anchoring, or a separate
append-only store with a distinct trust boundary from the application database — plus a documented
verification procedure a regulator or auditor can run. As written this is an unbacked claim in a
document whose entire value proposition is provability.

**G-69 — HIGH — No malware scanning of uploads.**
FR-24 permits arbitrary PDF, Office, image, audio, video, ZIP and CSV uploads into a multi-tenant
platform, retained for six years, redistributed to other users, and referenced from emailed reports.
Nothing in Section 13 requires virus/malware scanning, archive-bomb protection, content-type
verification, or safe rendering. ZIP archives are called out explicitly as an accepted type.

**G-70 — HIGH — No storage quota, and the cost model is unbounded on a fixed-price contract.**
FR-24/NFR-11 make max *file* size configurable but set no per-tenant or per-firm storage cap. Video
and screen recordings are accepted evidence types and must be retained six years, undeletable.
*Scenario:* 30 firms × 40 GB/year of video evidence × 6 years ≈ 7 TB of undeletable EU-region
storage, plus per-tenant encryption and backups. Under a fixed-fee build in a client-owned account
(G-67), it is not even stated who absorbs that. Needed: per-plan storage allowances, an overage
policy, and lifecycle tiering (e.g. move cold evidence to archival storage after N months, with
retrieval latency accepted).

**G-71 — HIGH — Authentication is under-specified for the enterprise buyer.**
FR-11 says email + password + "a second verification step on their phone". Missing: whether MFA is
TOTP, push, or SMS (SMS is explicitly out of scope for notifications under NT-01 — a probable
contradiction if SMS OTP was intended); password policy; account lockout and brute-force protection;
session lifetime and idle timeout; concurrent-session policy; MFA recovery.
*Scenario:* both Firm Super Admins lose their phones. FR-15 exists to prevent lockout, but nothing
describes an MFA reset path — and the Portal team recovering it for them (SA-06 says they cannot see
firm data) is undefined.
Also absent and expected by enterprise CASPs: SSO/SAML/OIDC, SCIM provisioning, IP allowlisting.
If these are out of MVP, state it — they are common procurement gates.

**G-72 — HIGH — NFR-05's concurrency figure contradicts TI-06's sizing.**
NFR-05: "up to 100 simultaneous users per firm". TI-06: MVP firms cap around 50 individuals with
typically ~10 platform users. 100 concurrent per firm is 10× the stated realistic ceiling, while the
figure that actually drives infrastructure — total concurrent users across all firms, and total
number of firms in Year 1 — is still unanswered (TI-06, estimation blocker). No data-volume targets
either (tests/firm/year, evidence GB/firm/year, findings/period). Load testing cannot be specified.

**G-73 — MEDIUM — No observability, monitoring, or platform-incident-response requirement.**
Nothing on application logging, metrics, alerting, error tracking, log retention, or what SayOne
does when the platform itself has an outage — including whether affected firms are notified, which
their own DORA obligations require them to receive (G-24).

**G-74 — MEDIUM — No environment or test-data strategy, though UAT carries a contractual obligation.**
Section 6.2 makes UAT the acceptance gate for the 85% AI accuracy commitment, but no UAT environment,
no seeded demo tenant, and no synthetic test data are specified. Realistic compliance test data
cannot be borrowed from production (it is customer PII).

**G-75 — MEDIUM — No accessibility requirement.**
No WCAG target anywhere. For an EU-market B2B SaaS sold to regulated financial entities — several of
which will have their own accessibility procurement requirements, and with the European Accessibility
Act now in force for in-scope services — this should be an explicit decision (target level, or a
stated exclusion), not silence.

**G-76 — MEDIUM — NFR-10's mobile requirement is unmeasurable and therefore unacceptable in a fixed-price contract.**
"The browser version should work well enough on mobile for approval sign-offs." Needed: named target
viewports, the specific flows that must work (Senior Management report sign-off, escalation
acknowledgement, finding closure sign-off), and the flows that explicitly need not.
Same defect class elsewhere: "professional report" (Section 1), "at-a-glance" (FR-48), "proactively
alerts" (FR-28), "without performance degradation" (NFR-05).

**G-77 — MEDIUM — No support, maintenance, warranty, or hypercare terms.**
CC-04 confirms a fixed-price milestone contract for the build. Nothing covers what happens after
go-live: defect warranty period and definition, support hours, response/resolution targets, who
runs production, regulatory-content updates as an ongoing service (RE-01 is still an open estimation
blocker), or SLA credits against the 99.5% target. This is a commercial gap with direct architectural
consequences (see G-67 on who operates the environment).

**G-78 — MEDIUM — No rate limiting, penetration testing, or secure-SDLC requirement for the platform itself.**
NFR-09 defers ISO 27001 and SOC 2 to a roadmap, TI-03 asks whether clients require them. Independent
of certification, a product that stores six years of regulated firms' compliance evidence should
carry explicit requirements for pre-launch penetration testing, dependency/vulnerability scanning,
secret management, and rate limiting. None are present.

---

# I. Platform Admin Portal — under-specification

**G-79 — BLOCKER — The Portal has 8 requirements against ~74 for the Firm Application, yet the fixed fee covers both equally.**
The IP/baseline note commits the fixed fee to "parallel development, deployment, and security
configuration of both the Firm Application and the Platform Admin Portal, both fully operational as
defined by this document's functional requirements". SA-01 to SA-08 do not come close to defining a
fully operational back office. Entirely absent:
- Portal user management, Portal roles beyond a single "Super Admin", and Portal MFA.
- A Portal audit log. NFR-04 says "every action in the platform" — is content authoring in scope?
  It must be: a change to a test procedure changes every firm's obligations.
- Content-authoring UX: how a multi-step procedure with evidence checklists, sampling rules and
  minimum sizes is actually built (SA-02 is one sentence).
- The review-and-publish workflow: SA-04 says "a review step" — by whom, how many approvers,
  what states, and is there a rollback/unpublish for a bad publication?
- Draft/staging content and preview before publication.
- Content import/export, and bulk authoring (the initial library is dozens of procedures).
- Per-jurisdiction content variants (see G-17).
- Cross-tenant content migration when a procedure version is superseded.
- Portal-side reporting beyond SA-08's usage report.
Recommendation: either write a full Portal requirement set before freeze, or explicitly scope the
Portal deliverable (e.g. "content authoring, versioning, publish workflow, firm list, system
settings — nothing further") so the fee maps to a bounded deliverable.

**G-80 — HIGH — No seat enforcement, despite seat-based pricing.**
CC-01 confirms seat-based plans configured per firm in the Portal at onboarding. SA-08's 25 Jun
addition gives month-end usage reporting (active users vs. subscribed seats). Nothing says what the
platform *does* when a firm exceeds its seats — block the invite, allow with a warning, allow and
report? Billing is off-platform via the reseller (CC-06), so there is no payment integration to
scope, but seat *enforcement* is a product behaviour that has to be decided.

**G-81 — MEDIUM — No marketing-site requirements beyond three sentences, and two open questions (MKT-04, MKT-05) sit on the delivery critical path.**
MKT-01 to MKT-03 define the site in three lines. Undefined: page inventory, who writes the copy,
lead-capture destination (a CRM? an email inbox?), GDPR consent/cookie banner for an EU-facing site
(mandatory, and currently unmentioned anywhere), analytics, and SEO. MKT-05 (domain) also blocks
CC-02 (branding), which is still open. If Demo Day (CC-05) is a real date, this is the most visible
deliverable with the least specification.

---

# J. Commercial and contractual

**G-82 — BLOCKER — The CC-03 IP clause as accepted has no background-IP or OSS carve-out, and is probably unperformable.**
Accepted text: "all right, title, and interest in and to this regulatory content, alongside all
platform source code, backend architectures, frontend user interfaces, and database schemas built by
the Contractor, belong 100% exclusively to the Client from the moment of creation. The Contractor
retains zero rights, ongoing claims, or implied licenses to any content or code within the platform."
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
Recommend a redraft: full assignment of purpose-built deliverables; background IP retained by SayOne
with a perpetual, irrevocable, worldwide licence to the Client; third-party OSS governed by its own
licences with a delivered SBOM. Flag before signature, not after.

**G-83 — BLOCKER — The baseline-freeze clause is logically incompatible with Sections 15 and 16.**
The freeze note: "upon formal sign-off of Section 18, this document is completely frozen. No further
modifications, workflow adjustments, or structural changes may be initiated by the Contractor without
an executed amendment to the master contract."
Section 16 states the opposite process: 11 workflow gaps (5 still open or partly open) "must be
resolved and documented before the development sprint that covers the relevant feature begins" —
i.e. after signature. Section 15 likewise leaves four estimation-blocking questions open (RE-01,
RE-04, TI-02, plus partials on TI-05/TI-06/RE-05).
*Consequence as written:* every gap resolution after signature is a document modification requiring
a contract amendment. Either the project runs on a permanent amendment treadmill, or the freeze
clause is quietly ignored — and an ignored clause in a fixed-price contract is a dispute waiting to
happen.
Recommend one of: (a) resolve all Section 15/16 items before signature (the freeze note itself hints
at this: "this review needs to be finished and folded in before signature"); or (b) add an explicit
carve-out — resolutions of named Section 15/16 items, recorded in a controlled decision log, are
deemed part of the baseline and do not require an amendment. Also worth defining: what counts as a
"structural change" and who arbitrates.

Related and also missing: no project timeline, no milestone list (despite CC-04's "milestone
contract"), no launch date, no per-FR acceptance criteria (UAT is only mentioned for the AI accuracy
bar), no change-control process, and no definition of done.

---

# K. Document integrity

**G-84 — BLOCKER — Section 1.2 does not exist.**
The document jumps from `## 1.1 The Two Parts of the Platform` to `## 1.3 Marketing Website`.
Section 1.2 is referenced elsewhere as the place where scope exclusions live: TI-05 says the
API leaning "confirms Section 1.2's existing exclusion". So the PRD's **out-of-scope list is
missing from the PRD**. On a strict fixed-price contract (CC-04) with a baseline-freeze clause
(Section 16 note), a document with no exclusions section means everything not explicitly
excluded is arguably in scope.
*Scenario:* client asks for a public API in month 4. SayOne points to "Section 1.2 exclusion".
That section does not exist in the signed baseline. There is no defence.

**G-85 — HIGH — Five FR IDs are missing with no explanation: FR-22, FR-23, FR-26, FR-29, FR-71.**
FR-21 is followed by FR-21b, FR-21c, then FR-24. FR-25 is followed by FR-27. FR-28 by FR-30.
FR-70 by FR-72. Estimators cannot tell whether these were deliberately deleted (and if so, what
they were) or lost in the rewrite from SRS v2.0. FR-71 sits exactly at the Section 10 → Section 11
boundary (communication channels → IT inventory), the highest-risk place for a dropped requirement.
Action: publish a reconciliation table mapping SRS v2.0 IDs to PRD v4.0 IDs, marking each
missing ID `withdrawn` or `merged into FR-xx`.

**G-86 — MEDIUM — Two conflicting version schemes in one document.**
Header says "Version 4.0 · June 2026" and "SRS v4.0". Section 17 history calls this same document
"v8.0 — PRD v4.0". Content carries edits dated 3 Jul 2026 while the version stays June 2026.
Sign-off (Section 18) says "agreed product baseline as of June 2026". If the signed artefact is
dated June 2026 but contains July 2026 commitments (the 85% AI accuracy clause, the IP clause),
the scope of the signature is ambiguous.

**G-87 — MEDIUM — Section 16's evidence base has been declared void by Section 16's own note.**
Section 16 states the 11 gaps "were identified through a cross-document audit of the RED v2.0,
Narrative v3, and PRD v3.0". The Version Supremacy note in the same section says no engineering
choice "may be justified by referencing legacy text from earlier versions". So the source
documents needed to resolve GAP-01/03/09/10/11 cannot legally be cited when resolving them.
Either the supremacy clause needs a carve-out for gap resolution, or the residual detail from
those documents must be pulled forward into this PRD before freeze.

**G-88 — LOW — `.docx` is the signed baseline, `.md` is the readable copy, and they can drift.**
The header note says "if the two disagree, the .docx wins", but there is no automated check.
Add a CI diff (`scripts/docx2md.py` output vs. committed `.md`) so a `.docx` edit that never
reaches `.md` is caught.

---

# Recommended priority order

**Resolve before signature (contract/scope integrity):**
G-84 (missing exclusions section), G-83 (freeze vs. open gaps), G-82 (IP clause), G-12 (AML in or
out of scope), G-79 (Portal scope), G-67 (AWS operating model), G-77 (support/maintenance terms).

**Resolve before estimation (materially changes cost):**
G-33 (sample generation vs. record-keeping), G-28 (AI hosting and NFR-03), G-27 (accuracy metric
definition), G-20 (GDPR erasure vs. immutability), G-23 (offboarding), G-70 (storage/cost model),
G-14 (DORA Register of Information), G-72 (real scale figures).

**Resolve before the relevant sprint:**
Everything in Section A (role contradictions — a two-hour workshop closes most of them), G-35
(period object), G-39 (service-line change handling), G-50 (report distribution security), G-53
(clocks and calendars), G-59/G-60/G-61 (department taxonomy, org chart, call tree).

**Add as explicit stated limitations rather than build:**
G-30 (English-only MVP), G-47 (no historical import), G-58 (no external auditor access), G-71
(no SSO in MVP), G-16 (manual regulator submission attestation).
