# Machine-Readable Regulatory Control Model (Brief Section 10)

**Scope.** How to represent MiCA/DORA validation controls in machine-readable form for the Continuous Regulatory Compliance Validation Platform, which validates firms' WSPs (Written Supervisory Procedures — internal compliance/supervision manuals, a term of US FINRA origin used here in an EU product context; see the terminology note in the WSP analysis docs). Regulatory authority hierarchy: **Official Regulation → Requirement → Control → Expected Evidence → WSP evidence**.

**Date of research:** 2026-08-17. All URLs accessed 2026-08-17.

---

## 1. Candidate standards evaluated

| Standard | What it is | Fit for our control model | Verdict |
|---|---|---|---|
| **Akoma Ntoso (AKN)** | OASIS Standard (approved 2018) XML vocabulary for legislative/judicial documents; hierarchical structure (article/paragraph/point) with stable eIds. [OASIS AKN v1.0](https://www.oasis-open.org/standard/akn-v1-0/), [Part 1 vocabulary](https://docs.oasis-open.org/legaldocml/akn-core/v1.0/akn-core-v1.0-part1-vocabulary.html) | Represents **legal text structure**, not controls. Relevant to *ingestion*: AKN4EU is the EU localization used interinstitutionally, with an official Formex→AKN converter (FMX2AK). [AKN4EU](https://op.europa.eu/en/web/eu-vocabularies/akn4eu), [Discover AKN4EU](https://interoperable-europe.ec.europa.eu/collection/semic-support-centre/solution/common-structured-format-eu-legislative-documents/discover-akn4eu) | Use for **text-structure model in the ingestion layer** (AKN-style eIds for article/paragraph anchors), not for controls. |
| **LegalRuleML** | OASIS standard for machine-readable legal *norms* (obligations, permissions, defeasibility), companion to AKN in the LegalXML family. [OASIS LegalDocML TC](https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=legaldocml) | Theoretically expresses deontic logic of MiCA/DORA obligations. In practice: near-zero tooling ecosystem, no regulator publishes MiCA/DORA in LegalRuleML, high authoring cost, and our validation is LLM/NLP-driven, not logic-programming-driven. | **Reject** as the control format; borrow its *concepts* (obligation type, bearer, conditions) as JSON fields. |
| **XBRL / iXBRL** | Tagging standard for structured **reporting data** (financial figures, DORA registers of information use ESA templates). | Designed for data-point reporting, not narrative-procedure validation. Irrelevant to representing "does the WSP contain an ICT incident-classification procedure?". | **Reject** for controls. Note only that DORA Register of Information reporting to ESAs is template-based — an evidence *topic*, not our format. |
| **OSCAL (NIST)** | JSON/YAML/XML models for security control **catalogs, profiles, implementations, assessments**. [OSCAL catalog model](https://pages.nist.gov/OSCAL/learn/concepts/layer/control/catalog/) | Closest structural analogue: catalog→control→part→assessment-objective mirrors our Regulation→Requirement→Control→Expected-Evidence chain; proven JSON tooling; used for compliance-as-code (e.g. [AWS/Canadian requirements](https://aws.amazon.com/blogs/security/using-oscal-to-express-canadian-cybersecurity-requirements-as-compliance-as-code)). But OSCAL assumes a *system security plan* target, US-flavored metadata, and has no native EU legal-provenance (ELI/CELEX) or effective-date/versioned-law semantics. | **Do not adopt wholesale; copy its architecture** (catalog/profile separation, control parts, back-matter citations). |
| **OPA / Rego (policy-as-code)** | Runtime policy engine evaluating structured input against rules. | Our "evaluation" is semantic comparison of narrative WSP text vs. regulatory requirements (LLM + retrieval), not boolean checks over structured input. OPA fits the *platform's own* authz, not compliance semantics. | **Reject** for the control model. |
| **Knowledge graphs / ontologies — ELI, FIBO** | **ELI** (European Legislation Identifier): EU-official URI + RDF metadata scheme for legislation, integrated into EUR-Lex; FRBR-based (work/expression/manifestation), supports point-in-time consolidated versions (e.g. `https://eur-lex.europa.eu/eli/reg/2023/1114/2024-01-09/eng`). [ELI at EUR-Lex](https://eur-lex.europa.eu/EN/legal-content/summary/european-legislation-identifier-eli.html), [ELI ontology](https://interoperable-europe.ec.europa.eu/collection/eli-european-legislation-identifier/solution/eli-ontology), [EU Vocabularies ELI](https://op.europa.eu/en/web/eu-vocabularies/eli). **FIBO**: EDM Council financial-industry ontology. | ELI is exactly the provenance identifier we need — official, versioned, machine-resolvable. FIBO models financial *instruments/entities*, not obligations; marginal value. | **Adopt ELI + CELEX identifiers** for every provenance link. FIBO: not adopted (ASSUMPTION: no payoff for WSP validation; revisit if entity-type reasoning grows). |

**VERIFIED FACT — what EUR-Lex actually serves (relevant constraint):** EUR-Lex/CELLAR serves metadata via a public **SPARQL endpoint** (Common Data Model, RDF/OWL) and content manifestations as **XHTML, PDF and Formex XML** via CELLAR RESTful services; a SOAP webservice exists for registered users. AKN4EU is the *interinstitutional drafting/exchange* format — it is **not** today the guaranteed retrieval format for arbitrary acts on EUR-Lex, so ingestion must be Formex/XHTML-first and AKN-*aware* (map to AKN-style structural IDs internally). Sources: [Cellar data](https://op.europa.eu/en/web/cellar/cellar-data), [EUR-Lex webservice](https://eur-lex.europa.eu/content/help/data-reuse/webservice.html), [Data extraction using web services (PDF)](https://eur-lex.europa.eu/content/tools/webservices/DataExtractionUsingWebServices.pdf), [AKN4EU](https://op.europa.eu/en/web/eu-vocabularies/akn4eu).

---

## 2. Recommendation — ARCHITECTURAL RECOMMENDATION

**Hybrid: custom JSON control model + ELI/CELEX provenance identifiers + Akoma-Ntoso-aware ingestion layer.**

Reasoning:
1. No existing standard covers the whole chain (versioned EU law ↔ compliance controls ↔ narrative-evidence expectations ↔ LLM validation instructions). OSCAL comes closest structurally but lacks EU legal provenance; LegalRuleML has provenance concepts but no ecosystem.
2. Custom JSON keeps the model aligned with how validation actually runs (retrieval + LLM prompts + evidence specs), is versionable in git, and is trivially queryable/indexable.
3. ELI/CELEX URIs give official, point-in-time-resolvable anchors so every finding traces to an exact expression of the law (e.g. CELEX `02023R1114-20240109` = MiCA consolidated as of 2024-01-09 — VERIFIED FACT: [consolidated MiCA](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02023R1114-20240109)).
4. AKN-style structural addressing (`art_68__para_2__point_a`) inside the ingestion layer gives article/paragraph-granular anchors that survive re-consolidation, and stays compatible if EUR-Lex later serves AKN4EU natively.

## 3. Control object — proposed JSON shape (illustrative)

```json
{
  "control_id": "MICA-ART68-ICT-01",
  "schema_version": "1.0",
  "title": "CASP ICT resilience procedures per MiCA Art. 68(7) / DORA",
  "hierarchy": {
    "regulation": {
      "celex_base": "32023R1114",
      "celex_consolidated": "02023R1114-20240109",
      "eli_work": "http://data.europa.eu/eli/reg/2023/1114/oj",
      "eli_expression": "https://eur-lex.europa.eu/eli/reg/2023/1114/2024-01-09/eng"
    },
    "requirement": {
      "anchor": {"article": "68", "paragraph": "7"},
      "akn_eid": "art_68__para_7",
      "text_sha256": "<hash of normalized provision text>",
      "obligation_type": "obligation",
      "addressee": ["CASP"]
    },
    "related_provisions": [
      {"celex_base": "32022R2554", "anchor": {"article": "9"}},
      {"level": "L2-RTS", "celex_base": "<RTS CELEX>", "status": "in_force"}
    ]
  },
  "applicability": {"entity_types": ["CASP"], "conditions": ["provides custody"]},
  "expected_evidence": [
    {"evidence_id": "EE-1",
     "description": "WSP section assigning responsibility for ICT risk management framework",
     "wsp_signals": ["designated principal", "ICT risk", "review frequency"],
     "sufficiency": "REQUIRES LEGAL REVIEW"}
  ],
  "validation": {
    "method": "llm_semantic",
    "retrieval_queries": ["ICT risk management responsibility"],
    "severity_if_absent": "high",
    "contradiction_checks": []
  },
  "lifecycle": {
    "status": "active",
    "version": 3,
    "effective_from": "2024-12-30",
    "effective_to": null,
    "supersedes": "MICA-ART68-ICT-01@v2",
    "change_reason": "consolidated-text diff 02023R1114-YYYYMMDD",
    "approved_by": "human-review-gate",
    "approved_at": "2026-..-.."
  },
  "guidance_refs": [
    {"source": "ESMA_QA", "id": "<QA id>", "url": "https://www.esma.europa.eu/publications-and-data/questions-answers", "authority_level": "L3-nonbinding"}
  ]
}
```

Key design rules:
- **Every control cites at least one CELEX + ELI anchor at article/paragraph granularity**; the `control→article index` built from these anchors drives change-impact analysis (see regulatory-ingestion.md §5).
- **Provision text hash** pinned per control enables cheap "did my provision change?" checks after each new consolidated expression.
- **Level-2/Level-3 material** (delegated acts, RTS/ITS, ESMA/EBA guidelines, Q&As) attaches as `related_provisions` / `guidance_refs` with an explicit `authority_level`, because Q&As are non-binding interpretive aids — findings based only on L3 must be labeled accordingly (REQUIRES LEGAL / COMPLIANCE INTERPRETATION).
- **Controls are immutable per version**; regulation change or human edit creates a new version through the human review gate.
- **OPEN QUESTION:** whether expected-evidence sufficiency thresholds (what counts as an adequate WSP procedure) can ever be fully encoded — current position: encode signals, let LLM assess, force human review on low-confidence; sufficiency criteria themselves REQUIRE LEGAL REVIEW.

## 4. What we deliberately did NOT adopt

- Full OSCAL serialization (would require lossy shoehorning of ELI versioning into OSCAL back-matter; revisit if customers demand OSCAL export — an **export mapping** JSON→OSCAL catalog is feasible later).
- LegalRuleML deontic encoding (no ecosystem; ASSUMPTION: cost > benefit for an LLM-centric validator).
- XBRL, OPA/Rego, FIBO — see table.
