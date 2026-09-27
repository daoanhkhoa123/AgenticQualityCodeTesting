from pydantic import BaseModel

from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import TestWriteResult
from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario
from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState


class PipelineResult(BaseModel):
    story_id: int
    user_story: StoryAgentState
    scenarios: list[Scenario]
    test_results: list[TestWriteResult]
