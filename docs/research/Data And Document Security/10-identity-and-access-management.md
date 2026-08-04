# 10 — Identity and Access Management

## Best practices

- **One identity plane per population, both federated.** Workforce identities (us) and customer identities (them) are different problems with different threat models; do not merge them into one directory.
- **Phishing-resistant MFA is the baseline, not the premium tier.** FIDO2/WebAuthn passkeys. TOTP is a fallback; SMS is not an authentication factor for a platform holding regulated financial data.
- **No standing privilege.** Everything above read-only-metadata is granted just-in-time, time-boxed, approved and logged.
- **Authorisation is a service, not scattered `if` statements.** A central policy engine with externalised, versioned, testable policy. Scattered checks drift, and drift in a multi-tenant system means cross-tenant exposure.
- **Every access decision produces an audit event** — subject, action, resource, tenant, decision, policy version, reason.
- **Automate joiner-mover-leaver.** SCIM provisioning and deprovisioning from the HR system of record. Manual offboarding is the classic insider-threat gap (doc 17).
- **Recertify access quarterly**, with evidence retained. Regulators ask for this specifically.

## EU regulatory implications

- **DORA Art. 9(4)(c)** — access management on a need-to-know, least-privilege and segregation-of-duties basis. **Delegated Reg. (EU) 2024/1774** is prescriptive on identity management: unique identities, strong authentication for remote access and privileged access, privileged access management, periodic review of access rights, and logging of privileged activity.
- **DORA Art. 5(2)** — the management body bears final responsibility; senior accountability for access governance must be documented.
- **GDPR Art. 5(1)(f), Art. 32(1)(b)/(4)** — confidentiality, and ensuring persons acting under our authority process data only on instruction. Access control is the enforcement mechanism. **Art. 25(2)** — by default, personal data must not be accessible to an indefinite number of persons.
- **NIS2 Art. 21(2)(i)/(j)** — access control policies, asset management, and "the use of multi-factor authentication or continuous authentication solutions" — MFA is explicitly named.
- **MiCA Art. 68** — "security access protocols"; also Art. 72 conflicts of interest, which has an access-segregation dimension.
- **GDPR Art. 15** — data subject access requests require knowing precisely who accessed what; the audit trail is a compliance artefact, not just a security one.

## Recommended architecture

### Workforce identity

```
HR system (source of truth)
   └─SCIM─▶ IdP (Entra ID or Okta)  ── FIDO2 passkeys + device compliance
              ├─ SAML/OIDC ─▶ AWS IAM Identity Center ─▶ permission sets per account
              ├─ OIDC ─▶ GitHub, observability, ticketing, all internal SaaS
              └─ Conditional access: managed device, EU/India geo-fence, risk-based step-up
```

- **Groups mirror job function, not systems.** `eng-backend`, `eng-sre-eu`, `security`, `compliance`, `support-tier1`. Permission sets attach to groups; individual grants are prohibited and detected by conformance scanning.
- **Conditional access policies:**
  - Managed, compliant device required for anything above read-only.
  - **Production access requires an EU-located session** — this is where the doc 03 geographic control is technically enforced.
  - Impossible-travel, unfamiliar-location and unfamiliar-sign-in-properties trigger step-up or block.
  - Legacy authentication protocols disabled entirely.
- **Privileged Access Management:** production and key-administration roles are not assigned to anyone. They are requested through an approval workflow (ticket + justification + dual approval by EU-resident approvers), granted for ≤4 hours, session-recorded, auto-revoked. Implemented via IAM Identity Center + an approval workflow, or a PAM product.
- **Break-glass:** two sealed, offline-stored root credentials with hardware MFA, split knowledge across two officers, use triggers an immediate page to the security lead and the CTO, quarterly tested, rotated after every use.
- **Offboarding:** SCIM deprovision within 15 minutes of HR termination event; session revocation across all systems; hardware token revoked; key access reviewed; a completion checklist retained as evidence.

### Customer identity

