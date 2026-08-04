# Threat Model

> **Baseline:** PRD v4.0. Applied model for the architecture in `reference-cloud-architecture`; methodology in `threat-modelling`. Scoring: Likelihood (L) and Impact (I) on 1–5; Risk = L × I. Residual assumes the `security-control-matrix` controls are implemented. Control IDs refer to `security-control-matrix`.

## 1. Assets

| ID | Asset | PRD anchor | Confidentiality | Integrity | Availability |
|---|---|---|---|---|---|
| AS-1 | Evidence files uploaded during tests and remediation | FR-24, FR-42, §2 | **Critical** | **Critical** | High |
| AS-2 | Test executions, results, findings, remediation records | §2, FR-27 | High | **Critical** | High |
| AS-3 | Generated compliance reports | FR-56, FR-61 | High | **Critical** | High |
| AS-4 | Audit log and notification log | FR-13, NFR-04, §2 | High | **Critical** | High |
| AS-5 | WSP manuals, versions and rule mappings | FR-30, FR-37 | High | **Critical** | Medium |
| AS-6 | Firm and staff records (qualifications, hardware, contact chain) | FR-63, FR-69, FR-70 | **Critical** | High | Medium |
| AS-7 | Encryption keys (per-firm, audit, evidence sealing) | NFR-02 | **Critical** | **Critical** | **Critical** |
| AS-8 | Regulatory content: Requirement IDs, test procedures, sampling library | SA-01, SA-02, SA-05, CC-03 | High | **Critical** | High — **the Client's core IP** |
| AS-9 | Platform source code, architecture and schemas | CC-03 | Medium | High | Medium — **owned 100% by the Client** |
| AS-10 | Backups | — | **Critical** | High | **Critical** |
| AS-11 | User credentials and sessions | FR-11, FR-12 | **Critical** | High | High |

## 2. Trust boundaries

| ID | Boundary | Crossing |
|---|---|---|
| TB-1 | Internet → edge | Untrusted user and attacker traffic |
| TB-2 | Edge → application | Authenticated but untrusted user input |
| TB-3 | Application → data stores | Firm-scoped queries |
| TB-4 | Application → key service | Key operations with encryption context |
| TB-5 | Application → AI inference | Prompts containing WSP content |
| TB-6 | Uploaded file → parser / OCR | **Attacker-controlled binary into a parser** |
| TB-7 | Non-EU location → EU production | Cross-border access, if any exists (`cross-border-data-processing`) |
| TB-8 | CI/CD → production | Deployment authority |
| TB-9 | Operator → firm data | Insider access |
| TB-10 | **Platform Admin Portal → firm data** | The SA-06/SA-08 boundary, **unresolved** |
| TB-11 | Platform → sub-processors | Data leaving platform control |
| TB-12 | **Firm A ↔ Firm B** | **The isolation boundary; NFR-01 requires it be impermeable** |

## 3. Threat actors

| Actor | Capability | Motivation | Primary targets |
|---|---|---|---|
| Financially motivated criminal group | High: ransomware, initial-access brokers, phishing | Extortion; resale of compliance and KYC-derived data | AS-1, AS-6, AS-10 |
| Competitor / commercial espionage | Medium | The regulatory test library is the Client's core IP | AS-8, AS-9 |
| Well-resourced state actor | Very high | Intelligence on EU crypto-asset flows; supply-chain access | AS-1, AS-6, AS-7, AS-9 |
| Malicious insider (delivery or Portal team) | High, legitimate access | Financial gain, coercion, grievance | AS-1, AS-4, AS-7, AS-8 |
| Compromised insider | High, unaware | Attacker-controlled | All |
| **Malicious firm user** | Medium | **Conceal a compliance failure**: fabricate or alter evidence, backdate a result, defeat two-person sign-off | AS-1, AS-2, AS-4, AS-5 |
| Opportunistic scanner | Low | Automated exploitation | AS-11, edge |
| Compromised supplier | High | Supply-chain foothold | AS-9, AS-10, all via deploy |

