#!/usr/bin/env python3
"""Run the LangSmith experiment: judge every step in the dataset, score against the
human tester, and report token cost.

    python3 -m testcase_poc.evals.run_eval --fixture bcp_rm_005 --context-mode retrieval
    python3 -m testcase_poc.evals.run_eval --judge-model gpt-4.1 --context-mode full

Each experiment is named "<mode>-<judge model>-..." so runs line up side by side in
the LangSmith UI (Datasets -> controliq-testcase-bcp-rm-005 -> Experiments).
"""
import argparse
import json
import os
import sys
from datetime import date, datetime, timezone
from typing import TypedDict

from langchain_core.runnables import RunnableLambda
from langsmith import Client, evaluate

from testcase_poc import evidence as ev
from testcase_poc.config import PROMPT_VERSION, REPO_ROOT, load_settings, require_openai_key
from testcase_poc.cost import RunMeter, UsageCallback
from testcase_poc.evals import evaluators
from testcase_poc.evals.build_dataset import build, dataset_name
from testcase_poc.graph import RunContext, judge_step, make_llm


class _Faithfulness(TypedDict):
    score: float
    reasoning: str


def run_experiment(fixture="bcp_rm_005", context_mode="retrieval", as_of_date=None,
                   settings=None, tester="CITT", max_examples=None, rebuild_dataset=True):
    settings = settings or load_settings()
    if not os.environ.get("LANGSMITH_API_KEY"):
        raise RuntimeError("LANGSMITH_API_KEY is not set -- evals need LangSmith")
    os.environ.setdefault("LANGSMITH_TRACING", "true")
    api_key = require_openai_key(settings)
    as_of_date = as_of_date or date.today().isoformat()
    client = Client()

    if rebuild_dataset:
        dataset, rows = build(fixture, client=client)
        evidence_path = rows[0]["inputs"]["evidence_ref"]
    else:
        dataset = client.read_dataset(dataset_name=dataset_name(fixture))
        evidence_path = next(client.list_examples(dataset_id=dataset.id)).inputs["evidence_ref"]
    if not os.path.isabs(evidence_path):
        evidence_path = os.path.join(REPO_ROOT, evidence_path)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    out_dir = os.path.join(settings.out_dir, "evals", f"{stamp}-{context_mode}-{settings.judge_model}")
    os.makedirs(out_dir, exist_ok=True)
    meter = RunMeter(settings.budget_usd * 3, os.path.join(out_dir, "audit.jsonl"))
    ctx = RunContext(settings=settings, meter=meter, api_key=api_key)
    index = ev.ingest(evidence_path, settings, meter, api_key)
    config = {"configurable": {"ctx": ctx}, "callbacks": [UsageCallback(meter)]}
    judge = RunnableLambda(judge_step).with_config(config)

    def target(inputs):
        step = inputs["step"]
        payload = {"step": step, "testcase": {**inputs["testcase_ctx"], "steps": [step]},
                   "evidence_doc_id": index.doc_id, "context_mode": context_mode,
                   "as_of_date": as_of_date, "tester": tester}
        verdict = judge.invoke(payload)["verdicts"][0]
        return {k: verdict.get(k) for k in
                ("tag", "action_taken", "narrative", "findings", "citations", "elements",
                 "confidence", "context")}

    grader = make_llm(ctx, settings.eval_judge_model).with_structured_output(_Faithfulness)
    grader = grader.with_config(config)
    evals = [evaluators.tag_exact_match,
             evaluators.make_narrative_faithfulness(grader),
             evaluators.make_citation_grounding(index.text),
             evaluators.elements_decomposed]

    data = dataset.name
    if max_examples:
        data = list(client.list_examples(dataset_id=dataset.id, limit=max_examples))
    results = evaluate(
        target, data=data, evaluators=evals, client=client,
        experiment_prefix=f"{context_mode}-{settings.judge_model}",
        description=f"{fixture} judged with {settings.judge_model}, {context_mode} context, as of {as_of_date}",
        metadata={"fixture": fixture, "context_mode": context_mode,
                  "judge_model": settings.judge_model, "eval_judge_model": settings.eval_judge_model,
                  "embedding_model": settings.embedding_model, "top_k": settings.top_k,
                  "query_expansion": settings.query_expansion, "as_of_date": as_of_date,
                  "prompt_version": PROMPT_VERSION},
        max_concurrency=4)

    rows, sums, counts = [], {}, {}
    for item in results:
        scores = {}
        for r in item["evaluation_results"]["results"]:
            scores[r.key] = r.score
            if r.score is not None:
                sums[r.key] = sums.get(r.key, 0.0) + float(r.score)
                counts[r.key] = counts.get(r.key, 0) + 1
        rows.append({"step_id": item["example"].metadata.get("step_id"),
                     "expected": item["example"].outputs.get("tag"),
                     "predicted": (item["run"].outputs or {}).get("tag"),
                     "scores": scores})
    rows.sort(key=lambda r: int((r["step_id"] or "step_0").split("_")[-1]))
    summary = {
        "experiment_name": results.experiment_name,
        "experiment_url": getattr(results, "url", None) or _experiment_url(client, results.experiment_name),
        "dataset": dataset.name, "context_mode": context_mode,
        "judge_model": settings.judge_model, "as_of_date": as_of_date,
        "mean_scores": {k: round(sums[k] / counts[k], 4) for k in sums},
        "rows": rows, "usage": meter.summary(), "out_dir": out_dir,
    }
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    return summary


def _experiment_url(client, name):
    try:
        project = client.read_project(project_name=name)
        return getattr(project, "url", None)
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="bcp_rm_005")
    parser.add_argument("--context-mode", choices=["retrieval", "full"], default="retrieval")
    parser.add_argument("--judge-model")
    parser.add_argument("--as-of-date")
    parser.add_argument("--max-examples", type=int)
    parser.add_argument("--no-rebuild", action="store_true", help="reuse the dataset as-is")
    args = parser.parse_args()
    settings = load_settings()
    if args.judge_model:
        settings.judge_model = args.judge_model
    summary = run_experiment(args.fixture, args.context_mode, args.as_of_date, settings,
                             max_examples=args.max_examples, rebuild_dataset=not args.no_rebuild)
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2))
    for r in summary["rows"]:
        print(f"  {r['step_id']}: expected {r['expected']} predicted {r['predicted']} {r['scores']}")


if __name__ == "__main__":
    sys.exit(main())
