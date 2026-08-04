# Security Control Matrix

> **Baseline:** PRD v4.0. Every control below carries a **classification** and, where it exists, the **PRD anchor** that requires or motivates it.

**Classification:** **[PRD]** required by the PRD · **[PROP]** implementation recommendation, not selected by the PRD · **[OPEN]** stakeholder or legal decision required · items outside the MVP baseline are **not listed here** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

**Phase:** 1 = before real client data · 2 = post-launch hardening. **Priority:** M = mandatory before client data · H = high · S = standard.

---

## A. Governance and regulatory

| ID | Control | Class | PRD anchor / driver | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| A-01 | GDPR processor obligations implemented; Data Processing Agreement in place | **[PRD]** | NFR-06 | Signed DPA | 1 | M | [regulatory-obligations](regulatory-obligations.md) |
| A-02 | Records of processing maintained | **[PROP]** | GDPR Art. 30 | Register | 1 | M | [regulatory-obligations](regulatory-obligations.md) |
| A-03 | Data protection impact assessment covering evidence storage and AI-assisted WSP mapping | **[PROP]** | GDPR Art. 35; FR-31 | Assessment document | 1 | H | [ai-governance](ai-governance.md), [threat-modelling](supporting-topics/threat-modelling.md) |
| A-04 | Obligation register maintained as versioned configuration, traced to PRD requirement IDs | **[PROP]** | — | Register + review records | 1 | H | [regulatory-obligations](regulatory-obligations.md) |
| A-05 | Sub-processor register maintained and disclosed | **[PROP]** | GDPR Art. 28 | Register + change notices | 1 | M | [data-residency](data-residency.md), [supply-chain-security](supply-chain-security.md) |
| A-06 | Named owner accountable for platform security | **[OPEN]** | not staffed by the PRD | — | 1 | H | [regulatory-obligations](regulatory-obligations.md) |
| A-07 | ISO 27001 and SOC 2 Type II placed on the roadmap; **no delivery date assumed** | **[PRD]** | NFR-09, TI-03 | Roadmap entry | 2 | S | [regulatory-obligations](regulatory-obligations.md), [security-roadmap](security-roadmap.md) |
| A-08 | NIS2 / AI Act / CRA applicability determined by counsel before any commitment | **[OPEN — LEGAL]** | — | Written opinions | 1 | H | [regulatory-obligations](regulatory-obligations.md) |
| A-09 | Coordinated vulnerability disclosure policy, subject to Client approval (CC-03) | **[PROP / OPEN]** | CC-03 | Policy | 2 | S | [secure-sdlc](secure-sdlc.md) |

## B. Data residency

| ID | Control | Class | PRD anchor / driver | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| B-01 | All client data stored in EU data centres | **[PRD]** | NFR-03 | Region configuration | 1 | M | [data-residency](data-residency.md) |
| B-02 | AWS, EU data centre, account owned solely by the Client | **[PRD]** | TI-01 | Account ownership record | 1 | M | [data-residency](data-residency.md), [reference-cloud-architecture](reference-cloud-architecture.md) |
| B-03 | EU-only region enforcement by organisation and resource policies; CI fails on non-approved regions | **[PROP]** | implements NFR-03 | Policy configuration, CI logs | 1 | M | [data-residency](data-residency.md) |
| B-04 | Observability, error tracking, email, support tooling and CI subject to the same residency review, each with a named EU implementation | **[PROP]** | implements NFR-03 | Component inventory | 1 | M | [data-residency](data-residency.md) |
| B-05 | Extracted text, OCR output, indexes and any embeddings classified and protected as the source document | **[PROP]** | implements NFR-01, NFR-03 | Data map | 1 | M | [data-residency](data-residency.md), [document-confidentiality](document-confidentiality.md) |
| B-06 | Synthetic data only in development and pre-production | **[PROP]** | implements NFR-01, NFR-03 | Scan results | 1 | M | [cross-border-data-processing](supporting-topics/cross-border-data-processing.md) |
| B-07 | Zero standing human access to production; break-glass dual-approved, recorded, time-boxed | **[PROP]** | supports NFR-04, FR-13 | Access logs, approvals | 1 | M | [cross-border-data-processing](supporting-topics/cross-border-data-processing.md), [identity-and-access-management](identity-and-access-management.md) |
| B-08 | Location policy for production access | **[PROP]** | supports NFR-03 | Policy + denial logs | 1 | H | [cross-border-data-processing](supporting-topics/cross-border-data-processing.md), [zero-trust-architecture](supporting-topics/zero-trust-architecture.md) |
| B-09 | Delivery topology (where development, support and administration occur) determined and, if any is non-EU, transfer tooling executed | **[OPEN — LEGAL]** | PRD silent | Signed transfer agreement, impact assessment | 1 | M | [cross-border-data-processing](supporting-topics/cross-border-data-processing.md) |
| B-10 | Region selection recorded as a decision against documented criteria | **[OPEN]** | PRD silent | Decision record | 1 | M | [data-residency](data-residency.md) |

