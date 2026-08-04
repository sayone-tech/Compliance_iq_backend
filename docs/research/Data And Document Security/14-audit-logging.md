# 14 — Audit Logging

Two distinct log populations with different requirements. Conflating them produces a system that is simultaneously too noisy to search and too weak to rely on as evidence.

| | **Operational logs** | **Audit logs** |
|---|---|---|
| Purpose | Debugging, performance | Accountability, evidence, forensics |
| Content | Technical detail | Who did what to which resource, when, why, from where, and the outcome |
| Personal data | Must be redacted/absent | Contains identifiers by necessity |
| Retention | 30–90 days | 5–7 years (doc 15) |
| Mutability | Deletable | Append-only, tamper-evident |
| Access | Engineering | Security and compliance only, itself audited |

## Best practices

- **Log the decision, not just the event.** Every access-control decision — allow *and* deny — with the policy version and reason. Denials are the highest-value security signal in the system.
- **Structured, schema-versioned events.** JSON with a stable, versioned schema. Free-text log lines are unusable for evidence and for detection engineering.
- **Redact at the source, not at the sink.** A pipeline-based redactor eventually misses a field. Use a typed field registry so sensitive values cannot be logged by construction.
- **Correlate everything.** A single trace/correlation ID threaded from the edge through every service, into the audit event and the AI inference record.
- **Tamper-evidence is a design requirement, not a storage setting.** Hash-chain events and anchor periodically (doc 15).
- **Log access to the logs.** Reading the audit log is itself an auditable event.
- **Time is evidence.** Synchronised, monotonic, trusted time; record both event time and ingestion time.

## EU regulatory implications

- **DORA Art. 9(4)(d)/Art. 10** — logging as a detection mechanism with multiple layers of controls; **Delegated Reg. (EU) 2024/1774** requires logging of ICT operations, of user and privileged activity, and requires that logs be **protected against unauthorised access, modification and deletion**, and retained per a defined policy aligned to business and regulatory needs.
- **DORA Art. 11–14** — response and recovery, and **Art. 13** learning; incident root-cause analysis is impossible without adequate logs. DORA also expects the ability to reconstruct the sequence of events after an incident.
- **MiCA Art. 68(9)** — records of all services, activities, orders and transactions retained **5 years, extendable to 7**. For our product, the audit log of who accessed and approved what *is* part of the customer's record set.
- **GDPR Art. 5(2)** accountability — the audit log is the primary means of demonstrating compliance. **Art. 15** — DSARs may require disclosing who accessed a data subject's data. **Art. 32** — logging is a security measure. **Art. 5(1)(c)/(e)** — the log itself is personal data: minimise it, define its retention, and have a lawful basis (legitimate interests / legal obligation) documented.
- **GDPR Art. 33** — a breach notification within 72 hours requires knowing the categories and approximate number of data subjects and records affected. Only a well-designed audit log makes that answerable within the window.
- **NIS2 Art. 21(2)(b)** incident handling; **Art. 23** reporting timelines demand rapid scoping.
- **eIDAS 2** — qualified timestamps give logged events a legal presumption of time accuracy.

## Recommended architecture

### Canonical audit event schema

```jsonc
{
  "schema_version": "1.0",
  "event_id": "01J8...",              // ULID, monotonic
  "event_time": "2026-08-03T09:14:22.481Z",   // when it happened (trusted source)
  "ingest_time": "2026-08-03T09:14:22.902Z",  // when the log pipeline received it
  "correlation_id": "req_01J8...",
  "tenant_id": "tnt_...",
  "actor": {
    "type": "user|service|system|support",
    "id": "usr_...",
    "roles": ["compliance_officer"],
    "session_id": "ses_...",
    "auth_method": "webauthn",
    "ip": "203.0.113.10",             // consider truncation/pseudonymisation policy
    "country": "DE",
    "device_id": "dev_...",
    "on_behalf_of": null              // support acting for a tenant user
  },
  "action": "document.read",
  "resource": {
    "type": "document",
    "id": "doc_...",
    "classification": "RESTRICTED",
    "tenant_id": "tnt_..."
  },
  "purpose": "audit_response",
  "decision": "allow",
  "policy_version": "cedar-2026.07.14",
  "reason": "role=compliance_officer, tenant match, mfa=phishing_resistant",
  "outcome": "success",
  "source_system": "document-service@v2.4.1",
  "prev_hash": "sha256:...",          // hash chain
  "hash": "sha256:..."
}
```

