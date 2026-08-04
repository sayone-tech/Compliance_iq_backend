# Secure Media Storage

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

Covers the upload → scan → store → serve pipeline for every file the platform accepts.

## What the PRD requires

| PRD ref | Requirement |
|---|---|
| FR-24 | Accepted evidence types: **PDF, .docx, .xlsx, PNG, JPG, MP3, WAV, MP4, MOV, AVI, screen recordings, ZIP archives, CSV**. Maximum file size is set in platform configuration and adjustable without a code change |
| NFR-11 | The maximum evidence file size is a configuration setting managed in the Platform Admin Portal; the initial limit is set from infrastructure cost modelling |
| FR-30 | WSP upload accepts `.docx`, PDF and **scanned PDF, read via OCR** |
| FR-02 | Optional upload of the regulator licence document (PDF) |
| FR-04, FR-62 | Structured uploads: revenue-source Excel template, staff CSV template |
| §7.1 step 5 | "All uploads are non-deletable and permanently linked to the test" |
| PRD §2, NFR-07 | Evidence files: minimum six years, **cannot be deleted by anyone** |
| NFR-02 | Evidence stored in encrypted object storage with per-firm encryption keys |
| FR-28 | Evidence has a shelf life; the platform tracks age and alerts before validity lapses. **This is an alerting feature, not a deletion feature** |

**The accepted type list is unusually broad for a compliance product.** Video, audio, screen recordings and ZIP archives are all attacker-friendly formats, they are large, and they must be retained unaltered for at least six years. That combination drives most of the design below.

## Best practices

- **Treat every uploaded file as hostile.** It is attacker-controlled input delivered to a parser. PDF, Office, image, media-container and archive parsers are among the most exploited software categories in existence.
- **Never trust client-supplied filename, extension or content type.** Determine type by content inspection, reject mismatches, generate the storage key server-side.
- **Quarantine before availability.** An uploaded file is not accessible to anyone until scanning completes. That is the difference between a malware incident and a malware *distribution* incident.
- **Process untrusted content in a sandbox with no credentials and no network.** Parsing, OCR, thumbnailing and media transcoding are the highest-risk code paths in the system.
- **Serve from a separate origin** with strict headers so a malicious document cannot execute against the application origin.
- **Never store user content on the same filesystem as application code**, and never where a web server can serve it directly.

## Regulatory implications

- **GDPR Art. 32** — the integrity of the storage pipeline; distributing malware to customers through the platform would be a reportable breach affecting them.
- **GDPR Art. 9** — evidence uploads may include identity documents containing biometric facial images; the controller (the firm) needs an Art. 9(2) condition, and the platform owes heightened measures.
- **GDPR Art. 5(1)(c)** — minimisation. Note the tension: minimisation would argue for discarding an original once a redacted derivative suffices, but **PRD §7.1 and NFR-07 forbid deleting evidence**. The PRD wins; see the note below.
- **Delegated Reg. (EU) 2024/1774** — malware protection is an explicit control area. *(Design reference.)*
- **PRD §2 / NFR-07** — stored files are records; their integrity across the six-year retention period must be demonstrable (`immutable-evidence-retention`).

> **Minimisation vs. non-deletability.** Earlier drafts of this research proposed retaining a redacted derivative and applying aggressive retention to the original identity document. **That is incompatible with PRD §7.1 step 5 and NFR-07.** Redacted derivatives may be generated *in addition* to the original, for display purposes; the original is retained. Whether the firm should be discouraged at upload time from attaching more personal data than the test requires is a **product** question worth raising. **[OPEN]**

## Recommended architecture

### Upload pipeline **[PROPOSED]**

```
1. Client requests upload        API validates authentication, authorisation, firm quota,
                                 declared type against FR-24, and declared size against the
                                 NFR-11 configured maximum. Issues a short-lived, single-use
                                 pre-signed PUT to the QUARANTINE bucket with an enforced
                                 content-length range and required encryption headers
                                     ↓
2. Client PUTs directly to       Never through the application tier — avoids memory exhaustion
   quarantine storage            and a denial-of-service vector, which matters with video files
                                     ↓
3. Event ──▶ queue ──▶ Scanner   Isolated account. No network egress, no credentials beyond the
                                 single object, ephemeral compute
                                 • Content-based type detection; reject on declared/actual mismatch
                                 • Structural sanity checks per format
                                 • Multi-engine malware scan
                                 • Archive recursion depth and decompression-ratio limits (ZIP is
                                   an accepted type — FR-24)
                                 • Embedded active-content detection: scripts in PDF, macros in
                                   Office, scripts in SVG, external entity references in XML
                                 • Media container validation for MP4/MOV/AVI/MP3/WAV
                                     ↓
4a. CLEAN     ──▶ PRIMARY bucket (firm key, per-object data key, write-once retention where the
                  object is evidence) ──▶ metadata row ──▶ derivation jobs ──▶ available
4b. INFECTED  ──▶ FORENSIC bucket (separate key, restricted access), alert, notify the Firm Super
                  Admin, record the event. Never silently discarded — and note that a rejected
                  upload never became evidence, so NFR-07 does not attach to it
4c. ERROR     ──▶ Remain in quarantine, alert, manual review. **Fail closed** — a scanner failure
                  never results in a file being marked clean
```

