# Document Confidentiality and Tenant Isolation

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

Uploaded evidence is the crown jewels: whatever a compliance officer attaches to prove a control operated — KYC extracts, board minutes, custody attestations, system reports, screen recordings, regulator correspondence (the PRD's testing workflow step 5, the accepted evidence file type list). Alongside it sit WSP manuals (the single WSP upload requirement), licence documents (the licence capture requirement), staff records including qualifications and hardware (the staff record fields requirement) and generated reports (the report contents requirement). A single cross-firm leak would end the product.

**The governing PRD requirement is the tenant isolation requirement:** *"Every client firm's data is held in complete isolation from every other firm… No firm can ever access another firm's data, even accidentally."*

## Best practices

- **Classify at ingest, enforce by class.** Every stored object carries a machine-readable classification that drives key selection, access rules, export permissions, watermarking and AI eligibility.
- **Tenant isolation is the primary control; defence in depth is the backup.** Enforce at four layers — application, database, storage/key, and identity — so that a bug at one layer is not sufficient.
- **Never serve documents from a guessable or enumerable path.** Opaque identifiers, authorisation checked on every access, short-lived signed URLs only.
- **Separate the content plane from the metadata plane.** Metadata is queried constantly; content is fetched rarely and under stricter control.
- **Make derived artefacts first-class.** Thumbnails, extracted text, OCR output, search index entries, cached previews and any embeddings are copies of the confidential source and must inherit its classification, key and access behaviour. Forgotten derivatives are the most common real-world leak.
- **Watermark and track.** Per-user watermarks on previews and exports; every view, download and export logged (this also serves the permanent audit log requirement).

## Regulatory implications

- **GDPR Art. 5(1)(f), Art. 32** — integrity and confidentiality; encryption and pseudonymisation named explicitly. The encryption requirement already mandates the encryption.
- **GDPR Art. 9** — evidence uploads may contain special-category data (identity documents, health-related context in staff records). The accepted evidence file type list permits arbitrary file types, so the platform cannot assume otherwise; the controller (the firm) needs an Art. 9(2) condition.
- **GDPR Art. 15/17/20** — access, erasure and portability requests must reach *every* copy including derivatives and indexes. **But see the retention conflict below: the PRD forbids deletion of most of this material.**
- **GDPR Art. 33/34** — a cross-firm exposure would almost certainly be a high-risk breach requiring notification.
- **the PRD's data and retention table** — the retention table: evidence files, test results, findings, remediation evidence, reports and audit logs are retained a **minimum of six years** and **cannot be deleted**.

### The erasure conflict — recorded, not resolved

the PRD's data and retention table and the non-deletable retention requirement state that evidence files, results, reports and audit records **cannot be deleted by anyone**. That is the requirement this design implements.

Where a data subject asserts an erasure right over material inside that set, the conflict is real and is **an open legal and product question** (`regulatory-obligations`, `open-questions` L-3). This research set does **not** adopt crypto-shredding, deletion sagas, soft-delete grace periods or any other mechanism that would render PRD-protected records unreadable. Any such mechanism would need the Client's explicit decision because it contradicts the non-deletable retention requirement on its face.

What *can* be designed now without prejudging the answer:

- A **record-class registry** distinguishing PRD-protected classes from classes with no retention obligation (for example, marketing contacts, or draft uploads never attached to a test). **[PROPOSED]**
- A **deletion capability that exists only for the unprotected classes**, with verified fan-out across derivatives, indexes and caches, and a deletion record. **[PROPOSED]**
- A **documented refusal path** for erasure requests touching protected classes, giving the controller the record class, the retention basis and the expiry date. **[PROPOSED]**

## Recommended architecture

### Classification model **[PROPOSED, implementing the tenant isolation requirement/the encryption requirement]**

| Class | ComplianceIQ examples | Key | AI eligible | Export | Deletion |
|---|---|---|---|---|---|
| `PUBLIC` | Platform templates: revenue-source Excel template (the revenue file requirement), staff CSV template (the staff import requirement), evidence checklist format (the document checklist requirement) | Platform key | Yes | Free | Deletable |
| `INTERNAL` | Firm profile, service-line configuration, testing calendar, notification settings | Firm key | Not applicable | Firm users | Deletable where no retention basis |
| `CONFIDENTIAL` | WSP manuals and versions (the single WSP upload requirement, the permanent WSP version history requirement), test executions, findings, remediation records, generated reports (the report contents requirement) | Firm key | WSP only, and only for the advisory AI mapping requirement mapping | Role-based, logged | **Non-deletable** (the PRD's data and retention table) |
| `RESTRICTED` | Evidence files and remediation evidence (the accepted evidence file type list, the remediation evidence requirement), licence documents (the licence capture requirement), staff records with qualifications and hardware (the staff record fields requirement) | Firm key + per-object data key | **No** | Step-up authentication, watermarked, logged | **Non-deletable** (the PRD's data and retention table) |

Classification is assigned at ingest from the upload context (which module, which test step, which record type), can be escalated by automated content inspection but never lowered without dual approval, and is enforced by the authorisation layer on every access.

A separate `PRIVILEGED` class for legally privileged material is **[FUTURE]** — the PRD does not distinguish it, though "Regulatory Organisation Responses" and regulator correspondence (the PRD's distribution list section) suggest it may become relevant.

### Isolation layers **[PROPOSED, implementing the tenant isolation requirement]**

1. **Application layer.** All document access flows through a single repository component requiring an authenticated tenant context. No raw query access to document tables. Enforced by a custom static-analysis rule (`secure-sdlc`) and by making the raw client unreachable outside the repository package.
2. **Database layer.** Row-level security enabled and forced on every tenant-scoped table; the application connects as a role that cannot bypass it; the tenant identifier is set per transaction from the validated session. This is the safety net for an application-layer bug.
3. **Storage and key layer.** Object keys prefixed per firm; server-side encryption with the **per-firm key mandated by the encryption requirement**; the key policy scoped so a service credential can only decrypt for the firm in its request context — that is, the firm identifier is bound into the encryption context and required by the key policy condition. A leaked object reference is useless without the matching key grant.
4. **Identity and network layer.** Service roles scoped per environment; no wildcard storage or key permissions; private service endpoints with policies restricting to the platform's own buckets and keys.

### Access path **[PROPOSED]**

```
Client ──▶ API (authn: session + MFA per the phone-based second factor requirement; authz: policy layer per the automatic role enforcement requirement)
              │  decision inputs: user, system role, firm, class, purpose, device posture
              ▼
        Document service ── audit event (who / what / when / from which device) ──▶ audit log (the permanent audit log requirement)
              │
              ├─ metadata from the database (row-level security enforced)
              └─ content: signed GET, short TTL, single use, attachment disposition,
                 served from a separate origin
```

- **Preview over download.** Default rendering is a server-side, sanitised viewer with a per-user watermark (user, firm, timestamp, document ID). Raw download is a separate, higher-friction, logged permission. **[PROPOSED]**
- **Separate content origin** with a strict content-security policy, no MIME sniffing, sandboxed rendering, and no application cookies — this prevents stored-script-in-document attacks against the application origin.
- **Purpose binding.** Access requests carry a purpose (test execution, review, report generation, remediation validation, support). Purpose is logged and, for `RESTRICTED`, drives additional checks.

### Derivative registry **[PROPOSED]**

Every derived artefact is recorded: source document, derivative type, storage location, key identifier, creation time. Legal hold, reclassification and key rotation iterate this registry. Derivative creation outside the single derivation service is blocked by design and detected by reconciliation. This matters more here than in most products because the single WSP upload requirement requires OCR of scanned PDFs, producing a full plaintext copy of the WSP.

### Support access to firm data

Sosinna's team can see a firm list, jurisdiction, services and last-use date (the Portal firm-visibility statement) but **the PRD marks the wider visibility boundary as an open question** — the 25 Jun call recorded a preference for seeing "pretty much everything", and month-end usage reporting was added (the Portal system settings requirement) with the explicit note that firms will not want their uploaded evidence visible to the Portal team, to be handled contractually rather than as a per-firm toggle. **The technical boundary between the Platform Admin Portal and firm evidence is therefore [OPEN]** and must be settled before the Portal's data-access layer is built. See `open-questions`, P-2.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Cross-firm access via an application bug | Catastrophic; breach of the tenant isolation requirement | Four-layer isolation; forced row-level security; mandatory cross-tenant negative tests per endpoint; per-firm keys with context binding |
| Derivative artefact leaks (cached thumbnail, OCR text in a shared index) | Confidentiality breach, often undetected | Derivative registry; classification and key inheritance; per-firm index namespaces |
| Signed URL leaked via referrer, log or shared link | Unauthorised access within the TTL | Short TTL, single use, never logged, never emailed |
| Stored script in an uploaded HTML/SVG document rendered in-app | Session theft, lateral access | Separate content origin, sanitising renderer, strict CSP, no sniffing (`secure-media-storage`) |
| Insider bulk export | Mass exfiltration | Rate limits, bulk-export approval, watermarking, access logging (`insider-threat-protection`, `data-loss-prevention`) |
| Portal team gains unintended visibility of firm evidence | Contractual and confidentiality breach | Resolve the Portal firm-visibility statement/the Portal system settings requirement boundary **before** building the Portal data layer; enforce it in the authorisation layer, not in the UI |
| A deletion path is built for a PRD-protected class | Breach of the non-deletable retention requirement / the PRD's data and retention table | Record-class registry; static-analysis rule forbidding delete/overwrite on protected classes; tests asserting deletion fails |
| Erasure request received for protected material | Unresolvable without a decision | Documented refusal path; escalate as an open legal question — do not build a shredding mechanism unilaterally |

## Trade-offs

- **Per-firm key (mandated) plus per-object data keys (extra layer, more metadata) vs. per-firm key alone.** The encryption requirement requires the per-firm key. Per-object data keys add granularity and make key rotation cheap under envelope encryption. Recommendation: per-firm key universally, per-object data keys for `RESTRICTED`. **[PROPOSED]**
- **Preview-only default vs. direct download.** Recommendation: watermarked preview default; download as a separate permission. **[PROPOSED]**
- **Row-level security (defence in depth, some query-planning cost) vs. application-only enforcement.** It has caught real bugs in production systems. Recommendation: enable and force it. **[PROPOSED]**
- **Auto-classification by content inspection vs. user-declared only.** Recommendation: both — the upload context declares, automated inspection may only escalate. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification | Basis |
|---|---|---|---|
| DD-06-01 | Complete data isolation between firms is the primary security property of the platform | **[PRD REQUIRED]** | Tenant isolation requirement |
| DD-06-02 | Four-level classification assigned at ingest, escalatable but not lowerable without dual approval, enforced on every access | **[PROPOSED]** | implements the tenant isolation requirement |
| DD-06-03 | Four-layer tenant isolation: repository pattern, forced row-level security, per-firm key with firm-bound encryption context, scoped identity and endpoint policies | **[PROPOSED]** | implements the tenant isolation requirement, the encryption requirement |
| DD-06-04 | Evidence, results, reports and audit records have **no deletion path** for any principal, including administrators | **[PRD REQUIRED]** | Non-deletable retention requirement, the permanent audit log requirement, the PRD's data and retention table |
| DD-06-05 | Signed URLs only: short TTL, single use, never logged, never emailed | **[PROPOSED]** | — |
| DD-06-06 | Watermarked in-app preview is the default access mode; raw download is separately granted and logged | **[PROPOSED]** | — |
| DD-06-07 | Documents served from a dedicated content origin with strict CSP and sandboxed rendering | **[PROPOSED]** | — |
| DD-06-08 | Derivative registry mandatory; no derivative created outside the derivation service; periodic reconciliation | **[PROPOSED]** | — |
| DD-06-09 | Deletion capability exists only for record classes with no retention obligation, with verified fan-out and a deletion record | **[PROPOSED]** | consistent with the non-deletable retention requirement |
| DD-06-10 | Erasure requests touching PRD-protected classes follow a documented refusal path; no shredding or soft-delete mechanism is adopted | **[OPEN — LEGAL]** | conflict recorded, not resolved |
| DD-06-11 | The Platform Admin Portal's visibility of firm data is enforced in the authorisation layer; the boundary itself is unresolved | **[OPEN]** | Portal firm-visibility statement, the Portal system settings requirement |

## References

- Regulation (EU) 2016/679 (GDPR) Art. 5, 9, 15, 17, 25, 32, 33, 34
- Commission Delegated Regulation (EU) 2024/1774 — data and system security *(design reference)*
- ISO/IEC 27001:2022 Annex A 5.12 (classification), 5.13 (labelling), 8.12 (data leakage prevention)
- PostgreSQL Row-Level Security documentation
- AWS KMS encryption context and key policy documentation
- OWASP Application Security Verification Standard — Access Control and File Handling chapters

## Confidence level

**High** — layered isolation, per-firm keys with context binding, the derivative registry, and preview-with-watermark. Proven patterns for exactly this workload, and directly aligned with the tenant isolation requirement and the encryption requirement.

**Not determined** — the erasure-versus-retention resolution, and the Platform Admin Portal's visibility boundary. Both are recorded as open questions rather than answered here.
