# Key Management

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

Key management is where residency, isolation, insider risk and record survival converge. **the encryption requirement requires that each firm has its own encryption key.** Getting the key architecture right is what makes that requirement a real isolation control; getting it wrong makes the encryption decorative and, worse, puts the six-year non-deletable record store (the non-deletable retention requirement) at risk of becoming unreadable.

## Best practices

- **Key custody answers the question buyers actually ask:** who can produce plaintext? Answer it with key architecture, not with a region name.
- **Keys never leave the hardware boundary in plaintext.** Generation, storage, wrapping and unwrapping happen inside a certified module.
- **Strict separation of duties.** Those who administer keys cannot access data; those who access data cannot administer keys. Enforce in identity policy, not in prose.
- **Every key has a documented lifecycle** — generate, activate, rotate, deactivate, archive — with owners and evidence at each transition.
- **Automate rotation.** Manual rotation is either not done or done wrong.
- **Maintain a key inventory:** purpose, algorithm, custodian, cryptoperiod, dependency map.
- **Design so that key loss cannot destroy records the PRD says cannot be deleted.** This is the constraint that most distinguishes ComplianceIQ from a generic SaaS.

## Regulatory implications

- **GDPR Art. 32/34** — key separation is what makes encrypted data "unintelligible" and can remove the duty to notify data subjects. **Chapter V / EDPB Recommendations 01/2020** — EU-held keys inaccessible to any third-country entity are the primary recognised technical supplementary measure (`cross-border-data-processing`).
- **Delegated Reg. (EU) 2024/1774** expects a cryptographic key management policy covering generation, renewal, storage, backup, archival, retrieval, transmission, retirement, revocation and destruction, plus key lifecycle records. Used here as a **design reference**; the register is cheap to build and directly useful in customer security reviews. **[PROPOSED]**
- **MiCA Art. 68(9)** (customer-side) — a CASP that loses access to its records has a record-keeping failure, not merely an availability incident. Key loss is therefore a compliance event for the customer, which is why key destruction is treated below as something to prevent rather than to schedule.

## Recommended architecture

### Key hierarchy **[PROPOSED, implementing the encryption requirement]**

```
Root of trust: managed key service with certified HSMs, EU region (`data-residency`)
├── Platform key            ── infrastructure secrets, non-firm data
├── Audit-log key           ── separate key, separate administrative role,
│                              deletion denied to every principal
├── Backup key              ── separate key, replicated to any secondary EU region used
├── Evidence-sealing key    ── asymmetric, sign-only, non-exportable
└── Per-firm key  (firm-<id>)                         ← required by the encryption requirement
    ├── Per-object data keys ── wrapped, stored beside the ciphertext
    ├── Field data key       ── per firm, for field-level encryption
    └── Blind-index HMAC key ── per firm
```

No customer-managed, hold-your-own-key or external-key-store tiering is in scope; see appendix 39. **[FUTURE]**

### Key policies — where enforcement actually happens **[PROPOSED]**

Each per-firm key policy enforces:

- Only the document service role may decrypt, **and only where the request's encryption context carries the matching firm identifier.** This is the mechanism that makes a cross-firm data-mixing bug fail closed (the tenant isolation requirement).
- No principal holds both key-deletion and data-plane decrypt rights.
- Key use is restricted to the specific services that need it, so a stolen credential cannot call the key service directly.
- All principals outside the organisation are denied, as are requests from outside the approved EU region set (the EU residency requirement).
- Key administration is a separate role, assumable only through break-glass with dual approval, never held standing.

### Key destruction — the ComplianceIQ-specific rule **[PRD REQUIRED in effect]**

Destroying a firm's key would render that firm's evidence, results, reports and audit records permanently unreadable. **the PRD's data and retention table and the non-deletable retention requirement state those records cannot be deleted by anyone, including administrators.** An unreadable record is a deleted record in substance.

Therefore:

1. **Deletion is denied in policy for the audit-log key, the evidence-sealing key and the backup key**, unconditionally.
2. **Deletion of a per-firm key is denied while that firm holds any record inside its retention period.** A key-destruction request must fail a precondition check against the retention registry (`immutable-evidence-retention`), not merely wait out a scheduling window.
3. Where key destruction is genuinely appropriate — a firm that never uploaded protected records, or a test tenant — it requires dual approval and produces an audit record.
4. **Crypto-shredding is not adopted as an erasure mechanism.** It is incompatible with the non-deletable retention requirement on its face. If it is ever to be used, that is a Client decision taken with counsel, recorded against the open erasure question (`regulatory-obligations`, `open-questions` L-3). **[OPEN — LEGAL]**

This is a deliberate departure from generic SaaS practice, where a 7- or 30-day key-deletion window is the norm.

### Rotation **[PROPOSED]**

| Key | Cryptoperiod | Mechanism |
|---|---|---|
| Per-firm keys and platform keys | Annual | Automatic rotation; old material retained so existing ciphertext stays readable — essential given six-year retention |
| Per-object data keys | Per object; re-wrapped when the firm key rotates | Envelope encryption means no bulk re-encryption |
| Field data keys | Annual, with background re-encryption | Versioned; ciphertext carries the key version |
| Blind-index HMAC keys | Rotation requires a full index rebuild — long cryptoperiod, or on compromise | Build and test the rebuild path before launch |
| TLS certificates | Short, automated | Managed certificates |
| Internal service certificates | Very short, automated | — |
| Evidence-sealing keys | Periodic, with **all historical public keys retained permanently** for verification | Key history recorded with the sealed records |

