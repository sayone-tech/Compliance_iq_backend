# Immutable Evidence Retention

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

This is the product's core promise, not merely a security control. PRD §2 opens with it: *"ComplianceIQ is the permanent record of a firm's compliance activity… Everything the platform stores must be kept securely, and most of it cannot be deleted."*

## What the PRD requires

| Record class (PRD §2) | Retention | Deletability |
|---|---|---|
| Firm profile | For as long as the firm is a client | — |
| Regulatory requirement IDs and test procedures | **Full history of every version kept forever** | Old versions never deleted (SA-02) |
| Test executions | Minimum 6 years | — |
| Test results | Minimum 6 years | **Cannot be changed once signed off** — only an amendment on top (FR-27) |
| Evidence files | Minimum 6 years | **Cannot be deleted by anyone** |
| Sampling records | Minimum 6 years | Original selection immutably retained alongside any change (FR-21c) |
| Findings | Minimum 6 years | — |
| Remediation action items | Minimum 6 years | — |
| Remediation evidence | Minimum 6 years | **Cannot be deleted** |
| Compliance reports | Minimum 6 years | **Cannot be changed after they are issued** (FR-61) |
| Staff records | Employment duration plus retention period | — |
| Audit log | Minimum 6 years | **Cannot be modified by anyone** (NFR-04, FR-13) |
| Notification log | Minimum 6 years | — |

Plus: **NFR-07** — "All test results, findings, evidence, reports and audit logs are retained for a minimum of six years. No user — including administrators — can delete them." **FR-37** — every WSP version and every mapping change kept permanently with complete version history; nothing overwritten. **FR-21b** — a recorded Not Applicable status is immutable, timestamped and permanently retained.

### What the PRD does **not** say

- **It does not specify an end date.** "Minimum six years" is a floor. When, if ever, a record class becomes eligible for disposal is **[OPEN]** — see the storage-limitation discussion below.
- **It does not resolve the erasure conflict.** See `regulatory-obligations` and the section below.
- **It does not require cryptographic anchoring, external timestamping or third-party verifiability.** Those are **[FUTURE]**.

## Best practices

- **Immutability must be enforced by something the operator cannot override.** An application-level "read-only" flag is worthless as proof. Write-once storage where no principal — including the account root — can delete within the retention period is the minimum credible bar, and it is what NFR-04's "not even the system administrators at SayOne" requires in practice.
- **Tamper-resistance and tamper-evidence are different, and both are needed.** Write-once storage resists deletion; hash chaining detects alteration.
- **Seal a self-contained record, not a database row.** A record that can only be interpreted by a running system is weak evidence in year five.
- **Separate retention from deletion authority.** Those who create records cannot destroy them; during the retention period nobody can.
- **Plan for verification, not just storage.** Verify continuously, internally, and alert on any discrepancy.

## Regulatory implications

- **PRD §2 / NFR-07** — the binding requirement. Six-year minimum, non-deletable.
- **MiCA Art. 68(9)** (customer-side) — records retained in a durable medium for at least 5 years, extendable to 7 on competent-authority request. **The PRD's six-year floor sits above MiCA's five and is the number this platform implements.** A firm asked by its authority to extend to seven needs the platform to support a longer hold; the retention service below accommodates that.
- **GDPR Art. 17(3)(b)** — erasure does not apply where processing is necessary for compliance with a legal obligation to which the *controller* is subject. The controller is the firm. This is the provision the refusal path relies on, and it must be documented **per record class**, not asserted generally.
- **GDPR Art. 5(1)(e)** — storage limitation: retention must be limited to what is necessary. Indefinite retention of everything is in tension with this. **The PRD sets a floor and no ceiling. The ceiling is an open legal and product question** — see below.
- **Legal hold** — supervisory investigation or litigation may require suspending any disposal on a defined scope, with an audit trail. **[PROPOSED]**

### The two unresolved retention questions

**1. Erasure vs. non-deletability.** Recorded in `regulatory-obligations` and repeated here because this is where it bites. The PRD's rule stands. This research set does **not** adopt crypto-shredding, deletion sagas, soft-delete grace periods, or any mechanism that would make PRD-protected records unreadable. Candidate resolutions — refusal under Art. 17(3)(b) for protected classes, ordinary deletion for unprotected classes — must be settled by the Client with counsel. **[OPEN — LEGAL]** (`open-questions`, L-3.)

**2. When does retention end?** A six-year minimum with no defined maximum means, implemented literally, records are kept forever. That is defensible for the retention period and questionable afterwards. Options to put to the Client: a defined disposal point per class once the minimum has elapsed and no hold applies; disposal on firm offboarding after the minimum; or explicit indefinite retention with a documented justification. **No default is chosen here.** **[OPEN — LEGAL]** (`open-questions`, L-4.)

## Recommended architecture

### Sealed record format **[PROPOSED]**

Every record in a protected class is stored as a self-describing package:

```
evidence/{firm_id}/{yyyy}/{mm}/{record_id}/
├── manifest.json          # canonical, deterministic serialisation
│   ├── record_id, firm_id, record_type, schema_version
│   ├── subject: { requirement_id, test_execution_id, testing_period,
│   │              related_document_ids[] }
│   ├── created_at, created_by, approved_by[], approval_time     # FR-32 / FR-44 approvers
│   ├── content_digests: { file: sha-256, ... }
│   ├── ai_provenance: { model_id, model_version, prompt_version,
│   │                    prompt_hash, reviewer_id, override_tag }   # `ai-governance`, only for
│   │                                                                # WSP mapping records
│   ├── chain: { sequence_no, prev_manifest_hash, manifest_hash }
│   └── retention: { policy_id, min_until, legal_hold }
├── content/               # the artefacts themselves
└── manifest.sig           # signature over manifest.json, sealing key held in the key service
```

`min_until` is derived from the retention service, never hand-entered. There is deliberately **no `max_until` default** — see open question 2 above.

### Storage layers **[PROPOSED]**

| Layer | Mechanism | Guarantee |
|---|---|---|
| 1. Write-once object storage | Object retention in a compliance-grade mode, retain-until derived from the retention service | No principal — including the account root — can delete or overwrite before expiry. This is what makes NFR-04 and NFR-07 technically true |
| 2. Hash chain | Each manifest references the previous manifest's hash, per firm | Any alteration or removal breaks the chain and is detectable |
| 3. Replica | Copy to a second EU location, retention preserved on the replica | Survives loss of the primary. **Whether a second region exists is [OPEN]** (`data-residency`, `disaster-recovery`) |
| 4. Signature | Manifest signed with a sign-only, non-exportable key (`key-management`) | Origin integrity |

**Compliance-grade retention mode versus a governance mode that a privileged principal can shorten:** only the former satisfies "not even the system administrators at SayOne" (NFR-04). The accepted consequence is that a mistake is permanent, which is why the staged rollout in `deployment-recommendations` §5 matters.

External anchoring — daily Merkle roots, qualified timestamps from a trust service provider, a published root feed, a distributable verifier tool — would materially strengthen third-party verifiability. **None of it is required by the PRD, and the verifier tool would also require a Client decision because CC-03 assigns all platform code exclusively to the Client.** All **[FUTURE]** (appendix 39).

### Retention service **[PROPOSED, implementing NFR-07]**

```
record_class            → { min_retention, basis, deletable, legal_hold_capable }

audit_log               → 6y minimum , PRD NFR-07 / FR-13      , not deletable
notification_log        → 6y minimum , PRD §2                  , not deletable
test_execution          → 6y minimum , PRD §2                  , not deletable
test_result             → 6y minimum , PRD §2, FR-27           , not deletable, not modifiable after sign-off
evidence_file           → 6y minimum , PRD §2, §7.1 step 5     , not deletable
sampling_record         → 6y minimum , PRD §2, FR-21c          , not deletable
finding                 → 6y minimum , PRD §2                  , not deletable
remediation_item        → 6y minimum , PRD §2                  , not deletable
remediation_evidence    → 6y minimum , PRD §2                  , not deletable
compliance_report       → 6y minimum , PRD §2, FR-61           , not deletable, not modifiable after issue
wsp_version + mappings  → permanent  , PRD FR-37               , never overwritten
requirement_id_versions → permanent  , PRD §2, SA-02           , old versions never deleted
firm_profile            → client relationship duration, PRD §2 , —
staff_record            → employment + retention period, PRD §2, —
operational_log         → weeks      , none                    , deletable
```

- `min_until` sets the write-once retain-until date at seal time.
- **Legal hold** is a separate flag with no expiry, applied and released only by dual-approved action, fully audited and surfaced to the firm.
- **Extension is supported** — a firm whose competent authority extends its MiCA retention to seven years can have the hold lengthened. Shortening below the PRD floor is not possible.
- **No automatic expiry or disposal job is specified**, because the PRD sets no ceiling. If the Client decides on one (open question 2), it belongs here and it must emit its own audit record.

### Verification **[PROPOSED]**

A scheduled internal job re-verifies a random sample plus the current chain head: content digests, manifest signature, chain linkage. Any discrepancy is a top-severity incident. This converts "we have immutable records" into "we verified them yesterday, and here is the record of it".

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Write-once retention applied with an incorrect duration or to the wrong class | Unremovable data; unbounded cost | Staged rollout via a reversible mode first (`deployment-recommendations` §5); mandatory seal-preview; retention derived only from the service, never hand-entered; bucket separation by class |
| Sealing key compromised | Records could be forged | Key held in the key service, sign-only, non-exportable, rotation with the full historical public-key set retained (`key-management`) |
| Hash chain broken by an ingestion gap or out-of-order write | Verification failure indistinguishable from tampering | Single-writer sealer with a monotonic sequence, idempotent retries, gap-detection alerting, a documented repair procedure that itself produces an audit record |
| A deletion or modification path exists for a protected class | **Direct breach of NFR-04 / NFR-07** | No delete API; static-analysis rule; tests asserting delete and update fail; write-once storage as the backstop |
| Key deletion used as a back-door deletion mechanism | Same breach, achieved indirectly | Key deletion blocked while records are inside retention (`key-management`, DD-08-06) |
| Storage cost growth over six-plus years | Unbudgeted cost; pressure to weaken retention | Lifecycle transition to colder storage classes that preserve the retention lock; model cost at multiples of current volume; note FR-24 admits video |
| Records retained indefinitely with no defined end | Tension with GDPR Art. 5(1)(e) | Escalate open question 2 rather than inventing a ceiling |
| Nobody verifies the records until a regulator asks | Catastrophic loss of product credibility | Scheduled automated verification of a sample plus the chain head |

