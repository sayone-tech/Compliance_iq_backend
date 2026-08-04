# Data Residency

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](future-scope/future-and-optional-scope.md).

## What the PRD fixes, and what it leaves open

| Settled by the PRD | Not settled by the PRD |
|---|---|
| All client data stored in **EU-based data centres** (NFR-03) | Which EU region or regions **[OPEN]** |
| Cloud provider is **AWS** (TI-01) | Whether a second EU region is used for backup or DR **[OPEN]** |
| The AWS account is **owned solely by the Client**, not SayOne (TI-01) | How infrastructure is provisioned into, and handed over inside, a Client-owned account **[OPEN]** |
| GDPR processor position (NFR-06) | Where development, support and administration are physically performed **[OPEN]** — see `cross-border-data-processing` |
| Multi-tenant isolation (NFR-01) | Any residency product tiering — none exists in the PRD **[FUTURE]** |

**Consequence of Client-sole account ownership.** Every recommendation below is a recommendation for how the *Client's* AWS organisation should be configured. Provisioning model, role handover, break-glass custody and who holds the root credentials are commercial and operational questions the PRD does not answer. **[OPEN]**

## Best practices

- **Residency is not a region setting.** It is the property that *every* copy, derivative, index, cache, log, backup, key and human eyeball stays inside the declared boundary. Most residency failures are in the unglamorous tier: telemetry, error tracking, email, CDN edge, DNS logs, support tooling and the vendor's own control plane.
- **Enumerate the full data-flow inventory before choosing a region.** For each data class: where written, where replicated, where indexed, where cached, where logged, where backed up, who can read it, and from which country.
- **Pin regions explicitly and enforce with policy.** Never rely on defaults. Deny non-EU regions at the organisation level.
- **Treat metadata as data.** Filenames, firm names, document titles, extracted text, embeddings, log lines and search index entries carry confidential content. Embeddings should be treated as personal data.
- **Support access is the hardest part.** A follow-the-sun support model with engineers reading production logs from outside the EU defeats a residency claim regardless of where the bytes live. See `cross-border-data-processing`.

## EU regulatory implications

- **GDPR** does not mandate EU residency; it mandates lawful transfer (Chapter V) and appropriate security (Art. 32). **The PRD mandates EU residency independently, in NFR-03** — so it is a hard requirement here regardless of the GDPR analysis.
- **DORA Art. 28–30** (customer-side): customers must consider where ICT services are provided and data is processed, record data locations in their register of information, and be notified before those locations change. Publishing authoritative region and sub-processor information is therefore useful to customers. Whether that becomes a product feature is **[OPEN]**.
- **MiCA Art. 68/73** (customer-side): CASPs must ensure continuity and supervisory access to records.
- **Third-country access law.** US CLOUD Act exposure via a US-parent provider is the standard objection to hyperscaler residency claims. **The PRD selects AWS (TI-01), so this objection is accepted by the Client at the baseline.** Key-custody responses to it are **[FUTURE]** (appendix 39).

## Recommended architecture

### Region policy **[PROPOSED, implementing NFR-03]**

- **Select an EU region and record the selection as a decision.** Selection criteria, in priority order: presence of every AWS service the design depends on; three availability zones; support for object-lock/WORM storage and KMS features needed for NFR-04 and NFR-07; latency to the customer base (EU CASPs, PRD §1); Client preference. **No region is selected in this research set.** **[OPEN]**
- If a second EU region is used for backup copies or recovery, apply the same criteria and verify service parity against the primary. **[PROPOSED]** — necessity and cost are a Client decision **[OPEN]**.
- **Hard region lockdown, technically enforced:**
  - An organisation-level policy denying actions where the requested region is outside the approved EU set, with a narrow allowlist for genuinely global services (IAM, Organizations, CDN, DNS, global WAF scope).
  - Resource-side policies restricting object storage, key management and token services to organisation principals and EU network paths.
  - Region and organisation conditions on every bucket policy and key policy.
  - CI fails on any infrastructure plan referencing a non-approved region.

### AI inference residency **[PROPOSED, supporting FR-31]**

The product's only AI feature is AI-assisted WSP-to-rule mapping (PRD §6.2). Requirement, stated as an outcome rather than a product:

> Inference must run on EU-resident infrastructure under terms that provide **no training on inputs or outputs and no provider-side retention**, and must be reachable without customer document content leaving the EU boundary.

Candidates that can satisfy this include an EU-region managed inference service on the selected cloud, or an EU-hosted open-weight model. **No provider or model is selected by the PRD, and none is selected here.** **[OPEN]** — see `ai-governance` and question T-4 in `open-questions`.

### The unglamorous tier — where residency actually fails **[PROPOSED]**

| Component | Requirement | Note |
|---|---|---|
| Observability (metrics, logs, traces) | EU-hosted, EU-only storage | Self-hosted in-region, or a vendor with contractually EU-only tenancy |
| Error tracking | EU tenancy; strip request bodies before send | |
| Email / notifications | EU sending infrastructure. PRD FR-59 sends reports to distribution lists and PRD §12 sends alerts by email | Report *content* leaving by email is a design decision to review — prefer link-plus-authentication over attachment |
| Support / ticketing | EU tenancy; no customer documents attached, reference by ID only | |
| CDN | EU points of presence for authenticated content, or serve authenticated content from the region directly | |
| Search index | In-region, encrypted with the tenant key | |
| Text extraction / OCR output | In-region; inherits the source document's classification (FR-30 requires OCR of scanned PDFs) | |
| Embeddings / vector store | In-region; treated as personal data | Only if the WSP mapping design uses retrieval |
| Backups | EU only; never a globally-replicated bucket | |
| DNS / WAF logs | EU log destination | |
| CI/CD | EU-resident runners for anything touching production configuration | See `secure-cicd` |

