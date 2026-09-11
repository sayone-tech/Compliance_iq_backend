# WSP Validation POC

Proof of concept for AI-assisted validation of a firm's Written Supervisory
Procedures (WSP) against **MiCA** (Reg. (EU) 2023/1114) and **DORA**
(Reg. (EU) 2022/2554), producing a per-article **covered / partial / gap**
report with citations back into the manual.

Implements the plan in the *WSP Validation POC — Implementation Plan* artifact.

**PRD anchors:** FR-30 (upload), FR-31 (AI suggests, human confirms), FR-34
(gap analysis per Requirement ID), FR-112 (expected vs. found framing),
Section 6.2 (85% verified accuracy at UAT), EV-01 / EV-08, SA-13 (MiCA
service-line tagging asymmetry).

The output is always a **suggestion set for human review**. It never
auto-determines compliance.

---

## What is here

| File | Role |
|---|---|
| `extract_wsp.py` | PDF → normalised text with `[[page:N]]` markers; optionally appends the synthetic fixture |
| `synthetic_sections.txt` | Fixture sections drafted to satisfy DORA Art. 11, DORA Art. 17, MiCA Art. 70 — the golden set's true positives |
| `validate_wsp.py` | The pipeline: scoping → chunking → embeddings → retrieval → LLM judgment → CSV/HTML/JSON report |
| `vector_store.py` | Everything Qdrant-specific: the chunk index, the embedding memo cache, point ids, the doc-scoped ranking |
| `tools/backfill_embedding_cache.py` | One-off: loads the retired `embeddings.json.gz` into the Qdrant cache collection |
| `tools/smoke_vector_store.py` | Asserts the Qdrant contract on a fresh server: lossless cache round trip, doc filtering, orphan sweep, count guard |
| `tools/compare_parity.py` | Diffs two `results.json` files on retrieved sets, ordering, scores and the auto-gap decision |
| `golden_set.json` | Labels for the two sample manuals — **label before running** |
| `score_golden.py` | Scores retrieval and judgment **separately** against the golden set |
| `requirements.txt` | Python deps; PDF extraction uses the poppler `pdftotext` binary |
| `.env.example` | Template for the API key — copy to `.env` (gitignored) |
| `../../Dockerfile`, `../../docker-compose.yml`, `../../.dockerignore` | Repository root: the `wsp-poc` app image (carries poppler) and the `qdrant` service |

`validate_wsp.py` reuses `../fetch_regulation.py` for the CELLAR fetch and
Formex parse — it does not reimplement either.

---

## Correction to the plan

The plan recorded both sample files as plain text with a misleading `.pdf`
extension. **They are real, text-native PDFs** — `Sample WSP.pdf` is 154pp
untagged PDFium, `WSP Sample.pdf` is 199pp tagged Word 2007 (measured in
`docs/research/WSP Analysis/wsp-analysis/sample-wsp-extraction-analysis.md`).
Neither needs OCR, so `extract_wsp.py` exists as a separate stage: poppler
`pdftotext -layout` plus the mandatory mojibake/footer/footnote normalisation
pass. Everything downstream of that stage matches the plan.

---

## Setup

### Docker (recommended)

A new machine needs only Docker — no host poppler, no host Python:

```bash
docker compose up -d qdrant             # the vector store, on 127.0.0.1:6333
docker compose build wsp-poc            # the app image, carries pdftotext
docker compose run --rm wsp-poc python3 scripts/wsp_poc/validate_wsp.py --help
```

The repository is bind-mounted at `/app`, so every path in this README works
verbatim inside the container and reports land in `out/` on the host, owned by
you. `docker compose up -d` on its own starts **only** Qdrant: `wsp-poc` sits
behind the `cli` profile because it is a one-shot command runner, not a daemon.

### Native

```bash
sudo apt install poppler-utils          # provides pdftotext
pip install -r scripts/wsp_poc/requirements.txt
docker compose up -d qdrant             # still needed: the index lives in Qdrant
```

