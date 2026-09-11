# Test-Case Execution POC (LangGraph + LangSmith + FastAPI)

Simulates a human control tester. Given a **test case** (numbered procedure steps) and an
**evidence** PDF, the graph judges every step -- PASS / FAIL / INCONCLUSIVE, a tester-style
narrative, findings, citations into the evidence -- aggregates an overall result, scores
itself against the human tester's answers, and reports exact token usage and USD.

Sample inputs: `docs/SampleTest/TestCase.pdf` (BCP-RM-005, 7 steps, human result
*Partially Effective*, 5 pass / 2 fail) and `docs/SampleTest/Evidence.pdf` (the 154-page
WSP; the Business Continuity Plan the tester used is Appendix B, pp. 123-135).

**The output is a suggestion set for human review. It never auto-determines compliance**
(same framing as the WSP POC, PRD FR-31).

---

## Pipeline

```
parse_testcase ──> ingest_evidence ──> judge_step ×N (parallel, Send) ──> aggregate ──> score
   LLM (or fixture)   pdftotext + chunk        retrieval | full context     rules + 1 LLM     tag match +
                      + embed + Qdrant         + date facts + structured    summary           LLM faithfulness
                      (cached by file hash)    verdict (elements first)
```

| Node | What it does | LLM calls |
|---|---|---|
| `parse_testcase` | TestCase PDF -> `TestCase` (steps for the judge, ground truth kept apart). Skipped when a fixture is given. | 1 |
| `ingest_evidence` | `wsp_poc.extract_wsp.build_document` -> `WspChunker` -> `OpenAIEmbedding` (memo-cached in Qdrant) -> `QdrantRetriever.index`. In-process cache by sha256 of the PDF. | 0 (embeddings only, $0 on repeat) |
| `judge_step` | Per step: 3-5 search queries (mini model), top-k retrieval + neighbour chunks, deterministic **date facts**, then one structured-output call that lists the step's required *elements* before choosing the tag. Citations to unseen chunks are dropped. | 2 per step |
| `aggregate` | Rule-based overall (all pass -> Effective; mix -> Partially Effective; none -> Not Effective; any inconclusive -> Needs Review) + one summary paragraph. | 1 |
| `score` | Tag exact-match vs human, plus an LLM-judge faithfulness score (0-1) of the AI narrative against the human one. | 1 per step |

Context modes: `retrieval` (default, ~6-8K evidence tokens per step) and `full` (whole
evidence, ~85K tokens per step, prompt-cached by OpenAI after the first step).

All prompts are in `prompts.py`; the version tag `config.PROMPT_VERSION` lands in every
audit line and LangSmith run.

Reused from `scripts/wsp_poc/`: extraction, chunker, embedding + Qdrant cache/retriever,
`CostMeter` + `PRICING` (see `cost.py` for the cached-token extension).

---

## Setup

### Third-party accounts

| Service | Needed for | Setup |
|---|---|---|
| **OpenAI** | all LLM + embedding calls | `OPENAI_API_KEY` in `scripts/testcase_poc/.env` (or `scripts/wsp_poc/.env`, or exported). Never a CLI flag. |
| **LangSmith** | tracing, per-node token/cost, eval datasets and experiments | 1. Sign up at https://smith.langchain.com (free *Developer* plan: 5k traces/month is plenty). 2. Settings -> API Keys -> *Create API Key* (Personal Access Token). 3. Put `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY=lsv2_pt_...`, `LANGSMITH_PROJECT=controliq-testcase-poc` in `.env`. **If the account was created in the EU region** (ours is) also set `LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com` -- the US endpoint answers `403 Forbidden` to an EU key. 4. Optional: Settings -> *Usage & Billing* -> model pricing map if a model's cost column shows empty. **Traces contain evidence text**; the EU endpoint keeps them in the EU, or leave tracing off for real client documents. |
| **Qdrant** | chunk index + embedding memo cache | `docker compose up -d qdrant` (already in the repo). `QDRANT_URL=none` runs in-memory instead. |
| poppler | `pdftotext` | in the Docker image; natively `sudo apt install poppler-utils`. |

