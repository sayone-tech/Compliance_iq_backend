# Security Architecture — WSP Compliance Validation Platform

**Brief Sections 19, 31** · **Date:** 2026-08-17 · **Status:** Research / architecture only (no application code)

Scope: platform-level security for a multi-tenant SaaS in which regulated firms (MiCA CASPs / DORA financial entities) upload confidential Written Supervisory Procedures (WSP) manuals — 150–200pp internal compliance manuals in the FINRA Rule 3110(b) sense (see `../regulatory/wsp-meaning.md`), *not* MiCA white papers — and receive evidence-cited compliance findings. LLM-specific threats (prompt injection, hidden text, model governance, EU AI Act) are covered in **`llm-security-governance.md`** and are referenced, not duplicated, here. Data/tenancy model alignment: `../architecture/data-and-events.md`.

Design context that raises the stakes (VERIFIED FACT): customers are themselves DORA-regulated financial entities; the platform is an **ICT third-party service provider** to them under DORA Art. 28 ff., so customers will contractually demand DORA Art. 30-style terms (audit rights, incident notification, exit support, data location). The platform's security posture is therefore a sales artifact, not just hygiene. (DORA (EU) 2022/2554, https://eur-lex.europa.eu/eli/reg/2022/2554/oj, accessed 2026-08-17. Whether the platform could be designated "critical" under Art. 31 is remote at this scale — REQUIRES LEGAL REVIEW.)

Unless marked otherwise, statements below are **ARCHITECTURAL RECOMMENDATION**.

---

## 1. Encryption

**In transit.** TLS 1.3 (min 1.2) everywhere, including service-to-service inside the VPC (mTLS via mesh or app-level). HSTS; modern cipher policy on the load balancer; no plaintext internal hops carrying document text.

**At rest — layered:**
1. **Infrastructure layer:** full-disk/volume encryption (AES-256) on DB, object store, queues, backups — table stakes via cloud KMS.
2. **Per-tenant application-layer envelope encryption for document content:** each firm gets a tenant Data Encryption Key (DEK); DEKs wrapped by a Key Encryption Key in KMS/HSM (AWS KMS eu-central-1 or equivalent EU-resident HSM). WSP originals in object storage and extracted full-text blobs are encrypted with the tenant DEK before write. Benefits: cryptographic tenant separation on top of RLS, crypto-shredding on offboarding (destroy DEK ⇒ data unrecoverable, supports GDPR erasure and DORA exit obligations), per-tenant key-rotation and BYOK/HYOK as an enterprise option.
3. **What stays searchable:** chunk text, embeddings, and FTS indexes in Postgres cannot be app-layer encrypted and remain protected by RLS + volume encryption + the audit layer. This is an accepted, documented trade-off (ASSUMPTION: acceptable to target customers; enterprise DB-per-tenant path in §2 removes it). Embeddings are treated as sensitive: inversion attacks can partially reconstruct text from vectors, so vectors never leave the trust boundary and are never returned by APIs.

Key hygiene: KMS key policies scoped per environment; annual (or on-compromise) DEK rotation via re-wrap, not re-encrypt-the-world; dual control for KEK deletion; all key usage logged (CloudTrail/equivalent) into the audit pipeline (§4).

## 2. Tenant Isolation

Adopts the decision in `../architecture/data-and-events.md` (do not re-litigate):

- **Default: shared Postgres with `FORCE ROW LEVEL SECURITY`**, `firm_id` (tenant_id) on every tenant-scoped table; session GUC set from the authenticated principal by the connection layer; app roles have no BYPASSRLS; RLS enforced even for table owners (`FORCE`). Tenant predicate lives **in the database, not in prompts or app code** — this is also the anti-cross-tenant-leakage control for retrieval (llm-security-governance.md §1.3).
- Regulatory content (regulations/articles/controls) is global, read-only to tenant paths — no tenant data ever written into shared regulatory tables.
- **Enterprise exception: DB-per-tenant** (dedicated database + dedicated DEK/KEK, optionally dedicated compute) for firms whose vendor-risk teams require physical separation.
- Isolation extends beyond the DB: per-tenant object-store prefixes with IAM conditions; queue/workflow payloads carry only IDs + tenant claim, never document text; per-tenant rate limits and per-tenant LLM spend budgets (abuse/cost isolation); parsing sandboxes (§6) are single-document, single-tenant, ephemeral.
- **Isolation testing:** automated cross-tenant probe suite in CI (attempt reads/searches/citation-resolution across tenant boundary under every API route and the retrieval path); any hit is a release blocker.