### Bucket topology **[PROPOSED]**

| Bucket | Purpose | Key | Policy |
|---|---|---|---|
| `quarantine` | Landing zone | Platform key | Short lifecycle expiry; no read access outside the scanner; public access blocked |
| `primary` | Clean files | Per-firm key | Versioning on; access only via signed URLs issued by the document service |
| `evidence` | Records under the PRD's six-year non-deletability rule | Evidence key | **Write-once retention with no delete path for any principal** (`immutable-evidence-retention`) |
| `derivatives` | Thumbnails, extracted text, OCR output, previews, transcodes | Per-firm key | Same access controls as primary; registered in the derivative registry (`document-confidentiality`) |
| `forensic` | Infected or suspicious files | Separate key, security access only | Retained for a defined investigation period; never served |

All buckets: public access blocked at account level, transport-security-only policies, organisation conditions, access logging to the log-archive account.

### Sandboxed processing **[PROPOSED]**

The processor (parse, OCR, thumbnail, text extract, transcode) runs:

- In a **separate account** with no access to production data beyond the single object being processed.
- With **no network egress** except the specific storage and key paths it needs.
- As **ephemeral, single-use compute** — one task per file, never a long-lived worker accumulating state across firms.
- With a read-only root filesystem, non-root user, dropped capabilities, restrictive syscall profile, and strict memory, CPU and time limits. A parser hitting a limit is a signal, not just a failure.
- Using **memory-safe parsers where available**, in preference to historically vulnerable native libraries; where an unsafe library is unavoidable, run it inside an additional sandbox.

A successful parser exploit then yields: one file's plaintext, no credentials, no network, and a container that dies in seconds. That is an acceptable worst case.

**OCR deserves specific attention** (FR-30): OCR output is a full plaintext copy of a firm's compliance manual. It inherits the source classification, the firm key and the derivative registry entry, and it is the text that feeds the FR-31 mapping path — which makes it the injection surface described in `ai-governance`.

### Serving **[PROPOSED]**

- **Signed GET URLs, short TTL, single use**, issued per request after a full authorisation decision (`zero-trust-architecture`). Never cached, never logged, never emailed.
- Served from a **separate origin** with a restrictive content-security policy, no MIME sniffing, attachment disposition with a sanitised filename, and no application cookies scoped to that origin.
- **Preferred default: server-side rendering to a sanitised, watermarked preview** for documents and images, so the raw file is never delivered to the browser. Raw download is a separate, higher-friction, logged permission (`document-confidentiality`).
- **Media (MP4/MOV/AVI/MP3/WAV) is the exception** — it must be streamed to a player. Serve it from the separate origin with range requests, transcode to a normalised profile for playback, retain the original untouched, and apply per-user download rate limits.
- Per-user and per-firm download rate limits to bound bulk exfiltration (`data-loss-prevention`).

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Parser or media-container exploit yields remote code execution | Compromise of the processing tier | No credentials, no network, ephemeral compute, separate account, memory-safe parsers, resource limits |
| Malware stored and later downloaded by a firm user | The platform becomes the distribution vector | Quarantine before availability, multi-engine scanning, fail-closed on scanner error, rescan recent uploads when signatures update |
| Stored script via SVG or HTML rendered in-app | Session theft, account takeover | Separate origin, sandboxed CSP, no sniffing, server-side rendering by default |
| Archive bomb or recursive ZIP | Resource exhaustion; availability incident against NFR-08 | Decompression ratio and depth limits, hard time and memory caps, size limit enforced at pre-sign time per NFR-11 |
| Signed URL leaked via referrer or a shared link | Unauthorised access within the TTL | Short TTL, single use, no-referrer policy, never in emails or logs |
| Write-once retention applied to the wrong bucket | Unremovable data in a class with no retention basis | Apply write-once retention only to the evidence class; stage the rollout (`deployment-recommendations`) |
| Derivative artefacts escape access control | Silent confidentiality breach | Derivative registry; identical bucket policy, key and classification inheritance |
| Upload bypasses scanning via pre-sign misuse | Unscanned content in the primary bucket | Pre-signs issued only for quarantine; the primary bucket accepts writes only from the scanner role |
| Large media files blow the cost model | Unbudgeted storage growth over six years | NFR-11 configurable ceiling; model storage at multiples of projected volume before setting it |

