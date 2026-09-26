from typing import Optional, Literal

from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel

ScenarioCategory = Literal["happy_path", "edge_case", "negative_case"]
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


class Plan(BaseModel):
    story_id: int
    scenarios: list[Scenario] = Field(default_factory=list)


class PlannerAgentContext(BaseModel):
    llm: BaseChatModel