## 3. Identity, RBAC/ABAC, Document Access Control

- **AuthN:** OIDC SSO (customer IdP federation for enterprise), MFA enforced, SCIM for lifecycle deprovisioning. Service-to-service auth via short-lived workload identities, not static API keys.
- **RBAC baseline (per tenant):** `org_admin`, `compliance_officer` (accept/override findings — the human-review role in llm-security-governance.md §2.4), `contributor` (upload/remediate), `viewer`, `auditor` (read-only incl. audit trail). Platform-side: `support` (no document content by default; time-boxed, ticket-bound, tenant-consented elevation — "break-glass" — fully audited), `platform_admin` (infrastructure, no content access path).
- **ABAC overlay:** attributes on documents/findings (e.g., document sensitivity, business line, draft-vs-final WSP version) evaluated by a central policy decision point; needed because large firms will restrict who sees which WSP sections/findings. Findings inherit the access policy of the WSP version they cite — a user who cannot read the document cannot read verbatim cited spans.
- **Every access decision is deny-by-default** and made server-side; object-store access only via short-TTL pre-signed URLs minted after a policy check; no direct-bucket paths in the client.

## 4. Immutable Audit Logging

Two distinct layers, both append-only:

1. **Domain audit (compliance product feature):** the existing append-only `evaluations`/`audit_log` design (REVOKE UPDATE/DELETE + trigger guard, monthly partitions — per `data-and-events.md`), plus the pinned-version eval record of llm-security-governance.md §2.1. Human overrides append with `supersedes_eval_id`, never mutate.
2. **Security audit:** authN events, permission changes, document access (who viewed/downloaded which WSP version), key usage, admin/break-glass actions, export events. Shipped near-real-time to WORM storage (S3 Object Lock compliance mode / equivalent) outside the app's blast radius; hash-chained (each batch includes the previous batch hash) so tampering is detectable; clock-synced; retained ≥ the customer-driven regulatory horizon (MiCA Art. 68(9) uses 5 years as the reference period for CASP records — customers will mirror this on vendors; exact retention REQUIRES LEGAL REVIEW).
3. Logs are **content-free** by policy (§8): identifiers, hashes, page/section refs — never WSP text.

This directly serves customers' DORA Art. 28 due-diligence questionnaires and the platform's own incident forensics.

## 5. EU Data Residency (incl. LLM processing)

