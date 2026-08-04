# 33 — Architecture Diagrams

Mermaid source. Renders in GitHub, GitLab, VS Code, Obsidian and most documentation tooling.

## D1 — System context

```mermaid
graph TB
    subgraph EXT["External"]
        CU["Compliance Officer<br/>(EU CASP staff)"]
        AU["External Auditor /<br/>Competent Authority"]
        IDP["Customer IdP<br/>SAML / OIDC / SCIM"]
    end

    subgraph EU["EU Boundary — eu-central-1 / eu-north-1"]
        PLAT["Compliance Platform"]
        BR["Amazon Bedrock<br/>Claude, EU-only inference"]
        QTSP["EU QTSP<br/>qualified timestamps"]
    end

    subgraph IN["India — Zone D"]
        DEV["Developers<br/>synthetic data only<br/>no production access"]
    end

    CU -->|"FIDO2 + device trust"| PLAT
    AU -->|"scoped, time-boxed<br/>auditor role"| PLAT
    IDP -.->|"federation"| PLAT
    PLAT -->|"pseudonymised spans"| BR
    PLAT -->|"RFC 3161 timestamp<br/>on daily Merkle root"| QTSP
    DEV -.->|"code only, via CI<br/>no data path"| PLAT

    style IN fill:#4a1010,stroke:#c04040,color:#fff
    style EU fill:#0d2818,stroke:#2e7d4f,color:#fff
    style EXT fill:#1a1a2e,stroke:#4a4a7a,color:#fff
```

## D2 — Network and account topology

```mermaid
graph TB
    NET["Internet"] --> R53["Route 53<br/>DNSSEC + query logs"]
    R53 --> CF["CloudFront + WAF + Shield"]
    CF --> ALB["ALB<br/>public subnet"]

    subgraph PROD["Account: prod — VPC 10.30.0.0/16, 3 AZs"]
        ALB --> ING["EKS ingress<br/>Envoy"]
        subgraph APP["private-app · egress via Network Firewall allowlist"]
            ING --> MESH["Linkerd mesh — mTLS, SPIFFE identities"]
            MESH --> API["api-gateway"]
            MESH --> DOC["document-service"]
            MESH --> ASM["assessment-service"]
            MESH --> EVD["evidence-service"]
            MESH --> KB["key-broker<br/>(Nitro Enclave, phase 2)"]
        end
        subgraph DATA["private-data · NO internet route"]
            PG[("Aurora PostgreSQL<br/>RLS forced, IAM auth")]
            CACHE[("ElastiCache")]
            OS[("OpenSearch<br/>per-tenant index")]
        end
        subgraph VPE["private-endpoints"]
            EP["VPC endpoints:<br/>S3 · KMS · Bedrock · SM · ECR · STS"]
        end
        APP --> DATA
        APP --> VPE
    end

    VPE --> S3[("S3<br/>quarantine · primary<br/>evidence (Object Lock)<br/>derivatives · forensic")]
    VPE --> KMS["AWS KMS<br/>per-tenant CMK"]
    VPE --> BED["Bedrock<br/>eu-central-1"]

    subgraph OTHER["Other accounts"]
        LOG["log-archive<br/>write-only, delete denied"]
        BAK["backup<br/>Vault Lock compliance"]
        SEC["security-tooling"]
        SND["sandbox-processing<br/>no creds, no egress"]
        SHR["shared-services<br/>ECR, CI runners, egress FW"]
    end

    PROD -.->|"write only"| LOG
    PROD -.->|"AWS Backup push"| BAK
    PROD -.->|"telemetry"| SEC
    S3 -.->|"quarantine events"| SND

    style DATA fill:#2a1a3e,stroke:#7a5aaa,color:#fff
    style PROD fill:#0d1f2d,stroke:#2a6f97,color:#fff
    style OTHER fill:#1f1f1f,stroke:#666,color:#fff
```

