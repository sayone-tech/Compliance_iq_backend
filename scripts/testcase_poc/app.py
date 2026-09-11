"""FastAPI front for the test-case execution graph.

    uvicorn testcase_poc.app:app --reload --port 8000        (PYTHONPATH=scripts)

    POST /runs                 multipart: evidence=@pdf, testcase=@pdf | fixture=bcp_rm_005,
                               context_mode=retrieval|full, as_of_date=YYYY-MM-DD, judge_model=...
    GET  /runs                 list known runs (this process + out/testcase on disk)
    GET  /runs/{id}            RunResult JSON (status queued|running|done|error)
    GET  /runs/{id}/report     HTML report
    POST /evals                run the LangSmith experiment over the fixture dataset
    GET  /health
"""
import glob
import json
import os
import shutil
import threading
from datetime import date
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

from testcase_poc.config import FIXTURES_DIR, PROMPT_VERSION, SAMPLE_EVIDENCE, load_settings
from testcase_poc.runner import new_run_id, run_testcase
from testcase_poc.schemas import RunResult

app = FastAPI(title="ControlIQ test-case execution POC", version=PROMPT_VERSION)
_RUNS: dict[str, RunResult] = {}
_LOCK = threading.Lock()


def _settings():
    return load_settings()


def _upload_dir(run_id):
    path = os.path.join(_settings().out_dir, run_id, "input")
    os.makedirs(path, exist_ok=True)
    return path


async def _save(upload: UploadFile, dest_dir, fallback_name):
    name = os.path.basename(upload.filename or fallback_name)
    path = os.path.join(dest_dir, name)
    with open(path, "wb") as handle:
        shutil.copyfileobj(upload.file, handle)
    return path


def _execute(run_id, **kwargs):
    result = run_testcase(run_id=run_id, **kwargs)
    with _LOCK:
        _RUNS[run_id] = result


@app.get("/health")
def health():
    s = _settings()
    return {"ok": True, "judge_model": s.judge_model, "qdrant_url": s.qdrant_url,
            "langsmith_tracing": s.tracing_enabled, "langsmith_project": s.langsmith_project,
            "prompt_version": PROMPT_VERSION,
            "fixtures": sorted(os.path.splitext(f)[0] for f in os.listdir(FIXTURES_DIR)
                               if f.endswith(".json"))}


@app.post("/runs", status_code=202)
async def create_run(background: BackgroundTasks,
                     evidence: Optional[UploadFile] = File(default=None),
                     testcase: Optional[UploadFile] = File(default=None),
                     fixture: Optional[str] = Form(default=None),
                     context_mode: str = Form(default="retrieval"),
                     as_of_date: Optional[str] = Form(default=None),
                     tester: str = Form(default="CITT"),
                     judge_model: Optional[str] = Form(default=None),
                     budget_usd: Optional[float] = Form(default=None),
                     use_sample_evidence: bool = Form(default=False)):
    """Start a run. Either upload `testcase` (PDF) or name a `fixture`; upload `evidence`
    or set `use_sample_evidence=true` for docs/SampleTest/Evidence.pdf."""
    if context_mode not in ("retrieval", "full"):
        raise HTTPException(422, "context_mode must be 'retrieval' or 'full'")
    if not (testcase or fixture):
        raise HTTPException(422, "provide a testcase PDF or a fixture name")
    if not (evidence or use_sample_evidence):
        raise HTTPException(422, "provide an evidence PDF or use_sample_evidence=true")
    if as_of_date:
        try:
            date.fromisoformat(as_of_date)
        except ValueError:
            raise HTTPException(422, "as_of_date must be YYYY-MM-DD")
    settings = _settings()
    if judge_model:
        settings.judge_model = judge_model
    if budget_usd is not None:
        settings.budget_usd = budget_usd

    run_id = new_run_id()
    inputs = _upload_dir(run_id)
    evidence_path = await _save(evidence, inputs, "evidence.pdf") if evidence else SAMPLE_EVIDENCE
    testcase_path = await _save(testcase, inputs, "testcase.pdf") if testcase else None
    if fixture and not os.path.exists(os.path.join(FIXTURES_DIR, f"{fixture}.json")):
        raise HTTPException(404, f"fixture '{fixture}' not found")

    with _LOCK:
        _RUNS[run_id] = RunResult(run_id=run_id, status="queued", context_mode=context_mode,
                                  as_of_date=as_of_date or date.today().isoformat(),
                                  judge_model=settings.judge_model)
    background.add_task(_execute, run_id, evidence_path=evidence_path,
                        testcase_path=testcase_path, fixture=fixture,
                        context_mode=context_mode, as_of_date=as_of_date, tester=tester,
                        settings=settings)
    return {"run_id": run_id, "status": "queued", "poll": f"/runs/{run_id}",
            "report": f"/runs/{run_id}/report"}


def _load_run(run_id):
    with _LOCK:
        result = _RUNS.get(run_id)
    if result is not None:
        return result
    path = os.path.join(_settings().out_dir, run_id, "result.json")
    if os.path.exists(path):                      # a run from an earlier process
        with open(path, encoding="utf-8") as handle:
            return RunResult.model_validate(json.load(handle))
    raise HTTPException(404, f"run '{run_id}' not found")


@app.get("/runs")
def list_runs():
    out_dir = _settings().out_dir
    on_disk = {os.path.basename(os.path.dirname(p))
               for p in glob.glob(os.path.join(out_dir, "*", "result.json"))}
    with _LOCK:
        live = dict(_RUNS)
    rows = []
    for run_id in sorted(on_disk | set(live), reverse=True):
        r = live.get(run_id)
        if r is None:
            try:
                r = _load_run(run_id)
            except HTTPException:
                continue
        rows.append({"run_id": run_id, "status": r.status, "context_mode": r.context_mode,
                     "judge_model": r.judge_model, "tag_accuracy": r.tag_accuracy,
                     "overall": r.overall.result if r.overall else None,
                     "total_usd": r.usage.total_usd if r.usage else None,
                     "langsmith_url": r.langsmith_url})
    return rows


@app.get("/runs/{run_id}")
def get_run(run_id: str):
    return JSONResponse(json.loads(_load_run(run_id).model_dump_json()))


@app.get("/runs/{run_id}/report", response_class=HTMLResponse)
def get_report(run_id: str):
    result = _load_run(run_id)
    path = os.path.join(_settings().out_dir, run_id, "report.html")
    if result.status in ("queued", "running") or not os.path.exists(path):
        return HTMLResponse(f"<p>run {run_id} is {result.status}; refresh shortly.</p>")
    with open(path, encoding="utf-8") as handle:
        return HTMLResponse(handle.read())


@app.post("/evals")
def run_evals(fixture: str = Form(default="bcp_rm_005"),
              context_mode: str = Form(default="retrieval"),
              judge_model: Optional[str] = Form(default=None),
              as_of_date: Optional[str] = Form(default=None),
              max_examples: Optional[int] = Form(default=None)):
    """Run the LangSmith experiment (blocking; ~1 min). Needs LANGSMITH_API_KEY."""
    from testcase_poc.evals.run_eval import run_experiment
    settings = _settings()
    if judge_model:
        settings.judge_model = judge_model
    try:
        return run_experiment(fixture=fixture, context_mode=context_mode, as_of_date=as_of_date,
                              settings=settings, max_examples=max_examples)
    except Exception as exc:
        raise HTTPException(500, f"{type(exc).__name__}: {exc}")
