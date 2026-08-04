# Data Loss Prevention

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](../future-scope/future-and-optional-scope.md).

Data loss prevention has a poor reputation because it is usually deployed as a content-inspection product bolted onto an architecture that already permits exfiltration. The effective approach inverts this: **architectural controls that make exfiltration paths not exist, with content inspection as a detective backstop on the few paths that must remain open.**

Not named by the PRD. Everything here is **[PROPOSED]** unless marked, in service of NFR-01 and NFR-03.

## Best practices

- **Close paths before inspecting content.** Default-deny egress (`network-security`), no standing production access (`identity-and-access-management`), no production data in development (`cross-border-data-processing`) — each eliminates a channel entirely, which no content-inspection product can match.
- **Rate-limit and threshold everything that reads data.** Volume is the most reliable exfiltration signal and the cheapest to implement.
- **Watermark what leaves.** Per-user watermarks on previews and exports make a leaked document traceable to an individual — a deterrent and a forensic aid.
- **Classify first.** Data loss prevention without classification either blocks everything or nothing. The classification model in `document-confidentiality` is the input.
- **Accept that determined exfiltration cannot be fully prevented.** A photograph of a screen defeats every technical control. Optimise for making it slow, small-scale, detectable and attributable.
- **Measure false positives.** A control that blocks legitimate compliance work will be disabled, formally or informally — and blocking a compliance officer mid-test is a customer incident.

## Regulatory implications

- **GDPR Art. 32** — a security-of-processing measure; **Art. 5(1)(f)** confidentiality; **Art. 33/34** — an exfiltration event is a notifiable breach, and this telemetry determines whether the scope can be characterised in 72 hours.
- **GDPR Art. 25** — data protection by default: personal data should not be extractable beyond what the purpose requires.
- **Delegated Reg. (EU) 2024/1774** — measures to prevent data leakage and control data flows. *(Design reference.)*
- **NFR-03** — egress control is also a residency control: an unlogged outbound path is a potential route out of the EU boundary.
- **Employee monitoring constraint** — endpoint controls and content inspection process employee personal data. Lawful basis, transparency, proportionality, and in several member states consultation. Inspecting employee email or chat content is legally sensitive. Design accordingly rather than assuming. **[OPEN — LEGAL]**

## Recommended architecture

### Layer 1 — architectural elimination (highest value, do this first)

| Exfiltration path | How it is eliminated |
|---|---|
| Developer copies production data | No production data in development; no production credentials outside production (`cross-border-data-processing`) |
| Compromised service calls out to attacker infrastructure | Default-deny egress with a hostname allowlist; the data tier has no internet route (`network-security`) |
| Operator reads evidence plaintext | Zero standing access; no operator shell into production (`identity-and-access-management`, `insider-threat-protection`) |
| Database dumped via a direct connection | No public endpoint; identity-based authentication; access only from the application security group |
| Backup copied out | Backup account isolation; no cross-account read path (`secure-backups`) |
| Bulk API scraping | Per-user and per-firm rate limits; pagination caps; bulk export requires approval |
| Signed URL shared externally | Short TTL, single use (`document-confidentiality`) |
| Search index or extracted text exfiltrated | In-region, firm-key encrypted, no external access path |

**This layer does most of the work.** Everything below is a backstop.

### Layer 2 — egress inspection and control

- **Network egress:** domain-allowlisted egress firewall; every denied connection alerts (`network-security`). Volume anomaly detection on allowed destinations catches abuse of a legitimate channel.
- **Application egress:** all outbound integrations — report distribution email (FR-59), notification email (PRD §12), the inference call (FR-31), the Portal's regulatory feed fetches (SA-03) — go through a single egress service that enforces destination allowlists, applies size limits, logs the transfer with classification metadata, and applies content policy.

  **Report distribution deserves specific attention:** FR-59 automatically emails a signed-off report to configured distribution lists, and PRD §10.6 defines six lists including ones that fire on regulator requests. That is a legitimate, PRD-required outbound path carrying `CONFIDENTIAL` content. Recommendation: send a notification with an authenticated link rather than the report as an attachment, so the content stays inside the platform boundary and every access is logged under FR-13. **[PROPOSED — needs product agreement]** **[OPEN]**