The firm-user threat deserves emphasis: this product's *purpose* is to produce a record a regulator will trust. A user who wants to hide a compliance failure is inside the trust boundary and is the reason FR-32, FR-44, FR-45, FR-27, FR-21b and FR-21c all exist.

## 4. Threat catalogue

### T-01 to T-08 — Cross-firm and access control

| ID | Threat | STRIDE | Boundary | L | I | Risk | Controls | Residual |
|---|---|---|---|---|---|---|---|---|
| T-01 | Application bug lets firm A read firm B's evidence | I | TB-12 | 3 | 5 | **15** | E-02, C-11, D-08, H-02 | 5 |
| T-02 | Cached or shared object (search index, extracted text, memoised result) leaks across firms | I | TB-12 | 3 | 5 | **15** | Per-firm index namespaces, firm key on index, cache keys include firm, cross-firm retrieval negative tests (E-06, C-11) | 5 |
| T-03 | Authorisation bypass via direct object reference | E, I | TB-2 | 3 | 5 | **15** | C-02, opaque identifiers, E-02, C-11 | 4 |
| T-04 | Credential stuffing against firm accounts | S | TB-1 | 4 | 3 | 12 | C-04 MFA, G-06 rate limits on authentication, breached-password checks | 4 |
| T-05 | Second factor subverted by SIM swap where SMS is used | S | TB-1 | 3 | 4 | 12 | C-05 — **unresolved**; recommendation is app-based or push MFA | 6 |
| T-06 | Session token theft via a script in a rendered document | S, I | TB-2, TB-6 | 3 | 4 | 12 | E-11 separate content origin, sandboxed policy, server-side rendering | 4 |
| T-07 | Privilege escalation through role drift or an over-broad firm-role mapping | E | TB-9 | 3 | 4 | 12 | C-01 fixed system roles, C-13 just-in-time privilege, K-09 | 4 |
| T-08 | **Portal team accesses firm evidence beyond the agreed boundary** | I | TB-10 | 3 | 4 | 12 | C-16 — **unresolved**; must be enforced in the authorisation layer once decided | 6 |

### T-09 to T-14 — Exfiltration and insider

| ID | Threat | STRIDE | Boundary | L | I | Risk | Controls | Residual |
|---|---|---|---|---|---|---|---|---|
| T-09 | Malicious insider bulk-exports firm evidence | I | TB-9 | 3 | 5 | **15** | B-07 zero standing access, K-11 rate limits, K-04 canaries, E-05 watermarking, K-10 | 5 |
| T-10 | Compromised operator workstation used to reach production | I, E | TB-9 | 3 | 5 | **15** | Device trust (`zero-trust-architecture`), B-08 location policy, C-13, endpoint detection, K-12 session recording | 5 |
| T-11 | Compromised service credential exfiltrates to attacker infrastructure | I | TB-3 | 3 | 5 | **15** | G-04 default-deny egress, G-02 no internet route from the data tier, workload identity, K-11 | 4 |
| T-12 | Person outside the EU/EEA reaches production personal data outside a sanctioned path | I | TB-7 | 3 | 4 | 12 | B-06 synthetic-only, B-07 break-glass, B-08 location policy — **depends on the unresolved delivery topology (B-09)** | 5 |
| T-13 | Firm document content pasted into a developer AI tool | I | TB-7, TB-11 | 3 | 4 | 12 | I-05 managed settings and paste blocking, B-06 synthetic-only, training | 4 |
| T-14 | Data exfiltrated through an allowlisted egress destination — for example report distribution email | I | TB-11 | 2 | 4 | 8 | Per-destination volume anomaly detection; single egress service with classification checks; DD-23-06 link-not-attachment | 4 |

### T-15 to T-21 — Record integrity (the product's core promise)

