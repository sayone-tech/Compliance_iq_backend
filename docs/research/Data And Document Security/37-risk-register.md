# 37 — Risk Register

Consolidated from the per-topic risk tables. Scoring: Likelihood (L) and Impact (I) 1–5. **Inherent** = before controls. **Residual** = with the controls in doc 31 implemented. Risks are ordered by residual score.

**Impact scale:** 5 = existential (company-ending or regulatory withdrawal of customer authorisation) · 4 = severe (major fine, mass customer loss) · 3 = significant (customer loss, remediation cost) · 2 = moderate · 1 = minor.

## Top risks (residual ≥ 8)

| ID | Risk | Category | Inherent (L×I) | Controls | Residual | Owner | Review |
|---|---|---|---|---|---|---|---|
| R-01 | **Cross-tenant document disclosure** via application, cache, index or key-scoping failure | Confidentiality | 4×5 = 20 | E-02 four-layer isolation, C-04 test matrix, D-06 encryption context, H-02 SAST rules, quarterly purple team | **10** | Head of Security | Monthly |
| R-02 | **Prompt injection in uploaded documents** produces a false compliance conclusion relied upon by a customer | AI / integrity | 4×5 = 20 | I-04 delimiting + schema constraints, I-05 citation verification, I-06 human approval, injection detection, red-teaming | **10** | Head of AI/Product | Monthly |
| R-03 | **Malicious or coerced insider exfiltrates customer documents** | Insider | 3×5 = 15 | B-07 zero standing access, D-13 enclaves, K-04 honeytokens, K-11 rate limits, K-12 tenant visibility, screening | **9** | Head of Security | Monthly |
| R-04 | **Unlawful EU→India transfer** through production access, data copy, or AI tooling paste | Regulatory | 4×4 = 16 | B-04 SCCs, B-05 TIA, B-06 synthetic-only, B-07/B-08 access controls, I-01/I-02 AI tooling controls | **8** | DPO | Monthly |
| R-05 | **Compromised upstream dependency** introduces a backdoor into production | Supply chain | 3×5 = 15 | H-11 pinning + cooldown, H-10 SBOM re-eval, G-04 egress limits, H-09 admission verification, runtime detection | **8** | Platform Lead | Monthly |
| R-06 | **Ransomware** encrypts production and attempts backup destruction | Availability | 3×5 = 15 | J-03 account isolation, J-04 Vault Lock compliance, F-04 Object Lock, J-05 daily restore verification | **8** | SRE Lead | Quarterly |
| R-07 | **Hallucinated regulatory citation** reaches a customer's regulatory filing | AI / integrity | 4×4 = 16 | I-05 deterministic citation verification (blocking), confidence thresholds, I-06 human approval, I-10 labelling | **8** | Head of AI/Product | Monthly |
| R-08 | **Incident misclassified or reported late**, breaching DORA/NIS2/GDPR deadlines | Regulatory | 3×4 = 12 | K-05 classification engine at triage, K-06 2-hour SLA, deadline timers with escalation, annual drill | **8** | Head of Security | Quarterly |

## Significant risks (residual 5–7)

