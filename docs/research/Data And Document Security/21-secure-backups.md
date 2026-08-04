# 21 — Secure Backups

Doc 16 covers disaster recovery strategy and RTO/RPO. This document covers the backup system itself as a *security* asset: a complete, encrypted, restorable copy of every customer's confidential data, which is simultaneously the last line of defence and one of the most attractive targets in the architecture.

## Best practices

- **The 3-2-1-1-0 rule**, adapted: **3** copies, **2** media/storage classes, **1** off-site (different region), **1** immutable and offline-equivalent, **0** errors on verified restore. The "1 immutable" and the "0 verified errors" are the two that most organisations get wrong.
- **Backups must not be deletable by the credentials that manage production.** If compromising production also compromises backups, you have replication, not backup.
- **Backups inherit the confidentiality of the source.** A backup of a tenant's KYC documents is a tenant's KYC documents. Same classification, same key, same access control, same audit logging.
- **Verify restores automatically and continuously.** A backup that has never been restored is an untested hypothesis.
- **Design tenant-granular restore**, not only full-system restore. The most common real recovery request is "a customer deleted a document set by mistake" — not "the region is gone".
- **Encrypt with a key the backup system cannot delete**, and understand that this makes key destruction the erasure mechanism (doc 15).

## EU regulatory implications

- **DORA Art. 12(1)** — backup policies specifying the scope of data subject to backup and the **minimum frequency of backup, based on the criticality of information and the confidentiality level of the data**. Note: confidentiality level explicitly drives backup policy, not just criticality.
- **DORA Art. 12(2)** — backup systems must begin restoration using **their own systems, logically and physically segregated from the source ICT system**. This forbids a backup that depends on the production control plane.
- **DORA Art. 12(3)** — restoration and recovery procedures and methods; **Art. 12(4)** — testing of backups and restoration on a periodic basis; where restoration uses secondary infrastructure it must be geographically and risk-profile separate.
- **DORA Art. 12(6)** — where data must be reconstructed, additional checks and reconciliation must be performed to verify integrity.
- **GDPR Art. 32(1)(c)** — ability to restore availability and access to personal data in a timely manner. **Art. 32(1)(d)** — regular testing of effectiveness.
- **GDPR Art. 17** — erasure and immutable backups conflict; resolved by crypto-shredding plus honest disclosure of backup expiry timelines in the DPA (doc 15).
- **GDPR Art. 5(1)(e)** — backups have a retention limit too. Perpetual backups are a violation. The backup lifecycle must expire.
- **MiCA Art. 68(9)** — the 5–7 year record retention obligation is partly satisfied by the evidence store, but backup integrity supports the "durable medium" requirement.
- **NIS2 Art. 21(2)(c)** — business continuity including backup management.
- **Residency (doc 02)** — backup copies must remain in the EU/EEA. A cross-region copy to a non-EU region is a transfer.

## Recommended architecture

### Backup inventory (what actually needs backing up)

| Asset | Method | Frequency | Retention | Immutable copy |
|---|---|---|---|---|
| Aurora PostgreSQL (metadata, assessments, config) | Automated snapshots + PITR; AWS Backup to backup account | Continuous PITR; daily snapshot | 35d daily / 12w weekly / 12m monthly / 7y annual | Monthly + annual (Vault Lock) |
| S3 primary documents | Versioning + Cross-Region Replication; S3 Batch Replication for the initial sync | Continuous | Per retention policy engine | Evidence bucket: Object Lock COMPLIANCE |
| S3 evidence | Object Lock COMPLIANCE + CRR with lock retained on replica | Continuous | 7y | Inherent |
| OpenSearch indexes | Snapshot to S3 | Daily | 30d | No — **rebuildable from source**, deliberately not treated as a source of truth |
| Vector embeddings | Rebuildable from documents | — | — | No |
| Secrets Manager | Cross-region replication + AWS Backup | Daily | 90d | No |
| KMS key metadata | Not backup-able; keys are the root of trust | — | — | Multi-region keys for backup/evidence CMKs |
| IaC / configuration | Git (multiple remotes, including one in a separate provider) | Per commit | Indefinite | Git history + protected branches |
| Container images | ECR with immutable tags + cross-region replication | Per build | 2y | Immutable tags |
| Audit logs | Written directly to Object Lock storage — the primary copy *is* immutable | Continuous | 7y | Inherent |

