# 09 — Secrets Management

## Best practices

- **Eliminate secrets before managing them.** Every long-lived credential replaced by a short-lived, workload-identity-derived token is a secret that can never leak. Target: zero long-lived cloud credentials anywhere.
- **No secrets in source, images, environment files, CI variables, tickets, chat, or wikis.** Enforce with automated detection at three points: pre-commit, PR, and repository-wide historical scan.
- **Short TTLs everywhere.** A 15-minute credential limits a leak to 15 minutes.
- **Every secret has an owner, a rotation schedule, and an automated rotation path.** A secret that cannot be rotated automatically is an incident waiting to happen.
- **Assume every secret will eventually leak; design the blast radius accordingly.** Scope each credential to the narrowest possible action set and resource set.
- **Detect and revoke fast.** Leak detection is worthless without an automated revocation path measured in minutes.

## EU regulatory implications

- **DORA Art. 9(4)(c)** and **Delegated Reg. (EU) 2024/1774** — identity and access management requirements cover authentication credential lifecycle, strong authentication, and privileged access management. Service credentials fall squarely within this.
- **NIS2 Art. 21(2)(i)/(j)** — human resources security, access control policies, and use of MFA/secured communications.
- **GDPR Art. 32** — a leaked database credential is a direct route to a personal-data breach; credential hygiene is an Art. 32 measure and will be examined after any incident.
- **DORA Art. 17–19** — a leaked credential with production data access is an ICT-related incident requiring classification and, if it meets the thresholds, reporting.
- **MiCA Art. 68** — "security access protocols" are called out explicitly for CASPs; our credential model becomes part of their supervisory narrative.

## Recommended architecture

### Tier 0 — Secretless (the goal for ~90% of cases)

| Use case | Mechanism | Result |
|---|---|---|
| CI/CD → AWS | GitHub Actions OIDC → `sts:AssumeRoleWithWebIdentity` | No AWS keys in CI, ever |
| Pod → AWS services | EKS Pod Identity / IRSA (service account → IAM role) | No AWS keys in pods |
| Service → service | mTLS with SPIFFE/SPIRE identities, ≤1h certificates | No shared service tokens |
| Service → PostgreSQL | RDS IAM database authentication (15-minute tokens) | No database passwords |
| Service → S3/KMS/SQS | Instance/pod role, scoped policy | No credentials at all |
| Human → AWS | SSO (IAM Identity Center) + FIDO2, ≤4h sessions | No IAM users, no access keys |

**IAM users with long-lived access keys are banned org-wide** via SCP (`iam:CreateAccessKey` denied except for a narrow, monitored break-glass account).

### Tier 1 — Managed secret store (for what remains)

