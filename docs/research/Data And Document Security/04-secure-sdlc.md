# 04 — Secure Software Development Lifecycle

## Best practices

- **Shift left, but gate right.** Fast feedback in the IDE and pre-commit; *blocking* gates only where a defect class genuinely warrants stopping a release. Gates that fire constantly on noise get bypassed, and a bypassed gate is worse than no gate because it produces false assurance.
- **Threat model per feature, not per year.** A lightweight, 30-minute STRIDE pass on every design that touches authn/authz, tenant isolation, crypto, file handling, or external integration. Output is a short list of abuse cases that become test cases (doc 24).
- **Security requirements as acceptance criteria.** "Documents are encrypted with the tenant CMK" belongs in the story's definition of done, verified by an automated test — not in a wiki page.
- **Everything as code, everything reviewed.** Application code, infrastructure (Terraform/OpenTofu), policies (OPA/Cedar), pipelines, and detection rules all go through the same PR + review + CI path. No console changes in production, ever.
- **Two-person rule on anything that reaches production**, with the author unable to approve their own change. This is simultaneously a quality control, an insider-threat control (doc 17) and a DORA change-management control.
- **Reproducible, attested builds.** Every artefact traceable to a commit, a build, and a signed attestation (doc 18).
- **Track and enforce remediation SLAs by severity**, measured and reported — DORA and NIS2 both expect demonstrable vulnerability management, not best-effort.

## EU regulatory implications

- **DORA Art. 8/9** — identification and protection: asset inventory, secure configuration, encryption policy, network segmentation. **Art. 13** — learning and evolving, including post-incident improvement fed back into development.
- **DORA Art. 16 / Commission Delegated Regulation (EU) 2024/1774** — the ICT risk management RTS contains explicit expectations on **ICT change management**, **acquisition, development and maintenance of ICT systems** (secure coding practices, separation of environments, testing before deployment, source-code review for critical systems), and **vulnerability and patch management**. This RTS is effectively our secure-SDLC control catalogue: map to it clause by clause.
- **DORA Art. 24–27** — resilience testing programme: annual vulnerability assessments, network security assessments, scenario-based testing, penetration testing; TLPT every three years for significant entities, and we will be scoped in as a third party.
- **NIS2 Art. 21(2)(e)** — "security in network and information systems acquisition, development and maintenance, including vulnerability handling and disclosure". Directly mandates a secure SDLC and a coordinated vulnerability disclosure process.
- **CRA (if we ship installable components)** — Annex I Part II requires: vulnerability handling, SBOM, security updates for the support period, coordinated vulnerability disclosure policy, and reporting of actively exploited vulnerabilities from 11 September 2026.
- **GDPR Art. 25** — data protection by design and by default is a *development-process* obligation, not a documentation obligation. Privacy requirements must appear as design inputs and be testable.
- **MiCA Art. 68** — customers must demonstrate resilient ICT systems; our SDLC evidence becomes part of their supervisory file.

## Recommended architecture

### Pipeline stages and gates

| Stage | Controls | Gate |
|---|---|---|
| **Design** | Lightweight STRIDE for qualifying changes; privacy screening (LINDDUN prompts); ADR for security-relevant decisions | Design review sign-off for auth/crypto/tenancy/file-handling changes |
| **Local** | Pre-commit hooks: `gitleaks`, formatter, linter; IDE SAST plugin; `.gitignore` hygiene | Advisory (fast, non-blocking) |
| **PR** | SAST (Semgrep with custom rules for our tenancy/authz idioms + CodeQL); dependency scan (OSV/Dependabot/Renovate); IaC scan (Checkov/tfsec/Trivy); secret scan; licence scan; unit + authz tests | **Blocking:** any new Critical/High; any secret; any tenancy-isolation test failure |
| **Build** | Hermetic, ephemeral runner; SBOM generation (CycloneDX); provenance attestation (SLSA); artefact signing (Sigstore/cosign); container base-image pinning by digest | **Blocking:** unsigned artefact cannot be promoted |
| **Pre-deploy** | DAST against staging; container image vulnerability scan; policy-as-code checks (OPA/Conftest) against the deployment manifest; migration review | **Blocking:** Critical vulns in the image; policy violations |
| **Deploy** | Progressive delivery (canary), automated rollback, immutable infra, no in-place mutation | **Blocking:** failed health/security smoke tests |
| **Runtime** | Runtime threat detection (GuardDuty/Falco), drift detection, continuous config compliance (AWS Config/Security Hub) | Alert + auto-remediate where safe |

