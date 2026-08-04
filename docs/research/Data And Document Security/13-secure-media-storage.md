# 13 — Secure Media Storage

Covers the upload → scan → store → serve pipeline for documents, images, scanned IDs and any other binary customer content.

## Best practices

- **Treat every uploaded file as hostile.** It is attacker-controlled input delivered to a parser. PDF, DOCX, XLSX and SVG parsers are among the most exploited software categories in existence.
- **Never trust client-supplied filename, extension, or `Content-Type`.** Determine type by content inspection (magic bytes), reject mismatches, and generate your own storage key.
- **Quarantine before availability.** An uploaded file is not accessible to anyone until scanning completes. This is the difference between a malware incident and a malware *distribution* incident.
- **Process untrusted content in a sandbox with no credentials and no network.** Parsing, OCR, thumbnailing and text extraction are the highest-risk code paths in the system.
- **Serve from a separate origin** with strict headers so a malicious document cannot execute against the application's origin.
- **Never store user content on the same filesystem as application code**, and never in a location that a web server can serve directly.

## EU regulatory implications

- **GDPR Art. 32** — security of processing covers the integrity of the storage pipeline; malware distribution to customers via our platform would be a reportable breach affecting them.
- **GDPR Art. 9** — scanned identity documents contain biometric facial images; where used for identification purposes this is special-category data requiring an Art. 9(2) condition and heightened measures.
- **GDPR Art. 5(1)(c)** — minimisation: do not retain the original high-resolution ID scan when a redacted derivative suffices for the compliance purpose. Challenge every retained original.
- **DORA Art. 9/10** — protection and detection; malware protection is an explicit control area in **Delegated Reg. (EU) 2024/1774**.
- **NIS2 Art. 21(2)(e)** — security in acquisition, development and maintenance; and supply-chain security for the scanning engines used.
- **MiCA Art. 68(9)** — stored documents are records; integrity over the 5–7 year retention period must be demonstrable (checksums, versioning, WORM — doc 15).
- **CRA** — if a scanning or rendering component is shipped to customers, its vulnerability handling comes into scope.

## Recommended architecture

### Upload pipeline

```
1. Client requests upload           API validates: authn, authz, tenant quota, declared type/size
                                     Issues presigned PUT to QUARANTINE bucket,
                                     TTL 5 min, single use, enforced content-length range,
                                     server-side encryption headers required
                                     ↓
2. Client PUTs directly to S3       Never through the application tier —
   (quarantine bucket)              avoids memory exhaustion and a DoS vector
                                     ↓
3. S3 event ──▶ SQS ──▶ Scanner (isolated account, no network egress, no credentials
                        beyond the specific object, ephemeral compute)
                        • Magic-byte type detection; reject on declared/actual mismatch
                        • Size and structural sanity checks
                        • Multi-engine AV scan (ClamAV + one commercial engine)
                        • Archive bomb / recursion depth / decompression ratio limits
                        • Embedded active-content detection (JS in PDF, macros in Office,
                          scripts in SVG, external entity references in XML)
                        • Optional Content Disarm & Reconstruction for high-risk types
                        ↓
4a. CLEAN  ──▶ copy to PRIMARY bucket (tenant CMK, per-document DEK, Object Lock where
               classified as evidence) ──▶ metadata row ──▶ derivation jobs ──▶ available
4b. INFECTED ──▶ move to FORENSIC bucket (separate key, restricted access), alert security,
               notify tenant admin, log to evidence store, never delete silently
4c. ERROR/TIMEOUT ──▶ retain in quarantine, alert, manual review. Fail closed: never
               default to "clean" on scanner failure.
```

### Bucket topology