## C. Identity and access

| ID | Control | Class | PRD anchor / driver | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| C-01 | Eight fixed system roles; firm-created role names map to exactly one system role | **[PRD]** | §3, §3.1, §3.2 | Role configuration | 1 | M | [identity-and-access-management](identity-and-access-management.md) |
| C-02 | Role-based access enforced automatically on every request | **[PRD]** | FR-09 | Policy repository, decision logs | 1 | M | [identity-and-access-management](identity-and-access-management.md) |
| C-03 | Invitation-only account creation; role assigned before any access | **[PRD]** | FR-12 | Invitation records | 1 | M | [identity-and-access-management](identity-and-access-management.md) |
| C-04 | Email + password + phone-based second factor for every user | **[PRD]** | FR-11 | Authentication configuration | 1 | M | [identity-and-access-management](identity-and-access-management.md) |
| C-05 | Concrete second-factor mechanism (app/push preferred over SMS) | **[OPEN]** | FR-11 silent | Decision record | 1 | M | [identity-and-access-management](identity-and-access-management.md) |
| C-06 | Users deactivated, never deleted; all history retained; work reassignment documented with reasoning in the immutable audit trail | **[PRD]** | FR-14 | Deactivation records | 1 | M | [identity-and-access-management](identity-and-access-management.md), [immutable-evidence-retention](immutable-evidence-retention.md) |
| C-07 | Minimum two Firm Super Admins enforced with a warning at one | **[PRD]** | FR-15 | Enforcement test | 1 | M | [identity-and-access-management](identity-and-access-management.md) |
| C-08 | Platform Admin Portal on a separate login and interface, invisible to firm users | **[PRD]** | §4 | Access test | 1 | M | [identity-and-access-management](identity-and-access-management.md), [reference-cloud-architecture](reference-cloud-architecture.md) |
| C-09 | Only the CCO can assign a test to a Lead Tester | **[PRD]** | FR-20 | Authorisation tests | 1 | M | [identity-and-access-management](identity-and-access-management.md) |
| C-10 | In-progress test visibility: assigned users contribute with versioned attribution; others view-only, and only with the right entitlements | **[PRD]** | GAP-05 | Authorisation tests | 1 | H | [identity-and-access-management](identity-and-access-management.md) |
| C-11 | Cross-firm negative test matrix (every system role × every action) as a blocking CI gate | **[PROP]** | implements NFR-01 | CI results | 1 | M | [document-confidentiality](document-confidentiality.md), [identity-and-access-management](identity-and-access-management.md) |
| C-12 | Step-up authentication for export, role change, mapping confirmation, finding closure and report generation | **[PROP]** | supports FR-32, FR-44, FR-55 | Authentication events | 1 | H | [identity-and-access-management](identity-and-access-management.md) |
| C-13 | Workforce identity plane with phishing-resistant MFA, conditional access and just-in-time privilege | **[PROP]** | — | Identity configuration | 1 | M | [identity-and-access-management](identity-and-access-management.md) |
| C-14 | Two-person break-glass with split knowledge and offline factors; root custody agreed with the Client | **[PROP / OPEN]** | TI-01 | Test records, use alerts | 1 | M | [identity-and-access-management](identity-and-access-management.md) |
| C-15 | Remediation Owner visibility scope | **[OPEN]** | FR-52 vs GAP-07 | Decision record | 1 | M | [identity-and-access-management](identity-and-access-management.md) |
| C-16 | Platform Admin Portal visibility of firm data | **[OPEN]** | SA-06, SA-08 | Decision record | 1 | M | [document-confidentiality](document-confidentiality.md), [identity-and-access-management](identity-and-access-management.md) |

