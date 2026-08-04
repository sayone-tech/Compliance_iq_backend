# 06 — Document Confidentiality

Uploaded documents are the crown jewels: KYC packs, board minutes, custody attestations, audit findings, wallet policy documents, regulator correspondence. A single cross-tenant leak ends the company.

## Best practices

- **Classify at ingest, enforce by class.** Every document carries a machine-readable classification that drives encryption key selection, retention, access rules, export permissions, watermarking and AI eligibility.
- **Tenant isolation is the primary control, defence-in-depth is the backup.** Enforce at four layers: application (repository pattern), database (row-level security), storage (per-tenant key + key policy), and network/identity (scoped credentials). A bug at one layer must not be sufficient.
- **Never serve documents from a path that can be guessed or enumerated.** Opaque, unguessable identifiers (UUIDv4/ULID); authorisation checked on every access; short-lived signed URLs only.
- **Separate the content plane from the metadata plane.** Metadata (title, tags, classification) is queried constantly; content is fetched rarely and under stricter control. Different keys, different access paths, different logging.
- **Make derived artefacts first-class.** Thumbnails, extracted text, OCR output, embeddings, search index entries and cached previews are all copies of the confidential document and must inherit its classification, key, retention and deletion behaviour. Forgotten derivatives are the most common real-world leak.
- **Watermark and track.** Dynamic per-user watermarks on previews and exports; track every view/download/export.

## EU regulatory implications

- **GDPR Art. 5(1)(f), Art. 32** — integrity and confidentiality; encryption and pseudonymisation named explicitly. **Art. 9** — KYC documents routinely contain special-category data (biometric passport photos, health-related PEP context, biometric facial images from ID verification), raising the bar and requiring an Art. 9(2) condition.
- **GDPR Art. 15/17/20** — access, erasure and portability must reach *every* copy including derivatives, backups and search indexes. Design deletion as a fan-out job with verifiable completion, not a single `DELETE`.
- **GDPR Art. 33/34** — a cross-tenant document exposure is almost certainly a high-risk breach requiring notification to both the supervisory authority (72h) and data subjects.
- **DORA Art. 9(2)/(4)** and **Delegated Reg. (EU) 2024/1774** — data and system security, including protection of data at rest, in transit and, where relevant, in use; classification of information assets by criticality.
- **MiCA Art. 68(9)** — records retained 5 years (extendable to 7). Confidentiality obligations persist for the entire retention period, including for departed customers.
- **Professional secrecy and legal privilege** — documents may include legal advice covered by privilege. Privileged material must be separable and excludable from AI processing and from broad internal access.
- **NIS2 Art. 21(2)(h)** — policies on the use of cryptography and, where appropriate, encryption.

## Recommended architecture

### Classification model

| Class | Examples | Key | AI eligible | Export | Retention |
|---|---|---|---|---|---|
| `PUBLIC` | Published policies, marketing | Platform key | Yes | Free | Standard |
| `INTERNAL` | Templates, checklists | Tenant key | Yes | Tenant users | Standard |
| `CONFIDENTIAL` | Compliance reports, audit evidence, assessments | Tenant key | Yes | Watermarked, logged | 5–7y policy |
| `RESTRICTED` | KYC packs, ID documents, special-category data | Tenant key + per-document DEK | Only with pseudonymisation; per-tenant opt-in | Dual-approval, watermarked | Policy + legal hold |
| `PRIVILEGED` | Legal advice, regulator correspondence | Tenant key, separate key alias | **No** | Named individuals only | Policy + legal hold |

Classification is assigned at upload (user-declared + automatic content inspection), immutable downward without dual approval, and enforced by policy engine on every access decision.

### Isolation layers

1. **Application layer.** All document access flows through a single `DocumentRepository` that requires an authenticated `TenantContext`. No raw query access to document tables. Enforced by a custom SAST rule (doc 04) and by making the raw client unreachable outside the repository package.
2. **Database layer.** PostgreSQL **Row-Level Security** enabled and forced on every tenant-scoped table; the application connects as a non-superuser role that cannot bypass RLS; `app.tenant_id` set per transaction from the validated session. RLS is the safety net for an application-layer bug.
3. **Storage layer.** S3 key prefix `tenants/{tenant_id}/documents/{doc_id}`; SSE-KMS with a **per-tenant CMK**; the KMS key policy and IAM grants scoped so that a service credential can only decrypt keys for tenants in its request context (enforced via KMS **encryption context** containing `tenant_id`, and a condition on `kms:EncryptionContext:tenant_id`). A leaked object reference is useless without the matching key grant.
4. **Identity/network layer.** Service roles scoped per environment; no wildcard S3 or KMS permissions; VPC endpoints with endpoint policies restricting to our buckets and keys.

### Access path

```
Client ──▶ API (authn: OIDC + MFA; authz: policy engine)
              │  decision inputs: user, role, tenant, doc class, purpose, device posture
              ▼
        Document service ── audit event (who/what/when/why) ──▶ audit log
              │
              ├─ metadata from Postgres (RLS enforced)
              └─ content: presigned GET, TTL ≤ 60s, single-use nonce, IP-bound where feasible,
                 Content-Disposition attachment, served from a separate origin/domain
```

- **Preview over download.** Default UX renders documents in a server-side-rendered, sanitised viewer with dynamic watermark (user email, timestamp, tenant, document ID). Raw download is a separate, higher-friction, logged permission.
- **Separate content domain** (e.g. `content.<product>.eu`) with a strict CSP, `X-Content-Type-Options: nosniff`, sandboxed iframe rendering, and no cookies from the main application domain — prevents stored-XSS-via-document and cookie theft.
- **Purpose binding.** Access requests carry a purpose (`review`, `export`, `audit-response`, `support`). Purpose is logged and, for `RESTRICTED`/`PRIVILEGED`, drives additional approval.

