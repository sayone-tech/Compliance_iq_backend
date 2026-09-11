"""The LangGraph pipeline.

    parse_testcase -> ingest_evidence -> (Send per step) judge_step -> aggregate -> score

Per-run dependencies (settings, cost meter, API key) travel in
`config["configurable"]["ctx"]`; the LangChain callback that meters token usage
travels in `config["callbacks"]` and is inherited by every LLM call underneath.
"""
import operator
import re
import sys
import threading
import time
from datetime import date
from dataclasses import dataclass
from typing import Annotated, Optional, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from testcase_poc import evidence as ev
from testcase_poc import prompts
from testcase_poc.config import PROMPT_VERSION, Settings
from testcase_poc.dates import date_facts, months_before
from testcase_poc.schemas import OverallResult, StepScore, StepVerdict, TestCase
from wsp_poc.extract_wsp import build_document


_PRIME = {}
_PRIME_GUARD = threading.Lock()
_CACHE_WARM_SECONDS = 240


class _NoLock:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _prime_lock(doc_id):
    """First caller per document gets a real lock (and primes the prompt cache);
    everyone after it gets a no-op, but only once the first call has released."""
    with _PRIME_GUARD:
        entry = _PRIME.get(doc_id)
        if entry is None:
            entry = _PRIME[doc_id] = {"lock": threading.Lock(), "primed_at": 0.0}

    def warm():                                 # OpenAI's cache lives ~5-10 minutes
        return time.time() - entry["primed_at"] < _CACHE_WARM_SECONDS

    if warm():
        return _NoLock()
    entry["lock"].acquire()
    if warm():                                  # someone finished while we waited
        entry["lock"].release()
        return _NoLock()

    class _Release:
        def __enter__(self_inner):
            return self_inner

        def __exit__(self_inner, *exc):
            entry["primed_at"] = time.time()
            entry["lock"].release()
            return False
    return _Release()


# Steps whose wording asks about currency get the date facts; the rest are told
# explicitly not to invent a currency element (mini models otherwise fail every
# step on the plan's approval date once they have seen it).
CURRENCY_RE = re.compile(r"\b(current|currency|approved|approval|up[- ]to[- ]date|annual|reviewed|"
                         r"recertif|re-certif|expired|effective date)\w*", re.IGNORECASE)
# "...contact list/roster is current" is about the entries, not the plan's approval date.
ROSTER_RE = re.compile(r"\b(roster|list|listing|directory|register|inventory|contacts?)\b", re.IGNORECASE)


@dataclass
class RunContext:
    settings: Settings
    meter: object
    api_key: str
    dry_run: bool = False


class RunState(TypedDict, total=False):
    run_id: str
    as_of_date: str
    context_mode: str
    tester: str
    testcase_path: Optional[str]
    testcase: Optional[dict]
    evidence_path: str
    evidence_doc_id: str
    evidence_pages: int
    evidence_chunks: int
    verdicts: Annotated[list, operator.add]
    overall: dict
    scores: list
    tag_accuracy: Optional[float]
    overall_match: Optional[bool]


class StepPayload(TypedDict):
    """What each Send carries into judge_step."""
    step: dict
    testcase: dict
    evidence_doc_id: str
    context_mode: str
    as_of_date: str
    tester: str


def _ctx(config) -> RunContext:
    return config["configurable"]["ctx"]


def make_llm(ctx, model, temperature=0.0):
    return ChatOpenAI(model=model, temperature=temperature, api_key=ctx.api_key,
                      max_retries=4, timeout=120)


# --------------------------------------------------------------------------
# nodes


def parse_testcase(state: RunState, config):
    if state.get("testcase"):
        return {}
    ctx = _ctx(config)
    text, _ = build_document(state["testcase_path"])
    if ctx.dry_run:
        raise RuntimeError("--dry-run needs a fixture test case (parsing a PDF costs one LLM call)")
    llm = make_llm(ctx, ctx.settings.parse_model).with_structured_output(TestCase)
    parsed = llm.invoke([SystemMessage(prompts.PARSE_SYSTEM), HumanMessage(text)],
                        config={"tags": ["parse_testcase"]})
    print(f"parsed {parsed.control_id}: {len(parsed.steps)} steps, "
          f"{len(parsed.ground_truth)} ground-truth entries", file=sys.stderr)
    return {"testcase": parsed.model_dump()}


def ingest_evidence(state: RunState, config):
    ctx = _ctx(config)
    index = ev.ingest(state["evidence_path"], ctx.settings, ctx.meter, ctx.api_key,
                      dry_run=ctx.dry_run)
    return {"evidence_doc_id": index.doc_id, "evidence_pages": index.pages,
            "evidence_chunks": len(index.chunks)}


def fan_out(state: RunState):
    tc = state["testcase"]
    return [Send("judge_step", StepPayload(
                step=step, testcase=tc, evidence_doc_id=state["evidence_doc_id"],
                context_mode=state["context_mode"], as_of_date=state["as_of_date"],
                tester=state["tester"]))
            for step in tc["steps"]]