### Custom SAST rules (highest-value investment)

Generic SAST finds generic bugs. The defects that will actually hurt this platform are domain-specific. Write Semgrep rules for:
- Any database query on a tenant-scoped table lacking a `tenant_id` predicate or not routed through the tenant-scoped repository layer.
- Any S3 object operation not routed through the tenant-key-aware storage service.
- Any log statement whose arguments include a field tagged as `@Sensitive` / in the PII field registry.
- Any HTTP handler lacking an authorisation decorator/middleware.
- Any use of a raw crypto primitive outside the approved crypto module.
- Any outbound HTTP call to a host not in the egress allowlist.
- Any prompt-construction call whose inputs include customer document content (doc 05).

### Environment separation

- Separate AWS accounts: `dev`, `staging`, `prod`, `security-tooling`, `log-archive`, `shared-services`. No cross-account trust from lower to higher environments.
- Promotion is artefact-based: the exact signed image tested in staging is the image deployed to production. No rebuild between environments.
- Production deployment identity is the pipeline's OIDC role, scoped to a single account and a single set of actions, with no interactive assume path.

### Vulnerability management SLAs

| Severity | Internet-facing / data-plane | Internal | Basis |
|---|---|---|---|
| Critical (CVSS ≥9.0 or known-exploited) | 24 hours | 7 days | KEV catalogue and DORA expectations |
| High (7.0–8.9) | 7 days | 30 days | |
| Medium (4.0–6.9) | 30 days | 90 days | |
| Low | 90 days or risk-accepted | Best effort | |

Exceptions require documented risk acceptance by the Head of Security with an expiry date. Overdue items are a reported metric, not a backlog item.

### Testing programme (DORA Art. 24–27 alignment)

- Continuous: SAST/SCA/IaC/secret scanning on every PR.
- Weekly: authenticated DAST against staging.
- Monthly: infrastructure vulnerability scanning; external attack-surface review.
- Quarterly: internal red-team exercise on one scenario (tenant isolation, document exfiltration, CI compromise, insider).
- Annual: independent penetration test by a CREST/OSCP-credentialled firm, covering application, API, infrastructure and multi-tenancy isolation. Report shared with customers under NDA.
- Every 3 years (or when customers require it): participation in customer TLPT / TIBER-EU exercises.

### Coordinated vulnerability disclosure

Published `security.txt` (RFC 9116) and a `SECURITY.md`, a monitored `security@` inbox with PGP, a defined triage SLA (acknowledge 3 working days, initial assessment 10 working days), safe-harbour language, and a public advisory practice. Required by NIS2 Art. 21(2)(e) and CRA; also the cheapest source of high-quality external findings.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Gate fatigue — noisy scanners get bypassed with `--no-verify` or blanket suppressions | False assurance; real findings buried | Tune ruthlessly; measure false-positive rate; suppression requires a comment with a ticket and expiry |
| Two-person rule circumvented (self-merge, emergency bypass) | Insider risk, unreviewed prod change | Branch protection enforced at org level; emergency bypass alerts security and requires retrospective review within 24h |
| Security tests exist but tenancy isolation is untested | Cross-tenant data exposure — the catastrophic failure for this product | Mandatory per-endpoint cross-tenant negative tests; coverage gate |
| Dependency updates deferred for stability | Exploitable known CVEs, SLA breach | Automated update PRs (Renovate) with strong test coverage; batch low-risk updates weekly |
| Design-stage threat modelling skipped under delivery pressure | Structural flaws found in pen test or production | Threat model is a merge requirement for qualifying change types, enforced by a PR template checkbox that CI validates against changed paths |
| SDLC evidence not retained | Cannot satisfy customer/DORA audit | Pipeline emits signed evidence records to the WORM evidence store automatically |