## D. Cryptography and keys

| ID | Control | Class | PRD anchor / driver | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| D-01 | AES-256 encryption at rest for all client data | **[PRD]** | NFR-02, §2 | Configuration, scan | 1 | M | [encryption-architecture](encryption-architecture.md) |
| D-02 | TLS 1.3 for traffic between the platform and browsers | **[PRD]** | NFR-02 | Endpoint scan | 1 | M | [encryption-architecture](encryption-architecture.md) |
| D-03 | A distinct encryption key per firm; evidence in encrypted object storage under that key | **[PRD]** | NFR-02, §2 | Key register | 1 | M | [encryption-architecture](encryption-architecture.md), [key-management](key-management.md) |
| D-04 | Single approved crypto module; raw primitives blocked by static analysis | **[PROP]** | — | Code, CI results | 1 | M | [encryption-architecture](encryption-architecture.md) |
| D-05 | Authenticated encryption with mandatory additional data binding firm and object identity | **[PROP]** | implements NFR-01 | Code review | 1 | M | [encryption-architecture](encryption-architecture.md) |
| D-06 | Envelope encryption: per-object data key → per-firm key → key service | **[PROP]** | implements NFR-02 | Format specification | 1 | M | [encryption-architecture](encryption-architecture.md) |
| D-07 | Algorithm and version identifier on every ciphertext and signature | **[PROP]** | supports NFR-07 longevity | Format specification | 1 | H | [encryption-architecture](encryption-architecture.md) |
| D-08 | Key policies require a matching firm encryption context; non-organisation principals and non-EU regions denied | **[PROP]** | implements NFR-01, NFR-03 | Key policies | 1 | M | [key-management](key-management.md) |
| D-09 | Key administration and data-plane decryption are mutually exclusive; key administration is break-glass only | **[PROP]** | — | Conformance report | 1 | M | [key-management](key-management.md), [insider-threat-protection](supporting-topics/insider-threat-protection.md) |
| D-10 | Automatic annual key rotation retaining prior versions so six-year-old ciphertext stays readable | **[PROP]** | supports NFR-07 | Key register | 1 | M | [key-management](key-management.md) |
| D-11 | **Key deletion denied for audit, evidence and backup keys; per-firm key deletion blocked while records are in retention** | **[PRD in effect]** | NFR-07, §2 | Key policies, precondition tests | 1 | M | [key-management](key-management.md) |
| D-12 | Documented cryptographic control policy | **[PROP]** | — | Policy document | 1 | H | [encryption-architecture](encryption-architecture.md), [key-management](key-management.md) |

## E. Document and data protection