Native runs and container runs share the same Qdrant, so the two can be mixed
freely. Without any Docker at all, `--qdrant-url none --retriever numpy` runs the
whole pipeline in-process — nothing persists, so every unit is re-embedded at
about $0.003 per run.

## API key

`validate_wsp.py` reads the key from the **environment variable
`OPENAI_API_KEY`**. It is never a command-line argument — that would put the key
into shell history and into the process list. Two ways to supply it:

**1. Export it in the shell** (nothing is written to disk):

```bash
export OPENAI_API_KEY=sk-...
```

**2. Put it in a `.env` file** (loaded automatically at startup):

```bash
cp scripts/wsp_poc/.env.example scripts/wsp_poc/.env
$EDITOR scripts/wsp_poc/.env          # OPENAI_API_KEY=sk-...
```

`scripts/wsp_poc/.env` is checked first, then a `.env` at the repository root.
An already-exported variable always wins over the file. **`.env` is gitignored —
never commit a real key.**

Related flags:

| Flag | Use |
|---|---|
| `--api-key-env VAR` | read the key from a different variable (default `OPENAI_API_KEY`) |
| `--base-url URL` | point at Azure OpenAI, a gateway, or a local mock |
| `--dry-run` | chunk, scope and estimate cost **with no key at all**, and with no Qdrant connection |
| `--qdrant-url URL` | Qdrant server (env `QDRANT_URL`, default `http://127.0.0.1:6333`) |
| `--collection-prefix P` | prefix for both collection names (env `QDRANT_COLLECTION_PREFIX`, default `wsp`) |
| `--offline` | never fetch regulations from CELLAR. It does **not** mean "no Qdrant" — Qdrant is local infrastructure, in the same category as the filesystem the old cache lived on |

Under compose the key reaches the container by either of two paths, both
verified: an **exported** `OPENAI_API_KEY` is passed through, and when the shell
has none the app's own loader finds `scripts/wsp_poc/.env` through the bind
mount. **The key is never baked into the image or into `docker-compose.yml`.**

> The compose `environment:` block lists `- OPENAI_API_KEY` (bare name) rather
> than `OPENAI_API_KEY: "${OPENAI_API_KEY:-}"`. The mapping-with-default form
> sets the variable to the **empty string** when the host shell has none, and an
> empty-but-present variable shadows the `.env` file — the run then dies with
> "no API key" while a perfectly good key sits in `scripts/wsp_poc/.env`.
> `load_dotenv()` also treats an empty variable as absent, so both layers are
> covered.

At startup the run prints which variable and file the key came from, plus its
last four characters, so a wrong key is obvious before any spend. If no key is
found the run stops before any API call with the paths it looked in.

## Run

Two manuals, two independent runs. Do them in order — run A populates the
regulation and embedding caches that run B reuses.

| Run key | PDF | Firm | Fixture | Role |
|---|---|---|---|---|
| `sample_wsp` | `Sample WSP.pdf` | WealthForge, 154pp | **appended** (`--with-synthetic`) | carries the known true positives |
| `triad_wsp` | `WSP Sample.pdf` | Triad Securities, 199pp | none | the control |

Keep the two in **separate `--out` directories**. The golden set is labelled per
document, and the MiCA Art. 70 pair (covered in `sample_wsp` via the fixture,
gap in `triad_wsp`) only works if the runs stay apart.

All commands run from the repository root. Only step 3 of each run needs the API
key; extraction, dry runs and scoring do not. Step 3 additionally needs Qdrant.

```bash
# 0. once per session, for both runs
docker compose up -d qdrant
```

Every command below is written natively. To run it in the container instead,
prefix it with `docker compose run --rm wsp-poc` and change nothing else:

```bash
docker compose run --rm wsp-poc \
    python3 scripts/wsp_poc/validate_wsp.py --wsp out/wsp/sample_wsp.txt --dry-run
```

### Run A — `sample_wsp` (WealthForge + synthetic fixture)

