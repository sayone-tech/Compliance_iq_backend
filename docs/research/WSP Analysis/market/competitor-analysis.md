# Market / Competitor Analysis — Continuous Regulatory Compliance Validation Platform (Brief Section 35)

**Date of research / all URL access dates: 2026-08-17.**
**Scope:** vendors in MiCA compliance tooling, crypto compliance, DORA compliance platforms, regulatory change monitoring / regulatory intelligence, policy-as-code, AI policy-vs-regulation gap analysis, and US broker-dealer WSP (Written Supervisory Procedures) review tools.

**Method & labeling.** All claims below are derived from vendor websites, press releases, and trade press located via web search on 2026-08-17. Vendor marketing pages are **not regulatory authority**; capability claims are labeled:

- **VERIFIED FACT** — confirmed on the vendor's own site or multiple independent trade-press sources.
- **UNVERIFIED** — could not be confirmed from available sources; treat as unknown, not absent.
- **ASSUMPTION** — reasonable inference, flagged as such.

**Terminology note (important).** In this product, "WSP" = *Written Supervisory Procedures* — a US FINRA broker-dealer's internal supervision/compliance manual (per FINRA Rules 3110/3120/3130), exemplified by the two sample PDFs in this repo ("Sample WSP.pdf", "WSP Sample.pdf" — Triad Securities Corp.). The product transplants this document type into an EU context, validating WSP-style internal procedure manuals against MiCA (Regulation (EU) 2023/1114) and DORA (Regulation (EU) 2022/2554). **No vendor found in this research markets "WSP validation against MiCA/DORA" as a product.** The closest analogues are (a) US WSP consulting/management tools and (b) AI policy-vs-regulation gap-mapping tools. That intersection is empty today — which is the core market claim of this brief. **REQUIRES LEGAL/COMPLIANCE INTERPRETATION:** whether an EU CASP's MiCA Art. 68 governance documents are legally comparable to a FINRA WSP is an interpretive question, not settled by any vendor material.

---

## 1. Competitive Landscape Map

| Segment | Representative vendors | Overlap with this product |
|---|---|---|
| Regulatory intelligence / change monitoring | CUBE, Corlytics (incl. Clausematch), Regology, AscentAI, Vixio, Archer (Compliance.ai) | High — the "regulation feed" half |
| AI policy-vs-regulation gap analysis | 4CRisk.ai, Norm Ai, Corlytics/Clausematch, CUBE RegPlatform | Highest — the "document validation" half |
| DORA compliance platforms | OneTrust, ServiceNow IRM, MetricStream, Archer, Bitsight, Interfacing, SecureSlate, DORApp, Copla | Medium — DORA pillar coverage, but workflow/register-centric, not document-validation-centric |
| MiCA / crypto compliance | Chainalysis, Elliptic, TRM Labs, Scorechain, Sumsub, Notabene, ComplyAdvantage, Fenergo | Low-medium — mostly AML/on-chain/KYC, not policy documents |
| US broker-dealer WSP tools | COMPLY (ComplySci + RIA in a Box), Oyster Solutions, Red Oak, ACA Group, Saifr, Luthor, StarCompliance | Medium — same document type, different (US) rulebook, mostly consulting/workflow not automated validation |
| Policy-as-code / machine-executable regulation | REGnosys (Rosetta/Rune, ISDA DRR), OPA/Styra (generic) | Low direct overlap; relevant as an architectural pattern |

---

## 2. Vendor Profiles

### 2.1 Regulatory intelligence / regulatory change monitoring

