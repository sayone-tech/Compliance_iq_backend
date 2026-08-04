# Identity and Access Management

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

This is the one area where the PRD is highly specific. The access model below is **the PRD's model**, not a proposal.

## What the PRD requires

| PRD ref | Requirement |
|---|---|
| §3, §3.1 | **Two levels of role.** *System roles* are defined by SayOne, carry fixed permissions and cannot be changed by any firm. *Firm roles* are custom names each firm creates, each linked to exactly one system role; that linkage determines actual permissions |
| §3.1 | **Eight system roles:** Platform Super Admin, Firm Super Admin, CCO / Compliance Manager, Compliance Officer (Lead Tester), Senior Management, Remediation Owner, IT / Systems Admin, Staff / Employee (**no login**) |
| FR-09 | Every user can only see and do what their role allows; enforced automatically by the platform |
| FR-10 | The Firm Super Admin can create, rename and deactivate custom firm roles; deactivating a role does not immediately lock out existing users — they must be reassigned first |
| FR-11 | Every user logs in with email and password **plus a second verification step on their phone** (MFA) |
| FR-12 | **Invitation only.** The Firm Super Admin sends an email invite; the new user sets up their account; the Super Admin assigns their role before they can access anything |
| FR-13 | Every action is permanently recorded in an audit log — what, when, and from which device. Not alterable or deletable by anyone, including administrators |
| FR-14 | On departure an admin deactivates the account; **everything the user ever did stays in the system**. Reassignment of their open work must be documented with reasoning and kept in an immutable audit trail |
| FR-15 | Each firm must always have **at least two Firm Super Admins**; the platform warns if it drops to one |
| §4 | The Platform Admin Portal is a **separate login and separate interface**; firm users never see it |
| §7.2 FR-20 | Only the CCO can assign a test to a Lead Tester; a Compliance Officer cannot self-assign |
| §7.1 step 3 / GAP-05 | Assigned users can work on a test; each contribution creates a version tagged to its contributor; non-assigned users get view-only, and only senior personnel with the right entitlements can view at all |
| §11 | IT / Systems Admin access is limited to the Systems & ICT Risk section; cannot see compliance tests or findings |

### Contradictions and gaps the PRD leaves open

| Ref | Issue | Status |
|---|---|---|
| FR-52 vs. GAP-07 | FR-52 says the Remediation Owner's personal task list "is the only compliance view they need"; Sosinna's GAP-07 answer says they should have view access to everything. **The PRD explicitly flags this as unresolved.** The authorisation model for this role cannot be built until it is settled | **[OPEN]** |
| SA-06 / SA-08 | How much firm data the Platform Admin Portal team can see. The PRD records a preference for broad visibility, an intention to handle evidence visibility contractually rather than by toggle, and marks it open | **[OPEN]** |
| FO-07 | Whether any Firm Super Admin or only the CCO may complete the onboarding wizard | **[OPEN]** |
| GAP-09 | Who may initiate a manual override of a WSP mapping | **[OPEN]** |
| GAP-11 | Whether the platform force-prompts reassignment of a deactivated user's open items or leaves it manual | **[OPEN]** |
| FR-11 | What "a second verification step on their phone" means concretely — SMS one-time code, authenticator-app TOTP, or push approval. **The PRD does not say.** See the recommendation below | **[OPEN]** |

## Best practices

- **One identity plane per population.** Workforce identities (the delivery and Portal teams) and firm user identities are different problems with different threat models; do not merge them into one directory.
- **No standing privilege on the operations side.** Anything above read-only metadata is granted just in time, time-boxed, approved and logged.
- **Authorisation is a service, not scattered conditionals.** A central, versioned, testable policy layer. Scattered checks drift, and drift in a multi-tenant system means cross-firm exposure.
- **Every access decision produces an audit event** — subject, action, resource, firm, decision, policy version, reason. FR-13 requires the event; recording the *decision* makes it useful.
- **Automate joiner–mover–leaver on the operations side.** Manual offboarding is the classic insider-threat gap (`insider-threat-protection`).
- **Recertify privileged access periodically**, with evidence retained.

## Regulatory implications

- **GDPR Art. 5(1)(f), Art. 32(1)(b)/(4)** — confidentiality, and ensuring persons acting under the processor's authority process data only on instruction. Access control is the enforcement mechanism. **Art. 25(2)** — by default, personal data must not be accessible to an indefinite number of persons.
- **GDPR Art. 15** — subject access requests require knowing precisely who accessed what; FR-13's audit log is a compliance artefact as well as a security one.
- **Delegated Reg. (EU) 2024/1774** — unique identities, strong authentication for remote and privileged access, privileged access management, periodic review of access rights, logging of privileged activity. *(Design reference.)*
- **MiCA Art. 68** (customer-side) — "security access protocols"; **Art. 68(2)** independence of the compliance function, which the product itself checks in FR-66.