## Trade-offs

- **Single scanning engine vs. multiple.** Compliance documents from crypto firms are a plausible malware delivery target. Recommendation: an open-source engine plus one commercial engine in parallel, failing closed if either times out. Cost is a Client decision. **[PROPOSED / OPEN]**
- **Content disarm and reconstruction vs. detection only.** Flattening a PDF can destroy signatures and structure that make it useful evidence. Recommendation: apply disarming to the **preview derivative only, never to the retained original** — which is also what NFR-07 requires. **[PROPOSED]**
- **Direct-to-storage pre-signed upload vs. proxying through the application.** Recommendation: direct-to-quarantine; inspection happens asynchronously and the denial-of-service surface is far smaller, which matters with video. **[PROPOSED]**
- **Server-side rendered preview vs. client-side rendering.** Recommendation: server-side by default; client-side only for plain text and pre-sanitised formats; media streamed from the separate origin. **[PROPOSED]**
- **How large the configured maximum file size should be.** NFR-11 makes it configurable and defers the number to infrastructure cost modelling. **The number itself is [OPEN]** and should be set from measured storage and egress cost against the six-year retention obligation.

## Design decisions

| ID | Decision | Classification | Basis |
|---|---|---|---|
| DD-13-01 | The platform accepts exactly the FR-24 file type list; anything else is rejected at upload | **[PRD REQUIRED]** | FR-24 |
| DD-13-02 | Maximum file size is a Portal-managed configuration value, changeable without a code release | **[PRD REQUIRED]** | NFR-11, FR-24 |
| DD-13-03 | Uploaded evidence is non-deletable and permanently linked to its test | **[PRD REQUIRED]** | PRD §7.1 step 5, NFR-07 |
| DD-13-04 | Five-bucket topology (`quarantine`, `primary`, `evidence`, `derivatives`, `forensic`) with distinct keys and policies | **[PROPOSED]** | — |
| DD-13-05 | All uploads land in quarantine via a short-lived single-use pre-signed PUT with an enforced size range; the primary bucket accepts writes only from the scanner role | **[PROPOSED]** | — |
| DD-13-06 | Multi-engine malware scanning plus structural and active-content inspection; **fail closed** on scanner error or timeout | **[PROPOSED]** | — |
| DD-13-07 | File processing runs in a separate account on ephemeral compute with zero network egress and no credentials beyond the single object | **[PROPOSED]** | — |
| DD-13-08 | Content type determined by content inspection; declared/actual mismatch rejected and logged as a security event | **[PROPOSED]** | — |
| DD-13-09 | Files served from a dedicated content origin with sandboxed CSP, no sniffing, attachment disposition and no application cookies | **[PROPOSED]** | — |
| DD-13-10 | Default access mode is a server-side rendered, watermarked preview; raw download is separately permissioned and logged; media is streamed from the content origin | **[PROPOSED]** | — |
| DD-13-11 | Recently uploaded files are rescanned when malware signatures update | **[PROPOSED]** | — |
| DD-13-12 | OCR output and every other derivative inherits the source classification, firm key and registry entry | **[PROPOSED]** | supports FR-30, NFR-01 |
| DD-13-13 | The configured maximum file size value | **[OPEN]** | NFR-11 defers it |

## References

- Regulation (EU) 2016/679 (GDPR) Art. 5(1)(c), 9, 32
- Commission Delegated Regulation (EU) 2024/1774 — malware protection, data and system security *(design reference)*
- OWASP File Upload Cheat Sheet; OWASP Top 10 A03/A08
- NIST SP 800-83 Rev. 1 — Guide to Malware Incident Prevention and Handling
- CWE-434 (Unrestricted Upload), CWE-409 (Decompression Bomb), CWE-611 (XXE)
- AWS S3: Block Public Access, Object Lock, pre-signed URLs, bucket policies

## Confidence level

**High** — the quarantine-scan-promote pipeline, sandboxed processing with no credentials or network, the separate content origin, and derivative handling. These are the established answers to a well-understood threat class, and FR-24's breadth makes them more necessary here than usual.

**Medium** — the scanning and processing cost profile for the media formats FR-24 admits, and the right value for the NFR-11 size ceiling. Both need measurement against real customer file mixes.
