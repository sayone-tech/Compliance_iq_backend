<!-- Authoritative Markdown source for ControlIQ_Architecture_Review_Responses.docx.
     Regenerate the .docx with:
         python3 scripts/archmd2docx.py \
             docs/tech-spec/ControlIQ_Architecture_Review_Responses.md \
             docs/tech-spec/ControlIQ_Architecture_Review_Responses.docx
     Styles are inherited from ControlIQ_System_Architecture.docx, which the
     script uses as its template. -->

# C O N T R O L I Q

Header: ControlIQ — Architecture Review Responses v1.0    September 2026

Architecture Review — Responses to Client Feedback

Response Document — v1.0

Date: 3 September 2026    Prepared by: SayOne Technologies    Client: Sosinna Degefu

Responds to: *Architecture Review Feedback* (client, September 2026)

Applies to: *ControlIQ System Architecture Document*, MVP Reference Document v1.0 (31 August 2026)

## How to read this document

Each item below restates the question, gives a direct answer, and — where the answer changes the architecture — sets out the exact wording that will replace the current text in **System Architecture v1.1**. Nothing here is left as "we will consider it": every item closes with either a committed change, a confirmed clarification, or a named open decision with an owner and a due point.

Every item carries one of four dispositions:

| Disposition | Meaning |
| --- | --- |
| **Corrected** | The review found a genuine contradiction or an overstated claim in v1.0. The document is wrong and is being changed. |
| **Accepted** | The review proposed a control or a wording improvement. It is adopted as specified. |
| **Clarified** | The architecture is unchanged; v1.0 was ambiguous or under-specified and v1.1 states the detail explicitly. |
| **Open** | The answer depends on a decision the client owns. The options, the recommendation and the deadline are stated. |

Section 4 lists inconsistencies that were found while working through the review but were not raised in it. They are handled on the same terms, because a review that fixes ten contradictions and leaves five behind has not made the document trustworthy.

Section 5 is the consolidated change list for v1.1, and Section 6 is the open-decision register with owners and due points.

### A note on section numbers

The review refers to vector storage as Section 10.3 and to retention as 10.4. In v1.0 those are the other way round: **10.3 is Retention** and **10.4 is Vector Storage (Qdrant)**. Both topics are answered below; this document uses the v1.0 numbering throughout, and each item's heading shows the section numbers as the review cited them alongside the actual ones where they differ.

## 1. Highest priority

### 1.1 Information sent to AI providers

*Review sections 2.1, 8, 15.1 — actual sections 2.1, 8, 15, 15.1*

**Question.** Section 8 says document text, prompts and completions never leave the tenant's data environment, yet an external provider must receive redacted content. What exactly leaves the AWS environment, what is removed first, and how is EU residency, non-retention and no-training confirmed?

**Disposition: Corrected.** The review is right, and the sentence in v1.0 is wrong as written. It conflates two different boundaries: the **telemetry boundary** (logs, metrics, traces — where the claim is true and absolute) and the **inference boundary** (the model call itself — where redacted content does leave the account by necessity). v1.1 separates them.

**What actually leaves the client's AWS account**

Exactly three payload elements cross the boundary on a model call, and nothing else:

- **Redacted chunk text** — the text of WSP sections and regulatory articles after the Presidio tokenisation pass, with every detected entity replaced by a typed placeholder (`<PERSON_1>`, `<IBAN_2>`, `<EMAIL_3>` and so on). The provider receives document structure and regulatory language, never identities.
- **The prompt template** — a versioned, reviewed instruction string from the prompt registry. It contains no firm data.
- **The candidate Requirement IDs and their titles** — drawn from the shared regulatory library. This is public regulatory reference data, not firm data.

Alongside these, the call carries model parameters and an opaque job UUID. **No `tenant_id`, firm name, licence number or user identifier is included in any provider request**, so the provider has no means of attributing content to a firm even in aggregate.

**What never leaves under any circumstance**

Raw un-redacted text; the original PDF, DOCX or image bytes of any WSP or evidence file; the PII token map; KMS keys and per-firm data keys; any database row; the audit trail; any credential; the firm's identity. Document parsing (Docling) and OCR (Textract) both execute in-region inside the client's account, so the binary original never reaches a model provider at all — only parsed, chunked, redacted text does.

**Provider routing and how residency is actually guaranteed**

A contractual promise of EU residency is weaker evidence than an infrastructure property, so v1.1 states the preference explicitly:

- **Default route: AWS Bedrock in an EU region** (eu-central-1 or eu-west-1), inside the client's own AWS organisation, reached over a VPC endpoint. Here residency is a property of the infrastructure the client already owns and audits — not a promise that has to be trusted and re-verified.
- **Direct-to-provider routes** (OpenAI, Anthropic, Azure OpenAI) are permitted only where the provider offers a contractual EU processing region, zero data retention and no training on customer data, all three evidenced in the signed agreement and listed in the customer-facing assurance pack.
- **The EU allowlist is enforced twice**, not once. In code, the provider registry resolves an endpoint and raises if its region is outside the EU allowlist. In infrastructure, the AI Service's egress is restricted to the allowlisted provider endpoints — any other outbound destination is dropped at the network. The first control catches a coding mistake; the second makes exfiltration to an unapproved endpoint impossible even if the first is bypassed.

**How each claim is demonstrated rather than asserted**

| Claim | Evidence that can be produced on demand |
| --- | --- |
| Only redacted text leaves | A CI redaction-leak test: a corpus seeded with synthetic EU identifiers is pushed through the real outbound payload builder, and the build fails if any unredacted entity appears. Runs on every pull request. |
| Nothing goes to a non-EU endpoint | Network egress allowlist (VPC/NAT rules) plus the code-level region check; both are Terraform-managed and reviewable. |
| The provider does not retain or train | Signed DPA terms, quoted in the assurance pack alongside the sub-processor register; reviewed annually and on any provider change. |
| Every call is accountable | Each `ai_job` row records provider, model ID, endpoint region, prompt-template version, redaction entity counts and token counts. The AI quality dashboard and the audit export expose this per firm. |

**LangSmith is a second egress point, and v1.0 did not say so plainly.** Traces leave the account too. v1.1 states that the **EU-hosted LangSmith region** is used, that trace payloads carry the same tokenised text the provider sees (never raw text), and that LangSmith appears in the sub-processor register on the same footing as the model provider. If the EU-hosted region cannot be contracted on acceptable terms, tracing falls back to self-hosted LangSmith inside the VPC — the observability requirement does not justify a residency exception.

**A dependency this creates — Section 3's embedding model.** v1.0 names `text-embedding-3-small` (OpenAI, 1536-dim) as the initial embedding model, while Section 15 treats embeddings as personal data for residency purposes. Embeddings are also the largest-volume egress in the system, because every chunk of every WSP is embedded. Those two facts sit awkwardly together on a direct-to-OpenAI route. This is raised as open decision **D-1** in Section 6.

**Change to the architecture document**

*Section 8, current:* "Telemetry captures identifiers, latency, token counts and confidence only — raw document text, prompts and completions never leave the tenant's data plane, and LangSmith traces carry PII-redacted payloads only (15.1)."

*Section 8, v1.1:* "Two boundaries are distinguished. **Telemetry** — logs, metrics and application traces — carries identifiers, latency, token counts and confidence only; raw document text, prompts and completions never appear in it. **Inference** necessarily crosses the account boundary: a model call carries redacted chunk text, the versioned prompt template and the candidate Requirement ID list, and nothing else — no `tenant_id`, no firm identity, no user identifier, no original file bytes, no token map. Parsing and OCR run wholly in-region, so no document ever leaves the account in its original form. Routing prefers AWS Bedrock in an EU region inside the client's own account, where residency is an infrastructure property rather than a contractual promise; direct-to-provider routes require contractual EU processing, zero retention and no training. The EU allowlist is enforced both in code (the provider registry raises on a non-EU endpoint) and in infrastructure (AI Service egress is restricted to allowlisted endpoints). LangSmith is an EU-hosted sub-processor receiving the same redacted payloads, listed in the assurance pack; if EU hosting cannot be contracted, tracing moves to a self-hosted instance inside the VPC."