Two useful principles visible in this table: (1) **derived data is rebuilt, not backed up** — this reduces the backup surface, cost and confidentiality exposure significantly; (2) **audit and evidence data is born immutable**, so it needs no separate backup regime beyond replication.

### Isolation architecture

```
prod account                    backup account                  DR region (eu-north-1)
────────────                    ──────────────                  ──────────────────────
Aurora, S3, EKS                 AWS Backup vaults               Copied vaults
     │                          Vault Lock (compliance)         S3 CRR destination
     │ AWS Backup               ──────────────────────          Object Lock preserved
     └──────push───────────────▶ NO trust policy allowing
                                 prod roles to delete
                                 Separate backup CMK
                                 Access: 2 named humans,
                                 break-glass only, dual-approved
```

- The backup account is **not** in the same organisational unit as production and is subject to an SCP denying `backup:DeleteRecoveryPoint`, `backup:DeleteBackupVault` and `kms:ScheduleKeyDeletion` to all principals.
- **AWS Backup Vault Lock in compliance mode** on monthly and annual vaults: once the lock's cooling-off period elapses, retention cannot be shortened and recovery points cannot be deleted by anyone — including AWS Support. This is the anti-ransomware guarantee. Configure carefully; it is irreversible.
- Daily and weekly vaults use governance mode to retain operational flexibility for genuine mistakes.

### Encryption and key interaction

- Backups are encrypted with a **dedicated multi-region backup CMK**, whose key policy denies `ScheduleKeyDeletion` to every principal.
- S3 replicated objects retain their per-tenant CMK encryption; replication uses a replica key in the DR region.
- **Critical interaction to understand and document:** destroying a tenant's CMK (crypto-shredding for erasure) renders their data unreadable in *all* backups. This is intended — it is the erasure mechanism — but it means key deletion is genuinely irreversible after the 30-day window, and it must never be treated as a recoverable operation.

### Restore capabilities

Three distinct restore paths, each tested:

1. **Full system restore** — new region, new account, from immutable vaults. Tested semi-annually (doc 16). Target: T1 services within 4 hours.
2. **Point-in-time restore** — Aurora PITR to any second within 35 days, into an isolated environment, for investigating or reversing a bad migration or destructive change.
3. **Tenant-granular restore** — restore a single tenant's documents and metadata to a point in time without affecting other tenants. This requires deliberate design: tenant-scoped object versioning, tenant-partitioned metadata export, and a restore tool that reassembles them consistently. **Build this; it is the restore customers will actually request**, and doing it by hand from a full snapshot is slow, error-prone and exposes other tenants' data to the operator performing it.

### Automated restore verification (daily)

```
1. Select a random recent snapshot
2. Restore into an isolated verification account (no production connectivity)
3. Run assertions:
   • Schema matches expected version
   • Row counts within expected bounds vs. source metrics
   • Referential integrity checks pass
   • Sample of documents decrypts successfully with the tenant key
   • Hash-chain verification passes for a sample of evidence records
   • Application smoke test starts successfully against the restored data
4. Record measured restore duration
5. Emit a sealed evidence record (doc 15); destroy the verification environment
6. Any failure → P1 incident
```

This job is the single most valuable backup control. It converts "we have backups" into "we restored successfully 24 hours ago, and here is the signed evidence".

### Access control on backups

- Restore is a privileged operation requiring dual approval and producing a customer-visible audit event where tenant data is involved.
- Restored data lands in an isolated environment with the same access controls as production — a common failure is restoring to a "temporary" environment with weak controls, effectively creating an unprotected copy of everything.
- Verification-environment lifetime is capped (hours), and its destruction is asserted.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Ransomware encrypts or deletes production **and** backups | Total, unrecoverable loss | Separate account, Vault Lock compliance mode, cross-region copies, no trust path from production |
| Backup restored into a weakly-controlled environment | Uncontrolled copy of all customer data | Isolated verification account with production-equivalent controls; automated teardown; access audited |
| Restore has never been tested at full scale | Discover 3-day restore time during a real disaster | Daily automated verification; semi-annual full restore test |
| Backup contains data that should have been erased | GDPR non-compliance | Crypto-shredding; documented backup expiry timeline in the DPA; finite backup retention |
| Backup encryption key lost or destroyed | Backups unreadable — total loss | Backup CMK is multi-region with deletion denied in policy; separate from tenant keys |
| Silent backup failure (job succeeds, data incomplete) | Undetected gap discovered at restore time | Daily restore verification with row-count and integrity assertions, not just job-status monitoring |
| Backup data crosses out of the EU (replica in a non-EU region) | Residency and transfer violation | SCP restricting replication destinations; automated conformance check on replication configuration |
| Vault Lock misconfigured with excessive retention | Unbounded, unremovable cost; storage-limitation breach | Governance-mode trial; retention derived from the policy engine; cost modelling before locking |
| Tenant-granular restore not built; operator does it manually | Slow, error-prone, and exposes other tenants' data to the operator | Build the tenant-restore tool before general availability |

