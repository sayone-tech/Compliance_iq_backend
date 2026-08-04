# Reference Cloud Architecture

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

## 0. What the PRD fixes

| Fixed | Reference |
|---|---|
| Cloud provider is **AWS** | TI-01 |
| Deployed inside an **EU-resident data centre** | NFR-03, TI-01 |
| On an account **owned solely by the Client**, not SayOne | TI-01 |
| **Two applications**: the Firm Application and the Platform Admin Portal, both fully operational, both inside the fixed fee | PRD §1.1, §16 baseline note |
| Multi-tenant isolation from day one | NFR-01 |
| AES-256 at rest, TLS 1.3 in transit, per-firm key | NFR-02 |
| Immutable audit log, no admin delete or modify | NFR-04, FR-13 |
| Six-year minimum retention, non-deletable | NFR-07, PRD §2 |
| Browser-based, no mobile app in v1 | NFR-10 |
| Dashboard within two seconds; up to 100 concurrent users per firm | NFR-05 |

**Not fixed, and therefore not selected in this document:** the region, the compute platform, the database engine, the service mesh, the authorisation engine, the search technology, the AI inference provider, and whether a second region exists. Each is marked **[OPEN]** below with the criteria for choosing.

## 1. Account topology **[PROPOSED]**

Within the Client-owned AWS organisation:

| Account | Purpose | Notable controls |
|---|---|---|
| `management` | Organisation, policies, billing. No workloads | Root credentials under agreed custody; break-glass only |
| `security-tooling` | Detection services, monitoring ingestion | Read-only into other accounts |
| `log-archive` | Immutable audit log and sealed record storage | **Write-only from other accounts; delete denied to every principal**; write-once retention |
| `backup` | Backup vaults | No trust path from production; immutable retention lock |
| `shared-services` | Registries, egress control, ephemeral CI runners | No client data |
| `prod` | Both applications' production workloads | Zero standing human access |
| `staging` | Pre-production, full architectural parity | Synthetic data only |
| `dev` | Development | Synthetic data only |
| `sandbox-processing` | Untrusted file parsing, OCR, media handling | No credentials, no network egress |
| `verification` | Automated restore verification | Ephemeral, auto-destroyed |

Organisation-wide guardrails: deny non-EU regions; deny long-lived access-key creation; deny disabling audit, configuration and threat-detection services; resource-side policies restricting storage, key and token access to organisation principals and EU paths.

**Open:** how these accounts are provisioned into, and handed over inside, an account structure the Client owns solely (TI-01). This is an operational and contractual question. **[OPEN]**

## 2. Production data plane **[PROPOSED]**

```
                                Internet
                                    │
                    ┌───────────────┴────────────────┐
                    │  DNS (signed, query logging)    │
                    └───────────────┬────────────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    │  CDN (TLS 1.3 — NFR-02)         │
                    │  WAF + rate limiting            │
                    └───────────────┬────────────────┘
                                    │
╔═══════════════════ Production network, 3 availability zones ═══════════════════╗
║  PUBLIC             │  Load balancer, NAT                                       ║
║ ────────────────────┼────────────────────────────────────────────────────────── ║
║  PRIVATE-APP        │  Firm Application services                                ║
║  (egress via the    │    ├── api gateway            (authn, rate limit)          ║
║   controlled path   │    ├── document service       (firm scoping, evidence)     ║
║   only)             │    ├── testing service        (executions, findings,       ║
║                     │    │                           remediation, reports)       ║
║                     │    ├── wsp-mapping service    (FR-30/31 pipeline)          ║
║                     │    ├── record-sealing service (immutability, chaining)     ║
║                     │    ├── notification service   (email + in-platform only)   ║
║                     │  Platform Admin Portal services                            ║
║                     │    ├── portal api             (separate login, PRD §4)     ║
║                     │    ├── regulatory-content     (SA-01/02/04 versioning)     ║
║                     │    └── reg-monitoring         (SA-03 feeds + manual entry) ║
║                     │  Shared: authorisation policy evaluation                   ║
║ ────────────────────┼────────────────────────────────────────────────────────── ║
║  PRIVATE-DATA       │  Relational store (row-level security forced, identity     ║
║  NO internet route  │  authentication, audit extension)                          ║
║                     │  Cache (encrypted, no persistence of personal data)        ║
║                     │  Search index (per-firm, firm key)                         ║
║ ────────────────────┼────────────────────────────────────────────────────────── ║
║  PRIVATE-ENDPOINTS  │  Private endpoints: object storage, key service, secrets,  ║
║                     │  registry, token service, logging, queues, AI inference    ║
╚════════════════════════════════════════════════════════════════════════════════╝
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
   Object storage              Key service                 AI inference
   quarantine / primary /      per-firm keys (NFR-02),     EU-resident, no training,
   evidence (write-once) /     audit key, backup key,      no retention.
   derivatives / forensic      sealing key                 **Provider [OPEN]**
```

