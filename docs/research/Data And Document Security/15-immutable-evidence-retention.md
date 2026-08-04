# 15 — Immutable Evidence Retention

This is the product's core value proposition, not merely a security control. A CASP's regulator asks: *"prove this control operated on this date, and prove the record has not been altered since."* Everything here exists to make that answer defensible.

## Best practices

- **Immutability must be enforced by something the operator cannot override.** Application-level "read-only" flags are worthless as evidence. WORM storage where even the root account cannot delete within the retention period is the minimum credible bar.
- **Tamper-evidence and tamper-resistance are different, and you need both.** Object Lock resists deletion; hash chaining detects alteration; external anchoring proves the chain existed at a point in time.
- **Anchor to something outside your control.** A hash chain you alone hold proves nothing to a sceptical auditor — you could have regenerated it. An eIDAS **qualified timestamp** from an independent QTSP carries a legal presumption of accuracy and integrity under EU law.
- **Seal a self-contained evidence package**, not a database row. The package must be verifiable years later without access to our running systems.
- **Separate retention from deletion authority.** The people who can create evidence cannot destroy it; nobody can destroy it during the retention period.
- **Plan for verification, not just storage.** Ship a verifier tool. Auditors will use it.

## EU regulatory implications

- **MiCA Art. 68(9)** — records of all services, activities, orders and transactions retained in a **durable medium** for at least **5 years**, extendable to **7 years** on competent-authority request. "Durable medium" implies an unalterable form allowing reproduction without change.
- **AMLR (Reg. (EU) 2024/1624, applicable 10 July 2027)** and current AMLD — CDD records and transaction records retained 5 years after the end of the relationship, with member-state extension possible. Our customer records and KYC evidence fall here.
- **DORA Art. 12** — backup and restoration policies; **Art. 13** — post-incident learning requires preserved evidence. **Delegated Reg. (EU) 2024/1774** requires logs protected against modification and deletion, with a defined retention policy.
- **DORA Art. 19/Art. 26** — incident documentation and TLPT evidence must be retained and producible to authorities.
- **GDPR Art. 17(3)(b)** — the right to erasure does not apply where processing is necessary for compliance with a legal obligation. This is the lawful basis that lets MiCA/AMLR retention survive an erasure request — **but it must be documented per record class, not asserted generally.** Records outside the legal-obligation scope must still be erasable.
- **GDPR Art. 5(1)(e)** — storage limitation: retention must end. Perpetual "immutable" storage is itself a violation. Retention periods must be finite, defined, and enforced by automatic expiry.
- **eIDAS 2 (Reg. (EU) 2024/1183 amending Reg. (EU) 910/2014)** — Art. 41: a **qualified electronic timestamp** enjoys a presumption of the accuracy of the date and time and of the integrity of the data. Art. 35: a **qualified electronic seal** enjoys a presumption of integrity and of correctness of origin. Using a QTSP converts our technical claim into a legal presumption — the single highest-leverage decision in this document.
- **Legal hold** — litigation or supervisory investigation may require suspending scheduled deletion; the system must support indefinite hold on a defined scope with an audit trail.

## Recommended architecture

### Evidence package format

Every sealed evidence record is a self-describing package:

```
evidence/{tenant_id}/{yyyy}/{mm}/{evidence_id}/
├── manifest.json          # canonical, deterministic serialisation
│   ├── evidence_id, tenant_id, evidence_type, schema_version
│   ├── subject: {control_id, period, related_document_ids[]}
│   ├── created_at, created_by, approved_by, approval_time
│   ├── content_digests: {file: sha-256, ...}
│   ├── ai_provenance: {model_id, model_version, prompt_version,
│   │                   prompt_hash, reviewer_id, override_reason}
│   ├── chain: {sequence_no, prev_manifest_hash, manifest_hash}
│   └── retention: {policy_id, min_until, max_until, legal_hold}
├── content/              # the actual artefacts (report PDF, extracted data, source refs)
├── manifest.sig          # our Ed25519 (+ ML-DSA from 2027) signature over manifest.json
└── manifest.tst          # RFC 3161 qualified timestamp token over manifest.sig
```

Verification requires only: the package, our published public keys, and the QTSP's certificate chain. No access to our systems. That is what makes it credible years later.

### Storage layers

| Layer | Mechanism | Guarantee |
|---|---|---|
| 1. WORM object storage | **S3 Object Lock, COMPLIANCE mode**, retention set per policy | No principal — including the AWS account root — can delete or overwrite before expiry |
| 2. Hash chain | Each manifest references the previous manifest hash, per tenant | Any alteration or removal breaks the chain and is detectable |
| 3. Merkle anchoring | Daily Merkle root over all manifests sealed that day | One timestamp covers an entire day's evidence — cost-efficient |
| 4. Qualified timestamp | RFC 3161 token over the daily Merkle root from an EU **QTSP** on the EU Trusted List | Legal presumption of time and integrity under eIDAS Art. 41 |
| 5. Cross-region replica | Replicated to `eu-north-1` with Object Lock retained on the replica | Survives regional loss (DORA Art. 12) |
| 6. Published root digest | Daily Merkle root published to a customer-visible, append-only feed | Customers can independently verify inclusion without trusting us |