*Section 15.1, added:* "A continuous integration redaction-leak test drives a synthetic-PII corpus through the real outbound payload builder and fails the build if any unredacted entity reaches the wire. Each `ai_job` row records the provider, model, endpoint region, prompt version and redaction entity counts, so any past call can be reconstructed for audit."

### 1.2 Qdrant tenant separation, and where BM25 comes from

*Review sections 3, 5, 10.3, 17.8 — actual sections 3, 5, 10.4, 17.8*

**Question.** PostgreSQL has database-level tenant protection through RLS; Qdrant appears to depend on the application adding the correct filter. Can that filter be bypassed? Will there be automated cross-firm access tests? And where is BM25 actually implemented?

#### Tenant separation in Qdrant

**Disposition: Clarified, with three controls added.** The observation is exactly right and worth stating without softening: **Qdrant has no equivalent of row-level security.** PostgreSQL fails closed inside the database engine — if `app.tenant_id` is unset, firm-owned tables return nothing regardless of what the application intended. Qdrant has no such backstop. The isolation guarantee there is an application-layer guarantee, and it is weaker in kind, not merely in degree. v1.1 says so rather than implying parity.

Because the guarantee is weaker, it is defended in depth. There are three realistic ways the filter could be bypassed, and each has a specific control:

**(a) Code that talks to Qdrant directly, bypassing the repository.** All vector access goes through a single `TenantScopedVectorRepository` in the AI Service's `retrieval` module. The raw Qdrant client may not be imported anywhere else — this is enforced mechanically by an `import-linter` contract in CI, not by review discipline. A new module that imports the client directly fails the build.

**(b) A tenant identifier arriving from the wrong place.** The filter is built from the request-scoped tenant context propagated from the Core API's signed internal call, never from a parameter a caller supplies. `tenant_id` is not an accepted field on any AI Service request body or query string; a test asserts that supplying one is ignored rather than honoured. The repository raises if the tenant context is absent — the same fail-closed posture as RLS, implemented one layer up.

**(c) Direct access with the Qdrant API key.** The key lives in Secrets Manager with 90-day rotation, the Qdrant endpoint accepts connections only from the AI Service security group, and no human has standing access outside an audited break-glass procedure.

Alongside these, `tenant_id` is declared as a **tenant payload index** in Qdrant (`is_tenant: true`), which is both the vendor's documented multi-tenancy pattern and a performance win, since it groups each firm's vectors on disk.

**Automated cross-firm tests — yes, and they gate the build.** v1.0 mentions a CI isolation suite for PostgreSQL only. v1.1 extends it to cover the vector plane and both planes end to end:

- Two firms are seeded with distinct WSPs and distinct evidence.
- For **every** retrieval and search entry point, the suite issues Firm A's credentials against Firm B's document, section and collection identifiers, and asserts zero rows and zero vector hits — not an error message, zero results.
- The same is asserted for the shared regulatory collection in the reverse direction: it must be readable by both and writable by neither.
- A registry check fails the build if a retrieval entry point exists without a matching isolation test, so the suite cannot quietly fall behind the code.
- A negative test asserts that a request carrying an attacker-supplied `tenant_id` is served the caller's own tenant scope.

**A deployment question v1.0 left unanswered.** Section 2.1 calls Qdrant a "dedicated EU-resident vector store" but never says whether it is self-managed or a vendor-hosted service. Given that Section 15 treats embeddings as personal data and commits to running inside the client-owned AWS organisation, the two are not equivalent. v1.1 states that **Qdrant runs self-managed inside the client's VPC** (ECS or EC2, private subnets, no public endpoint), so vectors never leave the client's account and Qdrant does not appear in the sub-processor register at all. Qdrant Hybrid Cloud remains an alternative that preserves the same property; the fully managed cloud offering does not, and is excluded.

#### Where BM25 comes from

**Disposition: Corrected.** The review found a real error. PostgreSQL's full-text search does not implement BM25 — it ranks with `ts_rank` and `ts_rank_cd`, which are term-frequency and coverage-density measures without BM25's document-length normalisation or saturation term. The BM25 extensions that do exist for PostgreSQL are not available on Aurora. Section 3's line "PostgreSQL tsvector/GIN + BM25 re-rank" therefore describes something that cannot be built as written.

The retrieval design is sound; only the attribution was wrong. What is actually built:

1. **Candidate generation** — Qdrant returns HNSW cosine top-k; PostgreSQL `tsvector`/GIN returns keyword candidates ranked by `ts_rank_cd`. Both are constrained to the tenant scope.
2. **Fusion** — the two lists are merged by Reciprocal Rank Fusion, which uses ranks rather than scores and so needs no score calibration between the two engines.
3. **BM25 re-ranking in the AI Service** — BM25 is computed in the `retrieval` module over the fused candidate set only, using corpus statistics (document frequency, average document length) maintained per collection and refreshed incrementally as content changes. The set is 50–100 candidates, so this is a millisecond-scale in-process computation, not a search-engine workload.
4. **LLM re-ranking** of the top 10–15, which may select Requirement IDs only from that candidate set.

This keeps the commitment in Section 3 that Phase 1 introduces no Elasticsearch or OpenSearch, while describing the system honestly.

**Change to the architecture document**

*Section 3 table, current:* "Full-text search | PostgreSQL tsvector/GIN + BM25 re-rank | No Elasticsearch/OpenSearch in Phase 1"

*Section 3 table, v1.1:* "Full-text search | PostgreSQL tsvector/GIN (`ts_rank_cd`) | Keyword candidate generation; BM25 re-ranking runs in the AI Service over the fused candidate set. No Elasticsearch/OpenSearch in Phase 1"

*Sections 8 and 10.4, current:* "…fused by Reciprocal Rank Fusion and BM25 re-ranked…"

*Sections 8 and 10.4, v1.1:* "…fused by Reciprocal Rank Fusion, then BM25 re-ranked inside the AI Service's retrieval module over the fused candidate set (50–100 items), using per-collection corpus statistics maintained incrementally; PostgreSQL supplies keyword candidates via `tsvector`/GIN with `ts_rank_cd`, not BM25 scoring."

*Section 5 and 10.4, added:* "Qdrant has no database-level equivalent of row-level security, so vector isolation is an application-layer guarantee and is defended in depth: a single tenant-scoped repository is the only permitted access path (enforced by a CI import contract), the filter is built from request-scoped tenant context and never from caller input, `tenant_id` is declared as a Qdrant tenant payload index, and the endpoint is network-restricted to the AI Service. The CI isolation suite covers both planes: for every retrieval entry point it asserts that one firm's credentials return zero rows and zero vector hits against another firm's identifiers, and a registry check fails the build if an entry point has no matching isolation test. Qdrant runs self-managed inside the client's VPC on private subnets with no public endpoint."

### 1.3 Retention and deletion

*Review sections 10.2, 10.4, 15 — actual sections 10.2, 10.3, 15*

**Question.** What happens after six years, during a legal hold, when a customer leaves, and on a GDPR erasure request? And should permanently quarantined infected files have a secure, audited deletion path?

#### The retention lifecycle

**Disposition: Clarified.** v1.0 states the six-year floor but stops there, which leaves the impression that records simply accumulate forever with no defined end. v1.1 adds the full lifecycle. The governing principle is that **expiry of the retention period creates eligibility for disposal, never disposal itself** — nothing is ever deleted by a timer.

**When the clock starts.** Six years runs from the date the record reaches its terminal state — report published, finding closed, test execution closed, evidence attached to a closed test — not from creation. A finding open for two years and then closed is retained for six years from closure, so the record survives at least six years in its final form.

**At expiry.** The record transitions to `disposal_eligible` and appears in a Portal disposal queue with its firm, record type, closure date and expiry date. It remains fully readable and fully non-deletable in that state. Disposal requires all four of: the firm's written authorisation, maker-checker approval by two Portal operators, absence of any legal hold, and an audit entry recording who authorised, who approved and what was destroyed. **If nobody acts, the record is retained.** Silence never destroys data.

**Legal hold.** A hold is a flag set at firm, matter or record scope. While it is set, the record cannot leave `disposal_eligible`, cannot be anonymised by a DSAR action, and cannot be caught by any lifecycle rule anywhere in the system. Setting and clearing a hold are both maker-checker actions recorded in the audit trail, with the reason and the requesting authority captured. A hold overrides expiry indefinitely and without limit.

