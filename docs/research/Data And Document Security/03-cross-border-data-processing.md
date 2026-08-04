
# 03 — Cross-Border Data Processing (EU ⇄ India)

This is the single highest-risk area in the whole architecture: development in India, production in the EU, regulated financial data in between. Get this wrong and every other control is decoration.

## The legal position, stated plainly

India has **no adequacy decision** under GDPR Art. 45. Every transfer of personal data from the EU to India — including *remote access* by an Indian-based engineer to data stored in Frankfurt — is a **restricted transfer** under Chapter V and requires an Art. 46 transfer tool plus, per *Schrems II*, a documented **Transfer Impact Assessment (TIA)** and supplementary measures where the assessment shows third-country law undermines the tool.

**Remote access is a transfer.** Viewing a production log line from Kochi is a transfer even though the bytes never persist in India. This is settled EDPB interpretation and the most commonly ignored fact in offshore development models.

## Best practices

- **Eliminate the transfer rather than legalise it.** The strongest control is architectural: Indian engineers never have access to EU production personal data. A transfer that cannot happen needs no TIA.
- **Where access is unavoidable, make it EU-resident-in-fact:** EU-hosted virtual desktops, no local persistence, no clipboard/file egress, session recording, time-boxed just-in-time grants with EU approval.
- **Hold the keys where the law you want to apply is.** Encryption only defeats a foreign access demand if the recipient of the demand cannot produce the plaintext. Key custody, not encryption, is the sovereignty control.
- **Separate the "development" transfer from the "support" transfer.** Development needs no personal data at all (synthetic only). Support occasionally needs real data. Different risk, different controls, different legal basis — do not merge them into one blanket authorisation.
- **Document the TIA before the first line of code**, not at the first customer security review.

## EU regulatory implications

### GDPR Chapter V

- **Art. 46(2)(c) — Standard Contractual Clauses**, Commission Implementing Decision (EU) 2021/914. Module selection matters:
  - EU customer (controller) → us (EU processor): **no SCCs**, an Art. 28 DPA suffices.
  - Us (EU processor) → Indian development entity (sub-processor): **Module 3 (processor-to-processor)**.
  - If the Indian entity is the contracting party with the customer: Module 2 (controller-to-processor). Avoid this structure.
- **Art. 28(2)/(4)** — general written authorisation for sub-processors, with advance notice of changes and a right to object. The Indian entity **must be named in the sub-processor list**. Hiding an offshore development arm is a contractual and regulatory landmine, and it will surface in a DORA Art. 28(3) register review.
- **Transfer Impact Assessment** per EDPB Recommendations 01/2020: assess Indian law for public-authority access that exceeds what is "necessary and proportionate in a democratic society", then apply supplementary measures.
- **Art. 32 / Art. 25** — security and data protection by design apply to the transfer channel itself.
- **Art. 44 anti-circumvention** — you cannot lower protection by routing through a third country.

### Indian law relevant to the TIA (be honest about this)

- **Information Technology Act 2000, s.69 / s.69B** — powers of interception, monitoring and decryption; s.69(3) can compel a person in charge of a computer resource to extend decryption assistance, with criminal penalty for refusal.
- **Telecommunications Act 2023, s.20(2)** — interception and message-suspension powers, with a definition of telecommunication services broad enough to create uncertainty for some service categories.
- **Digital Personal Data Protection Act 2023 (DPDP)** — India's own data protection statute; rules were notified with phased implementation running into 2026–2027. It provides genuine obligations for the Indian entity (security safeguards, breach notification, purpose limitation) but **s.36 permits the Central Government to require information from any data fiduciary**, and government exemptions under s.17 are broad. *Verify the current commencement status of specific DPDP Rules provisions at implementation time.*
- **No independent judicial authorisation** for several of these powers, and limited effective redress for non-nationals. A candid TIA will conclude that **Indian law does not provide protection essentially equivalent to EU law for compelled access**, and therefore supplementary measures are **required**, not optional.

The honest conclusion: **SCCs alone are insufficient for EU→India transfers of confidential regulated financial data. The supplementary measures must be technical and must be strong enough that the Indian entity cannot produce plaintext even under compulsion.**

### DORA and MiCA overlay

- **DORA Art. 28(2)/29** — customers must assess the country where ICT services are performed. "Development in India" is a disclosable fact that will appear in their register of information and their concentration-risk analysis. Disclose it proactively; discovering it late destroys trust.
- **DORA Art. 30(3)(e)/(f)** — audit and access rights must extend to subcontractors, including the Indian entity, and to competent authorities. The Indian entity must be contractually bound to accept EU regulator inspection.
- **Commission Delegated Regulation (EU) 2024/1773** — conditions for subcontracting ICT services supporting critical or important functions; the subcontracting chain must be assessed, monitored and contractually controlled end to end.
- **MiCA Art. 73** — outsourcing does not transfer responsibility; the CASP must be able to demonstrate control over the whole chain.

