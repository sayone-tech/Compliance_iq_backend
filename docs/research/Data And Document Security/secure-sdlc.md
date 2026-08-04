# Secure Software Development Lifecycle

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

Nothing in this document is named by the PRD. Its content is classified **[PROPOSED]** unless stated otherwise: it is the development discipline reasonably necessary to deliver NFR-01 (tenant isolation), NFR-02 (encryption), NFR-04 (immutable audit) and NFR-07 (non-deletable six-year retention) with any confidence that they actually hold in the shipped product.

## Best practices

- **Shift left, but gate right.** Fast feedback locally; *blocking* gates only where a defect class genuinely warrants stopping a release. Gates that fire constantly on noise get bypassed, and a bypassed gate is worse than no gate because it produces false assurance.
- **Threat model per feature, not per year.** A short structured pass on every design touching authentication, authorisation, tenant isolation, cryptography, file handling, retention or the AI mapping path. Output is a list of abuse cases that become test cases (`threat-modelling`).
- **Security requirements as acceptance criteria.** "Evidence files are encrypted with the firm's key" belongs in the story's definition of done, verified by an automated test — not in a wiki page.
- **Everything as code, everything reviewed.** Application code, infrastructure, authorisation policy, pipelines and detection rules all go through the same review and CI path. No console changes in production.
- **Two-person rule on anything that reaches production**, with the author unable to approve their own change. This mirrors the product's own two-person sign-off philosophy (FR-32, FR-44) and is simultaneously a quality control and an insider-threat control.
- **Reproducible, attested builds.** Every artefact traceable to a commit and a build (`supply-chain-security`).
- **Track and enforce remediation SLAs by severity**, measured and reported.

## Regulatory context

- **GDPR Art. 25** — data protection by design and by default is a *development-process* obligation. Privacy requirements must appear as design inputs and be testable. This is the one item here with a direct line to a PRD requirement (NFR-06).
- **GDPR Art. 32** — security of processing; the SDLC is how the stated measures come to exist in the code.
- **Delegated Reg. (EU) 2024/1774** (DORA ICT risk management RTS) contains explicit expectations on change management; secure acquisition, development and maintenance; environment separation; testing before deployment; and vulnerability and patch management. Used here as a **design reference** — it binds customers, not the platform vendor (`regulatory-obligations`).
- **NIS2 Art. 21(2)(e)** would mandate a secure SDLC and coordinated vulnerability disclosure **if** NIS2 applies. Scope is undetermined (`regulatory-obligations`). **[OPEN — LEGAL]**
- **CRA** obligations attach only if an installable or embeddable artefact ships. The PRD ships none. **[OPEN, conditional]**

## Recommended architecture

### Pipeline stages and gates **[PROPOSED]**

| Stage | Controls | Gate |
|---|---|---|
| **Design** | Short structured threat-model pass for qualifying changes; privacy screening; a recorded decision for security-relevant choices | Design review sign-off for auth, crypto, tenancy, file-handling and retention changes |
| **Local** | Pre-commit hooks: secret scan, formatter, linter; IDE static analysis | Advisory, fast, non-blocking |
| **PR** | Static analysis with custom rules for tenancy and authorisation idioms; dependency scan; infrastructure-as-code scan; secret scan; licence scan; unit and authorisation tests | **Blocking:** any new Critical/High; any secret; any tenant-isolation test failure |
| **Build** | Hermetic ephemeral runner; SBOM; provenance attestation; artefact signing; base-image pinning by digest | **Blocking:** unsigned artefact cannot be promoted |
| **Pre-deploy** | Dynamic scan against pre-production; image vulnerability scan; policy-as-code checks on the deployment manifest; migration review | **Blocking:** Critical vulnerabilities in the image; policy violations |
| **Deploy** | Progressive delivery, automated rollback, immutable infrastructure | **Blocking:** failed health and security smoke tests |
| **Runtime** | Runtime threat detection, drift detection, continuous configuration compliance | Alert, and auto-remediate where safe |

### Custom static-analysis rules — the highest-value investment **[PROPOSED]**

Generic scanners find generic bugs. The defects that will actually hurt ComplianceIQ are domain-specific. Write rules for:

- Any database query on a tenant-scoped table lacking a tenant predicate or not routed through the tenant-scoped repository layer. *(NFR-01)*
- Any object-storage operation not routed through the tenant-key-aware storage service. *(NFR-02)*
- Any log statement whose arguments include a field marked sensitive in the field registry. *(`audit-logging`)*
- Any HTTP handler lacking an authorisation decorator or middleware. *(FR-09)*
- Any use of a raw cryptographic primitive outside the approved crypto module. *(NFR-02)*
- Any outbound call to a host not in the egress allowlist. *(NFR-03)*
- Any code path that deletes or overwrites a record in a PRD non-deletable class. *(NFR-07, FR-13)*
- Any prompt-construction call whose inputs include customer document content outside the sanctioned mapping path. *(`ai-governance`)*

The last two are specific to this product and are worth writing first.

### Environment separation **[PROPOSED]**

- Separate cloud accounts for development, pre-production, production, security tooling, log archive and shared services, inside the Client-owned AWS organisation (TI-01). No trust path from lower to higher environments.
- Promotion is artefact-based: the exact signed image tested in pre-production is the image deployed to production. No rebuild between environments.
- Production deployment identity is the pipeline's federated role, scoped narrowly, with no interactive assume path.

### Vulnerability management SLAs **[PROPOSED]**

| Severity | Internet-facing / data plane | Internal |
|---|---|---|
| Critical (CVSS ≥ 9.0 or known-exploited) | 24 hours | 7 days |
| High (7.0–8.9) | 7 days | 30 days |
| Medium (4.0–6.9) | 30 days | 90 days |
| Low | 90 days or risk-accepted | Best effort |

