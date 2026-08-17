# DORA vs WSP — Applicability Analysis (Section 9 input)

**Date of research:** 2026-08-17
**Author:** Research subagent (web research task: DORA vs WSP)
**Status of law:** DORA (Regulation (EU) 2022/2554) applies in full since **17 January 2025**. First-batch RTS/ITS in force since 17 Jan 2025; second batch (incident reporting, TLPT, subcontracting) applicable during 2025.

**Terminology caveat (critical):** "WSP" in this product means a firm's **Written Supervisory Procedures manual** — a document type originating in **US FINRA broker-dealer regulation** (FINRA Rule 3110(b)). The two sample PDFs in this repo ("Sample WSP.pdf", "WSP Sample.pdf") are US FINRA WSPs and serve **only as document-structure test cases**. DORA never uses the term "WSP" or "written supervisory procedures". The EU-law question is therefore: *which DORA obligations require written/documented policies and procedures that a firm's internal supervisory-procedures manual could legitimately contain or evidence?* — **REQUIRES LEGAL / COMPLIANCE INTERPRETATION** as a framing, applied below per article.

---

## 1. Is a WSP manual itself directly subject to DORA?

**VERIFIED FACT — No.** DORA regulates **financial entities** (Art. 2) and their ICT risk management, incident handling, testing and third-party arrangements. It contains no obligation attaching to any document called a "supervisory procedures manual", and no article requires a single consolidated compliance manual. What DORA repeatedly requires is that specific **policies, procedures, protocols, plans and processes be documented** (e.g. Art. 6(2) "well-documented ICT risk management framework"; Art. 9(4) "documented policies"; Art. 11(1)-(2) "documented arrangements, plans, procedures"; Art. 28(2) written "strategy on ICT third-party risk").

**Consequence for the platform (ARCHITECTURAL RECOMMENDATION):** DORA findings against an uploaded WSP must be phrased as *"the WSP does not document / does not evidence policy X required by DORA Art. Y"*, never *"the WSP violates DORA"*. Absence of a topic from the WSP is **not proof of non-compliance** — the firm may hold the required policy in a separate document (see §4). Severity of "missing from WSP" findings must therefore reflect *evidence gap*, not *established regulatory breach*.

## 2. Entity scope — does DORA apply to the platform's target firms?

- **VERIFIED FACT:** Crypto-asset service providers (CASPs) **as authorised under MiCA**, and **issuers of asset-referenced tokens (ARTs)**, are DORA financial entities under **Art. 2(1)(f)** (verified against full text). E-money token issuers are typically in scope anyway as credit institutions (Art. 2(1)(a)) or electronic money institutions (Art. 2(1)(d)).
  Source: EUR-Lex, Regulation (EU) 2022/2554, https://eur-lex.europa.eu/eli/reg/2022/2554/oj (accessed 2026-08-17; EUR-Lex blocks automated retrieval, article text cross-checked via full-text mirror https://www.digital-operational-resilience-act.com/Article_2.html, accessed 2026-08-17).
- **VERIFIED FACT (important nuance):** Per **ESMA Q&A 2364** (published 2024-12-08), VASPs operating under the **MiCA transitional (grandfathering) regime** are *not* "authorised under" MiCA and are **not subject to DORA** until they obtain CASP authorisation. Source: https://www.esma.europa.eu/publications-data/questions-answers/2364 (accessed 2026-08-17). By Aug 2026 most Member-State transition windows have closed (max 1 July 2026 under MiCA Art. 143(3)), so essentially all operating EU CASPs should now be authorised and DORA-scoped — **REQUIRES LEGAL REVIEW per firm** (platform should capture authorisation status as firm metadata).
- **VERIFIED FACT — Proportionality, Art. 4:** Chapter II (ICT risk management) is implemented "in accordance with the principle of proportionality", taking account of size, overall risk profile, and the nature, scale and complexity of services.
- **VERIFIED FACT — Microenterprise, Art. 3(60):** a financial entity (other than certain market infrastructures) employing **fewer than 10 persons** with annual turnover/balance sheet total **≤ EUR 2 million**. Microenterprises get carve-outs in, i.a., Art. 5(3), 6(4)-(5), 11 (crisis management function, some testing, loss reporting), 13, 16 context, and simplified register/reporting expectations. Many small CASPs will qualify — **the platform must model microenterprise status as a firm attribute that suppresses or downgrades specific controls.**
- **VERIFIED FACT — Art. 16 simplified framework does NOT cover CASPs:** the simplified ICT risk framework of Art. 16 is limited to small non-interconnected investment firms, exempted payment/e-money institutions, exempted CRD institutions and small IORPs. CASPs and ART issuers must apply the **full** Chapter II framework (subject to Art. 4 proportionality).
- **NOT APPLICABLE:** The two sample WSPs belong to US FINRA broker-dealers; DORA does not apply to them at all. They are structure test cases only.

