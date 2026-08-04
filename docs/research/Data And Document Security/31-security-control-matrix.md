# 31 — Security Control Matrix

Controls are grouped by domain. Each row maps a control to its regulatory drivers, implementation, evidence source, and the research document that details it.

**Legend — Phase:** 1 = MVP / pre-first-customer · 2 = pre-enterprise GA · 3 = scale/maturity.
**Priority:** M = mandatory before production data · H = high · S = standard.

## A. Governance and regulatory

| ID | Control | Regulatory driver | Implementation | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| A-01 | Obligation register maintained as code | DORA 5–6; NIS2 20–21; GDPR 5(2) | Versioned YAML in repo; quarterly review | Register + review records | 1 | M | 01 |
| A-02 | Management body accountability for ICT risk | DORA 5(2); NIS2 20 | Named accountable executive; quarterly board reporting | Board minutes | 1 | M | 01 |
| A-03 | DPIA for AI-assisted document processing | GDPR 35 | Documented DPIA with LINDDUN risk section | DPIA document | 1 | M | 05, 24 |
| A-04 | Records of processing (controller + processor) | GDPR 30 | Maintained register | RoPA | 1 | M | 01 |
| A-05 | AI Act classification assessment | AI Act 6, 50 | Documented classification; annual review | Assessment + legal opinion | 1 | H | 05 |
| A-06 | Sub-processor register, published + machine-readable | GDPR 28; DORA 28(3) | Public list + attestation API | Register + change notices | 1 | M | 02, 18 |
| A-07 | Customer DORA register-of-information extract | DORA 28(3) | Structured export per tenant | Export samples | 2 | H | 18 |
| A-08 | ISO/IEC 27001 certification | Market + NIS2 24 | ISMS implementation, external audit | Certificate + SoA | 2 | H | 01 |
| A-09 | SOC 2 Type II | Market | 6-month control operation, external audit | Report | 2 | H | 01 |
| A-10 | Coordinated vulnerability disclosure policy | NIS2 21(2)(e); CRA | security.txt, SECURITY.md, PGP inbox, safe harbour | Policy + advisory history | 1 | M | 04 |
| A-11 | CRA scoping gate on installable artefacts | CRA | Design-review gate | Scoping decisions | 2 | H | 01 |

## B. Data residency and transfers

| ID | Control | Regulatory driver | Implementation | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| B-01 | EU-only region enforcement | GDPR Ch.V; DORA 28–30 | SCP + RCP on `aws:RequestedRegion`; CI plan check | SCP config, CI logs | 1 | M | 02 |
| B-02 | Boring-tier residency (logs, errors, email, CI, support) | GDPR Ch.V | EU-resident implementations per component | Component inventory | 1 | M | 02 |
| B-03 | Embeddings/indexes classified as personal data | GDPR 4(1) | Tenant-key encryption, in-region, same retention | Data map | 1 | M | 02, 06 |
| B-04 | SCCs Module 3 with Indian entity | GDPR 46(2)(c) | Executed agreement with accurate Annex II | Signed SCCs | 1 | M | 03 |
| B-05 | Transfer Impact Assessment, annually reviewed | Schrems II; EDPB 01/2020 | Documented TIA covering IT Act s.69, Telecom Act s.20, DPDP | TIA document | 1 | M | 03 |
| B-06 | Synthetic-data-only in dev/staging | GDPR 5(1)(c), Ch.V | Fixture factory; Macie scan of non-prod accounts | Scan results | 1 | M | 03 |
| B-07 | Zero standing production access | DORA 9(4)(c); GDPR 32(4) | JIT break-glass, dual EU approval, VDI, recorded | Access logs, approvals | 1 | M | 03, 10 |
| B-08 | EU session-location policy for production access | GDPR Ch.V | Conditional access + Cedar policy | Policy + denial logs | 1 | M | 03, 12 |
| B-09 | Government access request playbook (both entities) | GDPR Ch.V | Documented, tested annually | Playbook + test record | 1 | H | 03 |
| B-10 | EU-resident production on-call capability | GDPR Ch.V; DORA 11 | Hired or contracted before enterprise GA | Rota | 2 | M | 03 |