- **All storage and compute pinned to EU regions** (DB, object store, queues, workflow engine, backups, log/WORM storage). Cross-region replication only EU→EU.
- **LLM inference residency is the hard part** (aligns with `data-and-events.md` §4): use provider offerings with (a) EU processing region, (b) **zero data retention / no-training contractual terms** under a DPA with SCCs where applicable. Options to evaluate: Anthropic/OpenAI zero-retention enterprise terms via EU endpoints, AWS Bedrock or Google Vertex EU regions (model runs in-region under the cloud DPA), or self-hosted open-weight models for the embedding tier (BGE-M3 already recommended self-hosted in `../ai/rag-architecture.md`, which removes embeddings from the vendor question entirely). US-parent providers remain a **Schrems II / transfer-risk question even with EU regions — REQUIRES LEGAL REVIEW**; per-tenant model-vendor configurability (already in the data design) is the pressure valve for customers who refuse a given vendor.
- **Managed OCR/extraction residency:** if a cloud extraction service is used at all, EU region + no service-improvement retention (Textract's cross-region service-improvement default must be org-opted-out; Azure EU Data Boundary preferred — per `../wsp-analysis/sample-wsp-extraction-analysis.md`, flagged REQUIRES LEGAL REVIEW there). Local-first Docling pipeline avoids this class entirely.
- Maintain a short, published **sub-processor list** with locations — DORA Art. 28 due diligence and MiCA Art. 73 outsourcing reviews by customers demand it; every added sub-processor is a sales friction, so fewer is a feature.
- OPEN QUESTION: whether any target customer requires *EU-owned* (not just EU-located) providers; drives the self-hosted-model roadmap.

## 6. Secure Parsing Sandbox (malicious/malformed PDF handling)

PDF parsers are a recurring RCE/DoS surface (decompression bombs, malformed xref, font/JBIG2 parsing bugs — cf. historical CVEs in poppler/mupdf-class libraries). Uploaded WSPs are hostile until proven otherwise.

Pipeline order:
1. **Upload validation:** size caps, MIME/magic-byte check (Tika/python-magic per extraction analysis), reject encrypted/password PDFs with a clear user message.
2. **Malware scan before any parse** (ClamAV + a commercial engine on the raw blob).
3. **Structural triage:** reject or quarantine PDFs with JavaScript, launch actions, embedded files, external references; strip annotations/XMP into a side channel (this is also hidden-text/injection input — see llm-security-governance.md §1.2).
4. **Parse inside an isolation boundary:** dedicated unprivileged container (or gVisor/Firecracker microVM) per document; **no network egress at all**; read-only rootfs; seccomp; cgroup limits on CPU/RAM/pids/time (kills decompression bombs and infinite loops); tmpfs-only scratch; output is structured JSON + page images only, never the raw file re-emitted. Sandbox is destroyed after each document.
5. Crash/timeout ⇒ quarantine + human triage, never silent retry into a different parser with elevated privileges.
6. Renderer used for the render-vs-extraction hidden-text diff runs under the same sandbox profile.

## 7. SSRF Prevention in Fetchers

(Complements llm-security-governance.md §1.3.) The **only** component with internet egress is the regulatory-ingestion fetcher (`../regulatory/regulatory-ingestion.md`); validation/parsing/LLM-orchestration workloads have **no egress** except to the LLM endpoint via a proxy.

- Static **domain allowlist** (eur-lex.europa.eu, op.europa.eu/CELLAR, esma.europa.eu, eba.europa.eu, ec.europa.eu, enumerated NCA domains); changes to the list are code-reviewed config, not runtime data.
- **Never fetch URLs found inside uploaded documents or model output** (both samples contain dead `finra.complinet.com`-era URLs — link content is data to be recorded, not dereferenced).
- Egress proxy that: resolves DNS itself and re-validates the resolved IP is public (blocks DNS-rebinding to RFC1918/169.254.169.254), forbids redirects off-allowlist, enforces HTTPS + response-size/time caps. Cloud metadata endpoints blocked at the network layer (IMDSv2-only where applicable).
- Fetched regulatory HTML/PDF is itself untrusted LLM input (already established in `regulatory-ingestion.md`).

## 8. Data-Leakage Controls (what never leaves the boundary)

Deny-list enforced by lint rules, log scrubbers, and code review:
- **Never in logs/traces/metrics/error reports:** WSP text or excerpts, extracted claims, finding rationale text, prompts/completions, embeddings, pre-signed URLs, tokens/secrets. Log identifiers + hashes + page/section pointers only. Crash reporters (Sentry-class) get scrubbed payloads; LLM requests/responses are logged only as `(eval_id, token counts, model_id, hashes)` — full payload capture only in a short-retention, EU-resident, access-controlled debug store with per-tenant consent.
- **Never in prompts:** other tenants' content (structurally impossible if retrieval is DB-filtered), platform secrets/config, sub-processor keys, internal URLs. System prompts contain no per-tenant secrets so prompt-extraction attacks yield nothing sensitive.
- **Never to the model vendor:** anything outside the pinned zero-retention path; no "improve the service" data-sharing flags.
- **Egress DLP:** exports (PDF/CSV finding reports) are watermarked per tenant/user; bulk-export is a privileged, audited action; UI renders model output as inert data (no markdown-image/URL rendering — exfil beacons, per llm-security-governance.md).

## 9. Supply Chain

- **Pinned dependencies** (lockfiles + hash pinning), private registry proxy/vendoring, no floating tags for containers (digest-pinned base images), signed builds with SBOM (CycloneDX) and provenance attestation (SLSA-aligned) so customers' DORA vendor reviews can be answered with artifacts.
- **CVE watch focused on the parser stack** (Docling/PyMuPDF-or-pdfplumber/poppler-class libs, image codecs, OCR): these process hostile input, so parser CVEs are P1; SLA: assess within 24h, patch or mitigate (sandbox already limits blast radius — §6) within days. Note PyMuPDF is AGPL (license risk flagged in extraction analysis — REQUIRES LEGAL REVIEW; MIT fallback pdfplumber).
- Model/weights supply chain: self-hosted weights (BGE-M3, reranker) pulled from pinned revisions with checksum verification; prompt templates versioned and change-gated like code (they are code).
- CI hardening: minimal-permission tokens, no secrets in forks/PRs, dependency-review gates, admission control that only signed images deploy.

## 10. Secrets Management

- Central secrets manager (Vault / AWS Secrets Manager, EU region); **no secrets in env-baked images, code, or CI variables**; runtime injection with short TTLs.
- Prefer **no long-lived credentials at all:** workload identity/IRSA for cloud APIs, IAM-auth to Postgres where possible; LLM API keys per environment *and per tenant tier*, scoped and budget-limited, rotated automatically (90-day max, on-demand on suspicion).
- KMS/DEK material never leaves KMS/HSM (§1); DB credentials distinct per service with least-privilege grants (the append-only REVOKEs in `data-and-events.md` depend on this).
- Secret-scanning in CI and on the repo history (gitleaks-class), push protection on.

---

## 11. Threat Model

| # | Threat | Vector | Mitigations | Residual risk |
|---|--------|--------|-------------|---------------|
| T1 | Cross-tenant data disclosure | RLS bypass bug, missing `firm_id` filter, retrieval over wrong tenant, IDOR on citation/deep-link APIs | FORCE RLS + session GUC from verified principal; per-tenant DEK envelope; DB-level retrieval filtering (never prompt-level); CI cross-tenant probe suite; DB-per-tenant enterprise path | Low — a novel Postgres RLS CVE or connection-pool GUC mix-up; contained by per-tenant crypto + audit detection |
| T2 | Prompt injection via uploaded WSP (forced PASS, tool abuse) | Instructions in body text, tables, metadata, annotations | See `llm-security-governance.md` §1: data/instruction separation, no-tool core loop, schema-constrained output + deterministic span-verification gate, ingestion injection scan, red-team corpus in CI | Medium — novel injections may still bias *semantic* judgments; bounded by human-review gates and FAIL-recall bias |
| T3 | Hidden-text evasion (invisible text steering findings) | White-on-white, <4pt, off-page, Tr 3, annotation/metadata text | Render-vs-extraction diff + rule layer at ingestion; strip-and-log of non-rendered objects (`llm-security-governance.md` §1.2) | Low–medium — render-diff is probabilistic on edge cases; flagged docs quarantined |
| T4 | Malicious PDF exploits parser (RCE/DoS) | Crafted xref/fonts/streams, decompression bombs, embedded JS | Magic-byte + AV scan pre-parse; JS/embedded-file rejection; egress-less sandboxed parse (microVM/container, cgroup/seccomp limits); crash ⇒ quarantine | Low — 0-day escapes the sandbox boundary; no network + minimal kernel surface limits impact |
| T5 | SSRF / internal pivot via fetcher | Regulation-URL fetching, URLs planted in WSPs, redirects, DNS rebinding | Single egress component; static allowlist; never fetch document/model-derived URLs; resolving proxy blocking private IPs + metadata endpoints; egress-less everything else | Low — allowlisted official domain compromise; mitigated by content-hash change review + human gate in ingestion |
| T6 | Data exfiltration via model output rendering | Markdown image beacons, attacker URLs in findings UI | Output rendered inert (no images/auto-links), CSP, output URL/secret scanning pre-persistence | Low |
| T7 | LLM vendor mishandling / non-EU transfer of WSP content | Inference payloads leaving EU, retention/training use | EU-region endpoints, zero-retention DPA terms, self-hosted embeddings, per-tenant vendor choice, short sub-processor list | Medium — Schrems II legal risk is contractual/legal, not fully technical (REQUIRES LEGAL REVIEW) |
| T8 | Insider access (platform staff) to customer WSPs | Support/admin roles, DB access, log access | No-content-by-default support role; time-boxed audited break-glass; content-free logs; per-tenant DEK (DB dump alone insufficient); WORM security audit | Low–medium — collusion of KMS-privileged + DB-privileged insiders; dual control on keys |
| T9 | Audit-trail tampering (hide a bad finding/override) | UPDATE/DELETE on evaluations, log editing | Append-only enforcement (REVOKE + triggers), `supersedes_eval_id` override chain, hash-chained WORM export off-platform | Low |
| T10 | Supply-chain compromise (parser lib, model weights, CI) | Poisoned dependency/base image/weights, CI token theft | Pinned+hashed deps, digest-pinned signed images, SBOM/provenance, checksum-verified weights, parser-CVE P1 watch, least-priv CI | Medium — upstream compromise pre-pin is industry-wide; sandbox + egress controls bound the blast radius |
| T11 | Credential/secret theft | Leaked keys in code/logs, long-lived tokens | Secrets manager + workload identity, no long-lived creds, scrubbed logs, secret scanning, rotation | Low |
| T12 | Availability attack (cost/DoS) | Upload floods, giant PDFs, LLM-spend amplification | Size caps, per-tenant rate limits and LLM budgets, queue backpressure, sandbox CPU/time kills | Low — service degradation, no confidentiality impact |
| T13 | Poisoned regulatory source ingested as truth | Compromised/spoofed source page, tampered consolidated text | HTTPS+allowlist, EUR-Lex as sole authority rule, content hashing, **mandatory human review gate before control activation** (`regulatory-ingestion.md`) | Low — human gate is the backstop; wrong controls would still be caught by review before tenant impact |

---

### Cross-references
- LLM threat surface & AI governance: `llm-security-governance.md` (this doc's §§2–4 of the LLM layer)
- Tenancy, append-only schema, EU pinning decisions: `../architecture/data-and-events.md`
- Retrieval/verification gates: `../ai/rag-architecture.md`
- Extraction stack & OCR residency: `../wsp-analysis/sample-wsp-extraction-analysis.md`
- Ingestion trust model & human gate: `../regulatory/regulatory-ingestion.md`

### Sources (accessed 2026-08-17)
- DORA (EU) 2022/2554 (ICT third-party risk, Arts. 28–30): https://eur-lex.europa.eu/eli/reg/2022/2554/oj
- MiCA (EU) 2023/1114 (Art. 68(9) record-keeping, Art. 73 outsourcing): https://eur-lex.europa.eu/eli/reg/2023/1114/oj/eng
- OWASP Top 10 for LLM Applications 2025: https://genai.owasp.org/llmrisk/llm01-prompt-injection/ (best practice, not regulation)
- GDPR (EU) 2016/679 (Art. 32 security of processing; transfer rules Ch. V): https://eur-lex.europa.eu/eli/reg/2016/679/oj

*EUR-Lex texts are the only regulatory authority cited; all vendor/OWASP material is best-practice guidance. Sample WSPs referenced only as test artifacts; both were probed read-only and neither contained instruction-like (prompt-injection) text — they remain treated as untrusted data.*
