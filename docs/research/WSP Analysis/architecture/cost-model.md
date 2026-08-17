# Cost Model — 1k / 10k / 100k Firms

**Scope:** Storage, extraction, embeddings, and LLM evaluation costs for the WSP validation platform; biggest drivers and optimizations.
**Date:** 2026-08-17. All prices are public list prices verified via web on 2026-08-17 and cited below. Labels: VERIFIED FACT (price) / ASSUMPTION (workload parameter).

---

## 1. Verified unit prices (2026-08-17)

| Item | Price | Source |
|---|---|---|
| Claude Haiku 4.5 (fast tier) | $1.00 / $5.00 per 1M input/output tokens | [Anthropic pricing roundup (TLDL, Aug 2026)](https://www.tldl.io/resources/anthropic-api-pricing); [silicondata 2026 table](https://www.silicondata.com/use-cases/anthropic-claude-api-pricing-2026) |
| Claude Sonnet 5 (quality tier) | $3.00 / $15.00 per 1M (intro $2/$10 through 2026-08-31) | [aipricing.guru Anthropic 2026](https://www.aipricing.guru/anthropic-pricing/); [BenchLM Aug 2026](https://benchlm.ai/anthropic/api-pricing) |
| Batch API discount | −50% on all token usage, ≤24h turnaround | [finout.io Anthropic pricing guide 2026](https://www.finout.io/blog/anthropic-api-pricing) |
| Prompt caching | cache reads ≈ 0.1× input price; writes 1.25× (5-min TTL) | [finout.io](https://www.finout.io/blog/anthropic-api-pricing) ("caching cuts cached input cost by 90%") |
| OpenAI `text-embedding-3-small` (1536-dim) | $0.02 per 1M tokens; $0.01 batch | [embeddingcost.com/openai](https://embeddingcost.com/openai); [costgoat Aug 2026](https://costgoat.com/pricing/openai-embeddings) |
| S3-class object storage (EU) | ≈ $0.023/GB-month | ASSUMPTION (standard AWS S3 EU list price; verify per region/tier at contract time) |

VERIFIED FACT: the token prices and discounts above; ASSUMPTION: everything in §2.

## 2. Workload assumptions (grounded in the two sample WSPs)

- WSP size: 150–200 pages (`Sample WSP.pdf` = 154pp; `WSP Sample.pdf` = 199pp) ⇒ ~120k–200k tokens of text; use **180k tokens/doc**.
- Chunking: ~600-token chunks ⇒ **~300–400 chunks/version**; embeddings ≈ 200k tokens/version (incl. overlap).
- Controls: MiCA+DORA control library with **~40 semantic controls** (brief range 20–50) + ~40 deterministic (free). Applicability filter drops ~25% per firm ⇒ **~30 LLM-evaluated controls per full validation**.
- Per semantic-control call: prompt = shared prefix ~2.5k tokens (system + control def + regulation excerpt — identical across firms, cacheable) + firm evidence ~3k tokens (5 chunks) ⇒ **5.5k input**, **0.75k output**.
- Cadence per firm/year: **3 new WSP versions** (full-ish validation, but ~60% of controls hash-reuse across versions ⇒ ~12 fresh LLM calls/version… conservatively model 30 calls on v1 and 40% residue after) + **6 regulatory-change revalidations** touching avg 4 controls each.
- Extraction: PDF → text/layout/sections. Options: open-source (Docling/unstructured — compute-only, ~$0.01–0.05/doc) or managed OCR (~$1.50/1,000 pages ⇒ ~$0.30/200pp doc). Model **$0.30/version** (conservative, managed).

## 3. Per-firm annual cost (quality tier = Sonnet 5 at full list $3/$15, batched, cache-warm)

Per fresh semantic call, batched: input 5.5k of which 2.5k cached-read ⇒ (3.0k × $3 + 2.5k × $0.30 + 0.75k × $15) × 0.5 / 1M ≈ **$0.011/call** (Sonnet) or ≈ **$0.0036/call** (Haiku 4.5 at $1/$5).

| Component | Calls or units / firm / yr | Sonnet cost | Haiku cost |
|---|---|---|---|
| Initial + 2 re-versions (30 + 2×12 fresh calls) | 54 calls | $0.59 | $0.19 |
| Regulatory-change revalidations (6 × 4 controls, ~70% residue after reuse) | ~17 calls | $0.19 | $0.06 |
| Embeddings (3 versions × 200k tok, batch $0.01/M) | 0.6M tok | $0.006 | $0.006 |
| Extraction (3 versions × $0.30) | 3 docs | $0.90 | $0.90 |
| **LLM + pipeline total / firm / yr** | | **≈ $1.7** | **≈ $1.2** |

Recommended production mix — Haiku screening pass on all calls, Sonnet escalation on the ~25% that are ambiguous/failing: ≈ **$0.45/firm/yr LLM** + $0.9 extraction ⇒ **≈ $1.4/firm/yr**. Un-batched, un-cached, all-Sonnet worst case: ~$8–10/firm/yr — i.e. the optimizations are worth ~6–7×.

## 4. Scale table (annual, platform-wide)

| | 1k firms | 10k firms | 100k firms |
|---|---|---|---|
| LLM evaluation (mixed tier, batched, cached) | ≈ $500 | ≈ $5k | ≈ $50k |
| LLM worst case (Sonnet, no batch/cache) | ≈ $9k | ≈ $90k | ≈ $900k |
| Embeddings | ≈ $6 | ≈ $60 | ≈ $600 |
| Extraction (managed OCR) | ≈ $900 | ≈ $9k | ≈ $90k |
| Object storage (PDFs+artifacts ~60MB/firm incl. history) | 60GB ≈ $17/mo | 600GB ≈ $170/mo | 6TB ≈ $1.7k/mo |
| Postgres rows: evaluations (~80 append-only rows/firm/yr) | 80k/yr | 800k/yr | 8M/yr — trivial; partition by month |
| pgvector rows (~1.2k chunks/firm live) | 1.2M | 12M | 120M — hash-partition by firm; per-version filtered queries stay tiny |
| Infra (Postgres HA, workers, Temporal, EU region) | ~$1–2k/mo | ~$3–6k/mo | ~$15–30k/mo |

**Reading:** model-API spend is *not* the dominant cost until ~100k firms, and even there it is O($50k–100k)/yr when engineered as above; **infrastructure + extraction dominate at small scale, and the un-optimized LLM path is the only component that could blow up (≈$1M/yr at 100k firms)**.

## 5. Biggest drivers & optimizations (ranked)

1. **Semantic-control call count** — driver #1. Mitigations already in the design: deterministic-first controls, applicability filtering, hash-level reuse across versions and across regulatory-change runs (`incremental-revalidation.md`), and alert-driven scoping (only impacted controls re-run on a change).
2. **Prompt structure for provider caching** — the shared prefix (system + control definition + regulation excerpt) is identical across every firm; ordering it first makes ~45% of input tokens cost 0.1×. Grouping batch jobs by control keeps the cache hot.
3. **Batch API** — every revalidation is latency-tolerant (hours-scale SLA is fine); 50% off nearly all evaluation spend. Reserve synchronous calls for interactive "validate now" UX only.
4. **Model tiering** — Haiku-class screen + Sonnet-class escalate ≈ 60–70% cheaper than all-Sonnet at comparable end quality; keep the tier per-control configurable (`control_versions.model_id`) so accuracy-critical controls pin to the quality tier.
5. **Extraction choice** — at 100k firms, managed OCR (~$90k/yr) rivals total LLM spend; self-hosted open-source extraction (Docling-class) on EU compute cuts this to compute cost (~$3–5k/yr) at the price of pipeline ownership. Decide at ~10k firms.
6. **Embedding dedupe** — WSP manuals share heavy boilerplate (both samples are template-derived FINRA-style manuals); a global `embedding_cache` keyed by text hash dedupes across versions *and* firms. Embeddings are already negligible; dedupe mainly saves vector storage.
7. **Storage lifecycle** — old WSP version PDFs → infrequent-access tier after 90 days; evaluations kept hot 24 months then archived partitions to object storage (retain for audit — REQUIRES LEGAL REVIEW for exact retention under customers' regulatory obligations).

## 6. Sensitivity notes

- Doubling controls (40→80 semantic) or evidence contexts (5→10 chunks) roughly doubles LLM spend — still <$120k/yr at 100k firms in the optimized path.
- If customers demand EU-sovereign models, unit prices may be 1.5–3× the above (ASSUMPTION; re-verify against the chosen EU provider) — the optimization stack (batch, cache, tiering, reuse) transfers as long as the provider supports batching and caching; if not, expect ~2× additional.
- Intro pricing (Sonnet 5 $2/$10 through 2026-08-31) is ignored above; using it lowers the Sonnet figures ~33% short-term.

**Sources** (all accessed 2026-08-17): [finout.io Anthropic pricing 2026](https://www.finout.io/blog/anthropic-api-pricing) · [TLDL Anthropic API pricing (Jul 2026)](https://www.tldl.io/resources/anthropic-api-pricing) · [silicondata Claude pricing 2026](https://www.silicondata.com/use-cases/anthropic-claude-api-pricing-2026) · [aipricing.guru](https://www.aipricing.guru/anthropic-pricing/) · [BenchLM (Aug 2026)](https://benchlm.ai/anthropic/api-pricing) · [embeddingcost.com/openai](https://embeddingcost.com/openai) · [costgoat OpenAI embeddings (Aug 2026)](https://costgoat.com/pricing/openai-embeddings) · [cloudzero OpenAI pricing 2026](https://www.cloudzero.com/blog/openai-pricing/). Note: these are reputable price aggregators, not the vendors' own pages; confirm against vendor pricing pages before contracting.
