# 17 — Insider Threat Protection

The insider with legitimate access is the hardest threat to defend against and the most likely source of a catastrophic confidentiality breach here. Our architecture concentrates enormous value — every EU crypto firm's compliance evidence — behind a small number of operators.

Three insider categories, each needing different controls:

| Type | Motivation | Primary control |
|---|---|---|
| **Malicious** | Financial gain (this data has real market value), grievance, coercion, recruitment by an external actor | Technical prevention — make the data unreachable |
| **Negligent** | Convenience, ignorance, pressure | Guardrails and training — make the safe path the easy path |
| **Compromised** | Their account or device is controlled by an attacker; they are unaware | Detection — behavioural analytics, device posture |

Note the crypto-specific angle: employees at a company serving crypto-asset managers are a plausible target for coercion, bribery and social engineering by well-funded actors. Treat this as a live threat, not a theoretical one.

## Best practices

- **Reduce what an insider can reach before trying to detect what they do.** Zero standing access (doc 10) removes most of the insider surface outright.
- **Dual control for irreversible or high-impact actions.** Key deletion, bulk export, retention changes, production configuration, tenant deletion.
- **Separation of duties by design.** The person who can approve an assessment cannot alter the audit log. The person who administers keys cannot read data. Encode this in IAM, not in a policy document.
- **Everything an operator does with customer data is visible to the customer.** Radical transparency is both an ethical position and an exceptionally strong deterrent.
- **Baseline behaviour and alert on deviation** — volume, timing, breadth, sequence.
- **Address the human side.** Background screening proportionate to access, clear policy, confidential reporting channel, awareness of coercion risk, and a supportive path for anyone under external pressure.
- **Offboarding is a security event with a deadline**, not an HR formality.

## EU regulatory implications

- **DORA Art. 9(4)(c)** — need-to-know, least privilege, segregation of duties. **Delegated Reg. (EU) 2024/1774** requires privileged access management, review of access rights, and logging of privileged user activity.
- **DORA Art. 5(2)(f)/Art. 13(6)** — ICT security awareness programmes and training for staff, including senior management, on an ongoing basis.
- **NIS2 Art. 21(2)(i)** — **human resources security**, access control policies and asset management are named explicitly as required risk-management measures. **Art. 20(2)** — management bodies must follow training.
- **GDPR Art. 32(4)** — ensuring that any natural person acting under our authority who has access to personal data does not process it except on instruction. This is precisely an insider-control obligation. **Art. 29** likewise.
- **GDPR Art. 5(1)(f)** — confidentiality; a malicious-insider exfiltration is a personal data breach requiring Art. 33/34 assessment.
- **MiCA Art. 68/Art. 72** — governance and conflicts of interest; personnel controls form part of the CASP's outsourcing due diligence on us.
- **Employment and privacy law constraint:** monitoring employees is itself processing personal data. It requires a lawful basis (normally legitimate interests), a documented balancing test, transparency to the employee, proportionality, and in several member states (notably Germany) **works council consultation**. Covert monitoring is generally unlawful. Session recording and UEBA must be disclosed in the employee privacy notice. **This applies to the Indian entity too, under DPDP and Indian employment law.**

## Recommended architecture

### Layer 1 — Prevention (the highest-value layer)

- **Zero standing access to production personal data** (DD-03-03, DD-10-03). Most insider scenarios simply cannot start.
- **Nitro Enclave document decryption** (doc 07) — plaintext exists only inside an attested enclave with no operator shell. Even a fully-privileged infrastructure administrator cannot read document content.
- **Separation of duties in IAM**, enforced and continuously verified:

| Capability A | Mutually exclusive with |
|---|---|
| Key administration | Data-plane decrypt |
| Audit log write | Audit log delete (nobody has delete) |
| Deploy to production | Approve the deploy |
| Create evidence | Alter retention policy |
| Grant access | Approve access grant |
| Manage backups | Delete backups (Vault Lock: nobody) |

- **Dual authorisation** required for: KMS key deletion, retention policy change, legal hold release, tenant deletion, bulk export above threshold, break-glass grant, production IAM policy change, disabling a security control.
- **Rate limiting on data access** per user: a compliance officer reads perhaps 50 documents a day; 5,000 is an exfiltration event. Thresholds are per-role, tuned from actual baselines, and enforced (not merely alerted) above a hard ceiling.
- **Export controls:** bulk export requires step-up authentication, a stated purpose, tenant-admin approval above threshold, produces a watermarked artefact, and generates a customer-visible notification.