| ID | Control | Class | PRD anchor / driver | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| E-01 | Complete data isolation between firms | **[PRD]** | NFR-01 | Isolation test results | 1 | M | [document-confidentiality](document-confidentiality.md) |
| E-02 | Four-layer tenant isolation (repository, row-level security, key encryption context, scoped identity) | **[PROP]** | implements NFR-01 | Test results | 1 | M | [document-confidentiality](document-confidentiality.md) |
| E-03 | Classification assigned at ingest, escalatable but not lowerable without dual approval, enforced on every access | **[PROP]** | implements NFR-01 | Classification audit | 1 | M | [document-confidentiality](document-confidentiality.md) |
| E-04 | Signed URLs only: short TTL, single use, never logged or emailed | **[PROP]** | — | Code, log sampling | 1 | M | [document-confidentiality](document-confidentiality.md), [secure-media-storage](secure-media-storage.md) |
| E-05 | Watermarked server-side preview as the default access mode | **[PROP]** | — | Rendering configuration | 1 | H | [document-confidentiality](document-confidentiality.md), [data-loss-prevention](supporting-topics/data-loss-prevention.md) |
| E-06 | Derivative registry with classification and key inheritance; no derivative created outside the derivation service | **[PROP]** | implements NFR-01 | Registry, reconciliation | 1 | M | [document-confidentiality](document-confidentiality.md) |
| E-07 | **No deletion path for evidence, results, reports or audit records, for any principal including administrators** | **[PRD]** | NFR-07, §2, §7.1 step 5 | Negative tests | 1 | M | [document-confidentiality](document-confidentiality.md), [immutable-evidence-retention](immutable-evidence-retention.md) |
| E-08 | Only the FR-24 file types accepted; maximum size configurable in the Portal without a code release | **[PRD]** | FR-24, NFR-11 | Configuration, tests | 1 | M | [secure-media-storage](secure-media-storage.md) |
| E-09 | Quarantine-scan-promote upload pipeline, multi-engine, **fail closed** | **[PROP]** | — | Scan logs | 1 | M | [secure-media-storage](secure-media-storage.md) |
| E-10 | File processing sandboxed: separate account, no credentials, no network egress, ephemeral | **[PROP]** | — | Account configuration | 1 | M | [secure-media-storage](secure-media-storage.md) |
| E-11 | Separate content origin with sandboxed content-security policy | **[PROP]** | — | Header scan | 1 | M | [document-confidentiality](document-confidentiality.md), [secure-media-storage](secure-media-storage.md) |
| E-12 | Deletion capability exists only for record classes with no retention obligation | **[PROP]** | consistent with NFR-07 | Class registry | 1 | H | [document-confidentiality](document-confidentiality.md) |
| E-13 | GDPR erasure requests touching protected classes | **[OPEN — LEGAL]** | PRD conflict | Documented position | 1 | M | [regulatory-obligations](regulatory-obligations.md), [immutable-evidence-retention](immutable-evidence-retention.md) |

## F. Records, logging and retention

| ID | Control | Class | PRD anchor / driver | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| F-01 | Every user action recorded permanently with actor, action, time and originating device | **[PRD]** | FR-13, FR-21 | Audit samples | 1 | M | [audit-logging](audit-logging.md) |
| F-02 | Audit log append-only; **no modify or delete capability for anyone, including SayOne administrators** | **[PRD]** | NFR-04, §2 | Bucket and key policies, negative tests | 1 | M | [audit-logging](audit-logging.md), [immutable-evidence-retention](immutable-evidence-retention.md) |
| F-03 | Minimum six-year retention for test results, findings, evidence, reports, audit log and notification log | **[PRD]** | NFR-07, §2 | Retention configuration | 1 | M | [immutable-evidence-retention](immutable-evidence-retention.md) |
| F-04 | Signed-off results immutable; correction only by amendment with written explanation, original retained | **[PRD]** | FR-27 | Workflow tests | 1 | M | [immutable-evidence-retention](immutable-evidence-retention.md) |
| F-05 | Issued reports permanently archived exactly as issued and unchangeable | **[PRD]** | FR-61 | Workflow tests | 1 | M | [immutable-evidence-retention](immutable-evidence-retention.md) |
| F-06 | Not Applicable decisions and original sample selections immutably retained | **[PRD]** | FR-21b, FR-21c | Workflow tests | 1 | M | [immutable-evidence-retention](immutable-evidence-retention.md) |
| F-07 | Every WSP version and mapping change retained permanently; nothing overwritten | **[PRD]** | FR-37 | Version history | 1 | M | [immutable-evidence-retention](immutable-evidence-retention.md) |
| F-08 | Requirement ID and test procedure versions retained in full; old versions never deleted | **[PRD]** | §2, SA-02 | Version history | 1 | M | [immutable-evidence-retention](immutable-evidence-retention.md) |
| F-09 | Operational logs separated from audit events, with distinct pipelines and retention | **[PROP]** | implements NFR-04 | Pipeline configuration | 1 | M | [audit-logging](audit-logging.md) |
| F-10 | Canonical audit schema including decision, policy version, purpose and reason | **[PROP]** | — | Schema + samples | 1 | M | [audit-logging](audit-logging.md) |
| F-11 | Redaction by construction via a typed sensitive-field registry, enforced by a blocking static-analysis rule | **[PROP]** | — | CI results, log sampling | 1 | M | [audit-logging](audit-logging.md) |
| F-12 | Audit events hash-chained and written to write-once storage in a write-only log-archive account | **[PROP]** | implements NFR-04 | Bucket and key policies | 1 | M | [audit-logging](audit-logging.md), [immutable-evidence-retention](immutable-evidence-retention.md) |
| F-13 | Synchronous durable audit write before completing high-value actions | **[PROP]** | supports FR-13 | Latency and coverage tests | 1 | M | [audit-logging](audit-logging.md) |
| F-14 | Audit-event coverage asserted per endpoint in CI | **[PROP]** | supports FR-13 | CI results | 1 | H | [audit-logging](audit-logging.md) |
| F-15 | Retention service with per-class minimums and legal-hold capability | **[PROP]** | implements NFR-07 | Policy configuration | 1 | M | [immutable-evidence-retention](immutable-evidence-retention.md) |
| F-16 | Scheduled internal verification of sealed records and the chain head | **[PROP]** | implements NFR-04 | Verification records | 1 | H | [immutable-evidence-retention](immutable-evidence-retention.md) |
| F-17 | Firms can search and export their own audit trail | **[PROP]** | implements the purpose of FR-13 | Export samples | 2 | H | [audit-logging](audit-logging.md) |
| F-18 | Full AI inference audit record for every mapping call | **[PROP]** | supports FR-31, FR-32 | Inference records | 1 | M | [ai-governance](ai-governance.md), [audit-logging](audit-logging.md) |
| F-19 | When retention ends after the six-year minimum | **[OPEN — LEGAL]** | PRD sets a floor only | Decision record | 2 | H | [immutable-evidence-retention](immutable-evidence-retention.md) |

