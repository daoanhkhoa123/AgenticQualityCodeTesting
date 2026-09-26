import json
import re

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langgraph.runtime import Runtime

from agentic_code_testing.agents.planner_agent.extract_ac_agent.typed_schemas import ExtractACAgentState
from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentContext

@tool
def extract_by_delimiter(text: str) -> str:
    """Extract items from a bulleted list into a JSON array of strings.

    Splits text where each item is on its own line, prefixed with a
    bullet delimiter ("-", "*", or "•"), for example:

        - a
        - b

    returns '["a", "b"]'. Lines without a bullet prefix are ignored.
    Always returns a JSON string (even '[]') rather than a bare list, since
    some providers reject an empty-list tool result as invalid message content.
    """
    pattern = re.compile(r"^\s*[-*•]\s+(.*\S)\s*$", re.MULTILINE)
    return json.dumps(pattern.findall(text))


SYSTEM_PROMPT = """
You are an expert QA engineer analyzing a user story.

Your task:
1. Extract the acceptance criteria as a bulleted list (using "-" or "*"), one criterion per line.
2. IF the user story does NOT contain acceptance criteria (or says "<Not found>"), you MUST infer and generate plausible, high-quality acceptance criteria yourself based on the user story requirements.
3. Once you have the bulleted list of acceptance criteria (whether extracted or generated), pass that bulleted text to the `extract_by_delimiter` tool.

CRITICAL: You MUST always call the `extract_by_delimiter` tool with a bulleted list before completing your task.
"""

def create_extract_ac_agent(llm: BaseChatModel):
    return create_agent(model=llm, tools=[extract_by_delimiter], system_prompt=SYSTEM_PROMPT)


def extract_ac_node(state: ExtractACAgentState, runtime: Runtime[PlannerAgentContext]) -> dict:
    agent = create_extract_ac_agent(runtime.context.llm)

    messages = [HumanMessage(content=state.user_story.acceptance_criteria)]
    if state.human_feedback:
        messages.append(HumanMessage(content=(
            f"Your previous extraction was: {state.acs}\n"
            f"A human reviewer rejected it with this feedback: {state.human_feedback}\n"
            "Please re-extract the acceptance criteria, taking this feedback into account."
        )))

    result = agent.invoke({"messages": messages})

    for message in reversed(result["messages"]):
        if getattr(message, "name", None) != "extract_by_delimiter":
            continue
        return {"acs": json.loads(message.content)}

    return {"acs": []}
