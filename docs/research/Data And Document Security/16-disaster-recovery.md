# 16 — Disaster Recovery

## Best practices

- **Set RTO/RPO from business impact analysis, then engineer to them.** Working backwards from a number someone liked is how you get an expensive architecture that still fails the actual scenario.
- **Test by doing, not by documenting.** An untested DR plan is a hypothesis. Regulators increasingly ask for evidence of *executed* tests with measured results, not plan documents.
- **Design for the scenarios that actually happen:** ransomware, accidental destructive change, a bad deployment, a corrupted migration, a compromised credential deleting resources, a dependency outage. Full region loss is the rarest and the one most DR plans over-index on.
- **Restore is the hard part.** Backups succeed routinely; restores fail routinely. Measure restore time and restore *correctness*, not backup job success.
- **Separate the failure domains.** Backups must not be deletable with the same credentials that manage production, must not live in the same account, and must not depend on the same key.
- **Graceful degradation beats binary availability.** Read-only mode preserving document access is far more valuable to a compliance officer mid-audit than a hard outage.

## EU regulatory implications

- **DORA Art. 11 — ICT business continuity policy.** Requires a documented policy, business impact analysis, response and recovery plans, and — importantly — that plans are **tested at least annually** and after substantive changes, including switchover to backup facilities. Crisis communication plans are explicitly required (Art. 14).
- **DORA Art. 12 — backup policies and recovery methods.** Requires backup policies specifying scope and frequency based on criticality and confidentiality; restoration procedures; and that backup systems are **physically and logically segregated** from the source system. It further requires that restoration testing does not jeopardise production, and that redundant capacity is sufficient to ensure business needs.
- **DORA Art. 11(6)** — for financial entities, testing of continuity plans must include scenarios of switchover to redundant capacity and back. Expect customers to require evidence of our equivalent.
- **DORA Art. 12(3)** — where recovery uses a secondary site, it must be geographically separate with a risk profile sufficiently distinct from the primary. This is why multi-AZ alone is insufficient; a second EU region is required.
- **MiCA Art. 68** — business continuity as part of sound governance; loss of records is a records-retention failure under Art. 68(9), not just downtime.
- **NIS2 Art. 21(2)(c)** — business continuity, including backup management and disaster recovery, and crisis management.
- **GDPR Art. 32(1)(c)** — the ability to restore availability and access to personal data in a timely manner in the event of a physical or technical incident. **Art. 32(1)(d)** — a process for regularly testing and evaluating effectiveness. Availability loss can itself be a notifiable personal data breach.
- **Data residency (doc 02)** — the DR region must be in the EU/EEA. No emergency exceptions.

## Recommended architecture

### Objectives by service tier

| Tier | Services | RTO | RPO | Strategy |
|---|---|---|---|---|
| **T1 — Critical** | Document read, evidence retrieval, authentication | **4 hours** | **15 minutes** | Warm standby in `eu-north-1` |
| **T2 — Important** | Document upload, assessment generation, reporting | **12 hours** | **1 hour** | Warm standby, scaled down |
| **T3 — Standard** | Analytics, admin console, batch jobs | **48 hours** | **24 hours** | Backup and restore |
| **T4 — Deferrable** | Internal tooling, reporting dashboards | **5 days** | **24 hours** | Rebuild from IaC |

Rationale for T1: a compliance officer mid-regulatory-response who cannot retrieve evidence is in a materially worse position than one who cannot upload a new document. Read paths recover first.

### Strategy: warm standby (pilot light plus)

```
PRIMARY: eu-central-1                    SECONDARY: eu-north-1
─────────────────────                    ──────────────────────
EKS cluster (full scale)      ────────▶  EKS cluster (minimum nodes, all deployments
                                          present at replica count 0–1)
Aurora PostgreSQL             ────────▶  Aurora Global Database secondary
  (Multi-AZ, 3 AZs)                       (typical replica lag < 1s; promotion in ~1 min)
S3 primary/evidence buckets   ────────▶  Cross-Region Replication (RTC: 99.99% within
                                          15 min), Object Lock retained on replica
KMS per-tenant CMKs           ────────▶  Multi-Region keys for backup/evidence CMKs
Secrets Manager               ────────▶  Replicated secrets
Route 53                      ────────▶  Health-check-based failover (manual approval gate)
IaC (Terraform/OpenTofu)      ────────▶  Same modules, region parameterised
```

- **Failover is a deliberate, approved action**, not automatic. Automatic cross-region failover on a transient health-check blip causes split-brain and data divergence — worse than the outage. Automation prepares everything; a human with dual approval pulls the trigger, with a documented decision threshold.
- **Aurora Global Database** gives sub-second replication and fast promotion, at roughly the cost of a second cluster's storage and replication I/O. This is the single largest DR line item and it is what buys the 15-minute RPO for T1.