- **DNS:** query logging and resolver firewall detect tunnelling (`network-security`).

### Layer 3 — application-layer controls (the highest-signal layer for this product)

Because the platform controls the application, enforcement can happen exactly where it belongs:

| Control | Implementation |
|---|---|
| **Access rate limits** | Per-role baselines; soft alert at a modest multiple, approval requirement above that, hard block at a high multiple, per rolling hour |
| **Bulk export gate** | Exports above a threshold require step-up authentication, a stated purpose and approval; always watermarked; always audited |
| **Download vs. preview** | Preview is the default; raw download is a distinct permission, logged and rate-limited separately (`document-confidentiality`) |
| **Watermarking** | User, firm, timestamp and document identifier rendered into every preview and exported PDF |
| **Copy deterrence in the viewer** | Disable text selection for `RESTRICTED` previews. Weak against a determined user; it stops casual copying and signals intent |
| **API pagination caps** | Hard maximum page size; cursor-based pagination; no unbounded list endpoints |
| **Screenshot deterrence** | Watermarks survive screenshots — the pragmatic answer, since prevention is not achievable in a browser |
| **Egress classification check** | Any outbound transfer of `RESTRICTED` content requires explicit policy allowance |

Steganographic watermarking is **[FUTURE]**.

### Layer 4 — endpoint controls (workforce)

Scoped narrowly and lawfully:

- **Managed devices only** for any access to client data (`zero-trust-architecture`).
- Block removable-media writes, personal cloud sync clients, and unmanaged browser profiles for work applications.
- **Clipboard and paste monitoring into AI coding tools** — specifically, blocking paste of content matching client-data patterns (`ai-governance`). **This is the highest-value endpoint control in this environment**, because it closes the one path by which a developer could move real customer content into a third-party tool.
- **Do not** deploy broad email or chat content inspection. It is legally sensitive, generates enormous false-positive volume, and is largely redundant given that engineers have no production data access in the first place.

### Layer 5 — data discovery

- Scheduled scanning of object storage for unexpected sensitive-data placement — for example personal data appearing in a bucket that should contain only logs or artefacts. This catches the *misconfiguration* class of data loss, which is where most real incidents originate.
- Automated scanning of non-production accounts for anything resembling production data — enforcing the synthetic-only rule (`cross-border-data-processing`) rather than merely stating it.

### Priority detections (feeding `security-monitoring`)

1. Canary record accessed.
2. A user exceeds their access baseline by a high multiple.
3. Bulk export requested outside normal hours.
4. Denied egress from a production workload.
5. First-time firm access by a workforce user.
6. Sensitive data found in an unexpected storage location.
7. Paste of client-data-pattern content into an AI tool.

Response is graduated: alert → step-up challenge → session termination → account suspension pending investigation. Automatic suspension is reserved for canary access and confirmed cross-firm attempts.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| False positives block legitimate compliance work | Customer impact during a firm's testing cycle; controls disabled under pressure | Baselines tuned from measured role behaviour; graduated response rather than immediate blocking; documented exception path |
| Determined insider photographs the screen | Undetectable exfiltration | Accepted as residual; watermarks aid attribution; limit what is displayed at once; rate-limit views |
| Endpoint controls deployed without a lawful basis or required consultation | Regulatory and employment-law exposure | Legal review; transparency notice; proportionality assessment; narrow scope |
| Exfiltration via an allowlisted destination | Slow leak through a legitimate channel | Per-destination volume anomaly detection; a single application egress service logging and classifying every transfer |
| Report content emailed as an attachment leaves the audited boundary | Confidential content outside FR-13's reach; a residency question if the mail path is not EU-only | Prefer authenticated links; EU-only mail infrastructure; resolve as a product decision |
| Watermarks cropped | Attribution lost | Vary placement per render; accept as partial |
| Detection telemetry itself becomes a sensitive store | Secondary exposure | Alerts store hashes and metadata, never matched content |
| Over-blocking degrades a legitimate bulk workflow — for example a genuine regulator request for hundreds of documents (PRD §10.6) | Customer dissatisfaction; workaround behaviour | Approval workflow rather than a hard block; make the legitimate path fast and documented |
| Content inspection prioritised while an architectural path remains open | False assurance | Prioritise Layer 1; review exfiltration paths in every threat model |