### Layer 2 — Detection

- **UEBA baselines** per user and per role: documents accessed per day, distinct tenants touched, access hours, access sequence entropy, download volume, unusual document classifications, first-time access to a tenant.
- **High-signal detections** (low false-positive, immediate escalation):
  - Any access to a tenant a user has never accessed before.
  - Access outside the user's normal hours combined with elevated volume.
  - Sequential enumeration patterns (reading documents in ID order).
  - Access immediately following a resignation event from the HR feed.
  - Break-glass used without a matching incident ticket.
  - Denial spike from one principal (probing for gaps).
  - Any use of a honeytoken document — a decoy record in each tenant that no legitimate workflow touches. **This is the single best insider detection available: zero false positives, immediate certainty.**
- **HR-security integration:** resignation, performance-management and role-change events feed the risk engine, raising monitoring sensitivity and triggering an access review. Handle this with care and transparency — it must be disclosed and proportionate, not punitive.
- **Session recording** for all break-glass and privileged sessions, retained 2 years, reviewed on a sampling basis and fully on any alert.

### Layer 3 — Customer transparency

- Every operator action on a tenant's data appears in **that tenant's own audit log** as a `support` actor event with actor, purpose, timestamp and scope.
- Optional per-tenant **access approval**: for T2/T3 customers, our support access to their document content requires their real-time approval (an "access request" the tenant admin approves, akin to lockbox models). This is a strong differentiator and effectively eliminates unilateral operator access.
- Monthly access report to each tenant admin summarising all support access.

### Layer 4 — Human and organisational

- **Screening proportionate to access:** identity verification, employment and education verification, and criminal record check where lawful in the jurisdiction, for anyone eligible for break-glass or key administration. Re-screening every 3 years for the highest-privilege roles. Note that permissible screening differs substantially between India and EU member states — take local advice.
- **Documented, signed acceptable-use and confidentiality obligations**, with specific acknowledgement of the sensitivity of customer compliance data.
- **Annual security awareness training** plus role-specific training for privileged operators, including social engineering and coercion scenarios. Required by DORA Art. 13(6) and NIS2 Art. 20(2).
- **Confidential reporting channel** (whistleblowing, EU Whistleblower Directive (EU) 2019/1937 compliant for the EU entity) covering both security concerns and reporting external pressure or approaches.
- **Coercion support policy:** an explicit, non-punitive path for any employee approached, threatened or bribed to report it immediately with protection. Without this, a coerced employee's rational choice is silence.
- **Offboarding SLA:** access revoked within 15 minutes of the HR termination event; devices recovered; hardware tokens revoked; a final access review conducted; departure recorded in the risk engine for a 90-day heightened-monitoring window on any residual shared credentials.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Privileged operator exfiltrates document content at scale | Catastrophic; likely terminal for the business | Zero standing access, enclave decryption, rate limits, honeytokens, dual control, customer-visible access |
| Operator alters or deletes audit evidence to cover tracks | Forensics destroyed; product credibility destroyed | Object Lock COMPLIANCE, write-only log-archive account, hash chain, external qualified timestamps, deletion denied to all principals |
| Slow, low-volume exfiltration below detection thresholds | Sustained undetected leakage | Cumulative (not just rate) baselines; distinct-tenant-count monitoring; honeytokens; periodic access-pattern review |
| Coerced or bribed employee | Bypasses all trust-based controls | Technical prevention over trust; dual control; coercion reporting policy with protection; screening |
| Monitoring implemented unlawfully (no basis, no transparency, no works council) | Regulatory action, employment litigation, evidence inadmissible | Legal review before deployment; employee privacy notice; balancing test documented; works council consultation where required |
| Departing employee retains access via a shared credential or a personal cloud copy | Post-departure access | No shared credentials (doc 09); DLP on egress; 90-day heightened monitoring; device recovery |
| Alert fatigue causes real insider signals to be ignored | Detection exists on paper only | Small number of high-signal detections; honeytokens as the zero-false-positive tier; measured alert-to-triage ratio |
| Over-surveillance damages culture and drives talent away | Loss of good engineers; a worse security outcome overall | Prefer prevention over surveillance; be transparent about what is monitored and why; never monitor covertly |