## Trade-offs

- **Vault Lock compliance mode (ransomware-proof; irreversible mistakes, unbounded cost if misconfigured) vs. governance mode.** **Recommendation: compliance mode for monthly and annual vaults only; governance for daily and weekly, where operational flexibility has genuine value.**
- **Daily automated restore verification (highest-value control; compute cost and engineering effort) vs. quarterly manual testing.** **Recommendation: daily automated. The cost is a few hundred euros a month and it is the control most likely to prevent a catastrophic surprise.**
- **Backing up derived data — search indexes, embeddings (faster recovery; more copies of confidential data, more cost) vs. rebuilding.** **Recommendation: rebuild. It reduces both cost and confidentiality surface, at the price of a longer recovery tail for search functionality — an acceptable degradation.**
- **7-year backup retention aligned to MiCA (simple) vs. shorter backups plus the immutable evidence store carrying long-term retention.** Long-retention backups are expensive and are a growing pile of erasure-conflicted personal data. **Recommendation: backups max 12 months; long-term retention obligations are met by the purpose-built evidence store, which is designed for it.**
- **Tenant-granular restore (real customer value, meaningful engineering effort) vs. full-restore only.** **Recommendation: build it — it is both a support-cost reduction and a sellable capability.**
- **Third-copy backup with an independent provider (defends against a total AWS-account compromise; adds a sub-processor, egress cost, and a residency question) vs. AWS-only with account isolation.** **Recommendation: AWS-only with strict account isolation and Vault Lock initially; reconsider a third-provider copy of the evidence store only (small, high-value dataset) at scale.**

## Design decisions

- **DD-21-01:** Backups written to a dedicated backup account with no trust path from production; SCP denies all deletion operations on vaults and backup keys.
- **DD-21-02:** AWS Backup Vault Lock in compliance mode on monthly and annual vaults; governance mode on daily and weekly.
- **DD-21-03:** Backup retention capped at 12 months; long-term regulatory retention (5–7 years) is served by the purpose-built immutable evidence store, not by backups.
- **DD-21-04:** Derived data (search indexes, embeddings, caches) is rebuilt rather than backed up.
- **DD-21-05:** Daily automated restore verification into an isolated, auto-destroyed account with integrity, decryption and hash-chain assertions; failures are P1; results are sealed as evidence.
- **DD-21-06:** Tenant-granular point-in-time restore is built as a first-class capability before general availability.
- **DD-21-07:** All backup copies remain in EU regions, enforced by SCP and verified by continuous conformance scanning.
- **DD-21-08:** Backups encrypted with a dedicated multi-region backup CMK whose policy denies deletion to all principals; the crypto-shredding interaction is documented in the DPA.
- **DD-21-09:** Restore operations require dual approval, land only in environments with production-equivalent controls, and generate customer-visible audit events where tenant data is involved.

## References

- Regulation (EU) 2022/2554 (DORA) Art. 12; Commission Delegated Regulation (EU) 2024/1774
- Regulation (EU) 2016/679 (GDPR) Art. 5(1)(e), 17, 32(1)(c)/(d)
- Directive (EU) 2022/2555 (NIS2) Art. 21(2)(c)
- Regulation (EU) 2023/1114 (MiCA) Art. 68(9)
- NIST SP 800-34 Rev. 1 — Contingency Planning Guide
- ISO 22301:2019 — Business Continuity Management
- AWS Backup Vault Lock; S3 Object Lock; S3 Cross-Region Replication; Aurora backup and PITR documentation
- ENISA — Ransomware threat landscape reports

## Confidence level

**High** — account isolation, Vault Lock, the rebuild-don't-backup principle for derived data, daily automated restore verification, and the split between short backup retention and long-term evidence retention. These are correct and directly satisfy DORA Art. 12.

**Medium** — the engineering effort required for genuinely consistent tenant-granular restore across the object store and the relational metadata (cross-store consistency at a point in time is harder than it first appears), and the true cost profile of daily restore verification at larger data volumes.
