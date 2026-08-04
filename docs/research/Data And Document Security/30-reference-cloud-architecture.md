# 30 — Reference Cloud Architecture

Target platform: **AWS, `eu-central-1` (Frankfurt) primary, `eu-north-1` (Stockholm) DR.** Portability constraints (Kubernetes, PostgreSQL, S3 API, PKCS#11/KMIP abstraction) preserve a migration path to an EU-sovereign provider — see ADR-001 and doc 02.

## 1. Account topology

| Account | Purpose | Notable controls |
|---|---|---|
| `management` | AWS Organizations, SCPs, RCPs, billing. No workloads. | Root MFA hardware token, break-glass only |
| `security-tooling` | GuardDuty/Security Hub delegated admin, SIEM ingestion, Macie, detection pipeline | Read-only into other accounts |
| `log-archive` | Immutable audit log and evidence storage | **Write-only from other accounts; delete denied to every principal**; Object Lock COMPLIANCE |
| `backup` | AWS Backup vaults | No trust path from `prod`; Vault Lock compliance mode |
| `shared-services` | ECR, CodeArtifact, Network Firewall egress, ephemeral CI runners | No customer data |
| `prod` | Production workloads | Zero standing human access |
| `staging` | Pre-production, full parity | Synthetic data only |
| `dev` | Development | Synthetic data only |
| `sandbox-processing` | Untrusted document parsing | No credentials, no network egress |
| `verification` | Daily automated restore verification | Ephemeral, auto-destroyed |

Organisation-wide guardrails: SCP denying non-EU regions, denying `iam:CreateAccessKey`, denying disablement of CloudTrail/GuardDuty/Config; RCPs restricting S3/KMS/STS access to `aws:PrincipalOrgID` and EU network paths.

## 2. Production data plane

```
                                Internet
                                    │
                    ┌───────────────┴────────────────┐
                    │  Route 53 (DNSSEC, query logs) │
                    └───────────────┬────────────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    │  CloudFront (TLS 1.3, EU PoPs) │
                    │  AWS WAF + Shield              │
                    └───────────────┬────────────────┘
                                    │
╔═══════════════════════ VPC 10.30.0.0/16, 3 AZs ═══════════════════════╗
║  PUBLIC subnets     │  ALB (TLS re-encrypt to targets), NAT GW        ║
║ ────────────────────┼───────────────────────────────────────────────  ║
║  PRIVATE-APP        │  EKS: ingress (Envoy) ──▶ Linkerd mesh (mTLS)   ║
║  (egress via        │    ├── api-gateway         (authn, rate limit)  ║
║   Network Firewall  │    ├── document-service    (tenant scoping)     ║
║   allowlist only)   │    ├── assessment-service  (AI orchestration)   ║
║                     │    ├── evidence-service    (sealing, chaining)  ║
║                     │    ├── policy-sidecars     (Cedar, signed bundle)║
║                     │    └── key-broker  ◀── Nitro Enclave (phase 2)  ║
║ ────────────────────┼───────────────────────────────────────────────  ║
║  PRIVATE-DATA       │  Aurora PostgreSQL (Multi-AZ, RLS forced,       ║
║  NO internet route  │    IAM auth, pgaudit)                           ║
║                     │  ElastiCache (encrypted, no persistence of PII) ║
║                     │  OpenSearch (per-tenant index, tenant CMK)      ║
║ ────────────────────┼───────────────────────────────────────────────  ║
║  PRIVATE-ENDPOINTS  │  VPC endpoints: S3, KMS, Secrets Manager, ECR,  ║
║                     │  STS, CloudWatch, SSM, SQS, Bedrock             ║
╚════════════════════════════════════════════════════════════════════════╝
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
   S3 buckets                  AWS KMS                    Amazon Bedrock
   quarantine / primary /      per-tenant CMK,            (Claude, eu-central-1,
   evidence (Object Lock       audit CMK, backup CMK,     EU-only inference,
   COMPLIANCE) / derivatives   evidence signing key       no training, no retention)
   / forensic
```

## 3. Component decisions

| Concern | Choice | Rationale / doc |
|---|---|---|
| Compute | EKS (managed node groups + Karpenter) | Portability to sovereign cloud (02); mature policy ecosystem |
| Service mesh | Linkerd | mTLS + identity authz at far lower operational cost than Istio (11, 12) |
| Workload identity | SPIFFE/SPIRE (via Linkerd) + EKS Pod Identity | No shared service credentials (09, 12) |
| Relational store | Aurora PostgreSQL, Multi-AZ, Global Database to `eu-north-1` | 15-min RPO for T1 (16); RLS for tenant isolation (06) |
| Object store | S3 with per-tenant SSE-KMS, Object Lock on evidence | Isolation + WORM (13, 15) |
| Search | OpenSearch, per-tenant index, tenant CMK | In-region, rebuildable (13, 21) |
| Vectors | pgvector in Aurora | Avoids a second data store; embeddings treated as personal data (02, 05) |
| Keys | AWS KMS; XKS for tier 3 | Sovereignty tiering (08, 20) |
| Secrets | Secrets Manager + Secrets Store CSI driver | Secretless-first (09) |
| Authorisation | Cedar, signed bundles, sidecar evaluation | Per-request authz, analysable (10, 12) |
| Workforce IdP | Entra ID or Okta → IAM Identity Center | Conditional access, FIDO2 (10) |
| Customer IdP | Managed enterprise SSO (WorkOS / Auth0) with SAML/OIDC/SCIM | Time-to-market (10) |
| AI inference | Amazon Bedrock (Claude) in `eu-central-1` | Residency + no training + existing sub-processor (05) |
| Egress control | AWS Network Firewall, FQDN allowlist | Exfiltration control (11, 23) |
| CI/CD | GitHub Actions (Zone 1 hosted, Zone 2/3 self-hosted ephemeral in EU) + Argo CD | Trust zoning, GitOps (19) |
| Admission control | Kyverno (signature + attestation verification) | SLSA enforcement (18) |
| Observability | Grafana stack or EU-tenancy SaaS; OCSF-normalised to SIEM | Residency of the "boring tier" (02, 22) |
| IaC | Terraform/OpenTofu, module-per-concern, provider isolated | Portability, reviewability (04) |

## 4. The document access path (the critical flow)

```
1. User authenticates          IdP: FIDO2 + device compliance + geo
2. API gateway                 validates token, rate limits, extracts TenantContext
3. Policy sidecar (Cedar)      PDP #1 — subject/action/resource/context → allow + reason
4. Mesh authz (Linkerd)        PDP #2 — only api-gateway may call document-service
5. document-service            PDP #3 — repository enforces tenant scoping
6. Aurora RLS                  PDP #4 — row-level policy on app.tenant_id
7. KMS decrypt                 PDP #5 — key policy requires EncryptionContext.tenant_id match
8. Nitro Enclave (phase 2)     plaintext exists only inside attested enclave
9. Render + watermark          server-side; presigned GET, TTL 60s, single use
10. Audit event                synchronous durable write before response for RESTRICTED
```

Five independent enforcement points. A single-layer bug does not produce cross-tenant disclosure.

## 5. The AI assessment path

```
Document (already stored, tenant CMK)
   ▼ extract text (sandbox-processing account, no network, no credentials)
   ▼ chunk + embed (pgvector, in-region)
   ▼ retrieve minimal relevant spans
   ▼ pseudonymise named entities (reversible map, tenant-key encrypted, in-region)
   ▼ assemble prompt: immutable signed system prompt + delimited untrusted-data block
   ▼ Bedrock (Claude, eu-central-1) — schema-constrained output
   ▼ validate: JSON schema + deterministic citation-offset verification + injection signatures
   ▼ re-identify entities
   ▼ human reviewer approval (named, logged, override rationale captured)
   ▼ evidence-service: manifest + Ed25519 signature + daily Merkle root + QTSP timestamp
   ▼ S3 evidence bucket (Object Lock COMPLIANCE) + CRR to eu-north-1
```

## 6. Data classification to control mapping

| Class | Key | Storage | AI | Access | Retention |
|---|---|---|---|---|---|
| `PUBLIC` | Platform CMK | primary | Yes | Any authenticated | Standard |
| `INTERNAL` | Tenant CMK | primary | Yes | Tenant users | Standard |
| `CONFIDENTIAL` | Tenant CMK | primary | Yes | Role-based | 5–7y policy |
| `RESTRICTED` | Tenant CMK + per-doc DEK | primary, no data-key cache | Pseudonymised, opt-in | Step-up + purpose | Policy + hold |
| `PRIVILEGED` | Tenant CMK, separate alias | primary | **No** | Named individuals | Policy + hold |
| `EVIDENCE` | Evidence CMK | evidence bucket, Object Lock COMPLIANCE | N/A | Read-only, all access logged | 7y, immutable |

## 7. Residency boundary

Everything below is inside the EU boundary and none of it has a non-EU path:

Compute, storage, keys, backups, DR, AI inference, search, embeddings, logs, metrics, traces, error tracking, email sending, CI runners (Zone 2/3), session recordings, evidence, and the CDN for authenticated content. Sub-processors are enumerated in a machine-readable attestation endpoint for customer DORA registers.

Outside the boundary, by design and disclosed: source code repositories (GitHub — IP, not customer data), Zone 1 CI (untrusted PR validation on synthetic data), and the Indian development entity (no production personal data access, SCCs Module 3 + TIA + supplementary measures).

## 8. Scaling and cost shape

| Component | Cost driver | Control |
|---|---|---|
| Aurora Global Database | Second cluster + replication I/O | Largest DR line item; justified by T1 RPO |
| KMS | Per-tenant keys (~€1/key/month) + requests | Class-based data-key caching |
| S3 + Object Lock | 7-year evidence growth | Lifecycle to Glacier Instant/Flexible (lock preserved) |
| Bedrock | Tokens per assessment | Minimal-span retrieval; pseudonymisation does not increase tokens materially |
| SIEM | Per-GB ingestion | Tiered retention; audit events to cheap immutable storage, not the SIEM |
| Network Firewall | Endpoint-hours + data processing | Single egress point per VPC |
| Nitro Enclaves | Instance sizing | Phase 2; scoped to key-broker and decryption only |

Model SIEM and evidence storage at **5× projected volume** before committing budget — these are the two components that surprise teams.

## 9. What this architecture deliberately does not do

- **No multi-cloud.** Portability is maintained; active multi-cloud is rejected (ADR-002) because it roughly doubles operational surface and degrades every control through inconsistency.
- **No active-active multi-region.** Warm standby only; cross-region active-active PostgreSQL introduces correctness risk exceeding its availability benefit.
- **No self-hosted frontier model at launch.** Managed inference with a self-hosted fallback for degraded mode and Tier 3 customers (ADR-004).
- **No standing human production access.** There is no "on-call has read access" exception.
- **No fallback encryption key.** Key unavailability means data unavailability, by design (DD-20-07).