## Trade-offs

- **Technical prevention (removes the risk; expensive, adds friction to operations) vs. monitoring and trust (cheap, detects after the fact).** Detection after exfiltration of compliance documents does not undo the harm. **Recommendation: invest in prevention first; monitoring is the backstop, not the strategy.**
- **Customer-approved access / lockbox model (near-elimination of unilateral operator access; slows incident response and requires customer availability) vs. transparent-after-the-fact access.** **Recommendation: transparent-after-the-fact as the default for all tenants; customer-approved access as a T2/T3 feature, with a documented emergency override that is loudly notified.**
- **Extensive UEBA (better detection; cost, false positives, privacy intrusion, works council friction) vs. targeted high-signal detections.** **Recommendation: a small set of high-signal detections plus honeytokens. Add broader UEBA only when the security team can triage it.**
- **Session recording of all privileged sessions (excellent forensics; storage cost, employee privacy concerns, review burden) vs. command logging only.** **Recommendation: full recording for break-glass and key administration; command-level logging for routine privileged operations.**
- **Deep background screening (better assurance; cost, delay, legal variability across India and EU member states, and a real limit on the hiring pool) vs. minimal.** **Recommendation: proportionate — deep screening only for the small set of break-glass/key-admin-eligible roles.**
- **Honeytokens (near-perfect detection; risk of confusing a new engineer or triggering a false incident) vs. none.** **Recommendation: deploy, document in the security runbook only, and ensure the incident process verifies before acting on a person.**

## Design decisions

- **DD-17-01:** Prevention over detection. Zero standing production access; enclave-based document decryption so infrastructure administrators cannot read plaintext.
- **DD-17-02:** Mutually-exclusive capability matrix enforced in IAM and verified continuously by automated conformance scanning; violations are P1.
- **DD-17-03:** Dual authorisation required for key deletion, retention changes, legal hold release, tenant deletion, bulk export above threshold, break-glass grants, and disabling any security control.
- **DD-17-04:** Per-role data-access rate limits, enforced with a hard ceiling, tuned from measured baselines.
- **DD-17-05:** Honeytoken documents deployed in every tenant; any access is an immediate P1 with a defined verification-before-accusation procedure.
- **DD-17-06:** All operator access to tenant data is written to that tenant's own audit log and included in a monthly report to the tenant admin.
- **DD-17-07:** Customer-approved access (lockbox) offered for T2/T3 customers, with a loudly-notified emergency override.
- **DD-17-08:** Full session recording for break-glass and key-administration sessions, retained 2 years, sampled for review and fully reviewed on any alert.
- **DD-17-09:** Monitoring is transparent: documented in the employee privacy notice, supported by a documented legitimate-interests balancing test, and subject to works council consultation where required in each jurisdiction, including India.
- **DD-17-10:** Offboarding revokes all access within 15 minutes of the HR event, with a documented checklist retained as evidence and a 90-day heightened-monitoring window.
- **DD-17-11:** Non-punitive coercion-reporting policy with protection, communicated in onboarding and annual training.

## References

- Commission Delegated Regulation (EU) 2024/1774 — privileged access management, access reviews, logging
- Regulation (EU) 2022/2554 (DORA) Art. 5(2), 9(4)(c), 13(6)
- Directive (EU) 2022/2555 (NIS2) Art. 20(2), 21(2)(i)
- Regulation (EU) 2016/679 (GDPR) Art. 5(1)(f), 29, 32(4)
- Directive (EU) 2019/1937 — protection of persons who report breaches of Union law
- CERT/SEI — Common Sense Guide to Mitigating Insider Threats, 7th edition
- MITRE ATT&CK — Exfiltration (TA0010), Collection (TA0009)
- ISO/IEC 27001:2022 Annex A 6.1–6.6 (people controls), 8.2 (privileged access)
- EDPB/WP29 Opinion 2/2017 on data processing at work (employee monitoring principles)

## Confidence level

**High** — the prevention-first strategy, separation-of-duties matrix, honeytokens, customer-visible operator access, and the offboarding SLA. These are effective, proportionate and well-evidenced.

**Medium** — the legality and practical implementation of behavioural monitoring across both jurisdictions (German works council requirements and Indian employment law differ substantially; this needs local counsel before deployment), and the acceptable friction level of a customer-approved access model in real incident response, which should be piloted with one customer first.