- **Enterprise SSO from day one.** SAML 2.0 and OIDC federation to the customer's IdP, plus **SCIM** for user provisioning and — critically — deprovisioning. Regulated buyers will not accept manual user management; and a departed employee at a CASP retaining access to their compliance evidence is a finding against *them*.
- **Local accounts** (for customers without an IdP) require passkeys or TOTP; passwords follow NIST SP 800-63B (length over composition rules, breached-password checking, no forced periodic rotation).
- **Tenant-scoped roles**, mapped from customer IdP groups:

| Role | Capability |
|---|---|
| `tenant_admin` | User management, settings, key configuration, export |
| `compliance_officer` | Full document and assessment access, approve AI assessments, sign off evidence |
| `analyst` | Create/edit assessments, read documents by classification |
| `auditor` | **Read-only, time-boxed, scoped to a defined evidence set** — every access logged and surfaced to the tenant admin |
| `viewer` | Read reports only, no raw documents |

- The `auditor` role is a differentiator: external auditors and regulators need scoped, expiring, fully-logged access. Building this properly removes the "email the documents to the auditor" anti-pattern that destroys confidentiality control.
- **Step-up authentication** required for: bulk export, key configuration changes, user role changes, `RESTRICTED`/`PRIVILEGED` document access, and evidence sign-off.
- **Session policy:** absolute lifetime 8 hours, idle timeout 30 minutes, single active session per user optional per tenant, and immediate invalidation on role change or IdP deprovision.

### Authorisation engine

Externalised policy using **Cedar** (AWS, verified-by-construction analysis, strong fit for AWS-native stacks) or **OPA/Rego** (broader ecosystem). Policy is versioned in git, unit-tested, and deployed with the application.

Decision inputs: `subject` (user, roles, tenant, MFA level, device posture), `action`, `resource` (tenant, classification, owner, legal hold status), `context` (time, IP geography, purpose, session age).

Every decision returns `{allow|deny, policy_version, reason}` and emits an audit event. Denials are logged and alertable — a spike in denials is an early attack signal.

**Policy test suite is mandatory**: a test matrix covering every role × every action × cross-tenant negative cases, run in CI as a blocking gate (doc 04).

### Machine identity

Covered in doc 09. Summary: SPIFFE workload identities, mTLS, no shared service accounts, no service credentials with human-usable authentication paths.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Privilege creep — permissions accumulate across role changes | Standing over-privilege; large insider blast radius | Group-based assignment only; quarterly recertification with evidence; automated detection of individual grants |
| Cross-tenant authorisation bug | Catastrophic confidentiality breach | Central policy engine; mandatory cross-tenant negative test matrix in CI; RLS as backstop (doc 06) |
| MFA bypass via legacy protocol, recovery flow, or help-desk social engineering | Account takeover of a privileged user | Disable legacy auth; FIDO2 only for privileged roles; help-desk verification procedure requiring manager callback + identity proofing |
| Orphaned accounts after offboarding | Undetected persistent access | SCIM-driven deprovisioning within 15 minutes; monthly orphan-account reconciliation |
| Customer IdP misconfiguration (open registration, weak assertions, no signature validation) | Unauthorised tenant access | Validate SAML/OIDC configuration at onboarding; enforce assertion signing and audience restriction; reject unsigned assertions |
| Break-glass credentials misused or lost | Total compromise or total lockout | Split knowledge, offline storage, hardware MFA, alerting on use, quarterly test |
| Session hijacking via stolen token | Impersonation | Short sessions, token binding where available, IP/device-change re-authentication, immediate revocation on anomaly |
| Support staff with broad tenant access | Insider risk at scale | Support access is JIT, purpose-bound, customer-visible, and metadata-only by default (doc 17) |

## Trade-offs