## Recommended architecture

### Firm user identity **[PRD REQUIRED unless marked]**

- **Account creation is invitation-only** (FR-12). No self-registration path exists, including on the marketing site (MKT-02 confirms there is no self-serve checkout).
- **Email plus password plus a phone-based second factor** (FR-11). **[PROPOSED]** on the mechanism: prefer authenticator-app TOTP or push approval over SMS one-time codes — SMS is interceptable via SIM-swap, which is a live risk for staff at crypto firms. This is a recommendation only; **the PRD says "phone", and the concrete factor is an open decision** (`open-questions`, P-5).
- **Password handling** follows NIST SP 800-63B: length over composition rules, breached-password checking, no forced periodic rotation. **[PROPOSED]**
- **Role assignment is a separate administrative act** after the invited user completes setup (FR-12).
- **Firm roles map to exactly one system role**; permissions derive from the system role only (PRD §3, §3.2). The mapping table is data; the permission set is code.
- **At least two Firm Super Admins per firm**, with a platform warning when the count drops to one (FR-15). **[PRD REQUIRED]**
- **Deactivation, never deletion** (FR-14): the account loses access; every action it performed remains. Reassignment of open work is recorded with a documented reason in the immutable audit trail.
- **Step-up authentication** for high-impact actions — evidence export, role changes, mapping confirmation (FR-32), finding closure (FR-44), report generation (FR-55). **[PROPOSED]**
- **Session policy:** absolute lifetime and idle timeout, immediate invalidation on role change or deactivation. **[PROPOSED]**

Enterprise single sign-on and automated provisioning from a firm's own identity provider are **[FUTURE]** — not in the PRD, and the PRD's invitation-only model (FR-12) assumes platform-native accounts.

### Workforce identity (delivery team and Platform Admin Portal) **[PROPOSED]**

- A workforce identity provider with phishing-resistant multi-factor authentication, federated to cloud access. Phishing-resistant factors (security keys or platform passkeys) are appropriate here because this population can reach infrastructure — a stronger bar than FR-11 sets for firm users, and there is no PRD constraint against it.
- **Groups mirror job function**, not systems. Permission sets attach to groups; individual grants are prohibited and detected by conformance scanning.
- **Conditional access:** managed, compliant device required for anything above read-only; access-location policy for production (the enforcement point for `cross-border-data-processing`); risk-based step-up; legacy authentication protocols disabled.
- **Privileged access management:** production and key-administration roles are assigned to nobody by default. They are requested with a justification, dual-approved, granted for a short window, session-recorded and auto-revoked.
- **Break-glass:** two sealed, offline-stored root credentials with hardware factors, split knowledge, use triggering an immediate alert, tested periodically, rotated after every use. Note TI-01: the AWS account is the Client's, so **custody of the root credentials is a Client decision** **[OPEN]**.
- **Offboarding:** deprovision promptly on the HR event, revoke sessions across all systems, review key access, retain a completion checklist as evidence.

### Authorisation layer **[PROPOSED]**

Externalised, versioned policy evaluated per request. Decision inputs: subject (user, system role, firm, MFA state), action, resource (firm, classification, record state — for example whether a test is signed off per FR-27, or a report issued per FR-61), and context (purpose, session age, device posture for workforce users).

Every decision returns allow or deny with the policy version and a reason, and emits an audit event. Denials are logged and alertable — a spike is an early attack signal.

**No policy engine product is selected here.** Externalised authorisation is worth considering for a product with eight fixed system roles, per-firm custom role mappings and record-state-dependent permissions; the choice between an off-the-shelf policy language and a well-structured in-application policy module is an implementation decision. **[OPEN]**

**A policy test suite is mandatory:** every system role × every action, including cross-firm negative cases, run in CI as a blocking gate (`secure-sdlc`). This is the single most important test asset in the product, because NFR-01 is the requirement whose breach is unrecoverable.

### Roles that do not exist in the PRD

A time-boxed, scoped external **auditor role** for a firm's own auditors or a regulator is a common product feature and would be useful, but it is not in the PRD and would add MVP scope. **[FUTURE]**

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Cross-firm authorisation bug | Catastrophic; breach of NFR-01 | Central policy layer; mandatory cross-tenant negative test matrix in CI; row-level security as a backstop (`document-confidentiality`) |
| Building the Remediation Owner's permissions before FR-52/GAP-07 is resolved | Rework, or shipping the wrong visibility | Escalate the contradiction before the sprint that covers it; PRD §9.1 already flags it |
| SMS-based second factor subverted by SIM swap | Account takeover at a crypto-sector firm | Recommend app-based or push MFA within the PRD's "phone" wording; decision needed (`open-questions`, P-5) |
| Firm drops below two Super Admins and is locked out | Loss of firm access; FR-15 breach | Enforce the warning; block the action that would remove the last-but-one where possible |
| Deactivated user's open work left unassigned | Compliance work stalls; GAP-11 unresolved | Resolve GAP-11; in the meantime surface open items on deactivation |
| Privilege creep on the workforce side | Standing over-privilege, large insider blast radius | Group-based assignment only; periodic recertification; automated detection of individual grants |
| Orphaned workforce accounts after offboarding | Undetected persistent access | Automated deprovisioning; periodic orphan-account reconciliation |
| Portal team's access to firm data exceeds what firms expect | Contractual and confidentiality breach | Resolve SA-06/SA-08; enforce in the authorisation layer, not the UI |
| Break-glass credentials for the Client-owned account misplaced or misused | Total compromise or total lockout | Split knowledge, offline storage, hardware factors, alerting on use, periodic test; custody agreed with the Client |