| ID | Risk | Category | Inherent | Controls | Residual | Owner |
|---|---|---|---|---|---|---|
| R-09 | Customer-managed key (T2/T3) unavailable, causing tenant outage | Availability | 3×4 | D-11 canary monitoring, contractual HA, key-degraded mode, SLA carve-out | 7 | Platform Lead |
| R-10 | Accidental or malicious key deletion destroys tenant data permanently | Availability | 2×5 | D-09 30-day window + dual approval + alerting, deletion denied for audit/evidence keys | 6 | Head of Security |
| R-11 | MFA bypass via help-desk social engineering on a privileged account | Access | 3×4 | Identity-proofing procedure with manager callback, FIDO2 for privileged, recovery-flow hardening | 6 | Head of Security |
| R-12 | Cloud misconfiguration exposes a bucket or database publicly | Confidentiality | 3×5 | Account-level Block Public Access, IaC-only changes, Config rules, continuous conformance scanning | 6 | Platform Lead |
| R-13 | Compromised CI/CD pipeline deploys malicious code | Supply chain | 2×5 | H-06 OIDC narrow trust, H-07 ephemeral runners, trust zoning, H-09 admission, H-13 GitOps, digest reconciliation | 6 | Platform Lead |
| R-14 | Evidence created fraudulently at source by a tenant user to conceal a compliance failure | Integrity | 3×5 | F-07 QTSP timestamp binding creation time, named-reviewer approval workflow, immutable creation audit | 6 | Head of Product |
| R-15 | Audit log gap prevents scoping a breach within 72 hours | Regulatory | 3×4 | F-06 coverage tests, F-05 synchronous writes, pre-written and tested scoping queries | 6 | Head of Security |
| R-16 | Regulatory change (AMLR 2027, CRA 2026/27, AI Act 2026/27) outpaces the obligation register | Regulatory | 3×3 | A-01 register as code, quarterly review, named owner, regulatory feed subscriptions | 6 | Compliance Lead |
| R-17 | Customer discovers Indian development late in procurement | Commercial | 3×3 | Proactive disclosure in the security pack, control narrative, A-06 sub-processor register | 5 | CEO |
| R-18 | Parser exploit in document processing yields RCE | Confidentiality | 3×4 | E-09 no credentials/no egress/ephemeral/separate account, memory-safe parsers, resource limits | 5 | Platform Lead |
| R-19 | Untested restore fails during a real disaster | Availability | 3×5 | J-05 daily automated restore verification, J-06 semi-annual full failover and failback | 5 | SRE Lead |
| R-20 | Derivative artefacts (thumbnails, extracted text, embeddings) escape access control | Confidentiality | 3×4 | E-05 derivative registry, classification/key inheritance, daily reconciliation | 5 | Engineering Lead |
| R-21 | Retention misconfiguration destroys records before the legal minimum, or retains beyond it | Regulatory | 2×5 | F-09 policy engine as single source, Object Lock, F-10 expiry job evidence, quarterly conformance report | 5 | Compliance Lead |
| R-22 | Malware uploaded and later distributed to customers | Integrity | 3×4 | E-08 quarantine-scan-promote fail-closed, multi-engine, 7-day rescan on signature update | 5 | Platform Lead |
| R-23 | AWS concentration risk challenged by a customer or supervisor | Regulatory / resilience | 3×3 | Documented concentration analysis, portability engineering, annually tested exit plan, honest disclosure | 5 | CTO |
| R-24 | AI provider changes terms, region or retention policy | Third party | 2×4 | Contractual change-notice, I-09 fallback provider exercised quarterly, annual review | 5 | CTO |
| R-25 | Session token theft via XSS in a rendered document | Access | 3×4 | E-10 separate content origin, CSP sandbox, nosniff, server-side rendering default | 5 | Engineering Lead |

## Managed risks (residual ≤ 4)

