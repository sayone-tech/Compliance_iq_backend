# Security Roadmap

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

Two delivery phases inside the MVP, plus a clearly separated post-MVP list that carries **no commitment**.

**Phase boundaries are gated by capability, not by calendar.** This document deliberately contains **no durations, no headcount assumptions and no budget figures** — the engagement is a fixed-price milestone contract (the fixed-price milestone engagement model) whose scope is defined by the PRD, and inventing a delivery schedule or a cost model here would misrepresent it.

---

## Phase 0 — Foundation

**Goal:** guardrails exist before any client data can be created.
**Exit gate:** a developer cannot create a resource outside the EU, cannot commit a secret, and cannot hold a production credential — because the system prevents it, not because policy says so.

| Workstream | Deliverables | Class | Doc |
|---|---|---|---|
| Cloud foundation | Account topology inside the Client-owned account; organisation guardrails denying non-EU regions, long-lived access keys and disabling of security services | **[PROPOSED]** implements the EU residency requirement, the confirmed cloud decision | [reference-cloud-architecture](reference-cloud-architecture.md), [network-security](supporting-topics/network-security.md) |
| Region decision | EU region selected against documented criteria and recorded | **[OPEN]** | [data-residency](data-residency.md) |
| Logging | Control-plane trail across all accounts and regions → write-only log archive with write-once retention; configuration and threat detection enabled | **[PROPOSED]** implements the immutable audit requirement | [audit-logging](audit-logging.md), [security-monitoring](security-monitoring.md) |
| Identity | Workforce identity provider deployed; strong second factors enrolled; conditional access including location policy for production | **[PROPOSED]** | [identity-and-access-management](identity-and-access-management.md) |
| Cryptography | Key hierarchy and policy templates, including deletion denial and retention preconditions; cryptographic control policy; crypto module skeleton with mandatory additional authenticated data | **[PROPOSED]** implements the encryption requirement | [encryption-architecture](encryption-architecture.md), [key-management](key-management.md) |
| Development | Repository with branch protection, signed commits, ownership rules, secret scanning and push protection; federated CI credentials; synthetic data fixture factory covering every the accepted evidence file type list type | **[PROPOSED]** | [secure-sdlc](secure-sdlc.md), [secrets-management](secrets-management.md), [secure-cicd](secure-cicd.md) |
| AI tooling governance | Managed developer AI tool settings deployed and **enforcement verified by test**; AI usage policy wording corrected per DD-05-01 | **[PROPOSED]** | [ai-governance](ai-governance.md) |
| Governance | Obligation register v1 traced to the PRD's stated requirements; named security owner; risk register opened | **[PROPOSED / OPEN on ownership]** | [regulatory-obligations](regulatory-obligations.md) |
| Legal | Delivery topology determined; if any part is non-EU, transfer position started | **[OPEN — LEGAL]** | [cross-border-data-processing](supporting-topics/cross-border-data-processing.md) |

**Key risk in this phase:** pressure to skip guardrails to get moving. Every day of delay here costs more later.

---

## Phase 1 — Secure MVP

**Goal:** the platform can hold real client data safely.
**Exit gate:** the go/no-go checklist in `deployment-recommendations` §11 is fully satisfied.

| Workstream | Deliverables | Class | Doc |
|---|---|---|---|
| **Tenant isolation** | Repository pattern; forced row-level security; per-firm key with firm-bound encryption context; cross-firm negative test matrix as a blocking CI gate | **[PRD REQUIRED]** The tenant isolation requirement, the encryption requirement | [document-confidentiality](document-confidentiality.md), [identity-and-access-management](identity-and-access-management.md) |
| **Access model** | Eight system roles; firm-role mapping; invitation-only accounts; phone-based second factor; two-Super-Admin rule; deactivate-never-delete; per-request authorisation with every decision audited | **[PRD REQUIRED]** the PRD's roles section, the access requirements | [identity-and-access-management](identity-and-access-management.md) |
| **Audit** | Canonical audit event schema including the originating device; redaction by construction with static-analysis enforcement; hash-chained writes to write-once storage; coverage tests per endpoint | **[PRD REQUIRED]** The permanent audit log requirement, the immutable audit requirement | [audit-logging](audit-logging.md) |
| **Retention and immutability** | Retention service with per-class six-year minimums; write-once retention with no delete path; amendment-not-edit for signed-off results; immutable issued reports; permanent WSP and mapping version history | **[PRD REQUIRED]** The non-deletable retention requirement, the amendment-not-edit requirement, the immutable issued report requirement, the permanent WSP version history requirement | [immutable-evidence-retention](immutable-evidence-retention.md) |
| Upload pipeline | Quarantine-scan-promote with multi-engine scanning, fail-closed; sandboxed processing account with no credentials and no egress; five-bucket topology; derivative registry; OCR handling | **[PROPOSED]** implements the accepted evidence file type list, the single WSP upload requirement | [secure-media-storage](secure-media-storage.md), [document-confidentiality](document-confidentiality.md) |
| **WSP mapping** | EU-resident inference; untrusted-content delimiting; schema-constrained output; deterministic span verification; human confirmation; two-person approval; override tagging; **evaluation harness gating the 85% bar** | **[PRD REQUIRED]** The advisory AI mapping requirement, the two-person mapping approval requirement, the mapping reversal requirement, the PRD's WSP mapping accuracy commitment, the PRD's mapping sign-off rules | [ai-governance](ai-governance.md) |
| Network | Three-tier network; private service endpoints; default-deny egress (staged); WAF (count then block); no bastions | **[PROPOSED]** | [network-security](supporting-topics/network-security.md) |
| Supply chain | Signed artefacts with provenance and attestations; admission verification; bill of materials with continuous re-evaluation; dependency pinning with cooldown; licence deny-list per the IP ownership term | **[PROPOSED]** | [supply-chain-security](supply-chain-security.md), [secure-cicd](secure-cicd.md) |
| Backup | Backup account isolation; immutable retention lock (staged); automated restore verification with decryption and chain assertions | **[PROPOSED]** protects the non-deletable retention requirement | [secure-backups](secure-backups.md) |
| Detection | Priority detections as code with tests, including the cross-firm and protected-record tripwires; canary records; log-source heartbeats | **[PROPOSED]** | [security-monitoring](security-monitoring.md) |
| Insider | Separation-of-duties matrix; dual authorisation on irreversible actions; session recording for break-glass; offboarding automation | **[PROPOSED]** | [insider-threat-protection](supporting-topics/insider-threat-protection.md) |
| Assurance | Data protection impact assessment; sub-processor list published; DPA executed; independent penetration test and remediation | **[PROPOSED]** The GDPR processor requirement | [regulatory-obligations](regulatory-obligations.md), [secure-sdlc](secure-sdlc.md) |
| Open decisions closed | Remediation Owner scope (the Remediation Owner view requirement/the Remediation Owner scope gap); Portal visibility (the Portal firm-visibility statement/the Portal system settings requirement); second-factor mechanism (the phone-based second factor requirement); inference provider; who may override a mapping (the mapping override initiation gap) | **[OPEN]** — **these block specific sprints** | [identity-and-access-management](identity-and-access-management.md), [ai-governance](ai-governance.md), [open-questions](open-questions.md) |