```bash
cp scripts/testcase_poc/.env.example scripts/testcase_poc/.env   # then edit
```

### Docker (recommended)

```bash
docker compose up -d qdrant
docker compose build testcase-api
docker compose up -d testcase-api          # http://127.0.0.1:8010/docs
```

The repo is bind-mounted, so uploads and reports land in `out/testcase/<run_id>/` on the
host. Host port is `TC_API_PORT` (default 8010; 8000 is often taken).

### Native

```bash
python3 -m venv .venv && .venv/bin/pip install -r scripts/testcase_poc/requirements.txt
docker compose up -d qdrant
cd scripts && PYTHONPATH=. ../.venv/bin/uvicorn testcase_poc.app:app --reload --port 8010
```

---

## Use

### API

```bash
# fixture test case + the sample evidence
curl -X POST localhost:8010/runs -F fixture=bcp_rm_005 -F use_sample_evidence=true -F as_of_date=2026-09-11

# upload both PDFs, whole-document context, stronger judge
curl -X POST localhost:8010/runs -F testcase=@docs/SampleTest/TestCase.pdf \
     -F evidence=@docs/SampleTest/Evidence.pdf -F context_mode=full -F judge_model=gpt-4.1

curl localhost:8010/runs/<run_id>            # JSON: verdicts, overall, scores, usage, langsmith_url
open http://localhost:8010/runs/<run_id>/report   # HTML side-by-side with the human narrative
curl localhost:8010/runs                     # every run, live and on disk
curl -X POST localhost:8010/evals -F context_mode=retrieval   # LangSmith experiment (blocking)
```

`POST /runs` returns `202` immediately; poll `GET /runs/{id}` until `status` is `done` or
`error`. `as_of_date` is the date of testing: "current / annual review" checks are decided
against it (the sample plan was approved 2023-01-05, so anything after 2024-01-05 fails
step 1 -- as the human tester found).

### CLI

```bash
cd scripts
PYTHONPATH=. ../.venv/bin/python -m testcase_poc.cli --fixture bcp_rm_005 --as-of-date 2026-09-11
PYTHONPATH=. ../.venv/bin/python -m testcase_poc.cli --testcase ../docs/SampleTest/TestCase.pdf --context-mode full
PYTHONPATH=. ../.venv/bin/python -m testcase_poc.cli --fixture bcp_rm_005 --dry-run     # no key, no LLM calls
# under compose:
docker compose run --rm testcase-api python3 -m testcase_poc.cli --fixture bcp_rm_005
```

### Outputs (`out/testcase/<run_id>/`)

- `result.json` -- everything the API returns: per-step verdict with `elements`, `findings`,
  `citations`, retrieval provenance (`context.retrieved`), scores, `usage`.
- `report.html` -- AI verdict and narrative next to the human's, with the grader's comment.
- `audit.jsonl` -- one line per LLM/embedding call: model, tokens (incl. cached), USD, stage.
- `input/` -- uploaded PDFs.

### LangSmith evaluation

```bash
cd scripts
PYTHONPATH=. ../.venv/bin/python -m testcase_poc.evals.build_dataset --fixture bcp_rm_005
PYTHONPATH=. ../.venv/bin/python -m testcase_poc.evals.run_eval --context-mode retrieval
PYTHONPATH=. ../.venv/bin/python -m testcase_poc.evals.run_eval --context-mode full --judge-model gpt-4.1
```

Dataset `controliq-testcase-bcp-rm-005`: one example per step; inputs = what the judge
sees, outputs = the human's tag + narrative. Evaluators (`evals/evaluators.py`):

| key | meaning |
|---|---|
| `tag_exact_match` | AI tag == human tag |
| `narrative_faithfulness` | LLM-judge 0-1: same conclusion and key facts as the human narrative |
| `citation_grounding` | fraction of citation quotes found verbatim in the evidence (0 if none) |
| `elements_decomposed` | the judge listed >= 2 required elements before deciding |

