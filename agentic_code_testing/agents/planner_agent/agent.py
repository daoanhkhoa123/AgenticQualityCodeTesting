import logging
import uuid

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from agentic_code_testing.agents.user_story_agent.typed_schemas import StoryAgentState
from agentic_code_testing.agents.planner_agent.extract_ac_agent.typed_schemas import ExtractACAgentState
from agentic_code_testing.agents.planner_agent.extract_ac_agent.graph import builder as extract_ac_builder
from agentic_code_testing.agents.planner_agent.plann_one_ac_agent.graph import planner_agent_once_ac
from agentic_code_testing.agents.planner_agent.typed_schemas import PlannerAgentState, PlannerAgentContext
from agentic_code_testing.agents.planner_agent.write_markdown.base import BaseScenarioWriter
from agentic_code_testing.logging.pydantic_logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def invoke_planning_agent(
    llm,
    user_story: StoryAgentState,
    file_writer: BaseScenarioWriter,
    output_dir,
    root_dir: str,
    max_acs: int | None = None,
):
    logger.info("Starting planning agent for story_id=%s", user_story.story_id)

    state = ExtractACAgentState()
    context = PlannerAgentContext(llm=llm, user_story=user_story, root_dir=root_dir)

    extract_ac_graph = extract_ac_builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    logger.info("Extracting acceptance criteria for story_id=%s", user_story.story_id)
    result = extract_ac_graph.invoke(state, config=config, context=context)
    if "__interrupt__" in result:
        logger.info(
            "Acceptance criteria not found for story_id=%s; auto-accepting %d AI-generated criteria",
            user_story.story_id,
            len(result["acs"]),
        )
        # No human is available to review AI-generated criteria here, so auto-accept them.
        result = extract_ac_graph.invoke(Command(resume={"accepted": True}), config=config, context=context)

    acs = result["acs"]
    logger.info("Extracted %d acceptance criteria for story_id=%s", len(acs), user_story.story_id)

    if max_acs is not None:
        acs = acs[:max_acs]
        logger.info("Capping to %d acceptance criteria for story_id=%s", len(acs), user_story.story_id)

    context = context.model_copy(update={"acs": acs})

    all_scenarios = []
    for ac_idx in range(len(acs)):
        logger.info("Generating scenarios for AC %d/%d", ac_idx + 1, len(acs))
        state = PlannerAgentState(ac_idx=ac_idx, is_category_covered=False, coverage_reasoning="")
        result = planner_agent_once_ac.invoke(state, context=context)
        logger.info("Generated %d scenarios for AC %d/%d", len(result["scenarios"]), ac_idx + 1, len(acs))
        all_scenarios.extend(result["scenarios"])

    logger.info("Writing %d scenarios to markdown at %s", len(all_scenarios), output_dir)
    file_writer.write(all_scenarios, output_dir)

    logger.info("Finished planning agent for story_id=%s", user_story.story_id)
    return all_scenarios