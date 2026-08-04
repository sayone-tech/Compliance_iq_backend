# 32 — Threat Model

Applied model for the platform described in doc 30. Methodology in doc 24. Scoring: Likelihood (L) and Impact (I) on 1–5; Risk = L × I. Residual risk assumes the stated controls are implemented.

## 1. Assets

| ID | Asset | Confidentiality | Integrity | Availability |
|---|---|---|---|---|
| AS-1 | Customer uploaded documents (KYC, board minutes, custody attestations) | **Critical** | High | High |
| AS-2 | Immutable audit evidence and compliance reports | High | **Critical** | High |
| AS-3 | Customer records (personal data, incl. special-category) | **Critical** | High | Medium |
| AS-4 | AI-generated assessments | High | **Critical** | Medium |
| AS-5 | Encryption keys (tenant CMKs, evidence signing key) | **Critical** | **Critical** | **Critical** |
| AS-6 | Audit logs | High | **Critical** | High |
| AS-7 | Platform source code and IaC | Medium | High | Medium |
| AS-8 | Backups | **Critical** | High | **Critical** |
| AS-9 | Customer credentials and session tokens | **Critical** | High | High |
| AS-10 | Tenant configuration (including key tier) | Medium | **Critical** | High |

## 2. Trust boundaries

| ID | Boundary | Crossing |
|---|---|---|
| TB-1 | Internet → edge (CloudFront/WAF/ALB) | Untrusted user and attacker traffic |
| TB-2 | Edge → application | Authenticated but untrusted user input |
| TB-3 | Application → data stores | Tenant-scoped queries |
| TB-4 | Application → KMS | Key operations with encryption context |
| TB-5 | Application → Bedrock | Prompts containing customer content |
| TB-6 | Uploaded file → parser | **Attacker-controlled binary into a parser** |
| TB-7 | India (Zone D) → EU production (Zone P) | Cross-border, break-glass only |
| TB-8 | CI/CD → production | Deployment authority |
| TB-9 | Operator → tenant data | Insider access |
| TB-10 | Customer IdP → platform | Federated assertions |
| TB-11 | Platform → sub-processors | Data leaving our control |
| TB-12 | Tenant A ↔ Tenant B | **The isolation boundary; must be impermeable** |

## 3. Threat actors

| Actor | Capability | Motivation | Primary targets |
|---|---|---|---|
| **Financially-motivated criminal group** | High; ransomware, initial-access brokers, phishing | Extortion, resale of compliance/KYC data | AS-1, AS-3, AS-8 |
| **Competitor / commercial espionage** | Medium | Customer lists, deal intelligence, regulatory findings | AS-1, AS-2 |
| **Nation-state** | Very high | Intelligence on EU crypto-asset flows; supply-chain access | AS-1, AS-3, AS-5, AS-7 |
| **Malicious insider** | High (legitimate access) | Financial gain, coercion, grievance | AS-1, AS-2, AS-5, AS-6 |
| **Compromised insider** | High (unaware) | N/A — attacker-controlled | All |
| **Malicious tenant user** | Medium | Cross-tenant access, evidence manipulation to conceal a compliance failure | AS-1, AS-2, AS-4 |
| **Opportunistic scanner / bot** | Low | Automated exploitation | AS-9, edge |
| **Compromised supplier** | High | Supply-chain foothold | AS-7, AS-8, all via deploy |

Note the crypto-sector specific elevation: customers handle high-value digital assets, making their compliance data and any credential material adjacent to it a target for well-funded actors. Assume nation-state and organised-crime interest, not just opportunistic scanning.

## 4. Threat catalogue

### T-01 to T-08 — Cross-tenant and access control

