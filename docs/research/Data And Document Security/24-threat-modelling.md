# 24 — Threat Modelling

This document covers the **methodology and programme**. The applied result — the actual threat model for this platform — is in `32-threat-model.md`.

## Best practices

- **Threat modelling is a habit, not a document.** A 200-page model produced once and filed is worth less than a 30-minute structured discussion on every design that touches a trust boundary.
- **Answer the four questions** (Shostack): *What are we building? What can go wrong? What are we going to do about it? Did we do a good job?* The fourth question is the one teams skip, and it is what converts a model into assurance.
- **Model data flows, not components.** Threats live at trust boundaries, and trust boundaries are visible only in a data-flow view.
- **Every threat produces a decision:** mitigate, transfer, accept (with a named owner and an expiry date), or eliminate. A threat with no decision is a threat you have merely documented.
- **Mitigations become tests.** An abuse case that is not a test case will regress. This is the single highest-leverage practice in the whole programme.
- **Include privacy threats.** STRIDE finds security threats; LINDDUN finds privacy threats. For a GDPR-regulated platform, omitting privacy threat modelling is a gap a supervisory authority will notice.
- **Include AI-specific threats.** Standard frameworks predate prompt injection and model supply-chain risk; supplement with OWASP LLM Top 10 and MITRE ATLAS.

## EU regulatory implications

- **DORA Art. 6(2)/Art. 8** — the ICT risk management framework must include identification of all sources of ICT risk, and continuous identification of risks affecting information and ICT assets. **Art. 8(2)** requires identification of all ICT-supported business functions, information assets and ICT assets, and their interdependencies. Threat modelling is the practical technique that produces this.
- **Commission Delegated Regulation (EU) 2024/1774** — requires risk assessment on ICT changes and on new or changed systems before deployment. A per-change threat model is the cleanest way to evidence this.
- **DORA Art. 24–27** — the resilience testing programme should be informed by identified threats; TLPT (TIBER-EU) is explicitly **threat-led**, meaning threat intelligence and a threat model drive scenario selection.
- **GDPR Art. 25** — data protection by design requires assessing risks to rights and freedoms at design time. **Art. 35** — the DPIA must contain "an assessment of the risks to the rights and freedoms of data subjects" and the measures to address them. **A LINDDUN privacy threat model is the most defensible way to produce the DPIA risk section** — far stronger than a narrative assessment.
- **NIS2 Art. 21(2)(a)** — policies on risk analysis and information system security. **Art. 21(1)** requires measures proportionate to the risks posed, which requires having assessed them.
- **AI Act** — even at limited-risk classification, documented risk assessment of the AI system is expected practice and will be requested by customers regardless of the legal floor.
- **MiCA Art. 68** — sound risk management as part of governance; our threat model feeds the customer's own outsourcing risk assessment.

## Recommended architecture (of the programme)

### Three tiers of threat modelling

| Tier | Trigger | Effort | Method | Output |
|---|---|---|---|---|
| **T1 — Per-change** | Any PR touching authn/authz, crypto, tenancy, file handling, external integration, or AI prompt construction | 20–30 min | STRIDE-per-element on the changed data flow, from a checklist | Abuse cases in the PR description; new tests |
| **T2 — Per-feature** | New feature or subsystem at design time | Half-day workshop | STRIDE + LINDDUN + relevant ATLAS techniques; DFD drawn | Threat table with decisions; ADR for significant choices |
| **T3 — System-wide** | Annual, and on major architectural change | 2–3 days | Full DFD refresh, attack trees for top scenarios, MITRE ATT&CK coverage mapping | Updated `32-threat-model.md`; risk register updates; testing programme inputs |

T1 is enforced by CI: a PR touching a designated path must contain a completed threat-model section in its description, checked by a workflow against changed paths (DD-04-04).

### Methods, and where each applies

