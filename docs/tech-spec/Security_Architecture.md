# ComplianceIQ – Security Architecture

**Version:** 1.0
**Status:** Baseline
**Depends On:** Technical Architecture Baseline (TAB) v2.0, Database Architecture v1.2, Backend Architecture v1.1, AI & Document Intelligence v1.1
**Audience:** Security Engineers, Backend Engineers, DevOps, Architects, Compliance/Legal

> This document defines the security controls for ComplianceIQ Phase 1: authentication and MFA, encryption key management, tenant isolation enforcement, network and API security, file upload safety, audit log integrity, AI/third-party data flow governance, GDPR data-subject-rights handling, incident response, and vulnerability management. It implements NFR-01 through NFR-11 and ADR-021, and closes gaps that no prior document addressed.

---

# 1. Purpose

Prior documents established *what* must be protected (tenant isolation, immutable audit trails, EU-resident data) but left several concrete security mechanisms unspecified. This document is the source of truth for:

- How authentication, MFA, and credential storage actually work.
- How per-tenant encryption keys are structured and rotated.
- How uploaded evidence files are screened before they enter the system.
- How the platform defends against API abuse and network-level attack.
- How the tension between GDPR erasure rights and MiCA/DORA retention obligations is handled.
- How security incidents and vulnerabilities are managed operationally, not just architecturally.

---

# 2. Guiding Security Principles (Reaffirmed from TAB v2.0 §18, ADR-021)

- JWT authentication, MFA, RBAC, immutable audit logs, TLS, AES-256 encryption at rest, Secrets Manager integration.
- Defense in depth: no single control (application check, database trigger, network rule) is trusted alone — this document extends that philosophy from Backend/Database Architecture into authentication, encryption, and network layers.
- Least privilege by default: every role (system or firm-custom) starts with the minimum access needed and is explicitly granted more, never the reverse.
- Security controls must not silently violate the platform's own data-integrity guarantees — e.g., a malware quarantine action still respects the "no evidence is ever deleted" rule (Section 8).

---

# 3. Authentication

## 3.1 Credential Storage

- Passwords hashed with **Argon2id** (memory-hard, resistant to GPU/ASIC cracking — stronger than bcrypt for this threat profile).
- Minimum 12-character password length; no arbitrary complexity rules beyond that (composition rules like "must contain a symbol" are known to push users toward predictable patterns — length is the stronger signal).
- New/changed passwords checked against a breach-list via a k-anonymity API (e.g., HaveIBeenPwned range query — only a hash prefix is ever sent externally, never the password itself).

## 3.2 Multi-Factor Authentication (FR-11)

- **TOTP (authenticator app)** is the primary second factor — not SMS. SMS OTP is vulnerable to SIM-swap attacks, a meaningful risk for a platform holding regulated financial-compliance data.
- One-time backup recovery codes (10 per user, single-use, regenerable) issued at MFA enrollment, for device-loss recovery without a support-desk bypass that could itself become an attack vector.
- MFA is mandatory for every login-capable system role (all seven login-capable roles in PRD Section 3.1) — no role is exempt, including Firm Super Admin.

## 3.3 Invitation & Onboarding Flow (FR-12)

Invitation tokens are single-use, time-limited (72 hours), and cryptographically random (not sequential/guessable). A new user cannot access anything until both their password is set **and** MFA is enrolled — partial onboarding never grants a live, unprotected session.

---

# 4. Session & Token Management

- **Access token:** short-lived JWT (15 minutes), carries `user_id`, `tenant_id`, `system_role`, `mfa_verified` claims (Backend Architecture §4.4).
- **Refresh token:** longer-lived (8 hours, matching a working day), stored server-side in a revocable token table — not a pure stateless JWT — so a refresh token can be invalidated immediately on logout, role change, or account deactivation (FR-14).
- **Forced revocation triggers:** user deactivation, role change, password change, and MFA re-enrollment all immediately invalidate all outstanding refresh tokens for that user, requiring re-authentication.
- **Concurrent sessions:** permitted (a CCO may reasonably be logged in on desktop and mobile), but every session is independently revocable and independently visible in the audit log by device fingerprint (FR-13).

