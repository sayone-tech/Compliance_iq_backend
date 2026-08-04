# 19 — Secure CI/CD

The pipeline is the most privileged system in the organisation: it can change production, it holds deployment identity, and it is trusted by every downstream control. Compromise the pipeline and every other control becomes irrelevant. Treat it as production, because it is.

## Best practices

- **No long-lived credentials anywhere in CI.** OIDC federation to short-lived cloud roles. This single change removes the most-exploited CI attack path.
- **Ephemeral, isolated runners.** Every job starts from a clean image and is destroyed afterwards. No shared state, no cached credentials, no cross-job contamination.
- **Separate the build identity from the deploy identity.** The role that compiles code must not be able to change production.
- **Untrusted code never runs with privileged credentials.** Pull requests from forks, dependency-update branches and any untrusted input execute in an unprivileged context only.
- **The pipeline definition is code, reviewed like code.** Changes to workflow files require the same review as application changes — arguably stricter, since they can rewrite the rules.
- **Everything the pipeline does is logged as an audit event** and reproducible from source.

## EU regulatory implications

- **DORA Art. 9(4)** and **Delegated Reg. (EU) 2024/1774** — **ICT change management** requirements: changes must be recorded, tested, assessed for risk, approved, and deployed in a controlled manner, with segregation between development and production and separation of duties between those who develop and those who approve/deploy. Emergency changes require a defined post-implementation process.
- **DORA Art. 8/9** — the pipeline is an ICT asset supporting a critical or important function; it must appear in the asset inventory and be protected accordingly.
- **DORA Art. 17–19** — a pipeline compromise leading to malicious code in production is a major ICT-related incident, reportable through customers.
- **NIS2 Art. 21(2)(e)** — security in system acquisition, development and maintenance covers the build and deployment toolchain.
- **CRA (where applicable)** — secure development environment requirements and the ability to demonstrate the integrity of shipped artefacts.
- **GDPR Art. 32** — the pipeline has access paths that could reach personal data (through deployment credentials); its controls are Art. 32 measures.
- **Cross-border (doc 03)** — CI runners that touch production configuration must run in the EU; Indian engineers may trigger a pipeline, but the pipeline's privileged execution happens in EU infrastructure with no interactive access.

## Recommended architecture

### Trust zones within the pipeline

```
Zone 1 — UNTRUSTED                Zone 2 — TRUSTED BUILD           Zone 3 — DEPLOY
PR validation                     Post-merge on main                Environment promotion
─────────────────                 ──────────────────                ─────────────────
GitHub-hosted runners             Self-hosted ephemeral runners     Same, separate identity
No cloud credentials              in eu-central-1 (EU residency)    Deploy role per environment
Read-only GITHUB_TOKEN            OIDC → build role                 OIDC → deploy role
Runs untrusted PR code            Signing via Sigstore keyless      Requires: approval gate,
Lint, test, SAST, SCA             Pushes to ECR                     signed artefact, attestations
Cannot access secrets             No production access              Manual approval for prod
```

The critical rule: **code from an unreviewed pull request never executes in Zone 2 or 3.** GitHub's `pull_request_target` trigger, self-hosted runners on fork PRs, and workflows that check out PR code before approval are the three classic ways this is violated.

### Identity and permissions

- **GitHub Actions OIDC → AWS IAM** with trust policies conditioned on:
  - `token.actions.githubusercontent.com:sub` matching the exact repository **and** ref/environment (`repo:org/repo:environment:production`) — never a wildcard on the repository or ref.
  - `aud` validated.
  - Session duration ≤1 hour.
- **Separate roles:** `ci-build` (ECR push, CodeArtifact read, no data access), `ci-deploy-staging`, `ci-deploy-prod` (EKS deploy, no data-plane read, no KMS decrypt of tenant keys). None of these can read customer data.
- **`GITHUB_TOKEN` permissions default to `read-all`**, elevated per job only where required.
- **Environment protection rules** on `production`: required reviewers (two, one from the security or platform group), a wait timer, and branch restriction to `main` only.
- No human holds a standing production deploy credential; deployment happens only through the pipeline (DD-04-08).

### Runner security

