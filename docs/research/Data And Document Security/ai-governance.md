# AI Governance: Development Tooling and the WSP Mapping Feature

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

## What the AI feature actually is

**The PRD contains exactly one AI feature: AI-assisted mapping of a firm's Written Supervisory Procedures (WSP) to regulatory Requirement IDs (the PRD's AI-assisted rule mapping section).**

| PRD ref | Statement |
|---|---|
| Single WSP upload requirement | The firm uploads its entire compliance manual as one document — `.docx`, PDF, or scanned PDF read via OCR |
| Advisory AI mapping requirement | "The AI suggestions are a starting point only — not a final determination. A compliance officer reviews each suggestion and either confirms it or adjusts it. The AI makes the process faster; the human makes the final call." |
| The PRD's WSP mapping accuracy commitment (accepted 3 Jul 2026) | "minimum verified accuracy rate of **85%** against pre-defined verification text vectors during UAT". Prompt engineering, vector database indexing and algorithmic tuning to hit and maintain that bar are inside the fixed-fee scope |
| Two-person mapping approval requirement | Before any rule mapping is confirmed or changed, **two senior people must independently approve it**; the policy author cannot be one of them |
| Mapping reversal requirement | Reversal of a confirmed mapping requires the same two-person approval; the reversal, both approvers and the date are permanently recorded |
| The PRD's mapping sign-off rules (Sosinna's answer on the mapping override gap) | Mapping re-runs automatically on upload of a new, correctly labelled WSP version. Manual override is allowed but **must carry a visible tag** flagging it as a human override rather than an AI or system mapping |
| Permanent WSP version history requirement | Every WSP version and every mapping change is kept permanently with full version history; nothing is overwritten |