## G. Network and infrastructure

| ID | Control | Class | PRD anchor / driver | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| G-01 | Account separation with organisation-level guardrails | **[PROP]** | implements NFR-01, NFR-03 | Organisation configuration | 1 | M | [network-security](supporting-topics/network-security.md), [reference-cloud-architecture](reference-cloud-architecture.md) |
| G-02 | Data tier with no route to the internet | **[PROP]** | — | Network configuration | 1 | M | [network-security](supporting-topics/network-security.md) |
| G-03 | Private service endpoints with restrictive policies | **[PROP]** | implements NFR-03 | Endpoint policies | 1 | M | [network-security](supporting-topics/network-security.md) |
| G-04 | Default-deny egress with a version-controlled allowlist; denials alert | **[PROP]** | implements NFR-03 | Rule configuration, alerts | 1 | M | [network-security](supporting-topics/network-security.md), [data-loss-prevention](supporting-topics/data-loss-prevention.md) |
| G-05 | DNS resolver firewall with query logging | **[PROP]** | — | Configuration, logs | 1 | H | [network-security](supporting-topics/network-security.md) |
| G-06 | WAF with rate limiting, tuned in count mode before blocking; request size aligned to the NFR-11 ceiling | **[PROP]** | supports NFR-08, NFR-11 | Rule metrics | 1 | M | [network-security](supporting-topics/network-security.md) |
| G-07 | No bastion hosts or SSH; administrative access fully session-recorded | **[PROP]** | supports FR-13 | Session recordings | 1 | M | [network-security](supporting-topics/network-security.md), [insider-threat-protection](supporting-topics/insider-threat-protection.md) |
| G-08 | Default-deny workload network policy; hardened runtime profile | **[PROP]** | — | Manifests, admission logs | 1 | M | [network-security](supporting-topics/network-security.md) |
| G-09 | Deny-by-default service call graph | **[PROP]** | implements NFR-01 | Policy manifests | 1 | H | [zero-trust-architecture](supporting-topics/zero-trust-architecture.md) |

## H. Secure development and supply chain

