# Insider Threat Protection

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](../future-scope/future-and-optional-scope.md).

The insider with legitimate access is the hardest threat to defend against and the most plausible source of a catastrophic confidentiality breach here. The platform concentrates every client firm's compliance evidence behind a small number of operators, and the PRD's own rules — NFR-04's "not even the system administrators at SayOne" and NFR-07's "no user, including administrators" — are explicitly insider-threat requirements.

Note the sector angle: staff at a company serving crypto-asset service providers are a plausible target for coercion, bribery and social engineering by well-funded actors. Treat it as live, not theoretical.

Three insider categories, each needing different controls:

| Type | Motivation | Primary control |
|---|---|---|
| **Malicious** | Financial gain, grievance, coercion, recruitment | Technical prevention — make the data unreachable |
| **Negligent** | Convenience, ignorance, pressure | Guardrails — make the safe path the easy path |
| **Compromised** | Their account or device is attacker-controlled; they are unaware | Detection — behavioural signals, device posture |

## What the PRD requires

| PRD ref | Requirement |
|---|---|
| NFR-04 | Not even SayOne's system administrators can modify or delete the audit log |
| NFR-07, §2 | No user, **including administrators**, can delete test results, findings, evidence, reports or audit logs |
| FR-13 | Every action recorded permanently with actor, time and device; not alterable by anyone |
| FR-14 | Departing users are deactivated, not deleted; their history remains; reassignment of open work is documented with reasoning in an immutable audit trail |
| SA-06, SA-08 | The Platform Admin Portal team's visibility of firm data — **the boundary is an open question**, with the expectation that evidence visibility is handled contractually |

Everything else below is **[PROPOSED]**.

## Best practices

- **Reduce what an insider can reach before trying to detect what they do.** Zero standing access (`identity-and-access-management`) removes most of the insider surface outright.
- **Dual control for irreversible or high-impact actions.** This mirrors the product's own philosophy — FR-32 two-person mapping sign-off, FR-44 two-person finding closure, FR-21c sample-change approval.
- **Separation of duties by design.** Encode it in identity policy, not in a policy document.
- **Everything an operator does with a firm's data should be visible to that firm.** Radical transparency is both an ethical position and a strong deterrent — but see the open SA-06/SA-08 boundary.
- **Baseline behaviour and alert on deviation** — volume, timing, breadth, sequence.
- **Address the human side.** Screening proportionate to access, clear policy, a confidential reporting channel, and a supportive path for anyone under external pressure.
- **Offboarding is a security event with a deadline**, not an HR formality.

## Regulatory implications

- **GDPR Art. 32(4) and Art. 29** — ensuring that any person acting under the processor's authority processes personal data only on instruction. This is precisely an insider-control obligation.
- **GDPR Art. 5(1)(f)** — confidentiality; insider exfiltration is a personal data breach requiring assessment.
- **Delegated Reg. (EU) 2024/1774** — privileged access management, access reviews, logging of privileged activity. *(Design reference.)*
- **Employment and privacy law constraint.** Monitoring employees is itself processing personal data. It requires a lawful basis, a documented balancing test, transparency to the employee, proportionality, and in several member states works council consultation. Covert monitoring is generally unlawful. Session recording and behavioural analytics must be disclosed in the employee privacy notice. **This applies in every jurisdiction where staff are employed, and the specifics differ — take local advice before deployment.** **[OPEN — LEGAL]**

## Recommended architecture

### Layer 1 — prevention (the highest-value layer) **[PROPOSED]**

- **Zero standing access to production personal data** (`cross-border-data-processing`, `identity-and-access-management`). Most insider scenarios cannot start.
- **No deletion path for protected records, for anyone.** This is the PRD's own requirement (NFR-04, NFR-07) and it is the single strongest insider control in the product: the most damaging insider action — destroying evidence of what happened — is architecturally unavailable.
- **Separation of duties, enforced and continuously verified:**

| Capability | Mutually exclusive with |
|---|---|
| Key administration | Data-plane decryption |
| Audit log write | Audit log delete (nobody has delete) |
| Deploy to production | Approve the deployment |
| Seal a record | Alter retention policy |
| Grant access | Approve the access grant |
| Manage backups | Delete backups (nobody has delete) |

