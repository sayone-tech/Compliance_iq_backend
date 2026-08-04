# Data and Document Security — ComplianceIQ MVP

Security research set for **ComplianceIQ**: a two-application, multi-tenant B2B SaaS compliance testing platform for EU-licensed Crypto Asset Service Providers. It stores uploaded evidence files, test executions and results, findings, remediation records, compliance reports, staff governance records and an immutable audit log, and it uses AI to suggest mappings between a firm's Written Supervisory Procedures and regulatory Requirement IDs.

**Baseline:** [`docs/requirement-specification/PRD.md`](../../requirement-specification/PRD.md) — ComplianceIQ PRD v4.0 — is the **sole source of truth**. Where this research and the PRD disagree, the PRD wins. Unresolved PRD questions stay unresolved here.

**Regulatory scope:** MiCA and DORA are the **customer-domain** regulations the product serves. **GDPR** binds the platform's own processing, as a processor under a DPA (the GDPR processor requirement). NIS2, CRA, the AI Act, AMLR, TFR, eIDAS 2 and the EU Data Act are **adjacent or conditional** — none is confirmed applicable by the PRD, and none drives MVP architecture without legal confirmation and Client approval.

> Engineering and architecture research, not legal advice. The delivery-topology transfer position, the GDPR-erasure-versus-non-deletability conflict, and any determination under NIS2, the AI Act or the CRA each require qualified counsel before anything is contracted or represented to a customer. See [open-questions.md](open-questions.md).

---

## Confirmed scope of this set

The documents at the top level of this folder cover exactly the confirmed security scope for the MVP:

| Confirmed scope item | Covered by |
|---|---|
| EU-only storage of client data | [data-residency.md](data-residency.md) |
| AWS as the selected cloud provider | [reference-cloud-architecture.md](reference-cloud-architecture.md) · ADR-001 |
| Client-owned AWS account | [reference-cloud-architecture.md](reference-cloud-architecture.md) · ADR-001 |
| AES-256 at rest and TLS 1.3 in transit | [encryption-architecture.md](encryption-architecture.md) |
| Per-tenant encryption keys | [key-management.md](key-management.md) · [encryption-architecture.md](encryption-architecture.md) |
| Strong multi-tenant isolation | [document-confidentiality.md](document-confidentiality.md) · [identity-and-access-management.md](identity-and-access-management.md) |
| Immutable audit logging | [audit-logging.md](audit-logging.md) |
| Non-deletable evidence and signed-off records | [immutable-evidence-retention.md](immutable-evidence-retention.md) |
| MFA and least-privilege role enforcement | [identity-and-access-management.md](identity-and-access-management.md) |
| Secure document upload, malware inspection, sandboxed parsing | [secure-media-storage.md](secure-media-storage.md) |
| Secure backups and tested recovery — **SLA / RTO / RPO remain proposals only** | [secure-backups.md](secure-backups.md) · [disaster-recovery.md](disaster-recovery.md) |
| Human approval of AI-generated WSP mappings | [ai-governance.md](ai-governance.md) |
| Prompt-injection and hallucination controls specific to WSP mapping | [ai-governance.md](ai-governance.md) |
| Secure SDLC, secrets management, vulnerability scanning, supply-chain controls | [secure-sdlc.md](secure-sdlc.md) · [secrets-management.md](secrets-management.md) · [supply-chain-security.md](supply-chain-security.md) · [secure-cicd.md](secure-cicd.md) |
| EU residency checks for AI inference over customer documents | [data-residency.md](data-residency.md) · [ai-governance.md](ai-governance.md) |
| Incident monitoring and customer notification supporting DORA obligations | [security-monitoring.md](security-monitoring.md) · [regulatory-obligations.md](regulatory-obligations.md) |

Everything outside that list has been moved, not deleted:

- **[`supporting-topics/`](supporting-topics/)** — real MVP-relevant depth that sits outside the confirmed list: network security, Zero Trust enforcement, insider threat, data loss prevention, threat-modelling method, and the conditional cross-border analysis. The control matrix and threat model still reference these.
- **[`future-scope/`](future-scope/)** — nothing here is in the MVP: customer-managed encryption / HYOK, and the full deferred list (sovereignty tiers, post-quantum, eIDAS timestamping, Merkle anchoring, verifier CLI, bug bounty, ISO 27701, and the rest).