## C. Identity and access

| ID | Control | Regulatory driver | Implementation | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| C-01 | Phishing-resistant MFA (FIDO2) for all workforce | DORA RTS; NIS2 21(2)(j) | IdP enforcement, no SMS | IdP config, coverage report | 1 | M | 10 |
| C-02 | Zero standing privilege; JIT elevation ≤4h | DORA 9(4)(c) | Approval workflow, auto-revoke | Grant logs | 1 | M | 10 |
| C-03 | Centralised Cedar authorisation, per-request | GDPR 25(2); DORA 9(4)(c) | Policy bundles, sidecar evaluation | Policy repo, decision logs | 1 | M | 10, 12 |
| C-04 | Cross-tenant negative test matrix in CI | GDPR 32 | Every role × action, blocking gate | CI results | 1 | M | 06, 10 |
| C-05 | SCIM provisioning/deprovisioning, 15-min SLA | DORA RTS; NIS2 21(2)(i) | HR → IdP → systems | Deprovision timings | 1 | M | 10, 17 |
| C-06 | Customer enterprise SSO (SAML/OIDC) + SCIM | Market; GDPR 32 | Managed SSO provider | Tenant configs | 1 | H | 10 |
| C-07 | Time-boxed, scoped `auditor` role | MiCA 68; DORA 30(3)(e) | Product feature | Access records | 2 | H | 10 |
| C-08 | Step-up auth for export, key config, role change | DORA RTS | Policy engine | Auth events | 1 | H | 10 |
| C-09 | Quarterly privileged access recertification | DORA RTS | Automated unused-access findings + human review | Recertification records | 2 | H | 10 |
| C-10 | Two-person break-glass, split knowledge, quarterly test | DORA 9 | Offline hardware MFA | Test records, use alerts | 1 | M | 10 |

## D. Cryptography and keys

| ID | Control | Regulatory driver | Implementation | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| D-01 | Documented cryptographic control policy | DORA RTS 2024/1774; NIS2 21(2)(h) | Approved algorithms, lifecycles, deprecation | Policy document | 1 | M | 07 |
| D-02 | Single approved crypto module; no raw primitives | GDPR 32 | Library + SAST rule | Code, CI results | 1 | M | 07 |
| D-03 | AES-256-GCM with mandatory AAD (tenant + object) | GDPR 32 | Non-optional in function signature | Code review | 1 | M | 07 |
| D-04 | Algorithm/version identifier on every ciphertext | DORA RTS (crypto agility) | Envelope format | Format spec | 1 | M | 07 |
| D-05 | TLS 1.3 external; mTLS internal (SPIFFE, ≤24h certs) | DORA 9; NIS2 21(2)(h) | Linkerd + ACM | Config, scan results | 1 | M | 07, 12 |
| D-06 | Per-tenant CMK with `tenant_id` encryption context | GDPR 32; DORA 9 | KMS key policy template + conformance scan | Key policies | 1 | M | 08 |
| D-07 | Key admin / data access separation of duties | DORA 9(4)(c) | IAM mutual exclusion, verified continuously | Conformance report | 1 | M | 08, 17 |
| D-08 | Automatic annual CMK rotation | DORA RTS | KMS automatic rotation | Key register | 1 | M | 08 |
| D-09 | 30-day key deletion window, dual approval, alerting | DORA 9; GDPR 32 | KMS + workflow | Deletion records | 1 | M | 08 |
| D-10 | Key register with `pqc_migration_status` | DORA RTS | Generated daily from cloud APIs | Register export | 1 | H | 08 |
| D-11 | Customer-managed keys (T2 grant, T3 XKS) | GDPR Ch.V; DORA 30(3) | Key-broker tiering | Tenant key config | 2/3 | H | 20 |
| D-12 | Hybrid PQC in transit (X25519MLKEM768) | NIS CG PQC roadmap | Endpoint config when path supports | Config, scan | 3 | S | 07 |
| D-13 | Nitro Enclave decryption (data in use) | DORA 9(2) | Enclave-bound key policy | Attestation records | 2 | H | 07, 17 |

