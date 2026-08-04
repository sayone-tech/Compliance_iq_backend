# Project Context

**Baseline:** `docs/requirement-specification/PRD.md` (ComplianceIQ PRD v4.0) is the sole source of truth for this research set. Where research and PRD disagree, the PRD wins. Unresolved PRD questions stay unresolved here.

Platform:
ComplianceIQ — a B2B SaaS compliance testing platform for EU-licensed Crypto Asset Service Providers (CASPs). Two applications: the **Firm Application** (used by each client firm's compliance team) and the **Platform Admin Portal** (used by the Client's own team to build and maintain the regulatory testing content). PRD §1.1.

Regulations

- **Customer domain (principal):** MiCA (EU 2023/1114), DORA (EU 2022/2554) — PRD title block and §1
- **Platform's own processing:** GDPR, as a data processor under a DPA — PRD NFR-06
- **Adjacent / conditional, requiring legal confirmation before they drive any MVP scope:** NIS2, CRA, AI Act, AMLR, TFR, eIDAS 2, EU Data Act. None is confirmed applicable by the PRD.

Security requirements stated by the PRD

- Multi-tenant isolation — complete data partition per firm (NFR-01)
- AES-256 at rest, TLS 1.3 in transit, per-firm encryption key (NFR-02)
- EU data residency; AWS, EU data centre, account owned solely by the Client (NFR-03, TI-01)
- Immutable, append-only audit log with no admin delete or modify (NFR-04, FR-13, PRD §2)
- Minimum six-year retention; evidence, results, reports and audit records cannot be deleted by anyone including administrators (NFR-07, PRD §2)
- GDPR processor obligations under a DPA (NFR-06)
- Role-based access across eight system roles, invitation-only accounts, phone-based MFA (PRD §3)
- AI-assisted WSP-to-rule mapping only; output is advisory and requires human review plus the PRD-defined two-person sign-off (FR-31, FR-32); minimum 85% verified accuracy at UAT (PRD §6.2)

Security principles carried into this research

- Least privilege
- Encryption by default
- Privacy by design
- EU data residency
- Immutable audit and evidence records
- No production personal data in development or test environments
- No customer documents in developer AI tooling (this is distinct from the product's own AI mapping path — see `ai-governance`)
- Defence in depth on tenant isolation

Expected deliverables

- Security architecture (technology-neutral where the PRD has not chosen)
- Threat model
- Control matrix traced to PRD requirement IDs
- Risk register
- Reference architecture
- ADRs, with status reflecting actual approval state — not assumed acceptance

Folder layout

- **Top level** — the confirmed MVP security scope, one document per topic, filenames carry no numeric prefix. See `README.md` for the scope-item-to-document mapping.
- **`supporting-topics/`** — MVP-relevant depth outside the confirmed list (network security, Zero Trust, insider threat, data loss prevention, threat-modelling method, conditional cross-border analysis). Still cited by the control matrix, threat model and risk register.
- **`future-scope/`** — nothing in the MVP. Customer-managed encryption / HYOK, and the full deferred list.

Conventions when editing

- Every material finding carries **[PRD REQUIRED]**, **[PROPOSED]**, **[OPEN]** / **[OPEN — LEGAL]**, or **[FUTURE]**. There is no "Accepted" status anywhere in this set.
- Cite the PRD section or requirement ID for anything marked **[PRD REQUIRED]**.
- Do not name a region, a compute platform, a database engine, a mesh, a policy engine, an AI provider or model, an RTO, an RPO or an availability figure beyond NFR-08's 99.5% *target* — those are open decisions.
- Owners are **roles to be assigned**, never named people or asserted job titles.
- `REVIEW-TRACEABILITY.md` records the PRD traceability, the withdrawn material and the restructure; keep it in step with any change here.
