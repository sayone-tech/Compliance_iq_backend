# Security Monitoring and Incident Response

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

Not named by the PRD. Everything here is **[PROPOSED]** unless marked. Its purpose is to detect a breach of NFR-01, NFR-04 or NFR-07 quickly enough to act, and to give client firms what they need for their own regulatory obligations.

## Best practices

- **Detections are code.** Version-controlled, unit-tested against synthetic events, peer-reviewed, deployed through CI. Rules edited live in a console drift, break silently and cannot be audited.
- **Optimise for a small number of high-fidelity alerts.** A team receiving hundreds of alerts a day investigates none of them properly. Alert volume per analyst per day is a first-class engineering metric.
- **Detect at the layer where the truth is.** Network detections miss encrypted application abuse; application detections miss infrastructure compromise.
- **Measure detection coverage against a threat model**, not against a vendor's rule count (`threat-model`).
- **Automate the first few minutes of response.** Enrichment, containment of clear-cut cases, and evidence collection should happen before a human reads the alert.
- **Practise.** Rules that have never been tested mostly do not work.

## Regulatory implications

- **GDPR Art. 33** — notification to the supervisory authority within 72 hours of becoming aware. As a **processor** (NFR-06), the platform's duty is to notify the controller — the client firm — "without undue delay". **A specific numeric SLA is not set by the PRD and is a contractual matter.** **[OPEN]**
- **GDPR Art. 34** — communication to data subjects where there is high risk; not required where data was rendered unintelligible by encryption with uncompromised keys (`encryption-architecture`).
- **Detection quality determines when "becoming aware" starts** and whether the scope can be characterised in time. That is the practical reason to invest here.
- **DORA and MiCA incident reporting are the customer's obligations, not the platform's.** The PRD builds tooling for the customer's four-hour DORA notification workflow (FR-76) as a *product feature*; that is not a statement about the platform vendor's own reporting duties. Whether any DORA reporting obligation flows to the platform by contract is **[OPEN]** (`regulatory-obligations`).
- **NIS2 Art. 23** reporting deadlines would apply **only if** NIS2 applies to the platform, which is undetermined. **[OPEN — LEGAL]** No NIS2 reporting commitment is made here.
- **Employee monitoring constraints** — as in `insider-threat-protection`, security monitoring that processes employee personal data requires a lawful basis, transparency and proportionality, and in some member states consultation.

## Recommended architecture

### Telemetry sources and coverage

| Layer | Sources | Primary detections |
|---|---|---|
| **Cloud control plane** | Control-plane audit trail across all accounts and regions, configuration state, threat-detection service, access analyser | Privilege escalation, policy weakening, key policy change, public-access change, non-EU region use, root account use |
| **Identity** | Identity provider sign-in and audit logs, MFA events, provisioning events | Impossible travel, MFA fatigue, new device, dormant account use, privilege grant, failed-then-successful authentication |
| **Network** | Flow logs, DNS query logs, WAF, load balancer, egress firewall | Denied egress, DNS tunnelling, scanning, beaconing patterns, unusual destination volume |
| **Host / container** | Runtime monitoring, orchestrator audit logs | Container escape attempts, unexpected process execution, package manager use in production |
| **Application** | The audit event stream (`audit-logging`) | Authorisation denial spikes, enumeration patterns, bulk access, cross-firm attempts, canary access |
| **Data** | Storage and key data events | Mass download, unusual decrypt volume, access to a never-touched firm, key operation anomalies |
| **AI** | Inference audit records (`ai-governance`) | Prompt-injection signatures, anomalous token volume, span-verification failure rate spike, output schema violations |
| **CI/CD** | Repository audit log, pipeline events, admission denials | New workflow, federation trust change, unsigned artefact attempt, branch protection change, emergency deploy |
| **Endpoint** | Endpoint detection on workstations, device management compliance | Malware, unmanaged device access, data-loss-prevention triggers |

### Pipeline

```
Sources ──▶ normalisation to a common schema ──▶ detection layer (rules as code)
                                                        │
                                          ┌─────────────┼─────────────┐
                                          ▼             ▼             ▼
                                   Auto-enrichment  Auto-contain   Alert to
                                   (identity,       (clear-cut     on-call with
                                    asset, recent    cases only)   a runbook link
                                    changes)
                                                        │
                                                        ▼
                                         Case record + evidence capture
                                                        │
                                            Regulatory assessment
                                                        │
                                            Notification to affected firms
```