**Note the Portal.** PRD §4 makes the Platform Admin Portal a separate login and interface that firm users never see. Architecturally that means a separate ingress path, a separate identity plane, and an authorisation boundary that must be enforced in the policy layer — not by deploying two front-ends against a shared, permissive API. The Portal's permitted visibility of firm data is **[OPEN]** (SA-06, SA-08).

## 3. Component selection criteria **[OPEN — none of these is selected]**

| Concern | Selection criteria | Notes |
|---|---|---|
| Region | Every dependent service available; three availability zones; write-once object retention and key-service features needed for NFR-04/NFR-07; latency to EU CASPs; Client preference | `data-residency` |
| Compute platform | Supports hardened workload isolation and default-deny network policy; operationally sustainable for the team size; portable | `network-security`, `zero-trust-architecture` |
| Relational store | Row-level security or an equivalent enforced tenant predicate; identity-based authentication; encryption with a customer-managed key; point-in-time recovery | `document-confidentiality` |
| Object storage | Per-object encryption under a firm key; **write-once retention that no principal can override** | `secure-media-storage`, `immutable-evidence-retention` |
| Search | In-region; per-firm isolation; encryptable with the firm key; rebuildable from source | `document-confidentiality`, `secure-backups` |
| Key service | Certified hardware modules; per-key policies with encryption-context conditions; automatic rotation retaining prior versions; deletion deniable by policy | `key-management` |
| Authorisation | Versioned, centrally authored, unit-testable, evaluated per request | `identity-and-access-management` |
| Workforce identity | Conditional access, phishing-resistant factors, provisioning automation | `identity-and-access-management` |
| AI inference | EU-resident; no training on inputs or outputs; no provider retention; contractual change notice; measured accuracy against the §6.2 verification vectors; cost per mapping run | `ai-governance` |
| Egress control | Hostname allowlisting; per-connection logging; highly available | `network-security` |
| CI/CD | Federated short-lived credentials; ephemeral runners; artefact signing and admission verification | `supply-chain-security`, `secure-cicd` |
| Observability | EU-hosted or contractually EU-only; supports redaction at source | `data-residency`, `audit-logging` |
| Infrastructure as code | Provider isolated behind thin interfaces for portability | `data-residency`, `secure-sdlc` |

## 4. The evidence access path — five enforcement points **[PROPOSED]**

```
1. User authenticates       Email + password + phone-based second factor (FR-11)
2. API gateway              Validates session, rate limits, builds firm context
3. Authorisation layer      PEP-1 — subject / action / resource / context → allow + reason
4. Service identity         PEP-2 — only the gateway may call the document service
5. Document service         PEP-3 — repository enforces firm scoping
6. Database                 PEP-4 — row-level policy on the firm identifier
7. Key service              PEP-5 — key policy requires a matching firm encryption context
8. Render + watermark       Server-side; signed GET, short TTL, single use
9. Audit event              Synchronous durable write before response (FR-13)
```

A single-layer bug does not produce cross-firm disclosure. That redundancy is the concrete implementation of NFR-01.

## 5. The WSP mapping path **[PROPOSED — see `ai-governance`]**

