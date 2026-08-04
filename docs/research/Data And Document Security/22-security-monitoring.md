# 22 — Security Monitoring

## Best practices

- **Detections are code.** Version-controlled, unit-tested against synthetic events, peer-reviewed, and deployed through CI. Detection rules edited live in a console drift, break silently, and cannot be audited.
- **Optimise for a small number of high-fidelity alerts.** A team that receives 200 alerts a day investigates none of them properly. Alert volume per analyst per day is a first-class engineering metric.
- **Detect at the layer where the truth is.** Network detections miss encrypted application abuse; application detections miss infrastructure compromise. Cover identity, network, host, application, data and cloud control plane.
- **Measure detection coverage against a threat model**, not against a vendor's rule count. Map coverage to MITRE ATT&CK and to our own threat model (doc 24), and track the gaps explicitly.
- **Automate the first five minutes of response.** Enrichment, containment of clear-cut cases, and evidence collection should happen before a human reads the alert.
- **Practise.** Purple-team exercises validate that detections actually fire on real techniques. Most rules that have never been tested do not work.

## EU regulatory implications

- **DORA Art. 10** — detection mechanisms: financial entities must have mechanisms to promptly detect anomalous activities, including ICT network performance issues and ICT-related incidents, with **multiple layers of control, defined alert thresholds and criteria to trigger incident response processes**, and sufficient resources and capabilities to monitor user activity, ICT anomalies and incidents. This is prescriptive and directly shapes the design below.
- **DORA Art. 17–19** — incident management: classification per **Delegated Reg. (EU) 2024/1772**, and reporting timelines under **Delegated Reg. (EU) 2025/301 / Implementing Reg. (EU) 2025/302** — working assumption **initial ≤4h from classification and ≤24h from detection, intermediate ≤72h, final ≤1 month** (verify against the published RTS/ITS before contracting).
- **DORA Art. 30(2)(f)/(3)** — contractual obligation to assist the customer during ICT incidents. Our detection quality directly determines whether they can meet their deadlines.
- **NIS2 Art. 23** — early warning within **24 hours**, incident notification within **72 hours**, final report within **1 month**, to the national CSIRT. As a likely in-scope entity, these are *our* deadlines, not only our customers'.
- **GDPR Art. 33** — notification to the supervisory authority within **72 hours** of becoming aware. "Becoming aware" starts when we have a reasonable degree of certainty that a breach occurred — detection quality determines when that clock starts and whether we can characterise scope in time. **Art. 33(2)** — as processor, we notify the controller "without undue delay" (contracted to 2 hours, DD-01-06).
- **MiCA Art. 68/69** — CASPs must notify competent authorities of incidents affecting their systems; our notifications feed theirs.
- **Employee monitoring constraints** — as in doc 17, security monitoring that processes employee personal data requires a lawful basis, transparency, proportionality and, in some member states, works council consultation.

## Recommended architecture

### Telemetry sources and coverage

| Layer | Sources | Primary detections |
|---|---|---|
| **Cloud control plane** | CloudTrail (all accounts/regions, management + S3/KMS data events), AWS Config, GuardDuty, Security Hub, IAM Access Analyzer | Privilege escalation, policy weakening, key policy change, public-access change, unusual region use, root account use |
| **Identity** | IdP sign-in and audit logs, IAM Identity Center, SCIM events, MFA events | Impossible travel, MFA fatigue/push bombing, new device, dormant account use, privilege grant, failed-then-successful auth |
| **Network** | VPC flow logs, DNS query logs, WAF, ALB, Network Firewall | Denied egress, DNS tunnelling, scanning, C2 beaconing patterns, unusual destination volume |
| **Host/container** | GuardDuty Runtime Monitoring or Falco, EKS audit logs | Container escape attempts, unexpected process execution, crypto-mining, package manager use in production containers |
| **Application** | Audit event stream (doc 14) | Authorisation denial spikes, enumeration patterns, bulk access, cross-tenant attempts, honeytoken access |
| **Data** | S3 data events, KMS usage, Macie findings | Mass download, unusual decrypt volume, access to a never-touched tenant, key operation anomalies |
| **AI** | Inference audit records (doc 05) | Prompt-injection signatures, anomalous token volume, citation-verification failure rate spike, model output schema violations |
| **CI/CD** | GitHub audit log, pipeline events, admission-controller denials | New workflow, OIDC trust change, unsigned image attempt, branch protection change, emergency deploy |
| **Endpoint** | EDR on workstations, MDM compliance | Malware, unmanaged device access, DLP triggers, credential dumping |

### Pipeline