```bash
# A1. extract, with the DORA 11 / DORA 17 / MiCA 70 fixture appended
python3 scripts/wsp_poc/extract_wsp.py \
    --pdf "docs/research/WSP Analysis/Sample WSP.pdf" \
    --out out/wsp/sample_wsp.txt --with-synthetic
#   -> 155 pages, ~57k words, "+ synthetic fixture" on the last line

# A2. dry run: chunking, article scoping and a cost estimate, no API calls.
#     The first invocation fetches DORA and MiCA from CELLAR into --regs-cache.
python3 scripts/wsp_poc/validate_wsp.py \
    --wsp out/wsp/sample_wsp.txt \
    --regs-cache out/regs/ \
    --out out/report/sample_wsp/ \
    --dry-run
#   -> "scoped 53 articles (27 DORA, 26 MiCA)"
#   -> ~206 chunks, worst case ~$0.033
#   Sanity check: the last chunks listed should sit under "APPENDIX Z".

# A3. validate (needs the API key)
python3 scripts/wsp_poc/validate_wsp.py \
    --wsp out/wsp/sample_wsp.txt \
    --profile exchange,execution,custody \
    --regs-cache out/regs/ \
    --gap-floor 0.25 \
    --budget-usd 1.00 \
    --out out/report/sample_wsp/
#   -> one line per article, then the report files and the total spend

# A4. score against the golden set
python3 scripts/wsp_poc/score_golden.py \
    --results out/report/sample_wsp/results.json \
    --chunks  out/report/sample_wsp/chunks.json \
    --run sample_wsp \
    --json out/report/sample_wsp/score.json
```

What to check in run A:

- DORA Art. 11, DORA Art. 17 and MiCA Art. 70 should come back **covered**,
  each citing a chunk under `APPENDIX Z`. These are the fixture's true
  positives; a miss here is a retrieval or rubric failure, not a document
  finding.
- MiCA Art. 75 / 77 and DORA Art. 26 / 28 should come back **gap**, most of them
  resolved by the auto-gap floor with no LLM call.
- Open `out/report/sample_wsp/gap_report.html` and read the expected-vs-found
  table of one `partial` article — that is the FR-112 output shape.

### Run B — `triad_wsp` (Triad Securities, control, no fixture)

```bash
# B1. extract, no fixture
python3 scripts/wsp_poc/extract_wsp.py \
    --pdf "docs/research/WSP Analysis/WSP Sample.pdf" \
    --out out/wsp/triad_wsp.txt
#   -> 200 pages, ~72k words, no "+ synthetic fixture"

# B2. dry run. --offline because run A already cached both regulations.
python3 scripts/wsp_poc/validate_wsp.py \
    --wsp out/wsp/triad_wsp.txt \
    --regs-cache out/regs/ \
    --out out/report/triad_wsp/ \
    --offline --dry-run
#   -> ~355 chunks, worst case ~$0.033

# B3. validate (needs the API key)
python3 scripts/wsp_poc/validate_wsp.py \
    --wsp out/wsp/triad_wsp.txt \
    --profile exchange,execution,custody \
    --regs-cache out/regs/ \
    --gap-floor 0.25 \
    --budget-usd 1.00 \
    --out out/report/triad_wsp/ \
    --offline

# B4. score
python3 scripts/wsp_poc/score_golden.py \
    --results out/report/triad_wsp/results.json \
    --chunks  out/report/triad_wsp/chunks.json \
    --run triad_wsp \
    --json out/report/triad_wsp/score.json
```

What to check in run B:

- **MiCA Art. 70 must be `gap` here.** Same article, same prompt, same
  thresholds as run A, differing only in the document — that pair is the
  cleanest evidence the pipeline reacts to content rather than to phrasing.
- The insider-trading, communications-with-the-public and BCP chapters should
  drive **partial** verdicts on MiCA Art. 92 / Art. 66 and DORA Art. 11.
- Triad's deep decimal numbering (`2.4.7`) exercises the other heading regime;
  spot-check `chunks.json` for sane `heading_path` values before trusting the
  verdicts.

### Both together