## E. Document and data protection

| ID | Control | Regulatory driver | Implementation | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| E-01 | Five-level classification enforced at every access | GDPR 32; DORA RTS | Assigned at ingest, policy-enforced | Classification audit | 1 | M | 06 |
| E-02 | Four-layer tenant isolation (repo, RLS, KMS ctx, IAM) | GDPR 32 | Forced RLS + repository + key policy | Test results | 1 | M | 06 |
| E-03 | Presigned URLs ≤60s, single use, never logged | GDPR 32 | Document service | Code, log sampling | 1 | M | 06, 13 |
| E-04 | Watermarked server-side preview as default | GDPR 32; DLP | Rendering service | Render config | 1 | H | 06, 23 |
| E-05 | Derivative registry; classification/key inheritance | GDPR 17, 32 | Single derivation service + reconciliation | Registry, reconciliation | 1 | M | 06 |
| E-06 | Deletion saga with verified completion + certificate | GDPR 17 | Fan-out job | Deletion certificates | 1 | M | 06 |
| E-07 | Crypto-shredding for erasure vs. immutable backups | GDPR 17; MiCA 68(9) | Per-document DEK destruction | DPA + shred records | 1 | M | 06, 15 |
| E-08 | Quarantine-scan-promote upload pipeline, fail closed | DORA 9; GDPR 32 | Multi-engine AV + structural checks | Scan logs | 1 | M | 13 |
| E-09 | Sandboxed processing: no credentials, no egress | GDPR 32 | Separate account, ephemeral compute | Account config | 1 | M | 13 |
| E-10 | Separate content origin with CSP sandbox | GDPR 32 | Header config | Header scan | 1 | M | 06, 13 |
| E-11 | `PRIVILEGED` class excluded from AI and tenant search | Professional privilege; GDPR 5 | Policy engine | Config + tests | 1 | H | 06 |

## F. Evidence, logging and retention

| ID | Control | Regulatory driver | Implementation | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| F-01 | Operational vs. audit log separation | DORA RTS; GDPR 5(1)(c) | Distinct pipelines and retention | Pipeline config | 1 | M | 14 |
| F-02 | Canonical audit schema incl. decision, policy version, purpose | DORA RTS; GDPR 5(2) | Versioned schema | Schema + samples | 1 | M | 14 |
| F-03 | Redaction by construction (typed field registry + SAST) | GDPR 5(1)(c), 32 | Serialiser + CI rule | CI results, log sampling | 1 | M | 14 |
| F-04 | Audit logs to write-only `log-archive`, Object Lock COMPLIANCE | DORA RTS | Cross-account, delete denied to all | Bucket + key policies | 1 | M | 14 |
| F-05 | Synchronous audit write for RESTRICTED reads, exports, key ops | DORA RTS | Service implementation | Latency + coverage tests | 1 | M | 14 |
| F-06 | Audit-event coverage test per endpoint in CI | DORA RTS | Blocking gate | CI results | 1 | H | 14 |
| F-07 | Evidence packages: manifest + signature + qualified timestamp | eIDAS 41; MiCA 68(9) | Evidence service + QTSP | Sealed packages | 1 | M | 15 |
| F-08 | Per-tenant hash chain + daily Merkle root, published | MiCA 68(9); DORA 12 | Sealer service | Root feed, verification logs | 1 | M | 15 |
| F-09 | Retention policy engine (min/max, legal hold, basis) | MiCA 68(9); GDPR 5(1)(e) | Policy objects driving lock durations | Policy config, expiry logs | 1 | M | 15 |
| F-10 | Automatic expiry job with its own evidence record | GDPR 5(1)(e) | Scheduled job + alerting | Expiry evidence | 1 | M | 15 |
| F-11 | Open-source `evidence-verify` CLI + daily internal verification | MiCA 68(9) | Published tool + cron | Verification records | 2 | H | 15 |
| F-12 | Customer-facing exportable tenant audit trail | MiCA 68(9); DORA 30 | Product feature | Export samples | 2 | H | 14 |
| F-13 | AI inference audit record for every call | AI Act 50; GDPR 5(2) | Assessment service | Inference records | 1 | M | 05, 14 |