def currency_cutoff(as_of_date, months=12):
    """The date a document must be dated on or after to count as current."""
    return months_before(date.fromisoformat(as_of_date), months).isoformat()


class _Queries(TypedDict):
    queries: list[str]


def expand_queries(ctx, step, tc):
    """3-5 element-level search queries in manual vocabulary; one cheap LLM call."""
    llm = make_llm(ctx, ctx.settings.parse_model).with_structured_output(_Queries)
    out = llm.invoke([SystemMessage(prompts.QUERY_SYSTEM),
                      HumanMessage(prompts.QUERY_USER.format(
                          control_id=tc["control_id"], title=tc["title"],
                          assessment_question=tc["assessment_question"],
                          instruction=step["instruction"]))],
                     config={"tags": ["expand_queries", step["id"]]})
    return [q for q in out["queries"] if q.strip()][:5]


def build_step_context(payload, settings, index, ctx=None, dry_run=False):
    """Pick the evidence a step sees. Returns (scored_chunks, mode_label, ranked)."""
    step, tc = payload["step"], payload["testcase"]
    if payload["context_mode"] == "full":
        return ev.full_context(index), "full document", []
    queries = [step["instruction"],
               f"{tc['title']}: {step['instruction']} {tc['assessment_question']}"]
    if settings.query_expansion and not dry_run:
        queries += expand_queries(ctx, step, tc)
    retrieve = ev.lexical_retrieve if dry_run else ev.retrieve
    chunks, ranked = retrieve(index, queries, settings.top_k, settings.neighbour_radius,
                              settings.max_context_tokens)
    return chunks, f"top-{settings.top_k} retrieval with neighbours", ranked


def judge_step(payload: StepPayload, config):
    ctx = _ctx(config)
    settings = ctx.settings
    step, tc = payload["step"], payload["testcase"]
    index = ev.get_index(payload["evidence_doc_id"])
    scored, mode_label, ranked = build_step_context(payload, settings, index, ctx, ctx.dry_run)
    allowed = {c.chunk_id for c, _ in scored}

    system = prompts.JUDGE_SYSTEM.format(
        tester=payload["tester"], control_id=tc["control_id"], title=tc["title"],
        assessment_question=tc["assessment_question"],
        firm_name=tc.get("firm_name") or "(not named)", as_of_date=payload["as_of_date"],
        currency_cutoff=currency_cutoff(payload["as_of_date"]))
    excerpts = ev.format_excerpts(scored)
    if CURRENCY_RE.search(step["instruction"]):
        facts = date_facts(excerpts, payload["as_of_date"]) or "(no dates found)"
        block = prompts.CURRENCY_ROSTER if ROSTER_RE.search(step["instruction"]) else prompts.CURRENCY_IN_SCOPE
        currency_block = block.format(date_facts=facts)
    else:
        currency_block = prompts.CURRENCY_OUT_OF_SCOPE
    user = prompts.JUDGE_USER.format(
        number=step["number"], instruction=step["instruction"], mode=mode_label,
        sample_methodology=step.get("sample_methodology") or "(none stated)",
        currency_block=currency_block, excerpts=excerpts)

    if ctx.dry_run:
        tokens = ev.estimate_tokens(system + user)
        ctx.meter.log(stage="judge_step_dry_run", step_id=step["id"],
                      context_chunks=len(scored), estimated_input_tokens=tokens)
        verdict = StepVerdict(step_id=step["id"], tag="INCONCLUSIVE",
                              action_taken="Unable to Validate",
                              narrative=f"dry run: {tokens:,} prompt tokens, {len(scored)} chunks",
                              confidence=0.0)
        return {"verdicts": [verdict.model_dump()]}

    llm = make_llm(ctx, settings.judge_model).with_structured_output(StepVerdict)
    messages = [SystemMessage(system), HumanMessage(user)]
    if payload["context_mode"] == "full":
        # Prompt caching only pays off if one call with the shared prefix has FINISHED
        # before the others start. The first step through takes the lock and calls
        # alone; the rest wait on it, then run in parallel against a warm cache.
        with _prime_lock(payload["evidence_doc_id"]):
            verdict = llm.invoke(messages, config={"tags": ["judge_step", step["id"]]})
    else:
        verdict = llm.invoke(messages, config={"tags": ["judge_step", step["id"]]})
    verdict.step_id = step["id"]
    verdict.confidence = max(0.0, min(1.0, verdict.confidence))
    # Guardrail: a citation to a chunk the model was never shown is a hallucination.
    # Models shorten "doc:chunk_0149" to "doc:0149" or "chunk_0149"; resolve by the
    # numeric suffix before treating a citation as hallucinated.
    by_suffix = {cid.rsplit("_", 1)[-1]: cid for cid in allowed}
    kept, dropped = [], []
    for cit in verdict.citations:
        if cit.chunk_id not in allowed:
            resolved = by_suffix.get(re.sub(r"\D", "", cit.chunk_id.rsplit(":", 1)[-1]).lstrip("0").zfill(4))
            if resolved:
                cit.chunk_id = resolved
        (kept if cit.chunk_id in allowed else dropped).append(cit)
    if dropped:
        print(f"  ! {step['id']}: dropped {len(dropped)} citation(s) to unseen chunks: "
              f"{[c.chunk_id for c in dropped]}", file=sys.stderr)
    verdict.citations = kept
    out = verdict.model_dump()
    out["context"] = {
        "mode": payload["context_mode"], "chunks": len(scored),
        "tokens": ev.context_tokens(scored),
        "retrieved": [{"chunk_id": c.chunk_id, "score": round(s, 4),
                       "pages": f"{c.page_start}-{c.page_end}",
                       "heading": " > ".join(c.heading_path) or "(untitled)"}
                      for c, s in ranked],
        "dropped_citations": [c.model_dump() for c in dropped],
    }
    return {"verdicts": [out]}


