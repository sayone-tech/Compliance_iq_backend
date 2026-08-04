# Threat Modelling

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](../future-scope/future-and-optional-scope.md).

This document covers the **methodology and programme**. The applied result — the actual threat model for ComplianceIQ — is in [Threat Model](../threat-model.md). Everything here is **[PROPOSED]**.

## Best practices

- **Threat modelling is a habit, not a document.** A large model produced once and filed is worth less than a short structured discussion on every design that touches a trust boundary.
- **Answer the four questions:** what are we building; what can go wrong; what are we going to do about it; did we do a good job. The fourth is the one teams skip, and it is what converts a model into assurance.
- **Model data flows, not components.** Threats live at trust boundaries, and trust boundaries are visible only in a data-flow view.
- **Every threat produces a decision:** mitigate, transfer, accept with a named owner and an expiry, or eliminate. A threat with no decision is a threat you have merely documented.
- **Mitigations become tests.** An abuse case that is not a test case will regress. This is the single highest-leverage practice in the programme.
- **Include privacy threats.** Security frameworks find security threats; a privacy framework finds privacy threats. For a GDPR-regulated platform (NFR-06), omitting privacy threat modelling is a visible gap.
- **Include AI-specific threats.** Standard frameworks predate prompt injection; supplement for the FR-31 mapping path.

## Regulatory implications

- **GDPR Art. 25** — data protection by design requires assessing risks to rights and freedoms at design time. **Art. 35** — a data protection impact assessment must contain an assessment of the risks and the measures addressing them. **A structured privacy threat model is the most defensible way to produce that risk section.**
- **Delegated Reg. (EU) 2024/1774** — risk assessment on ICT changes and on new or changed systems before deployment. A per-change threat model is the cleanest way to evidence it. *(Design reference.)*
- **PRD NFR-01, NFR-04, NFR-07** — these three requirements define what "catastrophic" means for this product, and therefore what the model must cover first: cross-firm disclosure, audit tampering, and record loss or deletion.

## Recommended programme

### Three tiers

| Tier | Trigger | Effort | Method | Output |
|---|---|---|---|---|
| **T1 — per change** | Any change touching authentication, authorisation, tenancy, cryptography, file handling, retention or immutability, or the WSP mapping path | 20–30 minutes | Structured per-element pass on the changed data flow, from a checklist | Abuse cases in the change description; new tests |
| **T2 — per feature** | A new feature or subsystem at design time | Half-day workshop | Security plus privacy analysis, with a data-flow diagram drawn | Threat table with decisions; a recorded decision for significant choices |
| **T3 — system-wide** | Periodically, and on major architectural change | Two to three days | Full data-flow refresh, attack trees for the top scenarios, coverage mapping | Updated `threat-model`; risk register updates; testing programme inputs |

T1 is enforced by CI: a change touching a designated path must contain a completed threat-model section, checked against the changed paths (`secure-sdlc`, DD-04-04).

### Methods, and where each applies

- **STRIDE, per element** (process, data store, data flow, external entity) — the workhorse for security threats. Per-element is systematic; per-diagram is intuition.
- **LINDDUN** — privacy threats: linking, identifying, non-repudiation, detecting, data disclosure, unawareness, non-compliance. Mandatory for personal-data flows; feeds the data protection impact assessment.
- **MITRE ATT&CK** — for coverage mapping and detection engineering (`security-monitoring`), not for discovery.
- **MITRE ATLAS and the OWASP LLM Top 10** — for the WSP mapping path: prompt injection, insecure output handling, excessive agency, supply chain.
- **Attack trees** — for the small number of catastrophic scenarios worth deep analysis, which for this product are defined by the PRD itself: cross-firm disclosure (NFR-01), audit or evidence tampering (NFR-04), record loss (NFR-07), mass exfiltration.

### Per-element checklist

| Element type | Spoofing | Tampering | Repudiation | Information disclosure | Denial of service | Elevation |
|---|---|---|---|---|---|---|
| External entity (firm user, Portal admin, inference provider) | ✓ | | ✓ | | | |
| Process (service, job, sandbox) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Data store (database, object storage, cache, index) | | ✓ | ✓ | ✓ | ✓ | |
| Data flow (API call, replication, queue) | | ✓ | | ✓ | ✓ | |

For each mark, record: threat, likelihood, impact, existing control, decision, test.

### Domain-specific threat prompts

Generic frameworks miss what is specific to ComplianceIQ. These seven questions are mandatory in every T2 model:

