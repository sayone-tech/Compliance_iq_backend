# Cross-Border Data Processing and Offshore Access

> **Baseline:** PRD v4.0. **[PRD REQUIRED]** · **[PROPOSED]** · **[OPEN]** · **[FUTURE]** — see [Future and Optional Scope](../future-scope/future-and-optional-scope.md).

## Status of this document — read first

**The PRD does not state where development, support or administration of ComplianceIQ is performed.** It states only that client data is stored in EU data centres (the EU residency requirement) on an AWS account owned solely by the Client (the confirmed cloud decision), and that SayOne acts as a GDPR processor under a DPA (the GDPR processor requirement).

Therefore everything below is **conditional**. It applies *if and to the extent that* any person outside the EU/EEA can reach EU production personal data — including by viewing a log line, opening a support ticket containing document content, or holding a production credential.

**The operating model is an open question.** Two things must be established with the Client and with counsel before this document can be closed out:

1. **Where will development, support and production administration be performed?** **[OPEN]**
2. **If any of it is outside the EU/EEA, in which country, and what is the transfer position?** **[OPEN — LEGAL]**

Until those are answered, the safe engineering position is the one this document describes: build so that **no production personal data is reachable from outside the EU/EEA at all**, because a transfer that cannot happen needs no transfer analysis. That position is inexpensive to adopt early and expensive to retrofit.

## The legal position, stated plainly

Where a third country has no adequacy decision under GDPR Art. 45, every transfer of personal data from the EU to that country — **including remote access by an engineer located there to data stored in the EU** — is a restricted transfer under Chapter V. It requires an Art. 46 transfer tool plus, per *Schrems II*, a documented Transfer Impact Assessment and supplementary measures where third-country law undermines the tool.

**Remote access is a transfer.** Viewing a production log line from outside the EU is a transfer even though the bytes never persist there. This is settled EDPB interpretation and the most commonly overlooked fact in offshore delivery models.

## Best practices

- **Eliminate the transfer rather than legalise it.** The strongest control is architectural: non-EU personnel never have access to EU production personal data.
- **Where access is genuinely unavoidable, make it EU-resident in fact:** EU-hosted virtual desktop, no local persistence, no clipboard or file egress, session recording, time-boxed just-in-time grants approved by an EU-resident approver.
- **Separate the development transfer from the support transfer.** Development needs no personal data at all — synthetic only. Support occasionally needs real data. Different risk, different controls, different authorisation. Do not merge them into a blanket permission.
- **Document the transfer position before writing code that assumes an answer**, not at the first customer security review.

## EU regulatory implications

### GDPR Chapter V (conditional)

- **Art. 46(2)(c) — Standard Contractual Clauses**, Commission Implementing Decision (EU) 2021/914. Module selection depends on the contracting structure:
  - EU customer (controller) → EU processor: no SCCs, an Art. 28 DPA suffices — this is the GDPR processor requirement relationship.
  - EU processor → non-EU affiliate acting as sub-processor: Module 3 (processor-to-processor).
- **Art. 28(2)/(4)** — general written authorisation for sub-processors, advance notice of changes, right to object. **Any non-EU delivery entity must be named in the sub-processor list.** Omitting it is a contractual and regulatory exposure that surfaces during customer due diligence.
- **Transfer Impact Assessment** per EDPB Recommendations 01/2020: assess the destination country's public-authority access powers against the European Essential Guarantees, then apply supplementary measures.
- **Art. 44 anti-circumvention** — protection cannot be lowered by routing through a third country.

### DORA and MiCA overlay (customer-side)

- **DORA Art. 28(2)/29** — customers assess the country where ICT services are performed. The place of development and support is a disclosable fact that appears in their register of information. Disclose proactively; discovering it late damages trust.
- **DORA Art. 30(3)(e)/(f)** — where these terms are contracted, audit and access rights extend to subcontractors.
- **MiCA Art. 73** — outsourcing does not transfer responsibility; the CASP must demonstrate control over the whole chain.

## Recommended architecture

**Principle: three zones with a technically enforced boundary.** **[PROPOSED]**

```
Zone D — Development                Zone S — EU pre-production        Zone P — EU production
────────────────────                ──────────────────────────        ──────────────────────
Synthetic data only                 Synthetic / anonymised only       Real customer data
Full engineer access                Full engineer access              No standing human access
Source code, infrastructure code    Full stack, EU-hosted             Pipeline identity only
AI coding tools permitted           AI coding tools permitted         AI coding tools forbidden
```