## 3. DORA obligations a WSP-style manual could legitimately evidence

Documented-policy obligations verified against full text (mirror pages Article_5/6/9/11/14/17/28, accessed 2026-08-17; official source EUR-Lex CELEX:32022R2554):

| Article | Documented item required by DORA | Can a supervisory-procedures manual evidence it? |
|---|---|---|
| Art. 5(2) | Governance: management body defines/approves/oversees ICT risk arrangements; data-security policies; roles for ICT functions; BC policy approval; audit plans; budget; training | Yes — governance/roles/escalation chapters |
| Art. 6(1)-(2), (5) | "Sound, comprehensive and well-documented ICT risk management framework" (strategies, policies, procedures, protocols, tools); annual review | Partially — WSP can state the framework's policies or reference the framework document |
| Art. 6(8) | Digital operational resilience strategy (risk tolerance, KPIs, architecture, testing approach) | Usually a separate strategy document — WSP references it |
| Art. 9(2)-(4) + RTS (EU) 2024/1774 | Information security policy; access control; strong authentication/cryptography; **documented ICT change management policies**; **documented patch and update policies** | Yes — classic procedures-manual content |
| Art. 11(1)-(3), (7) | ICT business continuity policy; documented response & recovery plans; crisis management function; records during disruption; BIA | Policy yes; the plans/BIA themselves are usually separate artifacts |
| Art. 13(6) | ICT security awareness programmes and digital operational resilience training as compulsory staff modules | Yes — training/supervision sections |
| Art. 14 | Crisis communication plans; internal/external communication policies; designated spokesperson | Yes |
| Art. 17 | ICT-related incident management process: early-warning indicators, procedures to identify/track/log/categorise/classify incidents, roles, escalation, response procedures | Yes — core procedures content |
| Art. 18 + Delegated Reg. (EU) 2024/1772 | Classification of incidents per harmonised materiality criteria/thresholds | Yes — the classification procedure (not individual classifications) |
| Art. 19 + Del. Reg. (EU) 2025/301 + Impl. Reg. (EU) 2025/302 | Major-incident reporting to competent authority: initial notification (4h from classification / 24h from awareness), intermediate report (72h), final report (1 month), standard templates | Yes — the reporting procedure and deadlines |
| Art. 24-25 | Digital operational resilience testing **programme** (risk-based; yearly testing of critical ICT systems) | The programme/policy yes; execution evidence no |
| Art. 26-27 + Del. Reg. (EU) 2025/1190 (TLPT RTS, applicable 8 July 2025) | TLPT every 3 years for designated entities | Procedure reference only; most CASPs unlikely to be designated — REQUIRES LEGAL INTERPRETATION |
| Art. 28(2) + Del. Reg. (EU) 2024/1773 | Written **strategy on ICT third-party risk** including a **policy on use of ICT services supporting critical or important functions**; regular management-body review (not for microenterprises) | Yes — policy content |
| Art. 28(4)-(8) | Pre-contract assessment/due-diligence procedure; documented **exit strategies** for critical/important functions | Procedures yes; executed assessments/exit plans are separate evidence |

RTS/ITS status sources: European Commission level-2 page and OJ publications — Del. Regs. (EU) 2024/1772, 2024/1773, 2024/1774 (all 13 March 2024, in force with DORA from 17 Jan 2025); Impl. Reg. (EU) 2024/2956 (register of information templates, 29 Nov 2024); Del. Reg. (EU) 2025/301 and Impl. Reg. (EU) 2025/302 (incident reporting, OJ Feb 2025); Del. Reg. (EU) 2025/532 (subcontracting RTS); Del. Reg. (EU) 2025/1190 (TLPT). See https://eur-lex.europa.eu/eli/reg_del/2025/301/oj and https://ec.europa.eu/finance/docs/level-2-measures/ (accessed 2026-08-17).

## 4. Obligations that belong to OTHER artifacts, not the WSP

