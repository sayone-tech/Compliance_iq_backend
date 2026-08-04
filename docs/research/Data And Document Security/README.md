# Security Architecture Research — AI Compliance Platform for EU Crypto-Asset Managers

Research set covering data and document security for a multi-tenant SaaS platform storing uploaded documents, audit evidence, compliance reports, customer records and AI-generated assessments for EU-regulated crypto-asset management firms. Development in India; production serving EU customers.

**Regulatory scope:** MiCA · DORA · GDPR · NIS2 · Cyber Resilience Act · (adjacent: AI Act, AMLR, TFR, eIDAS 2, EU Data Act)

**Date:** 2026-08-03 · **Status:** Research complete; decisions proposed, not ratified.

> This is engineering and architecture research, not legal advice. The transfer impact assessment, NIS2 scope determination and AI Act classification each require qualified counsel before anything is contracted or represented to customers. See `36-open-questions.md`.

---

## Start here

| Document | For |
|---|---|
| **[00 — Executive Summary](00-executive-summary.md)** | Everyone. The four load-bearing decisions, regulatory position, top risks, roadmap shape |

## Research topics

Each topic provides: best practices · EU regulatory implications · recommended architecture · risks · trade-offs · design decisions · references · confidence level.

### Regulatory and jurisdictional
| # | Topic | Core question |
|---|---|---|
| [01](01-regulatory-obligations.md) | Regulatory obligations | What binds us directly, and what flows through customer contracts? |
| [02](02-data-residency.md) | Data residency | Where does every copy, index, cache, log and key actually live? |
| [03](03-cross-border-data-processing.md) | Cross-border data processing (EU ⇄ India) | How is offshore development made lawful and safe? |

### Development and AI governance
| # | Topic | Core question |
|---|---|---|
| [04](04-secure-sdlc.md) | Secure software development lifecycle | Which gates block, and which advise? |
| [05](05-ai-assisted-development-governance.md) | AI-assisted development governance | How are the two AI surfaces governed differently? |

### Data protection
| # | Topic | Core question |
|---|---|---|
| [06](06-document-confidentiality.md) | Document confidentiality | How does tenant isolation survive a single bug? |
| [07](07-encryption-architecture.md) | Encryption architecture | What is encrypted, with what, and how does it stay agile? |
| [08](08-key-management.md) | Key management | Who can produce plaintext under legal compulsion? |
| [09](09-secrets-management.md) | Secrets management | How do we get to zero long-lived credentials? |

### Access and network
| # | Topic | Core question |
|---|---|---|
| [10](10-identity-and-access-management.md) | Identity and access management | How is standing privilege eliminated? |
| [11](11-network-security.md) | Network security | How is exfiltration prevented at the network layer? |
| [12](12-zero-trust-architecture.md) | Zero Trust architecture | How does no access decision depend on network position? |

### Storage, evidence and resilience
| # | Topic | Core question |
|---|---|---|
| [13](13-secure-media-storage.md) | Secure media storage | How is a hostile uploaded file handled safely? |
| [14](14-audit-logging.md) | Audit logging | Can a breach be scoped within 72 hours? |
| [15](15-immutable-evidence-retention.md) | Immutable evidence retention | Will a regulator accept this record in 2033? |
| [16](16-disaster-recovery.md) | Disaster recovery | What actually recovers, how fast, and has it been tested? |

### Threat, supply chain and pipeline
| # | Topic | Core question |
|---|---|---|
| [17](17-insider-threat-protection.md) | Insider threat protection | What can a privileged insider reach at all? |
| [18](18-supply-chain-security.md) | Supply chain security | Do we know and verify what we ship and who we depend on? |
| [19](19-secure-cicd.md) | Secure CI/CD | Can a compromised pipeline reach production? |

### Customer controls and detection
| # | Topic | Core question |
|---|---|---|
| [20](20-customer-managed-encryption.md) | Customer-managed encryption | What exactly does the customer control, and at what cost? |
| [21](21-secure-backups.md) | Secure backups | Can ransomware reach the backups? Has a restore been proven? |
| [22](22-security-monitoring.md) | Security monitoring | Which few alerts actually matter, and who reads them at 3am? |
| [23](23-data-loss-prevention.md) | Data loss prevention | Which exfiltration paths were eliminated, not just watched? |
| [24](24-threat-modelling.md) | Threat modelling | How does threat modelling stay a habit rather than a document? |

## Consolidated deliverables

| Document | Contents |
|---|---|
| [30 — Reference Cloud Architecture](30-reference-cloud-architecture.md) | Account topology, data plane, component decisions, critical paths, residency boundary, cost shape |
| [31 — Security Control Matrix](31-security-control-matrix.md) | ~120 controls (A–K) mapped to regulation, implementation, evidence, phase and priority |
| [32 — Threat Model](32-threat-model.md) | Assets, trust boundaries, actors, 38 scored threats, attack trees, LINDDUN privacy threats, threat-to-test traceability |
| [33 — Architecture Diagrams](33-architecture-diagrams.md) | 12 Mermaid diagrams: context, network, access path, upload, AI pipeline, keys, zones, CI/CD, evidence chain, DR, lifecycle, incident clocks |
| [34 — Deployment Recommendations](34-deployment-recommendations.md) | Build order, staged rollout of irreversible controls, benchmarks, certification sequencing, go/no-go checklist |
| [35 — Security Roadmap](35-security-roadmap.md) | Four phases with gates, continuous activities, long-lead items, indicative budget |
| [36 — Open Questions](36-open-questions.md) | 40 unresolved questions with recommended defaults, grouped by owner and deadline |
| [37 — Risk Register](37-risk-register.md) | 40 scored risks plus 6 accepted risks, with owners and review cadence |
| [38 — Architecture Decision Records](38-architecture-decision-records.md) | 13 ADRs for the hard-to-reverse decisions, with reversibility ratings |

## The four load-bearing decisions

1. **Key custody, not geography, is the sovereignty control.** Per-tenant keys; customer-held keys as a tier. (ADR-003, ADR-005)
2. **Zero standing production access; India has no production data path.** Synthetic data only outside production. (ADR-006)
3. **Evidence verifiable without trusting us.** Object Lock COMPLIANCE + hash chain + eIDAS qualified timestamps + open-source verifier. (ADR-007)
4. **AI output is advisory, grounded and deterministically verified.** Citation offsets checked in code; named human approval mandatory. (ADR-004, ADR-011)

## Conventions

- `DD-nn-nn` — design decision, defined in topic document `nn`.
- `A-01`…`K-20` — controls in the security control matrix (doc 31).
- `T-01`…`T-38` — threats in the threat model (doc 32).
- `R-01`…`R-40`, `RA-01`…`RA-06` — risks and accepted risks in the register (doc 37).
- `ADR-001`…`ADR-013` — architecture decision records (doc 38).

Cross-references are bidirectional: every control traces to an obligation and a threat; every mitigated threat traces to a test and a detection.

## Maintenance

| Artefact | Cadence | Owner |
|---|---|---|
| Obligation register (doc 01) | Quarterly | Compliance Lead + Head of Security |
| Control matrix (doc 31) | Per phase gate | Head of Security |
| Threat model (doc 32) | Annual + per material change + post-incident | Security + Engineering |
| Risk register (doc 37) | Monthly (top risks), quarterly (full), board quarterly | Head of Security |
| Open questions (doc 36) | Quarterly; answered items move to ADRs | Head of Security |
| ADRs (doc 38) | On decision; superseded rather than edited | CTO |
