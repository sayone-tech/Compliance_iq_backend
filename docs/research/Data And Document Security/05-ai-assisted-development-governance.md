# 05 — AI-Assisted Development Governance

Two distinct AI surfaces exist and must be governed separately:

- **AI-in-development** — Claude Code used by engineers in India to build the platform. Risk: source code and, if uncontrolled, customer data leaving the environment; unvetted code entering production.
- **AI-in-product** — the LLM that generates compliance assessments for customers. Risk: customer document content in prompts, residency, hallucinated compliance conclusions, prompt injection from uploaded documents.

The project rule *"No Customer Documents in AI Prompts"* is stated absolutely in CLAUDE.md. Read literally it forbids the product's core function. The correct reading, and the one this architecture implements: **no customer documents in *developer-tool* AI prompts, ever; customer documents in *product* AI prompts only through a governed, EU-resident, contractually-bound inference path with no training use and no retention.** This distinction should be written into policy explicitly, because ambiguity here will be resolved badly under delivery pressure.

## Best practices

### AI-in-development

- **Enforce controls with managed configuration, not policy documents.** Anything relying on developer discipline will fail on a Friday afternoon.
- **Deny read access to sensitive paths at the tool level** — `.env*`, credential files, key material, any production configuration.
- **Ban permission bypass flags** (`--dangerously-skip-permissions` and equivalents) via managed settings that developers cannot override.
- **Treat AI-generated code as untrusted third-party contribution**: same review, same SAST, same tests, same two-person rule. No exceptions for "it's just a refactor".
- **Log and retain AI tool usage** for audit — which repositories, which sessions, what was approved.
- **Contract properly with the AI provider**: DPA, no-training commitment, retention terms, sub-processor listing, region of processing.

### AI-in-product

- **Data minimisation into the prompt.** Send the smallest span of document text needed for the task. Chunk, retrieve, and pass only relevant excerpts — not whole documents.
- **Pseudonymise before inference where the task allows.** Named-entity redaction (names, account numbers, wallet addresses, national IDs) with a reversible token map held in-region, restored after inference. This changes the risk profile substantially and is often invisible to answer quality.
- **Treat uploaded documents as hostile input.** A PDF can contain instructions aimed at the model. Prompt injection is the top AI-specific threat here (doc 24).
- **Never let model output take a privileged action directly.** Output is data. Any action derived from it passes through deterministic validation and human approval.
- **Ground every assertion.** Assessments must cite the source document, page, and span. Ungrounded output is unusable in a regulated audit file and is the fastest route to a customer relying on a hallucination.
- **Evaluate continuously** against a held-out, expert-labelled set; track hallucination rate, citation accuracy, and regulatory-mapping precision as production metrics.

## EU regulatory implications

- **GDPR Art. 28** — the AI inference provider is a **sub-processor**. Requires a DPA, customer notification, and listing in the sub-processor register. **Art. 32** — security of processing covers the prompt/response channel. **Art. 5(1)(b)/(c)** — purpose limitation and minimisation directly constrain what enters a prompt. **Art. 44 et seq.** — if inference occurs outside the EU, it is a transfer requiring its own tool and TIA.
- **GDPR Art. 22 / Recital 71** — automated decisions producing legal or similarly significant effects. Our output is decision *support*; keep it that way with a competent, empowered human reviewer whose approval is logged (see DD-01-05).
- **GDPR Art. 35** — a DPIA is mandatory: large-scale processing of special-category-capable data with new technology.
- **EU AI Act (Regulation (EU) 2024/1689)** — we are a **provider** of an AI system. Art. 4 AI literacy obligations and Art. 5 prohibitions applied from 2 February 2025. Art. 50 transparency: users must know they are interacting with AI and that content is AI-generated. Expect limited-risk classification for compliance assessment, but document the classification and re-run it on material feature change. If a feature ever scores or profiles *natural persons* in a way touching Annex III, the classification changes materially.
- **DORA Art. 28–30** — the AI provider is an ICT third-party service provider in the customer's supply chain, appearing in their register of information. If AI assessment supports a critical or important function, the Art. 30(3) contract set flows through to the AI provider — including audit rights and exit strategy. **This is a hard requirement to check against your chosen inference vendor's standard terms.**
- **DORA Art. 12/Art. 11** — dependence on a single AI provider is a concentration risk requiring a documented exit plan and a fallback (a second model provider or degraded manual mode).
- **NIS2 Art. 21(2)(d)/(j)** — supply-chain security and the use of cryptography/MFA in the toolchain; AI development tooling is part of the supply chain.
- **Copyright/IP** — AI-generated code may carry licence-contamination risk. Enable code-referencing filters where available and run licence scanning regardless.

## Recommended architecture

