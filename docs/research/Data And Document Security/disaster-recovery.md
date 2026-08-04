# Disaster Recovery

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

## What the PRD says, and what it does not

| PRD ref | Statement |
|---|---|
| Availability target | "The platform targets **99.5% availability** (approximately 44 hours per year). Planned maintenance windows are communicated in advance." |
| Open uptime-SLA question | "Uptime SLA: Is 99.5% availability sufficient, or do clients require 99.9%? — **Still open — estimation blocker**" |
| Non-deletable retention requirement, the PRD's data and retention table | Records must survive: minimum six years, non-deletable. **Losing records is a worse outcome than downtime for this product** |
| Resilience test report storage requirement | The platform *stores* firms' own BCP and DR test reports. That is a product feature, not a statement about the platform's own recovery |

**The PRD sets no RTO, no RPO, no recovery architecture and no DR obligation on the platform.** It states an availability *target*, and records the target itself as an open question.

Therefore: **no recovery time or recovery point objective appears in this document as a commitment.** None is proposed as a number. What follows is the shape of a recovery capability and the process for setting targets, which is a Client decision informed by measurement.

## Best practices

- **Set recovery targets from business impact, then engineer to them.** Working backwards from a number someone liked produces an expensive architecture that still fails the actual scenario.
- **Test by doing, not by documenting.** An untested plan is a hypothesis.
- **Design for the scenarios that actually happen:** ransomware, an accidental destructive change, a bad deployment, a corrupted migration, a compromised credential, a dependency outage. Full region loss is the rarest and the one most plans over-index on.
- **Restore is the hard part.** Backups succeed routinely; restores fail routinely. Measure restore *time* and restore *correctness*.
- **Separate the failure domains.** Backups must not be deletable by the credentials that manage production, must not live in the same account, and must not depend on the same key.
- **Graceful degradation beats binary availability.** For a compliance officer mid-audit, read-only access to evidence is far more valuable than a hard outage.

## Regulatory implications

- **GDPR Art. 32(1)(c)** — the ability to restore availability and access to personal data in a timely manner after an incident. **Art. 32(1)(d)** — a process for regularly testing and evaluating effectiveness. Availability loss can itself be a notifiable breach.
- **The non-deletable retention requirement** — record survival is a hard requirement independent of any availability target. A recovery design that could lose records breaches it.
- **Delegated Reg. (EU) 2024/1774 / DORA Art. 11–12** (customer-side) — continuity policy, backup policy with scope and frequency driven by criticality *and confidentiality*, restoration procedures, segregation of backup systems from source systems, periodic restoration testing, and geographic separation where a secondary site is used. Customers will ask about the platform's equivalent; used here as a **design reference**.
- **Residency (`data-residency`)** — any recovery location must be in the EU/EEA (the EU residency requirement). **No emergency exceptions.**

## Recommended architecture

### Recovery priority, without committing to numbers **[PROPOSED]**

Order of restoration, derived from what the product is for:

| Priority | Capability | Why first |
|---|---|---|
| **1** | Read access to evidence, reports and audit records; authentication | A firm responding to a regulator that cannot retrieve its evidence is in a materially worse position than one that cannot upload a new file. This also protects the non-deletable retention requirement promise |
| **2** | Evidence upload, test execution, WSP mapping, report generation | The day-to-day work |
| **3** | Dashboards, analytics, regulatory news feed, Platform Admin Portal content authoring | Deferrable for hours |
| **4** | Internal tooling and reporting | Rebuildable from infrastructure code |

**Target recovery times and recovery points for each priority band require Client approval and must be measured before they are contracted.** See `deployment-recommendations` §7. **[OPEN]**

### Recovery strategy — options, not a selection

