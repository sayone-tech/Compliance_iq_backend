"""One entry point for the API, the CLI and the evals: run_testcase()."""
import html
import json
import os
import sys
import uuid
from datetime import date, datetime, timezone

from testcase_poc.config import FIXTURES_DIR, PROMPT_VERSION, load_settings, require_openai_key
from testcase_poc.cost import RunMeter, UsageCallback
from testcase_poc.graph import RunContext, graph
from testcase_poc.schemas import RunResult, TestCase, UsageSummary


def load_fixture(name):
    path = name if os.path.exists(name) else os.path.join(FIXTURES_DIR, f"{name}.json")
    with open(path, encoding="utf-8") as handle:
        return TestCase.model_validate(json.load(handle))


def new_run_id():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6]


def run_testcase(evidence_path, testcase_path=None, fixture=None, context_mode="retrieval",
                 as_of_date=None, tester="CITT", run_id=None, settings=None, dry_run=False,
                 out_dir=None):
    """Run the graph once. Returns a RunResult; also writes result.json, audit.jsonl and
    report.html under <out_dir>/<run_id>/."""
    if not (testcase_path or fixture):
        raise ValueError("need testcase_path or fixture")
    settings = settings or load_settings()
    run_id = run_id or new_run_id()
    as_of_date = as_of_date or date.today().isoformat()
    out_dir = os.path.join(out_dir or settings.out_dir, run_id)
    os.makedirs(out_dir, exist_ok=True)
    api_key = None if dry_run else require_openai_key(settings)

    meter = RunMeter(settings.budget_usd, os.path.join(out_dir, "audit.jsonl"))
    ctx = RunContext(settings=settings, meter=meter, api_key=api_key, dry_run=dry_run)
    result = RunResult(run_id=run_id, status="running", context_mode=context_mode,
                       as_of_date=as_of_date, judge_model=settings.judge_model,
                       started_at=datetime.now(timezone.utc).isoformat())
    state = {
        "run_id": run_id, "as_of_date": as_of_date, "context_mode": context_mode,
        "tester": tester, "evidence_path": evidence_path,
        "testcase_path": testcase_path,
        "testcase": load_fixture(fixture).model_dump() if fixture else None,
        "verdicts": [],
    }
    config = {"configurable": {"ctx": ctx}, "callbacks": [UsageCallback(meter)],
              "run_name": f"testcase_run {run_id}",
              "tags": [f"mode:{context_mode}", f"judge:{settings.judge_model}"],
              "metadata": {"run_id": run_id, "context_mode": context_mode,
                           "judge_model": settings.judge_model, "as_of_date": as_of_date,
                           "prompt_version": PROMPT_VERSION}}
    try:
        final, url = _invoke_traced(state, config, settings)
        result.testcase = TestCase.model_validate(final["testcase"])
        result.evidence_doc_id = final.get("evidence_doc_id")
        result.evidence_pages = final.get("evidence_pages")
        result.evidence_chunks = final.get("evidence_chunks")
        result.verdicts = sorted(final.get("verdicts", []),
                                 key=lambda v: int(v["step_id"].split("_")[-1]))
        result.overall = final.get("overall")
        result.scores = final.get("scores", [])
        result.tag_accuracy = final.get("tag_accuracy")
        result.overall_match = final.get("overall_match")
        result.langsmith_url = url
        result.status = "done"
    except Exception as exc:                      # partial result is still worth writing
        result.status = "error"
        result.error = f"{type(exc).__name__}: {exc}"
        print(f"run {run_id} failed: {result.error}", file=sys.stderr)
    result.usage = UsageSummary.model_validate(meter.summary())
    result.finished_at = datetime.now(timezone.utc).isoformat()
    write_outputs(result, out_dir)
    return result


def _invoke_traced(state, config, settings):
    """Wrap the graph in a LangSmith root run so the API can hand back a trace URL."""
    if not settings.tracing_enabled:
        return graph.invoke(state, config=config), None
    from langsmith import trace
    with trace(name=config["run_name"], run_type="chain", tags=config["tags"],
               metadata=config["metadata"],
               inputs={"run_id": state["run_id"], "context_mode": state["context_mode"],
                       "evidence_path": state["evidence_path"]}) as root:
        final = graph.invoke(state, config=config)
        root.end(outputs={"overall": final.get("overall"),
                          "tag_accuracy": final.get("tag_accuracy")})
        try:
            url = root.get_url()
        except Exception:
            url = None
    return final, url


def write_outputs(result, out_dir):
    with open(os.path.join(out_dir, "result.json"), "w", encoding="utf-8") as handle:
        handle.write(result.model_dump_json(indent=2))
    with open(os.path.join(out_dir, "report.html"), "w", encoding="utf-8") as handle:
        handle.write(render_html(result))