### Backup strategy (defence against ransomware and destructive error)

| Layer | Mechanism | Retention | Isolation |
|---|---|---|---|
| Continuous | Aurora backtrack / PITR | 35 days | Same account, protects against logical error |
| Daily snapshot | AWS Backup → **separate backup account** | 35 days | Cross-account; production credentials cannot delete |
| Weekly snapshot | AWS Backup → backup account + copy to `eu-north-1` | 12 weeks | Cross-account + cross-region |
| Monthly | AWS Backup with **Vault Lock in compliance mode** | 12 months | **Immutable — deletable by nobody, including root** |
| Annual | Vault Lock, cold storage | 7 years | Immutable, matches MiCA retention |
| Object storage | S3 versioning + CRR + Object Lock on evidence | Per retention policy | Cross-region, WORM |

- **AWS Backup Vault Lock in compliance mode is the anti-ransomware control.** Once locked, the retention cannot be shortened and backups cannot be deleted by any principal. Set it up carefully — like S3 Object Lock COMPLIANCE, mistakes are permanent — and test in governance mode first.
- **Separate backup account** with no trust relationship allowing production roles to delete. The blast radius of a fully compromised production account must not include the backups.
- **Backup encryption** uses a dedicated backup CMK (doc 08), multi-region, with deletion denied in the key policy. Note the interaction: crypto-shredding a tenant key makes their data in backups unreadable, which is the intended erasure mechanism (doc 15) — this must be understood before anyone treats key deletion as reversible.

### Testing programme (this is what regulators actually inspect)

| Test | Frequency | Scope | Evidence produced |
|---|---|---|---|
| Automated restore verification | **Daily** | Restore a random database snapshot to an isolated environment, run integrity checks and a data-consistency suite | Automated report to evidence store |
| Component failover | Monthly | AZ failure simulation, pod eviction, node drain, dependency failure injection | Test record with measured recovery time |
| Regional failover (full) | **Semi-annual** | Complete failover to `eu-north-1`, run production-equivalent load, **fail back** | Formal DR test report, timings vs. RTO/RPO |
| Ransomware / destructive-action scenario | Annual | Restore from immutable vault assuming production and its credentials are fully compromised | Test report; feeds incident response |
| Crisis communication | Annual | Tabletop with executives, including customer and regulator notification drafting | Tabletop report (DORA Art. 14) |
| Key-unavailability scenario | Annual | KMS regional impairment; customer-managed key revoked | Documented degraded-mode behaviour |

Every test produces a sealed evidence record (doc 15) with measured RTO/RPO against target. Deviations become findings with owners and dates. **This evidence pack is what customers request during DORA due diligence** — it is a sales asset, not just a compliance artefact.

### Degraded operating modes

Define and implement explicitly, rather than discovering them under pressure:

1. **Read-only mode** — document and evidence retrieval works; uploads, assessments and edits are disabled. Triggered by database primary failure or capacity loss.
2. **AI-degraded mode** — inference provider unavailable; assessments queue and the UI states clearly that AI generation is delayed. Everything else functions. (Also the DORA Art. 12 concentration-risk answer for the AI dependency.)
3. **Key-degraded mode** — customer-managed key unavailable; that tenant is read-blocked with a clear message and an alert to the customer's admin; other tenants unaffected.
4. **Evidence-only mode** — extreme scenario; a standalone read path serving the evidence bucket directly, so customers can always retrieve their records for a regulator even if the application tier is unavailable. Cheap to build and disproportionately valuable.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Backups exist but restore has never been tested at full scale | Discover during a real disaster that restore takes 3 days | Daily automated restore verification; semi-annual full regional failover |
| Ransomware encrypts production *and* backups | Total loss | Vault Lock compliance mode, separate backup account, cross-region copies, immutable evidence store |
| DR region lacks a service used in primary | Failover fails at the worst moment | Service-parity check in CI against the DR region; no service adopted without DR-region availability |
| Failover automation causes split-brain | Data divergence, corrupted records — worse than downtime | Manual approval gate; fencing on promotion; documented decision threshold |
| Cross-region replication lag exceeds RPO undetected | Silent data loss on failover | Continuous replication-lag monitoring with alerting at 50% of RPO budget |
| Customer-managed key (T2/T3) unavailable during DR | Cannot decrypt that tenant's data even after successful failover | Multi-region customer keys required contractually for T2/T3; documented in the tier terms |
| Vault Lock misconfigured with an excessive retention | Unbounded, unremovable storage cost | Governance-mode trial period; retention derived from the policy engine |
| DR runbook depends on a person, a laptop, or a system that is also down | Recovery blocked | Runbooks in an independently-accessible store; break-glass credentials offline; contact tree printed |
| Failback never tested; system runs indefinitely in the DR region | Degraded capacity, residency and cost surprises | Failback is a mandatory part of every regional test |

