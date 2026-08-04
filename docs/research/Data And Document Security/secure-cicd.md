# Secure CI/CD

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

The pipeline is the most privileged system in the organisation: it can change production, it holds deployment identity, and every downstream control trusts it. Compromise the pipeline and the tenant isolation requirement, the encryption requirement, the immutable audit requirement and the non-deletable retention requirement all become claims rather than properties. Treat it as production.

Not named by the PRD. Everything here is **[PROPOSED]**. Specific tools named below are examples of a pattern, not selections. **[OPEN]**

## Best practices

- **No long-lived credentials anywhere in CI.** Federated short-lived credentials only. This single change removes the most-exploited CI attack path.
- **Ephemeral, isolated runners.** Every job starts from a clean image and is destroyed afterwards. No shared state, no cached credentials.
- **Separate the build identity from the deploy identity.** The role that compiles code must not be able to change production.
- **Untrusted code never runs with privileged credentials.** Pull requests from forks, dependency-update branches and any untrusted input execute unprivileged.
- **The pipeline definition is code, reviewed like code** — arguably stricter, since it can rewrite the rules.
- **Everything the pipeline does is logged and reproducible from source.**

## Regulatory implications

- **GDPR Art. 32** — the pipeline holds access paths that could reach personal data; its controls are Art. 32 measures.
- **Delegated Reg. (EU) 2024/1774** — change management: changes recorded, tested, risk-assessed, approved and deployed in a controlled manner, with separation between development and production and between those who develop and those who approve. Emergency changes need a defined post-implementation process. *(Design reference — and the two-person model below mirrors the product's own approval philosophy in the two-person mapping approval requirement and the finding closure requirement.)*
- **Residency (`data-residency`, `cross-border-data-processing`)** — runners that touch production configuration should run in the EU. Where the pipeline is triggered from matters less than where its privileged execution happens.
- **the IP ownership term** — the pipeline builds artefacts whose IP belongs exclusively to the Client; build provenance is part of demonstrating that.

## Recommended architecture

### Trust zones within the pipeline

```
Zone 1 — UNTRUSTED               Zone 2 — TRUSTED BUILD          Zone 3 — DEPLOY
Pull-request validation          Post-merge on the main branch   Environment promotion
──────────────────────           ───────────────────────────     ─────────────────────
Hosted runners                   Self-hosted ephemeral runners   Same, separate identity
No cloud credentials             in an EU region                 Deploy role per environment
Read-only repository token       Federated → build role          Federated → deploy role
Runs untrusted PR code           Artefact signing                Requires: approval gate,
Lint, test, SAST, SCA            Pushes to the registry          signed artefact, attestations
Cannot access secrets            No production data access       Manual approval for production
```

**The critical rule: code from an unreviewed pull request never executes in Zone 2 or 3.** The three classic ways this is violated are privileged fork-PR triggers, self-hosted runners accepting fork PRs, and workflows that check out PR code before approval.

### Identity and permissions

- **Federated identity from the CI platform to cloud roles**, with trust conditions matching the exact repository *and* branch or environment — never a wildcard — and short session durations.
- **Separate roles:** a build role (registry push, package read, no data access); a deploy role per environment (workload deployment, no data-plane read, no ability to decrypt firm keys). **None of these can read client data.**
- **Default token permissions are read-only**, elevated per job only where required.
- **Environment protection rules** on production: required reviewers, a wait timer, and restriction to the main branch.
- **No human holds a standing production deploy credential**; deployment happens only through the pipeline (`secure-sdlc`, DD-04-08).

### Runner security

- **Self-hosted runners are ephemeral** — one job per instance. A persistent self-hosted runner is a shared, credential-bearing machine and one of the highest-value targets in the organisation.
- Runners execute in a shared-services account with **no network path to production data** and egress restricted to the allowlist (`network-security`).
- Runner images are built in-house, scanned, signed and pinned by digest.
- Runners never execute fork-PR code.

### Pipeline stages

| Stage | Zone | Key actions |
|---|---|---|
| PR validation | 1 | Lint, unit tests, **tenant-isolation tests**, **record-immutability tests**, static analysis, dependency scan, infrastructure scan, secret scan, licence scan, authorisation policy tests |
| Merge | — | Two-person review enforced by branch protection; signed commits |
| Build | 2 | Hermetic build, bill of materials, provenance attestation, vulnerability scan attestation, artefact signature, push by digest |
| Deploy to pre-production | 3 | Automatic; admission control verifies signature and attestations; dynamic and integration tests run post-deploy |
| Deploy to production | 3 | Manual approval by two reviewers, same artefact digest as pre-production, progressive rollout, automated rollback on regression |
| Post-deploy | — | Drift detection, configuration compliance scan, deployment record written to the immutable store |

- **Promotion is by digest.** The exact artefact tested in pre-production is deployed to production. No rebuild, no mutable tags.
- **Progressive delivery** with automated rollback on error-rate, latency or security-signal regression. Latency regression matters directly here — The performance requirement sets a two-second dashboard target.
- **Declarative deployment** (the desired state lives in a repository and the environment reconciles to it) is worth considering: it removes cluster credentials from the pipeline and makes production state reviewable. **[PROPOSED / OPEN]**

### Emergency changes

A defined emergency-change process, not the absence of one:

- Emergency deploys use the same pipeline with the approval gate satisfied by a single approver plus an automatic notification to security.
- Full review, risk assessment and documentation completed within a defined window afterwards.
- Emergency deploy count is a reported metric; a rising trend indicates a process problem, not an emergency problem.
- **There is no path that bypasses artefact signing or admission control.** Emergency means faster approval, never weaker verification.

### Pipeline integrity monitoring

- Workflow file changes require review by a designated security reviewer.
- Alert on: new workflow files, changes to federation trust policies, changes to branch protection or environment rules, new self-hosted runners registering, and any use of a privileged fork-PR trigger.
- Periodic reconciliation of deployed artefact digests against signed build records; anything running in production that did not come from a verified build is a top-severity incident.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Compromised pipeline deploys malicious code | Total compromise; client data at risk | Trust zones, narrow federation conditions, ephemeral runners, declarative deployment, admission verification, digest reconciliation |
| Fork PR executes untrusted code with secrets | Secret exfiltration, pipeline takeover | Blocked by policy and alerted; fork PRs run only in Zone 1 with read-only tokens |
| Persistent self-hosted runner compromised and reused | Credential theft, cross-project contamination | Strictly ephemeral runners, one job per instance |
| Over-broad federation trust condition | Any repository or branch can assume the production deploy role | Exact subject conditions including branch or environment; automated policy conformance check |
| Malicious CI action pulled via a mutable tag | Supply-chain compromise of the build | Actions pinned to immutable revisions; allowlist of permitted actions |
| Approval gate bypassed via an administrative override | Unreviewed production change | Overrides alert and require retrospective review; organisation-level branch protection; audit of override events |
| Deploy credential can also read client data | Pipeline compromise becomes a data breach | Deploy roles have no data-plane permissions and cannot decrypt firm keys |
| CI logs leak secrets or client data | Credential exposure; residency breach | Secret masking; no debug logging in Zones 2 and 3; log retention limits; **no production data in CI, ever** |
| Manual console changes cause drift | Unreviewed production state; failed audits | Reconciliation, drift alerting, policies restricting console write access in production |

## Trade-offs

- **Hosted runners vs. self-hosted in the EU.** Source code is the Client's IP under the IP ownership term, not client personal data, so hosted runners are defensible for untrusted PR validation. Zones 2 and 3 handle deployment identity and should be EU-resident. Recommendation: hosted for Zone 1, self-hosted ephemeral in the EU for build and deploy. **[PROPOSED]**
- **Declarative reconciliation vs. push-based deploy from CI.** The former removes cluster credentials from the pipeline; it adds a component. Recommendation: adopt it if the team has capacity; the credential reduction is the main benefit. **[PROPOSED / OPEN]**
- **Manual production approval vs. fully automated deployment.** For a platform whose records must be provably unaltered, an approval gate is worth the latency. Recommendation: manual approval by two reviewers for production; automatic to pre-production. **[PROPOSED]**
- **Two reviewers vs. one.** Painful in a small team. Recommendation: two for production deploys and for changes to security-relevant paths (authentication, authorisation, cryptography, tenancy, retention, pipeline, infrastructure); one for everything else. Monitor override rates. **[PROPOSED]**
- **Signed commits vs. not.** Recommendation: require them; the friction is now low and the provenance value is high. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification |
|---|---|---|
| DD-19-01 | Three trust zones; unreviewed code never executes with privileged credentials or on self-hosted runners | **[PROPOSED]** |
| DD-19-02 | Zero long-lived credentials in CI; federation only, with trust conditions matching the exact repository and branch or environment, and short sessions | **[PROPOSED]** |
| DD-19-03 | Build and deploy identities are separate; neither can read client data or decrypt firm keys | **[PROPOSED]** |
| DD-19-04 | Self-hosted runners are ephemeral, single-job, EU-resident, network-restricted, built from in-house scanned and signed images | **[PROPOSED]** — supports the EU residency requirement |
| DD-19-05 | Artefact promotion is by immutable digest; no rebuild between environments | **[PROPOSED]** |
| DD-19-06 | Production deployment requires two reviewers; progressive rollout with automated rollback | **[PROPOSED]** |
| DD-19-07 | Emergency changes use a faster approval path but never bypass signing, attestation or admission control | **[PROPOSED]** |
| DD-19-08 | Workflow files, federation trust policies and branch protection changes require security review and generate alerts | **[PROPOSED]** |
| DD-19-09 | Periodic reconciliation of production artefact digests against signed build records | **[PROPOSED]** |
| DD-19-10 | Signed commits required on branches that can reach production | **[PROPOSED]** |
| DD-19-11 | Every deployment produces a record (actor, approvers, artefact digest, attestations, timestamp) in the immutable store | **[PROPOSED]** — reuses the immutable audit requirement store |
| DD-19-12 | Declarative deployment reconciliation | **[PROPOSED / OPEN]** |

## References

- Commission Delegated Regulation (EU) 2024/1774 — change management, separation of environments and duties *(design reference)*
- Regulation (EU) 2016/679 (GDPR) Art. 32
- SLSA v1.0 build requirements (https://slsa.dev/spec/v1.0/requirements)
- NIST SP 800-204D — Integrating Software Supply Chain Security in DevSecOps CI/CD
- OWASP Top 10 CI/CD Security Risks
- CIS Software Supply Chain Security Guide

## Confidence level

**High** — trust zoning, federation with narrow trust conditions, ephemeral runners, digest-based promotion and admission-time verification are the current standard.

**Medium** — the sustainability of a two-reviewer requirement in a small team; it is the control most likely to erode in practice, so monitor override rates.