| ID | Threat | STRIDE | Boundary | L | I | Risk | Controls | Residual |
|---|---|---|---|---|---|---|---|---|
| T-01 | Application bug allows tenant A to read tenant B's documents | I | TB-12 | 3 | 5 | **15** | E-02 four-layer isolation; C-04 test matrix; D-06 encryption context; H-02 SAST tenancy rule | 5 |
| T-02 | Cached or shared object (search index, embedding, memoised result) leaks across tenants | I | TB-12 | 3 | 5 | **15** | Per-tenant index namespaces; tenant key on index; cache keys include tenant; cross-tenant retrieval negative tests | 5 |
| T-03 | Authorisation bypass via direct object reference / IDOR | E, I | TB-2 | 3 | 5 | **15** | C-03 per-request Cedar; opaque ULIDs; E-02; C-04 | 4 |
| T-04 | Customer IdP misconfiguration (unsigned assertions, open registration) grants unauthorised tenant access | S | TB-10 | 2 | 5 | 10 | Assertion signing and audience restriction enforced; onboarding validation; periodic re-validation | 4 |
| T-05 | Session token theft via XSS in a rendered document | S, I | TB-2, TB-6 | 3 | 4 | 12 | E-10 separate content origin, CSP sandbox, nosniff; server-side rendering default | 4 |
| T-06 | Privilege escalation through an over-broad role or permission drift | E | TB-9 | 3 | 4 | 12 | C-02 zero standing privilege; C-09 recertification; K-09 capability matrix; IAM Access Analyzer | 4 |
| T-07 | Credential stuffing / password spraying on customer accounts | S | TB-1 | 4 | 3 | 12 | C-01/C-06 SSO + FIDO2; WAF rate limits on auth endpoints; breached-password checks | 4 |
| T-08 | MFA bypass via help-desk social engineering | S | TB-10 | 3 | 4 | 12 | Help-desk verification procedure with manager callback; FIDO2 for privileged; recovery-flow hardening | 6 |

### T-09 to T-15 — Data exfiltration and insider

| ID | Threat | STRIDE | Boundary | L | I | Risk | Controls | Residual |
|---|---|---|---|---|---|---|---|---|
| T-09 | Malicious insider bulk-exports customer documents | I | TB-9 | 3 | 5 | **15** | B-07 zero standing access; D-13 enclave decryption; K-11 rate limits; K-04 honeytokens; E-04 watermarking; K-12 tenant visibility | 5 |
| T-10 | Compromised operator workstation used to access production | I, E | TB-9 | 3 | 5 | **15** | Device trust (doc 12); B-08 EU session policy; FIDO2; EDR; JIT elevation; session recording | 5 |
| T-11 | Compromised service credential used to exfiltrate to attacker infrastructure | I | TB-3 | 3 | 5 | **15** | G-04 default-deny egress; G-02 no internet route from data tier; workload identity; K-11 volume detection | 4 |
| T-12 | India-based engineer accesses EU production personal data outside the sanctioned path | I | TB-7 | 3 | 4 | 12 | B-06 synthetic-only; B-07 break-glass with EU approval; B-08 geo policy; VDI with egress disabled; DLP | 4 |
| T-13 | Customer document content pasted into developer AI tooling | I | TB-7, TB-11 | 3 | 4 | 12 | I-01 managed settings; I-02 paste blocking; synthetic-only Zone D; training | 4 |
| T-14 | Data exfiltrated through an allowlisted egress destination | I | TB-11 | 2 | 4 | 8 | Per-destination volume anomaly detection; single application egress service with classification checks | 4 |
| T-15 | Backup copied out of the environment | I | TB-9 | 2 | 5 | 10 | J-03 backup account isolation; no cross-account read; restore requires dual approval and lands in controlled environment | 4 |

### T-16 to T-21 — Evidence and integrity