Irreducible secrets: third-party API keys (payment provider, email, AI provider where OIDC isn't supported), customer-supplied integration credentials, signing keys not held in KMS.

- **AWS Secrets Manager** as the store (native rotation Lambdas, KMS encryption with a dedicated CMK, IAM-scoped access, CloudTrail-audited reads, cross-region replication for DR).
- **External Secrets Operator** syncs into Kubernetes as short-TTL Secrets, or — preferably — the **Secrets Store CSI driver** mounts them as ephemeral files so they never enter etcd or environment variables.
- **Never inject secrets as environment variables** where avoidable: environment variables leak via crash dumps, `/proc`, child processes, debug endpoints, error pages and observability agents. Mounted files with restrictive permissions are strictly better.
- **Per-environment isolation:** `dev`, `staging` and `prod` secrets live in separate accounts with no cross-account access path. A compromised dev secret must be worthless in production.
- **Customer-supplied credentials** (e.g. a customer's own API keys for integrations) are encrypted with the **tenant CMK**, stored in the application database rather than the platform secret store, and are never readable by operators.

### Rotation

| Secret type | Rotation | Automation |
|---|---|---|
| Database credentials | Not applicable (IAM auth) | N/A |
| Third-party API keys | 90 days | Secrets Manager rotation function per provider where supported; ticketed manual rotation with SLA where not |
| Signing keys | Per doc 08 | KMS |
| Encryption keys | Per doc 08 | KMS automatic |
| Break-glass credentials | After every use, and quarterly | Automated on use-detection |
| Customer integration credentials | Customer-driven; expiry warnings at 30/14/7 days | Notification pipeline |

### Detection and response

- **Pre-commit:** `gitleaks` hook (advisory, fast).
- **PR:** blocking secret scan on the diff; blocking is justified here because the false-positive rate is low and the cost of a miss is high.
- **Repository:** GitHub secret scanning with push protection enabled; partner-pattern alerts route to the SIEM.
- **Runtime:** canary/honeytoken credentials embedded in repos and images — any use is an immediate high-severity alert and a definitive breach indicator (doc 22).
- **Automated revocation runbook:** detection → automated revocation within 5 minutes for supported providers → rotation → git history rewrite where feasible (noting that public exposure means the secret must be treated as permanently compromised regardless) → incident record → DORA/GDPR assessment.
- **Historical scan** of the entire git history at project start, and after any repository visibility change.

### Local development

- Developers never hold production or staging secrets. Local development uses:
  - `docker-compose` with fixed, obviously-fake local credentials.
  - LocalStack or equivalent for AWS service emulation.
  - Synthetic data (DD-03-02).
  - A `.env.example` committed with placeholder values; real `.env` files are `.gitignore`d **and** blocked by the Claude Code deny rules (doc 05).
- Access to *staging* secrets, where genuinely needed, is via SSO-derived short-lived credentials, never a copied file.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Secret committed to git and pushed to a public or widely-read repo | Credential exposed permanently; automated scrapers exploit within minutes | Push protection, blocking PR scan, honeytokens, 5-minute automated revocation |
| Secret in a container image layer | Persists in the registry and every pull | Multi-stage builds, image scanning for secrets, no build-time secret ARGs (use BuildKit secret mounts) |
| Secret in environment variables exposed via a crash dump or debug endpoint | Silent compromise from a low-severity bug | File-mounted secrets, disable core dumps, scrub crash reports, no debug endpoints in prod |
| Long-lived IAM access key created for "just one integration" | Permanent standing credential outside the model | SCP denying `iam:CreateAccessKey`; weekly conformance report |
| Third-party secret cannot be rotated automatically | Rotation deferred indefinitely | Register tracks rotation automation status; manual rotations are ticketed with SLA and reported |
| Over-broad secret access from a compromised pod | Lateral movement to unrelated secrets | Per-workload IAM scoping to specific secret ARNs; no wildcard `secretsmanager:GetSecretValue` |
| Secret sprawl into ticketing, chat and documentation | Uncontrolled copies, no rotation | DLP patterns on chat/ticketing; training; a "share a secret" internal tool with expiring one-time links |
| Break-glass credential used without detection | Undetected privileged access | Use triggers immediate alert; rotation after every use; session recording |

## Trade-offs

- **AWS Secrets Manager (integrated, auto-rotation, ~$0.40/secret/month + API costs) vs. HashiCorp Vault (dynamic secrets, multi-cloud, strong audit; substantial operational burden and its own HA/unseal problem).** Vault's dynamic secrets are genuinely better, but running Vault reliably is a meaningful ongoing commitment for a small team, and a Vault outage is a total outage. **Recommendation: Secrets Manager now; revisit Vault only if multi-cloud or on-prem deployment becomes a requirement.**
- **Secrets Store CSI driver (never in etcd, more moving parts) vs. External Secrets Operator into K8s Secrets (simpler, secrets land in etcd).** With etcd encryption at rest enabled, ESO is acceptable; CSI is stronger. **Recommendation: CSI driver for production, ESO acceptable in staging.**
- **Blocking PR secret scan (safe, occasional false-positive friction) vs. advisory.** **Recommendation: blocking. The false-positive rate is low and the failure mode is severe.**
- **Honeytokens (excellent, near-zero-false-positive detection; small maintenance overhead and the risk of confusing a new engineer) vs. none.** **Recommendation: deploy them, and document their existence in the security runbook only.**
- **Git history rewrite after a leak (removes the artefact, breaks clones and signatures) vs. rotate-and-move-on.** **Recommendation: always rotate first and treat the secret as burned; rewrite history only for private repos where the exposure window was genuinely internal.**

## Design decisions

- **DD-09-01:** Secretless by default. OIDC federation for CI, EKS Pod Identity/IRSA for workloads, RDS IAM authentication for databases, SPIFFE mTLS for service-to-service, SSO+FIDO2 for humans.
- **DD-09-02:** IAM users and long-lived access keys prohibited org-wide by SCP, with a single monitored break-glass exception.
- **DD-09-03:** AWS Secrets Manager for irreducible secrets, encrypted with a dedicated CMK, mounted via the Secrets Store CSI driver as ephemeral files — not environment variables.
- **DD-09-04:** Strict per-environment secret isolation across separate AWS accounts; no cross-environment credential path exists.
- **DD-09-05:** Customer-supplied integration credentials are encrypted with the tenant CMK and stored in the application data plane, unreadable by operators.
- **DD-09-06:** Secret scanning at pre-commit (advisory), PR (blocking) and repository level (push protection), plus a full historical scan at project start.
- **DD-09-07:** Honeytoken credentials deployed across repositories and images; any use is a P1 incident.
- **DD-09-08:** Automated revocation runbook with a 5-minute target for supported providers; every leak generates an incident record and a DORA/GDPR assessment.
- **DD-09-09:** No production or staging secret ever resides on a developer workstation.

## References

- Commission Delegated Regulation (EU) 2024/1774 — identity and access management, authentication credentials
- Regulation (EU) 2022/2554 (DORA) Art. 9, 17–19
- Directive (EU) 2022/2555 (NIS2) Art. 21(2)(i)/(j)
- NIST SP 800-63B — Digital Identity Guidelines, Authentication and Lifecycle Management
- OWASP Secrets Management Cheat Sheet
- AWS: IAM Roles for Service Accounts / EKS Pod Identity; Secrets Manager rotation; RDS IAM authentication; GitHub Actions OIDC federation
- SPIFFE/SPIRE specification (https://spiffe.io)
- Kubernetes Secrets Store CSI Driver documentation

## Confidence level

**High** — the secretless-first model, OIDC federation, per-environment isolation, and detection/revocation pipeline. These are mature, widely-deployed patterns with well-understood failure modes.

**Medium** — the operational effort of the Secrets Store CSI driver versus ESO in a small team, and the achievable coverage of automated revocation across the specific third-party providers eventually integrated (varies significantly by vendor).