The zone model is worth adopting **even if all delivery is EU-resident**, because it also serves the tenant isolation requirement (isolation), the immutable audit requirement (audit integrity) and insider-risk control (`insider-threat-protection`). Its cost is low and it removes the transfer question entirely for development.

### Zone D — development environment **[PROPOSED]**

- **Synthetic data only.** A generated corpus of fake firms, staff records, WSP documents and evidence files — realistic in structure, volume and file type (the accepted evidence file type lists PDF, DOCX, XLSX, PNG/JPG, MP3/WAV, MP4/MOV/AVI, screen recordings, ZIP, CSV) but containing zero real personal data. Generated by a fixture factory, never derived from production by masking — masking failures are the classic leak path.
- **No production credentials on developer machines.** Enforced by federated short-lived credentials only, secret scanning, and a deny-by-default egress proxy.
- **Managed endpoints:** company-owned devices, full-disk encryption, endpoint detection, device management, no removable media, no personal cloud sync clients.
- **Source code access** is acceptable in Zone D. Source code is the Client's IP under the IP ownership term, not customer personal data; production configuration and secrets are a separate matter and are not present.
- **AI coding tool governance** — `ai-governance`.

### Zone S — EU pre-production **[PROPOSED]**

Full architectural parity with production, hosted in the EU, **synthetic or fully anonymised data only**. This is where integration and pre-release verification happen against realistic infrastructure without real data, so a compromised workstation cannot yield customer data.

### Zone P — EU production **[PROPOSED]**

- **No standing human access.** Deployment via pipeline identity only.
- **Break-glass model for genuine emergencies:**
  1. Incident record with justification.
  2. Dual approval; where any approver or requester is outside the EU/EEA, at least the approver must be EU-resident for personal-data access.
  3. Access only through an EU-hosted virtual desktop with clipboard, printing, USB redirection and local drive mapping disabled.
  4. Session fully recorded to immutable storage.
  5. Time-boxed and auto-revoked; mandatory post-access review.
  6. Every break-glass event logged, reviewed and trended toward zero.
- **Preference order for production debugging**, each step avoiding a transfer: redacted structured logs and metrics (`audit-logging`) → aggregated analytics → synthetic reproduction in Zone S → EU-resident engineer investigates → break-glass virtual desktop as the last resort.
- **Data-class gating:** even under break-glass, evidence file *contents* are a higher-privilege class than metadata. Metadata-only is the default grant.

> **Not assumed here:** that EU-resident production on-call staff will be hired or contracted. That is a cost and operating-model decision for the Client and is recorded as an open question (`open-questions`, O-1). The architecture above is designed so that the amount of EU-resident cover needed is as small as possible.

### Legal and contractual scaffolding (only if delivery is partly non-EU) **[PROPOSED / OPEN]**

1. **Data transfer agreement** incorporating SCCs Module 3, with annexes describing the technical and organisational measures **accurately, not aspirationally**.
2. **Transfer Impact Assessment** covering the destination country's interception, monitoring and compelled-decryption powers, the practical likelihood of access, and the supplementary measures below. Reviewed annually and on legal change.
3. **Supplementary measures** (EDPB 01/2020 taxonomy):
   - *Technical:* production personal data not accessible outside the EU in plaintext by design; encryption keys held such that the non-EU entity has no access path; EU-hosted virtual desktop with egress controls; strong pseudonymisation for anything that does cross.
   - *Contractual:* transparency on government access requests, challenge-and-notify commitments, audit rights, prohibition on responding to foreign requests without EU-entity instruction.
   - *Organisational:* documented access policy, EU-resident approver requirement, training, escalation path, periodic attestation.