#### CUBE (cube.global)
- **Product(s):** RegPlatform (enterprise), RegPlatform Intel (mid-market); RegBrain AI engine.
- **Website:** https://cube.global/ (accessed 2026-08-17); enterprise: https://cube.global/solutions/cube-regplatform-enterprise; Intel: https://cube.global/solutions/cube-intel
- **Use case:** VERIFIED FACT — automated regulatory intelligence: tracks, classifies, and monitors laws/rules globally in every published language; AI-driven classification and regulatory change management; maps regulatory obligations to a firm's "regulatory footprint."
- **MiCA support:** VERIFIED FACT that MiCA/DORA are within monitored content universe (CUBE Intel marketing names DORA among covered regimes; MiCA within global coverage). UNVERIFIED — any MiCA-specific control library.
- **DORA support:** VERIFIED FACT — DORA named in CUBE Intel coverage.
- **WSP/policy-validation:** PARTIAL — RegPlatform maps obligations to internal policies/controls; UNVERIFIED that it performs automated gap/contradiction analysis of an uploaded procedures manual with clause-level evidence.
- **Regulatory monitoring:** VERIFIED FACT (core product).
- **Automated revalidation on regulatory change:** PARTIAL/UNVERIFIED — change alerts flow to impacted obligations; no evidence of automated re-validation of a specific uploaded document.
- **AI/RAG:** VERIFIED FACT — RegBrain semantic AI; generative assistant features announced. RAG architecture specifics UNVERIFIED.
- **Evidence traceability:** UNVERIFIED at clause/page level.
- **API:** UNVERIFIED (enterprise integrations advertised).
- **Public pricing:** none published (enterprise sales).
- **Strengths:** largest regulatory content universe; big-bank customer base; acquired Thomson Reuters Regulatory Intelligence business (2023–24 trade press). **Weaknesses:** horizon-scanning-first, not document-validation-first; enterprise price point; no WSP concept.