| ID | Control | Class | PRD anchor / driver | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| H-01 | Blocking CI gates: secrets, new Critical/High vulnerabilities, tenant-isolation failures, unsigned artefacts, policy violations, record-immutability violations | **[PROP]** | protects NFR-01, NFR-07 | CI history | 1 | M | [secure-sdlc](secure-sdlc.md) |
| H-02 | Custom static-analysis rules for tenant scoping, authorisation, sensitive-field logging, crypto usage, egress, record immutability and prompt construction | **[PROP]** | protects NFR-01, NFR-04, NFR-07 | Rules + results | 1 | M | [secure-sdlc](secure-sdlc.md) |
| H-03 | Threat model required for qualifying changes | **[PROP]** | — | Change records | 1 | H | [threat-modelling](supporting-topics/threat-modelling.md) |
| H-04 | Two-person review; signed commits | **[PROP]** | — | Review records | 1 | M | [secure-sdlc](secure-sdlc.md), [secure-cicd](secure-cicd.md) |
| H-05 | Vulnerability SLAs by severity with dated exceptions | **[PROP]** | — | SLA reports | 1 | M | [secure-sdlc](secure-sdlc.md) |
| H-06 | Secretless CI via federation; no long-lived cloud keys | **[PROP]** | — | Identity configuration | 1 | M | [secrets-management](secrets-management.md), [secure-cicd](secure-cicd.md) |
| H-07 | Ephemeral, EU-resident build and deploy runners | **[PROP]** | supports NFR-03 | Runner configuration | 1 | M | [secure-cicd](secure-cicd.md) |
| H-08 | Signed artefacts with provenance and attestations, verified at admission | **[PROP]** | — | Attestations, admission logs | 1 | H | [supply-chain-security](supply-chain-security.md) |
| H-09 | Bill of materials generated at build time with continuous advisory re-evaluation | **[PROP]** | — | Repository | 1 | H | [supply-chain-security](supply-chain-security.md) |
| H-10 | Dependency pinning, cooldown, private registry proxy | **[PROP]** | — | Lockfiles, configuration | 1 | M | [supply-chain-security](supply-chain-security.md) |
| H-11 | Licence scanning with a deny-list derived from CC-03 exclusive assignment | **[PROP]** | CC-03 | Scan results | 1 | H | [supply-chain-security](supply-chain-security.md) |
| H-12 | Vendor intake gate requiring EU-only processing before any client data is touched | **[PROP]** | NFR-03, NFR-06 | Vendor records | 1 | M | [supply-chain-security](supply-chain-security.md) |
| H-13 | Independent penetration test including multi-tenancy before real client data | **[PROP]** | protects NFR-01 | Test report | 1 | M | [secure-sdlc](secure-sdlc.md) |
| H-14 | Deployment record written to the immutable store | **[PROP]** | reuses NFR-04 store | Deploy records | 2 | S | [secure-cicd](secure-cicd.md) |

## I. AI governance (WSP mapping only)

| ID | Control | Class | PRD anchor / driver | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| I-01 | AI mapping output is advisory; a compliance officer confirms or adjusts every suggestion | **[PRD]** | FR-31 | Workflow tests | 1 | M | [ai-governance](ai-governance.md) |
| I-02 | Two independent senior approvers per mapping confirmation and per reversal; policy author excluded | **[PRD]** | FR-32, FR-33 | Approval records | 1 | M | [ai-governance](ai-governance.md) |
| I-03 | Minimum 85% verified accuracy against pre-defined verification vectors at UAT, maintained thereafter | **[PRD]** | §6.2 | Evaluation results | 1 | M | [ai-governance](ai-governance.md) |
| I-04 | Mapping re-runs automatically on a new labelled WSP version; manual overrides carry a visible tag | **[PRD]** | §6.3, GAP-09 | Workflow tests | 1 | M | [ai-governance](ai-governance.md) |
| I-05 | No customer data in developer AI tooling; managed settings with deny rules and bypass disabled, verified by test | **[PROP]** | supports NFR-01, NFR-03 | Configuration + test records | 1 | M | [ai-governance](ai-governance.md), [data-loss-prevention](supporting-topics/data-loss-prevention.md) |
| I-06 | Production inference EU-resident, no training on inputs or outputs, no provider retention | **[PROP]** | NFR-03 | Configuration + contract | 1 | M | [ai-governance](ai-governance.md) |
| I-07 | WSP content delimited as untrusted; output schema-constrained; no privileged action from model output | **[PROP]** | supports FR-31 | Prompt versions, tests | 1 | M | [ai-governance](ai-governance.md) |
| I-08 | Deterministic verification that cited WSP spans exist at the stated offsets | **[PROP]** | supports §6.2 | Validation results | 1 | M | [ai-governance](ai-governance.md) |
| I-09 | Evaluation harness gating promotion on the 85% bar | **[PROP]** | implements §6.2 | Evaluation results | 1 | M | [ai-governance](ai-governance.md) |
| I-10 | Reversible entity pseudonymisation before inference | **[PROP]** | GDPR Art. 5(1)(c), 32 | Configuration, samples | 2 | H | [ai-governance](ai-governance.md) |
| I-11 | AI-suggested mappings labelled as such in the interface | **[PROP]** | consistent with GAP-09 tagging | Screenshots | 1 | H | [ai-governance](ai-governance.md) |
| I-12 | Inference provider and model selection | **[OPEN]** | PRD silent | Decision record | 1 | M | [ai-governance](ai-governance.md) |
| I-13 | Who may initiate a manual mapping override | **[OPEN]** | GAP-09 partial | Decision record | 1 | H | [ai-governance](ai-governance.md), [identity-and-access-management](identity-and-access-management.md) |