```
WSP upload (.docx / PDF / scanned PDF — FR-30)
   ▼ malware scan and structural checks (sandbox-processing account)
   ▼ store (object storage, firm key — NFR-02)
   ▼ text extraction incl. OCR (in-region, sandboxed, no network)
   ▼ chunk and index (in-region, firm-key encrypted)
   ▼ retrieve minimal relevant spans
   ▼ pseudonymise named entities (reversible, in-region)
   ▼ prompt: versioned system prompt + delimited UNTRUSTED WSP block
   ▼ EU-resident inference — schema-constrained output          [provider OPEN]
   ▼ validate: schema + cited span exists at the stated offset + injection signatures
   ▼ re-identify entities
   ▼ compliance officer confirms or adjusts                     [FR-31]
   ▼ two independent senior approvers, policy author excluded   [FR-32]
   ▼ mapping record; full version history, nothing overwritten  [FR-37]
   ▼ accuracy measured against the verification vectors ≥ 85%   [PRD §6.2]
```

## 6. Classification to control mapping **[PROPOSED — see `document-confidentiality`]**

| Class | Key | Storage | AI eligible | Access | Retention |
|---|---|---|---|---|---|
| `PUBLIC` | Platform key | primary | Not applicable | Any authenticated user | Standard |
| `INTERNAL` | Firm key | primary | Not applicable | Firm users | Standard |
| `CONFIDENTIAL` | Firm key | primary; sealed copy for reports and results | WSP only, for FR-31 | Role-based | **≥ 6 years, non-deletable** |
| `RESTRICTED` | Firm key + per-object data key | primary; no data-key caching | **No** | Step-up + purpose | **≥ 6 years, non-deletable** |
| `AUDIT` | Audit key | log-archive, write-once | No | Read-only, all access logged | **≥ 6 years, immutable** |

## 7. Residency boundary **[PRD REQUIRED — NFR-03]**

Inside the EU boundary, with no non-EU path: compute, storage, keys, backups, any recovery location, AI inference, search, extracted text and OCR output, logs, metrics, traces, error tracking, email sending, CI runners for build and deploy, session recordings, sealed records, and the content delivery path for authenticated content.

Outside the boundary, by design and requiring disclosure: source code hosting if a non-EU provider is used (the Client's IP under CC-03, not client personal data), and untrusted pull-request validation running against synthetic data. **Where development, support and administration are performed is [OPEN]** — see `cross-border-data-processing`.

## 8. Cost shape **[PROPOSED]**

| Component | Cost driver | Control |
|---|---|---|
| Object storage with write-once retention | Six-plus years of growth, including video evidence (FR-24) | Lifecycle transition to colder classes preserving the retention lock; the NFR-11 file-size ceiling |
| Key service | Per-firm keys plus request volume | Bounded data-key caching |
| Relational store | Transaction volume, and any replication if a second region is used | Depends on the unresolved recovery decision (`disaster-recovery`) |
| AI inference | Tokens per mapping run; re-runs are automatic on each new WSP version (§6.3) | Minimal-span retrieval; measure cost per run against the 85% accuracy bar |
| Monitoring | Ingestion volume | Tiered retention; audit events to cheap immutable storage |
| Egress control | Endpoint hours plus data processed | Single egress point per network |

Model object storage and monitoring at multiples of projected volume before committing budget — these are the two components that surprise teams, and the six-year non-deletable requirement means storage only grows.

## 9. What this architecture deliberately does not do

- **No multi-cloud.** The PRD selects AWS (TI-01). Portability is maintained as a design discipline; active multi-cloud is not proposed.
- **No standing human production access.** There is no "on-call has read access" exception (`cross-border-data-processing`).
- **No deletion path for protected records**, for any principal (NFR-04, NFR-07).
- **No customer-managed key tiers, sovereignty tiers or security-differentiated pricing.** Pricing is seat-based per CC-01 (`customer-managed-encryption`).
- **No self-registration.** Accounts are invitation-only (FR-12); the marketing site captures leads only (MKT-02).
- **No public API in v1.** TI-05 keeps it a later phase.
- **No AI decision-making.** The single AI feature suggests WSP-to-rule mappings; humans confirm them (FR-31) and two seniors approve them (FR-32).