## Trade-offs

- **Buy a workforce identity provider vs. self-host.** Identity outage equals total outage. Recommendation: buy. **[PROPOSED]**
- **Externalised policy engine vs. a disciplined in-application policy module.** The former is more analysable and testable; the latter has fewer moving parts for a team of this size. Recommendation: whichever is chosen, the policy must be versioned, centrally authored and covered by the full role × action test matrix. **[OPEN]**
- **Just-in-time privileged access vs. standing access for operations.** Standing access defeats the model. Recommendation: just-in-time with a fast pre-approved emergency path that grants quickly but alerts loudly. **[PROPOSED]**
- **Periodic human recertification vs. continuous automated review.** Recommendation: continuous automated detection of unused and anomalous permissions, plus a lighter periodic human review focused on privileged roles. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification | Basis |
|---|---|---|---|
| DD-10-01 | Eight fixed system roles; firm-created role names map to exactly one system role, and permissions derive only from the system role | **[PRD REQUIRED]** | PRD §3, §3.1, §3.2 |
| DD-10-02 | Role-based access enforced automatically by the platform on every request | **[PRD REQUIRED]** | FR-09 |
| DD-10-03 | Accounts are created by invitation only; the Super Admin assigns the role before any access is granted | **[PRD REQUIRED]** | FR-12 |
| DD-10-04 | Email and password plus a phone-based second factor for every user | **[PRD REQUIRED]** | FR-11 |
| DD-10-05 | The concrete second factor (app TOTP / push preferred over SMS) | **[OPEN]** | FR-11 silent |
| DD-10-06 | Users are deactivated, never deleted; all of their historical actions and uploads remain; reassignment of open work is recorded with a documented reason | **[PRD REQUIRED]** | FR-14 |
| DD-10-07 | Minimum of two Firm Super Admins enforced, with a warning when the count falls to one | **[PRD REQUIRED]** | FR-15 |
| DD-10-08 | Platform Admin Portal uses a separate login and interface; firm users have no path to it | **[PRD REQUIRED]** | PRD §4 |
| DD-10-09 | Separate workforce identity plane with phishing-resistant MFA, conditional access and just-in-time privilege | **[PROPOSED]** | — |
| DD-10-10 | Zero standing production privilege for the delivery team; elevation is dual-approved, time-boxed, session-recorded, auto-revoked | **[PROPOSED]** | supports FR-13 |
| DD-10-11 | Centralised, versioned authorisation policy with every decision audited; engine choice not fixed | **[PROPOSED / OPEN]** | implements FR-09 |
| DD-10-12 | Cross-firm negative test matrix (every system role × every action) is a blocking CI gate | **[PROPOSED]** | implements NFR-01 |
| DD-10-13 | Step-up authentication for evidence export, role changes, mapping confirmation, finding closure and report generation | **[PROPOSED]** | supports FR-32, FR-44, FR-55 |
| DD-10-14 | Remediation Owner visibility scope | **[OPEN]** | FR-52 vs GAP-07 — PRD flags the contradiction |
| DD-10-15 | External auditor / regulator role | **[FUTURE]** | not in PRD |

## References

- Regulation (EU) 2016/679 (GDPR) Art. 5(1)(f), 25(2), 32
- Commission Delegated Regulation (EU) 2024/1774 — identity management, access rights, privileged access *(design reference)*
- NIST SP 800-63B Rev. 3 — Authentication and Lifecycle Management
- NIST SP 800-207 — Zero Trust Architecture
- W3C WebAuthn Level 3; FIDO2 CTAP2 — for the workforce plane
- OWASP Application Security Verification Standard — Access Control chapter

## Confidence level

**High** — the PRD's role model is explicit and the enforcement architecture around it is standard.

**Medium** — whether an externalised policy engine or an in-application policy module is the better fit at this team size.

**Not determined** — the Remediation Owner's visibility scope, the concrete second factor, the Portal's visibility boundary, and who may complete onboarding or initiate a mapping override. Four of these are PRD-flagged open items and one is a PRD-flagged contradiction.
