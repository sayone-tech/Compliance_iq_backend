# ComplianceIQ – Infrastructure & DevOps

**Version:** 1.0
**Status:** Baseline
**Depends On:** Technical Architecture Baseline (TAB) v2.0, Database Architecture v1.2, Backend Architecture v1.1, Security Architecture v1.0
**Audience:** DevOps, Backend Engineers, Architects, Security Engineers

> This document defines the infrastructure and deployment architecture for ComplianceIQ Phase 1: AWS account structure, compute/database/cache/storage infrastructure, networking, DNS, CI/CD pipeline design, deployment strategy, observability, disaster recovery, and cost management. It implements ADR-017/018/019, TAB v2.0 §4a.3 (environment strategy), and closes gaps no prior document addressed.

---

# 1. Purpose

Prior documents fixed the environment *strategy* (TAB v2.0 §4a.3: Dev → Staging → UAT → Production) and the technology choices (ECS Fargate, PostgreSQL, Redis, S3 — TAB v2.0 §7) but left the concrete infrastructure design, CI/CD mechanics, and operational targets unspecified. This document is the source of truth for:

- How AWS accounts and environments are actually structured.
- What runs where in ECS Fargate, and how it scales.
- Database and cache infrastructure specifics.
- DNS/domain ownership, tying together the subdomain-per-tenant decision (Backend Architecture §5) and the marketing site.
- The CI/CD pipeline, including where the AI evaluation gate (AI & Document Intelligence §9) and database migration ordering (ADR-018) actually sit in the pipeline.
- Disaster recovery targets that back the 99.5% uptime SLA (TI-02).

---

# 2. AWS Account Structure

**Decision:** AWS Organizations, multi-account, within the client-owned AWS Organization (per TI-01).

| Account | Purpose |
|---|---|
| **Management/Shared Services** | AWS Organizations root, billing consolidation, CI/CD runners, container registry (ECR), centralized logging aggregation |
| **Development** | Per-developer or shared dev workloads, synthetic data only |
| **Staging** | Integration testing, mirrors Production configuration, synthetic/anonymized data only |
| **UAT** | Client-facing acceptance environment (TAB v2.0 §4a.3) — where the AI accuracy gate is formally evaluated and Sosinna's team validates Portal-authored content |
| **Production** | Live tenant data, EU-resident (TI-01) |

**Rationale:** blast-radius isolation. A misconfigured IAM policy, a runaway cost, or a security incident in Staging is structurally incapable of touching Production — separate accounts, not just separate VPCs within one account, enforce this at the AWS control-plane level rather than relying on application-level environment checks.

---

# 3. Compute — ECS Fargate

## 3.1 Cluster & Service Design

One ECS Fargate cluster per environment. Services map directly to the queue/module isolation already established:

| ECS Service | Maps To | Scaling Trigger |
|---|---|---|
| `django-web` | Django app (both `firm_api` and `admin_portal_api` namespaces, one deployable per Backend Architecture §3) | Request count / CPU |
| `celery-default` | `default` queue | Queue depth |
| `celery-outbox` | `outbox` queue (Backend Architecture §6) | Queue depth, low-latency target (2–5s poll) |
| `celery-ai` | `ai` queue | Queue depth — isolated so a slow AI call can't starve other queues |
| `celery-reporting` | `reporting` queue | Queue depth, CPU (WeasyPrint/docxtpl rendering is CPU-bound) |
| `celery-notifications` | `notifications` queue | Queue depth |
| `celery-regulatory-monitoring` | `regulatory_monitoring` queue | Scheduled (Celery Beat), minimal scaling needs |
| `celery-ai-eval` | `ai_eval` queue | Triggered on config change, not continuous load |
| `ai-service` | FastAPI AI Service (separate deployable, per AI & Document Intelligence §3) | Request count / CPU, scaled independently of Django |

Each service has its own task definition, CPU/memory allocation, and auto-scaling policy — a spike in report generation doesn't starve outbox event processing, and a slow AI provider response doesn't block the web tier.

## 3.2 Auto-Scaling

Target-tracking scaling policies per service (CPU utilization target ~60-70%, or queue-depth target for Celery services), with minimum task counts set to maintain Multi-AZ availability even at idle (never scale a service to zero in Production).