## Recommended architecture

**Principle: three concentric zones, with a hard, technically-enforced boundary between them.**

```
Zone D (India)              Zone S (EU staging)          Zone P (EU production)
Development                 Pre-production               Live customer data
─────────────────           ─────────────────            ─────────────────
Synthetic data only         Synthetic + masked data      Real customer data
Full engineer access        Full engineer access         NO standing access
Source code, IaC            Full stack, EU-hosted        Break-glass only
Claude Code permitted       Claude Code permitted        Claude Code forbidden
```

### Zone D — Indian development environment

- **Synthetic data only.** A generated corpus of fake documents, fake customer records, fake evidence — realistic in structure and volume, containing zero real personal data. Generated by a fixture factory in CI, never derived from production by masking (masking failures are the classic leak path).
- **No production credentials on developer machines.** Ever. Enforced by: no long-lived cloud keys (OIDC only), secret scanning, and a deny-by-default egress proxy.
- **Managed endpoints:** company-owned devices, full-disk encryption, EDR, MDM, disk-level DLP, no removable media, screen-lock policy, no personal cloud sync clients.
- **Source code access is itself a control question.** Source code is our IP and contains security-relevant logic, but it is not customer personal data. Full access for Zone D is acceptable; production configuration and secrets are not.
- **Claude Code governance** — see doc 05. Summary: permitted in Zone D against synthetic data only, with managed settings enforcing deny rules and telemetry controls.

### Zone S — EU staging

- Hosted in `eu-central-1`, full architectural parity with production, **synthetic or fully anonymised data only**. Indian engineers access it over SSO+FIDO2. This is where integration testing, load testing and pre-release verification happen with realistic infrastructure but no real data — so a compromise of an Indian workstation cannot yield customer data.

### Zone P — EU production

- **No standing human access. None.** Not for developers, not for SREs, not for the CTO. Deployment is via pipeline identity only.
- **Break-glass access model** for the genuine emergency:
  1. Incident ticket with justification.
  2. **EU-resident approver** (dual approval: one EU security, one EU engineering lead). Approval by an India-based person is not valid for personal-data access.
  3. Access granted **only through an EU-hosted virtual desktop** (Amazon WorkSpaces / AppStream 2.0 in `eu-central-1`) with clipboard, printing, USB redirection and local drive mapping **disabled**.
  4. Session is **fully recorded** (SSM Session Manager logging to a WORM bucket, plus WorkSpaces session capture).
  5. Time-boxed to ≤4 hours, auto-revoked, with a mandatory post-access review.
  6. Every break-glass event is a logged, reviewed, reported metric — trend it, and drive it toward zero.
- **Preference order for production debugging** (each step avoids a transfer):
  1. Redacted/structured logs and metrics — no personal data (doc 14).
  2. Aggregated, differentially noisy analytics.
  3. Synthetic reproduction of the fault in Zone S.
  4. EU-resident engineer performs the investigation.
  5. Break-glass VDI for an India-based engineer — last resort, exceptional, recorded.
- **Data-class gating:** even under break-glass, document *contents* (uploaded PDFs, KYC images) are a separate, higher-privilege class requiring a customer-notification commitment. Metadata-only break-glass is the default grant.

### Legal and contractual scaffolding

1. **Intra-group Data Transfer Agreement** incorporating SCCs Module 3 (EU entity processor → Indian entity sub-processor), unmodified, with the required annexes (technical and organisational measures described accurately, not aspirationally).
2. **Transfer Impact Assessment** covering IT Act s.69/69B, Telecommunications Act 2023 s.20, DPDP s.36/s.17, practical likelihood of access, and the supplementary measures below. Reviewed annually and on legal change.
3. **Supplementary measures** (EDPB 01/2020 taxonomy):
   - *Technical:* production data never accessible in India in plaintext by design; EU-held encryption keys the Indian entity cannot access; EU-hosted VDI with egress controls; end-to-end encryption with EU-side key custody; strong pseudonymisation for anything that does cross.
   - *Contractual:* transparency obligation on government access requests, challenge-and-notify commitments, warrant canary, audit rights, prohibition on responding to foreign requests without EU-entity instruction.
   - *Organisational:* documented access policy, EU-resident approver requirement, mandatory training, internal escalation path, annual attestation.
