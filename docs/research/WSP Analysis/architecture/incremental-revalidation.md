# Incremental Revalidation Algorithm

**Scope:** How the platform re-validates only what changed — after a regulatory change, a control-logic change, or a new WSP version — minimizing LLM calls while never silently reusing a stale verdict.
**Depends on:** schema in `data-and-events.md` (append-only `evaluations`, `text_sha256` on sections/paragraphs, `control_versions`, `change_impacts`).
**Date:** 2026-08-17. Labels: ARCHITECTURAL RECOMMENDATION / ASSUMPTION.

---

## 1. The dependency index

The core artifact is a materialized dependency table linking every evaluation to exactly the inputs that determine it. It is written *at evaluation time* (not inferred later), so it is always exact:

```
control_section_dependency(
  evaluation_id FK,            -- the evaluation this row explains
  control_version_id FK,
  wsp_version_id FK,
  wsp_section_id FK,           -- one row per section actually consulted
  section_text_sha256,         -- content hash at evaluation time
  requirement_ids uuid[],      -- regulation-side inputs
  reg_text_sha256,             -- hash of concatenated paragraph texts backing those requirements
  prompt_sha256, model_id,     -- logic-side inputs
  PK(evaluation_id, wsp_section_id)
)
```

An evaluation is **stale** iff any of its recorded input hashes no longer matches current state:
- section text changed (new WSP version edited that section),
- regulation paragraph text changed (amendment/consolidation),
- control logic changed (`control_versions` bumped, or `change_impacts.impact = 'invalidates'`),
- model/prompt changed (platform upgrade — treat as control-logic change, roll out gradually).

Everything not stale is **reusable**: the prior verdict is carried forward into the new run with `reused_from_evaluation_id` set, at zero LLM cost.

## 2. Cache & reuse layers (cheapest first)