Normalising to a common event schema before ingestion means detection logic survives a tooling change — worth the modest upfront effort.

### The detections that matter most here

Ranked by value for this specific platform:

1. **Canary record access** (document or credential) — zero false positives, immediate top severity.
2. **Cross-firm access attempt** — an authorisation denial where the resource firm differs from the principal's firm. Should be identically zero in normal operation. **This is the NFR-01 tripwire.**
3. **Attempted delete or modify on a protected record or audit entry** — should also be identically zero. **This is the NFR-04 / NFR-07 tripwire.**
4. **Bulk evidence access** — a user exceeding their role's baseline by a defined multiple within a window.
5. **First-time firm access by a workforce user.**
6. **Key anomalies** — decrypt volume spike, key policy change, any deletion attempt, grant creation.
7. **Break-glass used without a matching incident record.**
8. **Denied egress from production** — should be near zero; each occurrence investigated.
9. **Write-once retention or retention-policy modification attempt.**
10. **Evidence hash-chain verification failure.**
11. **Unsigned artefact admission denial in production.**
12. **Prompt-injection signature detected in an uploaded WSP.**
13. **Root account use in any account.**
14. **Impossible travel or new-country sign-in for a privileged user.**
15. **Production access from a non-approved location** — the technical detection backing the `cross-border-data-processing` control.

Each detection is defined in code with rationale, technique mapping, data sources, false-positive profile, severity, runbook link, and a unit test containing both a positive and a negative event.

### Incident response

**Severity model**, with the regulatory assessment evaluated at triage rather than discovered later:

| Severity | Definition | Response | Regulatory assessment |
|---|---|---|---|
| **P1** | Confirmed or probable client data compromise; production unavailable; audit or evidence integrity failure | Immediate page, incident commander | Immediate GDPR Art. 33 processor assessment; firm notification clock starts |
| **P2** | Security control failure without confirmed data impact; single-firm availability loss | Same-business-day response | Assessed promptly |
| **P3** | Anomaly requiring investigation | Next business day | Assessed at closure |
| **P4** | Informational, tuning candidate | Backlog | Not applicable |

- **Regulatory assessment tooling:** a structured decision aid applying GDPR Art. 33 risk criteria and producing a documented rationale retained as evidence. Additional regimes are added **only if and when** their applicability is confirmed (`regulatory-obligations`). **The assessment decision is the highest-stakes half-hour of any incident** — do not leave it to memory under pressure.
- **Firm notification templates**, pre-drafted and legally reviewed, containing exactly what a firm needs for its own filing: nature of the incident, categories and approximate number of records and data subjects, likely consequences, measures taken, and a contact point. **The notification deadline is a contractual term to be agreed, not a figure this research invents.** **[OPEN]**
- **Evidence preservation** automatic at P1: snapshot affected instances, preserve logs beyond normal retention, record chain of custody.
- **Retrospectives** are blameless, produce dated actions with owners, and feed the threat model (`threat-modelling`).

### Staffing

Continuous human coverage is a cost and headcount decision the PRD does not make. The realistic shape:

- Automated detection and containment run continuously — this part is engineering, not headcount.
- P1 alerts page a named on-call responder with an acknowledgement target.
- **Whether that on-call is internal, contracted, EU-resident, or a managed detection and response provider is [OPEN]** (`open-questions`, O-2). If a provider is engaged, scope their access to security telemetry only — never production data — under EU processing terms, and list them as a sub-processor.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Alert fatigue causes real incidents to be missed | Detection exists on paper only | Small high-fidelity rule set; measured alerts per analyst per day; ruthless tuning; dated suppressions |
| Detection gap for an unmodelled technique | Undetected compromise | Coverage mapping against the threat model; gaps tracked as risks |
| A log source silently stops | Blind spot with no alarm | Heartbeat monitoring per source; alert on the *absence* of expected events |
| Insufficient log detail to scope a breach in 72 hours | Cannot answer "whose data, how many records" | Audit event design (`audit-logging`); scoping queries pre-written and tested against synthetic incidents |
| Slow regulatory assessment | Late notification to firms; their own deadlines missed | Assessment at triage; timers on every incident; escalation part-way to any agreed deadline |
| A monitoring provider's access becomes an insider risk | Third-party access to security telemetry | Scope to telemetry only, never production data; audit their access; contractual terms |
| Employee monitoring deployed without a lawful basis | Regulatory and employment-law exposure | Balancing test, transparency notice, consultation where required |
| Logging cost at six-year audit retention | Sampling introduced; evidence gaps appear | Tiered retention — recent window searchable, older audit events in cheap immutable storage, never sampled |

