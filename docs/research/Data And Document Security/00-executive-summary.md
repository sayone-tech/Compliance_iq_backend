# 00 — Executive Summary

**Subject:** Security architecture for an AI-powered compliance platform serving EU crypto-asset management firms, developed in India, operated in the EU.
**Date:** 2026-08-03 · **Status:** Research complete; decisions proposed, not yet ratified.

---

## The situation in one paragraph

You are building a system that concentrates the most sensitive records of multiple EU-regulated financial firms — KYC packs, audit evidence, board minutes, custody attestations, regulator correspondence — in one place, processes them with AI, and must prove years later that those records have not been altered. Your customers are supervised under MiCA and DORA; you are directly bound by GDPR as a processor and, on the reading this research recommends, by NIS2 as a cloud service provider. Development happens in a country with no GDPR adequacy decision. The architecture must make all of that safe, provable, and saleable.

## The four decisions that determine whether this works

Everything else in this research is supporting detail. These four are load-bearing.

**1. Key custody is the sovereignty control, not geography.**
"Our data is in Frankfurt" does not answer the question sophisticated buyers and supervisors actually ask: *who can produce plaintext under legal compulsion?* Per-tenant encryption keys, with customer-held keys available as a tier, answer it definitively. This single architectural choice simultaneously resolves the CLOUD Act objection, provides the technical supplementary measure that makes the India transfer defensible under *Schrems II*, enables crypto-shredding as the answer to the erasure-versus-immutability conflict, and becomes a premium product tier. **(ADR-003, ADR-005)**

**2. Zero standing human access to production, with India holding no production data path at all.**
Remote access from India to EU production personal data is a restricted transfer under GDPR Chapter V — viewing a log line from Kochi is a transfer. Standard Contractual Clauses alone are not sufficient for confidential regulated financial data given Indian lawful-access powers. The defensible answer is architectural: development and staging contain **synthetic data only**; production has **no standing human access for anyone**; the rare genuine emergency uses a dual-approved, EU-hosted, egress-disabled, session-recorded virtual desktop. This constrains the operating model more than any other decision here, and it requires funding EU-resident production on-call. **(ADR-006)**

**3. Evidence must be verifiable without trusting us.**
The product's core promise is records a regulator will accept years later. Object Lock in COMPLIANCE mode makes deletion impossible for any principal including root; hash chaining makes alteration detectable; and an **eIDAS qualified timestamp from an EU trust service provider** converts a technical claim into a *legal presumption* of integrity and time accuracy under Regulation (EU) 910/2014 Art. 41. Ship an open-source verifier so auditors check it themselves. This is the highest value-per-euro control in the entire architecture and it is also the product's competitive moat. **(ADR-007)**

**4. AI output is advisory, grounded, and deterministically verified.**
Two AI surfaces exist and must be governed separately: the developer tooling (which must never see customer data) and the product's inference path (which must). For the product path: document content enters prompts only through an EU-resident, no-training, no-retention channel; uploaded documents are treated as hostile input capable of prompt injection; every citation is verified **deterministically against the source document offset** before an assessment can be produced; and a named human must approve before anything becomes an evidence record. A hallucinated regulatory citation reaching a customer's audit file is among the most damaging things this platform could do. **(ADR-004, ADR-009, ADR-011)**

## Regulatory position

| Regime | Applies to us | Key consequence |
|---|---|---|
| **GDPR** | Directly (processor; controller for staff data) | DPIA mandatory; India transfer requires SCCs + TIA + technical supplementary measures; erasure resolved by crypto-shredding |
| **DORA** | Indirectly but completely, via mandatory customer contract terms (Art. 28–30) | Design as if it bound us directly. Assume every customer designates us as supporting a critical or important function |
| **MiCA** | To our customers; we enable their compliance | 5-year record retention (extendable to 7); our evidence integrity becomes part of their supervisory file |
| **NIS2** | Likely directly, as a cloud computing service | 24h early warning / 72h notification / 1 month final. Verify national scope with counsel — **open question A-1** |
| **CRA** | Only if we ship installable components | Gate every installable artefact behind a scoping review before it becomes an unplanned CE-marked product |
| **AI Act** | Directly, as an AI system provider | Expect limited-risk + Art. 50 transparency; document the classification and re-run it on material feature change |
| **eIDAS 2** | Optional, and strategically valuable | Qualified timestamps give evidence a legal presumption — take it |

The commercially decisive framing: **comply with DORA voluntarily.** It costs more up front and it is the only way to sell into tier-1 CASPs without a six-month security review per deal.

## Architecture in brief

AWS `eu-central-1` primary, `eu-north-1` warm standby. EKS with a Linkerd mesh (mTLS, SPIFFE identities), Aurora PostgreSQL with forced row-level security, S3 with per-tenant keys and Object Lock for evidence, Amazon Bedrock for EU-only inference, Cedar for per-request authorisation, GitOps deployment with signed and attested artefacts verified at admission.

