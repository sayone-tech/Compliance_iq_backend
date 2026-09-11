"""Pydantic models shared by the graph, the API and the evals.

Two halves of the test case are kept apart on purpose: `TestStep` is what the
AI judge sees, `GroundTruth` is the human tester's answer and is only ever read
by the scorer. Mixing them would leak the answer key into the prompt.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Tag = Literal["PASS", "FAIL"]
VerdictTag = Literal["PASS", "FAIL", "INCONCLUSIVE"]
ContextMode = Literal["retrieval", "full"]


class TestStep(BaseModel):
    """One numbered test procedure step, as the AI sees it."""
    id: str = Field(description="stable id, e.g. 'step_1'")
    number: int
    instruction: str = Field(description="the procedure text, e.g. 'Obtain the ... and confirm it is current and approved.'")
    sample_methodology: Optional[str] = Field(default=None, description="e.g. 'Tier 1: 100% Census'")


class GroundTruth(BaseModel):
    """The human tester's recorded result for one step. Hidden from the judge."""
    step_id: str
    tag: Tag
    action_taken: Optional[str] = Field(default=None, description="'Validated' or 'Not Validated'")
    narrative: str


class TestCase(BaseModel):
    control_id: str = Field(description="e.g. 'BCP-RM-005'")
    title: str = Field(description="e.g. 'Personnel & Facilities'")
    assessment_question: str
    evidence_ref: Optional[str] = Field(default=None, description="URL or filename of the evidence document")
    firm_name: Optional[str] = Field(default=None, description="the firm under test, if the document names one")
    steps: list[TestStep]
    ground_truth: list[GroundTruth] = Field(default_factory=list)
    overall_result_expected: Optional[str] = Field(default=None, description="e.g. 'Partially Effective'")


class Citation(BaseModel):
    chunk_id: str = Field(description="chunk id exactly as shown in the evidence excerpt header")
    pages: str = Field(description="page range of the cited chunk, e.g. '123-124'")
    quote: str = Field(description="short verbatim quote (<= 40 words) from that chunk supporting the finding")


class ElementCheck(BaseModel):
    """One required element of a step, checked on its own. Listed before the tag so the
    model decomposes the step before it decides."""
    element: str = Field(description="what the step requires, e.g. 'successor documented for the CCO'")
    status: Literal["met", "not_met", "not_addressed"]
    evidence_note: str = Field(description="the fact (with date/name/page) that meets it, or what is missing")


class StepVerdict(BaseModel):
    """What the judge returns for one step. Also the schema for structured output."""
    step_id: str
    elements: list[ElementCheck] = Field(default_factory=list, description="every element the step requires, each checked individually")
    tag: VerdictTag
    action_taken: Literal["Validated", "Not Validated", "Unable to Validate"]
    narrative: str = Field(description="tester-style narrative, 3-6 sentences, past tense, names the documents and facts checked")
    findings: list[str] = Field(default_factory=list, description="bullet-style facts that drove the verdict, including anything required but missing")
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class StepScore(BaseModel):
    step_id: str
    expected_tag: Tag
    predicted_tag: VerdictTag
    tag_match: bool
    narrative_faithfulness: Optional[float] = Field(default=None, description="0-1, LLM-judged overlap of facts/findings with the human narrative")
    faithfulness_reasoning: Optional[str] = None


class OverallResult(BaseModel):
    result: Literal["Effective", "Partially Effective", "Not Effective", "Needs Review"]
    passed: int
    failed: int
    inconclusive: int
    summary: str


class UsageSummary(BaseModel):
    total_usd: float
    calls: int
    budget_usd: float
    by_model: dict
    cached_tokens: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0


class RunResult(BaseModel):
    """API/disk shape of one run. Verdicts and scores stay plain dicts because the
    verdicts carry a `context` block (retrieval provenance) beyond StepVerdict."""
    model_config = {"validate_assignment": True}

    run_id: str
    status: Literal["queued", "running", "done", "error"]
    context_mode: ContextMode
    as_of_date: str
    judge_model: str
    testcase: Optional[TestCase] = None
    evidence_doc_id: Optional[str] = None
    evidence_pages: Optional[int] = None
    evidence_chunks: Optional[int] = None
    verdicts: list[dict] = Field(default_factory=list)
    overall: Optional[OverallResult] = None
    scores: list[dict] = Field(default_factory=list)
    tag_accuracy: Optional[float] = None
    overall_match: Optional[bool] = None
    usage: Optional[UsageSummary] = None
    langsmith_url: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