| ID | Threat | STRIDE | Boundary | L | I | Risk | Controls | Residual |
|---|---|---|---|---|---|---|---|---|
| T-15 | Insider alters or deletes audit entries or evidence to conceal an action | T, R | TB-9 | 2 | 5 | 10 | F-02 no delete path, F-12 write-once and write-only archive, D-11 key deletion blocked, K-09 separation of duties | 3 |
| T-16 | **Firm user fabricates or backdates evidence to satisfy a regulator** | T, R | TB-2 | 3 | 5 | **15** | F-01 creation-time audit with actor and device, I-02/two-person approvals, FR-45 recorder exclusion, F-04/F-05 immutability after sign-off | 5 |
| T-17 | Two-person sign-off defeated — one person operates two accounts, or the excluded party approves | S, T | TB-2 | 3 | 5 | **15** | Approver identity checks, policy-author and recorder exclusion enforced server-side (FR-32, FR-45), C-03 invitation-only accounts, C-12 step-up | 5 |
| T-18 | Sealing key compromised, enabling forged records | S, T | TB-4 | 2 | 5 | 10 | Sign-only non-exportable key, D-09 separation of duties, historical public keys retained | 4 |
| T-19 | Hash chain broken by an ingestion gap, indistinguishable from tampering | T | TB-3 | 3 | 3 | 9 | Single-writer sealer, monotonic sequence, gap detection, documented repair that itself produces a record | 4 |
| T-20 | Audit gap prevents scoping a breach within 72 hours | R | TB-3 | 3 | 4 | 12 | F-14 coverage tests, F-13 synchronous writes, pre-written scoping queries | 4 |
| T-21 | **Records destroyed before the six-year minimum** — by deletion, key destruction, misconfigured retention, or backup expiry | T, D | TB-3, TB-4 | 2 | 5 | 10 | E-07 no delete path, D-11 key deletion blocked during retention, F-15 retention service as the only source, J-03 off-domain copies, F-16 verification | 3 |

### T-22 to T-26 — AI-specific (WSP mapping path only)

| ID | Threat | ATLAS / OWASP | Boundary | L | I | Risk | Controls | Residual |
|---|---|---|---|---|---|---|---|---|
| T-22 | Prompt injection in an uploaded WSP steers the mapping — for example causing a genuine gap to be mapped as covered | LLM01 | TB-5, TB-6 | **4** | 4 | **16** | I-07 untrusted delimiting and schema constraints, injection-signature detection, I-08 span verification, **I-01 human confirmation and I-02 two-person approval** | 6 |
| T-23 | Prompt injection exfiltrates another document's content in the response | LLM01 | TB-5 | 2 | 5 | 10 | Minimal-span retrieval; per-request context scoped to one firm and one document; output schema; no tool access from the model | 4 |
| T-24 | Suggested mapping cites a WSP section that does not exist, and a reviewer accepts it | LLM09 | TB-5 | **4** | 3 | 12 | I-08 deterministic span verification (blocking), I-11 AI labelling, I-01/I-02 human review, I-03 accuracy bar | 4 |
| T-25 | Model or prompt change silently drops accuracy below the **85% PRD commitment** | T | TB-5 | 3 | 4 | 12 | I-09 evaluation harness as a promotion gate; model registry; rollback target | 4 |
| T-26 | Inference provider changes terms, region or retention | — | TB-11 | 2 | 4 | 8 | Contractual change notice; provider selection criteria; annual review — **provider not yet selected (I-12)** | 5 |

Note what is **not** on this list, because the PRD's design removes it: the model cannot produce a compliance conclusion, cannot decide a test result, cannot take a privileged action, and cannot finalise a mapping without a human and then two approvers.

### T-27 to T-32 — Infrastructure, supply chain and pipeline