### Derivative registry

Every derived artefact is recorded in a `document_derivatives` table: `document_id, derivative_type, storage_location, key_id, created_at`. Deletion, legal hold, reclassification and key rotation iterate this registry and record verified completion per derivative. Derivative creation outside the registry is blocked by design (single derivation service) and detected by reconciliation jobs.

### Deletion

Document deletion is a **saga** with verified completion: object + versions, all derivatives, search index entries, embeddings, caches, CDN invalidation, metadata rows, then backup expiry tracking (backups age out under their own schedule — document this honestly to customers rather than claiming instant backup erasure). A `deletion_certificate` record is written to the evidence store. **Crypto-shredding** (destroying the per-document DEK) provides immediate effective erasure for backups that cannot be selectively purged — this is the defensible answer to Art. 17 versus immutable backups.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Cross-tenant access via an application bug | Catastrophic; likely company-ending | Four-layer isolation; RLS forced; mandatory cross-tenant negative tests per endpoint; per-tenant keys with encryption-context binding |
| Derivative artefact leaks (thumbnail cached publicly, embeddings in a shared index) | Confidentiality breach, often undetected for months | Derivative registry; same key/classification inheritance; per-tenant index namespaces |
| Presigned URL leaked (referrer, logs, shared link) | Unauthorised access within TTL | TTL ≤60s, single-use, IP-bound, never logged, no URLs in emails |
| Stored XSS / malicious HTML or SVG document rendered in-app | Session theft, lateral access | Separate content origin, sanitising renderer, CSP, `nosniff`, CDR for active content (doc 13) |
| Insider bulk export | Mass exfiltration | Rate limits, bulk-export approval, UEBA baselines, watermarking, DLP (docs 17, 23) |
| Erasure request not reaching backups/derivatives | GDPR non-compliance, regulatory finding | Derivative registry + crypto-shredding + honest backup-expiry disclosure |
| Privileged legal material processed by AI or exposed in broad search | Loss of privilege, serious client harm | `PRIVILEGED` class excluded from AI and from tenant-wide search by default |

## Trade-offs

- **Per-tenant CMK (strong isolation, crypto-shredding, higher cost/ops) vs. single platform key.** At ~€1/key/month plus request costs, per-tenant keys are cheap relative to the risk. Per-*document* DEKs add another layer and enable document-level shredding at more complexity. **Recommendation: per-tenant CMK universally; per-document DEK for `RESTRICTED`/`PRIVILEGED`.**
- **Preview-only default (safer, more infrastructure) vs. direct download (simple, weak control).** **Recommendation: watermarked preview default; download as a separate permission.**
- **RLS (defence in depth, some query-planning complexity and performance cost) vs. application-only enforcement.** RLS has caught real bugs in production systems. **Recommendation: enable and force RLS.**
- **Content inspection for auto-classification (better coverage, processing of content) vs. user-declared only.** **Recommendation: both — user declares, automated inspection can only escalate classification, never lower it.**
- **Immediate hard delete vs. soft delete with grace period.** Immediate deletion is unrecoverable from user error; a grace period conflicts with erasure expectations. **Recommendation: 30-day soft delete with content already crypto-shredded at request time — the user-visible record can be restored only if the DEK destruction is deferred; make the choice per class and state it in the DPA.**

## Design decisions

- **DD-06-01:** Five-level classification (`PUBLIC`/`INTERNAL`/`CONFIDENTIAL`/`RESTRICTED`/`PRIVILEGED`) assigned at ingest, immutable downward without dual approval, and enforced by the policy engine on every access.
- **DD-06-02:** Four-layer tenant isolation: repository pattern, forced PostgreSQL RLS, per-tenant KMS CMK with `tenant_id` encryption context, scoped IAM/VPC endpoint policies.
- **DD-06-03:** Presigned URLs only: TTL ≤60 seconds, single-use, never logged, never emailed.
- **DD-06-04:** Watermarked in-app preview is the default access mode; raw download is a separately-granted, logged permission.
- **DD-06-05:** Documents served from a dedicated content origin with strict CSP and sandboxed rendering.
- **DD-06-06:** Derivative registry is mandatory; no derivative may be created outside the derivation service; reconciliation runs daily.
- **DD-06-07:** Deletion implemented as a verified saga producing a deletion certificate; crypto-shredding provides erasure guarantees for immutable backups.
- **DD-06-08:** `PRIVILEGED` documents are excluded from AI processing and from tenant-wide search by default.

## References

- Regulation (EU) 2016/679 (GDPR) Art. 5, 9, 15, 17, 20, 25, 32, 33, 34
- Regulation (EU) 2022/2554 (DORA) Art. 9; Commission Delegated Regulation (EU) 2024/1774
- Regulation (EU) 2023/1114 (MiCA) Art. 68(9)
- ISO/IEC 27001:2022 Annex A 5.12 (classification), 5.13 (labelling), 8.12 (DLP)
- PostgreSQL Row-Level Security documentation
- AWS KMS encryption context and key policy documentation
- OWASP Application Security Verification Standard — Access Control and File Handling chapters

## Confidence level

**High** — layered isolation, per-tenant keys with encryption context, derivative registry, crypto-shredding for erasure-vs-immutability, and preview-with-watermark. All are proven patterns for exactly this workload.

**Medium** — the correct default on soft-delete grace period versus immediate crypto-shred; this is a commercial and legal judgement to settle in the DPA with counsel.