## Classification used throughout

| Label | Meaning |
|---|---|
| **[PRD REQUIRED]** | Explicitly required by the PRD. The requirement is named descriptively and quoted where the wording settles the point |
| **[PROPOSED]** | An implementation recommendation — reasonably necessary to deliver a PRD requirement, but not selected by the PRD |
| **[OPEN]** / **[OPEN — LEGAL]** | A stakeholder or legal decision is required. **No default is adopted** |
| **[FUTURE]** | Outside the MVP baseline. Indexed in [future-scope/future-and-optional-scope.md](future-scope/future-and-optional-scope.md), with no commitment attached |

**There is no "Accepted" status in this set.** No decision here has been approved by anyone other than where the PRD itself states it.

## Start here

| Document | For |
|---|---|
| **[executive-summary.md](executive-summary.md)** | Everyone. What the PRD fixes, the load-bearing points, regulatory position, top risks, what needs deciding |
| **[REVIEW-TRACEABILITY.md](REVIEW-TRACEABILITY.md)** | Reviewers. PRD traceability table, what was kept, deferred, removed or corrected, and the questions the PRD cannot answer |

## Topic documents

Each states what the PRD requires, what is proposed to implement it, what stays open, risks, trade-offs, design decisions (`DD-nn-nn`), references and confidence.

### Regulatory and residency
| Document | Core question |
|---|---|
| [regulatory-obligations.md](regulatory-obligations.md) | What binds the platform, what binds the customer, and what binds neither? |
| [data-residency.md](data-residency.md) | Does every copy, index, cache, log, key **and AI inference call** stay in the EU? |

### Development and AI governance
| Document | Core question |
|---|---|
| [secure-sdlc.md](secure-sdlc.md) | Which gates block, and which advise? |
| [secrets-management.md](secrets-management.md) | How do we reach zero long-lived credentials? |
| [supply-chain-security.md](supply-chain-security.md) | Do we know and verify what we ship and what we depend on? |
| [secure-cicd.md](secure-cicd.md) | Can a compromised pipeline reach production? |
| [ai-governance.md](ai-governance.md) | Human approval, the 85% UAT bar, prompt injection and hallucination — for WSP mapping specifically |

### Data protection and isolation
| Document | Core question |
|---|---|
| [document-confidentiality.md](document-confidentiality.md) | Does tenant isolation survive a single bug? |
| [encryption-architecture.md](encryption-architecture.md) | AES-256 and TLS 1.3 — applied where, and how does it stay agile? |
| [key-management.md](key-management.md) | Per-firm keys — and why key destruction cannot become a deletion route |
| [identity-and-access-management.md](identity-and-access-management.md) | Eight system roles, invitation-only accounts, phone-based MFA, least privilege |
| [secure-media-storage.md](secure-media-storage.md) | How is a hostile evidence upload scanned, parsed and served safely? |

### Records, resilience and detection
| Document | Core question |
|---|---|
| [audit-logging.md](audit-logging.md) | Is the log genuinely append-only for every principal, including administrators? |
| [immutable-evidence-retention.md](immutable-evidence-retention.md) | Do six-year, non-deletable records actually hold up? |
| [secure-backups.md](secure-backups.md) | Can ransomware reach the copies, and has a restore been proven? |
| [disaster-recovery.md](disaster-recovery.md) | What recovers, and what targets can honestly be committed to? **No RTO/RPO is proposed** |
| [security-monitoring.md](security-monitoring.md) | Which alerts matter, and what does customer incident notification require? |

## Consolidated deliverables

