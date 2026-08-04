# Architecture Diagrams

> **Baseline:** PRD v4.0. Diagrams show the **PRD-fixed** elements as concrete and everything else as role-labelled rather than product-labelled — region, compute platform, database engine, mesh, policy engine and AI provider are all unselected. See `reference-cloud-architecture` §3.

Mermaid source. Renders in GitHub, GitLab, VS Code and most documentation tooling.

**Every diagram below maps to a confirmed MVP security scope item.** Diagrams whose subject sits outside that scope were removed — see [What was removed](#what-was-removed) at the end.

| # | Diagram | Confirmed scope item it serves |
|---|---|---|
| D1 | System context | EU-only storage · AWS · Client-owned account · MFA · EU residency for AI inference |
| D2 | Account topology and data plane | AWS · Client-owned account · multi-tenant isolation · immutable audit log |
| D3 | Evidence access path — layered tenant isolation | Multi-tenant isolation · per-tenant keys · least-privilege roles · immutable audit logging |
| D4 | Upload pipeline | Secure document upload, malware inspection, sandboxed parsing |
| D5 | WSP mapping pipeline | Human approval of AI mappings · prompt-injection and hallucination controls · EU residency for inference |
| D6 | Key hierarchy | Per-tenant encryption keys · AES-256 at rest · non-deletable records |
| D7 | CI/CD trust zones and environment data rules | Secure SDLC · secrets management · vulnerability scanning · supply-chain controls |
| D8 | Record integrity chain | Immutable audit logging · non-deletable evidence and signed-off records |
| D9 | Backup and recovery topology | Secure backups and tested recovery (SLA/RTO/RPO remain proposals) |
| D10 | Record lifecycle | Non-deletable evidence and signed-off records |
| D11 | Incident handling | Incident monitoring and customer notification supporting DORA obligations |

---

## D1 — System context

```mermaid
graph TB
    subgraph EXT["External"]
        FU["Firm users<br/>8 system roles (the PRD's system-role table)<br/>invitation-only, phone MFA"]
        PA["Platform Admin Portal team<br/>separate login (the PRD's Platform Admin Portal section)"]
        REG["Regulatory sources<br/>EUR-Lex · EBA · ESMA<br/>RSS / official API only (the regulatory monitoring requirement)"]
    end

    subgraph EU["EU boundary — AWS, EU data centre, Client-owned account (the confirmed cloud decision, the EU residency requirement)"]
        FIRM["Firm Application"]
        PORTAL["Platform Admin Portal"]
        INF["AI inference<br/>EU-resident · no training · no retention<br/>PROVIDER NOT SELECTED"]
        MAIL["Email delivery<br/>EU sending infrastructure"]
    end

    FU -->|"email + password + phone second factor (the phone-based second factor requirement)"| FIRM
    PA -->|"separate login"| PORTAL
    PORTAL -->|"publishes test procedure versions (the publication review requirement)"| FIRM
    REG -.->|"feeds, human-reviewed before publication"| PORTAL
    FIRM -->|"WSP spans only, pseudonymised"| INF
    FIRM -->|"report + alert notifications (the report distribution requirement, the PRD's notifications section)"| MAIL
    PORTAL -.->|"firm data visibility — BOUNDARY UNRESOLVED (the Portal firm-visibility statement/the Portal system settings requirement)"| FIRM

    style EU fill:#0d2818,stroke:#2e7d4f,color:#fff
    style EXT fill:#1a1a2e,stroke:#4a4a7a,color:#fff
    style INF fill:#3a3a1a,stroke:#a0a040,color:#fff
```

## D2 — Account topology and data plane

Account separation is what makes "no admin can delete the audit log" (the immutable audit requirement) and "no deletion path" (the non-deletable retention requirement) structural rather than procedural. Network-layer detail — subnet tiering, egress allowlisting, WAF tuning — is in [`supporting-topics/network-security`](supporting-topics/network-security.md).

```mermaid
graph TB
    NET["Internet"] --> EDGE["Edge: DNS + CDN + WAF<br/>TLS 1.3 (the encryption requirement)"]

    subgraph PROD["Account: prod — EU region (NOT SELECTED)"]
        EDGE --> AUTHZ["Per-request authorisation<br/>versioned policy, every decision audited (the automatic role enforcement requirement)"]
        subgraph APP["Application tier · egress via controlled allowlist only"]
            AUTHZ --> API["api gateway"]
            AUTHZ --> DOC["document service"]
            AUTHZ --> TST["testing service"]
            AUTHZ --> WSP["wsp-mapping service"]
            AUTHZ --> SEAL["record-sealing service"]
            AUTHZ --> PORT["portal api (separate ingress)"]
        end
        subgraph DATA["Data tier · NO internet route"]
            DB[("Relational store<br/>row-level security forced<br/>identity auth")]
            CACHE[("Cache")]
            IDX[("Search index<br/>per-firm, firm key")]
        end
        APP --> DATA
        APP --> VPE["Private endpoints:<br/>object storage · key service · secrets ·<br/>registry · logging · inference"]
    end

    VPE --> OBJ[("Object storage<br/>quarantine · primary<br/>evidence (write-once)<br/>derivatives · forensic")]
    VPE --> KMS["Key service<br/>per-firm keys (the encryption requirement)"]
    VPE --> AI["AI inference endpoint<br/>EU-resident"]

    subgraph OTHER["Other accounts in the Client-owned organisation (the confirmed cloud decision)"]
        LOG["log-archive<br/>write-only · delete denied to ALL principals<br/>the immutable audit requirement"]
        BAK["backup<br/>immutable retention lock"]
        SEC["security-tooling"]
        SND["sandbox-processing<br/>no creds · no egress"]
        SHR["shared-services<br/>registry · CI runners · egress control"]
    end

    PROD -.->|"write only"| LOG
    PROD -.->|"push only, no delete path back"| BAK
    PROD -.->|"telemetry"| SEC
    OBJ -.->|"quarantine events"| SND

    style DATA fill:#2a1a3e,stroke:#7a5aaa,color:#fff
    style PROD fill:#0d1f2d,stroke:#2a6f97,color:#fff
    style OTHER fill:#1f1f1f,stroke:#666,color:#fff
    style LOG fill:#0d2818,stroke:#2e7d4f,color:#fff
```

## D3 — Evidence access path: layered tenant isolation

Each numbered check is independent. Any one of them alone prevents cross-firm disclosure — that redundancy is the answer to the tenant isolation requirement. The enforcement-model rationale is in [`supporting-topics/zero-trust-architecture`](supporting-topics/zero-trust-architecture.md); the isolation requirement itself is `document-confidentiality`.

```mermaid
sequenceDiagram
    autonumber
    participant U as Firm user
    participant IDP as Authentication
    participant GW as api gateway
    participant PDP as Authorisation layer
    participant DS as document service
    participant DB as Database (row-level security)
    participant K as Key service
    participant S as Object storage
    participant AL as Audit log

    U->>IDP: email + password + phone second factor (the phone-based second factor requirement)
    IDP-->>U: session (system role, firm)
    U->>GW: GET /evidence/{id}?purpose=test_execution
    GW->>GW: validate session, rate limit, build firm context
    GW->>PDP: check 1 — authorise(subject, action, resource, context)
    PDP-->>GW: allow + policy version + reason
    GW->>DS: check 2 — service identity
    DS->>DB: check 3 — repository firm scoping
    DB->>DB: check 4 — row-level security on firm id
    DB-->>DS: metadata + wrapped data key
    DS->>K: check 5 — decrypt(encryption context: firm id)
    K-->>DS: data key (FAILS on context mismatch)
    DS->>S: fetch ciphertext
    DS->>DS: decrypt, render, watermark
    DS->>AL: synchronous durable write (the permanent audit log requirement)
    AL-->>DS: recorded
    DS-->>U: signed GET, short TTL, single use
```

## D4 — Upload pipeline (the evidence file types the PRD lists, the configurable file-size limit size ceiling)

```mermaid
flowchart LR
    A["Client"] -->|"pre-signed PUT<br/>short TTL, size bounded (the configurable file-size limit)"| Q[("quarantine")]
    Q -->|"event"| SQS[["queue"]]
    SQS --> SC["Scanner<br/>sandbox account<br/>no credentials · no egress · ephemeral"]

    SC --> MB{"Content type matches<br/>declared type and the accepted evidence file type list?"}
    MB -->|no| REJ["Reject + log security event"]
    MB -->|yes| AV{"Multi-engine scan<br/>+ structural checks<br/>+ archive limits (ZIP)<br/>+ media container checks"}
    AV -->|infected| FOR[("forensic<br/>separate key")]
    AV -->|"error / timeout"| HOLD["Stay in quarantine<br/>alert · manual review<br/>FAIL CLOSED"]
    AV -->|clean| P[("primary<br/>firm key + per-object data key")]

    P --> DER["Derivation service"]
    DER --> TH[("previews / transcodes")]
    DER --> TX[("extracted text / OCR (the single WSP upload requirement)")]
    DER --> REG[("derivative registry")]
    P --> EVD[("evidence — write-once retention<br/>NON-DELETABLE, ≥6 years<br/>the non-deletable retention requirement, the PRD's testing workflow step 5")]

    FOR --> ALERT["Alert security<br/>notify Firm Super Admin"]

    style HOLD fill:#4a3010,stroke:#c08040,color:#fff
    style FOR fill:#4a1010,stroke:#c04040,color:#fff
    style EVD fill:#0d2818,stroke:#2e7d4f,color:#fff
```

## D5 — WSP mapping pipeline (the only AI feature)

```mermaid
flowchart TB
    D[("WSP document<br/>.docx / PDF / scanned PDF — The single WSP upload requirement<br/>firm key")] --> EX["Extract text incl. OCR<br/>sandboxed, no network"]
    EX --> CH["Chunk + index<br/>in-region, firm key"]
    CH --> RT["Retrieve minimal relevant spans"]
    RT --> PS["Pseudonymise entities<br/>reversible, in-region"]
    PS --> PA["Assemble prompt<br/>versioned system prompt<br/>+ delimited UNTRUSTED WSP block"]
    PA --> BR["EU-resident inference<br/>no training · no retention<br/>schema-constrained output<br/>PROVIDER NOT SELECTED"]
    BR --> V{"Validation"}
    V -->|"schema fail"| RJ["Reject · retry · log"]
    V -->|"cited span not found at offset"| RJ
    V -->|"injection signature"| RJ
    V -->|pass| RI["Re-identify entities"]
    RI --> HR{"Compliance officer<br/>confirms or adjusts — The advisory AI mapping requirement"}
    HR -->|adjust| OVR["Manual override<br/>VISIBLY TAGGED (the mapping override initiation gap)"]
    HR -->|confirm| TP{"Two independent senior approvers<br/>policy author excluded — The two-person mapping approval requirement"}
    OVR --> TP
    TP -->|approved| MAP[("Mapping record<br/>full version history<br/>nothing overwritten — The permanent WSP version history requirement")]
    MAP --> ACC["Accuracy measured against<br/>verification vectors ≥85% — the PRD's WSP mapping accuracy commitment"]

    style BR fill:#3a3a1a,stroke:#a0a040,color:#fff
    style HR fill:#2d3a1a,stroke:#7aa04a,color:#fff
    style TP fill:#2d3a1a,stroke:#7aa04a,color:#fff
    style MAP fill:#0d2818,stroke:#2e7d4f,color:#fff
    style RJ fill:#4a1010,stroke:#c04040,color:#fff
```

## D6 — Key hierarchy (the encryption requirement)

```mermaid
graph TB
    HSM["Managed key service — certified HSMs<br/>EU region (NOT SELECTED)"]

    HSM --> PK["Platform key"]
    HSM --> AK["Audit key<br/>DELETION DENIED to all principals"]
    HSM --> BK["Backup key<br/>DELETION DENIED"]
    HSM --> SK["Record-sealing key<br/>sign-only · non-exportable"]
    HSM --> TK["Per-firm key — firm-{id}<br/>REQUIRED BY the encryption requirement"]

    TK --> DEK["Per-object data key<br/>wrapped, stored with ciphertext<br/>AAD = firm id + object id + class"]
    TK --> FDK["Field data key"]
    TK --> HK["Blind-index key (per firm)"]

    TK -.->|"deletion BLOCKED while any record<br/>is inside its retention period<br/>(the non-deletable retention requirement / the PRD's data and retention table)"| GUARD["Retention precondition check"]

    style GUARD fill:#4a3010,stroke:#c08040,color:#fff
    style TK fill:#0d2818,stroke:#2e7d4f,color:#fff
```

## D7 — CI/CD trust zones and environment data rules

```mermaid
flowchart LR
    subgraph Z1["Zone 1 — UNTRUSTED"]
        PR["Pull request"] --> V1["Hosted runners<br/>read-only token · NO credentials<br/>lint · test · cross-firm isolation tests ·<br/>immutability tests · SAST · SCA · secret scanning"]
    end
    subgraph Z2["Zone 2 — TRUSTED BUILD"]
        M["Merge<br/>2 reviewers · signed commits"] --> B["Ephemeral EU runner<br/>federated credentials → build role<br/>no client data, no firm key access"]
        B --> ART["Signed artefact + bill of materials<br/>+ provenance + scan attestation"]
    end
    subgraph Z3["Zone 3 — DEPLOY"]
        ART --> STG2["Pre-production<br/>admission verifies attestations<br/>SYNTHETIC DATA ONLY"]
        STG2 --> APR{"2 approvers"}
        APR --> CAN["Progressive rollout<br/>auto-rollback on regression"]
        CAN --> PRDE["Production — real client data<br/>NO standing human access<br/>pipeline identity only"]
        PRDE --> EVD2["Deployment record → immutable store"]
    end
    DEV["Developer workstations<br/>managed device · AI tooling governed<br/>SYNTHETIC DATA ONLY"] --> PR
    DEV -.->|"EXCEPTIONAL ONLY"| BG["Break-glass:<br/>dual approval · EU virtual desktop<br/>egress disabled · recorded · time-boxed"]
    BG -.-> PRDE
    V1 -.->|"never runs in Zone 2/3"| Z2

    style Z1 fill:#4a1010,stroke:#c04040,color:#fff
    style Z2 fill:#3a3a1a,stroke:#a0a040,color:#fff
    style Z3 fill:#0d2818,stroke:#2e7d4f,color:#fff
    style DEV fill:#3a3a1a,stroke:#a0a040,color:#fff
    style BG fill:#4a3010,stroke:#c08040,color:#fff
```

> Where development, support and administration are physically performed is **not stated by the PRD** and is an open question (`open-questions` L-1, detailed in [`supporting-topics/cross-border-data-processing`](supporting-topics/cross-border-data-processing.md)). The synthetic-data and zero-standing-access rules above are worth adopting regardless of the answer.

## D8 — Record integrity chain

```mermaid
graph LR
    E1["Record n-1<br/>manifest hash H(n-1)"] --> E2["Record n<br/>prev_hash = H(n-1)<br/>hash = H(n)"]
    E2 --> E3["Record n+1<br/>prev_hash = H(n)"]
    E2 --> SG["Manifest signature<br/>sign-only key"]
    SG --> OL[("Write-once object retention<br/>NO DELETE PATH FOR ANY PRINCIPAL<br/>the immutable audit requirement · the non-deletable retention requirement")]
    OL --> REP[("Copy outside the primary<br/>failure domain, within the EU")]
    VER["Scheduled internal verification<br/>digests · signature · chain head"] -.-> OL

    FUT["FUTURE (not MVP): external anchoring —<br/>qualified timestamps, published Merkle roots,<br/>distributable verifier"] -.-> OL

    style OL fill:#0d2818,stroke:#2e7d4f,color:#fff
    style FUT fill:#1f1f1f,stroke:#666,color:#fff
```

## D9 — Backup and recovery topology

```mermaid
graph TB
    subgraph P["PRIMARY — EU region (not selected)"]
        PE["Application workloads"]
        PA[("Relational store")]
        PS[("Object storage")]
        PK["Keys"]
    end
    subgraph B["ACCOUNT: backup"]
        BV["Vaults<br/>short cycle: reversible mode<br/>long cycle: IMMUTABLE RETENTION LOCK"]
    end
    subgraph V["ACCOUNT: verification"]
        VR["Automated restore verification<br/>integrity · decryption with the correct firm key ·<br/>chain assertions · auto-destroyed"]
    end
    subgraph S["Secondary EU location — EXISTENCE UNRESOLVED"]
        SS[("Record copies<br/>write-once retention preserved")]
    end

    P -->|"push only, no delete path back"| BV
    BV --> VR
    PS -.->|"record copies (protects the non-deletable retention requirement)"| SS
    NOTE["Recovery architecture, availability SLA and any recovery<br/>time/point targets: PROPOSALS ONLY, NOT COMMITTED<br/>(the open uptime-SLA question, `disaster-recovery`)"]

    style B fill:#2a1a3e,stroke:#7a5aaa,color:#fff
    style S fill:#1f1f1f,stroke:#666,color:#fff
    style NOTE fill:#4a3010,stroke:#c08040,color:#fff
```

## D10 — Record lifecycle

```mermaid
stateDiagram-v2
    [*] --> Quarantine: pre-signed upload
    Quarantine --> Rejected: type mismatch / infected
    Quarantine --> Classified: scan clean
    Classified --> Active: classification assigned
    Active --> Active: access · preview · derive
    Active --> Sealed: attached to a test, result signed off,<br/>or report issued
    Sealed --> Sealed: amendment added on top (the amendment-not-edit requirement)<br/>original never removed
    Active --> LegalHold: hold applied (dual approval)
    Sealed --> LegalHold: hold applied
    LegalHold --> Sealed: hold released (dual approval)
    Rejected --> [*]

    note right of Sealed
        NO DELETION PATH.
        Minimum 6 years (the non-deletable retention requirement).
        End of retention after the
        minimum: OPEN QUESTION.
    end note
    note right of Rejected
        A rejected upload never
        became evidence, so the
        non-deletability rule
        does not attach.
    end note
```

## D11 — Incident handling and customer notification

```mermaid
flowchart TB
    DET["Detection<br/>monitoring · canary · alert"] --> TRI["Triage<br/>severity + scope"]
    TRI --> CLS["Assessment"]
    CLS --> D2{"GDPR Art. 33:<br/>personal data breach?"}
    D2 -->|yes| CTRL["Notify the affected firm (controller)<br/>DEADLINE AGREED CONTRACTUALLY —<br/>not set by the PRD"]
    D2 -->|"high risk to individuals"| DS["Firm considers data-subject<br/>communication (Art. 34)"]
    CLS --> DORA["Firm's own DORA obligations:<br/>supply what the firm needs to make<br/>its major-incident determination and filing"]
    CLS --> OTH{"Any other regime applicable?<br/>NIS2 flow-down: UNDETERMINED —<br/>see `regulatory-obligations`"}
    OTH -->|"only if confirmed by counsel"| EXT["Additional notification path"]

    CTRL --> CONT["Containment · eradication · recovery"]
    DORA --> CONT
    EXT --> CONT
    CONT --> PIR["Blameless retrospective"]
    PIR --> TM["Threat model updated<br/>'was this modelled?'"]

    style CTRL fill:#4a3010,stroke:#c08040,color:#fff
    style DORA fill:#0d2818,stroke:#2e7d4f,color:#fff
    style OTH fill:#1f1f1f,stroke:#666,color:#fff
```

---

## What was removed

| Removed | Why | Where the content now lives |
|---|---|---|
| **Environment zones** (former D7) | Its primary subject — the boundary between development, pre-production and production, and *where* each is operated — is the unresolved delivery-topology question, which sits outside the confirmed scope | The still-relevant parts (synthetic data only outside production, zero standing production access, break-glass) are folded into **D7 — CI/CD trust zones and environment data rules**. Narrative in `secure-sdlc` and [`supporting-topics/cross-border-data-processing`](supporting-topics/cross-border-data-processing.md) |
| Network-layer internals of the former topology diagram — public/private subnet tiering, ingress, load balancer, DNS resolver firewall, WAF staging | Network security is outside the confirmed scope list; the account-and-data-plane view that *is* in scope was kept | [`supporting-topics/network-security`](supporting-topics/network-security.md) |

Nothing was deleted outright — every removed element is either folded into a retained diagram or described in text in the document named above.