| ID | Risk | Controls | Residual | Owner |
|---|---|---|---|---|
| R-26 | Insider alters or deletes evidence to conceal an action | Object Lock COMPLIANCE, write-only log archive, hash chain, QTSP timestamps, separation of duties | 3 | Head of Security |
| R-27 | Secret committed to source control | Pre-commit + blocking PR scan + push protection, honeytokens, 5-minute automated revocation | 4 | Engineering Lead |
| R-28 | Regional outage exceeds RTO | Warm standby, tested failover, DR-region parity checks | 4 | SRE Lead |
| R-29 | DDoS during a customer's regulatory deadline | CloudFront + WAF + Shield, autoscaling, evidence-only degraded read path | 4 | SRE Lead |
| R-30 | Privilege creep through role changes | Group-based assignment, quarterly recertification, IAM Access Analyzer unused-access findings | 4 | Head of Security |
| R-31 | Data exfiltration through an allowlisted egress destination | Per-destination volume anomaly detection, single application egress service with classification checks | 4 | Platform Lead |
| R-32 | Customer IdP misconfiguration grants unauthorised tenant access | Assertion signing and audience restriction enforced, onboarding validation, periodic re-validation | 4 | Engineering Lead |
| R-33 | Model or prompt change silently degrades assessment quality | Model registry, golden-set evaluation gate, prompt versioning, rollback target | 4 | Head of AI/Product |
| R-34 | Employee monitoring deployed without a lawful basis or consultation | Legal review, privacy notice, balancing test, works council consultation where required | 4 | DPO |
| R-35 | Backup or replica placed outside the EU | SCP restricting replication destinations, continuous conformance scanning | 3 | Platform Lead |
| R-36 | Hash chain broken by an ingestion gap, indistinguishable from tampering | Single-writer sealer, monotonic sequence, gap detection, documented repair producing evidence | 4 | Engineering Lead |
| R-37 | Certificate expiry causes an outage | ACM auto-renewal, expiry monitoring at 30/14/7 days, no manual certificates | 3 | SRE Lead |
| R-38 | Alert fatigue causes real incidents to be missed | Small high-fidelity rule set, measured alerts per analyst, tuning discipline, dated suppressions | 4 | Head of Security |
| R-39 | Object Lock COMPLIANCE applied with wrong retention or to the wrong data | Staged rollout via GOVERNANCE, seal-preview, retention derived only from policy engine, bucket separation | 3 | Compliance Lead |
| R-40 | Third-party service breach affecting our data | Vendor intake gate, contractual notification SLA, data minimisation per provider, per-provider playbook | 4 | Head of Security |

## Accepted risks (no further mitigation planned)

| ID | Risk | Rationale for acceptance | Owner | Expiry |
|---|---|---|---|---|
| RA-01 | A determined insider photographs a screen to exfiltrate a small number of documents | No technical control prevents this. Watermarking provides attribution; volume is inherently limited | Head of Security | Annual review |
| RA-02 | AWS as a single cloud provider (concentration risk) | Multi-cloud would roughly double operational surface and degrade every control through inconsistency. Portability and a tested exit plan are the proportionate response (ADR-002) | CTO | Annual review |
| RA-03 | Blind index leaks equality and frequency information within a tenant | Necessary for searchability of encrypted fields. Per-tenant keys prevent cross-tenant analysis; field set is limited and documented | Engineering Lead | Annual review |
| RA-04 | Backup data cannot be selectively erased; crypto-shredding is used instead | The only workable resolution of GDPR Art. 17 against immutable backups. Disclosed in the DPA (A-4 in doc 36 pending) | DPO | On A-4 resolution |
| RA-05 | Source code repositories hosted outside EU-controlled infrastructure (GitHub) | Source code is our IP, not customer personal data. Zone 2/3 CI is EU-resident | CTO | Annual review |
| RA-06 | T2/T3 customers can render their own data permanently unrecoverable | Inherent to the security guarantee they are buying. Contractually acknowledged with separate signature | CEO | Per contract |

## Register governance

- **Monthly review** of all risks with residual ≥ 8 by the Head of Security.
- **Quarterly review** of the full register; reported to the management body (DORA Art. 5(2) accountability).
- **Every accepted risk carries a named owner and an expiry date.** Expired acceptances escalate to the management body rather than lapsing silently.
- **New risks** enter via: threat modelling (doc 24), incident retrospectives, penetration tests, purple-team exercises, regulatory change review, and vendor assessments.
- **Scores are re-baselined annually** against actual incident data and threat intelligence rather than carried forward unchanged.
- Risks are linked bidirectionally to controls in doc 31 and threats in doc 32, so a control regression automatically surfaces the risks it affects.