## D3 — Document access path (five enforcement points)

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant IDP as IdP
    participant GW as api-gateway
    participant PDP as Cedar sidecar
    participant DS as document-service
    participant DB as Aurora (RLS)
    participant K as KMS
    participant S as S3
    participant AL as Audit log

    U->>IDP: authenticate (FIDO2 + device posture)
    IDP-->>U: token (roles, tenant, MFA level)
    U->>GW: GET /documents/{id}?purpose=review
    GW->>GW: validate token, rate limit, build TenantContext
    GW->>PDP: PEP-1 authorise(subject, action, resource, context)
    PDP-->>GW: allow + policy_version + reason
    GW->>DS: PEP-2 mesh mTLS — SPIFFE identity check
    DS->>DB: PEP-3 repository tenant scoping
    DB->>DB: PEP-4 row-level security on app.tenant_id
    DB-->>DS: metadata + wrapped DEK
    DS->>K: PEP-5 Decrypt(EncryptionContext: tenant_id=T)
    K-->>DS: plaintext DEK (fails if context mismatch)
    DS->>S: fetch ciphertext
    DS->>DS: decrypt, render, watermark (enclave in phase 2)
    DS->>AL: synchronous durable write (RESTRICTED)
    AL-->>DS: sealed
    DS-->>U: presigned GET, TTL 60s, single use
```

## D4 — Document upload pipeline

```mermaid
flowchart LR
    A["Client"] -->|"presigned PUT<br/>TTL 5 min, size bounded"| Q[("S3 quarantine")]
    Q -->|"S3 event"| SQS[["SQS"]]
    SQS --> SC["Scanner<br/>sandbox-processing account<br/>no credentials · no egress · ephemeral"]

    SC --> MB{"Magic bytes<br/>match declared type?"}
    MB -->|no| REJ["Reject + log<br/>security event"]
    MB -->|yes| AV{"Multi-engine AV<br/>+ structural checks"}
    AV -->|infected| FOR[("S3 forensic<br/>separate key<br/>90-day retention")]
    AV -->|"error / timeout"| HOLD["Remain in quarantine<br/>alert · manual review<br/>FAIL CLOSED"]
    AV -->|clean| P[("S3 primary<br/>tenant CMK<br/>per-document DEK")]

    P --> DER["Derivation service"]
    DER --> TH[("thumbnails")]
    DER --> TX[("extracted text")]
    DER --> EM[("embeddings — pgvector")]
    DER --> REG[("derivative registry")]

    FOR --> ALERT["Alert security<br/>notify tenant admin<br/>evidence record"]

    style HOLD fill:#4a3010,stroke:#c08040,color:#fff
    style FOR fill:#4a1010,stroke:#c04040,color:#fff
    style SC fill:#2a1a3e,stroke:#7a5aaa,color:#fff
```

## D5 — AI assessment pipeline

```mermaid
flowchart TB
    D[("Stored document<br/>tenant CMK")] --> EX["Extract text<br/>sandboxed, no network"]
    EX --> CH["Chunk + embed<br/>pgvector, in-region"]
    CH --> RT["Retrieve minimal<br/>relevant spans"]
    RT --> PS["Pseudonymise entities<br/>reversible map, tenant-key encrypted"]
    PS --> PA["Assemble prompt<br/>immutable signed system prompt<br/>+ delimited UNTRUSTED data block"]
    PA --> BR["Bedrock — Claude<br/>eu-central-1 · EU-only inference<br/>no training · no retention<br/>schema-constrained output"]
    BR --> V{"Validation"}
    V -->|"schema fail"| RJ["Reject · retry · alert"]
    V -->|"citation offset<br/>not found in source"| RJ
    V -->|"injection signature"| RJ
    V -->|pass| RI["Re-identify entities"]
    RI --> HR{"Named human reviewer"}
    HR -->|reject| FB["Feedback loop<br/>logged with rationale"]
    HR -->|approve| EV["evidence-service:<br/>manifest + Ed25519 signature"]
    EV --> MK["Daily Merkle root"]
    MK --> TS["QTSP qualified timestamp"]
    TS --> ES[("S3 evidence<br/>Object Lock COMPLIANCE<br/>+ CRR to eu-north-1")]

    style BR fill:#1a2f4a,stroke:#4a8fc0,color:#fff
    style HR fill:#2d3a1a,stroke:#7aa04a,color:#fff
    style ES fill:#0d2818,stroke:#2e7d4f,color:#fff
    style RJ fill:#4a1010,stroke:#c04040,color:#fff