| ID | Threat | STRIDE | Boundary | L | I | Risk | Controls | Residual |
|---|---|---|---|---|---|---|---|---|
| T-16 | Insider alters or deletes evidence to conceal an action | T, R | TB-9 | 2 | 5 | 10 | F-04 Object Lock COMPLIANCE; write-only log-archive; F-08 hash chain; F-07 qualified timestamps; K-09 separation of duties | 3 |
| T-17 | Tenant user backdates or fabricates an evidence record to satisfy a regulator | T, R | TB-2 | 3 | 5 | **15** | F-07 QTSP timestamp binds creation time; approval workflow with named reviewer; F-08 chain; immutable audit of creation | 4 |
| T-18 | Evidence signing key compromised, enabling forged records | S, T | TB-4 | 2 | 5 | 10 | KMS sign-only non-exportable key; D-07 separation of duties; timestamp binds signatures to pre-compromise time; key history published | 4 |
| T-19 | Hash chain broken by an ingestion gap, indistinguishable from tampering | T | TB-3 | 3 | 3 | 9 | Single-writer sealer with monotonic sequence; idempotent retries; gap detection; documented repair producing its own evidence | 4 |
| T-20 | Audit log gap prevents breach scoping within 72 hours | R | TB-3 | 3 | 4 | 12 | F-06 coverage tests; F-05 synchronous writes for high-value actions; pre-written scoping queries tested against synthetic incidents | 4 |
| T-21 | Retention policy misconfiguration destroys records before the legal minimum | T | TB-3 | 2 | 5 | 10 | F-09 policy engine as single source; Object Lock prevents early deletion; F-10 expiry job evidence; quarterly conformance report | 3 |

### T-22 to T-27 — AI-specific

| ID | Threat | STRIDE / ATLAS | Boundary | L | I | Risk | Controls | Residual |
|---|---|---|---|---|---|---|---|---|
| T-22 | Prompt injection in an uploaded document steers the assessment to a false conclusion | T (LLM01) | TB-5, TB-6 | **4** | 4 | **16** | I-04 untrusted-data delimiting + schema-constrained output; injection-signature detection; I-05 citation verification; I-06 human approval | 6 |
| T-23 | Prompt injection causes exfiltration of another document's content in the response | I (LLM01) | TB-5 | 3 | 5 | **15** | Minimal-span retrieval; per-request context scoped to one tenant and one task; output schema; no tool access from the model | 5 |
| T-24 | Hallucinated regulatory citation reaches a customer's audit file | T (LLM09) | TB-5 | **4** | 4 | **16** | I-05 deterministic citation-offset verification (blocking); confidence thresholds; I-06 human approval; I-10 AI labelling | 5 |
| T-25 | Model output triggers a privileged action (excessive agency) | E (LLM06) | TB-5 | 2 | 5 | 10 | Output is data only; no tool/function access to privileged operations; deterministic validation before any action | 3 |
| T-26 | Model or prompt change silently degrades assessment quality | T | TB-5 | 3 | 4 | 12 | I-07 model registry + golden-set evaluation gate; prompt versioning; rollback target | 4 |
| T-27 | Inference provider changes terms/region/retention | — | TB-11 | 2 | 4 | 8 | Contractual change-notice; I-09 fallback provider; annual review | 4 |

### T-28 to T-33 — Infrastructure, supply chain and pipeline

| ID | Threat | STRIDE | Boundary | L | I | Risk | Controls | Residual |
|---|---|---|---|---|---|---|---|---|
| T-28 | Compromised CI/CD deploys malicious code to production | T, E | TB-8 | 2 | 5 | 10 | H-06 OIDC with narrow trust; H-07 ephemeral runners; trust zoning; H-09 admission verification; H-13 GitOps; digest reconciliation | 4 |
| T-29 | Compromised upstream dependency introduces a backdoor | T | TB-8 | 3 | 5 | **15** | H-11 pinning + 3-day cooldown + private registry; H-10 SBOM continuous re-eval; G-04 egress limits exfiltration; runtime detection | 6 |
| T-30 | Parser exploit in document processing yields RCE | E | TB-6 | 3 | 4 | 12 | E-09 no credentials, no egress, ephemeral, separate account; memory-safe parsers; resource limits | 4 |
| T-31 | Ransomware encrypts production and attempts to destroy backups | D, T | TB-8, TB-9 | 3 | 5 | **15** | J-04 Vault Lock compliance; J-03 account isolation; F-04 Object Lock; J-05 daily restore verification; J-06 DR testing | 5 |
| T-32 | Cloud misconfiguration exposes a bucket or database publicly | I | TB-3 | 3 | 5 | **15** | Account-level Block Public Access; IaC-only changes; Config rules; G-02/G-03; continuous conformance scanning | 4 |
| T-33 | Malware uploaded and later distributed to customers | T | TB-6 | 3 | 4 | 12 | E-08 quarantine-scan-promote, fail closed, multi-engine; 7-day rescan on signature update | 4 |