## Trade-offs

- **Commercial monitoring platform vs. cloud-native services plus a lightweight detection layer vs. open source.** Recommendation: start with the cloud provider's native detection services plus a rules-as-code layer; adopt a commercial platform when there is a security function able to exploit it. Normalise to a common schema from day one so migration is cheap. **[PROPOSED / OPEN on cost]**
- **Continuous external triage vs. internal-only.** A platform serving crypto-sector firms will be probed outside business hours. Recommendation: put the cost of continuous coverage to the Client alongside the residual risk of not having it. **[OPEN]**
- **Automatic containment vs. human approval.** Recommendation: automatically contain only unambiguous cases — disable a credential on canary access, block an IP on confirmed scanning, revoke a session on impossible travel. Everything else human-approved. **[PROPOSED]**
- **Full-fidelity retention vs. tiered.** Recommendation: tiered — a searchable recent window, then long-term audit retention in immutable storage per NFR-07's six-year minimum. **[PROPOSED]**
- **Adversarial validation exercises.** Valuable for proving detections fire, but a recurring cost the PRD does not fund. **[FUTURE]**

## Design decisions

| ID | Decision | Classification |
|---|---|---|
| DD-22-01 | All detections defined as version-controlled code with rationale, technique mapping, false-positive profile, runbook and mandatory positive/negative unit tests. No console-authored rules | **[PROPOSED]** |
| DD-22-02 | Telemetry normalised to a common schema before ingestion to preserve detection portability | **[PROPOSED]** |
| DD-22-03 | The priority detections listed above are implemented before real client data is accepted; canary access, cross-firm attempts and protected-record modification attempts are top severity with automated containment | **[PROPOSED]** — protects NFR-01, NFR-04, NFR-07 |
| DD-22-04 | Heartbeat monitoring on every log source; absence of expected events raises an alert | **[PROPOSED]** |
| DD-22-05 | Severity model links operational impact to a GDPR Art. 33 processor assessment performed at triage, with the rationale retained | **[PROPOSED]** |
| DD-22-06 | Pre-drafted, legally reviewed firm notification templates; **the notification deadline is agreed contractually, not assumed** | **[PROPOSED / OPEN]** |
| DD-22-07 | Automatic evidence preservation on P1 declaration with chain-of-custody recording | **[PROPOSED]** |
| DD-22-08 | Continuous alert triage model (internal, contracted, or provider) | **[OPEN]** |
| DD-22-09 | Automatic containment limited to unambiguous cases; all other response actions human-approved | **[PROPOSED]** |
| DD-22-10 | Tiered retention: searchable recent window, then audit events in immutable storage for the six-year minimum | **[PROPOSED]** — NFR-07 |
| DD-22-11 | No NIS2 or DORA reporting commitment is made until applicability is confirmed | **[OPEN — LEGAL]** |

## References

- Regulation (EU) 2016/679 (GDPR) Art. 33, 34; EDPB Guidelines 9/2022 on personal data breach notification
- Regulation (EU) 2022/2554 (DORA) Art. 10, 17–19; Commission Delegated Regulation (EU) 2024/1772 *(customer-side, design reference)*
- Directive (EU) 2022/2555 (NIS2) Art. 23 — conditional on scope
- NIST SP 800-61 Rev. 2 — Computer Security Incident Handling Guide
- NIST SP 800-92 — Log Management
- MITRE ATT&CK Enterprise and Cloud matrices; MITRE ATLAS for AI-specific techniques
- Open Cybersecurity Schema Framework (OCSF)

## Confidence level

**High** — detections as code, the priority detection set, source heartbeat monitoring, and assessment at triage.

**Not determined** — the incident notification deadline to firms, the continuous-coverage staffing model, and whether any regime beyond GDPR imposes reporting duties on the platform.