```

## D6 — Key hierarchy

```mermaid
graph TB
    HSM["AWS KMS — FIPS 140-3 HSMs<br/>eu-central-1"]

    HSM --> PK["Platform CMK"]
    HSM --> AK["Audit CMK<br/>deletion denied to all principals"]
    HSM --> BK["Backup CMK<br/>multi-region · deletion denied"]
    HSM --> SK["Evidence signing key<br/>sign-only · non-exportable"]
    HSM --> TK["Per-tenant CMK<br/>tenant-{id}"]

    TK --> DEK["Per-document DEK<br/>wrapped, stored with ciphertext<br/>AAD = tenant_id + doc_id + class"]
    TK --> FDK["Field DEK<br/>national IDs, wallet addresses"]
    TK --> HK["Blind-index HMAC key<br/>per tenant"]

    subgraph T2["Tier 2 — customer-managed"]
        CKMS["Customer AWS KMS<br/>cross-account grant<br/>EncryptionContext: tenant_id"]
    end
    subgraph T3["Tier 3 — HYOK"]
        XKS["Customer HSM via<br/>KMS External Key Store<br/>key material never in AWS"]
    end

    DEK -.->|"tier 2 tenants"| CKMS
    DEK -.->|"tier 3 tenants"| XKS

    style T3 fill:#0d2818,stroke:#2e7d4f,color:#fff
    style T2 fill:#1a2f4a,stroke:#4a8fc0,color:#fff
```

## D7 — Environment zones and the cross-border boundary

```mermaid
graph LR
    subgraph ZD["Zone D — India"]
        DEVW["Developer workstations<br/>MDM · EDR · managed Claude Code<br/>synthetic data only"]
        GIT["Source code"]
    end

    subgraph ZS["Zone S — EU staging"]
        STG["Full architectural parity<br/>synthetic / anonymised data only<br/>SSO + FIDO2 access"]
    end

    subgraph ZP["Zone P — EU production"]
        PRD["Real customer data<br/>NO standing human access<br/>pipeline identity only"]
        BG["Break-glass:<br/>dual EU approval · EU VDI<br/>egress disabled · recorded · ≤4h"]
    end

    DEVW --> GIT
    GIT -->|"CI: Zone 1 hosted<br/>Zone 2/3 EU ephemeral"| STG
    STG -->|"same signed artefact digest<br/>2 approvers"| PRD
    DEVW -.->|"EXCEPTIONAL ONLY"| BG
    BG -.-> PRD

    style ZD fill:#4a1010,stroke:#c04040,color:#fff
    style ZS fill:#3a3a1a,stroke:#a0a040,color:#fff
    style ZP fill:#0d2818,stroke:#2e7d4f,color:#fff
    style BG fill:#4a3010,stroke:#c08040,color:#fff
```

## D8 — CI/CD trust zones

```mermaid
flowchart LR
    subgraph Z1["Zone 1 — UNTRUSTED"]
        PR["Pull request"] --> V1["GitHub-hosted runners<br/>read-only token · NO credentials<br/>lint · test · SAST · SCA · IaC · secrets"]
    end
    subgraph Z2["Zone 2 — TRUSTED BUILD"]
        M["Merge to main<br/>2 reviewers · signed commits"] --> B["Self-hosted ephemeral runner<br/>eu-central-1 · OIDC to ci-build role"]
        B --> ART["Signed image + SBOM<br/>+ SLSA provenance<br/>+ scan attestation → ECR"]
    end
    subgraph Z3["Zone 3 — DEPLOY"]
        ART --> STG2["Argo CD → staging<br/>Kyverno verifies attestations"]
        STG2 --> APR{"2 approvers"}
        APR --> CAN["Canary 5% → 25% → 100%<br/>auto-rollback on SLO breach"]
        CAN --> EVD2["Deployment evidence record"]
    end
    V1 -.->|"never runs in Zone 2/3"| Z2

    style Z1 fill:#4a1010,stroke:#c04040,color:#fff
    style Z2 fill:#3a3a1a,stroke:#a0a040,color:#fff
    style Z3 fill:#0d2818,stroke:#2e7d4f,color:#fff
```

## D9 — Evidence integrity chain

```mermaid
graph LR
    E1["Evidence n-1<br/>manifest hash H(n-1)"] --> E2["Evidence n<br/>prev_hash = H(n-1)<br/>hash = H(n)"]
    E2 --> E3["Evidence n+1<br/>prev_hash = H(n)"]
    E2 --> MT["Daily Merkle tree<br/>over all manifests sealed today"]
    E3 --> MT
    MT --> RT["Merkle root"]
    RT --> SG["Ed25519 signature<br/>KMS sign-only key"]
    SG --> QT["RFC 3161 qualified timestamp<br/>EU QTSP on Trusted List"]
    QT --> PUB["Published append-only root feed<br/>customers verify inclusion independently"]
    QT --> OL[("S3 Object Lock COMPLIANCE<br/>+ CRR to eu-north-1")]

    VER["evidence-verify CLI<br/>open source"] -.->|"validates digests, signature,<br/>timestamp, chain, inclusion"| PUB

    style QT fill:#0d2818,stroke:#2e7d4f,color:#fff
    style OL fill:#1a2f4a,stroke:#4a8fc0,color:#fff