**Object Lock COMPLIANCE vs. GOVERNANCE:** GOVERNANCE mode allows a sufficiently-privileged principal to shorten retention — which means an insider or a compromised root account can destroy evidence, defeating the purpose. **COMPLIANCE mode is the only defensible choice for evidence**, with the accepted consequence that a mistake is permanent. Mitigate with a mandatory seal-preview step and a short GOVERNANCE-mode staging period before final sealing.

### Retention policy engine

```
record_class → { min_retention, max_retention, basis, erasable, legal_hold_capable }

audit_log            → 7y   , MiCA Art.68(9) + DORA        , not erasable during period
compliance_report    → 7y   , MiCA Art.68(9)               , not erasable during period
kyc_evidence         → 5y after relationship end, AMLR     , not erasable during period
ai_assessment        → 7y   , MiCA + auditability          , not erasable during period
customer_document    → tenant-configurable, default 7y     , erasable if outside legal basis
support_session_rec  → 2y   , DORA Art.9 privileged access , erasable after period
operational_log      → 90d  , none                         , erasable
marketing/CRM data   → 3y   , legitimate interests         , erasable on request
```

- `min_until` sets the Object Lock retain-until date at seal time.
- `max_until` drives an automatic expiry job that deletes at end of life. **Storage limitation requires this job to exist and to run** — it is as much a compliance control as the retention itself.
- **Legal hold** is a separate S3 Object Lock legal hold flag with no expiry, applied and released only by dual-approved action, fully audited, and surfaced to the tenant.

### Erasure vs. immutability — the resolution

This tension is the most-asked question in every security review. The answer, per record class:

1. **Records under a legal-retention obligation (MiCA/AMLR):** erasure refused under GDPR Art. 17(3)(b), with a documented basis and a response template. The data subject is told which obligation applies and when it expires.
2. **Records outside a legal obligation:** erasable, and the deletion saga of doc 06 applies.
3. **Records in immutable backups where selective deletion is impossible:** **crypto-shredding** — destroy the per-document DEK. The ciphertext remains in the WORM store and in backups but is permanently unreadable. This satisfies erasure in substance while preserving the integrity of the WORM medium. Document this mechanism in the DPA; it is well-recognised but must be disclosed rather than assumed.
4. **Never** apply Object Lock COMPLIANCE to record classes that may need erasure. Bucket-level separation makes this structural rather than procedural.

### Verification tooling

Ship an open-source CLI: `evidence-verify <package>` which validates content digests, the manifest signature, the qualified timestamp token, the hash-chain linkage, and inclusion in the published daily Merkle root. Give it to auditors and customers. It converts "trust us" into "check it yourself" and is a strong competitive differentiator.

Run continuous internal verification: a daily job that re-verifies a random sample plus the full chain-head, alerting on any discrepancy.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| COMPLIANCE-mode lock applied with a wrong (too long) retention or to the wrong data | Unremovable data; storage-limitation violation; unbounded cost | Staging period in GOVERNANCE mode; mandatory seal-preview; retention derived from policy engine, never hand-entered; bucket separation by erasability |
| Signing key compromise | Attacker can forge evidence | KMS/HSM-held sign-only key, no export, rotation with full public-key history published, qualified timestamp binds signature to a time before compromise |
| QTSP ceases operation or its certificate is revoked | Historic timestamps become harder to validate | Choose a QTSP on the EU Trusted List with long-term validation (LTV) support; store the full validation chain in the package; consider dual-QTSP timestamps for the highest-value records |
| Hash chain broken by an ingestion gap or out-of-order write | Verification failure indistinguishable from tampering | Single-writer sealer with a monotonic sequence, idempotent retries, gap detection alerting, documented chain-repair procedure that itself produces evidence |
| Erasure obligation collides with an over-broad COMPLIANCE lock | Unresolvable GDPR conflict; supervisory finding | Per-class retention design; crypto-shredding; only genuinely legally-mandated classes go in the COMPLIANCE bucket |
| Storage cost growth over 7 years | Unbudgeted cost; pressure to weaken retention | Lifecycle transition to S3 Glacier Instant/Flexible Retrieval (Object Lock is preserved across storage classes); model cost at 5× current volume |
| Automatic expiry job fails silently | Perpetual retention; Art. 5(1)(e) violation | Expiry job emits its own evidence record; alerting on non-execution; quarterly retention-conformance report |
| Nobody ever verifies the evidence until an audit, then it fails | Catastrophic loss of product credibility | Daily automated verification of a sample plus chain-head; publish verification status to customers |

## Trade-offs