4. **Sub-processor disclosure**: the Indian entity is publicly listed with its role ("software development and, exceptionally, remote technical support under EU supervision") and its country.
5. **Government access request playbook**: any request received by the Indian entity is escalated immediately to the EU entity DPO and legal, challenged where lawful, customers notified where permitted.
6. **DORA subcontractor addendum**: audit/inspection rights for customers and competent authorities extended to the Indian entity, with cooperation obligations.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Remote access treated as "not a transfer" | Unlawful transfer, supervisory-authority enforcement, customer contract breach | Explicit policy statement; TIA covers remote access; access controls assume transfer |
| Production data copied to Zone D for debugging ("just this once") | Direct unlawful transfer and residency breach | No prod credentials in Zone D; egress DLP; export from prod requires the same break-glass path |
| Masked production data used as a test corpus, masking is incomplete | Reidentification, silent breach | Ban production-derived test data outright; synthetic-only |
| Indian entity receives a lawful-access demand it cannot disclose | Undetectable disclosure | Key custody in EU so plaintext cannot be produced; warrant canary; minimise what is reachable |
| Customer discovers Indian development late in procurement | Deal loss, trust damage, DORA register inaccuracy | Proactive disclosure in the security pack from day one |
| Break-glass becomes routine (used weekly) | Effective standing access with extra paperwork; audit finding | Hard cap and trend metric; every use reviewed by security; >2/month triggers root-cause work |
| Claude Code session in Zone D receives real customer content pasted by a developer | Transfer to a third-party AI provider **and** to India | Managed settings deny rules, DLP on paste, training, synthetic-only culture (doc 05) |
| SCCs signed but annexes describe measures that are not implemented | Contract is evidence *against* us | Annex II generated from the actual control set and reviewed with each release |

## Trade-offs

- **Zero-access model (strongest) vs. supervised access (faster incident resolution).** Zero-access materially slows some production incidents and requires investment in redacted observability and synthetic reproduction. That investment is exactly what a regulated buyer expects. **Recommendation: zero standing access + engineered break-glass; fund the observability work that makes it viable.**
- **Hire EU-resident SREs (expensive) vs. rely on break-glass from India (cheap, risky).** A small EU on-call capability (2–3 people, or an EU MSP) removes the highest-risk transfer scenario entirely. **Recommendation: budget for EU-resident production on-call before the first enterprise customer goes live.**
- **Synthetic data (safe, effort to build) vs. anonymised production data (realistic, leak-prone).** Synthetic corpora take real engineering effort to make representative. **Recommendation: synthetic, invested in properly, with a documented realism review.**
- **VDI (controllable, latency, licence cost) vs. bastion+SSH (cheap, weak egress control).** **Recommendation: VDI for anything touching personal data; bastion acceptable for metadata-only operations.**
- **Disclose India development prominently vs. minimally.** Prominent disclosure costs some early deals and wins the ones that matter, because it survives due diligence. **Recommendation: prominent, with the control narrative attached.**

## Design decisions

- **DD-03-01:** Remote access from India to EU production personal data is classified as an international transfer and governed accordingly. Written into policy.
- **DD-03-02:** Development and test environments contain **synthetic data only**. Production-derived data — masked or not — is prohibited in non-production environments.
- **DD-03-03:** Zero standing human access to production. Break-glass only, dual-approved by two EU-resident approvers, EU-hosted VDI, egress-disabled, session-recorded, ≤4 hours, auto-revoked.
- **DD-03-04:** Encryption keys for customer document content are held such that the Indian entity has no access path, technical or administrative.
- **DD-03-05:** SCCs Module 3 executed between the EU entity and the Indian entity, with a TIA maintained and reviewed annually; Annex II generated from the live control inventory.
- **DD-03-06:** The Indian development entity is publicly disclosed as a sub-processor from launch.
- **DD-03-07:** EU-resident production on-call capability is a launch prerequisite for the first enterprise customer, not a later hire.
- **DD-03-08:** Government access request playbook maintained and tested annually in both entities.

## References

- Regulation (EU) 2016/679, Chapter V (Art. 44–49), Art. 28, Art. 32
- Commission Implementing Decision (EU) 2021/914 — Standard Contractual Clauses (Modules 2 and 3)
- CJEU C-311/18 *Data Protection Commissioner v Facebook Ireland and Schrems* (*Schrems II*)
- EDPB Recommendations 01/2020 on measures that supplement transfer tools, v2.0 (18 June 2021)
- EDPB Recommendations 02/2020 on the European Essential Guarantees for surveillance measures
- EDPB Guidelines 05/2021 on the interplay between Art. 3 and Chapter V
- Regulation (EU) 2022/2554 (DORA) Art. 28–30; Commission Delegated Regulation (EU) 2024/1773
- Information Technology Act 2000 (India), s.69, s.69B; Telecommunications Act 2023 (India), s.20
- Digital Personal Data Protection Act 2023 (India) — verify current rule commencement status

## Confidence level

**High** — that remote access constitutes a transfer, that SCCs alone are insufficient for India, that key custody is the decisive supplementary measure, and that the zone model is the correct architectural response. These follow directly from *Schrems II* and EDPB guidance.

**Medium** — the precise current commencement status and operative detail of the Indian DPDP Rules, and how individual EU supervisory authorities would weigh a well-implemented VDI-plus-key-custody model. Have Indian and EU counsel review the TIA; do not rely on this document as legal advice.
