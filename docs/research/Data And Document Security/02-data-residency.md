# 02 — Data Residency

## Best practices

- **Residency is not a region setting.** It is the property that *every* copy, derivative, index, cache, log, backup, key, and human eyeball stays inside the declared boundary. Nine out of ten residency failures are in the "boring" tier: telemetry, error tracking, email, CDN edge, DNS logs, support tooling, and the vendor's own control plane.
- **Enumerate the full data-flow inventory before choosing a region.** For each data class: where written, where replicated, where indexed, where cached, where logged, where backed up, who can read it, and from which country.
- **Distinguish three strengths of residency claim**, and sell them as distinct tiers rather than blurring them:
  1. **Data residency** — data at rest is stored in the EU.
  2. **Data sovereignty** — data and its keys are subject to EU law only; operational and support access is EU-restricted.
  3. **Technical sovereignty / immunity from third-country access** — infrastructure operated by an EU-controlled entity, keys held outside the provider's reach.
- **Pin regions explicitly and enforce with policy.** Never rely on defaults. Deny-by-default all non-EU regions at the organisation level.
- **Treat metadata as data.** Filenames, tenant names, document titles, embeddings, log lines and search indexes carry confidential content. Embeddings in particular are invertible enough to be treated as personal data.
- **Support access is the hardest part.** A 24/7 follow-the-sun support model with Indian engineers reading production logs will defeat any residency claim regardless of where the bytes live.

## EU regulatory implications

- **GDPR** does not mandate EU residency. It mandates lawful transfer (Chapter V) and appropriate security (Art. 32). Residency is a *means*, and the strongest practical means, but it is not itself the legal test. Marketing must not conflate them.
- **DORA Art. 28(2) and Art. 29** require customers to consider the country in which ICT services are provided and where data is processed/stored, and to assess concentration risk. Customers must record data locations in their **register of information** (Art. 28(3)) — meaning we must publish authoritative, machine-readable region and sub-processor data.
- **DORA Art. 30(2)(b)** requires contractual specification of the locations (regions/countries) where functions are provided and data is processed/stored, **and notification before any change**. Region changes become a contractual event, not an ops decision.
- **MiCA Art. 68/73** — CASPs must ensure continuity and supervisory access to records; competent authorities expect to reach records without third-country legal obstruction.
- **NIS2 Art. 21(2)** supply-chain security measures pull the residency posture of our own sub-processors into scope.
- **Third-country access law is the real driver.** US CLOUD Act (18 U.S.C. §2713) permits compelled production of data held by US-controlled providers irrespective of storage location. This is why "eu-central-1" alone does not satisfy sophisticated buyers, and why key custody (doc 08, 20) is the actual control.
- **EUCS** (EU Cloud Services certification scheme) remained unadopted with its sovereignty requirements contested; do not build commitments on it. **EU Cloud Code of Conduct**, **BSI C5**, and **SecNumCloud** are the usable assurance references today.

## Recommended architecture

**Primary posture: EU hyperscaler region, EU-restricted operations, customer-controlled keys — with an engineered exit path to an EU-sovereign provider.**

- **Primary region:** `eu-central-1` (Frankfurt, Germany). Rationale: largest EU service surface, three AZs, German data-protection expectations align with the buyer base, mature KMS/HSM/Object Lock support.
- **Secondary/DR region:** `eu-north-1` (Stockholm, Sweden) or `eu-west-1` (Ireland). Both EU/EEA. Sweden preferred for jurisdictional diversity away from a single member state and for lower-carbon operations; Ireland preferred for service parity. **Recommendation: `eu-north-1`**, with a documented service-parity check per component.
- **Hard region lockdown:**
  - AWS Organizations SCP denying all actions where `aws:RequestedRegion` is not in `{eu-central-1, eu-north-1}` (with a narrow allowlist for genuinely global services: IAM, Organizations, CloudFront, Route 53, WAFv2 global scope).
  - **Resource Control Policies (RCPs)** to deny access to S3/KMS/STS from non-EU network paths and non-approved principals — RCPs bind on the resource side and close the gap SCPs leave for cross-account access.
  - `aws:RequestedRegion` and `aws:PrincipalOrgID` conditions on every S3 bucket policy and KMS key policy.
