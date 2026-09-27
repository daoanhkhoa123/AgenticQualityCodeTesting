from typing import Optional, Literal

from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from agentic_code_testing.agents.code_reader_agent.client import DEFAULT_BASE_URL
from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState

ScenarioCategory = Literal["happy path", "edge case", "negative case"]
Priority = Literal["P0", "P1", "P2"]
TestType = Literal["unit", "integration", "e2e"]


class Scenario(BaseModel):
    scenario_id: str
    story_id: int
    ac_id: Optional[str] = None

    category: ScenarioCategory
    priority: Priority
    test_type: TestType

    title: str
    description: str
    preconditions: Optional[str] = None
    steps: list[str] = Field(default_factory=list)
    expected_result: str


class ScenarioGenResult(BaseModel):
    scenario: Optional[Scenario]
    is_category_covered: bool
    coverage_reasoning: str


class PlannerAgentState(BaseModel):
    scenarios: list[Scenario] = Field(default_factory=list)
    current_category: Optional[ScenarioCategory] = None

    is_category_covered: bool
    coverage_reasoning: str

    ac_idx: int = -1
    senarios_idx: int = -1

    code_context: Optional[str] = None


class PlannerAgentContext(BaseModel):
    llm: BaseChatModel
    user_story: StoryAgentState = Field(description="Current acceptance criteria solving")
    acs: list[str] = Field(default_factory=list, description="List of acceptance criteria")
    root_dir: str = Field(description="Directory of the codebase to read for code context")
    code_reader_base_url: str = Field(
        default=DEFAULT_BASE_URL, description="Base URL of the code_reader_agent A2A server"
    )