def render_html(result):
    e = html.escape
    tc = result.testcase
    truth = {g.step_id: g for g in (tc.ground_truth if tc else [])}
    steps = {s.id: s for s in (tc.steps if tc else [])}
    scores = {s["step_id"]: s for s in result.scores}
    rows = []
    for v in result.verdicts:
        step = steps.get(v["step_id"])
        g = truth.get(v["step_id"])
        sc = scores.get(v["step_id"], {})
        cites = "".join(f"<li><code>{e(c['chunk_id'])}</code> pp.{e(c['pages'])}: "
                        f"<q>{e(c['quote'])}</q></li>" for c in v.get("citations", []))
        finds = "".join(f"<li>{e(f)}</li>" for f in v.get("findings", []))
        match = "" if g is None else ("match" if sc.get("tag_match") else "mismatch")
        rows.append(f"""
<section class="step {e(v['tag'].lower())} {match}">
  <h3>Step {step.number if step else '?'}: {e(step.instruction if step else v['step_id'])}</h3>
  <p><b>AI:</b> <span class="tag">{e(v['tag'])}</span> ({e(v['action_taken'])}, confidence {v['confidence']:.2f})
     {'' if g is None else f"&nbsp; <b>Human:</b> <span class='tag'>{e(g.tag)}</span> ({e(g.action_taken or '')}) &nbsp; <b>{match}</b>"}
     {'' if sc.get('narrative_faithfulness') is None else f"&nbsp; faithfulness {sc['narrative_faithfulness']:.2f}"}</p>
  <p><b>AI narrative:</b> {e(v['narrative'])}</p>
  {'' if g is None else f"<p class='human'><b>Human narrative:</b> {e(g.narrative)}</p>"}
  {'' if not sc.get('faithfulness_reasoning') else f"<p class='grader'><b>Grader:</b> {e(sc['faithfulness_reasoning'])}</p>"}
  {f'<p><b>Findings:</b></p><ul>{finds}</ul>' if finds else ''}
  {f'<p><b>Citations:</b></p><ul>{cites}</ul>' if cites else ''}
  <p class="meta">context: {e(json.dumps({k: v['context'][k] for k in ('mode', 'chunks', 'tokens')}))}</p>
</section>""" if v.get("context") else f"<section><h3>{e(v['step_id'])}</h3><p>{e(v['narrative'])}</p></section>")
    usage = result.usage.model_dump() if result.usage else {}
    by_model = "".join(
        f"<tr><td>{e(m)}</td><td>{u['calls']}</td><td>{u['in']:,}</td><td>{u.get('cached', 0):,}</td>"
        f"<td>{u['out']:,}</td><td>${u['usd']:.4f}</td></tr>"
        for m, u in usage.get("by_model", {}).items())
    ov = result.overall
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>{e(tc.control_id if tc else result.run_id)} -- test case run</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:60rem;margin:2rem auto;padding:0 1rem;line-height:1.45}}
.tag{{font-weight:700}} .pass .tag:first-of-type{{color:#0a7f3f}} .fail .tag:first-of-type{{color:#b3261e}}
.inconclusive .tag:first-of-type{{color:#8a6d00}} section{{border:1px solid #ddd;border-radius:6px;padding:.5rem 1rem;margin:1rem 0}}
.mismatch{{border-color:#b3261e}} .human{{color:#444}} .grader{{color:#555;font-size:.92em}} .meta{{color:#777;font-size:.85em}}
table{{border-collapse:collapse}} td,th{{border:1px solid #ccc;padding:.2rem .6rem;text-align:right}} td:first-child{{text-align:left}}
q{{font-style:italic}}
</style></head><body>
<h1>{e(tc.control_id + ' -- ' + tc.title if tc else result.run_id)}</h1>
<p><b>Run</b> {e(result.run_id)} &middot; status {e(result.status)} &middot; mode {e(result.context_mode)} &middot;
judge {e(result.judge_model)} &middot; as of {e(result.as_of_date)}
{'' if not result.langsmith_url else f' &middot; <a href="{e(result.langsmith_url)}">LangSmith trace</a>'}</p>
{'' if tc is None else f'<p><b>Assessment question:</b> {e(tc.assessment_question)}</p>'}
{'' if result.error is None else f'<p style="color:#b3261e"><b>Error:</b> {e(result.error)}</p>'}
{'' if ov is None else f"<h2>Overall: {e(ov.result)} ({ov.passed} passed, {ov.failed} failed, {ov.inconclusive} inconclusive)</h2><p>{e(ov.summary)}</p>"}
{'' if result.tag_accuracy is None else f"<p><b>Tag accuracy vs human:</b> {result.tag_accuracy:.0%} &middot; overall result match: {result.overall_match}</p>"}
<h2>Usage</h2>
<table><tr><th>model</th><th>calls</th><th>input</th><th>cached</th><th>output</th><th>USD</th></tr>{by_model}
<tr><td><b>total</b></td><td>{usage.get('calls', 0)}</td><td>{usage.get('total_input_tokens', 0):,}</td>
<td>{usage.get('cached_tokens', 0):,}</td><td>{usage.get('total_output_tokens', 0):,}</td><td><b>${usage.get('total_usd', 0):.4f}</b></td></tr></table>
<p class="meta">evidence {e(result.evidence_doc_id or '')}: {result.evidence_pages} pages, {result.evidence_chunks} chunks &middot; prompt {e(PROMPT_VERSION)}</p>
<h2>Steps</h2>
{''.join(rows)}
<p class="meta">AI output is a suggestion set for human review. It never auto-determines compliance.</p>
</body></html>"""
