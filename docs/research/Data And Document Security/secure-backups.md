# Secure Backups

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

`disaster-recovery` covers recovery strategy. This document covers the backup system itself as a *security* asset: a complete, encrypted, restorable copy of every firm's confidential data, which is simultaneously the last line of defence and one of the most attractive targets in the architecture.

The PRD does not mention backups. What it does say, and what governs everything here: **records in the protected classes must survive a minimum of six years and cannot be deleted by anyone (the non-deletable retention requirement, the PRD's data and retention table), all client data stays in EU data centres (the EU residency requirement), and encryption is AES-256 with a per-firm key (the encryption requirement).** Everything below is **[PROPOSED]** in service of those.

## Best practices

- **Three copies, at least two storage classes or locations, at least one immutable, and zero errors on a verified restore.** The immutable copy and the verified restore are the two most organisations get wrong.
- **Backups must not be deletable by the credentials that manage production.** If compromising production also compromises backups, you have replication, not backup.
- **Backups inherit the confidentiality of the source.** A backup of a firm's evidence *is* that firm's evidence: same classification, same key, same access control, same audit logging.
- **Verify restores automatically and continuously.** A backup that has never been restored is an untested hypothesis.
- **Design firm-granular restore**, not only full-system restore. The most common real recovery request is "a firm's data was corrupted by a bad migration", not "the region is gone".
- **Encrypt with a key the backup system cannot delete.**

## Regulatory implications

- **GDPR Art. 32(1)(c)** — the ability to restore availability and access to personal data in a timely manner. **Art. 32(1)(d)** — regular testing of effectiveness.
- **GDPR Art. 5(1)(e)** — backups have a retention limit too; perpetual backups are in tension with storage limitation. **But see the open question below — the PRD sets a six-year floor and no ceiling, so no backup expiry schedule is invented here.**
- **The non-deletable retention requirement** — the six-year minimum applies to the records themselves. The primary durable copy of protected records is the immutable evidence store (`immutable-evidence-retention`), which is designed for long retention. Backups exist to recover *operational* state, not as the long-term record archive.
- **Delegated Reg. (EU) 2024/1774 / DORA Art. 12** (customer-side) — backup scope and frequency driven by criticality **and confidentiality**; restoration using systems logically and physically segregated from the source; periodic restoration testing; integrity checks where data is reconstructed. Used as a **design reference**.
- **Residency (`data-residency`)** — every backup copy stays in the EU/EEA. A copy to a non-EU location would breach the EU residency requirement.

## Recommended architecture

### Backup inventory

| Asset | Method | Immutable copy | Note |
|---|---|---|---|
| Relational store (firm profiles, tests, findings, remediation, mappings, staff records, configuration) | Point-in-time recovery plus scheduled snapshots pushed to a separate backup account | Yes, for the longer-retention tier | The operational recovery workhorse |
| Object storage — evidence and reports | Versioning plus a copy outside the primary failure domain; write-once retention preserved on the copy | Inherent (`immutable-evidence-retention`) | This is the durable record copy, not a backup in the usual sense |
| Object storage — WSP documents and derivatives | Versioning plus copy | Yes for WSP versions (the permanent WSP version history requirement requires permanent retention) | Derivatives are rebuildable |
| Search index | Rebuildable from source | No | Deliberately not a source of truth |
| Extracted text, OCR output, embeddings | Rebuildable from source documents | No | Reduces backup surface and confidentiality exposure |
| Secret store | Replication plus scheduled backup | No | Short retention |
| Key material | Not backup-able; keys are the root of trust | — | Replicate the backup and evidence keys to any secondary EU location in use (`key-management`) |
| Infrastructure and application code | Version control, with at least one independent remote | History plus protected branches | IP ownership term: the Client owns this; ensure the Client can obtain it |
| Container images | Registry with immutable tags plus a copy | Immutable tags | — |
| Audit log | Written directly to write-once storage — the primary copy *is* immutable | Inherent | Needs replication, not a separate backup regime |

Two principles visible in that table: **derived data is rebuilt, not backed up**, which cuts cost and confidentiality exposure; and **audit and evidence data is born immutable**, so its durability comes from the store itself.

### Isolation architecture

```
prod account                    backup account                  secondary EU location (if any)
────────────                    ──────────────                  ──────────────────────────────
Databases, object storage       Backup vaults                   Copied vaults
     │                          Immutable retention lock         Replicated object storage
     │ push only                ──────────────────────           Write-once retention preserved
     └──────────────────────────▶ NO trust policy allowing
                                  prod roles to delete
                                  Separate backup key
                                  Access: named individuals,
                                  break-glass, dual-approved
```

- The backup account sits outside the production organisational unit and is subject to policy denying deletion of recovery points, deletion of vaults, and deletion of the backup key, **to all principals**.
- **An immutable retention lock on the longer-retention vaults** is the anti-ransomware guarantee: once locked, retention cannot be shortened and recovery points cannot be deleted by anyone. It is irreversible — configure it carefully and stage the rollout (`deployment-recommendations` §5).
- Shorter-retention vaults may use a reversible mode to retain operational flexibility for genuine mistakes.

### Encryption and the key interaction

- Backups are encrypted with a dedicated backup key whose policy denies deletion to every principal (`key-management`).
- Replicated objects retain their per-firm key encryption.
- **Critical interaction:** destroying a firm's key would render that firm's data unreadable in backups as well as in production. `key-management` therefore **blocks key deletion while records are inside their retention period**. Key deletion is not a permitted erasure mechanism in this design — see `regulatory-obligations` and `immutable-evidence-retention`.

### Backup retention schedule — **[OPEN]**

The PRD sets a six-year minimum for protected records and no maximum. It says nothing about backup retention.

**No backup retention cap is proposed here.** The engineering position:

- The **immutable evidence store** (`immutable-evidence-retention`) is the mechanism that satisfies the non-deletable retention requirement; it is designed for long retention and its records cannot be deleted.
- **Backups serve operational recovery** — reversing a bad migration, recovering corrupted state, restoring after ransomware. That purpose is served by a schedule of days to months, not years.
- **Whether long-horizon backup copies are also kept, and for how long, is a Client decision** balancing cost, the GDPR storage-limitation argument, and how much confidence is wanted that the evidence store's own durability is not a single point of failure. See `open-questions`, L-4.

Any schedule chosen must **not** be able to undercut the non-deletable retention requirement for any record class whose only durable copy is in a backup.

### Restore capabilities

Three distinct restore paths, each tested:

1. **Full system restore** — into a clean environment from immutable vaults. Exercised as part of the recovery testing programme (`disaster-recovery`).
2. **Point-in-time restore** — into an isolated environment, for investigating or reversing a bad migration or destructive change.
3. **Firm-granular restore** — restoring a single firm's operational data to a point in time without affecting other firms. This requires deliberate design: firm-scoped object versioning, firm-partitioned metadata export, and a tool that reassembles them consistently. **Build it.** Doing it by hand from a full snapshot is slow, error-prone, and exposes other firms' data to the operator performing it — a direct the tenant isolation requirement hazard. **[PROPOSED]**

### Automated restore verification **[PROPOSED]**

```
1. Select a recent snapshot
2. Restore into an isolated verification account with no production connectivity
3. Assert:
   • Schema matches the expected version
   • Row counts within expected bounds against source metrics
   • Referential integrity checks pass
   • A sample of evidence files decrypts successfully with the correct firm key
   • Hash-chain verification passes for a sample of sealed records (`immutable-evidence-retention`)
   • Historical ciphertext written under a previous key version still decrypts (`key-management`)
   • The application starts against the restored data
4. Record the measured restore duration
5. Emit a record into the immutable store; destroy the verification environment
6. Any failure is a top-severity incident
```

This job converts "we have backups" into "we restored successfully, and here is the record".

### Access control on backups

- Restore is a privileged operation requiring dual approval and producing an audit event.
- Restored data lands in an environment with production-equivalent controls. A common failure is restoring to a "temporary" environment with weak controls, creating an unprotected copy of everything.
- Verification-environment lifetime is capped and its destruction asserted.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Ransomware encrypts or deletes production **and** backups | Total, unrecoverable loss; breach of the non-deletable retention requirement | Separate account with no trust path, immutable retention lock, copies outside the primary failure domain |
| Backup restored into a weakly controlled environment | Uncontrolled copy of all firms' data; breach of the tenant isolation requirement | Isolated verification account with production-equivalent controls; automated teardown; access audited |
| Restore never tested at scale | Discovering a multi-day restore time during a real incident | Automated restore verification on a short cycle; a full restore exercise before real customer data |
| Backup encryption key lost or destroyed | Backups unreadable — total loss | Backup key replicated within the EU with deletion denied in policy; separate from firm keys |
| Silent backup failure — job succeeds, data incomplete | Undetected gap discovered at restore time | Restore verification with row-count and integrity assertions, not just job-status monitoring |
| Backup copy placed outside the EU | Breach of the EU residency requirement | Policy restricting replication destinations; automated conformance check |
| Immutable lock configured with an excessive retention period | Unbounded, unremovable cost | Reversible-mode trial; retention derived from the retention service; cost modelling before locking |
| Firm-granular restore not built; an operator does it manually | Slow, error-prone, exposes other firms' data | Build the firm-restore tool before general availability |
| Backup schedule assumed to satisfy the non-deletable retention requirement | Records lost after backups expire | The evidence store, not backups, is the non-deletable retention requirement mechanism; assert this in design review |

## Trade-offs

- **Immutable retention lock vs. a reversible mode.** Recommendation: immutable for the longer-retention tier, reversible for the short-cycle tier where operational flexibility has genuine value. **[PROPOSED]**
- **Frequent automated restore verification vs. periodic manual testing.** Recommendation: automated and frequent. It is the control most likely to prevent a catastrophic surprise, and its cost is modest. **[PROPOSED]**
- **Backing up derived data vs. rebuilding it.** Recommendation: rebuild. Lower cost, smaller confidentiality surface; the price is a longer recovery tail for search, which is an acceptable degradation. **[PROPOSED]**
- **Firm-granular restore vs. full-restore only.** Recommendation: build it — support-cost reduction and an isolation safeguard. **[PROPOSED]**
- **A third copy with an independent provider vs. account isolation within the chosen provider.** Recommendation: account isolation and immutable retention initially; reconsider an independent copy of the evidence store alone — small, high-value — if the Client wants further assurance against a total account compromise. **[OPEN]**

## Design decisions

| ID | Decision | Classification | Basis |
|---|---|---|---|
| DD-21-01 | Backups are written to a dedicated account with no trust path from production; policy denies all deletion operations on vaults and backup keys | **[PROPOSED]** | protects the non-deletable retention requirement |
| DD-21-02 | Immutable retention lock on the longer-retention vaults; reversible mode on the short-cycle tier | **[PROPOSED]** | — |
| DD-21-03 | The immutable evidence store, not backups, is the mechanism that satisfies the six-year minimum; backups serve operational recovery | **[PROPOSED]** | Non-deletable retention requirement, `immutable-evidence-retention` |
| DD-21-04 | Backup retention schedule and whether long-horizon copies are kept | **[OPEN]** | Client decision; no cap invented |
| DD-21-05 | Derived data (search indexes, extracted text, embeddings, caches) is rebuilt rather than backed up | **[PROPOSED]** | — |
| DD-21-06 | Automated restore verification into an isolated, auto-destroyed environment with integrity, decryption and chain assertions; failures are top severity | **[PROPOSED]** | GDPR Art. 32(1)(d) |
| DD-21-07 | Firm-granular point-in-time restore built as a first-class capability | **[PROPOSED]** | protects the tenant isolation requirement |
| DD-21-08 | All backup copies remain in EU regions, enforced by policy and verified continuously | **[PROPOSED]** | EU residency requirement |
| DD-21-09 | Backups encrypted with a dedicated backup key whose policy denies deletion to all principals | **[PROPOSED]** | Encryption requirement |
| DD-21-10 | Restore operations require dual approval, land only in environments with production-equivalent controls, and generate audit events | **[PROPOSED]** | supports the permanent audit log requirement |

## References

- Regulation (EU) 2016/679 (GDPR) Art. 5(1)(e), 32(1)(c)/(d)
- Regulation (EU) 2022/2554 (DORA) Art. 12; Commission Delegated Regulation (EU) 2024/1774 *(design reference)*
- NIST SP 800-34 Rev. 1 — Contingency Planning Guide
- ISO 22301:2019 — Business Continuity Management
- AWS Backup Vault Lock; S3 Object Lock; S3 Cross-Region Replication
- ENISA — Ransomware threat landscape reports

## Confidence level

**High** — account isolation, immutable retention, the rebuild-rather-than-back-up principle for derived data, automated restore verification, and the separation between operational backups and the non-deletable retention requirement evidence store.

**Medium** — the engineering effort for genuinely consistent firm-granular restore across object storage and relational metadata; point-in-time consistency across stores is harder than it first appears.

**Not determined** — the backup retention schedule, which is a Client decision.
