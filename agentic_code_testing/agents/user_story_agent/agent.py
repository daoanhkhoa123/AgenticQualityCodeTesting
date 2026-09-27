import logging

from langchain_core.language_models.chat_models import BaseChatModel

from agentic_code_testing.agents.user_story_agent.subgraphs.parsing_graph import parsing_graph
from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentContext, StoryAgentState
from agentic_code_testing.logging.pydantic_logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def invoke_user_story_agent(llm: BaseChatModel, file_path: str, story_id: int) -> StoryAgentState:
    logger.info("Starting user story agent for story_id=%s, file_path=%s", story_id, file_path)

    state = StoryAgentState(
        story_id=story_id,
        file_path=file_path,
        story_body="",
        name=None,
        description=None,
        test_description=None,
        acceptance_criteria=None,
        techinal_description=None,
        parsing_field_name=None,
    )
    context = StoryAgentContext(llm=llm)

    result = parsing_graph.invoke(state, context=context)

    logger.info("Finished user story agent for story_id=%s", story_id)
    return StoryAgentState.model_validate(result)