## G. Network and infrastructure

| ID | Control | Regulatory driver | Implementation | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| G-01 | Account separation with SCP/RCP guardrails | DORA RTS (segmentation) | Organizations | Org config | 1 | M | 11 |
| G-02 | Data tier with no internet route | DORA RTS | Subnet routing | VPC config | 1 | M | 11 |
| G-03 | VPC endpoints with restrictive endpoint policies | DORA 9 | All AWS service access | Endpoint policies | 1 | M | 11 |
| G-04 | Default-deny egress, FQDN allowlist, alert on denial | DORA 9; DLP | Network Firewall | Rule config, denial alerts | 1 | M | 11, 23 |
| G-05 | DNS Firewall + query logging | DORA 10 | Route 53 Resolver | Config, logs | 1 | H | 11 |
| G-06 | WAF (count-mode tuning then block) + rate limits | DORA 9 | CloudFront + WAF | Rule metrics | 1 | M | 11 |
| G-07 | No bastion/SSH; Session Manager with full recording | DORA RTS | SSM | Session recordings | 1 | M | 11 |
| G-08 | NetworkPolicy default-deny; restricted Pod Security Standard | DORA RTS | Kubernetes | Manifests, admission logs | 1 | M | 11 |
| G-09 | Private-only EKS API endpoint | DORA RTS | Cluster config | Config | 1 | H | 11 |
| G-10 | Mesh authorisation policies (deny-by-default call graph) | DORA 9(4)(c) | Linkerd | Policy manifests | 1 | H | 12 |

## H. Secure development and supply chain

| ID | Control | Regulatory driver | Implementation | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| H-01 | Blocking CI gates (secrets, Critical/High, tenancy tests, unsigned, policy) | DORA RTS; NIS2 21(2)(e) | Pipeline config | CI history | 1 | M | 04 |
| H-02 | Custom SAST rules (tenancy, authz, PII logging, crypto, egress, prompts) | GDPR 32 | Semgrep rule set with tests | Rules + results | 1 | M | 04 |
| H-03 | Threat model required for qualifying changes | DORA 6, 8; GDPR 25 | CI path check | PR records | 1 | M | 24 |
| H-04 | Two-person review; signed commits | DORA RTS (change mgmt) | Branch protection | Review records | 1 | M | 04, 19 |
| H-05 | Vulnerability SLAs by severity, exceptions dated | DORA 8; NIS2 21(2)(e) | Tracking + reporting | SLA reports | 1 | M | 04 |
| H-06 | Secretless CI (OIDC), no long-lived cloud keys | DORA RTS | Trust policies, SCP | IAM config | 1 | M | 09, 19 |
| H-07 | Ephemeral, EU-resident build/deploy runners | GDPR Ch.V; DORA RTS | ARC on EKS | Runner config | 1 | M | 19 |
| H-08 | SLSA L3 provenance + Sigstore signing + attestations | NIS2 21(2)(d); CRA | Build pipeline | Attestations | 1 | H | 18 |
| H-09 | Kyverno admission verification of signature/attestations | NIS2 21(2)(d) | Cluster policy | Admission logs | 1 | H | 18 |
| H-10 | CycloneDX SBOM + Dependency-Track continuous re-eval + VEX | CRA Annex I; NIS2 21(2)(d) | Build + service | SBOM repository | 1 | H | 18 |
| H-11 | Dependency pinning + 3-day cooldown + private registry | NIS2 21(2)(d) | Renovate + CodeArtifact | Lockfiles, config | 1 | M | 18 |
| H-12 | Vendor intake gate before any data processing | GDPR 28; DORA 28–30 | Checklist + register update | Vendor records | 1 | M | 18 |
| H-13 | GitOps deployment; drift detection and revert | DORA RTS | Argo CD | Drift alerts | 1 | H | 19 |
| H-14 | Deployment evidence record sealed per deploy | DORA RTS | Pipeline → evidence service | Deploy evidence | 2 | H | 19 |