```

## D10 — Disaster recovery topology

```mermaid
graph TB
    subgraph P["PRIMARY — eu-central-1"]
        PE["EKS full scale"]
        PA[("Aurora PostgreSQL<br/>Multi-AZ")]
        PS[("S3 buckets")]
        PK["KMS CMKs"]
    end
    subgraph S["SECONDARY — eu-north-1 (warm standby)"]
        SE["EKS minimum nodes<br/>deployments at replica 0-1"]
        SA[("Aurora Global DB<br/>secondary · lag < 1s")]
        SS[("S3 CRR destination<br/>Object Lock preserved")]
        SK["Multi-region replica keys<br/>backup + evidence"]
    end
    subgraph B["ACCOUNT: backup"]
        BV["AWS Backup vaults<br/>daily/weekly: governance<br/>monthly/annual: VAULT LOCK compliance"]
    end
    subgraph V["ACCOUNT: verification"]
        VR["Daily automated restore<br/>integrity + decrypt + chain assertions<br/>auto-destroyed"]
    end

    PA -->|"< 1s"| SA
    PS -->|"CRR · RTC 15 min"| SS
    PK --> SK
    P -->|"AWS Backup push<br/>no delete path back"| BV
    BV --> VR
    R53["Route 53 health-check failover<br/>MANUAL dual approval · 15-min decision SLA"] -.-> P
    R53 -.-> S

    style B fill:#2a1a3e,stroke:#7a5aaa,color:#fff
    style S fill:#1f1f1f,stroke:#666,color:#fff
    style V fill:#3a3a1a,stroke:#a0a040,color:#fff
```

## D11 — Data classification and lifecycle

```mermaid
stateDiagram-v2
    [*] --> Quarantine: presigned upload
    Quarantine --> Rejected: type mismatch / infected
    Quarantine --> Classified: scan clean
    Classified --> Active: classification assigned<br/>(PUBLIC → PRIVILEGED)
    Active --> Active: access · preview · derive
    Active --> LegalHold: hold applied (dual approval)
    LegalHold --> Active: hold released (dual approval)
    Active --> SoftDeleted: user deletion request
    SoftDeleted --> Active: restore within grace window
    SoftDeleted --> CryptoShredded: DEK destroyed
    Active --> RetentionExpired: max_until reached
    RetentionExpired --> Purged: deletion saga + certificate
    CryptoShredded --> Purged: ciphertext lifecycle expiry
    Rejected --> [*]
    Purged --> [*]

    note right of LegalHold
        Object Lock legal hold
        No expiry · audited
        Visible to tenant
    end note
    note right of CryptoShredded
        Satisfies GDPR Art. 17
        even where backups
        cannot be selectively purged
    end note
```

## D12 — Incident response and regulatory clocks

```mermaid
flowchart TB
    DET["Detection<br/>SIEM · honeytoken · alert"] --> TRI["Triage<br/>severity + scope"]
    TRI --> CLS["Regulatory classification engine"]
    CLS --> D1{"DORA<br/>Del. Reg. 2024/1772<br/>major incident?"}
    CLS --> D2{"GDPR Art. 33<br/>risk to rights<br/>and freedoms?"}
    CLS --> D3{"NIS2 Art. 23<br/>significant<br/>incident?"}

    D1 -->|yes| CN["Notify affected customers<br/>≤ 2 HOURS from confirmation<br/>(so they can meet their deadlines)"]
    D2 -->|yes| SA["Supervisory authority<br/>≤ 72 HOURS"]
    D2 -->|"high risk"| DS["Data subjects<br/>without undue delay<br/>(unless encrypted + keys safe)"]
    D3 -->|yes| CS["National CSIRT<br/>early warning ≤ 24h<br/>notification ≤ 72h<br/>final ≤ 1 month"]

    CN --> CONT["Containment · eradication · recovery"]
    SA --> CONT
    CS --> CONT
    CONT --> PIR["Blameless retrospective<br/>DORA Art. 13 learning evidence"]
    PIR --> TM["Threat model updated<br/>'was this modelled?'"]

    style CN fill:#4a3010,stroke:#c08040,color:#fff
    style SA fill:#4a1010,stroke:#c04040,color:#fff
    style CS fill:#4a1010,stroke:#c04040,color:#fff
```