### T-34 to T-38 — Availability, key and regulatory

| ID | Threat | STRIDE | Boundary | L | I | Risk | Controls | Residual |
|---|---|---|---|---|---|---|---|---|
| T-34 | Accidental or malicious key deletion destroys tenant data permanently | D | TB-4 | 2 | 5 | 10 | D-09 30-day window, dual approval, alerting; deletion denied for audit/evidence keys; K-10 dual authorisation | 4 |
| T-35 | Customer-managed key (T2/T3) becomes unavailable | D | TB-4 | 3 | 4 | 12 | D-11 canary monitoring; contractual HA obligations; key-degraded mode; SLA carve-out; documented acknowledgement | 6 |
| T-36 | DDoS renders the platform unavailable during a customer's regulatory deadline | D | TB-1 | 3 | 4 | 12 | G-06 CloudFront + WAF + Shield; autoscaling; J-08 degraded modes incl. evidence-only read path | 5 |
| T-37 | Regional outage exceeds RTO | D | TB-3 | 2 | 4 | 8 | J-02 warm standby; J-06 tested failover; J-10 parity checks | 4 |
| T-38 | Incident misclassified or reported late, breaching DORA/NIS2/GDPR deadlines | — | — | 3 | 4 | 12 | K-05 classification engine at triage; K-06 2-hour customer SLA; timers with escalation at 50% of deadline; annual drill | 4 |

## 5. Top risks after mitigation (residual ≥5)

| Rank | Threat | Residual | Why it stays elevated | Further action |
|---|---|---|---|---|
| 1 | **T-22 Prompt injection steering assessments** | 6 | No complete technical defence exists; adversarial documents evolve | Continuous red-teaming of the assessment pipeline; injection-detection model; conservative confidence thresholds; keep human approval mandatory |
| 2 | **T-29 Compromised dependency** | 6 | Upstream compromise is outside our control | Dependency reduction as a tracked objective; runtime behavioural detection; egress limits blast radius |
| 3 | **T-35 Customer key unavailability** | 6 | Risk transferred to the customer by design | Contractual HA requirements; onboarding readiness assessment; consider mandating a minimum key-availability architecture for T3 |
| 4 | **T-08 MFA bypass via help desk** | 6 | Human process is the weak link | Formal identity-proofing procedure; consider removing help-desk reset authority entirely for privileged accounts |
| 5 | T-01/T-02/T-09/T-10/T-23/T-31 | 5 | Catastrophic impact even at low likelihood | Quarterly purple-team validation of each; these are the standing test scenarios |

## 6. Attack trees for the four catastrophic scenarios

**AT-1 — Mass cross-tenant document disclosure**
```
Goal: read documents belonging to many tenants
├── Application authorisation flaw
│   ├── Missing tenant predicate in a query        → blocked by RLS (layer 2) + SAST rule
│   ├── IDOR on document endpoint                  → blocked by Cedar per-request authz
│   └── Bug in a background/batch job              → blocked by RLS; jobs run with tenant context
├── Database compromise
│   ├── Credential theft                           → IAM auth, no passwords, no public endpoint
│   └── SQL injection                              → parameterised queries, SAST, WAF
├── Storage compromise
│   ├── Over-broad IAM grant                       → blocked by KMS encryption context per tenant
│   └── Public bucket misconfiguration             → account-level Block Public Access, Config rules
└── Key compromise
    └── Single key for all tenants                 → eliminated by per-tenant CMK design
```
Every leaf requires defeating at least two independent layers. This is the intended property.