## I. AI governance

| ID | Control | Regulatory driver | Implementation | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| I-01 | Managed Claude Code settings (deny rules, bypass disabled) | GDPR Ch.V, 32 | MDM-deployed, enforcement tested | Config + test records | 1 | M | 05 |
| I-02 | No customer data in developer AI tooling (policy + technical) | GDPR Ch.V | Synthetic-only Zone D, hooks, DLP paste block | Policy, DLP events | 1 | M | 05, 23 |
| I-03 | Production inference EU-only, no training, no retention | GDPR Ch.V, 28 | Bedrock `eu-central-1`, cross-region disabled | Config + contract | 1 | M | 05 |
| I-04 | Document content delimited as untrusted; schema-constrained output | OWASP LLM01/LLM05 | Prompt architecture | Prompt versions, tests | 1 | M | 05 |
| I-05 | Deterministic citation verification (blocking) | GDPR 5(1)(d); market | Assessment service | Validation results | 1 | M | 05 |
| I-06 | Named human approval before assessment becomes evidence | GDPR 22; AI Act 14 | Workflow | Approval records | 1 | M | 05 |
| I-07 | Model registry + golden-set evaluation gate on promotion | AI Act; DORA RTS | Registry + CI | Eval results | 2 | H | 05 |
| I-08 | Reversible entity pseudonymisation before inference | GDPR 5(1)(c), 32 | Pipeline stage | Config, samples | 2 | H | 05 |
| I-09 | Fallback inference provider exercised quarterly | DORA 12, 28–30 | Second model path | Test records | 2 | H | 05 |
| I-10 | AI-generated content labelled in UI and exports | AI Act 50 | Product | Screenshots, exports | 1 | M | 05 |

## J. Resilience and recovery

| ID | Control | Regulatory driver | Implementation | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| J-01 | Documented BIA and tiered RTO/RPO | DORA 11 | BIA document | BIA + tier map | 1 | M | 16 |
| J-02 | Warm standby in `eu-north-1` (Aurora Global DB, S3 CRR) | DORA 12(3) | Infrastructure | Replication metrics | 2 | M | 16 |
| J-03 | Backup account isolation; delete denied to prod | DORA 12(2) | SCP + account topology | Config | 1 | M | 21 |
| J-04 | Vault Lock compliance mode on monthly/annual | DORA 12; ransomware | AWS Backup | Lock config | 1 | M | 21 |
| J-05 | Daily automated restore verification with integrity assertions | DORA 12(4)/(6); GDPR 32(1)(d) | Verification account job | Daily evidence records | 1 | M | 21 |
| J-06 | Semi-annual full regional failover **and failback** | DORA 11(6) | DR exercise | DR test reports | 2 | M | 16 |
| J-07 | Annual ransomware-scenario and crisis-comms exercises | DORA 11, 14 | Tabletop + technical | Exercise reports | 2 | H | 16 |
| J-08 | Four degraded modes implemented and tested | DORA 11, 12 | Read-only, AI-degraded, key-degraded, evidence-only | Test records | 2 | H | 16 |
| J-09 | Tenant-granular point-in-time restore | GDPR 32(1)(c); market | Restore tooling | Restore tests | 2 | H | 21 |
| J-10 | DR-region service parity check in CI | DORA 12(3) | Automated check | CI results | 1 | H | 16 |

## K. Monitoring, response and insider risk