**Emergency rotation runbook** for suspected key compromise: new key version → re-wrap data keys → re-encrypt field data → revoke the old version → assess the exposure window → notify affected firms. Rehearsed periodically. **[PROPOSED]**

### Key inventory **[PROPOSED]**

A machine-maintained register: key identifier, alias, purpose, algorithm, firm, custodian role, created, last rotated, next rotation, dependencies, destruction policy. Generated from cloud APIs and reconciled on a schedule.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| **Key deletion destroys records the PRD says cannot be deleted** | Breach of the non-deletable retention requirement and the PRD's data and retention table; for the firm, a MiCA record-keeping failure | Deletion denied for audit, evidence and backup keys; per-firm key deletion blocked by a retention precondition; dual approval; alerting |
| Encryption context not enforced in the key policy | Cross-firm decryption possible with one leaked role — breach of the tenant isolation requirement | Policy template with a mandatory firm-identifier condition; automated policy conformance scanning |
| Key administrator with standing access | Insider compromise of all data | No standing key administration; break-glass with dual approval and session recording (`insider-threat-protection`) |
| Key-service request cost or throttling at scale | Latency against the performance requirement; cost surprise | Bounded data-key caching; monitor throttling; benchmark under load |
| Regional key-service impairment | All decryption blocked | Replicate the backup and evidence keys to any secondary EU region in use; document the impact; include a key-degraded scenario in recovery testing |
| Blind-index key rotation requires a full reindex and is never planned | Rotation deferred indefinitely | Implement and test the rebuild path before launch |
| Key rotation loses old material, making six-year records unreadable | Silent breach of the non-deletable retention requirement | Use rotation mechanisms that retain prior key versions; assert readability of historical ciphertext in restore verification (`secure-backups`) |

## Trade-offs

- **Managed key service vs. dedicated single-tenant HSM.** A managed service is cheaper, certified, integrated and adequate for the encryption requirement. A dedicated HSM costs roughly an order of magnitude more and adds real operational burden. Recommendation: managed key service. **[PROPOSED]**
- **Per-firm keys for every firm (mandated) vs. a shared key with encryption context.** The encryption requirement removes the choice. The cost is small; treat it as fixed. **[PRD REQUIRED]**
- **Data-key caching vs. no caching.** Caching cuts cost and latency but keeps a decrypted data key in process memory for its lifetime. Recommendation: cache with a short TTL and bounded use count, never across firm boundaries, disabled for `RESTRICTED` evidence. **[PROPOSED]**
- **Replicating keys to a second EU region vs. single-region keys.** Replication supports recovery; the risk is misconfiguring a replica outside the EU. Recommendation: replicate only the backup and evidence keys, with a policy preventing non-EU replicas. Whether a second region exists at all is **[OPEN]** (`data-residency`).

## Design decisions

| ID | Decision | Classification | Basis |
|---|---|---|---|
| DD-08-01 | A managed key service in the selected EU region is the root of trust; a distinct key per firm protects that firm's data | **[PRD REQUIRED]** | Encryption requirement, the EU residency requirement |
| DD-08-02 | Separate keys, with distinct administrative roles, for audit logs, backups and evidence sealing | **[PROPOSED]** | supports the immutable audit requirement |
| DD-08-03 | Key policies mandate a matching firm identifier in the encryption context, restrict use to named services, and deny non-organisation principals and non-EU regions | **[PROPOSED]** | implements the tenant isolation requirement, the EU residency requirement |
| DD-08-04 | Hard separation of duties — no principal holds both key administration and data-plane decrypt rights; key administration is break-glass only, dual-approved, session-recorded | **[PROPOSED]** | — |
| DD-08-05 | Automatic annual rotation with prior key versions retained, so ciphertext written at any point in the six-year window remains readable | **[PROPOSED]** | supports the non-deletable retention requirement |
| DD-08-06 | Deletion denied unconditionally for audit, evidence and backup keys; per-firm key deletion blocked while any record is inside its retention period | **[PRD REQUIRED in effect]** | Non-deletable retention requirement, the PRD's data and retention table |
| DD-08-07 | Crypto-shredding is **not** adopted as an erasure mechanism; any future use is a Client decision taken with counsel | **[OPEN — LEGAL]** | conflicts with the non-deletable retention requirement |
| DD-08-08 | Machine-generated key register, reconciled on a schedule | **[PROPOSED]** | — |
| DD-08-09 | Bounded data-key caching with a short TTL and use count; disabled for `RESTRICTED` evidence | **[PROPOSED]** | — |
| DD-08-10 | A documented key management policy covering the full lifecycle, reviewed annually | **[PROPOSED]** | — |

## References

- NIST SP 800-57 Part 1 Rev. 5 — Recommendation for Key Management
- NIST SP 800-130 — Framework for Designing Cryptographic Key Management Systems
- FIPS 140-3 — Security Requirements for Cryptographic Modules
- Commission Delegated Regulation (EU) 2024/1774 — key management requirements *(design reference)*
- Regulation (EU) 2016/679 (GDPR) Art. 32, 34; EDPB Recommendations 01/2020
- AWS KMS: key policies, encryption context, grants, multi-region keys
- OASIS KMIP 2.x; PKCS#11 v3.0

## Confidence level

**High** — the hierarchy, per-firm keys with encryption-context binding, separation of duties, and the rule that key destruction must not become a back door around the non-deletable retention requirement.

**Medium** — key-service cost and latency at eventual volume; this needs load testing against the performance requirement performance target.
