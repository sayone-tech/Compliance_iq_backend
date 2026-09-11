#!/usr/bin/env python3
"""Create or refresh the LangSmith dataset from a fixture: one example per step.

    python3 -m testcase_poc.evals.build_dataset --fixture bcp_rm_005

inputs            what the judge sees (step + test-case context + evidence ref)
outputs           the human tester's tag, action and narrative (the reference)
"""
import argparse
import os
import sys

from langsmith import Client

from testcase_poc.config import REPO_ROOT, load_settings
from testcase_poc.runner import load_fixture


def dataset_name(fixture):
    return f"controliq-testcase-{fixture.replace('_', '-')}"


def examples_for(tc, evidence_ref):
    truth = {g.step_id: g for g in tc.ground_truth}
    ctx = {"control_id": tc.control_id, "title": tc.title,
           "assessment_question": tc.assessment_question, "firm_name": tc.firm_name}
    for step in tc.steps:
        g = truth[step.id]
        yield {
            "inputs": {"step": step.model_dump(), "testcase_ctx": ctx, "evidence_ref": evidence_ref},
            "outputs": {"tag": g.tag, "action_taken": g.action_taken, "narrative": g.narrative},
            "metadata": {"control_id": tc.control_id, "step_id": step.id, "step_number": step.number},
        }


def build(fixture, evidence_ref=None, client=None):
    tc = load_fixture(fixture)
    evidence_ref = evidence_ref or tc.evidence_ref
    if not evidence_ref:
        raise SystemExit("fixture has no evidence_ref; pass --evidence")
    if not os.path.isabs(evidence_ref):
        evidence_ref = os.path.join(REPO_ROOT, evidence_ref)
    client = client or Client()
    name = dataset_name(fixture)
    existing = list(client.list_datasets(dataset_name=name))
    if existing:
        dataset = existing[0]
        # Replace the examples so a fixture edit is reflected; ids are per-step anyway.
        old = list(client.list_examples(dataset_id=dataset.id))
        if old:
            client.delete_examples(example_ids=[e.id for e in old])
    else:
        dataset = client.create_dataset(
            dataset_name=name,
            description=f"{tc.control_id} {tc.title}: {len(tc.steps)} test steps with the human "
                        f"tester's tag and narrative as reference outputs.")
    rows = list(examples_for(tc, evidence_ref))
    client.create_examples(dataset_id=dataset.id, examples=rows)
    print(f"dataset {name}: {len(rows)} examples ({'refreshed' if existing else 'created'})",
          file=sys.stderr)
    return dataset, rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="bcp_rm_005")
    parser.add_argument("--evidence", help="evidence PDF path (default: fixture.evidence_ref)")
    args = parser.parse_args()
    load_settings()
    if not os.environ.get("LANGSMITH_API_KEY"):
        raise SystemExit("LANGSMITH_API_KEY is not set")
    build(args.fixture, args.evidence)


if __name__ == "__main__":
    main()