---

# 5. Authorization / RBAC

Authorization enforcement is defined at the mechanism level in Backend Architecture §13 (three deliberately redundant layers: DRF permission classes, service-layer checks, database triggers). This document adds the security-specific framing:

- **Least privilege at the system-role level:** the eight system roles (PRD §3.1) are fixed, not client-editable, and each carries the minimum permission set its function requires (e.g., IT/Systems Admin cannot see compliance findings — PRD explicit).
- **Firm-role mapping cannot escalate privilege:** a firm can rename a role ("VP of Compliance") but cannot change what system role it maps to without going through Firm Super Admin action, which is itself audit-logged.
- **Portal/Firm boundary is the highest-stakes authorization boundary in the system** (TAB v2.0 §5.2) — enforced at the namespace, database-router, and tenant-context-middleware levels simultaneously (Backend Architecture §5), not by a single permission check.

---

# 6. Encryption

## 6.1 Encryption at Rest — Key Hierarchy (NFR-02)

**Decision:** AWS KMS envelope encryption, one Customer Master Key (CMK) per tenant.

- Each tenant's S3 evidence objects and any encrypted database fields (e.g., licence document references) are encrypted with a per-tenant **Data Encryption Key (DEK)**, which is itself encrypted ("wrapped") by that tenant's CMK.
- CMKs are rotated automatically on an annual cycle via KMS's built-in rotation; DEKs are re-wrapped transparently on rotation without re-encrypting the underlying data.
- This means a compromised DEK for one tenant cannot be used to decrypt another tenant's data even if an attacker somehow obtained cross-tenant database access — the encryption boundary reinforces the schema-isolation boundary (Database Architecture §2) rather than depending on it alone.

## 6.2 Encryption in Transit

TLS 1.3 for all client-to-platform and internal service-to-service traffic (Django ↔ AI Service, Django ↔ PostgreSQL where the connection crosses a network boundary). No plaintext internal traffic, even inside the VPC.

## 6.3 Secrets Management

All credentials, API keys (including AI provider keys), and database connection strings are stored in AWS Secrets Manager, never in environment variables or source control. Secrets are rotated on a defined schedule (90 days for static credentials; provider-managed rotation where the AI provider supports it).

---

# 7. Network Security

- **VPC segmentation:** PostgreSQL and the AI Service run in private subnets with no direct public route; only the Django application tier and the load balancer are internet-facing.
- **WAF (AWS WAF):** deployed in front of the Firm App, Admin Portal, and Marketing Site lead-capture endpoint. Rate-based rules throttle abusive traffic patterns before they reach the application tier at all — particularly relevant for the marketing site's public, unauthenticated demo-request form.
- **CORS:** per Backend Architecture §5.4, regex-scoped to `*.complianceiq.com` for tenant subdomains, with a separate explicit origin entry for the Admin Portal host and the Marketing Site domain (once MKT-05 is resolved).
- **DDoS protection:** AWS Shield Standard at minimum (included by default with WAF/CloudFront); Shield Advanced is a cost/roadmap decision, not a Phase 1 architectural requirement.

---

# 8. API Rate Limiting

- **Per-user/per-tenant throttling:** DRF throttle classes limit request rate per authenticated user (e.g., a sane per-minute ceiling tuned above realistic UI usage patterns, low enough to blunt credential-stuffing or scripted abuse).
- **Unauthenticated endpoints** (marketing site lead-capture, login itself): stricter IP-based throttling, since these are the only endpoints reachable without a valid session.
- **Edge-layer throttling (WAF)** is the first line of defense; **application-layer throttling (DRF)** is the second — consistent with the platform's general defense-in-depth posture.