```
Sources ──▶ normalisation (OCSF schema) ──▶ SIEM ──▶ detections-as-code
                                                          │
                                            ┌─────────────┼─────────────┐
                                            ▼             ▼             ▼
                                     Auto-enrichment  Auto-contain   Alert to
                                     (identity, asset, (clear-cut     on-call
                                      threat intel,     cases only)   with runbook
                                      recent changes)                  link
                                                          │
                                                          ▼
                                             Case management + evidence capture
                                                          │
                                            DORA/NIS2/GDPR classification engine
                                                          │
                                            Customer notification (≤2h SLA)
```

Normalising to **OCSF** (Open Cybersecurity Schema Framework) before ingestion means detection logic survives a SIEM migration — worth the modest upfront effort given the SIEM market's volatility.

### The detections that matter most here

Ranked by value for this specific platform:

1. **Honeytoken access** (document or credential) — zero false positives, immediate P1.
2. **Cross-tenant access attempt** — authorisation denial where `resource.tenant != principal.tenant`. Should be identically zero in normal operation.
3. **Bulk document access** — user exceeding their role's baseline by a defined multiple within a window.
4. **First-time tenant access by an operator** — support engineer touching a tenant they have never touched.
5. **KMS anomalies** — decrypt volume spike, key policy change, scheduled key deletion, grant creation.
6. **Break-glass without a matching incident ticket**.
7. **Denied egress from production** — should be near-zero; each occurrence is investigated.
8. **Object Lock or retention policy modification attempt**.
9. **Evidence hash-chain verification failure**.
10. **Unsigned image admission denial** in production.
11. **Prompt-injection signature detected** in an uploaded document.
12. **Root account use** in any AWS account.
13. **Impossible travel or new-country sign-in** for a privileged user.
14. **Production access from a non-EU location** — the technical detection backing the doc 03 control.

Each detection is defined in code with: rationale, ATT&CK mapping, data sources, false-positive profile, severity, runbook link, and a unit test containing both a positive and a negative event.

### Incident response

- **Severity model** mapped to both operational impact *and* regulatory classification, so the regulatory clock is evaluated at triage rather than discovered later:

| Sev | Definition | Response | Regulatory assessment |
|---|---|---|---|
| **P1** | Confirmed or probable customer data compromise; production unavailable; evidence integrity failure | Immediate page, incident commander, war room | Immediate DORA/NIS2/GDPR classification; customer notification clock starts |
| **P2** | Security control failure without confirmed data impact; single-tenant availability loss | Page during business hours, 4h response | Assessed within 4h |
| **P3** | Anomaly requiring investigation | Next business day | Assessed at closure |
| **P4** | Informational, tuning candidate | Backlog | N/A |

- **Regulatory classification engine:** a structured decision tool applying Delegated Reg. (EU) 2024/1772 criteria (clients affected, data losses, reputational impact, duration, geographical spread, economic impact, criticality of services affected), GDPR Art. 33 risk assessment, and NIS2 Art. 23 significance criteria. Produces a recommendation and a documented rationale, both retained as evidence. **The classification decision is the highest-stakes 30 minutes of any incident** — do not leave it to memory under pressure.
- **Customer notification templates** pre-drafted and legally reviewed, containing exactly what a customer needs for their own filing: nature of the incident, categories and approximate number of records and data subjects, likely consequences, measures taken, and our contact point.
- **Evidence preservation** is automatic at P1 declaration: snapshot affected instances, preserve logs beyond normal retention, capture memory where feasible, and record the chain of custody.
- **Retrospectives** are blameless, produce dated actions with owners, and feed DORA Art. 13 "learning and evolving" evidence.

### Staffing reality

24/7 human SOC coverage is not achievable for a small team. The realistic model:
- Automated detection and containment running continuously.
- P1 alerts page an on-call security engineer (EU-based, per doc 03) with a 15-minute acknowledgement SLA.
- An **MDR/MSSP provider for 24/7 triage** of the alert queue, escalating true positives. Choose one with EU data processing and an acceptable DPA; they become a sub-processor.
- Internal capability grows before the MDR relationship is unwound, not after.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Alert fatigue causes real incidents to be missed | Detection exists on paper only | Small high-fidelity rule set; measured alerts-per-analyst-per-day; ruthless tuning; suppression requires a dated ticket |
| Detection gap for a technique not modelled | Undetected compromise | ATT&CK coverage mapping, quarterly purple-team exercises, coverage gaps tracked as risks |
| Log source silently stops (agent dies, permission change) | Blind spot with no alarm | Heartbeat monitoring per source; alert on absence of expected events, not just on events |
| Regulatory clock missed because classification was slow | Late notification, supervisory enforcement | Classification engine at triage, timers on every incident, escalation on 50% of deadline elapsed |
| Insufficient log detail to scope a breach within 72 hours | Cannot answer "whose data, how many records" | Audit event design (doc 14); scoping queries pre-written and tested against synthetic incidents |
| MDR provider's access becomes an insider risk | Third-party access to security telemetry and possibly data | Scope their access to telemetry only, never to production data; audit their access; contractual DORA terms |
| Monitoring of employees deployed without a lawful basis | Regulatory and employment-law exposure | Legitimate-interests balancing test, transparency notice, works council consultation where required |
| Cost of full-fidelity logging at scale | Sampling introduced, gaps appear | Tiered retention (hot 90d, warm 1y, cold 7y), route audit events to cheap immutable storage, keep only detection-relevant data in the SIEM |