#### Corlytics (corlytics.com) — incl. Clausematch
- **Product(s):** Corlytics regulatory risk intelligence; Clausematch policy management (acquired July 2023); SparQ regulatory monitoring (acquired Jan 2023).
- **Website:** https://www.corlytics.com/ ; https://www.corlytics.com/solutions/clausematch-policy-management/ (accessed 2026-08-17). Acquisition: https://www.finextra.com/newsarticle/42592/corlytics-acquires-clausematch (accessed 2026-08-17).
- **Use case:** VERIFIED FACT — end-to-end chain: regulatory monitoring → change management → policy management → attestation. Obligations mapped directly to policies "with full traceability, ensuring every policy statement can be evidenced back to its regulatory source" (vendor claim, trade press corroborated). Named "Policy Management Solution of the Year" in the 2026 FinTech Breakthrough Awards (https://www.corlytics.com/press-releases/corlytics-named-policy-management-solution-of-the-year-in-2026-fintech-breakthroughawards-program/, accessed 2026-08-17).
- **MiCA/DORA support:** UNVERIFIED as dedicated modules; both regimes fall inside its monitored EU content. Corlytics publishes enforcement-risk analytics by regulator.
- **WSP/policy-validation:** CLOSEST COMPETITOR CAPABILITY — Clausematch is a policy authoring/management platform with obligation-to-policy-statement mapping. However, its model assumes policies are authored/maintained *inside* the platform; UNVERIFIED support for validating an externally authored, uploaded 150–200 pp WSP PDF. No WSP-specific product.
- **Monitoring:** VERIFIED FACT. **Automated revalidation:** PARTIAL — change alerts propagate to mapped policy paragraphs (vendor claim); depth UNVERIFIED.
- **AI/RAG:** VERIFIED FACT — AI classification/tagging; "AI-powered one-stop-shop" positioning.
- **Evidence traceability:** VERIFIED FACT at policy-statement-to-obligation level (vendor claim).
- **API:** Clausematch historically offered APIs/integrations — UNVERIFIED current state. **Public pricing:** none.
- **Strengths:** the most complete regulatory-source-to-policy-paragraph traceability story on the market; 14 of top-50 banks (2023 figure). **Weaknesses:** author-in-platform model vs validate-uploaded-document; no MiCA/DORA-native control library marketed; no severity-scored gap findings on external documents.

#### Regology (regology.com)
- **Product(s):** Regology platform; Reggi generative-AI assistant; Regulatory Change / Compliance / Research agents.
- **Website:** https://www.regology.com/ ; https://regology.com/reggi ; https://www.regology.com/platform (accessed 2026-08-17).
- **Use case:** VERIFIED FACT — industry-agnostic regulatory intelligence over a proprietary database of 16M+ laws/regulations; law library, change tracking, requirement extraction; conversational AI with cited references.
- **MiCA/DORA support:** ASSUMPTION — EU regulations are in the library; no MiCA/DORA-specific product found (UNVERIFIED).
- **WSP/policy-validation:** UNVERIFIED — no evidence of uploaded-document gap analysis as a product.
- **Monitoring:** VERIFIED FACT. **Automated revalidation:** UNVERIFIED.
- **AI/RAG:** VERIFIED FACT — LLM answers grounded in its regulatory database with citations (vendor claim, i.e., a RAG pattern).
- **Evidence traceability:** citations to regulatory sources — VERIFIED (vendor claim); to customer documents — UNVERIFIED.
- **API:** UNVERIFIED. **Public pricing:** none.
- **Strengths:** breadth, agentic roadmap, citation discipline. **Weaknesses:** generalist; not finance/EU-native; no document-validation loop.

#### AscentAI / Ascent RegTech (ascentregtech.com)
- **Product(s):** Ascent Horizon (horizon scanning), AscentFocus (obligations inventory + change management).
- **Website:** https://www.ascentregtech.com/ (accessed 2026-08-17); https://www.ascentregtech.com/our-difference/change-management/
- **Use case:** VERIFIED FACT — ML extraction of granular obligations from regulatory text into a firm-tailored obligations register; monitors regulator sources and flags applicable changes automatically. Partnership/integration with Resolver (https://www.resolver.com/ascent/, accessed 2026-08-17).
- **MiCA/DORA support:** UNVERIFIED — historically US/UK/AU financial regulators focus.
- **WSP/policy-validation:** UNVERIFIED — obligations map to policies/controls via GRC integrations, not document validation.
- **Monitoring:** VERIFIED FACT. **Automated revalidation:** obligations register auto-updates on change (VERIFIED vendor claim); document-level revalidation — no.
- **AI/RAG:** VERIFIED FACT (ML obligation extraction; "AscentAI" branding 2025).
- **Evidence traceability / API / pricing:** UNVERIFIED / UNVERIFIED / none public.
- **Strengths:** granular obligation extraction — the same decomposition step this product's Requirement layer needs. **Weaknesses:** no EU crypto focus; no document analysis.

#### Vixio (vixio.com)
- **Product:** Vixio Regulatory Intelligence (Payments Compliance, Digital Assets modules).
- **Website:** https://www.vixio.com/ ; https://www.vixio.com/digital-assets (accessed 2026-08-17).
- **Use case:** VERIFIED FACT — analyst-validated horizon scanning across 200+ jurisdictions; licence and framework mapping explicitly including **MiCA** (EMI, PI, MTL, MiCA, MiFID); 500+ organisations.
- **MiCA support:** VERIFIED FACT (MiCA named in framework mapping). **DORA:** VERIFIED FACT — Vixio publishes DORA change-tracking content (https://www.vixio.com/blog/tools-to-track-digital-operational-resilience-act-dora-regulatory-changes-affecting-banks-and-fintechs, accessed 2026-08-17).
- **WSP/policy-validation:** NO — content/intelligence product, not document analysis.
- **Monitoring:** VERIFIED FACT. **Automated revalidation / evidence traceability / API:** UNVERIFIED. **Pricing:** none public.
- **Strengths:** deep EU payments/crypto regulatory analyst coverage. **Weaknesses:** human-readable intelligence only; no computable controls, no validation.

#### Archer + Compliance.ai (archerirm.com)
- **Product:** Archer GRC with Compliance.ai regulatory change management (acquired 2024-02-20).
- **Website/press:** https://www.archerirm.com/press-releases/archer-acquires-compliance.ai-to-drive-ai-powered-regulatory-compliance-and-risk-management ; https://www.businesswire.com/news/home/20240220502745/en/ (accessed 2026-08-17).
- **Use case:** VERIFIED FACT — continuous regulatory monitoring; patented Expert-In-The-Loop (EITL) ML; "automatically maps regulatory changes to internal policies, procedures, and controls."
- **MiCA/DORA:** UNVERIFIED as specific modules (Archer sells DORA via GRC configuration — see §2.3).
- **WSP/policy-validation:** PARTIAL — mapping of changes to policy objects inside the GRC; not clause-level validation of uploaded manuals (UNVERIFIED).
- **AI/RAG:** VERIFIED FACT (EITL ML). **Evidence traceability/API/pricing:** UNVERIFIED / GRC APIs exist / none public.
- **Strengths:** installed enterprise GRC base. **Weaknesses:** GRC-object-centric; heavy implementation; US-leaning content.

### 2.2 AI policy-vs-regulation gap analysis (closest functional competitors)

#### 4CRisk.ai — likely the "4CR" in the brief
- **Note:** the brief's shorthand "4CR" could not be verified as a standalone company; searches surface **4CRisk.ai**, which matches the described category. ASSUMPTION: "4CR" = 4CRisk.ai.
- **Product(s):** Compliance Map; Regulatory Change; Regulatory Research; Ask ARIA Co-Pilot.
- **Website:** https://4crisk.ai/ ; https://www.4crisk.ai/compliance-maps ; https://www.4crisk.ai/regulatory-change-management (accessed 2026-08-17).
- **Use case:** VERIFIED FACT — **semantic AI matching of external regulations/standards against internal policies, procedures, and controls, surfacing gaps needing remediation**; generates suggested language for controls/policies to close gaps; tracks remediation; integrates with GRC systems. Vendor claims 40–50x speedup vs manual mapping.
- **MiCA support:** UNVERIFIED. **DORA support:** UNVERIFIED (vendor targets financial services, retail, hi-tech generally; US-leaning marketing).
- **WSP/policy-validation:** FUNCTIONALLY YES for generic policy documents (VERIFIED vendor claim of policy-vs-regulation gap analysis); **no WSP-specific or FINRA-specific product identified (UNVERIFIED)**.
- **Monitoring:** VERIFIED FACT (Regulatory Change product). **Automated revalidation of previously mapped documents on regulation change:** UNVERIFIED — the two products exist separately; a closed loop is not demonstrated in public material.
- **AI/RAG:** VERIFIED FACT — private-by-design language models trained on regulatory corpus (vendor claim); free trial offered (https://www.4crisk.ai/free-trial).
- **Evidence traceability:** PARTIAL — mapping assessments show matched/unmatched provisions; page/clause-level citation depth UNVERIFIED.
- **API:** GRC integration claimed; open API UNVERIFIED. **Public pricing:** none (free trial exists).
- **Strengths:** closest single-product analogue to this platform's core validation engine; remediation-language generation. **Weaknesses:** not MiCA/DORA-native; no curated EU control library; continuous re-validation loop unproven; evidence granularity unclear.

#### Norm Ai (norm.ai)
- **Product:** "Agentic law" platform — regulations and policies encoded as decision trees traversed by LLM agents; Regulated Content Review; Compliance Agent for Microsoft 365 Copilot (launched May 2026).
- **Website:** https://www.norm.ai/ ; https://www.norm.ai/platform/ ; https://www.prnewswire.com/news-releases/norm-ai-launches-compliance-agent-for-microsoft-365-copilot-302769123.html (accessed 2026-08-17).
- **Use case:** VERIFIED FACT — converts regulations into machine-executable decision-tree logic authored by legal engineers; agents review content/documents against encoded frameworks *and internal policies*; every recommendation carries rationale + citation; 100+ regulations across US/UK/EU/Canada/APAC; raised $120M Series C (2026, per Enterprise DNA/trade press — figure UNVERIFIED against primary source).
- **MiCA/DORA support:** UNVERIFIED — EU coverage claimed generally; MiCA/DORA not named in found material.
- **WSP/policy-validation:** PARTIAL — reviews content against internal policies; validating the policy manual *itself* against regulation is UNVERIFIED.
- **Monitoring/revalidation:** UNVERIFIED. **AI/RAG:** VERIFIED FACT (hybrid symbolic decision trees + LLM — notably *not* pure RAG). **Evidence traceability:** VERIFIED FACT (citation + rationale per finding — vendor claim). **API:** enterprise integrations; UNVERIFIED. **Pricing:** none public.
- **Strengths:** strongest evidence-per-finding story; regulator/attorney-authored logic = defensibility. **Weaknesses:** per-regulation encoding is expensive/slow to extend; MiCA/DORA absence; content-review-centric.

### 2.3 DORA compliance platforms

DORA (Reg. (EU) 2022/2554) applies since 2025-01-17 (VERIFIED FACT — EUR-Lex: https://eur-lex.europa.eu/eli/reg/2022/2554/oj, accessed 2026-08-17). The vendor market clusters around two pillars: the EBA-template **Register of Information** for ICT third-party contracts, and **incident classification/reporting** — *not* validation of internal procedure documents.

| Vendor | Product / DORA angle | Key verified point | Source (accessed 2026-08-17) |
|---|---|---|---|
| OneTrust | Third-Party Management with automated DORA Register of Information report creation | VERIFIED FACT — "first-to-market" automated RoI reporting claim | https://www.prnewswire.com/news-releases/onetrust-automates-dora-ict-risk-management-and-compliance-302257101.html |
| ServiceNow IRM, Archer, MetricStream | Enterprise GRC; DORA via module packs / configuration; multi-entity register consolidation, concentration-risk analytics; six-figure cost | VERIFIED (trade/analyst commentary) | https://www.legiscope.com/blog/best-dora-compliance-software.html |
| Bitsight | TPRM + DORA-lens vendor assessment questionnaires | VERIFIED FACT | https://www.bitsight.com/blog/how-to-prepare-your-2026-DORA-compliance-strategy |
| Interfacing | AI-powered IMS linking processes, risks, controls, vendors, continuity plans for DORA | VERIFIED (vendor claim) | https://interfacing.com/digital-operational-resilience-act-dora-compliance |
| SecureSlate | Maps DORA ICT requirements alongside ISO 27001/SOC 2/NIS 2 with automated evidence | VERIFIED (vendor claim) | https://getsecureslate.com/blog/dora-compliance-software-for-eu-fintech-2026 |
| DORApp, Copla, Crises Control | Niche DORA workflow/incident/TPRM tools | VERIFIED (vendor claims) | https://blog.dorapp.eu/digital-operational-resilience/dora-digital-operational-resilience-act ; https://copla.com/blog/compliance-regulations/dora-directive-regulations-compliance-and-framework/ |

**Common gaps across DORA vendors:** none found performs AI gap analysis of a firm's *written procedures* against DORA article text with cited findings; none offers continuous document revalidation on RTS/ITS updates; WSP support: none (all UNVERIFIED-to-NO).

### 2.4 MiCA / crypto compliance

MiCA (Reg. (EU) 2023/1114) fully applicable since 2024-12-30; CASP transitional ("grandfathering") periods end by 2026-07-01 at the latest, per Art. 143(3) and national elections (VERIFIED FACT — EUR-Lex: https://eur-lex.europa.eu/eli/reg/2023/1114/oj ; ESMA MiCA hub: https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica, accessed 2026-08-17; the 2026-07-01 outer deadline also reported at https://hacken.io/discover/mica-regulation/, accessed 2026-08-17).

- **Chainalysis / Elliptic / TRM Labs / Scorechain / Sumsub / Notabene / ComplyAdvantage:** VERIFIED FACT — the dominant "MiCA compliance" tooling is AML/CFT, Travel Rule (TFR (EU) 2023/1113), sanctions screening, and on-chain analytics for CASP authorisation evidence; typical CeFi stack pricing reported at $100K–$500K+/yr (trade press: https://sphinxhq.com/blog-posts/top-crypto-compliance-software-2026 ; https://www.scorechain.com/resources/crypto-glossary/chainalysis-vs-elliptic ; https://financefeeds.com/7-best-compliance-tools-for-crypto-businesses-after-mica/, accessed 2026-08-17). **None validates governance/procedure documents. WSP support: NO.**
- **Fenergo (fenergo.com):** VERIFIED FACT — CLM/KYC across 120+ jurisdictions, onboarding, KYRA AI agents (https://www.fenergo.com/client-lifecycle-management, accessed 2026-08-17). MiCA-specific CASP module: UNVERIFIED. Policy/document validation: NO.
- **MiCA Crypto Alliance Tool Hub:** VERIFIED FACT — trackers of CASP authorisations and white paper submissions built on ESMA registers; white-paper drafting services (https://www.micacryptoalliance.com/tool-hub, accessed 2026-08-17). This is registry tracking, not procedure validation.
- **ESMA white-paper iXBRL PoC:** VERIFIED FACT — ESMA published a proof of concept for machine-readable (Inline XBRL) crypto-asset white papers incl. draft taxonomy (https://www.esma.europa.eu/document/mica-white-papers-poc, accessed 2026-08-17). Relevant as evidence the *regulator itself* is moving toward machine-readable MiCA artifacts — an architectural tailwind, not a competitor.

### 2.5 US broker-dealer WSP tools (the document type's home market)

- **COMPLY / ComplySci + RIA in a Box (comply.com):** VERIFIED FACT — compliance program management for 2,600+ RIAs/BDs; publishes WSP educational content (https://www.comply.com/compliance-glossary/written-supervisory-procedures-wsps/, accessed 2026-08-17; merger: https://www.prnewswire.com/news-releases/complysci-and-ria-in-a-box-join-forces-to-launch-the-future-of-compliance-software-301440718.html). **Automated AI WSP-vs-rulebook validation: UNVERIFIED** — offering is workflow, registration, trade monitoring, consulting.
- **Oyster Consulting / Oyster Solutions (oysterllc.com):** VERIFIED FACT — GRC platform whose Govern module "houses policies, procedures and risk assessments, mapping these to regulatory requirements"; Oyster *writes* WSPs as a consulting service (https://www.oysterllc.com/what-we-do/oyster-solutions/ ; https://www.oysterllc.com/what-we-do/compliance/program-review/code-of-ethics-policies-procedures-manual/, accessed 2026-08-17). Mapping is human-configured; **AI gap analysis UNVERIFIED**.
- **Red Oak (redoak.com):** VERIFIED FACT — advertising/communications review platform (est. 2010, Texas); its AI review lets firms encode prompts *derived from* their WSPs to review marketing pieces (https://www.redoak.com/ ; https://www.redoak.com/resources/articles/finra-warns-about-genai-risks/, accessed 2026-08-17). It consumes WSPs as configuration; **it does not validate WSPs**.
- **ACA Group (acaglobal.com):** VERIFIED FACT — consulting: WSP drafting/review, FINRA 3110/3120 reports, supervisory control testing (https://www.acaglobal.com/who-we-serve/broker-dealers, accessed 2026-08-17). Human service, not software validation.
- **Saifr (saifr.ai, Fidelity-backed), Luthor (luthor.ai), StarCompliance:** VERIFIED FACT — AI review of *marketing/communications* against FINRA 2210 / SEC Marketing Rule (https://www.luthor.ai/guides/2025-ai-compliance-software-buyer-guide-rias-saifr-starcompliance-luthor, accessed 2026-08-17). Adjacent AI-review pattern; **not WSP validation, not EU**.
- **EQube Compliance (equbecompliance.com):** WSP drafting/templates service (https://www.equbecompliance.com/written-supervisory-procedures, accessed 2026-08-17) — consulting.
- **Market conclusion:** in the WSP's home market, WSP work is dominated by **consultants + templates + GRC workflow**, with FINRA's own 2026 oversight report scrutinizing GenAI supervision (https://www.swlaw.com/publication/finras-2026-oversight-report-signals-a-supervisory-reckoning-for-autonomous-ai/, accessed 2026-08-17). **No automated WSP-vs-regulation validation product was verifiable in either the US or EU market.**

### 2.6 Policy-as-code / machine-executable regulation

- **REGnosys (regnosys.com):** VERIFIED FACT — Rosetta platform + Rune DSL (contributed to FINOS); powers ISDA's Digital Regulatory Reporting (DRR): trade-reporting rules expressed as open, human-readable *and* machine-executable code on the Common Domain Model; production use at BNP Paribas, JP Morgan, Standard Chartered, DTCC et al. (https://regnosys.com/ ; https://regnosys.com/solutions/regulatory-reporting/ ; https://a-teaminsight.com/briefs/regnosys-contributes-rosetta-language-to-finos/, accessed 2026-08-17). Scope: **reporting rules**, not conduct/governance obligations; no document validation; no MiCA/DORA. Relevance: proves the Regulation→Requirement→executable-Control decomposition pattern this product's control library needs.
- **OPA/Styra and generic policy-as-code:** infra authorization policy engines; no regulatory-content overlap (ASSUMPTION: not competitors; possible internal building block).

---

## 3. Capability Matrix (summary)

Legend: ✔ = VERIFIED, ◐ = partial/vendor claim, ? = UNVERIFIED, ✘ = no evidence / not offered.

| Vendor | MiCA | DORA | Policy/WSP validation | Reg. monitoring | Auto revalidation loop | AI/RAG | Evidence traceability | API | Public pricing |
|---|---|---|---|---|---|---|---|---|---|
| CUBE | ◐ | ✔ | ◐ | ✔ | ? | ✔ | ? | ? | ✘ |
| Corlytics/Clausematch | ? | ? | ◐ (in-platform policies) | ✔ | ◐ | ✔ | ◐ | ? | ✘ |
| Regology | ? | ? | ? | ✔ | ? | ✔ | ◐ (reg. citations) | ? | ✘ |
| AscentAI | ? | ? | ✘ | ✔ | ◐ (obligations only) | ✔ | ? | ? | ✘ |
| Vixio | ✔ | ✔ | ✘ | ✔ | ✘ | ◐ | ✘ | ? | ✘ |
| Archer/Compliance.ai | ? | ◐ | ◐ | ✔ | ? | ✔ | ? | ◐ | ✘ |
| 4CRisk.ai | ? | ? | ✔ (generic policies) | ✔ | ? | ✔ | ◐ | ◐ | ✘ (free trial) |
| Norm Ai | ? | ? | ◐ | ? | ? | ✔ (symbolic+LLM) | ✔ | ? | ✘ |
| OneTrust (DORA) | ✘ | ✔ (RoI) | ✘ | ◐ | ✘ | ◐ | ◐ | ✔ | ✘ |
| Chainalysis/Elliptic/TRM/Scorechain | ✔ (AML lens) | ✘ | ✘ | ◐ | ✘ | ◐ | ✔ (on-chain) | ✔ | ✘ ($100–500K/yr reported) |
| Fenergo | ? | ? | ✘ | ◐ | ✘ | ✔ | ? | ✔ | ✘ |
| COMPLY / Oyster / Red Oak / ACA | ✘ | ✘ | ◐ (workflow/consulting) | ◐ (US) | ✘ | ◐ | ? | ? | ✘ (SmartAsset reports RIA in a Box tiers) |
| REGnosys | ✘ | ✘ | ✘ | ✘ | ◐ (rule versioning) | ✘ (DSL) | ✔ (code provenance) | ✔ | ✘ (open-source core) |

No vendor scores ✔ across MiCA + DORA + uploaded-document validation + continuous revalidation + clause-level evidence. That column-combination is this product's whitespace.

---

## 4. Differentiation Opportunities for This Product

1. **The continuous revalidation loop (strongest differentiator).** Every surveyed vendor treats regulatory change monitoring and policy/document assessment as *separate* products or steps. None demonstrably re-runs validation of a specific uploaded WSP automatically and incrementally when a MiCA/DORA delegated act, RTS/ITS, or ESMA/EBA Q&A changes, re-scoring only affected findings. Building change-impact propagation from Regulation → Requirement → Control → affected WSP sections closes a loop nobody ships today. (ARCHITECTURAL RECOMMENDATION: make regulation-version pinning and finding-level diffing first-class.)
2. **Evidence-cited, severity-scored findings on an uploaded document.** Norm Ai proves citation-per-finding sells; 4CRisk proves policy-vs-regulation mapping sells; nobody combines them for a 150–200 pp uploaded procedures manual with page/section-level evidence quotes on both sides (regulation article ↔ WSP clause). The two sample WSPs (154 pp untagged PDF; 199 pp tagged PDF with deep numbered TOC) show the parsing spread the engine must handle.
3. **EU MiCA/DORA-native curated control library.** DORA vendors sell registers and workflows; MiCA vendors sell AML analytics; regulatory intelligence vendors sell feeds. A hand-curated, lawyer-reviewable library of MiCA (EU 2023/1114) + DORA (EU 2022/2554) requirements → controls → expected evidence, with EUR-Lex/ESMA/EBA citations per control, is not offered by anyone surveyed. It is also defensible content, not just software. (REQUIRES LEGAL REVIEW for each control's interpretation.)
4. **Single-document-type focus = quality moat.** Generalists (Regology, CUBE) must handle any document; specializing in one document genre (WSP-style supervisory procedure manuals) permits genre-aware chunking (numbered TOC hierarchies), contradiction detection across sections, and calibrated severity — depth generalists can't match.
5. **Cross-regime contradiction detection.** No vendor markets detection of *internal contradictions* within a policy manual or conflicts between a firm's procedures and two regimes simultaneously (MiCA vs DORA overlap, e.g., ICT incident handling under both DORA Art. 17–23 and MiCA operational-resilience expectations).
6. **Transparency wedge vs enterprise pricing.** Public pricing is absent across all direct competitors; enterprise GRC DORA implementations run six figures. A transparent, mid-market price with a free "upload your WSP, get top-10 gaps" motion is an open go-to-market wedge (mirrors 4CRisk's free-trial motion).
7. **Regulator-machine-readability tailwind.** ESMA's iXBRL white-paper PoC signals machine-readable regulatory artifacts are coming; a platform whose control library is already versioned and machine-consumable is positioned to ingest them first.

**Competitive threats (honest view):** Corlytics/Clausematch (has traceability + monitoring; could add upload-validation), 4CRisk.ai (has the gap engine; could add MiCA/DORA content), and Norm Ai (has capital, $120M Series C reported, and the evidence discipline; could encode MiCA/DORA). Estimated fastest-mover time-to-parity is a content problem (curating MiCA/DORA controls), not a technology problem — hence the control library and the revalidation loop, not the LLM, are the moat. (ASSUMPTION.)

**OPEN QUESTIONS:** (a) whether "4CR" in the source brief meant 4CRisk.ai or an unfound company; (b) actual clause-level citation depth of Clausematch and 4CRisk (requires demos, not websites); (c) whether any EU NCA informally expects WSP-style consolidated supervisory manuals from CASPs — REQUIRES LEGAL/COMPLIANCE INTERPRETATION.

---

*All vendor capability statements are vendor or trade-press claims as of access date 2026-08-17 and are not regulatory authority. Sample WSPs in this repo are test artifacts only and were not used as authority for any claim in this document.*