Experiments are named `<mode>-<judge model>-<hash>` so they line up side by side under
*Datasets -> controliq-testcase-bcp-rm-005 -> Experiments*. Each experiment's own token
cost is in `out/testcase/evals/<stamp>/summary.json` and in the trace view.

---

## Measured results (LangSmith experiments, prompt v2026-09-11.4, as_of_date 2026-09-11)

| mode | judge | tag accuracy | faithfulness | citation grounding | tokens in (cached) / out | USD / experiment |
|---|---|---|---|---|---|---|
| retrieval | gpt-4.1-mini | **7/7** | 0.61 | 0.61 | ~70K (0) / ~5K | **$0.05** |
| full | gpt-4.1-mini | 6/7 (step 2) | 0.61 | 0.64 | ~590K (~500K) / ~4K | **$0.11** |
| retrieval | gpt-4.1 | 6/7 | -- | -- | ~70K / ~6K | $0.18 |

Earlier prompt versions scored 5-6/7 in both modes; steps 2 and 7 flipped between runs
until the per-role successor rule and the roster-currency block were added (v.4). Run the
experiment a few more times before trusting any single number -- `temperature=0` does not
make gpt-4.1-mini deterministic, and query expansion changes the retrieved set.

Every USD figure includes the gpt-4.1 faithfulness grader (~$0.015). The full-mode price
depends on OpenAI prompt caching: the evidence sits *before* the step text so all steps
share one ~85K-token prefix, and `graph._prime_lock` makes the first step finish alone
before the rest run in parallel. Cold and fully parallel it costs ~$0.26. Evidence
embedding is ~73K tokens = $0.0015 once, then $0 (Qdrant memo cache). Parsing the
TestCase PDF instead of using the fixture adds ~$0.005.

Known weak spot: **step 2 (successors for key roles)** -- the human failed it because the
CEO / CCO / CFO have no documented successor; the model sometimes accepts the DR
coordinator back-up as "successors documented". Faithfulness sits at ~0.7 on matched
steps because the human narrative cites reconciliations against HR rosters and IT
inventories the AI was never given.

Deterministic helpers that were needed to get here (both visible in the trace as plain
data): `dates.date_facts` (mini models cannot reliably tell that January 2023 is more than
12 months before September 2026) and the *elements-first* verdict schema
(`schemas.ElementCheck`).

---

## Files

| file | role |
|---|---|
| `app.py` | FastAPI: `/runs`, `/runs/{id}`, `/runs/{id}/report`, `/evals`, `/health` |
| `cli.py` | same run from the shell; `--dry-run` needs no key |
| `runner.py` | `run_testcase()` -- builds the config, invokes the graph, writes outputs |
| `graph.py` | the StateGraph and its nodes |
| `evidence.py` | ingest / cache / retrieve on top of `wsp_poc` |
| `dates.py` | deterministic date extraction + currency arithmetic for the judge |
| `cost.py` | `RunMeter` (thread-safe CostMeter with cached-token pricing) + `UsageCallback` |
| `prompts.py`, `schemas.py`, `config.py` | prompts, Pydantic models, settings |
| `fixtures/bcp_rm_005.json` | golden set transcribed from `TestCase.pdf` |
| `evals/` | LangSmith dataset builder, evaluators, experiment runner |
| `langgraph.json` | `pip install "langgraph-cli[inmem]" && langgraph dev` for LangGraph Studio |

## Known limits

- POC only: runs are in-process background tasks, one worker; no auth; no persistence
  beyond `out/`. Evidence indexes live in the process -- a restart re-ingests (embeddings
  still come from the Qdrant cache).
- One evidence PDF per run. The tester's real work reconciles against HR rosters, IT
  inventories, etc.; the AI only sees the documents it is given and says so in the narrative.
- Text-native PDFs only (no OCR), same as the WSP POC.
- Pricing table (`cost.py`) is hand-maintained -- re-verify before quoting numbers.