def aggregate(state: RunState, config):
    ctx = _ctx(config)
    verdicts = sorted(state["verdicts"], key=lambda v: int(v["step_id"].split("_")[-1]))
    tags = [v["tag"] for v in verdicts]
    passed, failed = tags.count("PASS"), tags.count("FAIL")
    inconclusive = tags.count("INCONCLUSIVE")
    if inconclusive:
        result = "Needs Review"
    elif failed == 0:
        result = "Effective"
    elif passed == 0:
        result = "Not Effective"
    else:
        result = "Partially Effective"

    if ctx.dry_run:
        summary = "dry run"
    else:
        lines = [f"Control {state['testcase']['control_id']} -- {state['testcase']['title']}",
                 f"Rule-based overall result: {result} ({passed} of {len(tags)} steps passed, "
                 f"{failed} failed, {inconclusive} inconclusive)", ""]
        for v in verdicts:
            step = next(s for s in state["testcase"]["steps"] if s["id"] == v["step_id"])
            lines.append(f"Step {step['number']} [{v['tag']}]: {step['instruction']}")
            for finding in v.get("findings") or []:
                lines.append(f"  - {finding}")
        llm = make_llm(ctx, ctx.settings.summary_model)
        summary = llm.invoke([SystemMessage(prompts.SUMMARY_SYSTEM), HumanMessage("\n".join(lines))],
                             config={"tags": ["aggregate"]}).content.strip()
    overall = OverallResult(result=result, passed=passed, failed=failed,
                            inconclusive=inconclusive, summary=summary)
    return {"overall": overall.model_dump()}


class _Faithfulness(TypedDict):
    score: float
    reasoning: str


def score(state: RunState, config):
    ctx = _ctx(config)
    tc = state["testcase"]
    truth = {g["step_id"]: g for g in tc.get("ground_truth") or []}
    if not truth:
        return {"scores": [], "tag_accuracy": None, "overall_match": None}
    verdicts = {v["step_id"]: v for v in state["verdicts"]}
    steps = {s["id"]: s for s in tc["steps"]}
    llm = None
    if not ctx.dry_run:
        llm = make_llm(ctx, ctx.settings.eval_judge_model).with_structured_output(_Faithfulness)
    scores = []
    for step_id, g in truth.items():
        v = verdicts.get(step_id)
        if v is None:
            continue
        entry = StepScore(step_id=step_id, expected_tag=g["tag"], predicted_tag=v["tag"],
                          tag_match=(g["tag"] == v["tag"]))
        if llm is not None:
            graded = llm.invoke(
                [SystemMessage(prompts.FAITHFULNESS_SYSTEM),
                 HumanMessage(prompts.FAITHFULNESS_USER.format(
                     instruction=steps[step_id]["instruction"], expected=g["narrative"],
                     predicted=v["narrative"]))],
                config={"tags": ["score", step_id]})
            entry.narrative_faithfulness = max(0.0, min(1.0, float(graded["score"])))
            entry.faithfulness_reasoning = graded["reasoning"]
        scores.append(entry.model_dump())
    accuracy = (sum(1 for s in scores if s["tag_match"]) / len(scores)) if scores else None
    expected_overall = (tc.get("overall_result_expected") or "").strip().lower() or None
    overall_match = None
    if expected_overall and state.get("overall"):
        overall_match = state["overall"]["result"].lower() == expected_overall
    return {"scores": scores, "tag_accuracy": accuracy, "overall_match": overall_match}


# --------------------------------------------------------------------------
# graph


def build_graph():
    g = StateGraph(RunState)
    g.add_node("parse_testcase", parse_testcase)
    g.add_node("ingest_evidence", ingest_evidence)
    g.add_node("judge_step", judge_step)
    g.add_node("aggregate", aggregate)
    g.add_node("score", score)
    g.add_edge(START, "parse_testcase")
    g.add_edge("parse_testcase", "ingest_evidence")
    g.add_conditional_edges("ingest_evidence", fan_out, ["judge_step"])
    g.add_edge("judge_step", "aggregate")
    g.add_edge("aggregate", "score")
    g.add_edge("score", END)
    return g.compile()


graph = build_graph()
__all__ = ["graph", "build_graph", "RunContext", "RunState", "PROMPT_VERSION"]
