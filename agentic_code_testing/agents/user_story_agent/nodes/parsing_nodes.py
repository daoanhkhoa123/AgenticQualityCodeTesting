from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState, StoryAgentContext
from agentic_code_testing.agents.user_story_agent.tools.read_file import read_file
from agentic_code_testing.agents.user_story_agent.tools.parse_text_body import parse_re_story_file

PARSING_FIELD_PROMPT = """Extract from body, the field {field}
---
{body}
---
only return value of field, if not found, return explicitly
<Not found>"""

prompt_template = PromptTemplate.from_template(PARSING_FIELD_PROMPT)


def read_file_node(state: StoryAgentState) -> dict:
    return {"story_body": read_file(state.file_path)}


def parse_regex_prefill_node(state: StoryAgentState) -> dict:
    return parse_re_story_file(state.story_body)


def parsing_single_field_node(state: StoryAgentState, runtime: Runtime[StoryAgentContext]) -> dict:
    llm = runtime.context.llm

    chain = prompt_template | llm
    response = chain.invoke({"field": state.parsing_field_name, "body": state.story_body})

    content = response.content
    if not isinstance(content, str):
        raise TypeError(f"Expected string content from LLM, got {type(content)}")

    return {
        state.parsing_field_name: content.strip(),
        "parsing_field_name": None,
    }