## Trade-offs

- **Blocking gates vs. developer velocity.** Every blocking gate costs throughput. Block only on: secrets, Critical/High new vulnerabilities, tenancy-isolation test failures, unsigned artefacts, policy violations. Everything else advisory-with-SLA. **Recommendation: this narrow blocking set.**
- **Custom SAST rules (high value, ongoing maintenance) vs. off-the-shelf only.** Custom rules catch the defects that matter here. **Recommendation: invest; budget ~1 engineer-week per quarter on rule maintenance.**
- **Build vs. buy the security toolchain.** A consolidated ASPM/platform (Snyk, GitHub Advanced Security, Semgrep Cloud) reduces integration effort and gives management reporting; OSS (Semgrep OSS, Trivy, OSV-Scanner, gitleaks, Checkov) is free but needs glue and dashboards. **Recommendation: OSS core + one commercial dependency/reachability tool to cut SCA false positives, which are the main source of gate fatigue.**
- **Annual pen test (baseline) vs. continuous pen testing / bug bounty.** Bug bounty finds more but generates unpredictable load and requires mature triage. **Recommendation: annual pen test + private, invite-only bounty from year 2.**
- **Monorepo (uniform gates, simple) vs. polyrepo (isolation, granular access).** **Recommendation: monorepo for the platform, with CODEOWNERS enforcing review by domain — simplest path to uniform enforcement.**

## Design decisions

- **DD-04-01:** Six-account separation (`dev`/`staging`/`prod`/`security`/`log-archive`/`shared`), artefact-based promotion, no rebuild between environments.
- **DD-04-02:** Blocking CI gates limited to: secrets detected, new Critical/High vulnerability, tenancy-isolation test failure, unsigned artefact, policy-as-code violation. All other findings advisory with tracked SLA.
- **DD-04-03:** Custom Semgrep rule set for tenant scoping, authorisation middleware, PII logging, crypto usage, egress and prompt construction — maintained as product code with its own tests.
- **DD-04-04:** Lightweight threat model mandatory for changes touching authn/authz, crypto, tenancy, file handling, or external integrations; enforced via changed-path detection in CI.
- **DD-04-05:** Two-person review on all changes; emergency bypass is technically possible but alerts security and requires a 24-hour retrospective.
- **DD-04-06:** Vulnerability SLAs as tabled above; exceptions require dated, signed risk acceptance.
- **DD-04-07:** Public CVD policy with `security.txt`, safe harbour, and published advisories from launch.
- **DD-04-08:** No console/manual changes in production. All change flows through IaC and the pipeline; drift detection alerts on violations.

## References

- Commission Delegated Regulation (EU) 2024/1774 — RTS on ICT risk management (change management; acquisition, development and maintenance; vulnerability management)
- Regulation (EU) 2022/2554 (DORA) Art. 8, 9, 13, 16, 24–27
- Directive (EU) 2022/2555 (NIS2) Art. 21(2)(e)
- Regulation (EU) 2024/2847 (CRA) Annex I Part II
- NIST SP 800-218 — Secure Software Development Framework (SSDF) v1.1
- OWASP SAMM v2; OWASP ASVS v4/v5; OWASP Top 10 (2021) and API Security Top 10 (2023)
- BSIMM; SLSA v1.0 (https://slsa.dev)
- RFC 9116 — security.txt; ISO/IEC 29147 and 30111 (vulnerability disclosure/handling)

## Confidence level

**High** — the pipeline structure, gate selection, custom-rule strategy, environment separation and SLA model are standard, well-evidenced practice and map cleanly to the DORA RTS.

**Medium** — the exact expectations supervisors will apply to a *third-party vendor* under DORA Art. 24–27 testing (we are scoped through customers rather than directly), and the precise CRA conformity path if installable components are shipped.
