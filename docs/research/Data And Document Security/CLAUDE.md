# Project Context

**Baseline:** `docs/requirement-specification/PRD.md` (ComplianceIQ PRD v4.0) is the sole source of truth for this research set. Where research and PRD disagree, the PRD wins. Unresolved PRD questions stay unresolved here.

Platform:
ComplianceIQ — a B2B SaaS compliance testing platform for EU-licensed Crypto Asset Service Providers (CASPs). Two applications: the **Firm Application** (used by each client firm's compliance team) and the **Platform Admin Portal** (used by the Client's own team to build and maintain the regulatory testing content). The PRD's two-application description.

Regulations

- **Customer domain (principal):** MiCA (EU 2023/1114), DORA (EU 2022/2554) — PRD title block and the PRD's product overview
- **Platform's own processing:** GDPR, as a data processor under a DPA — the GDPR processor requirement
- **Adjacent / conditional, requiring legal confirmation before they drive any MVP scope:** NIS2, CRA, AI Act, AMLR, TFR, eIDAS 2, EU Data Act. None is confirmed applicable by the PRD.

Security requirements stated by the PRD

- Multi-tenant isolation — complete data partition per firm (the tenant isolation requirement)
- AES-256 at rest, TLS 1.3 in transit, per-firm encryption key (the encryption requirement)
- EU data residency; AWS, EU data centre, account owned solely by the Client (the EU residency requirement, the confirmed cloud decision)
- Immutable, append-only audit log with no admin delete or modify (the immutable audit requirement, the permanent audit log requirement, the PRD's data and retention table)
- Minimum six-year retention; evidence, results, reports and audit records cannot be deleted by anyone including administrators (the non-deletable retention requirement, the PRD's data and retention table)
- GDPR processor obligations under a DPA (the GDPR processor requirement)
- Role-based access across eight system roles, invitation-only accounts, phone-based MFA (the PRD's roles section)
- AI-assisted WSP-to-rule mapping only; output is advisory and requires human review plus the PRD-defined two-person sign-off (the advisory AI mapping requirement, the two-person mapping approval requirement); minimum 85% verified accuracy at UAT (the PRD's WSP mapping accuracy commitment)

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
- Control matrix traced to the PRD's stated requirements, named descriptively
- Risk register
- Reference architecture
- ADRs, with status reflecting actual approval state — not assumed acceptance

Folder layout

- **Top level** — the confirmed MVP security scope, one document per topic, filenames carry no numeric prefix. See `README.md` for the scope-item-to-document mapping.
- **`supporting-topics/`** — MVP-relevant depth outside the confirmed list (network security, Zero Trust, insider threat, data loss prevention, threat-modelling method, conditional cross-border analysis). Still cited by the control matrix, threat model and risk register.
- **`future-scope/`** — nothing in the MVP. Customer-managed encryption / HYOK, and the full deferred list.

Conventions when editing

- Every material finding carries **[PRD REQUIRED]**, **[PROPOSED]**, **[OPEN]** / **[OPEN — LEGAL]**, or **[FUTURE]**. There is no "Accepted" status anywhere in this set.
- Name the PRD requirement descriptively for anything marked **[PRD REQUIRED]** — quote the PRD wording where it settles the point. **Do not cite PRD requirement IDs or section numbers**; they change between PRD versions. The ID mapping lives in `REVIEW-TRACEABILITY.md` and nowhere else.
- Do not name a region, a compute platform, a database engine, a mesh, a policy engine, an AI provider or model, an RTO, an RPO or an availability figure beyond the 99.5% availability target already stated — those are open decisions.
- Owners are **roles to be assigned**, never named people or asserted job titles.
- `REVIEW-TRACEABILITY.md` records the PRD traceability, the withdrawn material and the restructure; keep it in step with any change here.
