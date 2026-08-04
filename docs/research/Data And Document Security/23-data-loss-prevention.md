# 23 — Data Loss Prevention

DLP has a poor reputation because it is usually deployed as a content-inspection product bolted onto an architecture that already permits exfiltration. The effective approach inverts this: **architectural controls that make exfiltration paths not exist, with content inspection as a detective backstop on the few paths that must remain open.**

## Best practices

- **Close paths before inspecting content.** Default-deny egress (doc 11), no standing production access (doc 10), no production data in development (doc 03), enclave-based decryption (doc 07) — each of these eliminates an exfiltration channel entirely, which no content-inspection product can match.
- **Rate-limit and threshold everything that reads data.** Volume is the most reliable exfiltration signal and the cheapest to implement.
- **Watermark what leaves.** Dynamic per-user watermarks on previews and exports make leaked documents traceable to an individual, which is a strong deterrent and a genuine forensic aid.
- **Classify first.** DLP without classification either blocks everything or nothing. Our classification model (doc 06) is the input.
- **Accept that determined exfiltration cannot be fully prevented** — a photograph of a screen defeats every technical control. Optimise for making it slow, small-scale, detectable and attributable.
- **Measure false positives.** A DLP that blocks legitimate work will be disabled, formally or informally.

## EU regulatory implications

- **GDPR Art. 32** — DLP is a security-of-processing measure; **Art. 5(1)(f)** confidentiality; **Art. 33/34** — an exfiltration event is a notifiable breach, and DLP telemetry determines whether we can characterise scope within 72 hours.
- **GDPR Art. 25** — data protection by default: personal data should not be accessible or extractable beyond what the purpose requires.
- **DORA Art. 9(4)(d)** and **Delegated Reg. (EU) 2024/1774** — data and system security, including measures to prevent data leakage and to protect data in transit and at rest; explicit expectations around controlling data flows and preventing unauthorised disclosure.
- **NIS2 Art. 21(2)** — risk management measures covering data security and incident handling.
- **MiCA Art. 68** — confidentiality of client records; a leak of a CASP's compliance evidence has direct supervisory consequences for them.
- **Employee monitoring constraint** — endpoint DLP and content inspection process employee personal data and communications. This requires a lawful basis, transparency, proportionality, and — in Germany and several other member states — **works council consultation**. Inspecting employee email or chat content is legally sensitive; in some jurisdictions, near-impossible without consultation. Design accordingly rather than assuming.
- **Cross-border (doc 03)** — DLP on the India ⇄ EU channel is a supplementary measure supporting the transfer assessment.

## Recommended architecture

### Layer 1 — Architectural elimination (highest value, do this first)

| Exfiltration path | How it is eliminated |
|---|---|
| Developer copies production data | No production data in dev; no production credentials in Zone D (doc 03) |
| Compromised service calls out to attacker infrastructure | Default-deny egress with FQDN allowlist; data tier has no internet route (doc 11) |
| Operator reads document plaintext | Zero standing access; enclave decryption; no operator shell (docs 7, 10, 17) |
| Database dumped via a direct connection | No public endpoint; IAM auth; access only from the application security group |
| Backup copied out | Backup account isolation; no cross-account read path (doc 21) |
| Bulk API scraping | Per-user and per-tenant rate limits; pagination caps; bulk export requires approval |
| Presigned URL shared externally | ≤60s TTL, single use, IP-bound where feasible (doc 06) |
| Search index or embeddings exfiltrated | In-region, tenant-key encrypted, no external access path |

**This layer does most of the work.** Everything below is a backstop.

### Layer 2 — Egress inspection and control

- **Network egress:** AWS Network Firewall with domain allowlisting and TLS SNI inspection; every denied connection alerts (doc 11). Volume anomaly detection on allowed destinations catches abuse of a legitimate channel.
- **Application egress:** all outbound integrations (webhooks, exports to customer systems, email) go through a single egress service that enforces destination allowlists, applies size limits, logs the full transfer with classification metadata, and applies content policy.
- **DNS:** query logging and DNS Firewall detect tunnelling (doc 11).