Exceptions require documented, dated risk acceptance by a named owner. Overdue items are a reported metric.

### Testing programme **[PROPOSED]**

- Continuous: static analysis, dependency, infrastructure and secret scanning on every PR.
- Regular: authenticated dynamic scanning against pre-production; infrastructure vulnerability scanning; external attack-surface review.
- **Independent penetration test before accepting real customer data**, covering application, API, infrastructure and multi-tenancy isolation, with the report available to customers under NDA. Cadence thereafter is a Client decision. **[PROPOSED / OPEN]**
- Internal adversarial exercises against modelled attack paths — valuable, but a staffing commitment the PRD does not fund. **[FUTURE]**
- Participation in customer threat-led penetration testing (TIBER-EU/TLPT) — **[FUTURE]**.

### Coordinated vulnerability disclosure **[PROPOSED]**

A published `security.txt` and `SECURITY.md`, a monitored security inbox, a defined triage SLA, safe-harbour language, and a public advisory practice. Cheap, and the cheapest source of high-quality external findings. Note CC-03: anything published about the platform is the Client's IP and its publication is the Client's call. **[OPEN]**

A private bug-bounty programme is **[FUTURE]**.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Gate fatigue — noisy scanners bypassed with blanket suppressions | False assurance; real findings buried | Tune ruthlessly; measure false-positive rate; suppression requires a comment with a ticket and expiry |
| Two-person rule circumvented (self-merge, emergency bypass) | Unreviewed production change | Branch protection at organisation level; emergency bypass alerts and requires a retrospective review |
| Tenant isolation untested | Cross-firm data exposure — the catastrophic failure for this product (NFR-01) | Mandatory per-endpoint cross-tenant negative tests; coverage gate |
| Retention/immutability rules implemented but never tested | Silent breach of NFR-07 / FR-13 | Automated tests asserting that delete and update paths fail for protected record classes |
| Dependency updates deferred for stability | Exploitable known vulnerabilities | Automated update PRs with strong test coverage; batch low-risk updates |
| Design-stage threat modelling skipped under delivery pressure | Structural flaws found in pen test or production | Threat model as a merge requirement for qualifying change types, validated in CI against changed paths |
| SDLC evidence not retained | Cannot satisfy a customer security review | Pipeline emits evidence records into the same immutable store used for NFR-04 |

## Trade-offs

- **Blocking gates vs. velocity.** Block only on: secrets, new Critical/High vulnerabilities, tenant-isolation test failures, unsigned artefacts, policy violations, and violations of the non-deletability rules. Everything else advisory with a tracked SLA.
- **Custom rules vs. off-the-shelf only.** Custom rules catch what matters here. Budget a small recurring maintenance allowance.
- **Build vs. buy the toolchain.** Open-source core plus one commercial dependency-reachability tool cuts the main source of gate fatigue. Cost is a Client decision. **[OPEN]**
- **Monorepo vs. polyrepo.** The product has two applications (Firm Application and Platform Admin Portal, PRD §1.1) that share tenancy, audit and evidence infrastructure. A monorepo with ownership rules per area is the simplest path to uniform enforcement across both.

## Design decisions

| ID | Decision | Classification |
|---|---|---|
| DD-04-01 | Separate accounts for dev / pre-production / production / security / log-archive / shared services; artefact-based promotion with no rebuild between environments | **[PROPOSED]** |
| DD-04-02 | Blocking CI gates limited to: secrets, new Critical/High vulnerability, tenant-isolation test failure, unsigned artefact, policy-as-code violation, non-deletability violation. All other findings advisory with tracked SLA | **[PROPOSED]** |
| DD-04-03 | Custom static-analysis rule set for tenant scoping, authorisation middleware, sensitive-field logging, crypto usage, egress, record immutability and prompt construction — maintained as product code with its own tests | **[PROPOSED]** |
| DD-04-04 | Threat model mandatory for changes touching authn/authz, crypto, tenancy, file handling, retention or the AI mapping path; enforced by changed-path detection in CI | **[PROPOSED]** |
| DD-04-05 | Two-person review on all changes; emergency bypass is possible but alerts and requires a documented retrospective | **[PROPOSED]** |
| DD-04-06 | Vulnerability SLAs as tabled; exceptions require dated, signed risk acceptance | **[PROPOSED]** |
| DD-04-07 | Independent penetration test, including multi-tenancy isolation, before real customer data is accepted; ongoing cadence is a Client decision | **[PROPOSED / OPEN]** |
| DD-04-08 | No console or manual changes in production; all change flows through infrastructure as code and the pipeline, with drift detection | **[PROPOSED]** |
| DD-04-09 | Coordinated vulnerability disclosure policy published, subject to Client approval given CC-03 | **[PROPOSED / OPEN]** |

## References

- Regulation (EU) 2016/679 (GDPR) Art. 25, 32
- Commission Delegated Regulation (EU) 2024/1774 — change management; acquisition, development and maintenance; vulnerability management *(design reference)*
- Directive (EU) 2022/2555 (NIS2) Art. 21(2)(e) — conditional on scope
- NIST SP 800-218 — Secure Software Development Framework (SSDF) v1.1
- OWASP SAMM v2; OWASP ASVS; OWASP Top 10 and API Security Top 10
- SLSA v1.0 (https://slsa.dev)
- RFC 9116 — security.txt; ISO/IEC 29147 and 30111 — vulnerability disclosure and handling

## Confidence level

**High** — the pipeline structure, gate selection, custom-rule strategy, environment separation and SLA model are standard practice.

**Medium** — the sustainable cadence for penetration testing and adversarial exercises at this project's funding level; these are Client decisions, not engineering ones.