## Trade-offs

- **Architectural elimination vs. content-inspection products.** Recommendation: invest in Layers 1 and 3 first; buy content inspection only for the narrow endpoint use case. **[PROPOSED]**
- **Hard blocking vs. alerting on threshold breach.** Hard-blocking a compliance officer mid-test is a customer incident. Recommendation: soft alert, then an approval workflow, then a hard block only at a high multiple — and make the approval fast. **[PROPOSED]**
- **Copy deterrence vs. relying on watermarking.** Recommendation: apply only to `RESTRICTED`; treat it as a deterrent, not a control. **[PROPOSED]**
- **Broad email and chat inspection vs. narrow endpoint controls.** Recommendation: skip broad inspection — the path is largely closed already. **[PROPOSED]**
- **Blocking paste into AI tools vs. detect-and-warn.** Recommendation: block for content matching client-data patterns and log the attempt; warn for lower-confidence matches. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification |
|---|---|---|
| DD-23-01 | Strategy prioritises architectural elimination of exfiltration paths; content inspection is a backstop, not the primary control | **[PROPOSED]** |
| DD-23-02 | Per-role data-access baselines with graduated response: alert, then approval, then hard block, per rolling hour | **[PROPOSED]** |
| DD-23-03 | Bulk export requires step-up authentication, a stated purpose, approval above a threshold, watermarking, and an audit event | **[PROPOSED]** |
| DD-23-04 | Per-user watermarks on all previews and exports | **[PROPOSED]** |
| DD-23-05 | All outbound integrations route through a single egress service enforcing destination allowlists, size limits, classification policy and full logging | **[PROPOSED]** — supports NFR-03 |
| DD-23-06 | Report and alert distribution prefers an authenticated link over attaching confidential content to email | **[PROPOSED / OPEN]** — affects FR-59 |
| DD-23-07 | Endpoint controls scoped narrowly to removable media, personal cloud sync, unmanaged browsers, and blocking paste of client-data patterns into AI tooling. Broad email and chat inspection is out of scope | **[PROPOSED]** |
| DD-23-08 | All employee monitoring is transparent, supported by a documented balancing test, and subject to locally required consultation | **[PROPOSED / OPEN — LEGAL]** |
| DD-23-09 | Scheduled scanning of object storage for misplaced sensitive data, including non-production accounts to enforce the synthetic-only rule | **[PROPOSED]** |
| DD-23-10 | Detection records store hashes and metadata only — never matched content | **[PROPOSED]** |
| DD-23-11 | Automatic account suspension limited to canary access and confirmed cross-firm access attempts | **[PROPOSED]** |
| DD-23-12 | Steganographic watermarking | **[FUTURE]** |

## References

- Regulation (EU) 2016/679 (GDPR) Art. 5(1)(f), 25, 32, 33, 34
- Commission Delegated Regulation (EU) 2024/1774 — data and system security *(design reference)*
- EDPB/WP29 Opinion 2/2017 on data processing at work
- ISO/IEC 27001:2022 Annex A 8.12 — Data leakage prevention
- MITRE ATT&CK — Exfiltration (TA0010), Collection (TA0009)

## Confidence level

**High** — the elimination-first strategy, application-layer rate limiting and export gating, watermarking, and the narrow endpoint scope. These avoid the well-documented failure modes of traditional data-loss-prevention deployments.

**Medium** — the correct calibration of access baselines, which must be derived from real usage after launch; initial thresholds will be wrong.

**Open** — whether report distribution (FR-59) sends content or a link, and the employment-law constraints in each jurisdiction where staff are employed.