| ID | Control | Regulatory driver | Implementation | Evidence | Phase | Pri | Doc |
|---|---|---|---|---|---|---|---|
| K-01 | Detections as code with positive/negative unit tests | DORA 10 | Repository + CI | Rule repo | 1 | M | 22 |
| K-02 | 14 priority detections implemented pre-GA | DORA 10 | SIEM rules | Rule list, test results | 1 | M | 22 |
| K-03 | Log-source heartbeat monitoring (alert on absence) | DORA 10 | Monitoring | Alert config | 1 | M | 22 |
| K-04 | Honeytoken documents and credentials in every tenant | Insider detection | Seeded records | Detection config | 1 | H | 17, 09 |
| K-05 | Regulatory classification engine at triage | DORA 18; NIS2 23; GDPR 33 | Decision tool | Classification records | 1 | M | 22 |
| K-06 | 2-hour customer incident notification SLA | DORA 30(2)(f) | Templates + workflow | Notification records | 1 | M | 01, 22 |
| K-07 | Automatic evidence preservation on P1 | DORA 19 | Runbook automation | Preservation records | 1 | H | 22 |
| K-08 | 24/7 MDR triage (telemetry-only access, EU processing) | DORA 10 | Provider contract | Contract, escalations | 1 | H | 22 |
| K-09 | Mutually-exclusive capability matrix, continuously verified | DORA 9(4)(c) | IAM + conformance scan | Scan reports | 1 | M | 17 |
| K-10 | Dual authorisation for irreversible actions | DORA 9(4)(c) | Workflow | Approval records | 1 | M | 17 |
| K-11 | Per-role access rate limits with graduated response | GDPR 32; DLP | Application | Threshold config, events | 1 | H | 17, 23 |
| K-12 | All operator access visible in the tenant's own audit log | GDPR 28(3)(h); trust | Product feature | Tenant audit samples | 2 | H | 17 |
| K-13 | Customer-approved access (lockbox) for T2/T3 | GDPR 28(3)(a) | Product feature | Approval records | 3 | S | 17 |
| K-14 | Session recording for break-glass and key admin | DORA RTS | SSM + WorkSpaces | Recordings | 1 | M | 17 |
| K-15 | Offboarding within 15 minutes; 90-day heightened monitoring | NIS2 21(2)(i) | HR automation | Timing records | 1 | M | 17 |
| K-16 | Quarterly purple-team validation of top attack paths | DORA 24–27 | Exercise programme | Exercise reports | 2 | H | 24 |
| K-17 | Annual independent penetration test incl. multi-tenancy | DORA 24–27 | External firm | Test reports | 2 | M | 04 |
| K-18 | Employee monitoring: lawful basis, transparency, consultation | GDPR 6, 88; national law | Privacy notice, balancing test | Documentation | 1 | M | 17, 23 |
| K-19 | Amazon Macie scanning for misplaced sensitive data | GDPR 32 | Scheduled scans incl. non-prod | Findings | 1 | H | 23 |
| K-20 | Security awareness training (all staff + role-specific) | DORA 13(6); NIS2 20(2) | Annual programme | Completion records | 1 | M | 17 |

## Coverage summary by regulation

| Regulation | Controls mapped | Highest-risk gaps if unimplemented |
|---|---|---|
| **GDPR** | A-03/04/06, B-01→10, C-03/04/05, D-*, E-*, F-01→13, I-*, K-18 | B-04/B-05 (transfer legality), E-02 (tenant isolation), E-07 (erasure) |
| **DORA** (via contract) | A-01/02/07, B-07, C-*, D-*, F-*, G-*, H-*, J-*, K-* | J-05 (untested restore), K-05/06 (reporting timelines), D-01 (crypto policy) |
| **MiCA** (enabling customers) | A-06, C-07, F-07→12, E-07 | F-07/F-08/F-09 (record integrity and retention) |
| **NIS2** | A-08/10, C-01, D-01/05, G-*, H-*, K-05 | K-05 (24h early warning readiness), H-10 (supply chain) |
| **CRA** (conditional) | A-11, H-08/H-10, A-10 | A-11 (undetected scope trigger) |
| **AI Act** | A-05, I-01→10 | I-06 (human oversight), I-10 (transparency) |
| **eIDAS 2** | F-07 | F-07 (evidence legal presumption) |