1. **Deterministic controls** (regex/keyword/structural checks): pure functions of section text → keyed by `(control_version_id, section_text_sha256)`. Cache hit = free, recompute = microseconds. Never send to an LLM.
2. **Embeddings**: keyed by `(embedding_model, chunk_text_sha256)`. A new WSP version typically edits a handful of sections; 90%+ of chunks re-hash identically and reuse stored vectors (dedupe table `embedding_cache(text_sha256, model, vector)` — also dedupes boilerplate shared *across firms*).
3. **Retrieval sets**: the top-k evidence chunks per control are a function of (control's query embedding, wsp_version chunk set). If neither changed, the retrieval set is unchanged — skip re-retrieval.
4. **Semantic (LLM) evaluations**: keyed by `input_sha256 = H(prompt_sha256 ‖ model_id ‖ ordered evidence chunk hashes ‖ reg_text_sha256)`. Exact-match hit ⇒ reuse verdict verbatim. This catches the common case "new WSP version, this control's evidence sections untouched."
5. **LLM prompt caching** (provider-side): structure every evaluation prompt as `[static system + control definition + regulation excerpt] ‖ [firm evidence]`. The static prefix is identical across *all firms* for a given control — provider prompt caching prices it at ~0.1× on reads (see `cost-model.md`).

## 3. Algorithm (pseudocode)

```python
# ── Triggers ────────────────────────────────────────────────────────────────
# T1: regulatory change detected      -> revalidate_for_change(change_id)
# T2: control version published       -> revalidate_for_controls([cv_id])
# T3: new WSP version uploaded        -> revalidate_wsp(wsp_version_id)

def revalidate_for_change(change_id):
    change = load(regulatory_changes, change_id)
    # 1. Regulation-side impact (SQL over the mapping layer; no LLM)
    impacted_cvs = sql("""
        SELECT DISTINCT crm.control_version_id
        FROM control_requirement_map crm
        JOIN requirements r ON r.id = crm.requirement_id
        WHERE r.paragraph_id = ANY(:paras)""",
        paras=change.affected_paragraph_ids)
    impacted_cvs |= {ci.control_version_id
                     for ci in change_impacts(change_id) if ci.impact != 'none'}
    # 2. Firm-side blast radius via the dependency index
    targets = sql("""
        SELECT DISTINCT wsp_version_id, firm_id
        FROM control_section_dependency d
        JOIN latest_evaluation le USING (evaluation_id)   -- only current posture
        WHERE d.control_version_id = ANY(:cvs)""", cvs=impacted_cvs)
    fanout(targets, impacted_cvs, trigger='reg_change', change_id=change_id)

def revalidate_wsp(new_wsp_version_id):
    prev = previous_version(new_wsp_version_id)
    diff = section_diff(prev, new_wsp_version_id)        # by section path + text_sha256
    changed_sections = diff.modified | diff.added | diff.removed
    # Controls that consulted a changed section last time, plus controls whose
    # retrieval might newly hit an ADDED section (re-run retrieval for all
    # semantic controls, but LLM-call only where the retrieval set changed).
    impacted_cvs = sql("""
        SELECT DISTINCT control_version_id FROM control_section_dependency
        WHERE wsp_version_id = :prev AND wsp_section_id = ANY(:secs)""",
        prev=prev.id, secs=[s.id for s in changed_sections])
    fanout([(new_wsp_version_id, firm_of(new_wsp_version_id))],
           all_control_versions(),                       # candidate set
           trigger='upload', hot_controls=impacted_cvs)

# ── Fan-out (Temporal workflow / batched jobs) ─────────────────────────────
def fanout(targets, candidate_cvs, trigger, **ctx):
    run_ids = {}
    for batch in chunks(targets, BATCH_SIZE):            # e.g. 500 firms/batch
        for (wsp_version_id, firm_id) in batch:
            run_ids[wsp_version_id] = insert(evaluation_runs,
                firm_id=firm_id, wsp_version_id=wsp_version_id,
                trigger=trigger, status='running', **ctx)
        plan = []                                        # LLM residue
        for (wsp_version_id, _) in batch:
            for cv in applicable(candidate_cvs, wsp_version_id):
                plan += plan_control(run_ids[wsp_version_id], cv, wsp_version_id)
        execute_llm_batch(plan)                          # provider Batch API, 50% off
    finalize(run_ids)

def plan_control(run_id, cv, wsp_version_id):
    if cv.kind == 'deterministic':
        persist(run_id, cv, run_deterministic(cv, wsp_version_id))   # never LLM
        return []
    # semantic / hybrid
    ev_chunks = retrieve_evidence(cv, wsp_version_id)    # uses embedding cache (§2.2–2.3)
    key = input_sha256(cv.prompt_sha256, cv.model_id,
                       [c.text_sha256 for c in ev_chunks], cv.reg_text_sha256)
    prior = lookup(evaluations, input_sha256=key)        # §2.4 exact-match reuse
    if prior and trigger_allows_reuse(cv):               # reg_change w/ 'invalidates' forbids reuse
        persist_reused(run_id, cv, prior)
        return []
    return [LLMTask(run_id, cv, ev_chunks, key)]         # only true residue hits the model

def execute_llm_batch(tasks):
    # Group by (model_id, prompt_sha256) so the shared prefix is provider-cache hot;
    # submit via Batch API; on completion:
    for t, result in run_batch(tasks):
        e = persist(evaluations, run=t.run_id, cv=t.cv, verdict=result.verdict,
                    severity=result.severity, input_sha256=t.key,
                    raw_output=result.json, cost_usd=result.cost)   # APPEND-ONLY
        write_dependency_rows(e, t.ev_chunks)            # §1, exact provenance

# ── Compare-previous & alert-on-worsening ──────────────────────────────────
SEV_RANK = {'info':0,'low':1,'medium':2,'high':3,'critical':4}
def finalize(run_ids):
    for wsp_version_id, run_id in run_ids.items():
        prev_run = previous_completed_run(wsp_version_id)
        for cur in evaluations_of(run_id):
            old = matching_eval(prev_run, cur.control_id)  # match by control lineage
            delta = classify(old, cur)
            # classify: NEW_GAP (pass->gap), WORSENED (sev rank up), IMPROVED,
            #           RESOLVED (gap->pass), UNCHANGED
            upsert_finding(cur, delta)                     # findings keep first_seen/last_seen
            if delta in ('NEW_GAP', 'WORSENED'):
                emit('notification.requested', firm=cur.firm_id,
                     dedupe_key=f'{cur.firm_id}:{cur.control_id}:{cur.verdict}:{cur.severity}')
            # IMPROVED/RESOLVED -> digest, not alert; UNCHANGED -> silent
        mark(run_id, status='completed')
```

## 4. Design points

- **Alert only on worsening.** Real-time alerts fire solely for `NEW_GAP`/`WORSENED`; improvements and unchanged results roll into a daily/weekly digest. `dedupe_key` on `notifications` prevents re-alerting the same (firm, control, verdict, severity) tuple across successive runs.
- **Reuse is forbidden where the trigger invalidates it.** `trigger_allows_reuse` returns False for controls flagged `invalidates` by the regulatory change even if hashes match — the *interpretation* changed although texts didn't (e.g. an ESMA Q&A reinterprets an unchanged article). This is the case hashes cannot see; it is driven by the human/curated `change_impacts` table. REQUIRES LEGAL / COMPLIANCE INTERPRETATION at curation time, by design.
- **`not_applicable` short-circuit.** `applicable(cv, wsp_version)` evaluates `requirements.applicability_expr` against firm metadata (entity class, services) before any retrieval — a large fraction of controls never reach the planner for a given firm.
- **LLM-call minimization summary:** deterministic-first → applicability filter → hash-level reuse → retrieval-set reuse → provider prompt caching on the residue → Batch API pricing on top. Expected residue for a typical regulatory change touching 3–5 controls: only those controls × affected firms, each a single cache-warm batched call (quantified in `cost-model.md`).
- **Idempotency & failure:** every LLMTask is keyed by `input_sha256`; re-delivery after a crash finds the persisted evaluation and skips. Batches are resumable child workflows (Temporal) or re-queued jobs; `evaluation_runs.status` makes partial runs visible and re-driable.
- ASSUMPTION: section diffing by `(path, text_sha256)` is reliable given a stable sectionizer; renumbering-only edits are handled by falling back to text-hash matching across paths before declaring sections added/removed.