### AI-in-development (Claude Code in Zone D)

**Managed, non-overridable settings** deployed by MDM to every engineer workstation (Linux: `/etc/claude-code/managed-settings.json`; macOS: `/Library/Application Support/ClaudeCode/managed-settings.json`). Managed settings take precedence over user and project settings and cannot be edited by the developer.

```jsonc
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
  "env": {
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  },
  "enableAllProjectMcpServers": false
}
```

Additional controls:
- **Verify the exact setting keys against the current Claude Code settings documentation before rollout** — key names evolve; a typo yields a silently unenforced control. Test enforcement after deployment by attempting a denied action.
- **PreToolUse hooks** that block any tool call whose arguments match production hostnames, real customer identifiers, or PII patterns, and log the attempt to the SIEM.
- **Enterprise agreement with the AI provider** covering: no training on our data, retention terms (zero-retention where offered), sub-processor disclosure, region of processing, security attestations.
- **Session telemetry to the SIEM** — user, repository, timestamp, tools used, denials triggered. Anomalies (unusual volume, denial spikes, off-hours) are alertable.
- **Zone D contains only synthetic data** (DD-03-02), so even a total tool compromise cannot yield customer data. This is the control that makes the rest tolerable.
- **AI-generated code is labelled** in commit trailers for traceability and post-hoc analysis, then subjected to identical review and CI gates.
- **No production access from any AI-assisted session.** Zone P is outside the tool's reach entirely.

### AI-in-product (customer document processing)

```
Upload ──▶ AV/CDR scan ──▶ Store (S3, tenant CMK) ──▶ Extract text (in-region, sandboxed)
                                                            │
                                              Chunk + embed (in-region, pgvector)
                                                            │
                                            Retrieve minimal relevant spans
                                                            │
                                     Pseudonymise entities (reversible, in-region map)
                                                            │
                              Prompt assembly ── system prompt is immutable, versioned, signed
                              Document content is delimited and marked as untrusted data
                                                            │
                        ┌───── Amazon Bedrock (Claude), eu-central-1, EU-only inference ─────┐
                        │      no training on inputs/outputs; no provider-side retention      │
                        └────────────────────────────────────────────────────────────────────┘
                                                            │
                              Output validation: schema, citation-existence check,
                              injection-signature detection, confidence scoring
                                                            │
                                             Re-identify entities from token map
                                                            │
                                      Human reviewer approval (logged, attributed)
                                                            │
                                    Assessment record ──▶ WORM evidence store
```

Key mechanisms:
- **Immutable, versioned system prompts** stored as signed artefacts. The prompt version is recorded on every assessment so any output can be reproduced and explained to an auditor. Prompt changes go through PR review.
- **Structural injection defence:** document text is passed inside clearly delimited, explicitly-untrusted blocks; the system prompt states that content within them is data and never instruction; output is constrained to a strict schema (tool/JSON mode) so free-form instruction-following cannot express itself as an action.
- **Citation verification is deterministic**, not model-judged: every cited span must exist in the source document at the stated offset. Failures block the assessment. This kills the most dangerous hallucination class outright.
- **Model registry**: model ID, version, prompt version, temperature, evaluation results, approval date, and rollback target for each production model configuration. Model upgrades are a change-managed event with re-evaluation.
- **Fallback provider** configured and periodically exercised (DORA exit/concentration requirement) — a second model on Bedrock, or a self-hosted open-weight model in-region for degraded operation.
- **Full inference audit trail**: for every call — tenant, user, document IDs, prompt hash, prompt version, model version, token counts, latency, output hash, validation results, reviewer decision. Retained with the assessment. Store the prompt *hash* plus the retrievable inputs rather than raw prompt text in general logs.
- **Per-tenant AI opt-out** and per-tenant model configuration where contractually required.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Developer pastes real customer document into Claude Code to debug | Unlawful transfer, residency breach, confidentiality breach | Synthetic-only Zone D; managed deny rules; DLP on clipboard; hooks blocking PII patterns; training |
| Prompt injection in an uploaded document steers the assessment or exfiltrates context | Wrong compliance conclusion; cross-document leakage; reputational/regulatory damage | Untrusted-data delimiting, schema-constrained output, injection detection, no privileged actions from output, human approval |
| Hallucinated regulatory citation reaches a customer's audit file | Customer regulatory finding, liability, loss of trust | Deterministic citation verification; confidence thresholds; mandatory human review; clear AI-generated labelling |
| AI provider changes terms, region, or retention | Residency/legal breach discovered late | Contractual change-notice; annual review; fallback provider ready |
| Cross-tenant leakage via a shared vector index | Catastrophic confidentiality breach | Per-tenant index namespace + tenant filter enforced at the data layer, plus a mandatory cross-tenant retrieval negative test |
| AI-generated code introduces a subtle authorisation flaw | Tenant isolation break | Identical review/SAST gates; custom tenancy rules; targeted isolation tests |
| Model upgrade silently degrades assessment quality | Undetected compliance-advice regression | Golden evaluation set run pre-promotion; blocked on regression |
| Over-reliance ("the AI said it was compliant") | De facto automated decision-making under Art. 22 | Reviewer must record an independent basis; UI never pre-approves; override rate monitored |

