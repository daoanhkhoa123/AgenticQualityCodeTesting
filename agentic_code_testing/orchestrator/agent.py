import logging

from agentic_code_testing.logging.pydantic_logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def run_pipeline(file_path: str, story_id: int, output_dir: str, root_dir: str):
    """Stub -- no workflow logic yet.

    Intended sequence once implemented:
    1. user_story_agent.client.ask_user_story_agent(file_path, story_id) -> StoryAgentState
    2. planner_agent.client.ask_planner_agent(user_story, output_dir, root_dir) -> list[Scenario]
    3. codetest_writer_agent.client.ask_codetest_writer_agent(scenarios, output_dir, root_dir)
       -> list[TestWriteResult]

    planner_agent and codetest_writer_agent each already resolve their own
    request_code_context interrupts via code_reader_agent.client.ask_code_reader
    (see their agent_executor.py) -- the orchestrator doesn't need to answer
    those itself, only call the three agents above in order.
    """
    raise NotImplementedError("orchestrator workflow logic not implemented yet")