- **Dual authorisation** required for: key operations, retention policy change, legal hold release, bulk export above a threshold, break-glass grant, production identity policy change, and disabling any security control.
- **Rate limiting on data access** per role. A compliance officer reads a modest number of documents a day; thousands is an exfiltration event. Thresholds tuned from real baselines and enforced above a hard ceiling, not merely alerted.
- **Export controls:** bulk export requires step-up authentication, a stated purpose, approval above a threshold, produces a watermarked artefact, and generates an audit event visible to the firm.

Hardware-enclave decryption, so that even infrastructure administrators cannot read plaintext, is **[FUTURE]** (appendix 39).

### Layer 2 — detection **[PROPOSED]**

High-signal detections, low false-positive, immediate escalation:

- **Canary records** — a decoy document and a decoy credential that no legitimate workflow touches. Any access is a definitive signal with essentially zero false positives. This is the best insider detection available.
- Any access to a firm a workforce user has never accessed before.
- Access outside normal hours combined with elevated volume.
- Sequential enumeration patterns.
- Break-glass used without a matching incident record.
- Authorisation-denial spike from one principal.
- Any attempt to delete or modify a protected record or an audit entry — which should be identically zero.

Broad behavioural analytics beyond this small set is **[FUTURE]** — it costs, it generates false positives, it intrudes on employees, and it requires a security function able to triage it.

**Session recording** for all break-glass and privileged sessions, retained for a defined period, reviewed on any alert.

### Layer 3 — firm-facing transparency **[PROPOSED / OPEN]**

Ideally, every operator action on a firm's data appears in that firm's own audit log with actor, purpose, timestamp and scope. **Whether and how this is surfaced depends on the unresolved SA-06/SA-08 visibility boundary** — the PRD records an intention to handle Portal visibility of evidence contractually rather than through per-firm toggles. Resolve the boundary, then implement it in the authorisation layer and reflect it in the audit trail. **[OPEN]**

Customer-approved access (a lockbox model where the firm must approve each support access) is **[FUTURE]**.

### Layer 4 — human and organisational **[PROPOSED]**

- **Screening proportionate to access**, for anyone eligible for break-glass or key administration. Permissible screening differs substantially by jurisdiction — take local advice.
- **Documented, signed acceptable-use and confidentiality obligations**, with specific acknowledgement of the sensitivity of client firms' compliance data.
- **Security awareness training**, plus role-specific training for privileged operators covering social engineering and coercion scenarios.
- **Confidential reporting channel** covering both security concerns and reporting external pressure or approaches. For an EU entity, align with Directive (EU) 2019/1937.
- **Coercion support policy:** an explicit, non-punitive path for anyone approached, threatened or bribed to report it immediately with protection. Without this, a coerced employee's rational choice is silence.
- **Offboarding:** access revoked promptly on the HR event; devices recovered; tokens revoked; a final access review conducted and retained as evidence.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Privileged operator exfiltrates evidence at scale | Catastrophic; breach of NFR-01 | Zero standing access, rate limits, canary records, dual control, firm-visible access, watermarking |
| Operator attempts to alter or delete audit evidence | Would breach NFR-04 directly | Write-once storage, write-only log-archive account, hash chain, deletion denied to all principals, key-deletion blocked during retention |
| Slow, low-volume exfiltration below thresholds | Sustained undetected leakage | Cumulative as well as rate baselines; distinct-firm-count monitoring; canary records; periodic access-pattern review |
| Coerced or bribed employee | Bypasses all trust-based controls | Technical prevention over trust; dual control; coercion reporting policy with protection; proportionate screening |
| Monitoring deployed without a lawful basis or required consultation | Regulatory and employment-law exposure; evidence inadmissible | Legal review before deployment; employee privacy notice; documented balancing test; consultation where required |
| Departing employee retains access via a shared credential | Post-departure access | No shared credentials (`secrets-management`); note FR-12 makes every account individually invited; prompt revocation; device recovery |
| Portal team access exceeds firm expectations | Contractual and confidentiality breach | Resolve SA-06/SA-08; enforce in the authorisation layer |
| Alert fatigue causes real signals to be ignored | Detection exists on paper only | A small number of high-signal detections; canary records as the zero-false-positive tier; measured alert-to-triage ratio |
| Over-surveillance damages culture | Loss of good engineers; a worse security outcome overall | Prefer prevention over surveillance; be transparent about what is monitored and why; never monitor covertly |