## J. Resilience and recovery

| ID | Control | Class | PRD anchor / driver | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| J-01 | Availability target 99.5%, planned maintenance communicated in advance | **[PRD]** | NFR-08 | Availability reporting | 1 | M | [disaster-recovery](disaster-recovery.md) |
| J-02 | Whether the target becomes 99.9%, and any recovery time or recovery point targets | **[OPEN]** | TI-02 | Decision record | 1 | M | [disaster-recovery](disaster-recovery.md) |
| J-03 | Record copies exist outside the primary failure domain, within the EU | **[PROP]** | protects NFR-07; NFR-03 | Replication configuration | 1 | M | [disaster-recovery](disaster-recovery.md), [secure-backups](secure-backups.md) |
| J-04 | Backup account isolation; deletion denied to production principals | **[PROP]** | protects NFR-07 | Configuration | 1 | M | [secure-backups](secure-backups.md) |
| J-05 | Immutable retention lock on longer-retention backup vaults | **[PROP]** | protects NFR-07 | Lock configuration | 1 | M | [secure-backups](secure-backups.md) |
| J-06 | Automated restore verification with integrity, decryption and chain assertions | **[PROP]** | GDPR Art. 32(1)(d) | Verification records | 1 | M | [secure-backups](secure-backups.md) |
| J-07 | Recovery architecture selection and exercise cadence | **[OPEN]** | PRD silent | Decision record | 1 | H | [disaster-recovery](disaster-recovery.md) |
| J-08 | Degraded modes implemented and tested: read-only, AI-degraded, evidence-only | **[PROP]** | supports NFR-07, FR-31 | Test records | 2 | H | [disaster-recovery](disaster-recovery.md) |
| J-09 | Firm-granular point-in-time restore | **[PROP]** | protects NFR-01 | Restore tests | 2 | H | [secure-backups](secure-backups.md) |
| J-10 | No recovery figure committed to a customer until measured | **[PROP]** | TI-02 open | Measurement records | 1 | M | [disaster-recovery](disaster-recovery.md), [deployment-recommendations](deployment-recommendations.md) |

## K. Monitoring, response and insider risk