**When a customer leaves.** Termination runs a fixed sequence: the firm moves to `terminated` and all logins stop immediately; a complete exit bundle — evidence, reports, findings, the audit trail and structured exports — is produced and delivered within the contractual window, satisfying the exit-support commitment in Section 15 and the exit-plan expectations DORA places on ICT third-party providers; the data is then retained to the six-year floor, because the firm's own regulatory record-keeping obligation does not end when the contract does; after the floor, the records enter the ordinary disposal queue. A former customer may request earlier destruction, which is honoured only for data outside the retention obligation.

**GDPR erasure.** Personal data outside the retention obligation is anonymised through the token map (Section 15.1): rewriting a data subject's tokens removes their identity across every record at once, without touching the immutable, trigger-protected compliance rows. Personal data inside the obligation is retained under Article 17(3)(b), and the firm — as controller — makes that determination; ControlIQ, as processor, executes it and records it. The DSAR response states plainly which categories were anonymised and which were retained, with the legal basis for each.

The legal sign-off that v1.0 tracks as an open item is retained, but with a defined scope rather than an open-ended question. It must answer: which MiCA and DORA articles create the record-keeping obligation and for how long; whether staff personal data appearing incidentally inside WSP documents and evidence falls inside that obligation; and what the firm's DSAR response must say when it does. Owner and deadline are in Section 6 as **D-2**.

#### Quarantined infected files

**Disposition: Accepted.** The suggestion is adopted. "Permanently quarantined and never deleted" was written to protect evidence, but an infected file is not evidence — it never passes the malware gate, is never promoted out of the quarantine prefix, and never becomes part of any test, finding or report. Retaining live malware indefinitely is a security liability that the retention policy was never meant to create.

v1.1 defines a destruction path that is narrow and audited:

- The **tombstone is permanent**: file name, SHA-256 hash, size, scanner verdict and signature name, uploading user, firm, timestamps for upload, verdict and destruction. This is the audit record, and it is never deleted.
- The **object body** is destroyed after a 90-day dwell, which is long enough for incident investigation and for the uploader to be told what happened and re-upload a clean file.
- Destruction is **maker-checker** by two Portal operators and produces an audit entry, exactly like any other two-person action in the platform.
- The lifecycle rule that permits this applies to the `evidence-quarantine/` prefix **only**. The compliance prefixes `wsp-documents/`, `evidence/` and `reports/` keep no deletion path whatsoever, unchanged from v1.0.

**Change to the architecture document**

*Section 10.2, current:* "an asynchronous malware scan promotes clean files and permanently quarantines infected ones (they are never deleted)"

*Section 10.2, v1.1:* "an asynchronous malware scan promotes clean files and quarantines infected ones. A quarantined file never becomes evidence, so it is not covered by the retention floor: its permanent tombstone (name, SHA-256, size, scanner verdict, uploader, firm, timestamps) is retained indefinitely in the audit trail, while the object body is securely destroyed after a 90-day investigation dwell under maker-checker approval. The deletion lifecycle rule applies to the `evidence-quarantine/` prefix only; `wsp-documents/`, `evidence/` and `reports/` retain no deletion path of any kind."

*Section 10.3, added:* Retention lifecycle text as set out above — clock start at terminal state, `disposal_eligible` at expiry, four-condition disposal with retention as the default on inaction, legal hold as an unlimited override, and the termination sequence.

### 1.4 Session revocation

*Sections 2.1, 7.2*

**Question.** Section 2.1 says deactivation takes effect immediately; Section 7.2 says an access token may stay valid for up to 15 minutes. Which is correct?

**Disposition: Corrected.** Both sentences described real behaviour, but they described different things and v1.0 presented both as "the" answer. As written, **Section 7.2 was accurate and Section 2.1 was not**: refresh stopped instantly, but a bearer token already in a browser stayed cryptographically valid until it expired, so a deactivated user could continue working for up to fifteen minutes. That is the wrong behaviour for a compliance platform where deactivation is frequently a response to something that has just gone wrong, and the review is right to press on it.

v1.1 makes revocation genuinely immediate, and does it without giving up the stateless hot path that the rest of the architecture depends on.

**The mechanism.** Each application container keeps a small in-memory revocation set — session and user identifiers revoked within the last fifteen minutes. Revocation publishes to a Redis pub/sub channel; every container applies the entry on receipt. Middleware checks the set on every request, which is a local hash lookup costing well under a microsecond, so the hot path still makes no network call to Redis or the database. The set stays small by construction: an entry can be dropped once the longest-lived access token issued before it has expired, so the set only ever holds fifteen minutes of revocations.

Three failure modes are handled explicitly, because an in-memory security control that is wrong after a restart is not a security control:

- **Container start.** A new container loads the current revocation snapshot from Redis before it passes its readiness check. It never serves a request with an empty set.
- **Dropped subscription.** Each container tracks the age of its last confirmed pub/sub heartbeat. Beyond a short staleness threshold it stops trusting its local set and falls back to a per-request Redis check — slower, still correct — until the subscription is re-established.
- **Total Redis loss.** Every session is gone, so every user re-authenticates. Revocation is moot in that scenario, and the outcome fails safe.

**The resulting guarantee, stated as a measurable target:** deactivation, role change, password change, MFA re-enrolment, forced logout and refresh-token-reuse detection all take effect fleet-wide within one second at the 99th percentile. The next request the affected user makes is rejected, whatever the age of their access token.

**Change to the architecture document**

*Section 2.1, current:* "…makes revocation instant across the whole fleet — deactivating a user or forcing logout on role change takes one key deletion, with sub-millisecond in-memory session checks on every request."

*Section 2.1, v1.1:* "…makes revocation effective fleet-wide within one second: a revocation deletes the session key and publishes to a Redis pub/sub channel, and every container applies it to a small in-memory revocation set that middleware checks locally on each request, so an already-issued access token is rejected rather than left to expire."

*Section 7.2, current:* "Logout & revocation — logout, deactivation, role change, password change or MFA re-enrolment deletes the user's session keys in Redis; refresh stops instantly and the outstanding access token dies within its 15-minute window at most."

*Section 7.2, v1.1:* "Logout & revocation — logout, deactivation, role change, password change, MFA re-enrolment and refresh-token-reuse detection delete the user's session keys in Redis and publish the revocation to every application container. Each container keeps an in-memory set of identifiers revoked within the last access-token lifetime and checks it locally on every request, so an outstanding access token is rejected immediately rather than remaining usable until it expires. Propagation is under one second at p99. Containers load the current revocation snapshot from Redis before passing readiness, and fall back to a per-request Redis check if their subscription goes stale, so revocation is never weakened by a restart or a dropped connection."

### 1.5 The 85 percent AI accuracy requirement

*Sections 8, 16.2, 18.2*

**Question.** What does 85 percent accuracy mean, how large is the test dataset, who approves it, and does the evaluation re-run when retrieval, chunking or document processing changes?

**Disposition: Clarified, with the change trigger widened as the review implies.** v1.0 states the number and the gate but never defines the measurement, which makes a contractual commitment unfalsifiable. v1.1 defines it completely.

#### What is measured

The unit of measurement is a **(WSP section, Requirement ID) pair**. Against a section's expert-labelled set of correct Requirement IDs, each suggestion the system would actually surface to a reviewer — that is, after the confidence threshold is applied — is a true positive if it is in the labelled set and a false positive if it is not; a labelled requirement the system does not surface is a false negative.

The gate is **two-sided, deliberately**:

- **Precision ≥ 85%** — of the suggestions a reviewer is shown, at least 85 out of 100 are correct. This is the number the reviewer experiences and the one the contractual commitment is read as meaning.
- **Recall ≥ 70%** — of the mappings that should be found, at least 70 out of 100 are surfaced.

A precision-only gate is trivially gamed by raising the threshold until the system suggests almost nothing and is right about all of it, which would pass at 100% while being useless and, worse, would hide compliance gaps. The recall floor removes that escape. F1 is reported alongside both, and every run is broken down by language (EN/DE/FR) and by regulation (MiCA/DORA), because an aggregate that passes while German fails is not a pass.

**The reading of "85% verified accuracy" as precision-at-threshold is a contractual interpretation and needs the client's explicit confirmation** — it is registered as **D-3** in Section 6 rather than assumed.

#### The dataset