**AT-2 — Evidence tampering** — requires simultaneously defeating Object Lock COMPLIANCE (impossible for any principal within the retention period), the hash chain (detectable), and the QTSP timestamp (requires compromising an independent trusted third party). Practical residual risk is concentrated on *evidence created fraudulently at the outset* (T-17), not on alteration afterwards — which is why the creation-time approval workflow matters as much as the storage immutability.

**AT-3 — Mass exfiltration by insider** — requires standing access (removed), enclave bypass (phase 2), rate-limit evasion (slow exfiltration, partially detectable by cumulative baselines), and avoiding honeytokens (probabilistically unlikely at scale). Residual concentrated in slow, small-volume exfiltration by a patient insider.

**AT-4 — Ransomware with backup destruction** — requires compromising production, then the backup account (no trust path), then defeating Vault Lock compliance mode (not possible before retention expiry). Residual concentrated on the recovery *time*, not on data loss.

## 7. Threat-to-test traceability (excerpt)

| Threat | Tests | Detection |
|---|---|---|
| T-01 | `test_cross_tenant_document_read_denied`, `test_rls_blocks_cross_tenant_select`, `test_kms_decrypt_wrong_context_fails` | DET-02 cross-tenant attempt |
| T-09 | `test_export_requires_approval_above_threshold`, `test_rate_limit_hard_block` | DET-01 honeytoken, DET-03 volume anomaly |
| T-22 | `test_injection_corpus_does_not_alter_output_schema`, `test_delimited_untrusted_block` | DET-11 injection signature |
| T-24 | `test_citation_offsets_verified_against_source`, `test_invalid_citation_blocks_assessment` | DET-12 citation-failure-rate spike |
| T-32 | `test_bucket_policy_denies_public`, IaC scan rules | DET-06 config-drift alert |

Full traceability maintained in the repository alongside the code; the ratio of mitigated threats with linked tests and detections is a reported metric (DD-24-04).

## 8. Privacy threats (LINDDUN summary, feeding the DPIA)

| LINDDUN category | Threat | Mitigation |
|---|---|---|
| **Linking** | Blind index frequency analysis links records across a tenant | Per-tenant index keys; limited field set; documented residual leakage |
| **Identifying** | Embeddings enable reidentification of pseudonymised content | Embeddings classified and protected as personal data; tenant-key encrypted |
| **Non-repudiation** | Audit trail could expose an individual's actions beyond what is necessary | Minimised audit fields; documented retention; actor pseudonymisation where feasible |
| **Detecting** | Existence of a record inferable from timing or error differences | Uniform error responses; constant-time authorisation failure paths for document existence |
| **Data disclosure** | Special-category data in KYC documents over-exposed | Classification, redacted derivatives, minimisation policy, `PRIVILEGED` exclusion from AI |
| **Unawareness** | Data subjects unaware their documents are AI-processed | AI labelling; controller (customer) transparency obligations supported by our documentation |
| **Non-compliance** | Retention conflicts between MiCA and GDPR resolved ad hoc | Retention policy engine with documented legal basis per class |

## 9. Review cadence

- **Per-change (T1):** CI-enforced for qualifying paths.
- **Per-feature (T2):** design-time workshop; DPO participates for personal-data flows.
- **Annual (T3):** full refresh of this document; likelihood re-scored against incident and threat-intelligence data; purple-team results incorporated.
- **Event-driven:** after any P1 incident, any major architectural change, and on publication of relevant new regulatory guidance.