- **S3 Object Lock COMPLIANCE (unbreakable, mistakes are permanent) vs. GOVERNANCE (recoverable, defeatable by a privileged insider).** **Recommendation: COMPLIANCE for sealed evidence, with a GOVERNANCE-mode staging bucket and a preview/approve step before sealing.**
- **Qualified timestamps from a QTSP (legal presumption, per-timestamp cost, external dependency) vs. self-signed timestamps (free, no legal presumption).** Daily Merkle anchoring makes the cost trivial — one timestamp per day per tenant-set. **Recommendation: qualified timestamps. This is the highest value-per-euro control in the entire architecture.**
- **Blockchain/public anchoring (strong public verifiability; cost, volatility, and an awkward conversation with crypto-firm customers about which chain) vs. QTSP.** eIDAS gives a *legal* presumption; a public chain gives a *technical* one. EU regulators recognise the former. **Recommendation: QTSP as primary; optionally publish the daily Merkle root to a public, immutable feed as a secondary anchor if customers ask.**
- **Ledger database (Amazon QLDB reached end of support in 2025; alternatives such as Trillian or an immutable-ledger product exist) vs. hash chain on standard storage.** **Recommendation: hash chain on S3 with Object Lock. Fewer dependencies, better durability, no vendor deprecation risk, and easier third-party verification.**
- **7-year retention for everything (simple, safe) vs. per-class retention (compliant with storage limitation, complex).** Blanket 7-year retention is a GDPR Art. 5(1)(e) violation and multiplies cost. **Recommendation: per-class policy engine.**
- **Ship the verifier as open source (trust-building, exposes format details) vs. keep it proprietary.** **Recommendation: open source. The format is not a secret, and independent verifiability is the entire point.**

## Design decisions

- **DD-15-01:** Evidence is stored as self-contained, self-verifying packages (manifest + content + signature + qualified timestamp), verifiable without access to our systems.
- **DD-15-02:** S3 Object Lock in **COMPLIANCE mode** on the evidence bucket, retain-until derived automatically from the retention policy engine, with a GOVERNANCE-mode staging step and mandatory seal-preview.
- **DD-15-03:** Per-tenant hash chain over manifests, daily Merkle root, RFC 3161 qualified timestamp from an EU QTSP on the EU Trusted List, with long-term validation data stored in the package.
- **DD-15-04:** Daily Merkle roots published to a customer-visible append-only feed for independent inclusion proofs.
- **DD-15-05:** Retention policy engine with per-record-class `min_until`/`max_until`, documented legal basis, and an automatic expiry job that emits its own evidence.
- **DD-15-06:** Erasure conflicts resolved per class: legal-obligation refusal (Art. 17(3)(b)), full deletion saga, or crypto-shredding — all three documented in the DPA.
- **DD-15-07:** COMPLIANCE-mode locking is applied only to record classes with an identified legal retention obligation; erasable classes live in separate buckets.
- **DD-15-08:** Legal hold supported at record and scope level, dual-approved, audited, and visible to the tenant.
- **DD-15-09:** Open-source `evidence-verify` CLI shipped to customers and auditors; daily automated internal verification with alerting.
- **DD-15-10:** Evidence signing keys are KMS/HSM-held, sign-only, non-exportable, rotated every 2 years with the full historical public-key set published permanently.

## References

- Regulation (EU) 2023/1114 (MiCA) Art. 68(9)
- Regulation (EU) 2024/1624 (AMLR); Directive (EU) 2024/1640 (AMLD6)
- Regulation (EU) 910/2014 as amended by Regulation (EU) 2024/1183 (eIDAS 2) — Art. 35 (qualified seals), Art. 41 (qualified timestamps); EU Trusted List of QTSPs
- Regulation (EU) 2016/679 (GDPR) Art. 5(1)(e), 17(3)(b)
- Regulation (EU) 2022/2554 (DORA) Art. 12, 13, 19; Commission Delegated Regulation (EU) 2024/1774
- RFC 3161 — Internet X.509 Time-Stamp Protocol; ETSI EN 319 421/422 (time-stamping policy and protocol profiles)
- ETSI EN 319 102-1 — signature creation and validation; ETSI TS 119 512 (preservation services)
- RFC 6962 — Certificate Transparency (Merkle tree and inclusion-proof design pattern)
- AWS S3 Object Lock documentation (COMPLIANCE vs. GOVERNANCE modes)

## Confidence level

**High** — the package format, Object Lock COMPLIANCE choice, hash chain plus Merkle anchoring, qualified timestamps under eIDAS, and the per-class erasure resolution including crypto-shredding. These are correct, defensible, and directly aligned to the cited articles.

**Medium** — the level of scrutiny a specific national competent authority would apply to crypto-shredding as satisfying an erasure request (well-recognised but not explicitly blessed in binding guidance), and the practical long-term-validation robustness of a specific QTSP over a 7-year horizon. Select the QTSP with counsel and confirm LTV support contractually.