### Layer 3 — Application-layer controls (the highest-signal DLP for this product)

Because we control the application, we can enforce DLP at exactly the right place — far more precisely than any network product:

| Control | Implementation |
|---|---|
| **Access rate limits** | Per-role baselines; soft alert at 2×, hard block at 5×, per rolling hour |
| **Bulk export gate** | Exports above N documents require step-up auth, stated purpose, and tenant-admin approval; always watermarked; always customer-notified |
| **Download vs. preview** | Preview is the default; raw download is a distinct permission, logged, and rate-limited separately |
| **Dynamic watermarking** | User email, tenant, timestamp, document ID rendered into every preview and exported PDF; visible and (where supported) steganographic |
| **Copy protection in the viewer** | Disable text selection and right-click for `RESTRICTED`/`PRIVILEGED` previews. Weak against a determined user, but it stops casual copying and signals intent |
| **API pagination caps** | Hard maximum page size; cursor-based pagination; no unbounded list endpoints |
| **Screenshot deterrence** | Watermarks survive screenshots — the pragmatic answer, since screenshot prevention is not achievable in a browser |
| **Egress classification check** | Any outbound transfer of `RESTRICTED`/`PRIVILEGED` content requires explicit policy allowance |

### Layer 4 — Endpoint DLP (workforce)

Scoped narrowly and lawfully:
- **Managed devices only** for any access to customer data (doc 12 device trust).
- Block: removable media write, personal cloud sync clients (Dropbox, Google Drive, personal OneDrive), unmanaged browser profiles for work applications.
- **Clipboard and paste monitoring into AI tools** — specifically, blocking paste of content matching customer-data patterns into developer AI tooling (doc 05). This is the highest-value endpoint DLP rule in our environment.
- **Do not** deploy broad email/chat content inspection initially. It is legally sensitive in the EU, requires works council consultation, generates enormous false-positive volume, and is largely redundant given that employees have no access to production data in the first place.

### Layer 5 — Cloud data discovery

- **Amazon Macie** scanning S3 for unexpected sensitive-data placement — for example, personal data appearing in a bucket that should contain only logs or artefacts. This detects the misconfiguration class of data loss rather than the malicious class, and it is where most real-world "DLP" incidents actually originate.
- Automated scan of non-production accounts for anything resembling production data — enforcing DD-03-02 rather than merely stating it.

### Detection and response

Priority DLP detections (feeding doc 22):
1. Honeytoken document accessed.
2. User exceeds access baseline by 5×.
3. Bulk export requested outside business hours.
4. Denied egress from a production workload.
5. First-time access to a tenant by an operator.
6. Macie finding: sensitive data in an unexpected location.
7. Paste of customer-data-pattern content into an AI tool.
8. Sustained elevated download volume by a user under HR risk flag.

Response is graduated: alert → step-up authentication challenge → session termination → account suspension pending investigation. Automatic suspension is reserved for honeytoken access and confirmed cross-tenant attempts.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| DLP false positives block legitimate compliance work | Customer impact; DLP disabled under pressure | Application-layer controls tuned to measured role baselines; graduated response rather than immediate blocking; documented exception path |
| Determined insider photographs the screen | Undetectable exfiltration | Accept as residual; watermarks aid attribution; limit what can be displayed at once; rate-limit views |
| Endpoint DLP deployed without a lawful basis or works council consultation | Regulatory and employment-law exposure; evidence inadmissible | Legal review; transparency notice; proportionality assessment; narrow scope |
| Exfiltration via an allowlisted egress destination | Slow leak through a legitimate channel | Volume anomaly detection per destination; application egress service logs and classifies every transfer |
| Watermarks stripped or cropped | Attribution lost | Combine visible and steganographic watermarks; watermark placement varies per render |
| DLP telemetry itself becomes a sensitive data store | Ironic secondary exposure | DLP alerts store hashes and metadata, never the matched content |
| Over-blocking degrades product usability for legitimate bulk workflows (e.g. a real audit response requiring 500 documents) | Customer dissatisfaction, workaround behaviour | Approval workflow rather than hard block; make the legitimate path fast and well-documented |
| Focus on content inspection while an architectural path remains open | False assurance | Prioritise Layer 1; review exfiltration paths as part of every threat model |

