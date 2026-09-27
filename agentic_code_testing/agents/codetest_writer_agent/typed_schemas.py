from typing import Optional, Literal

from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel

from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario

TestOutcomeStatus = Literal["passed", "flagged_source_bug", "unresolved", "blocked"]


class TestRunResult(BaseModel):
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


class DraftedTest(BaseModel):
    code: Optional[str] = Field(
        default=None, description="Complete pytest test file source, including imports. Null if asking a question instead."
    )
    rationale: Optional[str] = None
    code_context_question: Optional[str] = Field(
        default=None,
        description=(
            "If the code context given is missing or insufficient to draft a test "
            "grounded in the real implementation, a specific question about the "
            "codebase to ask instead of guessing. Otherwise null."
        ),
    )


class FailureClassification(BaseModel):
    is_test_code_bug: bool
    reasoning: str
    suggested_fix: Optional[str] = Field(
        default=None,
        description="Concise fix instruction if is_test_code_bug is true; null if the bug is in the source under test.",
    )


class CodeTestWriterState(BaseModel):
    scenario_idx: int
    attempt: int = 0

    code_context: Optional[str] = None
    static_context: Optional[str] = None
    target_file: Optional[str] = None
    pending_code_context_question: Optional[str] = None

    drafted_code: Optional[str] = None
    run_result: Optional[TestRunResult] = None
    blocked_reasons: list[str] = Field(default_factory=list)
    classification: Optional[FailureClassification] = None
    attempts_exhausted: bool = False

    status: Optional[TestOutcomeStatus] = None
    notes: str = ""


class CodeTestWriterContext(BaseModel):
    llm: BaseChatModel
    scenarios: list[Scenario] = Field(default_factory=list)
    root_dir: str = Field(description="Directory of the codebase to read and run tests against")
    max_attempts: int = Field(default=3, description="Max draft/run/classify attempts per scenario")
    pytest_timeout_s: float = Field(default=60.0, description="Timeout for a single pytest subprocess run")
    scratch_dir_name: str = Field(
        default=".codetest_writer_scratch",
        description="Name of the git-ignored scratch subdirectory created under root_dir while running drafts",
    )


class TestWriteResult(BaseModel):
    scenario_id: str
    title: str
    status: TestOutcomeStatus
    attempts: int
    test_code: Optional[str] = None
    notes: str = ""
    classification: Optional[FailureClassification] = None
