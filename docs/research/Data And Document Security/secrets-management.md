# Secrets Management

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

Not named by the PRD. Everything here is **[PROPOSED]**: credential hygiene is what stops a single leaked secret from defeating NFR-01 (isolation), NFR-02 (encryption) and NFR-04 (audit integrity) at once.

## Best practices

- **Eliminate secrets before managing them.** Every long-lived credential replaced by a short-lived, workload-identity-derived token is a secret that can never leak. Target: zero long-lived cloud credentials.
- **No secrets in source, images, environment files, CI variables, tickets, chat or wikis.** Enforce with automated detection at three points: pre-commit, pull request, and a repository-wide historical scan.
- **Short lifetimes everywhere.** A 15-minute credential limits a leak to 15 minutes.
- **Every secret has an owner, a rotation schedule and an automated rotation path.** A secret that cannot be rotated automatically is an incident waiting to happen.
- **Assume every secret will eventually leak; design the blast radius accordingly.** Scope each credential to the narrowest action and resource set.
- **Detect and revoke fast.** Detection without an automated revocation path measured in minutes is decorative.

## Regulatory implications

- **GDPR Art. 32** — a leaked database credential is a direct route to a personal-data breach; credential hygiene is an Art. 32 measure and will be examined after any incident.
- **Delegated Reg. (EU) 2024/1774** — identity and access management expectations cover credential lifecycle, strong authentication and privileged access. Service credentials fall squarely within it. *(Design reference — `regulatory-obligations`.)*
- **MiCA Art. 68** (customer-side) — "security access protocols" are called out explicitly for CASPs; the platform's credential model becomes part of their outsourcing narrative.

## Recommended architecture

### Tier 0 — secretless, the goal for the large majority of cases

| Use case | Mechanism | Result |
|---|---|---|
| CI/CD → cloud | OIDC federation to a short-lived role | No cloud keys in CI, ever |
| Workload → cloud services | Workload identity bound to the service account | No cloud keys in running services |
| Service → service | Mutual TLS with short-lived workload certificates | No shared service tokens |
| Service → database | Identity-based database authentication with short-lived tokens | No database passwords |
| Human → cloud | Single sign-on with a strong second factor, short sessions | No long-lived user credentials, no access keys |

**Long-lived cloud access keys are prohibited organisation-wide** by policy, with a single narrow, monitored break-glass exception.

### Tier 1 — managed secret store for what remains

Irreducible secrets: third-party API keys (email delivery, the AI inference provider where federation is unsupported), customer-supplied integration credentials, and signing keys not held in the key service.

- A **managed secret store** with native rotation, encryption under a dedicated key (`key-management`), identity-scoped access and audited reads.
- **Mount secrets as ephemeral files rather than environment variables.** Environment variables leak via crash dumps, process listings, child processes, debug endpoints, error pages and observability agents.
- **Per-environment isolation:** development, pre-production and production secrets live in separate accounts with no cross-account path. A compromised development secret must be worthless in production.
- **Customer-supplied credentials** — if any integration ever requires them — are encrypted with the **firm's key** (NFR-02), stored in the application data plane rather than the platform secret store, and are not readable by operators.

### Rotation

| Secret type | Rotation | Automation |
|---|---|---|
| Database credentials | Not applicable under identity-based authentication | — |
| Third-party API keys | 90 days | Automated where the provider supports it; ticketed with an SLA where not |
| Signing and encryption keys | Per `key-management` | Key service |
| Break-glass credentials | After every use, and periodically | Automated on use detection |

### Detection and response

- **Pre-commit:** secret-scanning hook, advisory and fast.
- **Pull request:** blocking secret scan on the diff. Blocking is justified — the false-positive rate is low and the cost of a miss is high.
- **Repository:** platform secret scanning with push protection; alerts routed to monitoring.
- **Runtime:** canary credentials embedded in repositories and images — any use is an immediate high-severity alert and a definitive breach indicator (`security-monitoring`).
- **Automated revocation runbook:** detection → automated revocation within minutes for supported providers → rotation → incident record → GDPR assessment. Treat any publicly exposed secret as permanently compromised regardless of history rewriting.
- **Historical scan** of the entire repository history at project start and after any visibility change.

### Local development