**Five independent authorisation enforcement points** stand between a user and a document: policy sidecar, mesh identity, application repository scoping, database row-level security, and a KMS key policy requiring a matching tenant encryption context. Any one of them alone prevents cross-tenant disclosure. That redundancy is deliberate — cross-tenant disclosure is the failure mode that ends the company. **(ADR-008)**

Portability is engineered in (Kubernetes, PostgreSQL, S3 API, PKCS#11 abstraction) so an EU-sovereign deployment remains achievable, and so the EU Data Act and DORA exit-strategy obligations are satisfiable in practice rather than on paper.

## Top residual risks after all controls

| Risk | Residual | Why it stays elevated |
|---|---|---|
| Cross-tenant document disclosure | 10/25 | Catastrophic impact; five layers reduce likelihood but not consequence |
| Prompt injection producing a false compliance conclusion | 10/25 | No complete technical defence exists; adversarial documents evolve |
| Malicious or coerced insider exfiltration | 9/25 | Crypto-sector staff are a plausible target for well-funded actors |
| Unlawful EU→India transfer | 8/25 | Legally novel territory; depends on TIA acceptance |
| Compromised upstream dependency | 8/25 | Outside our control by definition |
| Ransomware | 8/25 | Immutable backups make loss unlikely; recovery *time* is the residual |
| Hallucinated citation reaching a customer filing | 8/25 | Mitigated by deterministic verification, but not to zero |
| Late or misclassified incident reporting | 8/25 | Three overlapping regimes with different clocks |

Full register in doc 37; full threat model in doc 32.

## What must be true before accepting real customer data

Twelve gate criteria are listed in doc 34 §11. The four that are most often skipped and most damaging to skip:

1. **Cross-tenant negative test matrix passing in CI**, every role × every action, no skipped tests.
2. **A restore actually performed** from an immutable backup, with measured timing.
3. **The evidence chain verified end to end**, including qualified timestamp validation.
4. **Zero standing production access confirmed by IAM audit** — not asserted by policy.

## Roadmap shape

| Phase | Duration | Gate |
|---|---|---|
| **0 — Foundation** | Weeks 1–6 | Guardrails prevent a developer from creating a non-EU resource, committing a secret, or holding a production credential |
| **1 — Secure MVP** | Weeks 7–20 | The doc 34 §11 go/no-go checklist fully satisfied; real customer data can be accepted |
| **2 — Enterprise readiness** | Months 6–12 | Pass a tier-1 CASP's DORA due diligence without a remediation cycle; ISO 27001 certified |
| **3 — Scale and sovereignty** | Months 12–24 | Hold-your-own-key tier live; post-quantum transit; SOC 2 Type II issued |

**Start immediately, because of lead time:** EU-resident on-call hiring (3–6 months), ISO 27001 (6–9 months), legal opinions on NIS2 scope and the transfer impact assessment (6–10 weeks).

## What this research recommends you decide first

Six questions block Phase 0 and need answers within weeks, not months:

1. Are we in NIS2 scope, and in which member state? *(counsel)*
2. Is the Transfer Impact Assessment conclusion defensible with our supplementary measures? *(EU + Indian counsel)*
3. What is the current status of the Indian DPDP Rules? *(Indian counsel)*
4. Will EU-resident production on-call be hired, contracted, or deferred? *(leadership — deferring keeps the highest-risk scenario live)*
5. Who is the accountable executive for ICT risk? *(leadership)*
6. Is a Head of Security funded, or fractional? *(leadership — this determines how much of the roadmap is realistically executable)*

Full list, with recommended defaults so nothing blocks while answers are obtained, in doc 36.

## Honest assessment of confidence

**High confidence** in the architecture: the isolation model, key hierarchy, evidence design, network and access controls, and CI/CD security are established practice for regulated multi-tenant workloads and map cleanly onto the DORA ICT risk management RTS (Commission Delegated Regulation (EU) 2024/1774).

**Medium confidence** in three areas that need verification before contractual commitment: the exact DORA incident-reporting time limits under the 2025 RTS/ITS; our NIS2 scope determination; and the AI Act classification of compliance-assessment AI. Each has a stated working assumption and a conservative default.

**This document is engineering and architecture research, not legal advice.** The regulatory analysis is careful and article-specific, but the transfer impact assessment, the NIS2 scope determination and the AI Act classification each require qualified counsel in the relevant jurisdictions before anything is contracted or represented to customers.

---

## Reading order

| If you are… | Read |
|---|---|
| An executive | This document, then 35 (roadmap) and 36 (open questions) |
| An architect | 30 (reference architecture), 33 (diagrams), 38 (ADRs), then the topic files |
| A security engineer | 32 (threat model), 31 (control matrix), then topics 06–15 |
| A compliance officer or DPO | 01 (obligations), 31 (control matrix), 03 (transfers), 15 (evidence retention), 37 (risks) |
| Preparing a customer security review | 31, 32, 34 §9, and the assurance pack list |
