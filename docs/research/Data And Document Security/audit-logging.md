# Audit Logging

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

## What the PRD requires

| PRD ref | Requirement |
|---|---|
| FR-13 | "Every action any user takes is permanently recorded in an audit log — **what they did, when, and from which device**. This log cannot be altered or deleted by anyone, including administrators. It exists precisely to prove, to a regulator if needed, that the compliance process was followed correctly." |
| NFR-04 | "Every action in the platform is permanently recorded in a tamper-proof audit log. **Not even the system administrators at SayOne** can modify or delete this log." |
| PRD §2 (dev note) | "Audit log is immutable — append-only. **No admin-level delete or modify capability.**" |
| PRD §2 (table) | Audit log: **minimum 6 years**, cannot be modified by anyone. Notification log: minimum 6 years |
| NFR-07 | Audit logs retained a minimum of six years; no user, including administrators, can delete them |
| FR-21 | Every action is timestamped and linked to the individual who performed it |
| FR-14, GAP-11 | Reassignment of a departed user's open work is documented with reasoning in an immutable audit trail |
| FR-27, FR-21b, FR-21c, FR-33, FR-44 | Amendments, N/A decisions, sample changes, mapping reversals and finding closures all record the actor, the reason and both approvers where two are required |

**This is the strongest requirement in the PRD's technical section, and it is stated three times.** Everything below implements it.

## Two log populations

Conflating them produces a system that is simultaneously too noisy to search and too weak to rely on as evidence.

| | **Operational logs** | **Audit log** |
|---|---|---|
| Purpose | Debugging, performance | Accountability and proof (FR-13) |
| Content | Technical detail | Who did what to which resource, when, from which device, why, and the outcome |
| Personal data | Redacted or absent | Contains identifiers by necessity |
| Retention | Short (weeks) | **Minimum 6 years** (NFR-07) |
| Mutability | Deletable | **Append-only, tamper-evident, no delete or modify path for anyone** (NFR-04) |
| Access | Engineering | Compliance and security; reads are themselves audited |

## Best practices

- **Log the decision, not just the event.** Every access-control decision — allow and deny — with the policy version and reason. Denials are the highest-value security signal in the system.
- **Structured, schema-versioned events.** Free-text log lines are unusable as evidence and unusable for detection engineering.
- **Redact at the source, not at the sink.** A pipeline-based redactor eventually misses a field. Use a typed field registry so sensitive values cannot be logged by construction.
- **Correlate everything.** One correlation identifier threaded from the edge through every service and into the AI inference record (`ai-governance`).
- **Tamper-evidence is a design requirement, not a storage setting.** Immutable storage resists deletion; hash chaining detects alteration.
- **Log access to the log.** Reading the audit log is itself an auditable event.
- **Time is evidence.** Synchronised, monotonic, trusted time; record both event time and ingestion time.

## Regulatory implications

- **GDPR Art. 5(2)** accountability — the audit log is the primary means of demonstrating compliance. **Art. 15** — subject access requests may require disclosing who accessed a data subject's data. **Art. 32** — logging is a security measure. **Art. 5(1)(c)/(e)** — the log itself is personal data: minimise it, define its retention, document the basis.
- **GDPR Art. 33** — breach notification within 72 hours requires knowing the categories and approximate number of data subjects and records affected. Only a well-designed audit log makes that answerable in the window.
- **Delegated Reg. (EU) 2024/1774** — logging of ICT operations and of user and privileged activity, with logs protected against unauthorised access, modification and deletion. *(Design reference; the PRD already requires the stricter version.)*
- **MiCA Art. 68(9)** (customer-side) — for the firm, the record of who accessed and approved what is part of their own record set.

> **Retention note.** MiCA's floor is five years. **The platform's baseline is the PRD's minimum six years (NFR-07, PRD §2).** No 5-year or 7-year default appears anywhere in this set.

## Recommended architecture

### Canonical audit event schema **[PROPOSED]**

```jsonc
{
  "schema_version": "1.0",
  "event_id": "01J8...",                       // monotonic, sortable
  "event_time": "2026-08-04T09:14:22.481Z",    // when it happened (trusted source)
  "ingest_time": "2026-08-04T09:14:22.902Z",   // when the pipeline received it
  "correlation_id": "req_01J8...",
  "firm_id": "frm_...",                        // null for Platform Admin Portal actions
  "actor": {
    "type": "user|service|system|portal_admin",
    "id": "usr_...",
    "system_role": "compliance_officer",       // one of the eight PRD system roles
    "firm_role_label": "AML Analyst",          // the firm's own name for it (PRD §3.2)
    "session_id": "ses_...",
    "auth_method": "password+phone_mfa",       // FR-11
    "ip": "203.0.113.10",
    "country": "PT",
    "device": { "id": "dev_...", "user_agent_hash": "..." }   // FR-13 "from which device"
  },
  "action": "evidence.upload",
  "resource": { "type": "evidence_file", "id": "evd_...", "classification": "RESTRICTED",
                "firm_id": "frm_...", "test_execution_id": "tex_..." },
  "purpose": "test_execution",
  "decision": "allow",
  "policy_version": "authz-2026.07.14",
  "reason": "role=compliance_officer, assigned lead tester, firm match, mfa satisfied",
  "outcome": "success",
  "source_system": "document-service@v2.4.1",
  "prev_hash": "sha256:...",                   // hash chain
  "hash": "sha256:..."
}
```