1. **Cross-firm (NFR-01):** can any input cause data from firm A to reach firm B? Consider caches, indexes, extracted text, error messages, background jobs, exports, report generation, and any shared inference context.
2. **Record immutability (NFR-04, NFR-07, FR-27, FR-61, FR-21b):** can this change allow a protected record — evidence, a signed-off result, an issued report, an audit entry, an N/A decision — to be altered, deleted, backdated or created without the required approvals?
3. **Approval integrity (FR-32, FR-33, FR-44, FR-45):** can a two-person sign-off be satisfied by one person, or by the excluded party (the policy author, or the finding's original recorder)?
4. **Key exposure:** does this change create a path by which plaintext or key material could reach a log, a metric, an error message or a lower-privilege component?
5. **Residency (NFR-03):** does this change create a path by which data or metadata could leave the EU, including via a new sub-processor, a globally replicated service, or telemetry?
6. **Non-EU access:** does this change create a path by which a person outside the EU/EEA could reach production personal data (`cross-border-data-processing`)?
7. **AI mapping (FR-31, §6.2):** can uploaded WSP content influence model behaviour? Can model output take any action without human confirmation? Can a mapping be confirmed without the two required approvers? Could the change move measured accuracy below the 85% bar?

### Linking threats to tests

Every mitigated threat gets a stable identifier:

```
THREAT-T01  Cross-firm evidence read via a manipulated object identifier
  Mitigation: repository tenant scoping + row-level security + key encryption context
  Tests:      test_cross_firm_evidence_read_denied        (application)
              test_rls_blocks_cross_firm_select           (database)
              test_decrypt_wrong_encryption_context_fails (crypto)
  Detection:  DET-02 cross-firm access attempt alert
  Status:     Mitigated, verified <date>
```

The model then becomes traceable: any threat can be followed to the code that mitigates it, the test that proves it, and the detection that catches a bypass. That traceability is what makes the model credible in a customer security review.

### Validation — "did we do a good job?"

- **Independent penetration test** with the threat model supplied to the testers, scoped explicitly to include multi-tenancy isolation, before real client data is accepted (`secure-sdlc`). **[PROPOSED]**
- **Incident retrospectives** ask: "was this threat in the model? If not, why not?" Gaps found by incidents are the most valuable input available.
- **Coverage metrics:** proportion of trust boundaries modelled; proportion of mitigated threats with tests; proportion with detections.
- Recurring internal adversarial exercises and a bug-bounty programme are **[FUTURE]** — valuable, but recurring costs the PRD does not fund.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Threat modelling becomes a ritual | Effort spent, no risk reduced | Tie every threat to a test or a detection; measure that ratio; review models in retrospectives |
| The model goes stale as the architecture evolves | It describes a system that no longer exists | T1 per-change modelling; periodic T3 refresh; diagrams generated partly from infrastructure code where possible |
| Only security-minded people participate | Engineers do not internalise the threats; models miss implementation reality | Engineers lead T1; security facilitates T2; keep the checklist short enough to actually use |
| Focus on exotic threats, miss the boring ones | A real breach via a misconfiguration nobody modelled | Include configuration, operational and human threats explicitly |
| Privacy threats omitted | Weak impact assessment; supervisory finding | Privacy analysis mandatory for personal-data flows |
| AI threats modelled with pre-LLM frameworks | Prompt injection and output-handling threats missed | ATLAS and the OWASP LLM Top 10 mandatory for changes touching the mapping path |
| Accepted risks accumulate silently | Risk posture drifts without visibility | Accepted risks carry an owner and an expiry date; expired acceptances escalate |

## Trade-offs

- **Formal method vs. lightweight checklist.** Adoption dominates completeness — an unused rigorous method finds nothing. Recommendation: the tiered approach above. **[PROPOSED]**
- **Threat-modelling tooling vs. markdown and diagrams in the repository.** Tools add structure and reuse but also friction and licence cost. Recommendation: markdown templates alongside the code, with diagrams as Mermaid so they version and diff. **[PROPOSED]**
- **Modelling everything vs. risk-based scoping.** Recommendation: risk-based — trust boundaries and the seven questions define scope. **[PROPOSED]**
- **Publishing a sanitised threat model summary to customers.** A strong maturity signal, but the material is the Client's IP under CC-03 and its publication is the Client's decision. **[OPEN]**

## Design decisions

| ID | Decision | Classification |
|---|---|---|
| DD-24-01 | Three-tier programme: per-change checklist enforced in CI on designated paths, per-feature workshop, periodic system-wide refresh | **[PROPOSED]** |
| DD-24-02 | STRIDE per element for security, a privacy framework feeding the impact assessment, ATLAS and the OWASP LLM Top 10 for the mapping path, attack trees for the catastrophic scenarios | **[PROPOSED]** |
| DD-24-03 | The seven domain-specific questions are mandatory in every per-feature model | **[PROPOSED]** — anchored on NFR-01, NFR-03, NFR-04, NFR-07, FR-31, FR-32 |
| DD-24-04 | Every mitigated threat carries a stable identifier linked to specific tests and detections; the linkage ratio is a reported metric | **[PROPOSED]** |
| DD-24-05 | Threat models live in the repository as markdown with diagrams, versioned with the code they describe | **[PROPOSED]** |
| DD-24-06 | Accepted risks require a named owner and an expiry date; expiry escalates rather than lapsing silently | **[PROPOSED]** |
| DD-24-07 | Independent penetration test before real client data, with the threat model supplied to testers | **[PROPOSED]** |
| DD-24-08 | Every incident retrospective asks whether the threat was modelled; gaps feed the next refresh | **[PROPOSED]** |
| DD-24-09 | Publication of a sanitised threat model summary to customers | **[OPEN]** — CC-03 |

## References

- Adam Shostack, *Threat Modeling: Designing for Security*; the Threat Modeling Manifesto
- Microsoft STRIDE; OWASP Threat Modeling Cheat Sheet
- LINDDUN privacy threat modelling framework (https://linddun.org)
- MITRE ATT&CK Enterprise and Cloud matrices; MITRE ATLAS
- OWASP Top 10 for LLM Applications
- NIST SP 800-30 Rev. 1 — Guide for Conducting Risk Assessments
- Regulation (EU) 2016/679 (GDPR) Art. 25, 35; EDPB/WP29 Guidelines on DPIA

## Confidence level

**High** — the tiered programme, method selection, threat-to-test traceability, and the domain-specific question set, which is derived directly from the PRD's own hard requirements.

**Medium** — sustaining per-change discipline under delivery pressure. CI enforcement helps; leadership attention is the real control.