- **STRIDE** — the workhorse for security threats. Applied per-element (process, data store, data flow, external entity) rather than per-diagram, because per-element is systematic and per-diagram is intuition.
- **LINDDUN** — privacy threats: **L**inking, **I**dentifying, **N**on-repudiation, **D**etecting, **D**ata disclosure, **U**nawareness, **N**on-compliance. Mandatory for anything processing personal data. Feeds the DPIA directly.
- **MITRE ATT&CK** — for coverage mapping and detection engineering (doc 22), not for discovery.
- **MITRE ATLAS + OWASP LLM Top 10** — for the AI subsystem. Prompt injection, training-data poisoning (less relevant with a managed model), model extraction, insecure output handling, excessive agency, supply chain.
- **Attack trees** — for the small number of catastrophic scenarios worth deep analysis: cross-tenant document disclosure, evidence tampering, mass exfiltration, key compromise.
- **PASTA** — considered and rejected as too heavyweight for a team of this size; its business-impact framing is captured instead in the risk register.

### Per-element STRIDE checklist (the working tool)

| Element type | S | T | R | I | D | E |
|---|---|---|---|---|---|---|
| External entity (user, customer IdP, AI provider) | ✓ | | ✓ | | | |
| Process (service, Lambda, enclave) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Data store (Postgres, S3, cache, index) | | ✓ | ✓ | ✓ | ✓ | |
| Data flow (API call, replication, queue) | | ✓ | | ✓ | ✓ | |

For each ✓, ask the standard question and record: threat, likelihood, impact, existing control, decision, test.

### Domain-specific threat prompts

Generic STRIDE misses the threats specific to this platform. Add these standing questions to every T2 model:

1. **Cross-tenant:** can any input cause data from tenant A to reach tenant B? Consider caches, indexes, embeddings, error messages, background jobs, exports, and shared model context.
2. **Evidence integrity:** can this change allow an evidence record to be altered, deleted, backdated, or created without a valid approval?
3. **Key exposure:** does this change create a path by which plaintext or key material could reach a log, a metric, an error message, or a lower-privilege component?
4. **Residency:** does this change create a path by which data or metadata could leave the EU, including via a new sub-processor, a global service, or telemetry?
5. **India access:** does this change create a path by which an India-based person could reach production personal data?
6. **AI:** can uploaded content influence model behaviour? Can model output trigger a privileged action? Can an assessment be produced without a human approval?
7. **Retention:** can this change cause data to be retained beyond policy, or deleted before its legal minimum?

These seven questions catch most of what generic frameworks miss here.

### Linking threats to tests

Every mitigated threat gets a test with a stable identifier:

```
THREAT-T07  Cross-tenant document read via manipulated object ID
  Mitigation: repository tenant scoping + RLS + KMS encryption context
  Tests:      test_cross_tenant_document_read_denied  (application)
              test_rls_blocks_cross_tenant_select      (database)
              test_kms_decrypt_wrong_context_fails     (crypto)
  Detection:  DET-03 cross-tenant access attempt alert
  Status:     Mitigated, verified 2026-07-xx
```

The threat model becomes traceable: a reviewer or auditor can follow any threat to the code that mitigates it, the test that proves it, and the detection that catches a bypass. This traceability is what makes the model credible under DORA and to enterprise buyers.

### Validation ("did we do a good job?")

- **Purple team** quarterly: attempt the top 5 modelled attack paths against staging; any success is a P1 finding.
- **Annual penetration test** with the threat model supplied to the testers, scoped explicitly to include multi-tenancy isolation.
- **Bug bounty** (private, from year 2) as an independent check on model completeness.
- **Incident retrospectives** ask: "was this threat in the model? If not, why not?" Model gaps found by incidents are the most valuable input available.
- **Coverage metrics:** percentage of trust boundaries modelled, percentage of mitigated threats with tests, percentage with detections.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Threat modelling becomes a compliance ritual | Effort spent, no risk reduced | Tie every threat to a test or a detection; measure that ratio; review models in incident retrospectives |
| Model goes stale as architecture evolves | Model describes a system that no longer exists | T1 per-change modelling keeps it current; annual T3 refresh; DFD generated partly from IaC where possible |
| Only security people participate | Engineers do not internalise the threats; models miss implementation reality | Engineers lead T1 models; security facilitates T2; make the checklist short enough to actually use |
| Focus on exotic threats, miss the boring ones | Real breach via a misconfiguration nobody modelled | Include configuration, operational and human threats explicitly; review incidents from comparable platforms |
| Privacy threats omitted | DPIA weak; supervisory finding | LINDDUN mandatory for personal-data flows; DPO reviews T2 models |
| AI threats modelled with pre-LLM frameworks | Prompt injection and output-handling threats missed | ATLAS and OWASP LLM Top 10 mandatory for AI-touching changes |
| Accepted risks accumulate silently | Risk posture drifts without visibility | Accepted risks carry an owner and expiry date; expired acceptances escalate to the management body |

