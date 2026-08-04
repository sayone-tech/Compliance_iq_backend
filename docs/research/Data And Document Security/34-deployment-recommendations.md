# 34 — Deployment Recommendations

Practical guidance for standing this architecture up, in the order it should be done.

## 1. Foundation before features (weeks 1–4)

Do not write application code that touches customer data until these exist. Retrofitting them is 5–10× the cost.

| # | Action | Why it must be first |
|---|---|---|
| 1 | **AWS Organizations with the full account topology** (doc 30 §1) | Account boundaries cannot be introduced later without a migration |
| 2 | **SCPs and RCPs**: EU-only regions, no IAM access keys, no disabling CloudTrail/GuardDuty/Config | Every subsequent resource inherits the guardrail |
| 3 | **CloudTrail (all accounts/regions) → `log-archive` with Object Lock** | You cannot recover logs you never collected; the first incident will be during build |
| 4 | **Terraform/OpenTofu with remote state, state locking, and no console write access in prod** | Manual drift from week 1 is unfixable culture |
| 5 | **IdP + IAM Identity Center + FIDO2 enrolment for the whole team** | Every access decision afterwards depends on this |
| 6 | **KMS key hierarchy with policy templates** (per-tenant, audit, backup, evidence) | Encryption context and key policy shape the data model |
| 7 | **Git repository with branch protection, signed commits, CODEOWNERS, secret scanning** | Prevents the first secret leak |
| 8 | **Synthetic data fixture factory** | Blocks the "just copy a bit of prod data" habit before it starts |

**The single most consequential early decision:** the tenant isolation model (repository pattern + forced RLS + per-tenant CMK with encryption context). Everything else can be added incrementally; this cannot.

## 2. Sequencing principle

Build in this order, because each stage depends on the last:

```
Guardrails → Identity → Crypto/keys → Data model with isolation
   → Document pipeline → Audit logging → Evidence sealing
      → AI assessment → Monitoring/detection → DR/backup testing
         → Customer SSO → Key tiers → Enclaves
```

Resist building the AI assessment feature first because it is the interesting part. Without audit logging and evidence sealing beneath it, its output is not usable in a regulated context, and you will rebuild it.

## 3. Environment build order

1. **`dev` account first**, with the same guardrails as prod. If a control is painful in dev, fix it before it reaches prod.
2. **`staging` with full architectural parity** — same VPC layout, same mesh, same policy engine, same key structure, synthetic data. Parity is what makes staging tests meaningful; a simplified staging environment is a source of false confidence.
3. **`prod` last**, deployed entirely from the same IaC modules with different parameters. If prod requires bespoke configuration, the modules are wrong.

## 4. Team and role prerequisites

| Role | When needed | Notes |
|---|---|---|
| Head of Security (or fractional CISO) | Before writing code | Owns the obligation register, control matrix, and management-body reporting |
| DPO (may be external) | Before processing any personal data | GDPR Art. 37 assessment; likely required given large-scale special-category processing |
| **EU-resident production on-call (2–3 people or an EU MSP)** | Before the first enterprise customer | Removes the highest-risk cross-border scenario (doc 03). This is a hiring lead-time item — start early |
| Platform/SRE engineer | Foundation phase | Owns IaC, EKS, mesh, GitOps |
| Compliance/GRC analyst | Before first audit | Evidence collection, customer questionnaires, certification programmes |
| MDR provider | Before production data | 24/7 triage; EU processing terms; sub-processor listing |

The EU on-call requirement is a genuine constraint on the operating model, not a nice-to-have. Plan for it in headcount and budget from the outset.

## 5. Rollout of high-risk controls

Several controls in this architecture are **irreversible or outage-causing if misconfigured**. Roll each out in this pattern:

| Control | Staged rollout |
|---|---|
| **S3 Object Lock COMPLIANCE** | GOVERNANCE mode in staging → GOVERNANCE in prod for 30 days → COMPLIANCE, with retention derived only from the policy engine |
| **AWS Backup Vault Lock compliance** | Governance mode → verify retention calculations → lock, understanding the cooling-off period is the last chance to change it |
| **Default-deny egress** | Log-only mode for 2 weeks, build the allowlist from observed traffic → alert mode → enforce |
| **WAF** | Count mode for 2 weeks → block with per-rule metrics and a documented exception path |
| **Forced RLS** | Enable in staging with full test suite → enable in prod with a monitored rollback plan (a missed `SET app.tenant_id` fails closed, which is correct but visible) |
| **Kyverno admission verification** | Audit mode → enforce in staging → enforce in prod |
| **mTLS mesh** | Permissive mode → strict, service by service |
| **Zero standing access** | Reduce standing access progressively; measure break-glass frequency; do not flip to zero before the redacted-observability work is done |

Never enable two irreversible controls in the same change window.

## 6. Data migration and onboarding

