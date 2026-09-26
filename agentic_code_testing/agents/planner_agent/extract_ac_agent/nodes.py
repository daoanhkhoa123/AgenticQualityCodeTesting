from agentic_code_testing.agents.user_story_agent.nodes.parsing_nodes import NOT_FOUND_TOKEN
from agentic_code_testing.agents.planner_agent.extract_ac_agent.typed_schemas import ExtractACAgentState, HumanReviewDecision
from typing import Literal

from langgraph.types import interrupt

ASK_HUMAN_FLAG = Literal["ask_human", "go_end"]
HUMAN_DECISION = Literal["accepted", "rejected"]

def remove_story_body(state:ExtractACAgentState) -> dict:
    return {"user_story": state.user_story.model_copy(update={"story_body": ""})}

def should_ask_human(state:ExtractACAgentState) -> ASK_HUMAN_FLAG:
    if state.user_story.acceptance_criteria == NOT_FOUND_TOKEN:
        return "ask_human"
    return "go_end"

def asking_human(state:ExtractACAgentState) -> dict:
    decision = interrupt(
        {"acs": state.acs, "question": "Accept these acceptance criteria?"},
        response_schema=HumanReviewDecision,
    )
    if isinstance(decision, HumanReviewDecision):
        decision = decision.model_dump()
    elif not isinstance(decision, dict):
        decision = {"accepted": bool(decision)}

    return {
        "human_accepted": bool(decision.get("accepted", False)),
        "human_feedback": decision.get("feedback"),
    }

def route_after_human(state:ExtractACAgentState) -> HUMAN_DECISION:
    return "accepted" if state.human_accepted else "rejected"