### Events that must always be logged

**Data plane:** document upload / read / preview / download / export / delete / reclassify; assessment generate / edit / approve / reject; evidence record create / seal; search queries (query text is sensitive — hash or classify it); bulk operations with counts.

**Control plane:** authentication (success, failure, MFA challenge, step-up); authorisation denials; session create/terminate; role and permission changes; SSO/SCIM provisioning events; key create/rotate/delete/grant changes; break-glass request, approval and use; configuration and policy changes; tenant lifecycle events; support access sessions (start, end, everything touched).

**AI plane:** every inference — tenant, user, document IDs, prompt hash, prompt version, model ID/version, token counts, output hash, validation results, human reviewer decision and any override rationale (doc 05).

**Infrastructure:** CloudTrail (all regions, all accounts, management + data events for S3 and KMS), EKS audit logs, VPC flow logs, DNS query logs, WAF logs, ALB access logs, Session Manager session recordings, RDS audit logs (pgaudit for DDL and privileged operations).

### Pipeline

```
Services ──▶ structured logger (redaction by typed field registry)
                │
                ├─ operational logs ──▶ CloudWatch Logs / Loki ──▶ 90-day retention
                │
                └─ audit events ──▶ Kinesis Data Streams (KMS-encrypted, audit CMK)
                                     ├─▶ Hash-chain sealer ──▶ S3 evidence bucket
                                     │      (Object Lock COMPLIANCE, doc 15)
                                     ├─▶ OpenSearch (90-day hot search, tenant-filtered)
                                     └─▶ SIEM (doc 22) for detection
```

- **Delivery guarantee:** audit events are written durably before the action completes for high-value actions (document read of `RESTRICTED`, key operations, exports). For lower-value actions, at-least-once asynchronous delivery is acceptable. State this per action class — "best effort logging of a `RESTRICTED` document read" is not defensible.
- **Log-archive account isolation:** the log-archive AWS account accepts writes from other accounts but grants delete to nobody. Even the organisation management account cannot delete from it (enforced by SCP + bucket policy + Object Lock).
- **Separate audit CMK** whose key policy denies `ScheduleKeyDeletion` to every principal.

### Redaction by construction

A typed field registry marks sensitive fields (`@Sensitive`, `@PII`, `@DocumentContent`). The serialiser refuses to emit them; a custom SAST rule (doc 04) fails the build if a sensitive-typed value reaches a log call. Sensitive values that must be correlated are logged as `HMAC-SHA256(log_pepper, value)` so identical values can be linked without exposing plaintext.

Never logged: document content, extracted text, prompt text, presigned URLs, tokens, keys, passwords, full payment identifiers, raw search query strings for `RESTRICTED` scopes.

### Customer-facing audit trail

Expose the tenant's own audit log as a product feature: searchable, filterable, exportable in a signed format, with a documented schema. This is directly saleable — CASPs need it for MiCA Art. 68(9) and their DORA evidence — and it makes our logging quality a revenue-aligned concern rather than a cost centre. Tenants see only their own events; our internal operational access to their tenant is shown to them as `support` actor events (radical transparency; see doc 17).

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Personal data or document content leaks into logs | The log becomes an unprotected copy of the crown jewels | Typed field registry, SAST rule, redaction tests, periodic log-content sampling audit |
| Log volume and cost explosion | Sampling introduced, evidence gaps appear | Separate audit (never sampled) from operational (sampled freely); tier storage; measure cost per event class |
| Log tampering by an insider | Forensics and evidence value destroyed | Hash chaining, Object Lock COMPLIANCE, write-only log-archive account, separate audit CMK with deletion denied |
| Clock skew or timezone errors | Event ordering wrong; evidence value damaged | NTP/Amazon Time Sync, UTC only, monotonic ULIDs, record both event and ingest time, alert on skew |
| Missing logs for a critical action discovered during an incident | Cannot scope a breach within the 72-hour window | Mandatory audit-event coverage test per endpoint in CI; annual log-coverage review against the threat model |
| Audit log is itself a DSAR/erasure target | Conflict between accountability and erasure | Legal-obligation basis (Art. 17(3)(b)); pseudonymise actor identifiers where possible; documented retention |
| Logging in the hot path causes latency or outage | Availability incident, or logging disabled under pressure | Asynchronous by default; synchronous only for the defined high-value action set; buffered with backpressure and a fail-closed decision for `RESTRICTED` reads |
| Nobody reads the logs | Detection value zero | Detections as code with tested rules (doc 22); weekly review of denial and anomaly trends |