## Trade-offs

- **Warm standby (~35–45% of primary infrastructure cost) vs. backup-and-restore (~10%, RTO measured in days) vs. active-active (~200%, near-zero RTO, complex consistency).** For a compliance platform, hours of downtime are tolerable; days are not; and active-active multi-region PostgreSQL introduces correctness risk that outweighs its benefit. **Recommendation: warm standby.**
- **Aurora Global Database (sub-second RPO, significant cost) vs. cross-region snapshot copies (RPO measured in hours, cheap).** **Recommendation: Global Database. The 15-minute T1 RPO is the commitment that makes the platform credible for evidence retention, and it is the single most defensible DR investment.**
- **Manual failover approval (safe, adds minutes to RTO) vs. automatic (fast, split-brain risk).** **Recommendation: manual with a 15-minute decision SLA and pre-approved criteria — automation does everything except the final trigger.**
- **Vault Lock compliance mode (ransomware-proof, permanent) vs. governance mode (recoverable, defeatable).** **Recommendation: compliance mode for monthly and annual backups; governance mode for daily/weekly to retain operational flexibility.**
- **Semi-annual full DR test (strong evidence, 1–2 engineer-weeks each) vs. annual.** DORA requires at least annual; customers increasingly ask for more. **Recommendation: semi-annual, with the second test doubling as customer-facing assurance evidence.**
- **Building the evidence-only read path (extra component to maintain) vs. relying on the main application.** **Recommendation: build it. It is small, and "you can always get your records out" is a powerful contractual and marketing position.**

## Design decisions

- **DD-16-01:** Four service tiers with distinct RTO/RPO: T1 4h/15min, T2 12h/1h, T3 48h/24h, T4 5d/24h. Read paths recover before write paths.
- **DD-16-02:** Warm standby in `eu-north-1` with Aurora Global Database, S3 Cross-Region Replication with Replication Time Control, multi-region backup/evidence CMKs, and identical IaC.
- **DD-16-03:** Failover requires human dual approval against pre-defined criteria with a 15-minute decision SLA; all preparatory steps are automated.
- **DD-16-04:** Backups stored in a separate AWS account; monthly and annual backups protected by AWS Backup Vault Lock in compliance mode.
- **DD-16-05:** Daily automated restore verification into an isolated environment with data-integrity assertions; failures are P1.
- **DD-16-06:** Semi-annual full regional failover **and failback** test, plus annual ransomware-scenario and crisis-communication exercises. Every test produces a sealed evidence record with measured results.
- **DD-16-07:** Four explicit degraded modes implemented and tested: read-only, AI-degraded, key-degraded, evidence-only.
- **DD-16-08:** No service is adopted into the architecture unless it is available in the DR region; enforced at design review and by an automated parity check.
- **DD-16-09:** DR runbooks, contact trees and break-glass credentials stored independently of the primary environment and verified quarterly.
- **DD-16-10:** T2/T3 customer-managed keys must be multi-region as a contractual condition of those tiers.

## References

- Regulation (EU) 2022/2554 (DORA) Art. 11, 12, 14; Commission Delegated Regulation (EU) 2024/1774
- Regulation (EU) 2016/679 (GDPR) Art. 32(1)(c)/(d)
- Directive (EU) 2022/2555 (NIS2) Art. 21(2)(c)
- Regulation (EU) 2023/1114 (MiCA) Art. 68
- ISO 22301:2019 — Business Continuity Management Systems
- NIST SP 800-34 Rev. 1 — Contingency Planning Guide for Federal Information Systems
- AWS Backup Vault Lock; Aurora Global Database; S3 Cross-Region Replication and Replication Time Control
- AWS Well-Architected Framework — Reliability Pillar; Disaster Recovery of Workloads on AWS whitepaper

## Confidence level

**High** — the tiering model, warm-standby strategy, immutable backup layering, manual-failover decision, and the testing programme. These map directly onto DORA Art. 11/12 and are standard practice for regulated workloads.

**Medium** — whether a 4-hour T1 RTO is achievable in practice on first attempt (it usually is not; measure and iterate), and the true cost of Aurora Global Database at eventual data volumes. Both need validation in the first regional failover test, and RTO commitments to customers should not be contracted until measured twice.