- **AI inference residency:** Amazon Bedrock in `eu-central-1` with **cross-region inference profiles disabled** (or restricted to an EU-only inference profile). Bedrock does not use customer inputs/outputs to train models and does not retain them for provider purposes; combined with EU-only routing this is the strongest available residency position for the AI tier. Alternative: EU-hosted open-weight models on EU infrastructure — see doc 05 trade-offs.
- **Boring-tier residency (this is where projects fail):**

| Component | Requirement | Concrete choice |
|---|---|---|
| Observability | EU-hosted, EU-only storage | Self-hosted Grafana/Loki/Mimir/Tempo in-region, or a vendor with a contractually EU-only tenancy |
| Error tracking | EU tenancy, PII scrubbing before send | Sentry EU (`de.sentry.io`) or self-hosted; strip request bodies |
| Email/notifications | EU sending infrastructure | Amazon SES in `eu-central-1`; no document content in email bodies |
| Support/ticketing | EU tenancy; no attachment of customer documents | EU-region SaaS; documents referenced by ID only |
| CDN | EU-only PoPs for authenticated content | CloudFront with a geo-restricted distribution, or serve authenticated content from the region directly |
| Search index | In-region, encrypted with tenant key | OpenSearch in-region, or Postgres full-text |
| Vector store / embeddings | In-region, treated as personal data | pgvector in the primary Aurora cluster |
| Backups | EU only, separate region, never a "global" bucket | Cross-region copy to `eu-north-1` only |
| DNS / WAF logs | EU log destination | Route 53 query logging to in-region CloudWatch/S3 |
| CI/CD | EU-hosted runners for anything touching prod | Self-hosted ephemeral runners in `eu-central-1` |