- **Size.** At least 900 labelled section–requirement pairs across at least 30 real WSP documents, split into a **development set (~300 pairs)** used for tuning and a **held-out gate set (~600 pairs)** used only for the gate. The gate set is never used for tuning; a threshold tuned on the set that judges it does not measure generalisation. Six hundred pairs put the 95% confidence interval around an 85% result at roughly ±3 percentage points, which is tight enough for the number to mean something.
- **Coverage.** Spanning EN, DE and FR; both MiCA and DORA; text-native and scanned documents; and both well-structured and poorly-structured WSPs, since the second kind is where accuracy actually degrades.
- **Labelling and approval.** Labelled by the client's compliance subject-matter expert, independently reviewed by a second qualified reviewer, with disagreements adjudicated and the adjudication recorded. **The client owns and approves the dataset**; SayOne cannot alter a label. Inter-rater agreement is measured and reported, because a gate resting on labels two experts cannot agree on is measuring the wrong thing.
- **Versioning.** The dataset is versioned in the `golden-dataset/` S3 prefix. Changes go through pull request with client sign-off, and every evaluation run records the exact dataset version it scored against.

#### When the evaluation runs

**The review's underlying point is correct and v1.0 was too narrow.** Restricting the gate to prompt, model and dataset changes leaves the biggest accuracy levers ungated — a chunking change or a parser upgrade can move accuracy further than a prompt edit. v1.1 widens the trigger to any change on the path from document to suggestion:

Docling version or parsing configuration; OCR configuration; chunking strategy or parameters; the embedding model, its dimensions or registry generation; retrieval configuration (top-k, RRF constant, BM25 parameters, re-ranker settings); prompt templates; model or provider selection; and the confidence threshold.

This is implemented as a path-based CI trigger over `ai-service/**` and the named configuration files, so it fires on the change itself rather than on someone remembering to run it. On top of that: a **full evaluation runs weekly on schedule** regardless of changes, catching provider-side model drift that no commit would reveal; and **a passing run against the current dataset version is mandatory before any UAT promotion**, whatever triggered or did not trigger.

Every run is recorded — dataset version, prompt versions, model IDs, retrieval configuration hash, per-item outcomes, aggregate metrics — and surfaced on the Portal AI quality dashboard with an exportable trend. In production, the human-override rate by confidence band is the continuing signal, alerting when it drifts from the evaluated baseline.

**If the gate cannot be met at UAT**, promotion is blocked. The remediation loop is dataset error analysis, then retrieval and prompt work, then re-evaluation. If it still cannot be met, the mapping feature ships in suggestion-only mode with no accuracy claim, by written agreement — it does not ship with the claim quietly dropped.

**Change to the architecture document**

*Section 8, added:* the definition above — unit of measurement, precision ≥85% with recall ≥70%, per-language and per-regulation breakdown, dataset size and split, client ownership of labels.

*Sections 16.2 and 18.2, current:* "whenever prompts, model configuration or the golden dataset changed"

*Sections 16.2 and 18.2, v1.1:* "whenever anything on the document-to-suggestion path changed — parsing, OCR, chunking, embedding model or generation, retrieval configuration, re-ranking, prompt templates, model or provider selection, or the confidence threshold — enforced as a path-based CI trigger rather than by convention. A full evaluation also runs weekly on schedule to catch provider-side model drift, and a passing run against the current dataset version is required before every UAT promotion regardless of trigger."

### 1.6 Redis, lost jobs and the dead-letter path

*Sections 6, 10.5, 12*

**Question.** If Redis fails while jobs are queued, how is every job recreated from the outbox? And will failed jobs have a permanent, reviewable, replayable home rather than only a log line?

#### Recovering queued work

**Disposition: Clarified, with one design change.** The outbox is the right mechanism and it is already in the architecture, but v1.0 did not state the property that makes it work: **an outbox row must not be considered done when it is dispatched.** If a row is marked processed at dispatch time and Redis is then lost, the durable record says the work happened and the work never happened. That gap is closed:

- An outbox row carries `dispatched_at` and `completed_at` separately. Dispatch sets the first; the consumer sets the second, idempotently, only after the work has actually succeeded.
- A sweeper re-dispatches any row with a `dispatched_at` older than its expected completion window and no `completed_at`. Redis loss therefore causes re-dispatch, not data loss. Delivery is at-least-once and consumers are idempotent, so re-dispatch is safe by design.
- `ai_job` rows behave the same way: the row in PostgreSQL is the source of truth, and a reaper re-enqueues jobs stuck in `queued` or `running` beyond their SLA. This is already how the UI reads status, so nothing new is exposed to users.
- Celery is configured with `task_acks_late` and `reject_on_worker_lost`, so a task killed mid-execution is redelivered rather than silently lost.

**A clarification on what "Redis is not backed up" means.** It means there is no restore procedure for Redis, not that a single node failure loses state. ElastiCache runs Multi-AZ with automatic failover and append-only persistence, so a node failure is a failover, not a loss. Only total cluster loss forces re-dispatch — and that path is exactly the one the outbox sweeper covers. v1.1 says this, because the current phrasing reads more alarming than the design actually is.

#### The dead-letter path

**Disposition: Accepted.** The suggestion is adopted in full. v1.0's "dead-letter logging" is inadequate for a platform whose value rests on being able to prove what happened: a log line is searchable at best, expires with the retention window, and cannot be acted on.

v1.1 introduces a `dead_letter_job` table in PostgreSQL holding the queue and task name, the full payload, the originating outbox event or `ai_job` identifier, the tenant, the attempt count, the first and last failure timestamps, the exception type and message, and the correlation ID. Around it:

- A **Portal dead-letter screen** lists entries filtered by queue, firm, task type and age.
- **Requeue** is available per entry and in bulk. Requeuing anything that mutates firm data is a maker-checker action, consistent with every other two-person rule in the platform.
- **Dismissal** requires a recorded reason and never deletes the row.
- A **non-zero depth raises an alarm**, and age of oldest entry is a tracked metric. Dead letters that nobody looks at are the same as dead letters that do not exist.
- Rows sit inside the audit retention floor and are non-deletable, so "we lost a notification and never noticed" cannot be an unanswerable question.

**Change to the architecture document**

*Section 6, current:* "retries use exponential backoff with a maximum of five attempts and dead-letter logging"

*Section 6, v1.1:* "Outbox rows record `dispatched_at` and `completed_at` separately: dispatch does not mark a row done, and a sweeper re-dispatches any row that has been dispatched without completing inside its expected window, so a total loss of the Redis broker causes re-dispatch rather than lost work. `ai_job` rows follow the same pattern with a reaper for jobs stuck in `queued` or `running`. Celery runs with `task_acks_late` and `reject_on_worker_lost`. Retries use exponential backoff to a maximum of five attempts, after which the task lands in the durable `dead_letter_job` table with its payload, error, attempt count and correlation ID — reviewable and replayable from the Portal, requeue under maker-checker where firm data is mutated, dismissal only with a recorded reason, non-zero depth alarmed, and rows retained inside the audit retention floor."

*Section 10.5, current:* "Redis is deliberately not backed up: it holds sessions, cache and queue state only, so losing it forces re-login and job re-dispatch, never data loss."

*Section 10.5, v1.1:* "Redis has no restore procedure, which is not the same as having no resilience: ElastiCache runs Multi-AZ with automatic failover and append-only persistence, so a node failure is a failover rather than a loss. Only a total cluster loss forces re-login and job re-dispatch — and re-dispatch is driven by the transactional outbox and `ai_job` sweepers (Section 6), which hold the durable record in PostgreSQL. No committed work is lost in either case."

## 2. Important but next in line

### 2.1 Publishing regulatory updates

*Sections 6, 9*

**Question.** Should regulatory publication require maker-checker approval? And does the prohibition on HTML scraping mean interpretation rather than retrieval?

#### Maker-checker on publication

**Disposition: Accepted.** The gap is real. Section 6 lists every two-person rule in the product and they are all firm-side; Section 9 requires only "the operator's confirmation" to publish. A published regulatory update propagates to every firm at once — it notifies them, re-opens WSP review obligations and feeds the news panel. It is the single highest-blast-radius action in the platform, and it was the one action with no second pair of eyes. That is the wrong way round.

v1.1 routes regulatory publication through the **same shared maker-checker service** that already backs mapping confirmation and finding closure, so this is a new caller rather than new machinery:

- The preparer — who imported, edited or tagged the draft — is excluded from approving it.
- The approval is recorded in the common approval table with both actors, timestamps and a diff of what was published.
- The same gate applies to **Requirement ID retirement** and **test-library publication**, which have the same cross-firm reach and the same missing control.
- **Break-glass**: a single operator may publish an urgent regulatory change alone. The action is flagged, alarmed, and requires retrospective approval within 24 hours; the Portal shows it as unapproved until that happens. Emergencies are real, but they leave a mark.

This creates a staffing constraint that v1.1 states explicitly: **at least two Platform Super Admin accounts are required**, mirroring the existing "at least two Firm Super Admins per firm" rule in Section 7.1. A two-person rule with one person is not a control.

#### HTML

**Disposition: Accepted — the review's reading is the correct one.** The intent was always to prohibit *deriving regulatory content* from HTML, never to prohibit an HTTP GET. v1.0's phrasing says the second and means the first, which is why it appears to contradict the content-hash monitoring described two lines later.

The distinction that matters: parsing regulatory text, article structure or Requirement IDs out of a page's markup is prohibited, because HTML layout is unversioned, changes without notice and produces silent, invisible errors in regulatory content. Fetching the page, normalising it and hashing it for change detection is not prohibited — it is the designed fallback, and it produces a Portal task for manual structured entry rather than any automated content extraction.

**Change to the architecture document**

*Section 9, current:* "HTML scraping is prohibited; where a source is HTML-only, change detection falls back to content-hash monitoring plus manual structured entry in the Portal. Automated fetch lands regulation changes in a draft queue, where Portal associates review, edit and tag them; publication requires the operator's confirmation."

*Section 9, v1.1:* "No regulatory content is ever derived from HTML: regulatory text, article structure and Requirement IDs are taken only from official machine-readable channels. Retrieving an HTML page is permitted and expected for change detection — where a source is HTML-only, the page is fetched, normalised and content-hashed on a schedule that respects the publisher's rate limits and terms, and a hash change raises a Portal task for manual structured entry. No text, structure or identifier is ever parsed out of markup. Automated fetch lands regulation changes in a draft queue, where Portal associates review, edit and tag them. Publication is a maker-checker action through the shared dual-control service: the preparer is excluded from approving, and both actors, timestamps and the published diff are recorded in the common approval table. The same gate governs Requirement ID retirement and test-library publication. An urgent single-operator publication is available as an alarmed break-glass path requiring retrospective approval within 24 hours."

*Section 6, updated list:* "Every two-person rule in the product — WSP mapping confirmation and reversal, finding closure, sampling changes, deadline extensions, regulatory publication, Requirement ID retirement, test-library publication, dead-letter requeue of firm-mutating tasks, quarantine destruction, legal-hold set and clear, and record disposal — is backed by one shared, parameterised maker-checker service."

*Section 7.1, added:* "Platform Super Admin — at least two required, so Portal dual-control gates always have an eligible approver."

### 2.2 Disaster recovery

*Sections 10.5, 16.3, 18.3*

**Question.** Have the RPO and RTO targets been tested across every store? If Qdrant needs rebuilding and Redis is lost, can the platform be restored within one hour? And is 99.5% availability acceptable?

**Disposition: Corrected on the targets, Open on availability.**

**Have they been tested? No — and they cannot have been.** The system is not yet built. v1.0 presents RPO ~5 minutes and RTO ~1 hour as properties of the platform, which they are not: they are design targets. v1.1 labels them as such and attaches the validation commitment — a **documented DR test is a go-live acceptance criterion**, producing a report of measured RPO and RTO per store, and no production promotion happens without it.

**The targets as stated do not hold for a region loss, and this is the most substantive correction in this section.** Aurora cross-region *snapshot replication* is not continuous. In-region, point-in-time recovery genuinely gives ~5 minutes. Across regions, with only replicated snapshots, the recovery point is the age of the last replicated snapshot — hours, not minutes. v1.0's single pair of numbers covers the in-region case and quietly overstates the cross-region one. v1.1 states two tiers:

| Scenario | RPO | RTO | Mechanism |
| --- | --- | --- | --- |
| In-region failure (AZ loss, instance failure, data corruption) | ~5 min | ~1 hour | Aurora Multi-AZ with sub-30-second failover; PITR at 5-minute granularity; ECS across AZs |
| Full region loss | ≤ 4 hours | ≤ 4 hours (interactive plane) | Cross-region snapshot copy to eu-central-1; S3 CRR with Replication Time Control; warm standby |

Cross-region RPO improves to seconds with **Aurora Global Database**, which replicates continuously rather than by snapshot. It carries a standing cost for a second-region cluster. It is registered as **D-4** in Section 6 for the client to decide, with a recommendation to defer it past MVP unless a customer contract requires a sub-hour cross-region recovery point — a full region loss in an AWS EU region is a rare event, and the MVP customer base is small.

S3 cross-region replication is asynchronous, so the compliance prefixes get **Replication Time Control**, which brings a contractual 15-minute replication SLA and the metrics to prove it, rather than best-effort.

**Can everything come back within an hour with Qdrant rebuilt and Redis lost? No — and the honest answer changes the shape of the objective rather than the number.** v1.1 separates RTO by plane, which is consistent with the design principle already stated in Sections 2.1 and 4.2 that an AI outage degrades AI features only:

- **Interactive plane** — authentication, tests, evidence, findings, remediation, reports, dashboards, audit. Target ≤1 hour. Redis loss costs a re-login and a re-dispatch, both of which are fast. This is the tier that matters for a firm's ability to work.
- **AI plane** — mapping suggestions, gap analysis, retrieval. Target ≤4 hours. The fast path is restoring the nightly Qdrant snapshot from S3; full re-embedding from PostgreSQL is the fallback and is bounded by corpus size and provider throughput, both measured during the DR test. During this window the platform is fully usable without AI: every AI output is advisory and human-confirmed by design (Section 8), so no compliance workflow is blocked.

**A gap the DR analysis exposed that nothing in v1.0 covers: KMS keys.** Section 15 gives each firm a customer master key. A single-region CMK cannot be used in the standby region — which means that with the design as written, the warm standby would hold replicated data it could not decrypt, and the DR plan would fail at the point of use. v1.1 specifies **multi-Region KMS keys** for the tenant CMKs, with the annual drill explicitly exercising decryption in the standby region. This is a correction, not an enhancement.

**Reconciling the two drill statements.** Section 10.5 promises an annual restore drill; Section 18.5 requires a restore tested within the last 30 days before production promotion. These are compatible but were never related to each other. v1.1 states both explicitly: **monthly automated restore verification** of Aurora and S3 into a scratch environment (satisfying the 30-day rule), and an **annual full region-failover drill** including tenant-key decryption in the standby region.

**Availability — Open.** 99.5% permits 3 hours 39 minutes of downtime per month; 99.9% permits 43 minutes. The architecture as designed — Aurora Multi-AZ, ECS across AZs, no single-AZ dependency in the interactive path — is capable of 99.9% for the interactive plane; the constraint on committing to it is single-region scope and planned maintenance, not the design.

Recommendation: **design to 99.9% for the interactive plane, commit contractually to 99.5% in year one, and publish measured monthly availability** so the committed number can be raised on evidence rather than optimism. Compliance work is periodic rather than real-time, so 99.5% is defensible on its merits. The more important point is regulatory: DORA requires ICT third-party contracts to specify service levels, so what matters most is that the number is precise, measurable and reported — a well-evidenced 99.5% is worth more in a customer's DORA assessment than an unmeasured 99.9%. Whether the customer base needs the higher figure is a commercial judgement, registered as **D-5**.

**Change to the architecture document**

*Section 16.3, current:* "Disaster recovery targets RPO ~5 minutes and RTO ~1 hour… The availability target is 99.5%."