---

# 9. File Upload Security (New — not addressed in prior documents)

Evidence and WSP uploads accept arbitrary file types (PDF, DOCX, XLSX, images, audio, video, ZIP archives — PRD FR-24), which is a real attack surface (malware payloads, zip bombs, embedded macros).

**Process:**

1. File uploads via presigned S3 URL (Backend Architecture §12) land in a **quarantine prefix**, not the final evidence location.
2. An async scan job (AWS GuardDuty Malware Protection for S3, or an equivalent ClamAV-based Lambda) runs against every uploaded object.
3. **Clean files** are moved to the tenant's encrypted evidence prefix (Section 6.1) and the `evidence` row is marked `available` — this is the point at which it becomes visible/downloadable in the platform.
4. **Infected files** are moved to a locked quarantine location (never deleted — consistent with the platform-wide no-hard-delete posture, Database Architecture §7), the `evidence` row is marked `quarantined` rather than `available`, and the uploader plus the CCO are notified. A quarantined file is never served to any user.
5. ZIP archives are scanned recursively; a ZIP bomb (extreme compression ratio) is rejected outright at the scan stage rather than being fully decompressed.

This scan step adds latency (seconds, not minutes, for typical evidence file sizes) between upload and evidence availability — acceptable given evidence isn't typically needed for immediate viewing the instant it's uploaded.

---

# 10. Audit Logging & Tamper Evidence

Builds on the append-only, trigger-enforced audit log design (Database Architecture §6, §5.9, §4.5):

- **Log integrity:** in addition to the "no UPDATE/DELETE grant" database-level enforcement, audit log exports (e.g., for a regulator request) include a cryptographic hash of the exported record set at export time, so a later dispute about whether an export was altered after the fact can be checked against the original hash.
- **SIEM/monitoring integration:** audit log write failures (which should never happen given the append-only design, but a full disk or a permissions misconfiguration are real failure modes) trigger an immediate CloudWatch alarm — a silent audit-logging failure is treated as a security incident, not just an operational one.

---

# 11. AI / Third-Party Data Flow Security

Recaps and extends AI & Document Intelligence §6 (EU-region enforcement) from the security-governance angle:

- **Subprocessor governance:** every AI provider used for any call touching tenant content is a registered subprocessor under the Data Processing Agreement (NFR-06), with its own entry in a subprocessor registry that can be surfaced to a firm on request.
- **Vendor risk assessment:** before a new AI provider or model is added to the EU-region allowlist (AI & Document Intelligence §6.2), it goes through a lightweight vendor security review (data handling terms, retention/training opt-out confirmation, region certification) — this is a governance gate on top of the code-level `ProviderRegionViolation` check, not a replacement for it.
- **No raw tenant content in observability tooling** (AI & Document Intelligence §11) is treated here as a security control, not just a data-hygiene one — observability platforms are a common breach vector precisely because they're treated as "just logs."

---

# 12. GDPR & Data Subject Rights

## 12.1 The Retention-vs-Erasure Tension

MiCA/DORA impose a minimum 6-year retention obligation on compliance records (NFR-07), enforced as immutable, non-deletable data (Database Architecture §6–7). GDPR Article 17 grants a right to erasure, but Article 17(3)(b) provides an exemption where processing is necessary for compliance with a legal obligation. **This is very likely sufficient legal basis to decline erasure of regulated compliance records** (test results, findings, evidence, audit logs, reports) — but this is a legal determination, not an engineering one, and **requires formal confirmation from Sosinna's/SayOne's legal counsel before go-live**, not an assumption baked silently into the architecture.

## 12.2 What the Architecture Supports Either Way