| ID | Threat | STRIDE | Boundary | L | I | Risk | Controls | Residual |
|---|---|---|---|---|---|---|---|---|
| T-27 | Compromised pipeline deploys malicious code | T, E | TB-8 | 2 | 5 | 10 | H-06 federation with narrow trust, H-07 ephemeral runners, trust zoning, H-08 admission verification, digest reconciliation | 4 |
| T-28 | Compromised upstream dependency introduces a backdoor | T | TB-8 | 3 | 5 | **15** | H-10 pinning and cooldown, H-09 continuous re-evaluation, G-04 egress limits blast radius, runtime detection | 6 |
| T-29 | Parser, OCR or media-container exploit yields code execution | E | TB-6 | 3 | 4 | 12 | E-10 no credentials, no egress, ephemeral, separate account; memory-safe parsers; resource limits | 4 |
| T-30 | Ransomware encrypts production and attempts to destroy backups | D, T | TB-8, TB-9 | 3 | 5 | **15** | J-05 immutable retention lock, J-04 account isolation, F-12 write-once records, J-06 restore verification | 5 |
| T-31 | Cloud misconfiguration exposes a bucket or database publicly | I | TB-3 | 3 | 5 | **15** | Account-level public-access block, infrastructure-as-code-only changes, conformance rules, G-02/G-03 | 4 |
| T-32 | Malware uploaded as evidence and later downloaded by a firm user | T | TB-6 | 3 | 4 | 12 | E-09 quarantine-scan-promote, fail closed, multi-engine, rescan on signature update | 4 |

### T-33 to T-36 — Availability, key and regulatory

| ID | Threat | STRIDE | Boundary | L | I | Risk | Controls | Residual |
|---|---|---|---|---|---|---|---|---|
| T-33 | Key deletion or loss makes a firm's six-year records unreadable | D | TB-4 | 2 | 5 | 10 | D-11 deletion denied and blocked during retention, D-10 rotation retains prior versions, K-10 dual authorisation | 3 |
| T-34 | Denial of service during a firm's testing deadline or a regulator response window | D | TB-1 | 3 | 4 | 12 | G-06 edge protection and rate limits, autoscaling, J-08 degraded modes including evidence-only read | 5 |
| T-35 | Loss of the primary environment exceeds whatever recovery expectation is eventually set | D | TB-3 | 2 | 4 | 8 | J-03 off-domain record copies, J-06 restore verification — **recovery architecture unresolved (J-07)** | 5 |
| T-36 | Incident assessed late, so firms cannot meet their own regulatory clocks | — | — | 3 | 4 | 12 | K-05 assessment at triage, K-06 templates — **notification deadline unresolved** | 5 |

## 5. Top residual risks

| Rank | Threat | Residual | Why it stays elevated | Further action |
|---|---|---|---|---|
| 1 | **T-22 prompt injection steering a mapping** | 6 | No complete technical defence exists; adversarial documents evolve. Mitigated in depth by the PRD's own human-confirmation and two-approver rules | Adversarial testing of the mapping pipeline; conservative confidence thresholds; keep FR-31/FR-32 inviolate |
| 2 | **T-28 compromised dependency** | 6 | Upstream compromise is outside our control | Dependency reduction as a tracked objective; runtime behavioural detection; egress limits |
| 3 | **T-05 SIM-swap on an SMS second factor** | 6 | Depends on an **unresolved** decision (C-05) | Choose an app-based or push factor within the FR-11 wording |
| 4 | **T-08 Portal visibility of firm evidence** | 6 | Depends on an **unresolved** boundary (SA-06/SA-08) | Settle the boundary before the Portal data layer is built |
| 5 | T-01, T-02, T-03, T-09, T-10, T-16, T-17, T-30 | 5 | Catastrophic impact even at moderate likelihood | These are the standing test scenarios for the isolation matrix and for penetration testing |

## 6. Attack trees for the catastrophic scenarios

**AT-1 — Mass cross-firm disclosure (breaches NFR-01)**

```
Goal: read evidence belonging to many firms
├── Application authorisation flaw
│   ├── Missing firm predicate in a query      → blocked by row-level security + static-analysis rule
│   ├── Direct object reference on an endpoint → blocked by per-request authorisation
│   └── Bug in a background or report job      → blocked by row-level security; jobs run with firm context
├── Database compromise
│   ├── Credential theft                       → identity authentication, no passwords, no public endpoint
│   └── Injection                              → parameterised queries, static analysis, WAF
├── Storage compromise
│   ├── Over-broad grant                       → blocked by the per-firm key encryption context
│   └── Public bucket misconfiguration         → account-level public-access block, conformance rules
└── Key compromise
    └── One key for all firms                  → eliminated by the NFR-02 per-firm key design
```