**What the AI feature is not.** The platform does not make compliance assessments, does not decide Pass/Fail/Observation outcomes (a Lead Tester records those — the PRD's testing workflow step 7), does not produce regulator-ready conclusions, and does not generate findings or remediation plans. Report generation (the report contents requirement) is a templated assembly of human-entered content. Regulatory change monitoring (the regulatory monitoring requirement) is RSS-feed and official-API based with mandatory human review — explicitly **not** scraping and not an AI feature. Any statement elsewhere in this research set implying broader AI scope has been corrected.

## The two AI surfaces

| Surface | What it is | Primary risk |
|---|---|---|
| **AI-in-development** | Coding assistants used by engineers to build the platform | Source code and, if uncontrolled, customer data leaving the environment; unvetted code entering production |
| **AI-in-product** | The inference path behind the advisory AI mapping requirement WSP mapping | Customer WSP content in prompts; residency; prompt injection from an uploaded manual; a wrong mapping surviving review |

The project rule *"No Customer Documents in AI Prompts"* is stated absolutely in `CLAUDE.md`. Read literally it forbids the advisory AI mapping requirement. The correct reading, and the one this architecture implements: **no customer documents in developer-tool AI prompts, ever; customer WSP content in the product's inference path only through a governed, EU-resident, contractually bound channel with no training use and no retention.** That wording should be adopted in policy, because ambiguity here resolves badly under delivery pressure. **[PROPOSED]**

## Best practices

### AI-in-development **[PROPOSED]**

- **Enforce with managed configuration, not policy documents.** Anything relying on developer discipline fails eventually.
- **Deny tool read access to sensitive paths** — environment files, credential files, key material, production configuration.
- **Ban permission-bypass flags** via managed settings developers cannot override.
- **Treat AI-generated code as an untrusted third-party contribution**: same review, same static analysis, same tests, same two-person rule.
- **Log and retain AI tool usage** for audit.
- **Contract properly with the tool provider**: DPA, no-training commitment, retention terms, region of processing.

### AI-in-product **[PROPOSED unless marked]**

- **Data minimisation into the prompt.** Send the smallest span of WSP text needed to propose a mapping. Chunk, retrieve, and pass relevant excerpts — not whole manuals.
- **Pseudonymise before inference where the task allows.** A WSP is a policy document and usually contains few personal identifiers, but staff names and contact details do appear. Named-entity redaction with a reversible in-region token map costs little and rarely affects mapping quality.
- **Treat the uploaded manual as hostile input.** A PDF can contain text aimed at the model. Prompt injection is the principal AI-specific threat here (`threat-model`, T-22).
- **Model output never takes a privileged action.** Output is a *suggestion* record. Confirmation is a human act under the advisory AI mapping requirement, and confirmation of the mapping requires two approvers under the two-person mapping approval requirement.
- **Ground every suggestion.** Each proposed mapping must cite the WSP section — document, page and character span — and the Requirement ID. An ungrounded suggestion is unreviewable.
- **Evaluate continuously** against a held-out labelled set. **The 85% UAT accuracy bar is a PRD requirement (the PRD's WSP mapping accuracy commitment)** — the evaluation harness that measures it is therefore **[PRD REQUIRED]** in effect, and must exist before UAT, not after.

## Regulatory implications

- **GDPR Art. 28** — the inference provider is a **sub-processor**: DPA, customer notification, listing in the sub-processor register. **Art. 32** — security of the prompt/response channel. **Art. 5(1)(b)/(c)** — purpose limitation and minimisation constrain what enters a prompt. **Chapter V** — inference outside the EU is a transfer with its own tool and assessment; the EU residency requirement makes EU-resident inference the requirement here anyway.
- **GDPR Art. 22** — the output is a suggestion, confirmed by a human with authority to reject and subject to two-person sign-off. On the PRD's design the Art. 22 question does not arise. Do not weaken the advisory AI mapping requirement or the two-person mapping approval requirement without re-examining it.
- **GDPR Art. 35** — a DPIA is appropriate. **[PROPOSED]**
- **EU AI Act** — the platform would be a provider of an AI system. **Classification is not determined by the PRD and is not determined here.** Transparency labelling of AI-suggested mappings is good practice regardless, and dovetails with the PRD's own requirement that manual overrides be visibly tagged (the mapping override initiation gap). **[OPEN — LEGAL]**
- **DORA Art. 28–30** (customer-side) — the inference provider becomes a fourth party in the customer's supply chain if they contract those terms. **[OPEN]**
- **Copyright / IP** — AI-generated code may carry licence-contamination risk, and **the IP ownership term assigns all platform code 100% exclusively to the Client**. Enable code-referencing filters where available and run licence scanning regardless. **[PROPOSED]**

## Recommended architecture

### AI-in-development **[PROPOSED]**

Managed, non-overridable settings deployed to every engineer workstation by device management. Managed settings take precedence over user and project settings.

```jsonc
// Illustrative — verify key names against current tool documentation before rollout,
// and test enforcement by attempting a denied action after deployment.
{
  "permissions": {
    "deny": [
      "Read(./.env)", "Read(./.env.*)", "Read(**/*.pem)", "Read(**/*.key)",
      "Read(**/*.p12)", "Read(**/*.pfx)", "Read(**/id_rsa*)",
      "Read(**/secrets/**)", "Read(**/credentials*)",
      "Read(~/.aws/**)", "Read(~/.kube/**)", "Read(~/.ssh/**)",
      "Read(**/prod/**)", "Read(**/production/**)",
      "Bash(aws:*)", "Bash(kubectl:*)", "Bash(terraform apply:*)",
      "Bash(curl:*)", "Bash(wget:*)",
      "WebFetch"
    ],
    "defaultMode": "acceptEdits",
    "disableBypassPermissionsMode": "disable"
  },
  "env": { "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1" },
  "enableAllProjectMcpServers": false
}
```

Additional controls:

- **Pre-tool hooks** blocking any tool call whose arguments match production hostnames, real firm identifiers or personal-data patterns, with the attempt logged.
- **Agreement with the tool provider** covering no training on the organisation's data, retention terms, sub-processor disclosure, region of processing.
- **Session telemetry** — user, repository, timestamp, tools used, denials triggered. Denial spikes and off-hours volume are alertable.
- **Development environments contain only synthetic data** (`cross-border-data-processing`), so even total tool compromise yields no customer data. This is the control that makes the rest tolerable.
- **AI-generated code labelled** in commit trailers, then subjected to identical review and CI gates.
- **No production access from any AI-assisted session.**

### AI-in-product — the advisory AI mapping requirement mapping path

```
WSP upload (the single WSP upload requirement: .docx / PDF / scanned PDF)
   ▼ malware scan and structural checks in an isolated sandbox (`secure-media-storage`)
   ▼ store (object storage, per-firm key — The encryption requirement)
   ▼ text extraction, incl. OCR for scanned PDFs (in-region, sandboxed, no network)
   ▼ chunk and index (in-region; index encrypted with the firm's key)
   ▼ retrieve minimal relevant spans per candidate Requirement ID
   ▼ pseudonymise named entities (reversible map, in-region, firm-key encrypted)   [PROPOSED]
   ▼ assemble prompt: versioned system prompt + WSP text in a delimited, explicitly untrusted block
   ▼ EU-resident inference, no training on inputs/outputs, no provider retention   [PROPOSED — provider OPEN]
   ▼ schema-constrained output: {requirement_id, wsp_section, page, char_offsets, confidence}
   ▼ deterministic validation: cited span exists in the source at the stated offset  [PROPOSED]
   ▼ re-identify entities
   ▼ suggestion presented to a compliance officer — confirm or adjust               [PRD REQUIRED — The advisory AI mapping requirement]
   ▼ two independent senior approvers, policy author excluded                        [PRD REQUIRED — The two-person mapping approval requirement]
   ▼ mapping record written with full version history, nothing overwritten           [PRD REQUIRED — The permanent WSP version history requirement]
```

Key mechanisms:

- **Versioned system prompts stored as reviewed artefacts.** The prompt version is recorded on every suggestion so any output can be reproduced and explained. Prompt changes go through PR review. **[PROPOSED]**
- **Structural injection defence:** WSP text passes inside clearly delimited, explicitly untrusted blocks; the system prompt states that content within them is data, never instruction; output is constrained to a strict schema so instruction-following cannot express itself as an action. **[PROPOSED]**
- **Deterministic span verification, not model-judged:** every cited WSP span must exist in the source document at the stated offset. Failure blocks the suggestion from being presented as grounded. This removes the most dangerous failure class — a suggestion pointing at text that is not in the manual — without relying on a model to check a model. **[PROPOSED]**
- **Accuracy harness:** a held-out set of pre-defined verification text vectors, run on every prompt or model change, reporting accuracy against the **85% bar**. Regression below the bar blocks promotion. **[PRD REQUIRED in substance — the PRD's WSP mapping accuracy commitment]**
- **Model registry:** model identifier, version, prompt version, sampling parameters, evaluation results, approval date, rollback target. Model upgrades are change-managed and re-evaluated. **[PROPOSED]**
- **Full inference audit trail:** for every call — tenant, user, document IDs, prompt hash, prompt version, model version, token counts, latency, output hash, validation results, reviewer decision, both approver identities. Retained with the mapping record. Store the prompt *hash* plus retrievable inputs rather than raw prompt text in general logs. **[PROPOSED, supporting the permanent audit log requirement / the immutable audit requirement]**
- **Override tagging:** any manual mapping change carries a visible tag distinguishing it from an AI or system-generated mapping. **[PRD REQUIRED — the PRD's mapping sign-off rules, the mapping override initiation gap]**
- **Who may initiate a manual override** is **[OPEN]** — The mapping override initiation gap is only partially resolved in the PRD.
- **Per-firm AI opt-out and per-firm model configuration** — not in the PRD. **[FUTURE]**
- **A second, independently exercised inference provider** for concentration risk — **[FUTURE]**.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Developer pastes a real customer document into an AI coding tool | Confidentiality breach; possible unlawful transfer | Synthetic-only development data; managed deny rules; clipboard pattern blocking; hooks; training |
| Prompt injection in an uploaded WSP steers the mapping | Wrong mapping presented as AI-derived; wasted reviewer trust; a real gap concealed | Untrusted-data delimiting, schema-constrained output, injection-signature detection, span verification, the advisory AI mapping requirement human review and the two-person mapping approval requirement two-person approval |
| Suggested mapping cites a WSP section that does not exist | Reviewer confusion; erosion of trust in the feature; accuracy bar missed | Deterministic span verification as a blocking check |
| Accuracy drifts below 85% after a model or prompt change | **Direct breach of a PRD-accepted commitment (the PRD's WSP mapping accuracy commitment)** | Evaluation harness on the verification vectors, run as a promotion gate; alert on regression |
| Cross-firm leakage via a shared retrieval index | Breach of the tenant isolation requirement | Per-firm index namespace with a firm filter enforced at the data layer, plus a mandatory cross-tenant retrieval negative test |
| Inference provider changes terms, region or retention | Breach of the EU residency requirement discovered late | Contractual change-notice; annual review; provider selection criteria written down (`open-questions`, T-4) |
| Over-reliance — "the AI mapped it, so it is mapped" | Two-person sign-off becomes rubber-stamping; the two-person mapping approval requirement's purpose defeated | Reviewer must record an independent basis; the UI never pre-approves; override and confirmation rates monitored |
| AI-generated code introduces a tenant-isolation flaw | Breach of the tenant isolation requirement | Identical review and CI gates; custom tenancy static-analysis rules; isolation tests |

## Trade-offs

- **Managed inference service vs. self-hosted open-weight model.** Managed services generally give better mapping quality and a cleaner residency and contractual story; self-hosting maximises control at a quality and operational cost. **The PRD selects neither.** Selection criteria to apply: EU-resident processing, no training on inputs or outputs, no provider-side retention, contractual change notice, measured accuracy against the verification vectors, and cost per mapping run. **[OPEN — see `open-questions`, T-4]**
- **Pseudonymise before inference vs. send raw excerpts.** Entity redaction rarely hurts regulatory-mapping tasks and improves the data-protection position. Recommendation: pseudonymise by default. **[PROPOSED]**
- **Ban AI coding tools vs. govern them.** A ban forfeits real productivity and drives shadow usage on personal accounts, which is worse. Recommendation: govern, with managed settings and synthetic-only data. **[PROPOSED]**
- **Full prompt logging vs. hash plus metadata.** Full prompts contain customer content and become another copy to protect. Recommendation: hash plus structured metadata plus inputs by reference; full-text capture only in a short-retention, firm-key-encrypted debug store enabled per firm on consent. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification | Basis |
|---|---|---|---|
| DD-05-01 | Policy states precisely: no customer data in developer AI tooling under any circumstances; customer WSP content enters product inference only via the governed EU-resident path. `CLAUDE.md` wording amended accordingly | **[PROPOSED]** | resolves an internal ambiguity |
| DD-05-02 | AI coding tools governed by managed settings with deny rules for secrets and production paths and bypass mode disabled; enforcement verified by test after each rollout | **[PROPOSED]** | — |
| DD-05-03 | Production inference is EU-resident with no training on inputs/outputs and no provider retention; **provider and model are not selected** | **[PROPOSED / OPEN]** | EU residency requirement |
| DD-05-04 | WSP content in prompts is delimited as untrusted data; model output is schema-constrained and never triggers a privileged action | **[PROPOSED]** | supports the advisory AI mapping requirement |
| DD-05-05 | Deterministic verification that each cited WSP span exists at the stated offset in the source document, blocking on failure | **[PROPOSED]** | supports the PRD's WSP mapping accuracy commitment accuracy |
| DD-05-06 | AI mapping suggestions are advisory; a compliance officer confirms or adjusts, and confirmation requires two independent senior approvers excluding the policy author | **[PRD REQUIRED]** | Advisory AI mapping requirement, the two-person mapping approval requirement |
| DD-05-07 | Reversal of a confirmed mapping follows the same two-person process; reversal, approvers and date are permanently recorded | **[PRD REQUIRED]** | Mapping reversal requirement |
| DD-05-08 | Mapping re-runs automatically on upload of a new labelled WSP version; manual overrides carry a visible manual-change tag | **[PRD REQUIRED]** | The PRD's mapping sign-off rules, the mapping override initiation gap |
| DD-05-09 | An evaluation harness against the pre-defined verification text vectors measures mapping accuracy and gates promotion at the 85% bar | **[PRD REQUIRED in substance]** | The PRD's WSP mapping accuracy commitment |
| DD-05-10 | Model registry with versioned prompts, evaluation results and a documented rollback target | **[PROPOSED]** | — |
| DD-05-11 | Reversible entity pseudonymisation before inference, token map held in-region and encrypted with the firm's key | **[PROPOSED]** | GDPR Art. 5(1)(c), 32 |
| DD-05-12 | Full inference audit record for every call, retained with the mapping record | **[PROPOSED]** | supports the permanent audit log requirement |
| DD-05-13 | AI-suggested mappings are labelled as such in the UI; whether further AI Act transparency obligations apply is undetermined | **[PROPOSED / OPEN — LEGAL]** | — |
| DD-05-14 | Who may initiate a manual override of a mapping | **[OPEN]** | Mapping override initiation gap partially open |

## References

- Regulation (EU) 2016/679 (GDPR) Art. 5, 22, 25, 28, 32, 35; Recital 71
- EDPB Opinion 28/2024 on AI models and personal data processing
- Regulation (EU) 2024/1689 (AI Act) — classification undetermined
- OWASP Top 10 for LLM Applications; MITRE ATLAS
- NIST AI Risk Management Framework (AI 100-1) and Generative AI Profile (NIST AI 600-1)
- Claude Code settings and managed policy documentation — verify current keys at implementation

## Confidence level

**High** — the two-surface split, synthetic-only development, the injection-defence pattern, deterministic span verification, and the human-review and two-person-approval requirements, which are PRD-mandated rather than inferred.

**Medium** — how much retrieval architecture the 85% bar actually requires; this needs a spike against real WSP documents and the agreed verification vectors before the approach is fixed.

**Not determined** — inference provider and model, AI Act classification, and who may initiate a manual mapping override.
