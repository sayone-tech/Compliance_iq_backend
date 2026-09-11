# AI Engine Diagrams

Standalone exports of every diagram embedded in `../AI_Engine_Architecture.md`.
The Markdown document is the source of truth; these files exist because
`scripts/archmd2docx.py` renders Mermaid fences as code blocks, not pictures, so
the .docx build needs images.

| File | Diagram |
|---|---|
| `00-notation-legend` | DFD notation used throughout (shape = primary encoding) |
| `01-dfd-level0-context` | Level 0 — the AI Engine as one process |
| `02-dfd-level1-engine` | Level 1 — 7 processes, 10 data stores, 5 planes |
| `03-dfd-1.0-regulatory-ingestion` | Level 2 — CELLAR fetch, Formex parse, hash, diff, ChangeSet |
| `04-dfd-3.0-wsp-document-intelligence` | Level 2 — parse, OCR, section tree, chunk, embed, index |
| `05-dfd-4.0-evidence-retrieval` | Level 2 — applicability, hybrid retrieval, rerank, relevance floor |
| `06-dfd-5.0-judgment-verification` | Level 2 — cache probe, generation, verification gate, confidence policy |
| `07-dfd-6.0-change-impact-revalidation` | Level 2 — impact map, human gate, hash reuse, run diff, alerts |
| `08-dfd-7.0-governance-eval-harness` | Level 2 — golden set, harness run, 85% promotion gate |
| `09-caching-cost-layers` | The four caches and where each applies |
| `10-sequence-end-to-end` | Control flow — Journey A (upload) and Journey B (regulation change) |
| `11-state-ai-job` | `ai_job` lifecycle |
| `12-state-finding` | Finding lifecycle, engine's authority boundary marked |
| `13-state-control-version` | Control version lifecycle including `invalidated` |
| `14-er-ai-engine-data-model` | Entities the engine reads and writes |

Each diagram ships as both `.mmd` (source) and `.svg` (rendered).

## Regenerating

Edit the Mermaid fence in `../AI_Engine_Architecture.md`, re-export the `.mmd`
files from it, then render:

```bash
npm install @mermaid-js/mermaid-cli
npx mmdc -i <file>.mmd -o <file>.svg -b white
```

On a headless Linux box without a bundled Chromium, point the CLI at the system
browser with a puppeteer config file:

```json
{"executablePath": "/usr/bin/google-chrome",
 "args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]}
```

and pass it with `-p pptr.json`.

## Diagram conventions

- Sharp rectangle = external entity · rounded rectangle = process · cylinder = data store.
- Red stroke = mandatory human gate. Purple stroke = a call leaving the engine to an AI provider (a cost and data-residency event).
- Shape carries the meaning; colour only reinforces it, so the diagrams survive greyscale printing and colour-vision deficiency.
- A data store may be drawn twice in one diagram (e.g. `D1 (read)` / `D1 (write)` in 1.0) — standard DFD practice to keep flow readable. It is one store.