*Section 16.3, v1.1:* "Disaster recovery targets are design targets pending validation; a documented DR test producing measured per-store RPO and RTO is a go-live acceptance criterion. Two scenarios are distinguished. In-region failure: RPO ~5 minutes and RTO ~1 hour, on Aurora Multi-AZ failover and 5-minute point-in-time recovery. Full region loss: RPO and RTO of ≤4 hours, on cross-region snapshot copy to eu-central-1 and S3 cross-region replication with Replication Time Control; Aurora Global Database would reduce the cross-region recovery point to seconds and is held as a post-MVP option. RTO is stated per plane: the interactive platform is restored within 1 hour, while the AI plane targets 4 hours, since a Qdrant collection is restored from its nightly snapshot or, in the worst case, re-derived from PostgreSQL. The platform remains fully usable while the AI plane is down, because every AI output is advisory and human-confirmed. Tenant customer master keys are multi-Region KMS keys so the standby region can decrypt replicated data. Restore verification runs monthly into a scratch environment; a full region-failover drill including standby-region tenant-key decryption runs annually. The availability target is 99.5% for year one, against an architecture designed to 99.9% for the interactive plane, with measured monthly availability published."

### 2.3 Notifications

*Sections 2.1, 12*

**Question.** How are duplicates prevented, how are bounces and permanent failures handled, will sensitive compliance information be excluded from email, and what evidence shows the intended person was notified?

**Disposition: Clarified, with the email content rule accepted as proposed.**

**Duplicates.** Delivery is at-least-once, so duplicate suppression is a property of the delivery record rather than of the queue. Every `notification_delivery` row carries a unique constraint on `(event_id, rule_id, recipient_id, channel)`. A retry or a re-dispatched task that reaches the send step a second time hits the constraint and becomes a no-op — at-least-once delivery plus a uniqueness key yields exactly-once from the user's point of view. Non-mandatory notifications additionally coalesce within a short window, so ten evidence uploads produce one message; mandatory notifications never coalesce and never digest, as Section 12 already requires.

**Bounces and permanent failures.** The email provider's event stream (SES event destinations via SNS, in the default configuration) is consumed and written onto the delivery record, so its lifecycle is `queued → sent → provider-accepted → delivered | bounced | complained`, with the provider message ID retained. Then:

- A **hard bounce** marks the address undeliverable and suppresses further sends to it. This is not the end of the story: the notification is escalated to the in-app channel and a task is raised for the Firm Super Admin to correct the address. A wrong email address must not become a silent hole in a firm's compliance notifications.
- A **soft bounce** retries with backoff before being treated as hard.
- A **complaint** unsubscribes the address from non-mandatory notifications only. Mandatory notifications escalate to in-app and to the Firm Super Admin instead — a compliance obligation is not opt-out-able, but nor is it delivered to someone who has marked it as spam.
- The provider suppression list is respected, and its state is visible in the Portal rather than being an invisible reason messages stop arriving.

**Sensitive content in email — accepted, and stated as a hard rule.** Email is the least controlled channel in the system: it lands in mailboxes the platform does not govern, forwards freely and is retained outside the audit trail. v1.1 therefore fixes the email payload to: the notification category, the firm name, the entity type, the due date or deadline where one applies, and an authenticated deep link. **Never** the finding text, evidence content or file names, sample data, document text, requirement detail, or any personal data beyond the recipient's own name. The substance lives behind authentication, always. A per-firm setting reduces this further to a link-only message for firms that want no compliance signal in email at all.

**Evidence that someone was notified — stated precisely, including its limits.** The `notification_delivery` row records the recipient, channel, template and its version, rendered subject, provider message ID, and timestamps for each lifecycle stage; in-app notifications additionally record a read receipt. All of it lands in the audit trail and is included in the audit export.

The limit needs saying plainly, because a compliance platform should not overclaim what its records prove: **provider confirmation proves delivery to a mail server, not that a person read it.** No email system can prove the latter. Where a workflow genuinely depends on a person having received something — remediation owner acknowledgement, records requests, sign-off requests — the authoritative evidence is the **in-app acknowledgement action**, which is a deliberate act by an authenticated user recorded in the audit trail. Email is the prompt; the in-app acknowledgement is the proof. v1.1 says this explicitly so that no one builds a regulatory argument on a delivery receipt that cannot bear the weight.

**Change to the architecture document**

*Section 12, added:* "Duplicate suppression is enforced by a unique constraint on `(event_id, rule_id, recipient_id, channel)` in the delivery record, so at-least-once dispatch yields exactly-once delivery from the recipient's point of view. Provider delivery events are consumed onto the delivery record: a hard bounce marks the address undeliverable, suppresses further email, escalates the notification in-app and raises a Firm Super Admin task to correct the address; a soft bounce retries with backoff; a complaint unsubscribes non-mandatory email only, with mandatory notifications escalating in-app instead. Email content is restricted by rule to the notification category, firm name, entity type, deadline and an authenticated deep link — never finding text, evidence content or file names, sample data, document text or requirement detail — with a per-firm link-only option. Delivery records carry recipient, channel, template version, rendered subject, provider message ID and per-stage timestamps, plus in-app read receipts, all in the audit trail and the audit export. Provider confirmation evidences delivery to a mail server, not human receipt; where a workflow depends on a person having been reached, the authoritative record is the in-app acknowledgement action by the authenticated user."

### 2.4 Deployment process

*Sections 4.2, 16.2, 18.1–18.3*

**Question.** Trunk-based with one long-lived branch, or separate Staging, UAT and Production branches? And is the tested image promoted, or rebuilt per environment?

**Disposition: Clarified on branching, Corrected on environment naming.**

**Branching: trunk-based, unambiguously.** `main` is the only long-lived branch in every repository. There are no Staging, UAT or Production branches and none will be created. The reference the review found comes from Section 18's opening, which names the Deployment Cycle Guide v1.5's `develop`/`uat`/`main` model in order to record ControlIQ's documented deviation from it. That is a description of what the guide says, not of what ControlIQ does — but it is the second thing a reader meets in Section 18, before the deviation is explained, so the confusion is the document's fault. v1.1 reorders it: the branching model is stated first, then the deviation is recorded against it.

**Environments are image tags, not branches.** Promotion moves an artifact through environments. Nothing is ever merged between branches to deploy.

**Image promotion: confirmed, and made verifiable.** The image is built exactly once, on merge to `main`, and tagged with the commit SHA. Promotion re-tags **the same manifest digest** — `uat`, then a version tag and `prod` — rather than rebuilding. Concretely: ECR tag immutability is enabled so a tag cannot be silently repointed; each deployment references the image by `sha256` digest rather than by a moving tag; and the deployment record stores that digest, so "exactly which artifact is in production" has a single exact answer at any moment. A rebuild between environments is not merely discouraged — the pipeline has no step that could perform one.

**A naming inconsistency the review's question surfaced.** Section 16.2 lists three environments as Staging → UAT → Production. Section 18.2 says merge to `main` auto-deploys to **Dev**. Section 18.4's Terraform layout is `environments/{dev,uat,prod}/`. Section 16.1's account list says staging. These are the same environment under two names. v1.1 standardises on **Staging** everywhere: three environments (Staging → UAT → Production), auto-deploy to Staging on merge to `main`, Terraform layout `environments/{staging,uat,prod}/`, AWS accounts named to match.

**Change to the architecture document**

*Section 18 opening, v1.1:* "ControlIQ uses trunk-based development: `main` is the single long-lived branch in every repository, and environments are reached by promoting a built image, never by merging between branches. There are no environment branches. This is one deliberate, documented deviation from the Deployment Cycle Guide & Checklist v1.5, whose `develop`/`uat`/`main` model ControlIQ does not follow; the pipeline follows the guide in every other respect, and any further deviation requires the guide's exception process — email approval from the Head of Engineering and the DevOps team. Silent skips are not permitted."

*Section 18.2, v1.1:* "The image auto-deploys to **Staging**, smoke tests run, and the team channel is notified." — with `Dev` replaced by `Staging` throughout, and 18.4's layout corrected to `environments/{staging,uat,prod}/`.

*Section 18.3, added:* "ECR tag immutability is enabled; deployments reference images by `sha256` digest rather than by tag; and each deployment record stores the deployed digest, so the artifact running in any environment is identified exactly. Promotion re-tags an existing manifest and the pipeline contains no step capable of rebuilding an image between environments."

## 3. Lowest priority and wording

### 3.1 Confidence scores and citations

*Section 8*

**Question.** How was the 0.4 threshold selected, will it be tuned on real results, and should "eliminates hallucinated citations" be softened to "reduces" or "limits"?

#### The 0.4 threshold