- **Self-hosted runners are ephemeral** (Actions Runner Controller on EKS, or EC2 with a one-job lifecycle). A persistent self-hosted runner is a shared, credential-bearing machine — one of the highest-value targets in the organisation.
- Runners execute in the `shared-services` account with **no network path to production data**, egress restricted to the allowlist (doc 11), and no ability to assume production data-plane roles.
- Runner images are built by us, scanned, signed, and pinned by digest.
- Runners never run fork-PR code.

### Pipeline stages

| Stage | Zone | Key actions |
|---|---|---|
| PR validation | 1 | Lint, unit tests, tenancy-isolation tests, SAST, SCA, IaC scan, secret scan, licence scan, policy tests |
| Merge to `main` | — | Two-person review enforced by branch protection; signed commits required |
| Build | 2 | Hermetic build, SBOM (CycloneDX), provenance attestation, vulnerability scan attestation, cosign signature, push to ECR by digest |
| Deploy staging | 3 | Automatic; Kyverno verifies signature and attestations; DAST and integration tests run post-deploy |
| Deploy production | 3 | Manual approval (two reviewers), same artefact digest as staging, progressive canary rollout, automated rollback on SLO breach |
| Post-deploy | — | Drift detection, config compliance scan, deployment evidence record sealed (doc 15) |

- **Promotion is by digest.** The exact image tested in staging is deployed to production. No rebuild, no `latest`, no tag mutation.
- **Progressive delivery:** canary at 5% → 25% → 100% with automated rollback on error-rate, latency or security-signal regression (Argo Rollouts or Flagger).
- **GitOps** (Argo CD) as the deployment mechanism: the desired state lives in a git repository, the cluster reconciles to it, and drift is detected and reverted automatically. The deploy pipeline's job is to update the git repo, not to hold cluster credentials directly — a meaningful reduction in what a compromised pipeline can do.

### Emergency changes

DORA expects a defined emergency-change process, not the absence of one:
- Emergency deploys use the same pipeline with the approval gate satisfied by a single approver plus an automatic P1 notification to security.
- Full review, risk assessment and documentation completed within 24 hours.
- Emergency deploy count is a reported metric; a rising trend indicates a process problem, not an emergency problem.
- **There is no path that bypasses artefact signing or admission control.** Emergency means faster approval, never weaker verification.

### Pipeline integrity monitoring

- Workflow file changes require review by a `CODEOWNERS`-designated security reviewer.
- Alert on: new workflow files, changes to OIDC trust policies, changes to branch protection or environment rules, new self-hosted runners registering, and any use of `pull_request_target`.
- Weekly reconciliation of deployed image digests against signed build records — anything running in production that did not come from a verified build is a P1.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Compromised pipeline deploys malicious code to production | Total compromise; customer data at risk; catastrophic trust loss | Trust zones, OIDC with narrow trust conditions, ephemeral runners, GitOps, admission control, digest reconciliation |
| `pull_request_target` or fork PR executes untrusted code with secrets | Secret exfiltration, pipeline takeover | Blocked by policy and alerted on; fork PRs run only in Zone 1 with read-only tokens |
| Persistent self-hosted runner compromised and reused across jobs | Credential theft, cross-project contamination | Strictly ephemeral runners, one job per instance |
| Over-broad OIDC trust policy (`repo:org/*:*`) | Any repository or branch can assume the production deploy role | Exact `sub` conditions including ref/environment; automated policy conformance check |
| Malicious GitHub Action version pulled via a mutable tag | Supply chain compromise of the build | Actions pinned to commit SHA; allowlist of permitted actions |
| Approval gate bypassed via admin override | Unreviewed production change | Admin overrides alert security and require retrospective review; org-level branch protection; audit of override events |
| Deploy credential can also read customer data | Pipeline compromise becomes a data breach | Deploy roles have no data-plane permissions and no tenant-key decrypt rights |
| CI logs leak secrets or customer data | Credential exposure | Secret masking, no debug logging in Zone 2/3, log retention limits, no production data in CI ever |
| Infrastructure drift from manual console changes | Unreviewed production state; failed audits | GitOps reconciliation, drift detection alerting, SCPs restricting console write access in production |

## Trade-offs