The `device` field is not optional garnish — **FR-13 names it explicitly.**

### Events that must always be logged

**Compliance workflow (the PRD's own audit surface):** test scheduled, assigned (FR-20), opened, step completed, sampling recorded (FR-21c), evidence uploaded, result recorded (Pass/Fail/Observation), N/A recorded with reason (FR-21b), finding created, remediation plan created, milestone confirmed, CCO approval or send-back (§7.1 step 10), AML Officer agreement (step 11), report generated (FR-55), senior management sign-off (FR-58), report distribution (FR-59), amendment added (FR-27), finding closure with both approvers (FR-44), deadline extension with justification (GAP-08), WSP upload and version (FR-30, FR-37), mapping suggestion, confirmation with both approvers (FR-32), reversal (FR-33), manual override with its tag (GAP-09).

**Data plane:** document read, preview, download, export; search queries (query text is sensitive — hash or classify it); bulk operations with counts.

**Control plane:** authentication success and failure, MFA challenge, step-up; authorisation denials; session create and terminate; invitation issued and accepted (FR-12); role assignment and change (FR-10); user deactivation and work reassignment (FR-14); key create, rotate, grant change; break-glass request, approval and use; configuration and policy changes; Portal actions affecting firms (SA-04 publication, SA-07 configuration, SA-08 settings).

**AI plane:** every inference call — firm, user, document identifiers, prompt hash, prompt version, model version, token counts, validation results, reviewer decision, both approver identities (`ai-governance`).

**Infrastructure:** cloud control-plane trail across all accounts and regions including storage and key data events, orchestrator audit logs, flow logs, DNS query logs, WAF logs, load-balancer logs, administrative session recordings, database audit logs for schema and privileged operations.

### Pipeline **[PROPOSED]**

```
Services ──▶ structured logger (redaction by typed field registry)
                │
                ├─ operational logs ──▶ log store ──▶ short retention
                │
                └─ audit events ──▶ durable stream (encrypted with the audit key)
                                     ├─▶ hash-chain sealer ──▶ immutable object storage
                                     │      write-once retention, no delete path (`immutable-evidence-retention`)
                                     ├─▶ searchable index (recent window, firm-filtered)
                                     └─▶ monitoring for detection (`security-monitoring`)
```

- **Delivery guarantee:** audit events are written durably **before** the action completes for high-value actions — evidence upload and read, result sign-off, approvals, exports, key operations, and anything that makes a record immutable. Lower-value actions may use at-least-once asynchronous delivery. State the classification per action: "best-effort logging of an evidence read" is not defensible against FR-13.
- **Log-archive isolation:** a separate account that accepts writes from other accounts and grants delete to **nobody**. Even the organisation management account cannot delete from it — enforced by organisation policy, bucket policy and write-once retention together. This is what makes NFR-04's "not even the system administrators at SayOne" technically true rather than aspirational.
- **Separate audit key** whose policy denies deletion to every principal (`key-management`).
- **Hash chaining** over events per firm, so any alteration or removal breaks the chain and is detectable. **[PROPOSED]**

External cryptographic anchoring of the chain — qualified timestamps, Merkle-root publication — is **[FUTURE]** (appendix 39).

### Redaction by construction **[PROPOSED]**

A typed field registry marks sensitive fields. The serialiser refuses to emit them; a static-analysis rule fails the build if a sensitive-typed value reaches a log call. Values that must be correlated are logged as a keyed hash so identical values can be linked without exposing plaintext.

**Never logged:** document or evidence content, extracted text, OCR output, prompt text, signed URLs, tokens, keys, passwords, raw search query strings for `RESTRICTED` scopes.

### Firm-visible audit trail **[PROPOSED]**

FR-13 states the log exists "to prove, to a regulator if needed, that the compliance process was followed correctly." A firm therefore needs to be able to *produce* it. A searchable, filterable, exportable view of a firm's own audit events is the reasonable implementation of that purpose. Firms see only their own events.

Signed or cryptographically verifiable export formats, and surfacing Portal-team access inside the firm's own log, are **[FUTURE]** — and the second depends on resolving the SA-06/SA-08 visibility boundary **[OPEN]**.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Personal data or evidence content leaks into logs | The log becomes an unprotected copy of the crown jewels | Typed field registry, static-analysis rule, redaction tests, periodic log-content sampling |
| A delete or modify path exists for the audit log | **Direct breach of NFR-04 and FR-13** | Write-once retention, write-only log-archive account, audit key with deletion denied, static-analysis rule forbidding delete on audit tables, tests asserting deletion fails |
| Log volume and cost growth over six years | Sampling introduced; evidence gaps appear | Separate audit (never sampled) from operational (sampled freely); tier storage; model cost at multiples of projected volume |
| Log tampering by an insider | Forensics and proof value destroyed | Hash chaining, write-once storage, separate account, separate key, separation of duties (`insider-threat-protection`) |
| Clock skew or timezone errors | Event ordering wrong; FR-21 timestamps unreliable | Network time synchronisation, UTC only, monotonic identifiers, both event and ingest time, alert on skew |
| Missing logs for a critical action, discovered during an incident | Cannot scope a breach within 72 hours; cannot prove process compliance | Mandatory audit-event coverage test per endpoint in CI; periodic coverage review against the threat model |
| Audit log is itself an erasure target | Conflict between accountability and erasure | Documented retention basis; pseudonymise actor identifiers where feasible; escalate as part of the open erasure question (`regulatory-obligations`) |
| Synchronous logging in the hot path causes latency | NFR-05 two-second target missed, or logging disabled under pressure | Asynchronous by default; synchronous only for the defined high-value set; buffered with backpressure and a fail-closed decision for `RESTRICTED` reads |
| Nobody reads the logs | Detection value zero | Detections as code with tested rules (`security-monitoring`); periodic review of denial and anomaly trends |

## Trade-offs

- **Synchronous audit write before the action vs. asynchronous.** Recommendation: synchronous for evidence reads and uploads, sign-offs, approvals, exports, key operations and privileged changes; asynchronous at-least-once for everything else. Document the classification. **[PROPOSED]**
- **Log everything vs. targeted logging.** Recommendation: complete coverage of a defined audit-event catalogue with strict field-level minimisation, rather than broad capture of raw requests. **[PROPOSED]**
- **Self-hosted search vs. managed monitoring.** Recommendation: in-region search for the recent window and evidence, with a monitoring tool for detection chosen with an EU processing guarantee (`security-monitoring`). **[PROPOSED]**
- **Hash chain vs. an append-only ledger database.** Recommendation: hash chain over immutable object storage — fewer dependencies, better durability, no vendor deprecation risk, and easier third-party verification. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification | Basis |
|---|---|---|---|
| DD-14-01 | Every user action is permanently recorded with actor, action, timestamp and originating device | **[PRD REQUIRED]** | FR-13, FR-21 |
| DD-14-02 | The audit log is append-only with **no delete or modify capability for any principal, including platform administrators** | **[PRD REQUIRED]** | NFR-04, PRD §2 |
| DD-14-03 | Audit log and notification log retained a minimum of six years | **[PRD REQUIRED]** | NFR-07, PRD §2 |
| DD-14-04 | Strict separation of operational logs (short retention, redacted, deletable) from audit events | **[PROPOSED]** | implements NFR-04 |
| DD-14-05 | Single versioned audit event schema with mandatory decision, policy version, purpose and reason fields; allows and denies both logged | **[PROPOSED]** | — |
| DD-14-06 | Redaction by construction via a typed sensitive-field registry, enforced by a blocking static-analysis rule | **[PROPOSED]** | — |
| DD-14-07 | Audit events hash-chained and written to write-once storage in a dedicated log-archive account that grants delete to no principal | **[PROPOSED]** | implements NFR-04 |
| DD-14-08 | Synchronous durable audit write before completing evidence reads and uploads, sign-offs, approvals, exports, key operations and privileged changes | **[PROPOSED]** | — |
| DD-14-09 | Full AI inference audit record for every mapping call, retained with the resulting mapping | **[PROPOSED]** | supports FR-31, FR-32 |
| DD-14-10 | Audit-event coverage asserted by automated tests per endpoint; missing coverage fails CI | **[PROPOSED]** | — |
| DD-14-11 | Firms can search and export their own audit trail | **[PROPOSED]** | implements the stated purpose of FR-13 |
| DD-14-12 | UTC everywhere, synchronised time, monotonic event identifiers, both event and ingest time recorded, clock-skew alerting | **[PROPOSED]** | supports FR-21 |
| DD-14-13 | Cryptographically signed exports and external anchoring of the chain | **[FUTURE]** | not in PRD |

## References

- Regulation (EU) 2016/679 (GDPR) Art. 5(2), 15, 32, 33
- Commission Delegated Regulation (EU) 2024/1774 — logging, protection of logs, retention *(design reference)*
- Regulation (EU) 2023/1114 (MiCA) Art. 68(9) — customer-side record keeping
- NIST SP 800-92 — Guide to Computer Security Log Management
- OWASP Logging Cheat Sheet; OWASP Top 10 A09
- RFC 6962 — Merkle tree and inclusion-proof design pattern, as a model for hash chaining

## Confidence level

**High** — the operational/audit split, schema design, redaction by construction, hash chaining and the write-only archive account. These implement the PRD's strongest technical requirement directly.

**Medium** — the cost profile at six-year retention and high evidence-access volume, and the latency impact of synchronous writes against the NFR-05 target. Both should be benchmarked before the action classification is fixed.