| Bucket | Purpose | Key | Policy |
|---|---|---|---|
| `quarantine` | Landing zone | Platform CMK | 24h lifecycle expiry; no read access outside scanner; block all public access |
| `primary` | Clean documents | Per-tenant CMK | Versioning on; no public access; access only via presigned URLs from the document service |
| `evidence` | Immutable records | Evidence CMK | **Object Lock in COMPLIANCE mode**; no delete path (doc 15) |
| `derivatives` | Thumbnails, extracted text, previews | Per-tenant CMK | Same access controls as primary; registered in the derivative registry (doc 06) |
| `forensic` | Infected/suspicious files | Separate CMK, security-team access only | Retained 90 days; never served |

All buckets: Block Public Access enabled at the account level (not just bucket level), TLS-only bucket policy (`aws:SecureTransport`), `aws:PrincipalOrgID` condition, access logging to the log-archive account, and MFA-delete or a deny-delete policy on evidence.

### Sandboxed processing

The document processor (parse, OCR, thumbnail, text extract) runs:
- In a **separate AWS account** with no access to production data beyond the single object it is processing.
- With **no network egress at all** (no NAT, no VPC endpoint except the specific S3 path and KMS).
- As **ephemeral, single-use compute** — a Fargate task or Lambda per document, never a long-lived worker that accumulates state across tenants.
- With a **read-only root filesystem**, non-root user, dropped capabilities, seccomp profile, and strict memory/CPU/time limits (a parser hitting a limit is a signal, not just a failure).
- Using **memory-safe parsers where available** (Rust-based PDF and image libraries) in preference to historically vulnerable C libraries; where a C library is unavoidable, it runs in a WASM sandbox or a dedicated microVM.

This design means a successful parser exploit yields: one document's plaintext, no credentials, no network, and a container that dies in seconds. That is an acceptable worst case.

### Serving

- **Presigned GET URLs, TTL ≤60 seconds, single-use**, generated per request after a full authorisation decision (doc 12). Never cached, never logged, never emailed.
- Served from a **separate origin** (`content.<product>.eu`) with:
  - `Content-Security-Policy: default-src 'none'; sandbox`
  - `X-Content-Type-Options: nosniff`
  - `Content-Disposition: attachment; filename="..."` (sanitised filename)
  - `Cross-Origin-Resource-Policy: same-site`
  - No application cookies scoped to this origin.
- **Preferred default: server-side rendering to a sanitised, watermarked image or PDF/A** shown in an in-app viewer, so the raw file is never delivered to the browser at all. Raw download is a separate, higher-friction, logged permission (doc 06).
- Range requests supported for large files; per-user and per-tenant download rate limits to bound bulk exfiltration (doc 23).

### Minimisation and redaction

- For identity documents, generate and retain a **redacted derivative** (document number and expiry visible, biometric photo and irrelevant fields masked) and set an aggressive retention on the original where the compliance purpose permits. Document the analysis per document type.
- OCR text extraction runs entity detection so that extracted text carries the same classification and pseudonymisation treatment as the source (doc 05).

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Parser exploit (PDF/image/Office zero-day) leads to RCE | Compromise of the processing tier | No credentials, no network, ephemeral compute, separate account, memory-safe parsers, resource limits |
| Malware stored and later downloaded by a customer | We become the distribution vector; severe reputational and contractual damage | Quarantine-before-availability, multi-engine scanning, fail-closed on scanner error, rescan on signature updates for recently-uploaded files |
| Stored XSS via SVG/HTML rendered in-app | Session theft, account takeover | Separate origin, CSP `sandbox`, `nosniff`, server-side rendering to image by default |
| Zip bomb / billion-laughs / recursive archive | Resource exhaustion, DoS | Decompression ratio and depth limits, hard time/memory caps, size limits at presign time |
| Presigned URL leaked via referrer header or shared link | Unauthorised access within TTL | ≤60s TTL, single use, `Referrer-Policy: no-referrer`, never in emails or logs |
| Object Lock applied to the wrong bucket in COMPLIANCE mode | Unremovable data, including data that must later be erased | Object Lock only on the evidence bucket; crypto-shredding provides the erasure path; test in GOVERNANCE mode first |
| Derivative artefacts (thumbnails, extracted text) escape access control | Silent confidentiality breach | Derivative registry; identical bucket policy, key and classification inheritance |
| Uploaded file bypasses scanning via direct presign misuse | Unscanned content in the primary bucket | Presigns are issued only for the quarantine bucket; the primary bucket accepts writes only from the scanner role |

