# 18 — Supply Chain Security

Three distinct supply chains, each with its own controls:

1. **Software dependencies** — open-source packages, container base images, build tools.
2. **Build and distribution** — the pipeline that turns source into a running artefact (doc 19).
3. **Third-party services** — cloud provider, AI inference, IdP, email, payments, observability. These are our sub-processors and our customers' fourth parties.

## Best practices

- **Know what you ship.** A complete, accurate, machine-readable SBOM for every artefact, generated at build time from the actual build — not inferred later from a manifest file.
- **Pin everything by digest, not by tag.** `image@sha256:...`, lockfiles committed, GitHub Actions pinned to commit SHAs. A mutable tag is an unauthenticated remote-code-execution channel.
- **Verify provenance before use.** Signature verification enforced at deploy time, not just performed at build time.
- **Reduce the surface.** Every dependency is a trust decision and a maintenance liability. The cheapest supply-chain control is having fewer dependencies.
- **Prioritise by reachability, not by CVSS.** Most "critical" CVEs in a dependency tree are in code paths never executed. Reachability analysis is what makes vulnerability management tractable rather than performative.
- **Assess third parties before signing, monitor them continuously afterwards.** A point-in-time questionnaire is not risk management.

## EU regulatory implications

- **DORA Chapter V (Art. 28–44)** is the dominant regime here. Even though it binds our customers rather than us, its requirements flow to us verbatim through contracts:
  - **Art. 28(3)** — customers maintain a **register of information** listing all ICT third-party providers and their **subcontractors supporting critical or important functions**. Our sub-processors appear in *their* regulatory filing. We must supply accurate, structured data.
  - **Art. 28(8)** — exit strategies for ICT services supporting critical or important functions.
  - **Art. 29** — concentration risk assessment, explicitly including sub-outsourcing chains.
  - **Art. 30(2)/(3)** — mandatory contractual provisions: service descriptions, data locations, availability/security requirements, incident assistance, audit and access rights extending to subcontractors, termination rights and exit support.
  - **Commission Delegated Regulation (EU) 2024/1773** — conditions for subcontracting ICT services supporting critical or important functions; requires assessment of the whole chain and contractual control over material subcontracting changes.
- **NIS2 Art. 21(2)(d)** — supply chain security, "including security-related aspects concerning the relationships between each entity and its direct suppliers or service providers". **Art. 21(3)** — entities must take into account vulnerabilities specific to each supplier and their overall security practices and secure development procedures.
- **CRA (Reg. (EU) 2024/2847)** — where we ship a product with digital elements: SBOM covering at least top-level dependencies (Annex I Part II), vulnerability handling for the support period, and due diligence on integrated third-party components. Manufacturers are responsible for the security of components they integrate.
- **GDPR Art. 28(2)/(4)** — sub-processor authorisation, advance notice of changes with a right to object, and equivalent contractual obligations flowed down. Every third-party service that touches personal data is a sub-processor requiring disclosure.
- **MiCA Art. 73** — outsourcing does not reduce the CASP's responsibility; they must be able to demonstrate control over our chain.

## Recommended architecture

### Dependency management

| Control | Implementation |
|---|---|
| Lockfiles | Committed, verified in CI (`npm ci`, `poetry lock --check`, `go.sum`, `cargo.lock`) |
| Digest pinning | All container images and GitHub Actions pinned to immutable digests/SHAs; Renovate maintains them |
| Private registry proxy | AWS CodeArtifact or Artifactory as the sole upstream; caches packages, blocks direct public-registry access from build |
| Namespace/typosquat protection | Scoped package names reserved; dependency-confusion protection (private registry always wins for internal scopes) |
| New-dependency review | Adding a dependency requires review against a checklist: maintenance activity, maintainer count, transitive weight, licence, known incidents, and whether it can be avoided |
| Update cadence | Renovate PRs; security updates within SLA (doc 04); grouped low-risk updates weekly |
| Cooldown period | New versions of a dependency are not adopted for 3 days unless they fix a security issue — defeats most compromised-release attacks, which are detected within hours |
| SCA + reachability | OSV-Scanner or Trivy for detection; a reachability-capable tool (Semgrep Supply Chain, Snyk, Endor) to prioritise |
| Licence compliance | Automated scan; deny-list for copyleft licences incompatible with our distribution model |

### Build provenance (SLSA)