Developers never hold production or pre-production secrets. Local development uses obviously-fake fixed credentials, local service emulation, and the synthetic data corpus (`cross-border-data-processing`). Real environment files are git-ignored **and** blocked by the AI coding tool deny rules (`ai-governance`).

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Secret committed and pushed | Credential exposed; automated scrapers exploit within minutes | Push protection, blocking PR scan, canary tokens, fast automated revocation |
| Secret baked into a container image layer | Persists in the registry and every pull | Multi-stage builds, image secret scanning, build-time secret mounts rather than build arguments |
| Secret in environment variables exposed via a crash dump or debug endpoint | Silent compromise from a low-severity bug | File-mounted secrets, disable core dumps, scrub crash reports, no debug endpoints in production |
| A long-lived access key created "for just one integration" | Permanent standing credential outside the model | Organisation policy denying access-key creation; periodic conformance report |
| Third-party secret cannot be rotated automatically | Rotation deferred indefinitely | Register tracks automation status; manual rotations ticketed with an SLA and reported |
| Over-broad secret access from a compromised workload | Lateral movement to unrelated secrets | Per-workload scoping to specific secret identifiers; no wildcard read permissions |
| Secret sprawl into ticketing, chat and documentation | Uncontrolled copies, no rotation | Detection patterns on chat and ticketing; training; an internal one-time-link sharing tool |
| Break-glass credential used undetected | Undetected privileged access | Use triggers an immediate alert; rotation after every use; session recording |

## Trade-offs

- **Managed secret store vs. a self-run secret manager.** Dynamic secrets from a self-run manager are genuinely better; running one reliably is a meaningful ongoing commitment, and an outage of it is a total outage. Recommendation: managed store now; revisit only if multi-environment or non-cloud deployment becomes a requirement. **[PROPOSED]**
- **Ephemeral file mounts vs. syncing secrets into orchestrator objects.** File mounts keep secrets out of the orchestrator's datastore. Recommendation: file mounts in production. **[PROPOSED]**
- **Blocking PR secret scan vs. advisory.** Recommendation: blocking. **[PROPOSED]**
- **Canary credentials vs. none.** Near-zero false positives, small maintenance overhead. Recommendation: deploy, and document their existence only in the security runbook. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification |
|---|---|---|
| DD-09-01 | Secretless by default: OIDC federation for CI, workload identity for services, identity-based database authentication, mutual TLS between services, single sign-on with a strong second factor for humans | **[PROPOSED]** |
| DD-09-02 | Long-lived cloud access keys prohibited organisation-wide, with a single monitored break-glass exception | **[PROPOSED]** |
| DD-09-03 | A managed secret store for irreducible secrets, encrypted under a dedicated key, mounted as ephemeral files rather than environment variables | **[PROPOSED]** |
| DD-09-04 | Strict per-environment secret isolation across separate accounts; no cross-environment credential path exists | **[PROPOSED]** |
| DD-09-05 | Any customer-supplied integration credential is encrypted with that firm's key and stored in the application data plane, unreadable by operators | **[PROPOSED]** |
| DD-09-06 | Secret scanning at pre-commit (advisory), pull request (blocking) and repository level (push protection), plus a full historical scan at project start | **[PROPOSED]** |
| DD-09-07 | Canary credentials deployed across repositories and images; any use is a top-severity incident | **[PROPOSED]** |
| DD-09-08 | Automated revocation runbook with a minutes-scale target; every leak generates an incident record and a GDPR assessment | **[PROPOSED]** |
| DD-09-09 | No production or pre-production secret ever resides on a developer workstation | **[PROPOSED]** |

## References

- Regulation (EU) 2016/679 (GDPR) Art. 32
- Commission Delegated Regulation (EU) 2024/1774 — identity and access management, authentication credentials *(design reference)*
- NIST SP 800-63B — Digital Identity Guidelines
- OWASP Secrets Management Cheat Sheet
- SPIFFE/SPIRE specification (https://spiffe.io) — one workload-identity option
- Kubernetes Secrets Store CSI Driver documentation — one ephemeral-mount option

## Confidence level

**High** — the secretless-first model, federation, per-environment isolation, and the detection and revocation pipeline are mature, widely deployed patterns.

**Medium** — achievable coverage of automated revocation across whichever third-party providers are eventually integrated; this varies significantly by vendor.