### Portability **[PROPOSED]**

Portability is worth engineering because the Client owns the account and the IP (TI-01, CC-03) and may later move or re-host. Keep the crypto layer, object access and data layer behind thin interfaces, and keep infrastructure as code with the provider isolated. This is a design discipline, not a product commitment. **No sovereign-cloud or alternative-provider offering is in scope.** **[FUTURE]**

### Machine-readable residency attestation

A customer-facing endpoint publishing regions, sub-processors and data classes per tenant is useful for customers' DORA registers — but it is a customer-facing assurance feature the PRD does not include. **[FUTURE]**

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| A "boring tier" service silently stores data outside the EU | Breach of NFR-03 | Component-by-component residency review recorded in a register; vendor intake gate (`supply-chain-security`) |
| Global or edge services replicating metadata outside the EU | Metadata leaves the EU | Explicit per-service review; disable global tables; geo-restrict distributions |
| Region chosen implicitly by whoever provisions first | Unreviewed residency posture, possible non-EU default | Deny non-EU regions at the organisation level before any workload exists (`deployment-recommendations` §1) |
| Support or administration performed from outside the EU | Possible unlawful transfer plus residency breach | Log redaction at source (`audit-logging`); access-location policy (`identity-and-access-management`); see `cross-border-data-processing` |
| Backup or replica placed outside the EU | Residency breach | Policy restricting replication destinations; continuous conformance scanning |
| Embeddings or extracted text treated as "not personal data" | Unlawful processing, reidentification | Classify derivatives at the source document's level (`document-confidentiality`) |
| Region-parity gap forces a non-EU fallback under pressure | Emergency non-compliance | Pre-validate every service in any secondary region; no undocumented fallbacks |
| Residency overclaimed in customer-facing material | Misrepresentation | Legal review of any residency or sovereignty claim before publication |

## Trade-offs

- **Single EU region vs. primary plus a second EU region for backups.** A single region is simpler and cheaper; a second region protects against regional loss and is the conventional answer for a six-year non-deletable record store. **The PRD sets no recovery target and no DR requirement.** Recommendation: cost the second-region backup copy and put it to the Client as an explicit decision. **[OPEN]**
- **Self-hosted observability (residency-clean, operationally heavy) vs. EU-tenancy SaaS (fast, adds a sub-processor).** Recommendation: EU-tenancy SaaS with a contractual EU-only storage term for speed; record it in the sub-processor register. **[PROPOSED]**
- **Per-tenant regional placement vs. a single-region fleet.** Per-tenant placement multiplies operational surface. Recommendation: single region for the whole fleet. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification | Basis |
|---|---|---|---|
| DD-02-01 | All client data, and every derivative of it, resides in EU data centres | **[PRD REQUIRED]** | NFR-03 |
| DD-02-02 | Cloud provider is AWS, on an account owned solely by the Client | **[PRD REQUIRED]** | TI-01 |
| DD-02-03 | Specific region(s) are selected against documented criteria and recorded as a decision; none is selected here | **[OPEN]** | — |
| DD-02-04 | Region restriction is enforced technically by organisation and resource policies, not by convention; CI fails on non-approved regions | **[PROPOSED]** | implements NFR-03 |
| DD-02-05 | Observability, error tracking, email, support tooling and CI are subject to the same residency review as the data plane, each with a named EU-resident implementation in the sub-processor register | **[PROPOSED]** | implements NFR-03 |
| DD-02-06 | Extracted text, OCR output, embeddings, search index entries, filenames and document titles are classified at the same sensitivity as the source document | **[PROPOSED]** | implements NFR-01/NFR-03 |
| DD-02-07 | AI inference for WSP mapping runs EU-resident under no-training, no-retention terms; provider and model are not selected here | **[PROPOSED / OPEN]** | supports FR-31 |
| DD-02-08 | Portability is maintained as a design discipline (thin provider interfaces, infrastructure as code); no alternative-provider or sovereign offering is in scope | **[PROPOSED]** | CC-03 context |

## References

- Regulation (EU) 2016/679 (GDPR) Chapter V, Art. 32
- Regulation (EU) 2022/2554 (DORA) Art. 28–30 (customer-side data-location obligations)
- CJEU C-311/18 (*Schrems II*); EDPB Recommendations 01/2020 on supplementary measures
- US CLOUD Act, 18 U.S.C. §2713 (context for the residency-versus-key-custody discussion)
- BSI C5:2020; ANSSI SecNumCloud 3.2 — usable assurance references
- AWS Service Control Policies and Resource Control Policies documentation

## Confidence level

**High** — the residency failure modes, the derivative-inventory discipline, and the enforcement model.

**Medium** — which specific services will and will not be available in a given EU region at build time; verify against live provider documentation once the region is chosen.

**Open** — region selection, second-region use, and the provisioning/handover model inside a Client-owned AWS account.