---

# 4. Database Infrastructure

**Decision:** Amazon Aurora PostgreSQL, Multi-AZ, not plain RDS PostgreSQL.

- **Version:** Aurora PostgreSQL-compatible edition, version aligned to PostgreSQL 16+ (ADR-006), confirmed compatible with the pgvector extension version required (Database Architecture §10).
- **Failover:** Aurora's sub-30-second automatic failover to a standby replica materially supports the 99.5% uptime SLA (TI-02) — meaningfully faster than standard RDS Multi-AZ failover.
- **Read replicas:** reserved for future use (e.g., Portal dashboard aggregate queries reading from a replica to avoid any contention with firm-facing write traffic) — not required for Phase 1 launch scale (~100 firms) but the engine choice keeps this available without a migration later.
- **Connection pooling:** RDS Proxy (or equivalent, e.g., PgBouncer sidecar) in front of Aurora, since the schema-per-tenant model combined with ECS Fargate's elastic task count could otherwise exhaust Postgres's connection limit under scale-out.

## 4.1 Backup Configuration (Recap, Database Architecture §12)

Continuous backup via Aurora's storage-layer replication (effectively continuous, sub-5-minute RPO within a region), daily snapshot exports retained 35 days for point-in-time recovery within that window. The 6-year regulatory retention guarantee is satisfied by the immutability design (rows are never deleted), not by backup retention — these remain two separate mechanisms for two separate risks, as established in Database Architecture §12.

---

# 5. Caching — Redis

