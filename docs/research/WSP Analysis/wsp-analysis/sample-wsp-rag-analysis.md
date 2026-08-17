# Sample WSP RAG Analysis — Chunking & Retrieval Requirements from Real Structures (Brief Section 40)

**Date:** 2026-08-17 · **Status:** Research/architecture only (ARCHITECTURAL RECOMMENDATION throughout unless labeled otherwise).
**WSP1** = `Sample WSP.pdf` (WealthForge, 154 pp, untagged, flat chapters + bold sub-headings) · **WSP2** = `WSP Sample.pdf` (Triad, 199 pp, tagged, deep `2.4.7` numbering).
This file derives *sample-grounded* chunking/retrieval requirements; the general RAG design lives in `../ai/rag-architecture.md`, extraction tooling in `sample-wsp-extraction-analysis.md`, structure evidence in `notes-sample-wsp-1.md` / `notes-sample-wsp-2.md`.

---

## 1. Corpus shape facts that drive the design (VERIFIED from samples)

| Property | WSP1 | WSP2 | RAG consequence |
|---|---|---|---|
| Size | ~56k words / 154 pp | ~72k words / 199 pp | ~300–400 chunks/doc at 300–500 tokens — retrieval is always **within one wsp_version**, so scale per query is trivial |
| Section tree source | TOC page numbers + font-span heading detection (untagged) | 797 numbered headings + tag tree (TOC has no page numbers) | Chunker consumes the unified section tree from the parser (`sample-wsp-structure.md` §4), never raw pages |
| Section length spread | Chapters pp.8–90; some TOC leaves are one paragraph, Appendix A is 32 pp | §13 is 1 p; §20 is 42 pp; §18 is 21 pp | Chunking must split long sections *and* merge sub-paragraph leaves — fixed-size chunking loses section identity, pure per-section chunking overflows context |
| Obligation locus | Prose + bullets (~85–90%); almost no tables | Same | Claim-bearing text is prose → sentence-integrity at chunk boundaries matters more than table serialization |
| Key tables | Appendix D roster p.142; Appendix E form p.143 | p.14 supervisor table; Appendices C–F logs/forms | Serialize tables as header-preserving rows AND retain raw cell grid; roster tables must be retrievable *whole* (splitting a roster destroys role-conflict detection) |
| Footnotes | ~69, interleaved mid-paragraph across page breaks | none significant | Footnote bodies must be extracted to sidecar records pre-chunking or they corrupt chunk text (WSP1 p.26 verified case) |
| Numbering collision | — | §18 pasted template with own "1.–20." numbering | Chunk metadata needs `numbering_scope` so "Section 12" retrieval does not match §18's internal item 12 |
| Cross-references | "full program in Appendix A" (p.44) | "See Section 2.11", "See Appendix C" | Retrieval must optionally expand 1 hop along the resolved cross-ref graph |
| Mojibake | `∑` 16× | `―`/`‖` ~495×, `‘` 359×, U–4/U-4 | Normalize BEFORE embedding and BM25 indexing; store raw text separately for verbatim span verification |
| Page parity | printed = physical | printed = physical | Chunk metadata carries `page_start/page_end` (+ bbox) → system fills citation fields; treat parity as measured `page_offset`, not assumption |

## 2. Chunking requirements