| Option | Cost shape | Recovery characteristics | Notes |
|---|---|---|---|
| Backup and restore in the primary region | Lowest | Slowest; no protection against regional loss | May be adequate against a 99.5% target |
| Backup copies to a second EU region, restore on demand | Low–moderate | Protects records against regional loss; restore measured in hours to days | The minimum that protects the non-deletable retention requirement against a regional event |
| Warm standby in a second EU region | Moderate–high | Faster recovery; ongoing replication cost | Meaningful only if a tighter target is agreed |
| Active-active across regions | Highest | Near-zero interruption; real write-consistency risk | Not recommended for a system whose records must be provably unaltered |

**No option is selected.** The choice depends on the answer to the open uptime-SLA question and on the Client's cost tolerance. **[OPEN]** The recommendation this research does make: **whatever is chosen, record copies must exist outside the primary region's failure domain**, because record loss breaches the non-deletable retention requirement and cannot be remediated. **[PROPOSED]**

### Failover control **[PROPOSED]**

If a secondary environment exists, **failover is a deliberate, approved action, not an automatic one.** Automatic cross-region failover on a transient health-check blip causes divergence — worse than the outage, and for an immutable record store, potentially unrecoverable. Automation prepares everything; a human with dual approval triggers it, against documented criteria.

### Backup strategy

Covered in `secure-backups`. The two properties that matter here: **backups live in an account with no deletion path from production**, and **restores are verified automatically and continuously**.

### Testing programme **[PROPOSED]**

| Test | Scope | Evidence produced |
|---|---|---|
| Automated restore verification | Restore a recent snapshot into an isolated environment; assert schema, row counts, referential integrity, decryption with the firm key, and hash-chain verification on a sample of sealed records | Automated report into the immutable store |
| Component failure exercise | Availability-zone failure simulation, workload eviction, dependency failure injection | Test record with measured recovery time |
| Full recovery exercise | Complete restoration into a clean environment, running realistic load, then returning to normal operation | Formal report with measured timings |
| Ransomware / destructive-action scenario | Restore from immutable backup assuming production and its credentials are fully compromised | Test report feeding incident response |
| Crisis communication exercise | Tabletop including customer notification drafting | Tabletop report |

Cadence for each is a Client decision. **[OPEN]** The engineering recommendation: automated restore verification should run on a short cycle because it is cheap and it is the control most likely to prevent a catastrophic surprise; the larger exercises are expensive and their frequency should be agreed.

### Degraded operating modes **[PROPOSED]**

Define and implement these explicitly rather than discovering them under pressure:

1. **Read-only mode** — evidence, reports and audit records retrievable; uploads, test execution and edits disabled. Triggered by database primary failure or capacity loss.
2. **AI-degraded mode** — the inference path is unavailable; WSP mapping suggestions queue and the UI states clearly that suggestions are delayed. **Everything else works, including manual mapping** — which is possible precisely because the advisory AI mapping requirement makes the human the decision-maker.
3. **Evidence-only mode** — an extreme scenario: a standalone read path serving the evidence store directly, so a firm can always retrieve its records for a regulator even if the application tier is down. Cheap to build and disproportionately valuable for a product whose promise is the permanent record.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Backups exist but restore has never been tested at scale | Discovering during a real incident that restore takes days | Automated restore verification; a full recovery exercise before real customer data (`deployment-recommendations` §11) |
| Ransomware encrypts production **and** backups | Total loss of six-year records — an unrecoverable breach of the non-deletable retention requirement | Immutable backup vaults, separate backup account, copies outside the primary failure domain, write-once evidence storage |
| A secondary environment lacks a service used in the primary | Recovery fails at the worst moment | Service-parity check before adopting any service; no undocumented fallbacks |
| Failover automation causes divergence | Corrupted or forked records | Manual approval gate; fencing on promotion; documented decision threshold |
| Replication lag exceeds expectations undetected | Silent data loss on recovery | Continuous replication-lag monitoring with alerting well below any agreed tolerance |
| Recovery targets contracted before being measured | Immediate breach of a commitment | Measure twice before contracting (`deployment-recommendations` §7); the open uptime-SLA question is still open |
| Recovery environment outside the EU under pressure | Breach of the EU residency requirement | Region policy denies it technically, not just procedurally |
| Runbook depends on a person, a laptop or a system that is also down | Recovery blocked | Runbooks in an independently accessible store; break-glass credentials offline; contact tree printed |