`--wsp` is repeatable, so one run can pool both manuals into a single query. The
mechanism is a **query-time filter, not a separate index**: every run upserts its
chunks into the one `wsp_chunks_*` collection tagged with their `doc`, and search
is filtered to the docs of the current run. A pooled run simply widens that
filter to both, and stores nothing twice.

```bash
python3 scripts/wsp_poc/validate_wsp.py \
    --wsp out/wsp/sample_wsp.txt --wsp out/wsp/triad_wsp.txt \
    --regs-cache out/regs/ --out out/report/both/ --offline
```

That answers "does the firm cover this article **anywhere** in its policy set",
which is the real product question for a multi-document upload. It is **not
scoreable against the golden set** — the labels are per document, and the Art. 70
control collapses as soon as the fixture is in the same index. Use it after
runs A and B, never instead of them.

### Re-running

Regulation JSON is cached on disk per CELEX; embeddings are memoised in Qdrant.
Iterating on the prompt or the rubric is therefore cheap: keep `--regs-cache`
pointing at the same directory, add `--offline`, leave Qdrant up, and only the
judge calls are billed again. A run prints `cache: N hit / M miss` for each
embedding pass — on a repeat run of an unchanged manual `M` should be `0`.

Bump `PROMPT_VERSION` in `validate_wsp.py` when the rubric changes — it is
stamped into every CSV row and every `audit.jsonl` line, and it is how two runs
are told apart afterwards.

Index and cache lifecycle:

| Flag / command | Effect | Cost |
|---|---|---|
| *(re-run, no flags)* | upserts this run's chunks, then sweeps any orphan under the same `doc` | $0 |
| `--recreate-index` | drops and rebuilds the **whole** chunk collection; the only way to change dimension or distance. Warns when it drops points belonging to docs outside this run | $0 — never touches the cache |
| `--reset-embedding-cache` | drops the memo cache; everything is re-embedded | ~$0.003 per manual pair |
| `--collection-prefix P` | a completely separate pair of collections, for experiments | $0 to create, re-embeds on first use |
| `docker compose down` | stops the server, **keeps** the index and the cache | — |
| `docker compose down -v` | destroys both volumes | ~$0.003 to rebuild |

Useful flags: `--celex MiCA=02023R1114-20240109` (use a consolidated expression
instead of the as-published text), `--top-k`, `--gap-floor`,
`--judge-model gpt-4.1-mini`, `--budget-usd`, `--retriever numpy` (the in-memory
reference implementation), `--no-store-chunk-text` (keep WSP prose out of the
Qdrant payload).

## Outputs

Written to `--out`:

- `gap_report.html` — self-contained, grouped regulation → block → article,
  verdict colour-coded, per-article expected-vs-found tables and the retrieved
  excerpts. The header states the documents, service-line profile, models,
  prompt version, thresholds and total cost.
- `gap_report.csv` — one row per article, with cited chunk ids, cited headings,
  cited pages, obligations satisfied/total, auto-gap flag, model, prompt
  version and article content hash.
- `results.json` — the same data structured, consumed by `score_golden.py`. Its
  `context.vector_store` block records which index produced the numbers: backend,
  URL, both collection names, the retriever, whether search was exact, and the
  fetch limit.
- `chunks.json` — every chunk with its provenance.
- `audit.jsonl` — one line per billed call and per auto-gap decision: model,
  prompt version, tokens, USD, article hash, candidate citations. Auditability
  is a product requirement, so the POC practises it.

## Cost

Measured on `Sample WSP.pdf` + fixture: 206 chunks / 143k embedding tokens
(~$0.003) and at most 53 judge calls (~$0.03 if nothing auto-gaps) — well under
$0.05 per full run. `--budget-usd` is a hard cap: the run aborts cleanly and
still writes a partial report.

The embedding half of that is paid once: the vectors live in Qdrant and survive
`docker compose down`, so re-runs and prompt iteration cost only judge calls.
`docker compose down -v` throws them away, at ~$0.003 to rebuild.

---

## Design notes

**Article scoping** (`DORA_SCOPE`, `mica_scope`) is configuration, not code.