- **GitHub-hosted runners (zero maintenance, but code and metadata leave EU-controlled infrastructure) vs. self-hosted in `eu-central-1` (residency-clean, ops burden).** Source code is our IP, not customer personal data, so GitHub-hosted is defensible for Zone 1. Zone 2/3 handle deployment identity and should be EU-resident. **Recommendation: GitHub-hosted for untrusted PR validation; self-hosted ephemeral runners in `eu-central-1` for build and deploy.**
- **GitOps (strong drift control, auditable desired state; extra component, slower rollbacks in some scenarios) vs. push-based deploy from CI.** **Recommendation: GitOps with Argo CD. It removes cluster credentials from the pipeline and makes production state reviewable.**
- **Manual production approval (control, adds latency, risks rubber-stamping) vs. fully automated continuous deployment.** For a regulated platform, DORA change-management expectations and customer assurance both favour an approval gate. **Recommendation: manual approval by two reviewers for production; fully automated to staging.**
- **Two-reviewer requirement (strong; painful in a small team, especially across time zones) vs. one.** **Recommendation: two for production deploys and for changes to security-relevant paths (auth, crypto, tenancy, pipeline, IaC); one for everything else. Revisit as headcount grows.**
- **Blocking all fork PRs from CI (safe; hurts open-source contribution to any public components) vs. maintainer-approved runs.** **Recommendation: maintainer approval required before any workflow runs on a fork PR — GitHub supports this natively.**
- **Signed commits required (verifiable authorship; onboarding friction) vs. not.** **Recommendation: require signed commits. With SSH signing and `gitsign`, the friction is now low and the provenance value is high.**

## Design decisions

- **DD-19-01:** Three trust zones; unreviewed code never executes with privileged credentials or on self-hosted runners.
- **DD-19-02:** Zero long-lived credentials in CI. OIDC federation only, with trust policies conditioned on exact repository and ref/environment, sessions ≤1 hour.
- **DD-19-03:** Build and deploy identities are separate; neither can read customer data or decrypt tenant keys.
- **DD-19-04:** Self-hosted runners are ephemeral, single-job, EU-resident, network-restricted, and built from our own scanned and signed images.
- **DD-19-05:** Artefact promotion is by immutable digest; the image tested in staging is the image deployed to production. No rebuild between environments.
- **DD-19-06:** Deployment via GitOps (Argo CD); the pipeline updates the desired-state repository rather than holding cluster credentials.
- **DD-19-07:** Production deployment requires two reviewers via GitHub environment protection; progressive canary with automated rollback.
- **DD-19-08:** Emergency changes use a faster approval path but never bypass signing, attestation or admission control; count is a reported metric with 24-hour retrospective documentation.
- **DD-19-09:** Workflow files, OIDC trust policies and branch protection changes require security review via `CODEOWNERS` and generate alerts.
- **DD-19-10:** Weekly reconciliation of production image digests against signed build records; unverified artefacts in production are a P1 incident.
- **DD-19-11:** Signed commits required on all branches that can reach production.
- **DD-19-12:** Every deployment produces a sealed evidence record (actor, approvers, artefact digest, attestations, timestamp) in the immutable evidence store.

## References

- Commission Delegated Regulation (EU) 2024/1774 — ICT change management, separation of environments and duties
- Regulation (EU) 2022/2554 (DORA) Art. 8, 9, 17–19
- Directive (EU) 2022/2555 (NIS2) Art. 21(2)(e)
- SLSA v1.0 build requirements (https://slsa.dev/spec/v1.0/requirements)
- NIST SP 800-204D — Strategies for Integrating Software Supply Chain Security in DevSecOps CI/CD
- CIS Software Supply Chain Security Guide
- OWASP Top 10 CI/CD Security Risks
- GitHub Actions: OIDC hardening, security hardening for GitHub Actions, environment protection rules
- Argo CD and Argo Rollouts documentation; Kyverno image verification

## Confidence level

**High** — trust zoning, OIDC federation with narrow trust conditions, ephemeral runners, digest-based promotion, GitOps, and admission-time verification. These are the current standard for securing CI/CD and directly satisfy the DORA change-management RTS.

**Medium** — the sustainability of a two-reviewer requirement in a small, time-zone-split team (it is the control most likely to erode in practice; monitor override rates), and the operational overhead of Argo CD for a team new to GitOps.