## Trade-offs

- **Recovery investment vs. The availability target.** A 99.5% target permits roughly 44 hours of downtime a year and does not on its own justify a warm standby. A 99.9% target would. **the open uptime-SLA question is unresolved, so the investment question is unresolved.** Recommendation: cost both and put them to the Client together with the measured restore time. **[OPEN]**
- **Record durability vs. service availability.** These are separable, and for this product they should be separated. **Record durability is non-negotiable (the non-deletable retention requirement); service availability is a target with an open number (the availability target).** Recommendation: fund record durability first — off-region immutable copies — before funding faster service recovery. **[PROPOSED]**
- **Automated vs. manual failover.** Recommendation: manual, with pre-approved criteria and everything else automated. **[PROPOSED]**
- **Building the evidence-only read path vs. relying on the main application.** Recommendation: build it. It is small, and "you can always get your records out" is exactly what this product promises. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification | Basis |
|---|---|---|---|
| DD-16-01 | The platform's availability target is 99.5%, with planned maintenance communicated in advance | **[PRD REQUIRED]** | Availability target |
| DD-16-02 | Whether the target becomes 99.9%, and what recovery time and recovery point targets apply | **[OPEN]** | Open uptime-SLA question |
| DD-16-03 | Recovery priority order: record read access and authentication first, then day-to-day work, then reporting and Portal authoring, then internal tooling | **[PROPOSED]** | supports the non-deletable retention requirement |
| DD-16-04 | Record copies exist outside the primary region's failure domain, in the EU | **[PROPOSED]** | protects the non-deletable retention requirement; the EU residency requirement |
| DD-16-05 | Recovery architecture (backup-and-restore, warm standby, or other) is selected by the Client once targets and costs are known | **[OPEN]** | — |
| DD-16-06 | Failover, if a secondary environment exists, requires human dual approval against documented criteria; all preparatory steps automated | **[PROPOSED]** | — |
| DD-16-07 | Automated restore verification with integrity, decryption and chain assertions; failures are top severity | **[PROPOSED]** | `secure-backups` |
| DD-16-08 | Full recovery, ransomware-scenario and crisis-communication exercises are performed; cadence agreed with the Client | **[PROPOSED / OPEN]** | — |
| DD-16-09 | Three degraded modes implemented and tested: read-only, AI-degraded, evidence-only | **[PROPOSED]** | supports the non-deletable retention requirement, the advisory AI mapping requirement |
| DD-16-10 | No service is adopted unless it is available in whatever recovery location is chosen | **[PROPOSED]** | — |
| DD-16-11 | Runbooks, contact trees and break-glass credentials stored independently of the primary environment | **[PROPOSED]** | — |
| DD-16-12 | No recovery-time or recovery-point figure is committed to a customer until it has been measured in a full test | **[PROPOSED]** | `deployment-recommendations` §7 |

## References

- Regulation (EU) 2016/679 (GDPR) Art. 32(1)(c)/(d)
- Regulation (EU) 2022/2554 (DORA) Art. 11, 12, 14; Commission Delegated Regulation (EU) 2024/1774 *(design reference, customer-side)*
- ISO 22301:2019 — Business Continuity Management Systems
- NIST SP 800-34 Rev. 1 — Contingency Planning Guide
- AWS Well-Architected Framework — Reliability Pillar

## Confidence level

**High** — the recovery priority ordering, the separation of record durability from service availability, the manual-failover principle, and the testing programme shape.

**Not determined** — every recovery target, the recovery architecture itself, and the exercise cadence. These follow from the open uptime-SLA question and from cost decisions that belong to the Client, and this document deliberately proposes no numbers.