Target **SLSA Build Level 3**:
- Builds run on ephemeral, isolated, hosted runners with no persistent state between builds.
- Build definitions are version-controlled and reviewed.
- Provenance is generated by the build platform (not by the build script), signed, and non-forgeable by the build itself.
- Artefacts are signed with **Sigstore/cosign** using keyless OIDC signing.
- **In-toto attestations** for the SBOM, the provenance, the test results, and the vulnerability scan.

Deploy-time enforcement is where this becomes real: an admission controller (**Kyverno** or **Sigstore policy-controller**) verifies, before any pod starts:
1. The image is signed by our identity.
2. Provenance attestation exists and references an approved source repository and workflow.
3. An SBOM attestation exists.
4. The vulnerability-scan attestation shows no unremediated Critical findings.

Unsigned or unattested images cannot run in production. Without admission-time verification, signing is ceremony.

### SBOM

- Generated at build time in **CycloneDX** format (better vulnerability and VEX support than SPDX for this use case) by Syft or the build tool's native support.
- Attached to the image as an attestation and stored in a queryable SBOM repository (**Dependency-Track**) with continuous re-evaluation against new advisories — so a newly-published CVE is matched against already-deployed artefacts automatically.
- **VEX** (Vulnerability Exploitability eXchange) statements published for our own components, so customers can distinguish "vulnerable dependency present" from "actually exploitable in our configuration". This dramatically reduces customer security-questionnaire load.
- Customer-facing SBOM available on request under NDA; required if CRA applies.

### Third-party service risk management

**Onboarding gate** — no service processes our or customer data until:

| Check | Evidence |
|---|---|
| Security assurance | SOC 2 Type II, ISO 27001, or equivalent; reviewed, not just collected |
| Data residency | Contractual EU-only processing and storage where personal data is involved |
| Sub-processor position | Willing to be listed publicly; discloses their own sub-processors |
| DPA | GDPR Art. 28 terms, SCCs where a transfer occurs |
| DORA terms | Art. 30(2)/(3) provisions where they support a critical or important function, including audit rights and exit support |
| Incident notification | Contractual notification SLA fast enough to feed our 2-hour customer SLA |
| Exit | Data export format, deletion certification, transition assistance |
| Concentration | Assessed against our existing provider mix |

**Continuous monitoring:** advisory feeds and status pages per provider; annual reassessment; automated alerting on their breach disclosures; an annual reconciliation of the actual sub-processor list against the published one (drift here is common and is a contractual breach).

**Our own third-party register** mirrors the DORA Art. 28(3) register structure so we can hand customers a ready-made extract for their filing. This turns a compliance burden into a sales advantage.

### Fourth-party visibility

Our customers must assess *our* subcontractors. Publish:
- A machine-readable sub-processor list (name, role, country, data categories, whether they support a critical or important function).
- 30 days' advance notice of changes, with a right to object.
- Our own concentration analysis (e.g. "AWS is a single point of dependency for compute, storage, keys and inference; mitigations are X, Y, Z").

Being candid about concentration risk is far more credible than pretending it does not exist — customers already know AWS concentration is systemic, and honest analysis builds trust.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Compromised upstream package (`xz`-style, or a maintainer account takeover) | Backdoor in production | Cooldown period, private registry proxy, minimal dependencies, runtime behavioural detection, egress allowlist limiting exfiltration |
| Dependency confusion / typosquatting | Malicious package pulled during build | Private registry precedence for internal scopes, name reservation, lockfile verification |
| Malicious or compromised GitHub Action | Full CI compromise, secret theft | Actions pinned to SHA, allowlist of permitted actions, minimal `GITHUB_TOKEN` permissions, OIDC instead of stored secrets (doc 19) |
| Unsigned image deployed via a bypass path | Provenance chain broken | Admission-controller enforcement with no exception path; break-glass deploy requires dual approval and generates a P1 review |
| Third party suffers a breach affecting our data | Cascading breach; our customers' regulatory obligations triggered | Contractual notification SLA, incident playbook per provider, data minimisation to each provider, encryption with our keys where possible |
| Sub-processor added without customer notice | GDPR Art. 28 and contractual breach | Vendor intake gate that automatically updates the published list and triggers customer notification |
| AWS concentration risk | Regulator or customer challenges resilience; systemic exposure | Documented analysis, portability engineering (doc 02), tested exit plan, honest disclosure |
| SBOM inaccurate or stale | False assurance; CRA non-compliance | Build-time generation from the actual build; continuous re-evaluation in Dependency-Track |
| Vulnerability backlog grows faster than remediation | SLA breach, audit finding | Reachability prioritisation, dependency reduction, automated updates, measured burn-down |