- **Regulated records** (as defined in PRD Section 2): fully retained, immutable, never erasable — by design, regardless of the legal conclusion above, since the 6-year retention requirement is independently mandated.
- **Non-regulated personal data** (e.g., a deactivated user's profile fields not needed for the audit trail's evidentiary value — phone number, personal email if different from the audit-logged login email): can be anonymized on request. The pattern is to null the PII fields on `platform_user`/`staff_member` while retaining the row itself (so `tenant_audit_log.actor_id` foreign keys never dangle) — "the actor record persists, the person's personal data doesn't."
- **Data Subject Access Requests (DSAR):** a firm's Firm Super Admin (or SayOne, as processor, on the firm's instruction) can generate a report of all personal data held about a given individual across `platform_user`, `staff_member`, and audit log actor references — this is a read/export capability, distinct from the erasure question above.

---

# 13. Incident Response & Breach Notification

- **GDPR 72-hour notification obligation:** any confirmed personal-data breach triggers a defined incident response runbook (detection → containment → assessment → notification), with the 72-hour regulator notification clock starting from confirmed awareness, mirroring the same urgency pattern already built for DORA major-incident handling (PRD FR-75/76) — the platform's own operational incident response follows the same discipline it enforces on client firms.
- **Severity classification:** security incidents are classified using a scheme analogous to the PRD's Finding severity model (High/Moderate/Low, PRD §8.1), so the same escalation muscle memory applies internally and externally.
- **Firm notification:** if a security incident affects tenant data, affected firms are notified without undue delay, independent of and in addition to any regulator notification obligation.

---

# 14. Vulnerability Management

- **Dependency scanning:** automated SCA (e.g., Dependabot or Snyk) runs in CI on every merge; critical/high CVEs in direct dependencies are patched within 7 days of disclosure.
- **SAST:** static analysis integrated into the CI pipeline for the Django and FastAPI codebases.
- **Penetration testing:** an annual third-party penetration test covering both the Firm Application and Platform Admin Portal, plus the tenant-isolation boundary specifically (a targeted test attempting cross-tenant data access, not just generic OWASP Top 10 coverage).
- **Patch cadence for infrastructure:** OS/container base image patching on a monthly cadence at minimum, immediate for critical CVEs.

---

# 15. Compliance Certification Roadmap (Ties to TI-03)

ISO 27001 and SOC 2 Type II remain a roadmap item (TI-03, still open per PRD Section 13.2) rather than a Phase 1 hard requirement. This document's controls (encryption key management, access logging, incident response, vulnerability management) are deliberately built to be **certification-compatible from day one** — e.g., the audit log design, the incident response runbook, and the vendor risk assessment process are all things a SOC 2 Type II audit would expect to see evidenced, so pursuing certification later is a documentation/audit exercise on top of existing controls, not a retrofit of new ones.

---

# 16. Open Items Carried Forward

| Item | Status |
|---|---|
| GDPR Art. 17(3)(b) legal sufficiency for regulated-record retention (Section 12.1) | **Requires formal legal counsel sign-off before go-live** — not an engineering decision |
| TI-03 (ISO 27001 / SOC 2 Type II required by clients?) | Open — roadmap item; Section 15 ensures controls are certification-ready regardless |
| Shield Advanced vs. Shield Standard for DDoS protection | Cost/roadmap decision, not a Phase 1 blocker |
| Malware scanning provider final selection (GuardDuty vs. ClamAV Lambda) | Implementation-phase decision; both satisfy the architectural requirement in Section 9 |
| Subprocessor registry — client-facing surfacing mechanism | Design detail for Reporting/Portal UI, not a backend blocker |

---

# 17. Version History

| Version | Date | Notes |
|---------|------|------|
| 1.0 | Jul 2026 | Initial Security Architecture: MFA method (TOTP), password/credential policy (Argon2id), token/session revocation model, per-tenant KMS envelope encryption, network/API security (WAF, rate limiting), evidence file malware-scanning flow, audit log integrity extensions, AI subprocessor governance, GDPR retention-vs-erasure analysis, incident response and breach notification process, vulnerability management program, and certification-readiness framing for the open TI-03 roadmap item. |