- DORA, 27 articles: 5–15 (ICT risk management), 16 (simplified regime, flagged
  either/or with 5–15), 17–23 (incidents), 24–27 (testing; 26–27 flagged
  TLPT-only), 28–30 (third-party risk), 45 (information sharing; a gap there is
  reported as *not applicable (voluntary)*). Art. 31–44 and 46+ are ESA/authority
  obligations, not firm obligations. **All annexes are out of scope.**
- MiCA, 26 articles for the default profile: 59–65, 66–74, 86–92, plus the
  service-specific articles pulled in by `--profile` (custody→75, exchange→77,
  execution→78, and so on). Titles II–IV (issuer obligations) and Title VII+ are
  excluded. **MiCA verdicts are only valid for the stated profile** — the report
  header and an explicit banner say so. This asymmetry (DORA universal, MiCA
  service-filtered) is SA-13.

**Auto-gap floor.** If no chunk clears `--gap-floor` cosine against any of an
article's paragraphs, the article is marked `gap` with no LLM call. On US-domain
manuals this is expected to resolve a third to half of the articles, and it is
what keeps the cost estimate honest at production scale.

**Retrieval.** Every WSP chunk and every *article paragraph* is embedded; an
article's score against a chunk is the max over its paragraphs. Per-paragraph
embedding is what lifts recall on long articles such as DORA Art. 28.

**Judgment rubric.** The model must decompose the article into individual
obligations before judging, and may cite only the chunk ids it was given.
`validate_wsp.py` then enforces the citation rule deterministically: citations
outside the retrieved set are stripped, an obligation with no surviving citation
is marked unsatisfied, and a `covered`/`partial` verdict with no citation at all
is downgraded to `gap`. WSP text is treated as untrusted data in the system
prompt (prompt-injection surface — customer uploads are adversarial-capable).

**Provider seam.** `EmbeddingProvider` and `JudgeProvider` are the interfaces;
`OpenAIEmbedding` and `OpenAIJudge` are the only OpenAI-specific classes. The
production stack is AWS Bedrock, and prompts, rubric, JSON schema and thresholds
port unchanged. The vector store is a **second, independent seam**: everything
Qdrant-specific lives in `vector_store.py`, so the Bedrock port's companion move
— Qdrant to OpenSearch or pgvector — rewrites that module and nothing else. That
is the architectural point of keeping it a separate file.

**Caching.** Regulation JSON is cached on disk per CELEX. Embeddings are memoised
in a Qdrant collection keyed by `sha256(model + text)` — the same key the retired
`out/regs/embeddings.json.gz` used. Prompt iteration never re-embeds.

## Vector store

Two collections, both created on first use:

| Collection | Holds | Distance | Searched? |
|---|---|---|---|
| `wsp_chunks_text_embedding_3_small` | one point per WSP chunk | COSINE | yes, filtered by `doc` |
| `wsp_embcache_text_embedding_3_small` | one point per `sha256(model + text)` | DOT | never |

The embedding model is part of both names because dimensionality and distance are
collection-level configuration: `-large` at 3072 dimensions can never share a
collection with `-small` at 1536.

**Why the cache uses DOT.** Under Cosine distance Qdrant L2-normalises the stored
vector and does not keep the original, so reading it back would return a
normalised vector rather than the one the provider returned. The cache is a
key/value store that is never searched, so DOT keeps it lossless.

**Why searches use `exact=True`.** At 200–500 points a full scan is both faster
than ANN and exact, which removes recall from the list of things a change has to
be reasoned about. `indexing_threshold=0` additionally means no HNSW graph is
ever built, so a query that forgets `exact=True` is still exact.

**Point ids** are `uuid5(POINT_NS, "<kind>\0<value>")` — chunks keyed on
`chunk_id`, cache points on the hex digest. Never keyed on `content_hash`: that
is `sha256(body)` and excludes the heading path, so two chunks with identical
bodies under different headings would collide and one would silently vanish.