## Trade-offs

- **Commercial SIEM (fast, rich content, per-GB cost that scales alarmingly) vs. open-source (OpenSearch/Wazuh — cheap at volume, real engineering investment) vs. cloud-native (Security Lake + Athena — cheap, less interactive).** **Recommendation: start with AWS Security Hub + GuardDuty + Security Lake and a lightweight detection layer; adopt a commercial SIEM when the security team can exploit it. Normalise to OCSF from day one so the migration is cheap.**
- **MDR provider (24/7 coverage now, cost, another sub-processor) vs. internal-only (cheaper, gaps overnight and at weekends).** A crypto-sector platform will be attacked outside business hours specifically. **Recommendation: MDR from launch, scoped to telemetry only, with an EU processing commitment.**
- **Auto-containment (fast, risk of automated self-inflicted outage) vs. human-approved.** **Recommendation: auto-contain only unambiguous cases — disable a credential on honeytoken use, block an IP on confirmed scanning, revoke a session on impossible travel. Everything else is human-approved.**
- **Full-fidelity retention (best forensics, high cost) vs. tiered.** **Recommendation: tiered — 90 days hot and searchable, 1 year warm, 7 years cold in immutable storage for audit events only.**
- **Detections-as-code (auditable, testable, slower to iterate) vs. console-authored rules.** **Recommendation: as code, without exception. It is also DORA change-management evidence.**

## Design decisions

- **DD-22-01:** All detections defined as version-controlled code with rationale, ATT&CK mapping, false-positive profile, runbook, and mandatory positive/negative unit tests. No console-authored rules.
- **DD-22-02:** Telemetry normalised to OCSF before ingestion to preserve detection portability.
- **DD-22-03:** The 14 priority detections listed above are implemented before general availability; honeytoken and cross-tenant-attempt detections are P1 with automated containment.
- **DD-22-04:** Heartbeat monitoring on every log source; absence of expected events raises an alert.
- **DD-22-05:** Severity model links operational impact to regulatory classification; a structured classification engine applying Delegated Reg. (EU) 2024/1772, GDPR Art. 33 and NIS2 Art. 23 criteria runs at triage and its rationale is retained as evidence.
- **DD-22-06:** Customer notification within 2 hours of confirmation, using pre-drafted, legally-reviewed templates containing the data customers need for their own filings.
- **DD-22-07:** Automatic evidence preservation on P1 declaration, with chain-of-custody recording.
- **DD-22-08:** MDR provider engaged for 24/7 triage from launch, scoped to security telemetry only with no production data access, under EU processing terms and listed as a sub-processor.
- **DD-22-09:** Auto-containment limited to unambiguous cases; all other response actions are human-approved.
- **DD-22-10:** Quarterly purple-team exercises validate detection efficacy; coverage gaps are tracked in the risk register.
- **DD-22-11:** Tiered retention — 90 days hot, 1 year warm, 7 years cold immutable for audit events.

## References

- Regulation (EU) 2022/2554 (DORA) Art. 10, 13, 17–19, 30; Commission Delegated Regulation (EU) 2024/1772; Commission Delegated Regulation (EU) 2025/301 and Implementing Regulation (EU) 2025/302 (incident reporting content and time limits — verify)
- Directive (EU) 2022/2555 (NIS2) Art. 23
- Regulation (EU) 2016/679 (GDPR) Art. 33, 34; EDPB Guidelines 9/2022 on personal data breach notification
- NIST SP 800-61 Rev. 2 — Computer Security Incident Handling Guide
- NIST SP 800-92 — Log Management
- MITRE ATT&CK Enterprise and Cloud matrices; MITRE ATLAS for AI-specific techniques
- Open Cybersecurity Schema Framework (OCSF)
- ENISA — Threat Landscape; ENISA NIS2 Technical Implementation Guidance (2025)

## Confidence level

**High** — detections-as-code, the priority detection set, source heartbeat monitoring, the classification-at-triage model, and MDR augmentation. These are correct and directly satisfy DORA Art. 10 and the reporting regimes.

**Medium** — precise DORA incident reporting time limits under the 2025 RTS/ITS (verify against the published texts before contracting), and SIEM cost at eventual log volumes, which is the most common budget overrun in this area and should be modelled at 5× projected volume.
