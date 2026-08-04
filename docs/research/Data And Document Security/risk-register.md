# Risk Register

> **Baseline:** PRD v4.0. Consolidated from the per-topic risk tables and `threat-model`. Scoring: Likelihood (L) and Impact (I) 1–5. **Inherent** = before controls; **Residual** = with the `security-control-matrix` controls implemented.
>
> **Ownership.** The PRD does not staff this project. Owners below are given as **roles to be assigned**, not as people or titles that exist. Assigning them is open question P-9 in `open-questions`. No risk in this register has been accepted by anyone — see the final section.

**Impact scale:** 5 = existential (loss of the platform's core promise, or a breach that ends the engagement) · 4 = severe (major regulatory or contractual consequence) · 3 = significant (client loss, remediation cost) · 2 = moderate · 1 = minor.

## Top risks (residual ≥ 8)

| ID | Risk | Category | Inherent | Controls (`security-control-matrix`) | Residual | Owner (to assign) |
|---|---|---|---|---|---|---|
| R-01 | **Cross-firm data disclosure** via application, cache, index or key-scoping failure — breaches NFR-01 | Confidentiality | 4×5 = 20 | E-01, E-02, E-03, E-06, C-11, D-05, D-08 | **10** | Security owner |
| R-02 | **Prompt injection in an uploaded WSP** produces a mapping that conceals a genuine compliance gap | AI / integrity | 4×5 = 20 | I-07, I-08, **I-01 human confirmation**, **I-02 two-person approval**, I-03 | **9** | Product owner |
| R-03 | **Malicious or coerced insider exfiltrates firm evidence** | Insider | 3×5 = 15 | B-07, K-04, K-11, K-10, E-05 | **9** | Security owner |
| R-04 | **A firm user fabricates or backdates evidence** to conceal a compliance failure | Integrity | 3×5 = 15 | F-01, F-04, F-05, F-06, I-02, FR-45 exclusion enforced server-side | **9** | Product owner |
| R-05 | **Mapping accuracy falls below the 85% PRD commitment** after a model or prompt change | Contractual | 4×4 = 16 | I-03, I-09 evaluation harness as a promotion gate | **8** | Product owner |
| R-06 | **Compromised upstream dependency** introduces a backdoor | Supply chain | 3×5 = 15 | H-10, H-09, G-04, H-08 | **8** | Engineering owner |
| R-07 | **Ransomware** encrypts production and attempts to destroy backups — would breach NFR-07 | Availability / integrity | 3×5 = 15 | J-04, J-05, F-12, J-06 | **8** | Engineering owner |
| R-08 | **Records destroyed before the six-year minimum** by deletion, key destruction or retention misconfiguration | Regulatory / integrity | 3×5 = 15 | E-07, D-11, F-15, J-03, F-16 | **8** | Security owner |
| R-09 | **Unresolved delivery topology** leaves an unlawful cross-border access path live | Regulatory | 4×4 = 16 | B-06, B-07, B-08 — **but B-09 is unanswered** | **8** | Legal / Client |

## Significant risks (residual 5–7)

| ID | Risk | Category | Inherent | Controls | Residual | Owner (to assign) |
|---|---|---|---|---|---|---|
| R-10 | Portal team accesses firm evidence beyond the agreed boundary | Confidentiality | 3×4 | C-16 — **boundary unresolved (SA-06/SA-08)** | 7 | Client / Product |
| R-11 | SIM-swap defeats an SMS-based second factor | Access | 3×4 | C-04, C-05 — **mechanism unresolved** | 6 | Security owner |
| R-12 | Two-person sign-off defeated by one person or by an excluded party | Integrity | 3×5 | Server-side approver identity and exclusion checks; C-03 invitation-only accounts | 6 | Product owner |
| R-13 | Cloud misconfiguration exposes storage or a database publicly | Confidentiality | 3×5 | G-01, G-02, G-03, conformance scanning | 6 | Engineering owner |
| R-14 | Compromised pipeline deploys malicious code | Supply chain | 2×5 | H-06, H-07, H-08 | 6 | Engineering owner |
| R-15 | Audit gap prevents scoping a breach within 72 hours | Regulatory | 3×4 | F-13, F-14, pre-tested scoping queries | 6 | Security owner |
| R-16 | Erasure request received for a record class the PRD says cannot be deleted | Regulatory | 3×4 | E-13 — **unresolved (`open-questions` L-3)** | 6 | Legal / Client |
| R-17 | Accepting real client data before the go/no-go checklist is met, under delivery pressure | Programme | 3×4 | `deployment-recommendations` §11 as a hard gate | 6 | Client / Delivery |
| R-18 | Parser, OCR or media exploit in the upload pipeline | Confidentiality | 3×4 | E-09, E-10 | 5 | Engineering owner |
| R-19 | Untested restore fails when needed | Availability | 3×5 | J-06 automated restore verification | 5 | Engineering owner |
| R-20 | Derivative artefacts (previews, extracted text, OCR output) escape access control | Confidentiality | 3×4 | E-06 derivative registry with inheritance | 5 | Engineering owner |
| R-21 | Malware uploaded as evidence and later downloaded by a firm user | Integrity | 3×4 | E-09 quarantine-scan-promote, fail closed | 5 | Engineering owner |
| R-22 | Storage cost growth over six-plus non-deletable years exceeds the model | Commercial | 3×3 | Lifecycle transitions; NFR-11 ceiling; cost modelling in `deployment-recommendations` §7 | 5 | Client / Delivery |
| R-23 | Inference provider changes terms, region or retention | Third party | 2×4 | Contractual change notice; selection criteria — **provider unselected** | 5 | Product owner |
| R-24 | Session token theft via a script in a rendered document | Access | 3×4 | E-11 separate content origin, sandboxed policy | 5 | Engineering owner |
| R-25 | Incident assessed or notified too late for firms to meet their own clocks | Regulatory | 3×4 | K-05, K-06 — **deadline unresolved** | 5 | Security owner |
| R-26 | Denial of service during a firm's testing or regulator-response deadline | Availability | 3×4 | G-06, J-08 degraded modes | 5 | Engineering owner |

## Managed risks (residual ≤ 4)

| ID | Risk | Controls | Residual | Owner (to assign) |
|---|---|---|---|---|
| R-27 | Insider alters or deletes audit entries | F-02, F-12, D-11, K-09 | 3 | Security owner |
| R-28 | Secret committed to source control | H-01, K-04 canaries, automated revocation | 4 | Engineering owner |
| R-29 | Privilege creep on the workforce side | C-13, group-based assignment, periodic recertification | 4 | Security owner |
| R-30 | Data exfiltrated through an allowlisted egress destination | G-04, single egress service with classification checks | 4 | Engineering owner |
| R-31 | Report content leaves the audited boundary as an email attachment | DD-23-06 link-not-attachment — **unresolved (P-7)** | 4 | Product owner |
| R-32 | Backup or record copy placed outside the EU | J-08 policy restriction, conformance scanning | 3 | Engineering owner |
| R-33 | Hash chain broken by an ingestion gap | Single-writer sealer, gap detection, documented repair | 4 | Engineering owner |
| R-34 | Certificate expiry causes an outage | Automated renewal, expiry monitoring | 3 | Engineering owner |
| R-35 | Alert fatigue causes real signals to be ignored | K-01 small high-fidelity rule set, measured triage ratio | 4 | Security owner |
| R-36 | Irreversible retention applied with the wrong duration or to the wrong class | Staged rollout (`deployment-recommendations` §5), retention derived only from the service | 3 | Security owner |
| R-37 | Employee monitoring deployed without a lawful basis | K-14 — **legal advice pending (L-8)** | 4 | Legal / Client |
| R-38 | Third-party service breach affecting platform data | H-12 vendor intake gate; per-provider playbook | 4 | Security owner |
| R-39 | Dependency licence incompatible with CC-03 exclusive assignment | H-11 licence deny-list, review at addition time | 3 | Engineering owner |

## Residual risks proposed for acceptance — **NOT YET ACCEPTED**

These are risks this research judges cannot be economically eliminated. **None has been accepted by anyone.** Each requires an explicit decision by the Client, with a named accepting party and a review date, before it can be treated as accepted. Listing them here is a proposal, not an approval.

| ID | Risk | Rationale for proposing acceptance | Status |
|---|---|---|---|
| RA-01 | A determined insider photographs a screen to exfiltrate a small number of documents | No technical control prevents this. Watermarking provides attribution; volume is inherently limited | **Proposed — awaiting Client decision** |
| RA-02 | Single cloud provider concentration | The PRD selects AWS (TI-01). Portability and an exit plan are the proportionate response; multi-cloud would degrade every control through inconsistency | **Proposed — the provider choice is PRD-fixed; the residual is not formally accepted** |
| RA-03 | Blind index leaks equality and frequency information within a firm | Necessary for searchability of encrypted fields. Per-firm keys prevent cross-firm analysis; the field set is limited and documented | **Proposed — awaiting Client decision** |
| RA-04 | Prompt injection cannot be eliminated, only reduced | No complete technical defence exists. The PRD's own human-confirmation and two-approver rules are the substantive mitigation | **Proposed — awaiting Client decision** |
| RA-05 | Source code hosted outside EU-controlled infrastructure, if a non-EU repository provider is used | Source code is the Client's IP (CC-03), not client personal data. Build and deploy runners remain EU-resident | **Proposed — depends on the unresolved delivery topology (L-1)** |

## Register governance **[PROPOSED]**

- **Periodic review** of all risks with elevated residual scores by the named security owner, once one exists.
- **Full register review** on a longer cycle, reported to whoever the Client designates as accountable.
- **Every proposed acceptance carries a named accepting party and a review date before it counts as accepted.** An acceptance nobody signed is not an acceptance.
- **New risks** enter via threat modelling (`threat-modelling`), incident retrospectives, penetration tests, regulatory change review and vendor assessments.
- **Scores are re-baselined** against real incident data rather than carried forward unchanged.
- Risks link bidirectionally to controls in `security-control-matrix` and threats in `threat-model`, so a control regression surfaces the risks it affects.
- **Several residual scores above are inflated by unanswered questions** (R-09, R-10, R-11, R-16, R-25, R-31). Answering them is the cheapest risk reduction available in this register.