## Trade-offs

- **Compliance-grade write-once retention (unbreakable; mistakes permanent) vs. a governance mode (recoverable; defeatable by a privileged insider).** NFR-04 removes the choice for audit and evidence: **compliance-grade**, with a staged rollout and a preview-and-approve step before sealing. **[PRD REQUIRED in effect]**
- **Hash chain on standard storage vs. a ledger database.** Recommendation: hash chain — fewer dependencies, better durability, no vendor deprecation risk. **[PROPOSED]**
- **Uniform retention for everything vs. per-class policy.** A blanket policy is simpler; per-class is more defensible under storage limitation and cheaper. Recommendation: per-class service, with the PRD's six-year floor as the minimum for every listed class. **[PROPOSED]**
- **External cryptographic anchoring vs. internal chain only.** Anchoring is the strongest available answer to "prove you did not regenerate this", and comparatively cheap if batched. **Not required by the PRD.** Recommendation: raise it as a possible differentiator for a later phase. **[FUTURE]**

## Design decisions

| ID | Decision | Classification | Basis |
|---|---|---|---|
| DD-15-01 | Test results, findings, evidence, remediation evidence, reports, audit logs and notification logs are retained for a **minimum of six years** | **[PRD REQUIRED]** | NFR-07, PRD §2 |
| DD-15-02 | None of those records can be deleted by any user, including administrators; no deletion API exists for them | **[PRD REQUIRED]** | NFR-07, PRD §2, §7.1 step 5 |
| DD-15-03 | A signed-off test result cannot be changed; correction is by amendment with a written explanation, the original retained | **[PRD REQUIRED]** | FR-27 |
| DD-15-04 | An issued report is permanently archived exactly as issued and cannot be changed | **[PRD REQUIRED]** | FR-61 |
| DD-15-05 | Every WSP version and every mapping change is retained permanently with full version history; nothing is overwritten | **[PRD REQUIRED]** | FR-37 |
| DD-15-06 | Requirement ID and test procedure versions are retained in full; old versions are never deleted | **[PRD REQUIRED]** | PRD §2, SA-02 |
| DD-15-07 | Records in protected classes are stored as self-contained sealed packages with content digests, a signed manifest and chain linkage | **[PROPOSED]** | implements NFR-04 |
| DD-15-08 | Write-once object retention in a compliance-grade mode, retain-until derived automatically from the retention service, with a staged rollout | **[PROPOSED]** | implements NFR-04, NFR-07 |
| DD-15-09 | Per-firm hash chain over manifests, with scheduled internal verification of a sample and the chain head | **[PROPOSED]** | implements NFR-04 |
| DD-15-10 | Retention service with per-class minimums and legal-hold capability; extension supported, shortening below the PRD floor impossible | **[PROPOSED]** | implements NFR-07 |
| DD-15-11 | Legal hold at record and scope level, dual-approved, audited, visible to the firm | **[PROPOSED]** | — |
| DD-15-12 | Whether and when retention ends after the six-year minimum | **[OPEN — LEGAL]** | PRD sets a floor, no ceiling |
| DD-15-13 | How GDPR erasure requests interact with protected classes | **[OPEN — LEGAL]** | `regulatory-obligations` |
| DD-15-14 | External anchoring (qualified timestamps, published Merkle roots) and a distributable verifier tool | **[FUTURE]** | not in PRD; CC-03 affects publication |

## References

- Regulation (EU) 2023/1114 (MiCA) Art. 68(9) — customer-side record keeping
- Regulation (EU) 2016/679 (GDPR) Art. 5(1)(e), 17(3)(b)
- Commission Delegated Regulation (EU) 2024/1774 — protection of logs and records *(design reference)*
- RFC 6962 — Merkle tree and inclusion-proof design pattern
- AWS S3 Object Lock documentation — COMPLIANCE versus GOVERNANCE modes
- ETSI TS 119 512 — preservation services *(context for the future-scope anchoring option)*

## Confidence level

**High** — the sealed package format, compliance-grade write-once storage, hash chaining, and the per-class retention service. These implement PRD §2 and NFR-07 directly and are the standard answer for regulated record stores.

**Not determined, and deliberately left so** — when retention ends, and how erasure requests are handled against protected classes. Both require a Client decision taken with counsel.