## Trade-offs

- **Aggressive dependency updating (fewer known vulnerabilities; risk of pulling in a compromised release) vs. conservative pinning (stable; accumulating known CVEs).** The `xz` incident showed that fast updates can be a vulnerability. **Recommendation: 3-day cooldown for routine updates, immediate for actively-exploited vulnerabilities — captures most of both benefits.**
- **SLSA Level 3 (strong provenance; real pipeline engineering effort) vs. signing only.** **Recommendation: Level 3. The admission-time verification is what makes it meaningful, and the incremental cost over signing alone is modest.**
- **Reachability analysis tooling (huge reduction in noise; commercial cost) vs. CVSS-only triage.** Teams drowning in unreachable "criticals" stop triaging. **Recommendation: buy a reachability tool; it pays for itself in engineer time within a quarter.**
- **Private registry proxy (control, dependency-confusion protection; another service to run, another availability dependency) vs. direct public registries.** **Recommendation: proxy — CodeArtifact is managed and cheap.**
- **Publishing detailed sub-processor and concentration information (trust, transparency; competitive intelligence exposure and more customer questions) vs. minimal disclosure.** **Recommendation: publish. Regulated buyers require it, and it pre-empts the questionnaire.**
- **Multi-cloud to reduce concentration risk (genuine resilience against provider failure; roughly doubles operational complexity and weakens every other control through inconsistency).** **Recommendation: do not go multi-cloud. Maintain portability and a tested exit plan instead, and document why — this is a defensible and commonly-accepted position.**

## Design decisions

- **DD-18-01:** All dependencies pinned by digest/lockfile; all GitHub Actions pinned to commit SHA; Renovate maintains updates with a 3-day cooldown except for actively-exploited vulnerabilities.
- **DD-18-02:** AWS CodeArtifact as the sole package upstream; direct public-registry access blocked from build environments; internal scopes always resolve privately.
- **DD-18-03:** SLSA Build Level 3 with Sigstore keyless signing, in-toto attestations for provenance, SBOM, tests and vulnerability scans.
- **DD-18-04:** Kyverno admission control verifies signature, provenance, SBOM and scan attestations before any pod runs in production. No exception path; break-glass deploys are dual-approved and reviewed as P1.
- **DD-18-05:** CycloneDX SBOM generated at build time, stored in Dependency-Track with continuous advisory re-evaluation; VEX statements published for our components.
- **DD-18-06:** Vulnerability prioritisation by reachability, with a commercial reachability tool; CVSS alone does not drive the SLA clock.
- **DD-18-07:** Vendor intake gate with a defined evidence checklist; no service touches customer data before passing it. Passing automatically updates the published sub-processor list and triggers customer notification.
- **DD-18-08:** Third-party register maintained in the DORA Art. 28(3) register-of-information structure and offered to customers as an export.
- **DD-18-09:** Single-cloud (AWS) with documented concentration analysis, engineered portability and an annually-tested exit plan. Multi-cloud explicitly rejected and the rationale recorded as an ADR.
- **DD-18-10:** New-dependency additions require documented review; reducing dependency count is a tracked engineering objective.

## References

- Regulation (EU) 2022/2554 (DORA) Art. 28–30; Commission Delegated Regulation (EU) 2024/1773; Implementing Regulation on the register of information
- Directive (EU) 2022/2555 (NIS2) Art. 21(2)(d), 21(3)
- Regulation (EU) 2024/2847 (CRA) Annex I Part II
- Regulation (EU) 2016/679 (GDPR) Art. 28
- SLSA v1.0 (https://slsa.dev); in-toto attestation framework
- NIST SP 800-161r1 — Cybersecurity Supply Chain Risk Management Practices
- NIST SP 800-218 (SSDF) — PS and PW practice groups
- CycloneDX v1.6; OpenVEX / CSAF VEX profiles
- Sigstore / cosign; Kyverno image verification policies
- OSV.dev; GitHub Advisory Database

## Confidence level

**High** — pinning, provenance with admission-time verification, SBOM with continuous re-evaluation, the vendor intake gate, and the single-cloud-with-portability position. All are established practice and map directly to DORA Chapter V and NIS2 Art. 21(2)(d).

**Medium** — the practical accuracy of reachability analysis across our eventual language mix (it is materially better for some ecosystems than others), and how individual customers' DORA teams will assess our AWS concentration position. Prepare the analysis carefully; expect challenge from tier-1 buyers.