## Trade-offs

- **ClamAV only (free, weaker detection) vs. multi-engine (better detection, cost and latency).** Compliance documents from crypto firms are a plausible malware delivery target. **Recommendation: ClamAV plus one commercial engine; run in parallel, fail closed if either times out.**
- **Content Disarm & Reconstruction (near-total active-content elimination; can break document fidelity and is not free) vs. detection-only.** For a compliance archive, document fidelity matters — a CDR-flattened PDF may lose signatures or structure needed as evidence. **Recommendation: CDR applied to the *preview derivative* only, never to the retained original.**
- **Direct-to-S3 presigned upload (scalable, no application memory pressure) vs. proxy-through-application (inspection before storage).** **Recommendation: direct-to-S3 into quarantine — inspection happens asynchronously and the DoS surface is far smaller.**
- **Server-side rendered preview (safest, compute cost, latency) vs. client-side rendering (fast, exposes the browser to the file).** **Recommendation: server-side rendered by default; client-side rendering only for plain text and pre-sanitised formats.**
- **Aggressive minimisation of ID document originals (best GDPR posture) vs. retaining originals for audit defensibility.** Customers may need the original to satisfy their own AML obligations. **Recommendation: retain originals by default with a per-tenant configurable minimisation policy, and offer redacted-derivative-only mode as a privacy-forward option.**

## Design decisions

- **DD-13-01:** Five-bucket topology (`quarantine`, `primary`, `evidence`, `derivatives`, `forensic`) with distinct keys and policies; account-level Block Public Access; TLS-only bucket policies.
- **DD-13-02:** All uploads land in quarantine via presigned PUT (TTL ≤5 min, single use, content-length range enforced). The primary bucket accepts writes only from the scanner role.
- **DD-13-03:** Multi-engine antivirus plus structural and active-content inspection; **fail closed** — scanner error or timeout never results in a file being marked clean.
- **DD-13-04:** Document processing runs in a separate AWS account, on ephemeral compute, with zero network egress and no credentials beyond the single object.
- **DD-13-05:** Content type determined by magic-byte inspection; declared/actual mismatch is rejected and logged as a security event.
- **DD-13-06:** Documents served from a dedicated content origin with `CSP sandbox`, `nosniff`, `Content-Disposition: attachment`, and no application cookies.
- **DD-13-07:** Default access mode is a server-side rendered, watermarked preview; raw download is separately permissioned and logged.
- **DD-13-08:** Recently-uploaded files are rescanned when AV signatures update (7-day rolling window) to catch same-day zero-days.
- **DD-13-09:** Redacted derivatives generated for identity documents; per-tenant configurable minimisation policy for originals.

## References

- Regulation (EU) 2016/679 (GDPR) Art. 5(1)(c), 9, 32
- Commission Delegated Regulation (EU) 2024/1774 — malware protection, data and system security
- Regulation (EU) 2022/2554 (DORA) Art. 9, 10
- OWASP File Upload Cheat Sheet; OWASP Top 10 A03/A08
- NIST SP 800-83 Rev. 1 — Guide to Malware Incident Prevention and Handling
- AWS S3: Block Public Access, Object Lock, presigned URLs, bucket policies
- CWE-434 (Unrestricted Upload), CWE-409 (Decompression Bomb), CWE-611 (XXE)

## Confidence level

**High** — the quarantine-scan-promote pipeline, sandboxed processing with no credentials or network, separate content origin, and derivative handling. These are the established answers to a well-understood threat class.

**Medium** — the correct default on ID-document minimisation (a legal and commercial judgement that varies by customer AML obligations), and the fidelity impact of CDR on specific document types, which needs testing against real customer file formats.