| Document | Contents |
|---|---|
| [reference-cloud-architecture.md](reference-cloud-architecture.md) | What the PRD fixes (AWS, EU data centre, Client-owned account), account topology, data plane, residency boundary — **region, compute platform, database engine, mesh, policy engine and AI provider deliberately unselected**, with selection criteria |
| [security-control-matrix.md](security-control-matrix.md) | 141 controls (A–K) mapped to the PRD requirements they serve, plus implementation, evidence, phase and priority |
| [threat-model.md](threat-model.md) | Assets, trust boundaries, actors, scored threat catalogue, attack trees, privacy threats, threat-to-test traceability |
| [architecture-diagrams.md](architecture-diagrams.md) | 11 Mermaid diagrams, each mapped to a confirmed scope item: context, account topology, evidence access path, upload pipeline, WSP mapping pipeline, key hierarchy, CI/CD zones, record integrity chain, backup and recovery, record lifecycle, incident handling |
| [deployment-recommendations.md](deployment-recommendations.md) | Build order, staged rollout of irreversible controls, what to measure before committing, go/no-go criteria (the PRD's systems and IT risk section) |
| [security-roadmap.md](security-roadmap.md) | Two MVP phases gated by capability — **no durations, no headcount, no budget figures** — plus an explicitly uncommitted post-MVP list |
| [open-questions.md](open-questions.md) | Questions this research cannot settle, grouped by owner. Interim engineering positions are marked as **not decisions** |
| [risk-register.md](risk-register.md) | Scored risks with owners given as **roles to be assigned**. **No risk has been accepted by anyone** |
| [architecture-decision-records.md](architecture-decision-records.md) | 14 ADRs. Status vocabulary is PRD REQUIRED / PROPOSED / OPEN — STAKEHOLDER DECISION REQUIRED / FUTURE. **No ADR is "Accepted"** |

## The load-bearing points

1. **Non-deletability is a PRD requirement, and it is the hardest constraint here.** The non-deletable retention requirement, the immutable audit requirement and the PRD's data and retention table mean no deletion path for any principal — and **key destruction must be blocked as a route around it**. Crypto-shredding, deletion sagas and soft-delete grace periods are **not adopted**. (ADR-004, ADR-005, ADR-012)
2. **Tenant isolation must survive a single bug.** Layered enforcement on the path to evidence plaintext, with a cross-firm negative test matrix as a blocking CI gate. (ADR-003, ADR-010)
3. **The AI feature is WSP-to-rule mapping, it is advisory, and it carries a contractual 85% UAT accuracy number.** Human confirmation and two-person approval are PRD rules, not design choices. The platform makes no automated compliance decisions. (ADR-007, ADR-009)
4. **Backups, recovery and availability are proposals.** A restore must be proven; no SLA, RTO or RPO figure is committed anywhere. (ADR-013)
5. **Region, stack, recovery targets and certification dates are not decided.** Selection criteria are given; selections are not. (reference-cloud-architecture, disaster-recovery, architecture-decision-records)

## Conventions

- `DD-nn-nn` — design decision, defined in the topic document whose old number was `nn`, each carrying a classification label.
- `A-01`…`K-nn` — controls in [security-control-matrix.md](security-control-matrix.md).
- `T-nn` — threats in [threat-model.md](threat-model.md).
- `R-nn` — risks in [risk-register.md](risk-register.md).
- `ADR-001`…`ADR-014` — decision records in [architecture-decision-records.md](architecture-decision-records.md).
- **PRD requirements are named descriptively, never by ID** — "the encryption requirement", "the advisory AI mapping requirement", "the confirmed cloud decision", "the non-deletable retention requirement", "the Portal firm-visibility statement". PRD requirement IDs and section numbers change between PRD versions, so quoting them here would rot. The **only** place that binds these names to PRD v4.0 IDs is [REVIEW-TRACEABILITY.md §0](REVIEW-TRACEABILITY.md). When a new PRD version lands, that one table is the only thing to update.
- Section references of the form `` `document-name` §N `` point at a section of that research document, not at the PRD.

Cross-references are bidirectional: every control traces to a PRD requirement and a threat; every mitigated threat traces to a test and a detection.

## Maintenance

The PRD does not staff this project. Owners below are **roles to be assigned** ([open-questions.md](open-questions.md), P-9) — not people, titles or functions asserted to exist. Cadences are **recommendations**, not commitments.

| Artefact | Recommended cadence | Owner (to assign) |
|---|---|---|
| Obligation register | Periodic | Security owner |
| Control matrix | Per phase gate | Security owner |
| Threat model | Periodic, on material change, and post-incident | Security + Engineering |
| Risk register | Periodic | Security owner |
| Open questions | Periodic; answered items move to the decision records **only with a real, named approval** | Security owner |
| Decision records | On decision; superseded rather than edited | Security owner |