- **First customer onboarding is a control test.** Run it as a rehearsal with a design partner, with the security team observing, and capture every friction point.
- **Tenant provisioning must be fully automated** — CMK creation, key policy, RLS context, bucket prefixes, index namespace, retention profile, IdP federation. Manual tenant setup guarantees inconsistency, and inconsistency in tenant isolation is a breach waiting to happen.
- **Bulk document import** (customers will have years of existing evidence) needs its own hardened path: same quarantine-scan-promote pipeline, rate-limited, with progress reporting and a rollback that does not leave orphaned derivatives.
- **Migration from a customer's existing system** is where residency and retention assumptions break. Validate the source data's classification and retention obligations before ingesting.

## 7. Performance and cost validation before GA

Benchmark these specifically — they are the ones that surprise teams:

| Item | Why | Target to validate |
|---|---|---|
| KMS request rate and latency under document load | Per-document DEK generation can throttle | p99 decrypt latency; throttling rate at 5× projected load |
| Synchronous audit write on RESTRICTED reads | Adds latency to the hot path | p99 impact; decide the action classification empirically |
| Five-layer authorisation overhead | Policy evaluation per request | p99 authorisation latency < 10ms with sidecar-local evaluation |
| Bedrock token cost per assessment | Directly drives unit economics | Cost per assessment at realistic document sizes |
| SIEM ingestion volume | The most common budget overrun | Model at 5× projected; tier retention accordingly |
| Evidence storage growth over 7 years | Object Lock prevents early deletion | Model at 5× volume; validate Glacier lifecycle transitions preserve the lock |
| Aurora Global Database replication lag | RPO commitment depends on it | Sustained lag under peak write load |
| Restore time from immutable vault | The RTO commitment | Measure twice before contracting an SLA |

**Do not contract RTO/RPO SLAs with customers until each has been measured twice in a full test.**

## 8. Certification and assurance sequencing

| Milestone | Prerequisite | Typical lead time |
|---|---|---|
| DPIA complete | Data flows finalised | 4–6 weeks |
| TIA + SCCs executed | Legal counsel in both jurisdictions | 6–8 weeks |
| Penetration test | Feature-complete staging with parity | 3–4 weeks + remediation |
| ISO/IEC 27001 | ISMS operating ~3 months | 6–9 months total |
| SOC 2 Type II | Controls operating ≥6 months | 9–12 months total |
| Customer security pack | All of the above in draft | Ongoing |

Start ISO 27001 early; it is the long pole and the entry ticket for regulated buyers. SOC 2 Type II requires an observation window that cannot be compressed — begin control operation as early as possible even if the audit starts later.

## 9. Documents to produce alongside the build

These are requested in essentially every enterprise security review. Having them ready converts a 6-week due-diligence cycle into a 1-week one:

- Security whitepaper (sanitised architecture + control summary)
- Sanitised threat model summary (doc 32)
- Sub-processor list + machine-readable attestation endpoint
- DPA with SCCs and accurate Annex II
- DORA addendum (Art. 30(2)/(3) provisions) on our paper
- Register-of-information extract template
- BCP/DR summary with the most recent test results
- Penetration test executive summary
- Incident response and notification procedure
- Data classification and retention schedule
- Business continuity and exit plan, including data export format and deletion certification

## 10. Common failure modes to avoid

| Failure mode | How it manifests | Prevention |
|---|---|---|
| Building features before guardrails | Retrofit costs, culture of exceptions | Foundation phase is non-negotiable |
| Simplified staging | Tests pass, production breaks | Full architectural parity |
| "Temporary" production access for launch | Becomes permanent | Zero standing access from day one; build the observability that makes it viable |
| Copying production data to debug | Unlawful transfer, residency breach | Synthetic-only enforced technically, not by policy |
| Enabling COMPLIANCE-mode locks before retention logic is correct | Permanent, unremovable data | Staged rollout per §5 |
| Deferring audit logging until "later" | Cannot scope the first incident | Audit event schema before the first data-handling endpoint |
| Contracting an SLA before measuring | Immediate breach of a commitment | Measure twice, then commit |
| Treating the Indian entity as invisible | Discovered in due diligence; deal loss and trust damage | Proactive disclosure with the control narrative |
| Single person holding all the security knowledge | Bus factor of one on the highest-risk area | Runbooks, pairing, documented decisions (ADRs) |

## 11. Go/no-go criteria for first production customer data

Do not accept real customer data until every one of these is true:

- [ ] All Phase 1 **mandatory (M)** controls in doc 31 implemented and evidenced
- [ ] Cross-tenant negative test matrix passing in CI, with no skipped tests
- [ ] Penetration test completed; all Critical and High findings remediated
- [ ] DPIA completed and signed off by the DPO
- [ ] SCCs executed with the Indian entity; TIA documented
- [ ] Restore verified successfully from an immutable backup, with measured timing
- [ ] Evidence chain verified end-to-end, including a qualified timestamp validation
- [ ] The 14 priority detections firing correctly in a purple-team test
- [ ] Incident response procedure exercised, including the notification templates
- [ ] Zero standing production access confirmed by an IAM audit
- [ ] Sub-processor list published; customer DPA and DORA addendum ready
- [ ] EU-resident on-call rota in place