## Trade-offs

- **Architectural elimination (highly effective, requires design discipline) vs. content-inspection products (fast to procure, high false positives, weak against encryption).** **Recommendation: invest in Layer 1 and Layer 3 first; buy content inspection only for the narrow endpoint use case.**
- **Hard blocking vs. alerting on threshold breach.** Hard-blocking a compliance officer mid-audit is a customer incident. **Recommendation: soft alert at 2× baseline, approval workflow at 3×, hard block only at 5× — and make the approval fast.**
- **Copy protection and disabled text selection (deters casual copying; user-hostile, trivially bypassed) vs. relying on watermarking.** **Recommendation: apply only to `RESTRICTED`/`PRIVILEGED`; accept it is a deterrent, not a control.**
- **Broad email/chat inspection (catches an exfiltration path; legally fraught in the EU, high false-positive volume, culturally corrosive) vs. narrow endpoint controls.** **Recommendation: skip broad inspection. Employees have no production data access, so the path is largely closed already.**
- **Steganographic watermarking (survives cropping and screenshots; implementation cost, and can be defeated) vs. visible only.** **Recommendation: visible watermarks at launch; add steganographic marking for `RESTRICTED`/`PRIVILEGED` in phase 2.**
- **Blocking paste into AI tools (prevents the highest-risk developer behaviour; some legitimate friction) vs. detect-and-warn.** **Recommendation: block for content matching customer-data patterns and log the attempt; warn for lower-confidence matches.**

## Design decisions

- **DD-23-01:** DLP strategy prioritises architectural elimination of exfiltration paths; content inspection is a backstop, not the primary control.
- **DD-23-02:** Per-role data-access baselines with graduated response: alert at 2×, approval required at 3×, hard block at 5×, per rolling hour.
- **DD-23-03:** Bulk export requires step-up authentication, a stated purpose, tenant-admin approval above threshold, watermarking, and customer notification.
- **DD-23-04:** Dynamic per-user watermarks on all previews and exports; steganographic marking for `RESTRICTED`/`PRIVILEGED` from phase 2.
- **DD-23-05:** All outbound integrations route through a single egress service enforcing destination allowlists, size limits, classification policy and full logging.
- **DD-23-06:** Endpoint DLP scoped narrowly to removable media, personal cloud sync, unmanaged browsers, and blocking paste of customer-data patterns into AI tooling. Broad email/chat content inspection is explicitly out of scope.
- **DD-23-07:** All employee monitoring is transparent, supported by a documented balancing test, and subject to works council consultation where required in each jurisdiction.
- **DD-23-08:** Amazon Macie scans object storage for misplaced sensitive data, including automated scanning of non-production accounts to enforce the synthetic-data-only rule.
- **DD-23-09:** DLP alert records store hashes and metadata only — never the matched content.
- **DD-23-10:** Automatic account suspension is limited to honeytoken access and confirmed cross-tenant access attempts; all other responses are graduated and human-approved.

## References

- Regulation (EU) 2016/679 (GDPR) Art. 5(1)(f), 25, 32, 33, 34
- Regulation (EU) 2022/2554 (DORA) Art. 9; Commission Delegated Regulation (EU) 2024/1774
- Directive (EU) 2022/2555 (NIS2) Art. 21(2)
- EDPB/WP29 Opinion 2/2017 on data processing at work
- ISO/IEC 27001:2022 Annex A 8.12 — Data leakage prevention
- MITRE ATT&CK — Exfiltration (TA0010), Collection (TA0009)
- Amazon Macie; AWS Network Firewall documentation

## Confidence level

**High** — the elimination-first strategy, application-layer rate limiting and export gating, watermarking, and the narrow endpoint scope. These are effective and proportionate for this architecture, and they avoid the well-documented failure modes of traditional DLP deployments.

**Medium** — the correct calibration of access baselines (must be derived from real usage after launch; initial thresholds will be wrong), and the extent of works council and employment-law constraints in each member state where staff are eventually employed.