## Trade-offs

- **Bedrock (EU region, AWS DPA, integrated IAM/KMS/logging, no training) vs. direct Anthropic API (newest models first, direct relationship).** Bedrock gives the cleaner residency and contractual story inside one existing sub-processor relationship. **Recommendation: Bedrock in `eu-central-1` for production inference; direct API acceptable for developer tooling in Zone D on synthetic data.**
- **Self-hosted open-weight model (maximum sovereignty) vs. managed frontier model (quality).** Compliance assessment quality is the product; a materially weaker model damages the value proposition and, arguably, safety. **Recommendation: managed frontier model, with a self-hosted fallback for degraded mode and for Tier 3 sovereign customers who accept the quality trade-off.**
- **Pseudonymise before inference (stronger privacy, some quality loss and engineering cost) vs. send raw excerpts.** Entity redaction rarely hurts regulatory-mapping tasks and greatly improves the DPIA position. **Recommendation: pseudonymise by default; allow per-tenant opt-out with documented justification where quality demonstrably suffers.**
- **Ban AI coding tools (simple, safe) vs. govern them (productive, requires controls).** A ban forfeits a real productivity advantage and drives shadow usage on personal accounts, which is strictly worse. **Recommendation: govern, with managed settings and synthetic-only data.**
- **Full prompt logging (great forensics) vs. hash-only (minimisation).** Full prompts contain customer content and become another copy to protect. **Recommendation: hash + structured metadata + retrievable inputs by reference; full-text capture only in a short-retention, tenant-key-encrypted debug store, enabled per-tenant on consent.**

## Design decisions

- **DD-05-01:** Policy is stated precisely: **no customer data in developer AI tooling under any circumstances**; customer document content may enter *product* inference only via the governed EU-resident path. The CLAUDE.md rule is amended to this wording to remove ambiguity.
- **DD-05-02:** Claude Code governed by MDM-deployed managed settings with deny rules for secrets/production paths and bypass-mode disabled; enforcement verified by test after every rollout.
- **DD-05-03:** Production inference on Amazon Bedrock in `eu-central-1`, cross-region inference disabled, no training on inputs/outputs, contractually confirmed.
- **DD-05-04:** All document content in prompts is delimited as untrusted data; model output is schema-constrained and never triggers a privileged action directly.
- **DD-05-05:** Deterministic citation verification against source offsets is a blocking gate on every assessment.
- **DD-05-06:** Named human reviewer approval required before any assessment becomes an evidence record; reviewer identity, timestamp and overrides logged immutably.
- **DD-05-07:** Model registry with versioned prompts, golden-set evaluation gate on promotion, and a documented rollback.
- **DD-05-08:** Reversible entity pseudonymisation before inference by default, token map held in-region and encrypted with the tenant key.
- **DD-05-09:** Second inference provider maintained and exercised quarterly to satisfy DORA concentration/exit expectations.
- **DD-05-10:** AI-generated content is labelled as such in the UI and in exported reports (AI Act Art. 50 alignment).

## References

- Regulation (EU) 2024/1689 (AI Act) Art. 4, 5, 50; Annex III
- Regulation (EU) 2016/679 (GDPR) Art. 5, 22, 25, 28, 32, 35; Recital 71
- EDPB Opinion 28/2024 on AI models and personal data processing
- Regulation (EU) 2022/2554 (DORA) Art. 28–30 (AI provider as ICT third party)
- OWASP Top 10 for LLM Applications (2025); MITRE ATLAS
- NIST AI Risk Management Framework (AI 100-1) and Generative AI Profile (NIST AI 600-1)
- Claude Code settings and managed policy documentation (verify current keys at implementation)
- Amazon Bedrock data protection and regional inference documentation

## Confidence level

**High** — the two-surface split, synthetic-only development, prompt-injection defence pattern, deterministic citation verification, and human-in-the-loop requirement. These are well-established and directly reduce the dominant risks.

**Medium** — exact Claude Code managed-settings key names and semantics (verify against current docs; test enforcement), and the final AI Act classification of compliance-assessment AI.

**Low-to-medium** — long-term stability of AI provider contractual terms on training/retention/region. Treat as a monitored dependency with a contractual change-notice clause.