**NOT APPLICABLE TO WSP** (the platform must not raise "missing from WSP" findings for these as if the WSP were the required home):

1. **Register of information** — Art. 28(3) + Impl. Reg. (EU) 2024/2956: a structured, template-based data register of all ICT contractual arrangements, reported annually to the competent authority. It is a dataset, not manual prose. WSP may at most describe the procedure for maintaining it (that procedure reference is the only defensible WSP control).
2. **ICT contractual arrangements themselves** — Art. 30 key contractual provisions live in the contracts with ICT providers, not in the WSP.
3. **Testing execution evidence** — Art. 24(5)-(6) test results, remediation tracking, TLPT attestations and reports.
4. **Incident reports** — the actual Art. 19 notifications/reports submitted via templates.
5. **Digital operational resilience strategy, BIA, response & recovery plans, exit plans** — normally standalone governed documents; the WSP references them.
6. **Aggregated annual cost/loss reporting** (Art. 11(10)) and **CTPP oversight framework** (Art. 31 et seq. — addresses ICT vendors, not the financial entity's manual).

## 5. Classification summary

- **DIRECT WSP REQUIREMENT** (DORA explicitly demands a documented policy/procedure of a kind a supervisory-procedures manual can legitimately contain): Art. 5(2) governance items, Art. 9(4) policies, Art. 11(1) BC policy, Art. 13(6) training, Art. 14 communication, Art. 17-19 incident procedures, Art. 24 testing programme description, Art. 28(2)/(4)/(8) third-party policy and procedures. *"Direct" here means the documentation obligation is explicit — not that DORA names the WSP.*
- **INDIRECT REGULATORY RELATIONSHIP**: Art. 6(2)/(8) framework & strategy, Art. 11(3) plans, Art. 28(3) register-maintenance procedure — WSP should reference/summarise, primary evidence lives elsewhere.
- **NOT APPLICABLE TO WSP**: §4 items (register data, contracts, test reports, submitted incident reports, CTPP oversight).
- **REQUIRES LEGAL INTERPRETATION**: whether a given firm is DORA-scoped (authorisation status, ESMA Q&A 2364), microenterprise status and resulting carve-outs, TLPT designation, and whether a firm's chosen document architecture (single manual vs. document suite) satisfies "documented" — DORA is document-architecture-neutral.

## 6. Candidate DORA-WSP control list (defensible only)

```json
{
  "regulation": "Regulation (EU) 2022/2554 (DORA)",
  "regulation_source": "https://eur-lex.europa.eu/eli/reg/2022/2554/oj",
  "accessed": "2026-08-17",
  "scope_precondition": "Firm is a DORA financial entity (e.g. MiCA-authorised CASP or ART issuer, DORA Art. 2(1)(f)). Controls marked microenterprise_sensitive must be suppressed/downgraded for Art. 3(60) microenterprises. All controls are evidence-gap checks against the uploaded WSP, not breach determinations.",
  "controls": [
    {
      "id": "DORA-WSP-001",
      "article": "Art. 5(2)-(3)",
      "requirement": "Governance: management body defines, approves and oversees the ICT risk management arrangements; clear roles and responsibilities for ICT-related functions; reporting/escalation channels to the management body.",
      "expected_wsp_evidence": "Governance chapter naming responsible roles (management body, senior management, ICT risk oversight), approval and escalation procedures.",
      "classification": "DIRECT WSP REQUIREMENT",
      "severity_if_missing": "HIGH",
      "microenterprise_sensitive": true
    },
    {
      "id": "DORA-WSP-002",
      "article": "Art. 6(1)-(2), 6(5)",
      "requirement": "Well-documented ICT risk management framework (strategies, policies, procedures, protocols, tools) reviewed at least yearly and after major incidents.",
      "expected_wsp_evidence": "WSP documents or explicitly references the ICT risk management framework and its annual review procedure.",
      "classification": "INDIRECT REGULATORY RELATIONSHIP",
      "severity_if_missing": "MEDIUM",
      "microenterprise_sensitive": true,
      "note": "Framework itself is typically a standalone document; absence from WSP is an evidence gap only."
    },
    {
      "id": "DORA-WSP-003",
      "article": "Art. 9(4)(a)-(c); RTS Del. Reg. (EU) 2024/1774",
      "requirement": "Documented information security policy; network/infrastructure management; access control policies limiting physical and logical access; strong authentication and cryptographic-key protection.",
      "expected_wsp_evidence": "Information security / access management sections with named policies and responsible supervisors.",
      "classification": "DIRECT WSP REQUIREMENT",
      "severity_if_missing": "HIGH"
    },
    {
      "id": "DORA-WSP-004",
      "article": "Art. 9(4)(e)",
      "requirement": "Documented ICT change management policies, procedures and controls (software, hardware, firmware, security parameters).",
      "expected_wsp_evidence": "Change management procedure with approval and rollback steps.",
      "classification": "DIRECT WSP REQUIREMENT",
      "severity_if_missing": "MEDIUM"
    },
    {
      "id": "DORA-WSP-005",
      "article": "Art. 9(4)(f)",
      "requirement": "Appropriate and comprehensive documented policies for patches and updates.",
      "expected_wsp_evidence": "Patch/update policy or procedure section.",
      "classification": "DIRECT WSP REQUIREMENT",
      "severity_if_missing": "MEDIUM"
    },
    {
      "id": "DORA-WSP-006",
      "article": "Art. 11(1)-(4)",
      "requirement": "ICT business continuity policy with documented arrangements; associated ICT response and recovery plans; annual testing of plans.",
      "expected_wsp_evidence": "BC policy section; reference to response/recovery plans and their testing schedule.",
      "classification": "DIRECT WSP REQUIREMENT (policy) / INDIRECT (plans, BIA)",
      "severity_if_missing": "HIGH",
      "microenterprise_sensitive": true
    },
    {
      "id": "DORA-WSP-007",
      "article": "Art. 13(6)",
      "requirement": "ICT security awareness programmes and digital operational resilience training as compulsory modules for staff and management.",
      "expected_wsp_evidence": "Training section covering ICT security awareness with frequency and audience.",
      "classification": "DIRECT WSP REQUIREMENT",
      "severity_if_missing": "MEDIUM"
    },
    {
      "id": "DORA-WSP-008",
      "article": "Art. 14",
      "requirement": "Crisis communication plans for major ICT incidents (clients, counterparts, public); internal/external communication policies; at least one designated spokesperson.",
      "expected_wsp_evidence": "Incident communication procedure naming the spokesperson role.",
      "classification": "DIRECT WSP REQUIREMENT",
      "severity_if_missing": "MEDIUM"
    },
    {
      "id": "DORA-WSP-009",
      "article": "Art. 17",
      "requirement": "ICT-related incident management process: early warning indicators; procedures to identify, track, log, categorise and classify incidents; assigned roles; escalation and response procedures; root-cause follow-up.",
      "expected_wsp_evidence": "Incident management procedure section covering detection through post-incident review.",
      "classification": "DIRECT WSP REQUIREMENT",
      "severity_if_missing": "HIGH"
    },
    {
      "id": "DORA-WSP-010",
      "article": "Art. 18; Del. Reg. (EU) 2024/1772",
      "requirement": "Incident classification procedure applying the harmonised criteria and materiality thresholds (clients affected, duration, geographical spread, data losses, criticality, economic impact).",
      "expected_wsp_evidence": "Classification procedure referencing DORA/RTS criteria and thresholds.",
      "classification": "DIRECT WSP REQUIREMENT",
      "severity_if_missing": "HIGH"
    },
    {
      "id": "DORA-WSP-011",
      "article": "Art. 19; Del. Reg. (EU) 2025/301; Impl. Reg. (EU) 2025/302",
      "requirement": "Major-incident reporting procedure to the competent authority: initial notification within 4 hours of classification (and classification within 24 hours of awareness), intermediate report within 72 hours, final report within 1 month, using mandated templates; voluntary significant cyber-threat notification.",
      "expected_wsp_evidence": "Regulatory reporting procedure with these deadlines and responsible role.",
      "classification": "DIRECT WSP REQUIREMENT",
      "severity_if_missing": "CRITICAL"
    },
    {
      "id": "DORA-WSP-012",
      "article": "Art. 24-25",
      "requirement": "Risk-based digital operational resilience testing programme; appropriate tests (vulnerability assessments/scans etc.) on ICT systems supporting critical or important functions at least yearly.",
      "expected_wsp_evidence": "Testing programme description with scope, frequency and remediation follow-up procedure.",
      "classification": "DIRECT WSP REQUIREMENT (programme) / NOT APPLICABLE (test execution reports)",
      "severity_if_missing": "MEDIUM",
      "microenterprise_sensitive": true
    },
    {
      "id": "DORA-WSP-013",
      "article": "Art. 28(2); Del. Reg. (EU) 2024/1773",
      "requirement": "Written strategy on ICT third-party risk, including a policy on the use of ICT services supporting critical or important functions, regularly reviewed by the management body.",
      "expected_wsp_evidence": "Third-party / outsourcing policy section addressing ICT services and critical-function providers.",
      "classification": "DIRECT WSP REQUIREMENT",
      "severity_if_missing": "HIGH",
      "microenterprise_sensitive": true
    },
    {
      "id": "DORA-WSP-014",
      "article": "Art. 28(3); Impl. Reg. (EU) 2024/2956",
      "requirement": "Procedure for maintaining and annually reporting the register of information on all ICT third-party contractual arrangements.",
      "expected_wsp_evidence": "Procedure describing who maintains the register and the annual reporting duty. The register itself is a separate structured artifact and is NOT expected inside the WSP.",
      "classification": "INDIRECT REGULATORY RELATIONSHIP",
      "severity_if_missing": "MEDIUM"
    },
    {
      "id": "DORA-WSP-015",
      "article": "Art. 28(4)-(8)",
      "requirement": "Pre-contract assessment/due-diligence procedure for ICT providers (criticality, concentration risk, conflicts of interest) and documented exit strategies for critical or important functions.",
      "expected_wsp_evidence": "Vendor onboarding/due-diligence and exit-planning procedures.",
      "classification": "DIRECT WSP REQUIREMENT (procedures) / NOT APPLICABLE (executed assessments, contracts per Art. 30)",
      "severity_if_missing": "MEDIUM"
    }
  ],
  "explicitly_excluded": [
    {"article": "Art. 26-27 TLPT (Del. Reg. (EU) 2025/1190)", "reason": "Applies only to entities designated by authorities; most CASPs unlikely designated — REQUIRES LEGAL INTERPRETATION; no default WSP control."},
    {"article": "Art. 30 contractual provisions", "reason": "Lives in ICT contracts, not the WSP."},
    {"article": "Art. 31+ CTPP oversight", "reason": "Addresses ICT vendors and ESAs, not the financial entity's manual."},
    {"article": "Art. 11(10) cost/loss reporting, Art. 19 submitted reports, test result reports", "reason": "Execution/reporting artifacts, not manual content."}
  ]
}
```

## 7. Sources (accessed 2026-08-17)

- Regulation (EU) 2022/2554 (DORA), EUR-Lex: https://eur-lex.europa.eu/eli/reg/2022/2554/oj — *EUR-Lex returned HTTP 202 anti-bot responses to automated retrieval during this research; article text was cross-verified against the full-text mirror https://www.digital-operational-resilience-act.com/ (Articles 2, 5, 6, 9, 11, 14, 17, 28). EUR-Lex remains the sole authoritative source; mirror used for verification only.*
- ESMA Q&A 2364 (DORA applicability to transitional-regime VASPs): https://www.esma.europa.eu/publications-data/questions-answers/2364
- Del. Reg. (EU) 2025/301 (major-incident reporting RTS): https://eur-lex.europa.eu/eli/reg_del/2025/301/oj
- European Commission level-2 measures (RTS texts incl. 2024/1532, 2024/1772-1774): https://ec.europa.eu/finance/docs/level-2-measures/
- TLPT RTS Del. Reg. (EU) 2025/1190 coverage: https://natlawreview.com/article/dora-delegated-regulation-threat-led-penetration-testing-published-official-journal (secondary; OJ publication 18 June 2025, applicable 8 July 2025)
- Impl. Reg. (EU) 2024/2956 (register of information ITS), Del. Reg. (EU) 2025/532 (subcontracting RTS), Impl. Reg. (EU) 2025/302 (incident reporting ITS): identified via A&O Shearman / Norton Rose regulatory trackers (secondary confirmation of OJ numbers).

**Honesty notes:** (1) No artificial controls invented — every control above maps to an explicit DORA documentation obligation. (2) "DIRECT WSP REQUIREMENT" asserts only that DORA requires the documented policy/procedure, not that DORA names a WSP; DORA is neutral on whether policies live in one manual or many documents (**REQUIRES LEGAL INTERPRETATION** when scoring firms that split documentation). (3) Secondary sources (law-firm trackers, mirror site) used only to confirm OJ instrument numbers and text; all normative claims trace to EUR-Lex/ESMA instruments.
