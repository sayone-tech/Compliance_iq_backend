#!/usr/bin/env python3
"""Run one test case from the shell.

    python3 -m testcase_poc.cli --fixture bcp_rm_005 --evidence docs/SampleTest/Evidence.pdf
    python3 -m testcase_poc.cli --testcase docs/SampleTest/TestCase.pdf --evidence ... --context-mode full
    python3 -m testcase_poc.cli --fixture bcp_rm_005 --evidence ... --dry-run   # no API calls

Run from the repository root with PYTHONPATH=scripts (the Docker image sets it).
"""
import argparse
import json
import sys

from testcase_poc.config import SAMPLE_EVIDENCE, load_settings
from testcase_poc.runner import run_testcase


def main():
    parser = argparse.ArgumentParser(description="AI test-case execution POC (LangGraph)")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--testcase", help="TestCase PDF to parse with the LLM")
    source.add_argument("--fixture", help="fixture name under fixtures/ (e.g. bcp_rm_005) or a JSON path")
    parser.add_argument("--evidence", default=SAMPLE_EVIDENCE, help="evidence PDF")
    parser.add_argument("--context-mode", choices=["retrieval", "full"], default="retrieval")
    parser.add_argument("--as-of-date", help="date of testing, YYYY-MM-DD (default today)")
    parser.add_argument("--tester", default="CITT", help="name the narrative is written as")
    parser.add_argument("--judge-model", help="override TC_JUDGE_MODEL")
    parser.add_argument("--budget-usd", type=float, help="override TC_BUDGET_USD")
    parser.add_argument("--dry-run", action="store_true",
                        help="chunk, retrieve and estimate prompt sizes; no LLM calls, no key needed")
    parser.add_argument("--out", help="output root (default out/testcase/)")
    args = parser.parse_args()

    settings = load_settings()
    if args.judge_model:
        settings.judge_model = args.judge_model
    if args.budget_usd is not None:
        settings.budget_usd = args.budget_usd
    if args.dry_run:
        settings.qdrant_url = "none"

    result = run_testcase(args.evidence, testcase_path=args.testcase, fixture=args.fixture,
                          context_mode=args.context_mode, as_of_date=args.as_of_date,
                          tester=args.tester, settings=settings, dry_run=args.dry_run,
                          out_dir=args.out)
    print(json.dumps({
        "run_id": result.run_id, "status": result.status, "error": result.error,
        "overall": result.overall.model_dump() if result.overall else None,
        "tag_accuracy": result.tag_accuracy,
        "overall_match": result.overall_match,
        "tags": [(v["step_id"], v["tag"]) for v in result.verdicts],
        "usage": result.usage.model_dump() if result.usage else None,
        "langsmith_url": result.langsmith_url,
        "out": f"{settings.out_dir}/{result.run_id}/",
    }, indent=2))
    return 0 if result.status == "done" else 1


if __name__ == "__main__":
    sys.exit(main())