## Trade-offs

- **Technical prevention vs. monitoring and trust.** Detection after evidence has been exfiltrated does not undo the harm. Recommendation: invest in prevention first; monitoring is the backstop, not the strategy. **[PROPOSED]**
- **Firm-visible operator access after the fact vs. firm-approved access before it.** Recommendation: transparent-after-the-fact as the baseline once SA-06/SA-08 is resolved; approval-before-access is **[FUTURE]**.
- **Broad behavioural analytics vs. targeted high-signal detections.** Recommendation: a small set plus canary records. **[PROPOSED]**
- **Session recording of all privileged sessions vs. command logging only.** Recommendation: full recording for break-glass and key administration; command-level logging for routine privileged operations. **[PROPOSED]**
- **Deep background screening vs. proportionate.** Recommendation: deeper screening only for the small set of break-glass and key-administration-eligible roles. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification | Basis |
|---|---|---|---|
| DD-17-01 | Platform administrators cannot delete or modify the audit log or protected records; there is no privileged override | **[PRD REQUIRED]** | NFR-04, NFR-07 |
| DD-17-02 | Prevention over detection: zero standing production access is the primary insider control | **[PROPOSED]** | — |
| DD-17-03 | Mutually exclusive capability matrix enforced in identity policy and verified continuously; violations are top severity | **[PROPOSED]** | — |
| DD-17-04 | Dual authorisation for key operations, retention changes, legal hold release, bulk export above threshold, break-glass grants and disabling any security control | **[PROPOSED]** | — |
| DD-17-05 | Per-role data-access rate limits with a hard ceiling, tuned from measured baselines | **[PROPOSED]** | — |
| DD-17-06 | Canary records seeded per firm; any access is a top-severity incident with a defined verification-before-accusation procedure | **[PROPOSED]** | — |
| DD-17-07 | Full session recording for break-glass and key-administration sessions | **[PROPOSED]** | — |
| DD-17-08 | Monitoring is transparent: documented in the employee privacy notice, supported by a balancing test, and subject to any locally required consultation | **[PROPOSED / OPEN — LEGAL]** | — |
| DD-17-09 | Offboarding revokes all access promptly with a documented checklist retained as evidence | **[PROPOSED]** | supports FR-14 |
| DD-17-10 | Non-punitive coercion-reporting policy communicated in onboarding and training | **[PROPOSED]** | — |
| DD-17-11 | Operator access to a firm's data surfaced in that firm's audit trail | **[OPEN]** | depends on SA-06/SA-08 |
| DD-17-12 | Firm-approved (lockbox) support access; broad behavioural analytics; enclave-based decryption | **[FUTURE]** | not in PRD |

## References

- Regulation (EU) 2016/679 (GDPR) Art. 5(1)(f), 29, 32(4)
- Commission Delegated Regulation (EU) 2024/1774 — privileged access management, access reviews, logging *(design reference)*
- Directive (EU) 2019/1937 — protection of persons who report breaches of Union law
- CERT/SEI — Common Sense Guide to Mitigating Insider Threats
- MITRE ATT&CK — Exfiltration (TA0010), Collection (TA0009)
- ISO/IEC 27001:2022 Annex A 6.1–6.6 (people controls), 8.2 (privileged access)
- EDPB/WP29 Opinion 2/2017 on data processing at work

## Confidence level

**High** — the prevention-first strategy, the separation-of-duties matrix, canary records, and the observation that the PRD's own non-deletability rules are the strongest insider control in the product.

**Not determined** — the legality and practical shape of behavioural monitoring in the jurisdictions where staff are employed, and the Portal's visibility boundary.