**Amazon ElastiCache for Redis, Multi-AZ with automatic failover.** Used per ADR/TAB for Celery broker/result backend and application-level caching (e.g., the gap-analysis cache mentioned in AI & Document Intelligence §8). Multi-AZ matters here specifically because Celery task delivery (including the outbox poller's own scheduling) depends on Redis availability — a single-AZ Redis instance would be a single point of failure for background processing generally.

---

# 6. Storage — S3

## 6.1 Bucket Structure

**Decision:** one multi-purpose bucket per environment, organized by prefix, not a bucket-per-tenant or bucket-per-purpose sprawl.

```
compliance-iq-prod-storage/
├── evidence/{tenant_id}/{evidence_id}         # per-tenant KMS DEK applied at this prefix (Security Architecture §6.1)
├── evidence-quarantine/{tenant_id}/...        # malware-scan quarantine (Security Architecture §9)
├── wsp-documents/{tenant_id}/{wsp_version_id}
├── reports/{tenant_id}/{report_id}/{pdf,docx,xlsx}
├── golden-dataset/                             # AI eval reference documents (shared, not tenant-prefixed)
└── platform-assets/                             # non-tenant platform content
```

**Rationale:** a single bucket keeps lifecycle-rule and IAM-policy management tractable (one bucket policy referencing prefix conditions, rather than potentially hundreds of per-tenant bucket policies as the firm count grows) while still allowing per-tenant KMS encryption to be applied at the prefix level via S3 Bucket Keys / per-object KMS key specification at upload time.

## 6.2 Lifecycle Policies

- `evidence-quarantine/` — indefinite retention (never auto-deleted; quarantined files are a security-review artifact, consistent with the no-hard-delete posture).
- `reports/` — no lifecycle expiration (6-year regulatory retention, Database Architecture §7).
- Standard → Infrequent Access storage class transition after 90 days of no access, for cost efficiency — a storage-tier change only, never a deletion or retention-window change.

---

# 7. Networking

Recap and infrastructure-level detail on Security Architecture §7:

- **VPC per environment**, with private subnets for Aurora, ElastiCache, and the AI Service; public subnets only for the load balancer.
- **No public IP** assigned to any ECS task directly — all inbound traffic passes through an Application Load Balancer.
- **Security groups** scoped tightly per service (e.g., the `django-web` security group is the only one permitted to reach Aurora's port; the AI Service's security group is the only one permitted to reach it from Django).
- **VPC endpoints** (PrivateLink) for S3, Secrets Manager, and ECR access, so traffic to these AWS services never traverses the public internet even though it's "AWS-to-AWS."

---

# 8. DNS & Domain

- **Route 53** hosted zone for `complianceiq.com` (or whichever domain MKT-05 ultimately confirms).
- **Wildcard record** `*.complianceiq.com` → Application Load Balancer, supporting subdomain-per-tenant routing (Backend Architecture §5) without per-firm DNS provisioning.
- **Wildcard ACM certificate** for `*.complianceiq.com`, auto-renewing, attached to the load balancer's HTTPS listener.
- **Separate, explicit record** for `admin.complianceiq.com` (Platform Admin Portal — deliberately not part of the tenant wildcard pattern, per Backend Architecture §5.3).
- **Marketing site** — see Section 9; DNS record points to the Amplify Hosting distribution rather than the ECS load balancer.

---

# 9. Marketing Site Hosting

**Decision:** AWS Amplify Hosting, not Vercel or a self-hosted ECS service.

**Rationale:** the marketing site is built as Next.js with SSG/ISR (TAB v2.0 §6). Amplify Hosting natively supports Next.js ISR (unlike a plain S3+CloudFront static export, which has no mechanism to run the ISR revalidation logic), while keeping the entire infrastructure footprint within AWS — avoiding the operational overhead of a second cloud vendor's billing, access management, and monitoring purely for a low-complexity marketing site. This doesn't compromise the "fully decoupled" principle from TAB v2.0 §6.2 — Amplify Hosting is still an independent deploy pipeline and independent from the ECS-hosted application tier, just within the same AWS Organization.

---

# 10. CI/CD Pipeline

**Decision:** GitHub Actions (source already on GitHub per the network allowlist), Terraform for infrastructure as code.

## 10.1 Pipeline Stages

```
1. Lint + unit tests (Django, FastAPI, React — all three codebases)
2. Dependency/SCA scan (Security Architecture §14) — blocks on critical/high CVEs
3. Build container images → push to ECR (shared services account)
4. Deploy to Staging
5. Database migrations (ADR-018: migrations run BEFORE application rollout, never after)
6. Tenant migrations (Tenant Migration Runner, Database Architecture §8) — applied per-tenant, tracked individually
7. Integration/smoke tests against Staging
8. [If change touches AI prompt/model config] AI evaluation gate (AI & Document Intelligence §9) —
   must clear ≥85% accuracy on the golden dataset before proceeding; this is a hard CI gate, not advisory
9. Manual approval gate (required for UAT and Production promotion — automatic for Dev/Staging)
10. Deploy to UAT — client-facing acceptance testing occurs here
11. Manual approval gate (Production promotion)
12. Rolling deployment to Production (Section 11)
```

## 10.2 Infrastructure as Code

All AWS infrastructure (VPCs, ECS services, Aurora, ElastiCache, S3, IAM, Route 53) is defined in **Terraform**, version-controlled, with `plan` output required as part of any infrastructure-change pull request review — no manual console changes to Production infrastructure outside a documented break-glass emergency procedure (which is itself audit-logged).

## 10.3 Migration Failure Handling

Per Database Architecture §8: a failed tenant migration during step 6 above is visible and resumable **per tenant**, not all-or-nothing — the pipeline reports which tenant schemas succeeded and which failed, halts application rollout if any migration failed (rather than rolling out a new application version against a mismatched schema), and alerts on-call for manual intervention on the specific failed tenant(s).

---

# 11. Deployment Strategy

**Rolling deployment** (ADR-018), with concrete gating:

- New task definition revision deployed incrementally (e.g., 25% of tasks at a time), with ECS health checks required to pass before the next batch proceeds.
- **Automatic rollback** triggers if the health check failure rate exceeds a threshold during rollout — ECS reverts to the previous task definition without waiting for manual intervention, minimizing exposure time for a bad deploy.
- Database migrations (Section 10.1, step 5) are designed to be backward-compatible with the *previous* application version wherever possible (additive schema changes deployed ahead of the code that depends on them), so a rollback of the application tier doesn't require a corresponding database rollback.

---

# 12. Observability & Alerting

Building on the TAB v2.0 monitoring stack (CloudWatch, Grafana Alloy, New Relic):

| Signal | Threshold-Style Alert |
|---|---|
| API error rate | Alert if 5xx rate exceeds a defined threshold over a rolling window |
| API latency (p95/p99) | Alert on sustained degradation |
| Celery queue depth (per queue, Section 3.1) | Alert if `outbox` queue depth suggests processing has stalled beyond a few minutes — outbox delay directly affects notification/audit timeliness |
| Aurora connection pool saturation | Alert before exhaustion, not after |
| Aurora replication lag / failover events | Immediate alert |
| S3 malware-scan queue backlog | Alert — a backlog here means evidence uploads are stuck in quarantine longer than expected |
| Audit log write failures | Immediate alert, treated as a security incident (Security Architecture §10) |
| AI evaluation gate failures | Alert to AI engineering — a prompt/model change failed the accuracy gate and did not promote |
| Certificate expiry (ACM auto-renews, but alert on any renewal failure) | Alert well ahead of expiry as a backstop |

On-call rotation and escalation policy (PagerDuty or equivalent) is an operational/staffing decision outside this document's architectural scope, but the alerting signals above are the contract that on-call tooling integrates against.

---

# 13. Disaster Recovery

**Targets:** RPO ~5 minutes, RTO ~1 hour for a full primary-region event.

- **Primary region:** an EU region (e.g., `eu-west-1`).
- **DR region:** a second EU region (e.g., `eu-central-1`) — must stay EU-to-EU per TI-01's residency requirement; a US or other non-EU DR region is not an option regardless of cost savings.
- **Mechanism:** Aurora cross-region snapshot replication (continuous or near-continuous, backing the ~5-minute RPO target) to the DR region; S3 cross-region replication for evidence/reports.
- **Posture:** warm standby, not active-active. Infrastructure (Terraform-defined, Section 10.2) can be stood up in the DR region from code within the RTO window; it is not continuously running idle compute in both regions. This is a deliberate cost/complexity tradeoff appropriate to ~100-firm Phase 1 scale — active-active would roughly double infrastructure cost for a failure mode (full region loss) that's rare relative to AZ-level failures, which Aurora Multi-AZ already handles in under 30 seconds without any DR invocation at all.
- **DR runbook:** documented, tested at least annually (tabletop exercise minimum, full failover drill recommended before the first renewal cycle) — an untested DR plan is not a real RTO commitment.

---

# 14. Cost Management & Tagging

- Every AWS resource tagged with `environment`, `service`, and (where applicable) `tenant_id`, enabling cost allocation reports that can attribute infrastructure spend to a specific tenant if ever needed for margin analysis on the Enterprise vs. seat-based pricing tiers (CC-01).
- AWS Budgets alerts configured per account (Section 2) to catch runaway costs (e.g., a misconfigured auto-scaling policy) early rather than at month-end billing.

---

# 15. Open Items Carried Forward

| Item | Status |
|---|---|
| Exact ECS task CPU/memory sizing per service | Implementation-phase tuning based on load testing, not an architectural blocker |
| On-call rotation/escalation tooling (PagerDuty vs. alternative) | Operational/staffing decision, outside architectural scope |
| Full DR failover drill scheduling | Should be scheduled once Production is live; first drill recommended before contract renewal cycle |
| RDS Proxy vs. PgBouncer sidecar for connection pooling (Section 4) | Either satisfies the architectural requirement; final choice is an implementation-phase decision |
| Shield Advanced adoption (Security Architecture §7) | Cost/roadmap decision, not a Phase 1 blocker |

---

# 16. Version History

| Version | Date | Notes |
|---------|------|------|
| 1.0 | Jul 2026 | Initial Infrastructure & DevOps specification: multi-account AWS Organization structure, ECS Fargate service-per-queue design, Aurora PostgreSQL (Multi-AZ) decision, ElastiCache Redis, single-bucket-with-prefixes S3 structure, networking/VPC design, wildcard DNS for subdomain-per-tenant, AWS Amplify Hosting for the marketing site, full CI/CD pipeline with the AI evaluation gate and per-tenant migration handling, rolling deployment with automatic rollback, observability alert signals, and explicit RPO/RTO disaster recovery targets. |