**Lifecycle** is upsert-then-sweep on every run: this run's points are written,
then anything else under the same `doc` is deleted. Re-running an unchanged
manual converges rather than accumulating, a re-extraction producing fewer chunks
drops the tail, a pooled run never touches another doc's points, and a crash
mid-run leaves a superset rather than an empty index. A count through the `doc`
filter is asserted against the number of chunks before any article is scored —
without that guard a stale filter would auto-gap an entire run and still produce
a plausible-looking report.

**The gap floor stays client-side.** It is never passed as Qdrant's
`score_threshold`: a below-floor article would then return zero points, and
`best_similarity` would be recorded as `0.0` instead of its true value,
corrupting `results.json`, the confidence figure, `audit.jsonl` and the CSV. The
floor is a *cost* heuristic, not a relevance filter — it needs the number it
compares against.

**Inspecting it.** The dashboard is at <http://localhost:6333/dashboard>. Note
that chunk payloads contain **client WSP prose** by default; `--no-store-chunk-text`
opts out, and `docker compose down -v` is the teardown.

**`doc` is a basename.** `doc_name()` derives it from the WSP filename, so two
identically-named files in different directories collapse to the same `doc` and
their point ids collide. That previously corrupted one report; now it corrupts
stored state. Give pooled inputs distinct filenames.

### Verifying a migration or a new server

`tools/` carries the two checks used when the store changed. Run them against any
new Qdrant before trusting its numbers:

```bash
# 1. contract: does this server behave the way vector_store.py assumes?
python3 scripts/wsp_poc/tools/smoke_vector_store.py http://127.0.0.1:6333

# 2. retrieval parity: numpy reference vs. the server, same cached vectors,
#    zero spend (--gap-floor 1.0 auto-gaps everything, so no judge call fires)
python3 scripts/wsp_poc/validate_wsp.py --wsp out/wsp/sample_wsp.txt \
    --profile exchange,execution,custody --regs-cache out/regs/ \
    --retriever numpy --gap-floor 1.0 --offline --out /tmp/parity/numpy/
python3 scripts/wsp_poc/validate_wsp.py --wsp out/wsp/sample_wsp.txt \
    --profile exchange,execution,custody --regs-cache out/regs/ \
    --gap-floor 1.0 --offline --out /tmp/parity/qdrant/
python3 scripts/wsp_poc/tools/compare_parity.py \
    /tmp/parity/numpy/results.json /tmp/parity/qdrant/results.json
```

The hard gate is set equality of the retrieved `chunk_id`s. Ordering differences
are reported rather than failed, but only tolerated among near-ties — twenty
pairs across the two manuals sit within 5e-4 of each other, and a swap between
0.61 and 0.54 would not be benign.

## Evaluation

`score_golden.py` scores the two AI stages separately — retrieval `recall@k` and
verdict accuracy, plus verdict accuracy *given* correct retrieval. A blended
number cannot tell you whether to fix chunking/embedding or the prompt/rubric.
That split is the proposed measurement method for the Section 6.2 85% bar
(EV-01 / EV-08).

Golden set: ~26 labels across the two manuals — known gaps, expected partials,
and the synthetic true positives. Every label except the fixture items ships as
`verified: false`; confirm them against the manual (and against `chunks.json`
for the `evidence_hint` strings) before quoting any accuracy number. The scorer
prints a warning while unverified labels remain.

## Known limitations

- Both samples are **US FINRA broker-dealer manuals**. Gap-heavy results are
  expected and intended (they stress gap detection), but precision on a real EU
  CASP manual is untested. The synthetic fixture only partially compensates. A
  realistic MiCA/DORA-aligned manual is needed before any UAT-grade accuracy
  claim.
- Heading detection works from text alone (font signals are gone after
  extraction), so unnumbered bold headings are approximated by ALL-CAPS and
  trailing-colon lines. Some numbered list items still register as headings;
  harmless here since provenance survives either way.
- Naive whole-manual-in-context is ruled out by cost even at POC scale. The
  retrieval-first design is an architectural finding that carries to production
  economics.