| ID | Control | Class | PRD anchor / driver | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| K-01 | Detections as code with positive and negative unit tests | **[PROP]** | — | Rule repository | 1 | M | [security-monitoring](security-monitoring.md) |
| K-02 | Priority detections implemented before real client data, including the cross-firm and protected-record tripwires | **[PROP]** | protects NFR-01, NFR-04, NFR-07 | Rule list, test results | 1 | M | [security-monitoring](security-monitoring.md) |
| K-03 | Log-source heartbeat monitoring | **[PROP]** | — | Alert configuration | 1 | M | [security-monitoring](security-monitoring.md) |
| K-04 | Canary records and credentials seeded | **[PROP]** | — | Detection configuration | 1 | H | [insider-threat-protection](supporting-topics/insider-threat-protection.md), [secrets-management](secrets-management.md) |
| K-05 | GDPR Art. 33 processor assessment performed at triage with retained rationale | **[PROP]** | NFR-06 | Assessment records | 1 | M | [security-monitoring](security-monitoring.md) |
| K-06 | Firm incident-notification templates; **notification deadline agreed contractually** | **[PROP / OPEN]** | PRD silent | Templates, contract | 1 | M | [security-monitoring](security-monitoring.md) |
| K-07 | Automatic evidence preservation on top-severity declaration | **[PROP]** | — | Preservation records | 1 | H | [security-monitoring](security-monitoring.md) |
| K-08 | Continuous alert triage model | **[OPEN]** | not staffed by the PRD | Decision record | 1 | H | [security-monitoring](security-monitoring.md) |
| K-09 | Mutually exclusive capability matrix, continuously verified | **[PROP]** | — | Scan reports | 1 | M | [insider-threat-protection](supporting-topics/insider-threat-protection.md) |
| K-10 | Dual authorisation for irreversible actions | **[PROP]** | — | Approval records | 1 | M | [insider-threat-protection](supporting-topics/insider-threat-protection.md) |
| K-11 | Per-role access rate limits with graduated response | **[PROP]** | protects NFR-01 | Threshold configuration | 1 | H | [insider-threat-protection](supporting-topics/insider-threat-protection.md), [data-loss-prevention](supporting-topics/data-loss-prevention.md) |
| K-12 | Session recording for break-glass and key administration | **[PROP]** | supports FR-13 | Recordings | 1 | M | [insider-threat-protection](supporting-topics/insider-threat-protection.md) |
| K-13 | Prompt offboarding with a documented checklist | **[PROP]** | supports FR-14 | Timing records | 1 | M | [insider-threat-protection](supporting-topics/insider-threat-protection.md) |
| K-14 | Employee monitoring lawful basis, transparency and any required consultation | **[PROP / OPEN — LEGAL]** | — | Documentation | 1 | M | [insider-threat-protection](supporting-topics/insider-threat-protection.md), [data-loss-prevention](supporting-topics/data-loss-prevention.md) |
| K-15 | Object storage scanning for misplaced sensitive data, including non-production | **[PROP]** | implements NFR-03 | Findings | 1 | H | [data-loss-prevention](supporting-topics/data-loss-prevention.md) |
| K-16 | Security awareness training | **[PROP]** | — | Completion records | 1 | S | [insider-threat-protection](supporting-topics/insider-threat-protection.md) |

---

## Coverage summary

| Requirement | Controls | Highest-risk gap if unimplemented |
|---|---|---|
| **NFR-01** multi-tenant isolation | E-01, E-02, E-03, E-06, C-11, D-05, D-08, G-09, K-02, K-11, J-09 | E-02 and C-11 — an untested isolation model |
| **NFR-02** AES-256 / TLS 1.3 / per-firm key | D-01, D-02, D-03, D-04, D-05, D-06, D-08, D-10 | D-03 and D-08 — a per-firm key not bound into the key policy is decorative |
| **NFR-03** EU residency | B-01, B-02, B-03, B-04, B-05, B-08, G-03, G-04, H-07, H-12, I-06, K-15 | B-04 — the unglamorous tier is where residency fails |
| **NFR-04** immutable audit | F-01, F-02, F-09→F-14, F-16, D-11, K-02 | F-02 and D-11 — any deletion path, direct or via key destruction |
| **NFR-06** GDPR processor | A-01, A-02, A-03, A-05, K-05, E-13 | E-13 — the unresolved erasure conflict |
| **NFR-07** six-year non-deletable retention | E-07, F-03→F-08, F-15, D-11, J-03, J-04, J-05, J-06 | J-03 — records with no copy outside the primary failure domain |
| **NFR-08** availability | J-01, J-02, G-06, J-07, J-08 | J-02 — the target itself is unresolved |
| **§3 access model** | C-01→C-10, C-12 | C-15 and C-16 — two unresolved scope questions block build |
| **§6 WSP mapping** | I-01→I-11 | I-03 and I-09 — the 85% bar needs a harness before UAT, not after |