## Trade-offs

- **Formal method (systematic, slow, high-quality) vs. lightweight checklist (fast, adopted, less complete).** Adoption dominates completeness — an unused rigorous method finds nothing. **Recommendation: tiered approach as above; checklist for T1, formal for T2/T3.**
- **Threat modelling tooling (OWASP Threat Dragon, IriusRisk, Microsoft TMT) vs. markdown and a whiteboard.** Tools add structure and reuse but also friction and licence cost. **Recommendation: markdown templates in the repo alongside the code, with diagrams as Mermaid so they version and diff. Revisit tooling if the model exceeds what a repo can carry.**
- **Modelling everything (complete, expensive) vs. risk-based scoping.** **Recommendation: risk-based — trust boundaries and the seven domain-specific questions define scope. Not every CRUD endpoint needs a model.**
- **Security-owned models (consistent quality; bottleneck and low engineering ownership) vs. engineer-owned (scalable, variable quality).** **Recommendation: engineer-owned with security review; invest in training so quality converges.**
- **Publishing a threat model summary to customers (strong differentiator, demonstrates maturity; reveals architecture detail to attackers) vs. keeping it internal.** **Recommendation: publish a sanitised summary under NDA in the security pack — the maturity signal materially outweighs the disclosure risk.**

## Design decisions

- **DD-24-01:** Three-tier threat modelling programme: T1 per-change checklist (CI-enforced on designated paths), T2 per-feature workshop, T3 annual system-wide refresh.
- **DD-24-02:** STRIDE-per-element for security, LINDDUN for privacy (feeding the DPIA), ATLAS + OWASP LLM Top 10 for AI, attack trees for the four catastrophic scenarios.
- **DD-24-03:** The seven domain-specific threat questions (cross-tenant, evidence integrity, key exposure, residency, India access, AI, retention) are mandatory in every T2 model.
- **DD-24-04:** Every mitigated threat carries a stable identifier linked to specific tests and detections; the linkage ratio is a reported metric.
- **DD-24-05:** Threat models live in the repository as markdown with Mermaid diagrams, versioned with the code they describe.
- **DD-24-06:** Accepted risks require a named owner and an expiry date; expiry escalates to the management body (DORA Art. 5(2) accountability).
- **DD-24-07:** Quarterly purple-team validation of the top modelled attack paths; annual penetration test scoped with the model supplied to testers.
- **DD-24-08:** Every incident retrospective asks whether the threat was modelled; gaps feed the next T3 refresh.
- **DD-24-09:** A sanitised threat model summary is included in the customer security pack under NDA.

## References

- Adam Shostack, *Threat Modeling: Designing for Security* (Wiley, 2014); the Threat Modeling Manifesto (2020)
- Microsoft STRIDE; OWASP Threat Modeling Cheat Sheet; OWASP Threat Dragon
- LINDDUN privacy threat modelling framework (https://linddun.org)
- MITRE ATT&CK Enterprise and Cloud matrices; MITRE ATLAS (adversarial threat landscape for AI systems)
- OWASP Top 10 for LLM Applications (2025)
- NIST SP 800-30 Rev. 1 — Guide for Conducting Risk Assessments
- Regulation (EU) 2022/2554 (DORA) Art. 6, 8, 24–27; Commission Delegated Regulation (EU) 2024/1774
- Regulation (EU) 2016/679 (GDPR) Art. 25, 35; EDPB/WP29 Guidelines on DPIA (WP248 rev.01)
- TIBER-EU Framework (ECB) — threat intelligence-based ethical red teaming

## Confidence level

**High** — the tiered programme, method selection, threat-to-test traceability, and the domain-specific question set. This is proven practice, appropriately scaled to a small team, and it produces exactly the evidence DORA and GDPR Art. 35 require.

**Medium** — sustaining T1 discipline under delivery pressure. This is the most common failure mode of threat modelling programmes; the CI enforcement helps, but leadership attention is the real control.