**Disposition: Clarified.** The honest answer is that **0.4 is a provisional placeholder, not a calibrated value**, and v1.0 should have said so. It was chosen for its direction rather than its precision: deliberately permissive, because at MVP the cost of a missed mapping — an undetected compliance gap — is materially higher than the cost of a rejected suggestion, which costs a reviewer a few seconds. When in doubt, show it and let a human decide.

It will be calibrated, by a defined method rather than by impression:

- During golden-dataset evaluation the threshold is **swept across its range** and the operating point chosen is the one maximising recall subject to precision ≥85% — the same two-sided criterion as the accuracy gate, so the threshold and the gate cannot drift apart.
- The sweep is run **per language and per document type**, because these do not share an optimum, and separate thresholds are configured where the difference is material.
- The value is a **configuration entry**, not a constant: `config.get('ai.mapping.confidence_threshold', tenant_id)`, versioned and changeable without a deploy, and — per Section 1.5 above — a change to it re-triggers the accuracy gate.
- It is **re-derived after UAT** on real firm documents and at every model change, and monitored continuously in production through the human-override rate by confidence band. A band being overridden far more often than its confidence implies is the signal to move the threshold.

One presentational consequence, which v1.1 states so the UI does not overclaim: the score is a raw retrieval-and-model score, not a calibrated probability. Until calibration data exists, a 0.4 does not mean "40% likely to be correct". The review queue therefore shows **confidence bands (low / medium / high)** rather than a bare number, so reviewers are not invited to read a precision the score does not have.

#### "Eliminates"

**Disposition: Accepted.** The review's distinction is exactly right, and the correction matters more than a word change suggests, because the two failure modes have different fixes.

What the constrained-candidate design does eliminate: **fabricated** Requirement IDs. The model may only return identifiers present in the retrieved candidate set, so it cannot invent `REQ-MICA-999`. That is a genuine structural guarantee, not a probabilistic one.

What it does not eliminate: **incorrect** Requirement IDs. The model can still select the wrong ID from a set of real ones — a mis-citation rather than an invented one. No architectural constraint prevents that; it is a model-quality problem, which is precisely what the ≥85% accuracy gate, the mandatory human confirmation and the production override rate exist to measure and contain.

v1.0 collapsed the two and claimed the stronger guarantee for both. v1.1 separates them.

**Change to the architecture document**

*Section 8, current:* "…an LLM re-ranks only the top 10–15 candidates and may select Requirement IDs solely from that candidate set, eliminating hallucinated citations by construction."

*Section 8, v1.1:* "…an LLM re-ranks only the top 10–15 candidates and may select Requirement IDs solely from that candidate set. This eliminates *fabricated* citations by construction — the model cannot return a Requirement ID that does not exist — but it does not eliminate *incorrect* ones: the model can still select the wrong Requirement ID from a set of real candidates. Mis-selection is contained by the mandatory human confirmation of every suggestion, measured by the ≥85% accuracy gate, and monitored in production through the human-override rate."

*Section 8, added:* "The initial confidence threshold of 0.4 is a deliberately permissive provisional value, set on the principle that a missed mapping costs more than a rejected suggestion. It is calibrated during golden-dataset evaluation by sweeping the threshold and selecting the operating point that maximises recall subject to precision ≥85%, run per language and per document type, re-derived after UAT and at every model change, and monitored in production through the override rate by confidence band. The score is a raw retrieval-and-model score rather than a calibrated probability, so the review queue presents confidence as low/medium/high bands rather than as a bare number."

### 3.2 Encryption and software security

*Sections 15, 15.1, 18.2–18.3*

**Question.** Is TLS 1.3 supported and enforced on every connection, including internal services, database connections and third-party callbacks? And does annual KMS rotation re-encrypt existing firm data keys, or only apply to new encryption?

#### TLS

**Disposition: Corrected.** "TLS 1.3 is used everywhere including intra-VPC" is not achievable as an absolute, and claiming it is worse than stating the truth — an unmeetable claim in a security section is the kind of thing that fails an audit precisely because it was written to sound reassuring. Two hops in the architecture cannot offer TLS 1.3 today.

The accurate position: **TLS 1.3 is negotiated on every connection where both ends support it, and TLS 1.2 is the enforced hard floor everywhere. Anything below TLS 1.2 is refused, without exception.** Per hop:

| Connection | Position |
| --- | --- |
| Browser → ALB | TLS 1.3 negotiated by all supported browsers; ALB policy sets TLS 1.2 as the floor |
| ALB → Caddy, Caddy → application | TLS 1.3 |
| Application → Aurora PostgreSQL | TLS 1.3, with the minimum protocol version pinned in the cluster parameter group |
| Application → ElastiCache Redis | **TLS 1.2** — in-transit encryption on ElastiCache does not currently offer 1.3. Re-checked at build time and raised if the engine version in use supports it |
| Application → S3, KMS, Secrets Manager | TLS 1.3 where the endpoint offers it, TLS 1.2 floor, over PrivateLink so traffic stays inside the VPC |
| AI Service → model providers | TLS 1.3 where offered, TLS 1.2 floor |
| Inbound third-party webhooks (payments) | **TLS 1.2 floor.** The caller chooses the version; the platform can enforce a floor and reject anything below it, but cannot compel 1.3 |

**How this is confirmed rather than asserted** — this is the part that answers the review's actual question. A **TLS conformance check** runs against every environment and enumerates each endpoint with its negotiated protocol version and cipher, producing a report. Any endpoint negotiating below the declared floor fails the check. It runs before every production promotion and on a schedule, so the claim is evidence rather than intent, and a regression is caught by the pipeline rather than by an auditor.

#### KMS rotation

**Disposition: Clarified.** The direct answer: **automatic annual rotation applies to new encryption only.** AWS KMS rotation creates new backing key material for the customer master key and uses it for subsequent operations; existing ciphertext is not rewritten, and remains decryptable because the previous material is retained. The key identifier does not change, so nothing in the application is aware of it. v1.0's "rotated annually" is true but reads as though existing data is re-encrypted, which it is not.

What v1.1 states, in three parts:

- **Automatic CMK rotation, annually** — new material for new encryption. Zero operational impact, no re-encryption.
- **Data-key re-wrap** — a scheduled job re-wraps existing per-firm data keys under the current CMK material. This is cheap, since it touches key material rather than data, and it bounds how old any wrapping key in active use can be.
- **Full re-encryption** — the data itself is re-encrypted under fresh data keys only on a key-compromise event or a firm-requested re-key, run as a background job with progress tracking. Doing this annually as routine would be significant cost and risk for no material security gain.

The existing constraint is unchanged and worth restating: key destruction is blocked while records sit inside the retention window, and crypto-shredding is deliberately not adopted as a deletion mechanism.

**Change to the architecture document**

*Section 15, current:* "TLS 1.3 is used everywhere including intra-VPC, data is AES-256 encrypted at rest, and KMS envelope encryption gives each firm one customer master key wrapping per-firm data keys, rotated annually."

*Section 15, v1.1:* "TLS 1.3 is negotiated on every connection where both endpoints support it, and TLS 1.2 is the enforced floor everywhere — anything below it is refused. Two hops sit at the floor rather than at 1.3: ElastiCache in-transit encryption, which does not currently offer 1.3, and inbound third-party webhooks, where the caller selects the version and the platform can only enforce a minimum. A TLS conformance check enumerates every endpoint's negotiated version and cipher before each production promotion and on a schedule, so the position is evidenced rather than asserted. Data is AES-256 encrypted at rest, and KMS envelope encryption gives each firm one customer master key — a multi-Region key, so the disaster-recovery standby region can decrypt — wrapping per-firm data keys. Automatic annual CMK rotation applies to new encryption only: existing ciphertext is not rewritten and stays decryptable under retained material. A scheduled re-wrap additionally re-encrypts existing data keys under current material, while full re-encryption of the underlying data is reserved for a key-compromise event or a firm-requested re-key. Key destruction remains blocked while records are inside the retention window; crypto-shredding is deliberately not adopted."

## 4. Further inconsistencies found while answering

These were not raised in the review. They were found while checking that each answer above stays consistent with the rest of the document, and they are corrected on the same terms — leaving them in place would mean v1.1 fixes what was noticed and preserves what was not.

