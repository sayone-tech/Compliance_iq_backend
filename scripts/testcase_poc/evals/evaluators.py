"""LangSmith evaluators. Each takes (inputs, outputs, reference_outputs) by name and
returns {"key", "score", "comment"}."""
import re

from langchain_core.messages import HumanMessage, SystemMessage

from testcase_poc import prompts

_WS = re.compile(r"\s+")


def _norm(text):
    return _WS.sub(" ", text or "").strip().lower()


def tag_exact_match(outputs, reference_outputs):
    predicted, expected = outputs.get("tag"), reference_outputs.get("tag")
    return {"key": "tag_exact_match", "score": float(predicted == expected),
            "comment": f"predicted {predicted}, expected {expected}"}


def make_narrative_faithfulness(llm):
    """LLM-judge: does the AI narrative carry the same conclusion and facts as the human one?"""
    def narrative_faithfulness(inputs, outputs, reference_outputs):
        graded = llm.invoke(
            [SystemMessage(prompts.FAITHFULNESS_SYSTEM),
             HumanMessage(prompts.FAITHFULNESS_USER.format(
                 instruction=inputs["step"]["instruction"],
                 expected=reference_outputs.get("narrative", ""),
                 predicted=outputs.get("narrative", "")))],
            config={"tags": ["eval", "narrative_faithfulness"]})
        return {"key": "narrative_faithfulness",
                "score": max(0.0, min(1.0, float(graded["score"]))),
                "comment": graded["reasoning"]}
    return narrative_faithfulness


_SPLIT = re.compile(r"\.\.\.|\u2026|\[\.\.\.\]|(?<=[a-z\)]):\s")
_MIN_WORDS = 5


def _grounded(quote, haystack):
    """A quote counts as grounded when every fragment of >= 5 words is found verbatim
    (whitespace-insensitive). Models stitch "Heading: body" and elide with "..."; the
    fragments on either side are still checkable, so split there."""
    fragments = [_norm(f) for f in _SPLIT.split(quote or "")]
    fragments = [f for f in fragments if len(f.split()) >= _MIN_WORDS]
    if not fragments:
        return _norm(quote) in haystack if _norm(quote) else False
    return all(f in haystack for f in fragments)


def make_citation_grounding(evidence_text):
    """Fraction of citation quotes found in the evidence (see _grounded). Zero citations
    is not a pass: it scores 0."""
    haystack = _norm(evidence_text)

    def citation_grounding(outputs):
        citations = outputs.get("citations") or []
        if not citations:
            return {"key": "citation_grounding", "score": 0.0, "comment": "no citations"}
        grounded = [c for c in citations if _grounded(c.get("quote"), haystack)]
        return {"key": "citation_grounding", "score": len(grounded) / len(citations),
                "comment": f"{len(grounded)}/{len(citations)} quotes found verbatim in evidence"}
    return citation_grounding


def elements_decomposed(outputs):
    """Did the judge decompose the step before deciding? (2+ elements checked)"""
    n = len(outputs.get("elements") or [])
    return {"key": "elements_decomposed", "score": float(n >= 2), "comment": f"{n} elements"}