Every leaf requires defeating at least two independent layers. That is the intended property.

**AT-2 — Record tampering (breaches NFR-04 / NFR-07).** Requires simultaneously defeating write-once retention (not possible for any principal within the retention period), the hash chain (detectable), and the key-deletion block. **The practical residual is concentrated on records created fraudulently at the outset (T-16, T-17), not on alteration afterwards** — which is why the creation-time approval workflow and the exclusion rules matter as much as the storage immutability.

**AT-3 — Mass exfiltration by an insider.** Requires standing access (removed), rate-limit evasion (slow exfiltration, partially detectable by cumulative baselines), and avoiding canary records (unlikely at scale). Residual concentrated in slow, small-volume exfiltration by a patient insider.

**AT-4 — Ransomware with backup destruction.** Requires compromising production, then the backup account (no trust path), then defeating the immutable retention lock (not possible before expiry). Residual concentrated on recovery *time*, not on data loss — and recovery time is unresolved (J-07).

## 7. Threat-to-test traceability (excerpt)

| Threat | Tests | Detection |
|---|---|---|
| T-01 | `test_cross_firm_evidence_read_denied`, `test_rls_blocks_cross_firm_select`, `test_decrypt_wrong_encryption_context_fails` | Cross-firm access attempt alert |
| T-09 | `test_export_requires_approval_above_threshold`, `test_rate_limit_hard_block` | Canary access; volume anomaly |
| T-16 | `test_evidence_creation_records_actor_and_device`, `test_signed_off_result_cannot_be_modified` | Protected-record modification attempt |
| T-17 | `test_mapping_confirmation_requires_two_distinct_approvers`, `test_policy_author_cannot_approve`, `test_finding_recorder_cannot_close` | Approval-anomaly alert |
| T-21 | `test_evidence_delete_api_absent`, `test_key_deletion_blocked_during_retention`, `test_retention_cannot_be_shortened` | Retention-modification attempt |
| T-22 | `test_injection_corpus_does_not_alter_output_schema`, `test_delimited_untrusted_block` | Injection signature |
| T-24 | `test_cited_span_offsets_verified_against_source`, `test_invalid_citation_blocks_suggestion` | Span-verification failure rate |
| T-31 | `test_bucket_policy_denies_public`, infrastructure scan rules | Configuration drift alert |

Full traceability is maintained in the repository alongside the code; the proportion of mitigated threats with linked tests and detections is a reported metric (DD-24-04).

## 8. Privacy threats (feeding the data protection impact assessment)

| Category | Threat | Mitigation |
|---|---|---|
| **Linking** | Blind index frequency analysis links records within a firm | Per-firm index keys; limited field set; documented residual leakage |
| **Identifying** | Extracted text and any embeddings enable reidentification | Classified and protected as the source document; firm-key encrypted |
| **Non-repudiation** | The audit trail exposes an individual's actions beyond what is necessary | Minimised audit fields; documented retention; note the tension with FR-13, which *requires* full attribution — the PRD prioritises accountability here |
| **Detecting** | Existence of a record inferable from timing or error differences | Uniform error responses; constant-time authorisation failure paths |
| **Data disclosure** | Special-category data inside evidence uploads over-exposed | Classification, `RESTRICTED` handling, step-up access, watermarking |
| **Unawareness** | Data subjects unaware that WSP content is AI-processed | AI labelling; the controller firm's own transparency obligations supported by platform documentation |
| **Non-compliance** | Retention and erasure conflict resolved ad hoc | Escalated as an open legal question (`regulatory-obligations`, `immutable-evidence-retention`) rather than resolved unilaterally |

## 9. Review cadence

- **Per change:** enforced in CI for qualifying paths (`threat-modelling`).
- **Per feature:** design-time workshop for personal-data flows.
- **Periodic:** full refresh of this document, with likelihood re-scored against real incident data.
- **Event-driven:** after any top-severity incident, any major architectural change, and on resolution of any of the open questions that currently inflate residual risk — notably C-05, C-15, C-16, I-12, B-09 and J-07.