1. **Section-tree chunking, not sliding windows.** Unit = deepest section node; split nodes >~500 tokens at paragraph boundaries into `part 1/n` children; merge <~80-token leaf runs with their parent heading. Every chunk carries: `chunk_id, wsp_version_id, section_id, section_path (e.g. "18 > Customer Identification Program"), heading_text, numbering_scope, page_start, page_end, char_offsets, text_sha256, component_id`.
2. **Appendices are components with independent metadata.** WSP1's AML program (App. A) and BCP (App. B) have their own revision dates and signatures — chunks inherit `component_revision_date` so retrieval-time freshness reasoning ("annual approval claim vs latest evidence") is possible without re-reading the document.
3. **Heading-context injection (contextual retrieval).** Prepend a generated 50–100-token context line (doc identity + section path + one-line gist) before embedding/BM25 — WSP2's "In General" headings and WSP1's bare "Introduction:" headings are meaningless without ancestry. (Anthropic contextual-retrieval numbers: ~49% retrieval-failure reduction, ~67% with reranking — https://www.anthropic.com/engineering/contextual-retrieval, accessed 2026-08-17.)
4. **Sidecar records, not inline noise:** footnote bodies (WSP1) keyed to their anchor chunk; DocuSign artifact strings (WSP1 p.122); footers already stripped. Footnote URLs feed the link-rot detector, not the embedding text.
5. **Two-layer text:** `text_normalized` (mojibake-repaired, dash-folded, de-glued) for indexing/LLM; `text_raw` + offsets for the deterministic span-existence check in the anti-hallucination gate (a quoted span must match the *stored* chunk verbatim — normalization must be reproducible/invertible via offset maps).

## 3. Retrieval requirements (control-driven, not chat-driven)

The dominant query is **control → candidate evidence chunks** (per `../ai/rag-architecture.md`): for each applicable control (e.g. DORA-WSP-006 BC policy), retrieve top 10–20 chunks from one wsp_version and ask the LLM for a PASS/PARTIAL/FAIL/N-A decision with chunk_id citations.

1. **Hybrid dense+sparse is mandatory, RRF-fused, reranked.** Sample-grounded reason: control language is EU-flavored ("ICT business continuity policy", "wind-down plan") while evidence language is US-flavored ("Business Continuity Plan", "SBD", "FinOp") — dense vectors bridge vocabulary (BCP case), but exact identifiers (Rule 17a-4, "314(a)", "$10,000", "G-37") need BM25 after dash/date normalization. Neither alone survives both samples.
2. **Query expansion from the control's terminology map.** The comparison doc (§4, `sample-wsp-comparison.md`) shows the same concept appears as "Email Review"/"Electronic Communications"/"Correspondence" — controls should carry synonym lists (canonical concept vocabulary) appended to the retrieval query, maintained as part of the control library.
3. **Structured filters before similarity:** `wsp_version_id` always; optional `component_id` (search only Appendix A for AML controls), `section_path` prefix, `numbering_scope`. This turns the §18 collision and appendix sub-documents into filter dimensions instead of noise.
4. **Whole-table retrieval mode:** roster-type chunks (WSP1 App. D p.142, WSP2 p.14) are flagged `is_roster=true` and always co-retrieved for role/governance controls — role-conflict findings need the full roster plus the prose designations.
5. **Cross-reference expansion (1 hop):** if a retrieved chunk contains a resolved internal reference ("full program in Appendix A"), optionally pull the target's head chunk. WSP1 §5 (pp.44–45) is a 2-page summary whose substance lives 47 pages later — without expansion, an AML adequacy judgment over §5 alone would be wrong.
6. **Negative-evidence protocol (absence proof).** MISSING verdicts (7+ rows in `sample-wsp-control-mapping.md`) cannot cite a supporting chunk. Requirements: (a) retrieval returns top-k *with scores* even when weak; (b) the LLM may assert absence only after seeing the best available candidates + the document's section inventory (TOC-derived outline chunk); (c) the finding cites the searched scope ("no section matched control terms X/Y/Z; nearest candidate: §8 p.57, rejected because…"). The section-inventory chunk (one per wsp_version) is a required synthetic chunk type.
7. **Reranking matters for near-miss discrimination:** WSP1 has privacy-framed security text (pp.41–43) that superficially matches DORA infosec controls — the reranker + judge must distinguish "Reg S-P customer-data privacy" from "ICT risk policy". Good hard-negative pairs for the golden set.

## 4. Incremental & versioning hooks

- Chunk identity = `(section_id, text_sha256)`: a re-uploaded WSP1 v2 with only the roster fixed re-embeds only changed sections (per `../architecture/incremental-revalidation.md`).
- Embedding cache keyed `(model, text_sha256)` — WSP2-class documents that never change never re-embed.
- Regulatory-change revalidation retrieves via the `control → section` dependency map recorded at evaluation time, so an Art. 19 RTS change re-touches only chunks previously retrieved for DORA-WSP-011.

## 5. Security note

Both samples scanned clean for instruction-like text (VERIFIED, notes files §5.11/§8), but every chunk enters LLM prompts as **untrusted data**: data-only framing, no tool use in the evaluation loop, render-vs-extraction hidden-text diff at ingestion (per `../security/llm-security-governance.md`).

## 6. Open questions

- Chunk-size sweep (300 vs 500 tokens) against a golden retrieval set built from the 15 mapping rows — measure recall@20 per control. **OPEN QUESTION** (empirical).
- Whether to embed footnote sidecars at all (WSP1 footnotes are mostly citations — likely BM25-only). **OPEN QUESTION**.
- Multi-document EU policy suites (one "WSP" = many files) change the corpus-per-query assumption — retrieval scope becomes a document *set*. **ASSUMPTION** pending real EU uploads; see `sample-wsp-structure.md` §5.