**4.1 Test coverage thresholds contradict each other.** Section 17.3 states "coverage will initially target 80%". Section 18.2 states "minimum 70% on changed code, 60% overall". Both are described as the standard, and they are different numbers.

*Resolution:* the CI gate is **70% on changed code and 60% overall** — this is what blocks a merge. **80% overall is the maturity target** for the end of the MVP build, at which point the gate is raised to match. Section 17.3 is reworded to say this, so the enforced number and the aspiration are no longer competing for the same role.

**4.2 The environment named both "Dev" and "Staging".** Covered in item 2.4: standardised on **Staging** across Sections 16.1, 16.2, 18.2 and 18.4.

**4.3 The two restore commitments were never related to each other.** Section 10.5 promises an annual restore drill; Section 18.5 requires a restore tested within the last 30 days before production promotion. Both stand, but they cover different things and neither said so. Resolved in item 2.2: monthly automated restore verification, annual full region-failover drill.

**4.4 Section 2.1 and Section 10.2 both say object storage has "no deletion path".** With the quarantine destruction path adopted in item 1.3, both need the same qualification — the compliance prefixes have no deletion path; `evidence-quarantine/` has a narrow, audited, dual-control one. Both sections are updated identically so they cannot drift.

**4.5 Qdrant's deployment mode was never stated.** Covered in item 1.2: self-managed inside the client's VPC, which is what Section 15's residency commitment already implies but never says.

**4.6 The embedding model choice sits uneasily with the residency position.** Covered in item 1.1 and registered as open decision **D-1**.

## 5. Consolidated change list for v1.1

| # | Section | Change | Origin |
| --- | --- | --- | --- |
| 1 | 8, 15.1 | Separate the telemetry boundary from the inference boundary; state exactly what crosses; prefer Bedrock in-region; enforce the EU allowlist in code and in network egress; name LangSmith EU as a sub-processor; add the CI redaction-leak test | 1.1 |
| 2 | 3, 8, 10.4 | Correct BM25 attribution: PostgreSQL supplies `ts_rank_cd` keyword candidates, BM25 re-ranking runs in the AI Service over the fused set | 1.2 |
| 3 | 5, 10.4, 17.8 | State that Qdrant has no RLS equivalent; add the tenant-scoped repository with a CI import contract, the tenant payload index, and cross-plane isolation tests with a registry check; state self-managed in-VPC deployment | 1.2 |
| 4 | 10.2 | Quarantine destruction after a 90-day dwell under maker-checker, permanent tombstone, lifecycle rule scoped to `evidence-quarantine/` only | 1.3 |
| 5 | 10.3 | Full retention lifecycle: clock start, `disposal_eligible`, four-condition disposal with retention as the default, legal hold as an unlimited override, termination sequence, DSAR treatment | 1.3 |
| 6 | 2.1, 7.2 | Immediate revocation via pub/sub-propagated in-memory deny-list; p99 under one second; cold-start and stale-subscription fallbacks | 1.4 |
| 7 | 8, 16.2, 18.2 | Define the accuracy metric (precision ≥85% with recall ≥70%), the dataset size, split, ownership and versioning; widen the gate trigger to the whole document-to-suggestion path; add the weekly scheduled run | 1.5 |
| 8 | 6, 10.5 | Separate `dispatched_at` from `completed_at` with a re-dispatch sweeper; add the durable `dead_letter_job` table and its Portal screen; clarify what "Redis is not backed up" means | 1.6 |
| 9 | 6, 7.1, 9 | Maker-checker on regulatory publication, Requirement ID retirement and test-library publication; alarmed break-glass with 24-hour retrospective approval; at least two Platform Super Admins; reword the HTML prohibition as interpretation, not retrieval | 2.1 |
| 10 | 15, 16.3, 18.3 | Two-tier DR objectives; RTO per plane; multi-Region KMS keys; S3 Replication Time Control; DR test as a go-live criterion; monthly restore verification plus annual failover drill | 2.2 |
| 11 | 12 | Duplicate-suppression key; bounce, complaint and suppression handling with in-app escalation; the email content rule; delivery evidence and its stated limits | 2.3 |
| 12 | 18, 18.2, 18.3, 18.4 | Lead with the trunk-based model; rename Dev to Staging throughout; ECR tag immutability, digest-pinned deploys and recorded deployed digests | 2.4 |
| 13 | 8 | "Eliminates fabricated citations, not incorrect ones"; confidence-threshold calibration method; confidence shown as bands | 3.1 |
| 14 | 15 | Accurate TLS position with the two documented floor exceptions; the TLS conformance check; KMS rotation semantics and the re-wrap job | 3.2 |
| 15 | 17.3 | Reconcile coverage: 70/60 as the enforced gate, 80% as the maturity target | 4.1 |

## 6. Open decisions

Each of these needs a client decision. Each has a recommendation, so none of them blocks progress by default — but each has a point beyond which the decision becomes expensive to change.

| ID | Decision and options | Recommendation | Owner / needed by |
| --- | --- | --- | --- |
| **D-1** | **Embedding and completion model route**, given that embeddings are treated as personal data. (a) OpenAI direct, under a contractual EU residency and zero-retention agreement, keeping `text-embedding-3-small` at 1536 dimensions; (b) AWS Bedrock in an EU region, with a Bedrock-hosted multilingual embedding model and a Bedrock-hosted completion model | **(b) for embeddings at minimum.** Embeddings are the largest-volume egress in the system and are treated as personal data; Bedrock makes residency an infrastructure property of an account the client already owns rather than a contractual promise. The embedding-model registry already makes the choice swappable, and model availability in the chosen EU region is confirmed at build time | Client + SayOne<br>Before AI Service build starts |
| **D-2** | **Legal position on the six-year retention floor versus GDPR Article 17.** An opinion covering which MiCA and DORA articles create the obligation and for how long; whether staff personal data appearing incidentally inside WSPs and evidence falls inside it; and what the DSAR response must state | Commission the opinion with that scope. The architecture supports either outcome — the anonymise-not-delete mechanism and the disposal queue work whichever way the boundary falls | Client legal<br>Before UAT |
| **D-3** | **The definition of "85% verified accuracy"** — precision at the surfaced threshold with a recall floor of 70%, as proposed in item 1.5, or a different definition | Confirm as proposed. The commitment is contractual, so the definition should be explicit and agreed now rather than inferred later from a disputed measurement | Client<br>Before golden-dataset labelling begins |
| **D-4** | **Cross-region replication method.** (a) Snapshot-based cross-region copy: RPO ≤4 hours, no standing cost; (b) Aurora Global Database: RPO in seconds, standing cost for a second-region cluster | **(a) for MVP**, unless a customer contract requires a sub-hour cross-region recovery point. A full EU-region loss is rare and the MVP customer base is small; (b) remains available later without redesign | Client<br>Before production infrastructure is provisioned |
| **D-5** | **Contractual availability target.** (a) 99.5% — 3h39m of downtime per month; (b) 99.9% — 43m per month | **Commit to 99.5% in year one against an architecture designed to 99.9% for the interactive plane, and publish measured monthly availability.** DORA requires ICT contracts to specify service levels, so a precise, measured and reported figure carries more weight in a customer's assessment than a higher unmeasured one. Raise the commitment on evidence | Client commercial<br>Before the first customer contract |

## 7. Closing note

Twelve items were raised. Five were genuine contradictions or overstated claims in v1.0 — what leaves the account on a model call, where BM25 comes from, whether session revocation is immediate, whether the DR targets hold across regions, and whether TLS 1.3 is truly everywhere. Each is corrected above rather than explained away. Four proposed controls or wording changes — maker-checker on regulatory publication, a durable dead-letter path, secure destruction of quarantined malware, and the "eliminates" wording — and all four are adopted as proposed. The remainder were places where the architecture was right but the document was silent, and those are now specified.

Six further inconsistencies surfaced while checking the answers against the rest of the document, and they are corrected on the same terms.

The recurring theme in the review is worth naming, because it shaped how these answers were written: the questions consistently ask not what the system does but how it can be *shown* to do it. That is the right question for a platform whose customers are themselves regulated. Wherever an answer above makes a claim, it names the artefact that evidences it — a CI test that fails the build, a conformance report, an audit record, a measured drill. Claims that could not be evidenced were changed rather than defended.

Subject to the five open decisions in Section 6, these responses are ready to be folded into **System Architecture v1.1**.