- **Buy an IdP (Entra ID / Okta — mature conditional access, high cost per user) vs. self-host Keycloak (free, full control, real operational burden and an availability single point of failure).** Identity outage = total outage. **Recommendation: buy. Entra ID if the workforce is Microsoft-centric; Okta otherwise.**
- **Build customer SSO/SCIM vs. buy (WorkOS, Auth0/Okta CIC, Cognito).** Enterprise SSO is deceptively hard — SAML edge cases, IdP quirks, SCIM semantics. **Recommendation: buy for time-to-market (WorkOS or Auth0), with an abstraction layer so migration remains possible; build only if per-user pricing becomes prohibitive at scale.**
- **Cedar (AWS-aligned, analysable, smaller ecosystem) vs. OPA/Rego (ubiquitous, more expressive, harder to reason about formally).** **Recommendation: Cedar, given the AWS-native architecture and the value of formal analysability for tenant-isolation policy.**
- **JIT privileged access (strong control, adds latency to incident response) vs. standing access for on-call.** Standing on-call access defeats the entire model. **Recommendation: JIT with a fast path — pre-approved emergency elevation that grants in <2 minutes but alerts loudly and requires retrospective justification.**
- **Quarterly recertification (thorough, tedious, risks rubber-stamping) vs. continuous automated review.** **Recommendation: continuous automated detection of anomalous/unused permissions (IAM Access Analyzer unused-access findings), plus a lighter quarterly human review focused on privileged roles only.**

## Design decisions

- **DD-10-01:** Separate workforce and customer identity planes. Workforce via Entra ID or Okta federated to IAM Identity Center; customer via a managed enterprise-SSO provider with SAML/OIDC/SCIM.
- **DD-10-02:** FIDO2/WebAuthn phishing-resistant MFA mandatory for all workforce accounts and for all customer privileged roles. SMS is never an accepted factor.
- **DD-10-03:** Zero standing production privilege. All elevated access is JIT, dual-approved by EU-resident approvers, ≤4 hours, session-recorded, auto-revoked.
- **DD-10-04:** Conditional access enforces EU session location for production access — the technical enforcement point for the cross-border control in doc 03.
- **DD-10-05:** Centralised Cedar policy engine; no authorisation logic in handlers; every decision audited with policy version and reason.
- **DD-10-06:** Cross-tenant negative test matrix (every role × every action) is a blocking CI gate.
- **DD-10-07:** SCIM-driven provisioning and deprovisioning for both workforce and customers, with a 15-minute deprovisioning SLA.
- **DD-10-08:** Time-boxed, scoped, fully-logged `auditor` role shipped as a product feature for external auditors and regulators.
- **DD-10-09:** Step-up authentication required for bulk export, key configuration, role changes, `RESTRICTED`/`PRIVILEGED` access, and evidence sign-off.
- **DD-10-10:** Two-person break-glass with split knowledge, offline hardware MFA, alerting on use, quarterly testing, rotation after each use.

## References

- Commission Delegated Regulation (EU) 2024/1774 — identity management, access rights, privileged access
- Regulation (EU) 2022/2554 (DORA) Art. 5(2), 9(4)(c)
- Directive (EU) 2022/2555 (NIS2) Art. 21(2)(i)/(j)
- Regulation (EU) 2016/679 (GDPR) Art. 5(1)(f), 25(2), 32
- NIST SP 800-63B Rev. 3 — Authentication and Lifecycle Management
- NIST SP 800-207 — Zero Trust Architecture
- W3C WebAuthn Level 3; FIDO2 CTAP2
- Cedar policy language (https://www.cedarpolicy.com); Open Policy Agent (https://www.openpolicyagent.org)
- RFC 7644 (SCIM 2.0 Protocol); OASIS SAML 2.0; OpenID Connect Core 1.0

## Confidence level

**High** — split identity planes, phishing-resistant MFA, JIT privilege, externalised policy engine, SCIM lifecycle, and the cross-tenant test matrix. All are proven and directly map to the DORA RTS requirements.

**Medium** — Cedar versus OPA is a genuine judgement call whose right answer depends on team familiarity and how much non-AWS policy enforcement is eventually needed; and the build-versus-buy line for customer SSO shifts with scale economics.
