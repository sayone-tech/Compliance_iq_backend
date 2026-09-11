"""Runtime settings. Everything comes from the environment (or a .env file next
to this package, or one at the repository root) so the same code runs natively,
under compose, and inside `langsmith.evaluate`.

The API key is never a CLI argument -- same rule as the WSP POC.
"""
import os
import sys
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(SCRIPTS_DIR)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)             # `wsp_poc` and `testcase_poc` as packages

from wsp_poc.validate_wsp import load_dotenv     # noqa: E402

DOTENV_PATHS = [os.path.join(HERE, ".env"),
                os.path.join(SCRIPTS_DIR, "wsp_poc", ".env"),
                os.path.join(REPO_ROOT, ".env")]

FIXTURES_DIR = os.path.join(HERE, "fixtures")
DEFAULT_OUT_DIR = os.path.join(REPO_ROOT, "out", "testcase")
SAMPLE_TESTCASE = os.path.join(REPO_ROOT, "docs", "SampleTest", "TestCase.pdf")
SAMPLE_EVIDENCE = os.path.join(REPO_ROOT, "docs", "SampleTest", "Evidence.pdf")

PROMPT_VERSION = "testcase-poc-2026-09-11.4"


def _env(name, default):
    value = os.environ.get(name)
    return value if value not in (None, "") else default


@dataclass
class Settings:
    openai_api_key_env: str = "OPENAI_API_KEY"
    judge_model: str = field(default_factory=lambda: _env("TC_JUDGE_MODEL", "gpt-4.1-mini"))
    parse_model: str = field(default_factory=lambda: _env("TC_PARSE_MODEL", "gpt-4.1-mini"))
    summary_model: str = field(default_factory=lambda: _env("TC_SUMMARY_MODEL", "gpt-4.1-mini"))
    eval_judge_model: str = field(default_factory=lambda: _env("TC_EVAL_JUDGE_MODEL", "gpt-4.1"))
    embedding_model: str = field(default_factory=lambda: _env("TC_EMBEDDING_MODEL", "text-embedding-3-small"))
    qdrant_url: str = field(default_factory=lambda: _env("QDRANT_URL", "http://127.0.0.1:6333"))
    # Same prefix as the WSP POC so the two share one embedding memo cache; the
    # chunk collection is filtered by doc name, so evidence docs never collide.
    collection_prefix: str = field(default_factory=lambda: _env("QDRANT_COLLECTION_PREFIX", "wsp"))
    top_k: int = field(default_factory=lambda: int(_env("TC_TOP_K", "10")))
    neighbour_radius: int = field(default_factory=lambda: int(_env("TC_NEIGHBOUR_RADIUS", "1")))
    query_expansion: bool = field(default_factory=lambda: _env("TC_QUERY_EXPANSION", "true").lower() == "true")
    max_context_tokens: int = field(default_factory=lambda: int(_env("TC_MAX_CONTEXT_TOKENS", "16000")))
    budget_usd: float = field(default_factory=lambda: float(_env("TC_BUDGET_USD", "1.00")))
    out_dir: str = field(default_factory=lambda: _env("TC_OUT_DIR", DEFAULT_OUT_DIR))
    langsmith_project: str = field(default_factory=lambda: _env("LANGSMITH_PROJECT", "controliq-testcase-poc"))

    @property
    def tracing_enabled(self):
        return _env("LANGSMITH_TRACING", _env("LANGCHAIN_TRACING_V2", "false")).lower() == "true"


def load_settings():
    load_dotenv(DOTENV_PATHS)
    settings = Settings()
    # LangSmith reads LANGSMITH_PROJECT itself; make sure the default is visible to it.
    os.environ.setdefault("LANGSMITH_PROJECT", settings.langsmith_project)
    return settings


def require_openai_key(settings):
    key = os.environ.get(settings.openai_api_key_env)
    if not key:
        raise RuntimeError(
            f"no API key: {settings.openai_api_key_env} is not set. Export it or put it in one of: "
            + ", ".join(DOTENV_PATHS))
    return key