**Phase 1 is where the product's regulatory credibility is built.** Everything marked **[PRD REQUIRED]** above is non-negotiable before real client data.

---

## Post-MVP — proposed, not committed

Nothing below is in the PRD baseline. Each item requires Client approval and, for anything with a recurring cost, a commercial conversation. Listed in rough order of value for this product.

| Item | Why it would matter | Class | Doc |
|---|---|---|---|
| Firm-visible, exportable audit trail | Directly serves the permanent audit log requirement's stated purpose — proving process compliance to a regulator | **[PROPOSED]** | [audit-logging](audit-logging.md) |
| Firm-granular point-in-time restore | The restore firms will actually request; also an isolation safeguard | **[PROPOSED]** | [secure-backups](secure-backups.md) |
| Degraded modes, including an evidence-only read path | "You can always get your records out" is the product's core promise | **[PROPOSED]** | [disaster-recovery](disaster-recovery.md) |
| Recovery architecture beyond off-domain record copies | Depends entirely on the unresolved the open uptime-SLA question availability decision | **[OPEN]** | [disaster-recovery](disaster-recovery.md) |
| Entity pseudonymisation before inference | Improves the data-protection position at low quality cost | **[PROPOSED]** | [ai-governance](ai-governance.md) |
| ISO 27001 and SOC 2 Type II | Certification roadmap item places them on the roadmap; **the timeline is to be agreed with the Client and no date is assumed** | **[PRD REQUIRED as roadmap items / OPEN on timing]** | [regulatory-obligations](regulatory-obligations.md) |
| Continuous out-of-hours alert triage | Detection without response is decorative | **[OPEN]** | [security-monitoring](security-monitoring.md) |
| Everything in [Future and Optional Scope](future-scope/future-and-optional-scope.md) | Key custody tiers, external cryptographic anchoring, enclaves, post-quantum work, an external auditor role, customer single sign-on, and the rest | **[FUTURE]** | [future-and-optional-scope](future-scope/future-and-optional-scope.md) |

---

## Cross-cutting continuous activities

Cadences below are **recommendations**, not commitments; each has a cost and an owner that the PRD does not assign. **[PROPOSED / OPEN]**

| Activity | Recommended cadence | Owner |
|---|---|---|
| Automated restore verification | Frequent and automated — the highest value-per-euro control here | Automated |
| Obligation and control register review | Periodic | Security owner |
| Risk register review | Periodic; escalate anything with elevated residual risk | Security owner |
| Privileged access recertification | Periodic | Security owner |
| Vulnerability SLA reporting | Periodic | Engineering |
| Independent penetration test | Before real client data, then as agreed | External |
| Recovery exercise | As agreed once the recovery architecture is chosen | Engineering |
| Threat model refresh | Periodic, and on any major architectural change | Security + Engineering |
| Sub-processor reconciliation | Periodic | Security owner |
| Security awareness training | Periodic | People + Security |

---

## Items with genuine lead time

Flagged because they cannot be compressed, not because they are scheduled:

- **Legal opinions** on transfer position (if delivery is partly non-EU), erasure versus non-deletability, and any regime beyond GDPR. Weeks, and they gate contractual commitments.
- **Independent penetration test** — booking plus remediation time, and it gates accepting real client data.
- **Certification observation windows** — a Type II report requires a period of control operation that cannot be shortened. Relevant only once the certification roadmap item's timeline is agreed.
- **The open decisions listed in Phase 1.** Several of them block specific sprints, and two of them (the Remediation Owner view requirement/the Remediation Owner scope gap and the Portal firm-visibility statement/the Portal system settings requirement) are already flagged as unresolved in the PRD itself.