4. **Sub-processor disclosure** naming any non-EU delivery entity, its role and its country.
5. **Government access request playbook**, escalating any request to the DPO and legal, challenged where lawful, customers notified where permitted.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Remote access treated as "not a transfer" | Unlawful transfer; customer contract breach | Explicit policy statement; access controls assume transfer; TIA covers remote access |
| Production data copied to a development environment "just this once" | Direct unlawful transfer and breach of the EU residency requirement | No production credentials in Zone D; egress controls; export from production requires the same break-glass path |
| Masked production data used as a test corpus, masking incomplete | Reidentification, silent breach | Ban production-derived test data outright; synthetic only |
| Non-EU entity receives a lawful-access demand it cannot disclose | Undetectable disclosure | Keys held in the EU so plaintext cannot be produced; minimise what is reachable |
| Customer discovers a non-EU delivery arrangement late in procurement | Deal loss, trust damage, inaccurate customer register of information | Proactive disclosure in the security pack from day one |
| Break-glass becomes routine | Effective standing access with extra paperwork | Hard cap and trend metric; every use reviewed; a threshold that triggers root-cause work |
| Customer document content pasted into a developer AI tool | Transfer to a third-party AI provider, and possibly to a third country | Managed tool settings, paste-pattern blocking, synthetic-only culture (`ai-governance`) |
| SCC annexes describe measures that are not implemented | The contract becomes evidence against you | Generate the annex from the actual control set and review it each release |

## Trade-offs

- **Zero-access model vs. supervised access.** Zero access materially slows some production incidents and requires investment in redacted observability and synthetic reproduction. That investment is exactly what a regulated buyer expects. Recommendation: zero standing access plus engineered break-glass. **[PROPOSED]**
- **EU-resident production cover vs. break-glass from wherever the team is.** EU-resident cover removes the highest-risk transfer scenario entirely; it has a real cost. **The PRD does not fund or require it.** Recommendation: put the cost and the residual risk to the Client as an explicit decision. **[OPEN]**
- **Synthetic data vs. anonymised production data.** Synthetic corpora take real effort to make representative — particularly for the media formats in the accepted evidence file type list. Recommendation: synthetic, invested in properly. **[PROPOSED]**
- **Virtual desktop vs. bastion and SSH.** Recommendation: virtual desktop for anything touching personal data; bastion acceptable for metadata-only operations. **[PROPOSED]**

## Design decisions

| ID | Decision | Classification | Basis |
|---|---|---|---|
| DD-03-01 | Remote access from outside the EU/EEA to EU production personal data is classified as an international transfer and governed accordingly | **[PROPOSED — LEGAL]** | GDPR Ch. V |
| DD-03-02 | Development and test environments contain synthetic data only; production-derived data, masked or not, is prohibited outside production | **[PROPOSED]** | supports the tenant isolation requirement, the EU residency requirement |
| DD-03-03 | Zero standing human access to production; break-glass only, dual-approved, EU-hosted virtual desktop, egress disabled, session recorded, time-boxed, auto-revoked | **[PROPOSED]** | supports the immutable audit requirement, the permanent audit log requirement |
| DD-03-04 | Encryption keys for customer document content are held so that no non-EU entity has an access path, technical or administrative | **[PROPOSED]** | supports the encryption requirement |
| DD-03-05 | If any delivery entity is outside the EU/EEA: SCCs Module 3 executed, TIA maintained and reviewed annually, annexes generated from the live control inventory | **[OPEN — LEGAL]** | conditional |
| DD-03-06 | Any non-EU delivery entity is disclosed as a sub-processor from launch | **[PROPOSED]** | GDPR Art. 28 |
| DD-03-07 | Where EU-resident production cover is required to make the zero-access model workable, the cost and the alternative are put to the Client as an explicit decision | **[OPEN]** | — |
| DD-03-08 | Government access request playbook maintained and tested in every entity that could receive one | **[PROPOSED]** | — |

## References

- Regulation (EU) 2016/679, Chapter V (Art. 44–49), Art. 28, Art. 32
- Commission Implementing Decision (EU) 2021/914 — Standard Contractual Clauses (Modules 2 and 3)
- CJEU C-311/18 (*Schrems II*)
- EDPB Recommendations 01/2020 on supplementary measures, v2.0 (18 June 2021)
- EDPB Recommendations 02/2020 on the European Essential Guarantees
- EDPB Guidelines 05/2021 on the interplay between Art. 3 and Chapter V
- Regulation (EU) 2022/2554 (DORA) Art. 28–30 (customer-side)

## Confidence level

**High** — that remote access constitutes a transfer, that a transfer tool alone is often insufficient without technical supplementary measures, and that the zone model is the correct architectural response.

**Not determined** — the actual delivery topology for this project, the destination country if any, and therefore the transfer analysis itself. This document is engineering research, not legal advice; the transfer position requires qualified counsel in both jurisdictions once the operating model is fixed.