## Trade-offs

- **Synchronous audit write before action (guaranteed evidence, latency and an availability coupling) vs. asynchronous (fast, small loss window).** **Recommendation: synchronous for `RESTRICTED`/`PRIVILEGED` reads, exports, key operations and privileged changes; asynchronous at-least-once for everything else. Document the classification.**
- **Log everything (complete forensics, cost, privacy exposure) vs. targeted logging.** **Recommendation: complete coverage of the defined audit-event catalogue with strict field-level minimisation, rather than broad capture of raw requests.**
- **Self-hosted (OpenSearch/Loki — residency-clean, cheaper at volume, ops burden) vs. SaaS SIEM (fast, feature-rich, residency and cost questions).** **Recommendation: OpenSearch in-region for search and evidence; a SIEM for detection, chosen with an EU-tenancy guarantee (doc 22).**
- **Hash chain (cheap, tamper-evident) vs. blockchain/ledger database (stronger third-party verifiability, cost and complexity; note Amazon QLDB reached end of support in 2025).** **Recommendation: hash chain plus periodic external anchoring with an eIDAS qualified timestamp — far better cost/benefit and stronger legal standing than a private ledger (doc 15).**
- **Expose customer-facing audit trail early (differentiator, engineering cost) vs. later.** **Recommendation: early. It is a genuine buying criterion for MiCA/DORA-regulated customers.**

## Design decisions

- **DD-14-01:** Strict separation of operational logs (90 days, redacted, deletable) from audit events (5–7 years, tamper-evident, immutable).
- **DD-14-02:** Single versioned audit event schema with mandatory `decision`, `policy_version`, `purpose` and `reason` fields; both allows and denies are logged.
- **DD-14-03:** Redaction by construction via a typed sensitive-field registry, enforced by a blocking SAST rule; correlatable values are HMAC-pseudonymised.
- **DD-14-04:** Audit events are hash-chained and written to an Object Lock (COMPLIANCE mode) evidence bucket in a dedicated log-archive account that grants delete to no principal.
- **DD-14-05:** Synchronous, durable audit write before completing `RESTRICTED`/`PRIVILEGED` reads, exports, key operations and privileged configuration changes.
- **DD-14-06:** Full AI inference audit record for every model call, retained with the resulting assessment.
- **DD-14-07:** Audit-event coverage is asserted by automated tests per endpoint; missing coverage fails CI.
- **DD-14-08:** Customer-facing, exportable, signed tenant audit trail shipped as a product feature, including visibility of all support access to their tenant.
- **DD-14-09:** UTC everywhere, Amazon Time Sync, ULID event IDs, both `event_time` and `ingest_time` recorded, clock-skew alerting.

## References

- Commission Delegated Regulation (EU) 2024/1774 — logging, protection of logs, retention
- Regulation (EU) 2022/2554 (DORA) Art. 9, 10, 11–14, 17–19
- Regulation (EU) 2023/1114 (MiCA) Art. 68(9)
- Regulation (EU) 2016/679 (GDPR) Art. 5(2), 15, 32, 33
- Directive (EU) 2022/2555 (NIS2) Art. 21(2)(b), 23
- NIST SP 800-92 — Guide to Computer Security Log Management
- OWASP Logging Cheat Sheet; OWASP Top 10 A09 (Security Logging and Monitoring Failures)
- RFC 3161 / eIDAS qualified timestamps; RFC 6962 (Certificate Transparency Merkle tree design, as a model)

## Confidence level

**High** — the operational/audit split, schema design, redaction-by-construction, hash chaining, and write-only log-archive account. These directly satisfy the DORA RTS logging requirements and are proven at scale.

**Medium** — the achievable cost profile at high document-access volumes (synchronous audit writes for `RESTRICTED` reads have a real latency and cost footprint; benchmark before committing to the action classification), and the right retention for IP addresses within audit events under GDPR minimisation, which merits a specific DPO decision.
