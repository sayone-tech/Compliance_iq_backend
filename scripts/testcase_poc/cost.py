"""Token and USD accounting for every LLM/embedding call in a run.

Two sources, one ledger:
  * LangChain calls (ChatOpenAI) report usage through a callback handler --
    `UsageCallback` below -- which charges the reused `CostMeter`.
  * The embedding path goes through wsp_poc.OpenAIEmbedding, which charges the
    same meter directly.

So `meter.summary()` is the whole run, and `audit.jsonl` has one line per call.
LangSmith records the same usage per trace independently; the two should agree
on tokens, and on USD as long as its model price map matches PRICING.
"""
import sys
import threading

from langchain_core.callbacks import BaseCallbackHandler

from testcase_poc.config import PROMPT_VERSION
from wsp_poc.validate_wsp import PRICING, BudgetExceeded, CostMeter  # noqa: F401

# List prices in USD per 1M tokens as at 2026-09-11 -- re-verify before quoting.
# `cached` is the discounted rate OpenAI applies to prompt-cache hits.
PRICING.update({
    "gpt-4.1":       {"input": 2.00, "output": 8.00, "cached": 0.50},
    "gpt-4.1-mini":  {"input": 0.40, "output": 1.60, "cached": 0.10},
    "gpt-4o-mini":   {"input": 0.15, "output": 0.60, "cached": 0.075},
})


def price(model, in_tokens, out_tokens, cached_tokens=0):
    """Like CostMeter.price but honours the cached-input discount."""
    rates = PRICING.get(model)
    if rates is None:
        return 0.0
    cached_rate = rates.get("cached", rates["input"])
    uncached = max(0, in_tokens - cached_tokens)
    return (uncached * rates["input"] + cached_tokens * cached_rate
            + out_tokens * rates["output"]) / 1_000_000


class RunMeter(CostMeter):
    """CostMeter that is safe under LangGraph's parallel fan-out and knows about
    cached prompt tokens."""

    def __init__(self, budget_usd, audit_path=None):
        super().__init__(budget_usd, audit_path)
        self.lock = threading.Lock()
        self.cached_tokens = 0

    def charge(self, model, in_tokens, out_tokens=0, cached_tokens=0, **audit):
        with self.lock:
            cost = price(model, in_tokens, out_tokens, cached_tokens)
            if model not in PRICING:
                print(f"  ! no price known for {model}; counted as $0", file=sys.stderr)
            self.total += cost
            self.calls += 1
            self.cached_tokens += cached_tokens
            entry = self.by_model.setdefault(
                model, {"calls": 0, "in": 0, "out": 0, "cached": 0, "usd": 0.0})
            entry["calls"] += 1
            entry["in"] += in_tokens
            entry["out"] += out_tokens
            entry["cached"] += cached_tokens
            entry["usd"] += cost
            self.log(model=model, input_tokens=in_tokens, output_tokens=out_tokens,
                     cached_tokens=cached_tokens, usd=round(cost, 6),
                     running_usd=round(self.total, 6), **audit)
            if self.total > self.budget:
                raise BudgetExceeded(
                    f"budget of ${self.budget:.2f} exceeded (${self.total:.4f} spent)")
            return cost

    def log(self, **fields):
        fields.setdefault("prompt_version", PROMPT_VERSION)
        super().log(**fields)

    def summary(self):
        out = super().summary()
        out["cached_tokens"] = self.cached_tokens
        out["total_input_tokens"] = sum(m["in"] for m in self.by_model.values())
        out["total_output_tokens"] = sum(m["out"] for m in self.by_model.values())
        return out


class UsageCallback(BaseCallbackHandler):
    """Forwards ChatOpenAI usage into the RunMeter. Attach via
    `llm.invoke(..., config={"callbacks": [cb]})` or the graph config."""

    def __init__(self, meter, stage="llm"):
        self.meter = meter
        self.stage = stage

    def on_llm_end(self, response, **kwargs):
        for generations in response.generations:
            for gen in generations:
                message = getattr(gen, "message", None)
                usage = getattr(message, "usage_metadata", None) if message is not None else None
                if not usage:
                    continue
                model = ((message.response_metadata or {}).get("model_name")
                         or (response.llm_output or {}).get("model_name") or "unknown")
                model = _normalise_model(model)
                details = usage.get("input_token_details") or {}
                self.meter.charge(
                    model, usage.get("input_tokens", 0), usage.get("output_tokens", 0),
                    cached_tokens=details.get("cache_read", 0),
                    stage=kwargs.get("tags") and ",".join(kwargs["tags"]) or self.stage)


def _normalise_model(name):
    """OpenAI reports dated snapshots ('gpt-4.1-mini-2025-04-14'); price by family."""
    for known in sorted(PRICING, key=len, reverse=True):
        if name == known or name.startswith(known + "-"):
            return known
    return name