- **Residency tiers as a product feature:**
  - **Tier 1 (default):** EU regions, EU-restricted support, provider-managed keys.
  - **Tier 2:** + customer-managed keys (CMK) in the customer's own AWS account via KMS grants / External Key Store.
  - **Tier 3:** + EU-sovereign or dedicated-tenancy deployment (AWS European Sovereign Cloud, or an EU-operated provider such as OVHcloud/Scaleway/IONOS/StackIT, or single-tenant deployment in the customer's account).
- **Portability by construction** (this is what makes Tier 3 achievable and satisfies the EU Data Act):
  - Kubernetes (EKS) rather than proprietary compute abstractions.
  - PostgreSQL wire protocol (Aurora PostgreSQL — accepting the lock-in trade-off, mitigated by logical replication export).
  - S3 API for objects (portable to MinIO/Ceph/Scaleway/OVH object storage).
  - PKCS#11/KMIP abstraction over the KMS so the crypto layer is not AWS-shaped.
  - Terraform/OpenTofu modules with the provider isolated behind a thin interface.
- **Residency attestation endpoint:** an authenticated API returning, per tenant, the current list of regions, sub-processors, and data classes — machine-readable, so customers can populate their DORA register of information automatically. This is a genuine differentiator.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| CLOUD Act exposure via US-parent provider | Residency claim rejected by conservative buyers/regulators; theoretical compelled disclosure | Customer-held keys (XKS/EKM) so provider cannot produce plaintext; Tier 3 sovereign option |
| Shadow data egress via a new SaaS tool (analytics, AI assistant, screenshot tool) | Silent, undetected breach of residency commitment | Vendor intake gate; egress allowlist proxy; quarterly sub-processor reconciliation |
| Global/edge services silently replicating (CloudFront, global tables, Route 53) | Metadata leaves EU | Explicit per-service residency review; disable global tables; geo-restrict distributions |
| Support engineer in India opening a production log line containing a document excerpt | Unlawful transfer + residency breach | Log redaction at source (doc 14), EU-only prod access (doc 03/17) |
| Region-parity gaps in DR region force a non-EU fallback | Emergency non-compliance under pressure | Pre-validate every service in `eu-north-1`; no undocumented fallbacks |
| Embeddings/vector index treated as "not personal data" | Reidentification, unlawful processing | Classify embeddings as personal data; encrypt with tenant key; same retention as source |
| Marketing overclaims "sovereign" | Misrepresentation, contractual liability | Tier language locked; legal review of all residency claims |

## Trade-offs

- **Hyperscaler EU region vs. EU-sovereign provider.** Hyperscaler wins on service depth, resilience, HSM/Object Lock maturity, hiring, and speed. Sovereign provider wins on CLOUD Act narrative and some public-sector/tier-1 buyers. Sovereign providers generally have thinner managed-service catalogues, which pushes operational burden (patching, HA, backup) back onto us — a *net resilience risk* under DORA. **Recommendation: hyperscaler now, engineered portability, sovereign as a paid Tier 3.**
- **Single region (simpler, cheaper) vs. multi-region EU (DORA resilience).** DORA Art. 12(3) expects backups to be geographically separated from the primary. Multi-AZ within one region is not sufficient for the backup obligation. **Recommendation: single active region + cross-region backup/DR.**
- **Frankfurt vs. Stockholm as primary.** Frankfurt has service depth and buyer familiarity; Stockholm has lower cost/carbon and jurisdictional diversity. **Recommendation: Frankfurt primary.**
- **Self-hosted observability (residency-clean, ops-heavy) vs. EU-tenancy SaaS (fast, adds a sub-processor).** **Recommendation: EU-tenancy SaaS with contractual EU-only storage for speed; migrate to self-hosted if a Tier 3 customer requires it.**
- **Per-tenant regional placement (sellable) vs. single-region fleet (operable).** Per-tenant placement multiplies operational surface and blast-radius testing. **Recommendation: single-region fleet + Tier 3 single-tenant deployments as bespoke, priced accordingly.**

## Design decisions

- **DD-02-01:** Primary `eu-central-1`, DR/backup `eu-north-1`. No production data outside EU/EEA under any circumstance, including incident response.
- **DD-02-02:** Region restriction enforced technically via SCPs + RCPs, not by convention. CI fails on any Terraform plan referencing a non-approved region.
- **DD-02-03:** Boring-tier services (logs, errors, email, support, CI) are subject to the same residency review as the data plane; each has a named EU-resident implementation recorded in the sub-processor register.
- **DD-02-04:** Embeddings, search indexes, filenames and document titles are classified at the same sensitivity as the source document.
- **DD-02-05:** Three published residency tiers; "sovereign" terminology reserved for Tier 3 only.
- **DD-02-06:** Machine-readable residency/sub-processor attestation API shipped as a product feature for customer DORA registers.
- **DD-02-07:** Portability constraints (K8s, PostgreSQL, S3 API, PKCS#11/KMIP abstraction) are architectural rules, enforced at design review.

## References

- Regulation (EU) 2022/2554 (DORA) Art. 28–30; Commission Implementing Regulation on the register of information
- Regulation (EU) 2016/679 (GDPR) Chapter V, Art. 32
- Regulation (EU) 2023/2854 (Data Act), Chapter VI — cloud switching, applicable 12 September 2025
- CJEU C-311/18 (*Schrems II*)
- EDPB Recommendations 01/2020 on supplementary measures (v2.0, 18 June 2021)
- US CLOUD Act, 18 U.S.C. §2713
- BSI C5:2020; ANSSI SecNumCloud 3.2; EU Cloud Code of Conduct
- AWS Service Control Policies and Resource Control Policies documentation
- AWS European Sovereign Cloud programme announcements (verify current availability)

## Confidence level

**High** — residency-failure modes, the boring-tier inventory, the CLOUD Act/key-custody logic, and the tiering model. These are stable, well-evidenced engineering and legal facts.

**Medium** — exact service parity between `eu-central-1` and `eu-north-1` at build time, and current availability/feature set of AWS European Sovereign Cloud. Both need verification against live provider documentation at implementation time.
