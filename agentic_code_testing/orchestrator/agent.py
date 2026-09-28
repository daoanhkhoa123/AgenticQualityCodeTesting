import logging
from pathlib import Path

from langsmith.run_helpers import get_current_run_tree, traceable

from agentic_code_testing.logging.pydantic_logger import setup_logging
from agentic_code_testing.orchestrator.clients.codetest_writer_client import ask_codetest_writer_agent_async
from agentic_code_testing.orchestrator.clients.planner_client import ask_planner_agent_async
from agentic_code_testing.orchestrator.clients.user_story_client import ask_user_story_agent_async
from agentic_code_testing.orchestrator.typed_schemas import PipelineResult
from agentic_code_testing.orchestrator.write_markdown.base import BasePipelineResultWriter
from agentic_code_testing.orchestrator.write_markdown.markdown_writer import MarkdownPipelineResultWriter
from agentic_code_testing.tracing.config import configure_tracing

setup_logging()
configure_tracing()
logger = logging.getLogger(__name__)

DEFAULT_PIPELINE_OUTPUT_DIR = "outputs/pipeline_outputs"


@traceable(name="pipeline_run")
async def run_pipeline(
    file_path: str,
    story_id: int,
    output_dir: str,
    root_dir: str,
    file_writer: BasePipelineResultWriter | None = None,
    pipeline_output_dir: str | Path = DEFAULT_PIPELINE_OUTPUT_DIR,
) -> PipelineResult:
    """Runs user_story_agent -> planner_agent -> codetest_writer_agent in sequence over A2A.

    An empty scenarios/test_results list is a legitimate outcome (e.g. no AC could be
    grounded in root_dir), not an error, so it is returned as-is. Any raised exception
    (unreachable file, unreachable downstream agent, timeout) propagates uncaught --
    the caller (agent_executor.py) lets it surface as a normal A2A error.

    Decorated with @traceable so this is the one root LangSmith run each pipeline
    execution's downstream A2A calls (user_story/planner/codetest_writer/code_reader,
    each in their own process) attach under -- see agentic_code_testing/tracing/.
    """
    logger.info("Starting pipeline for story_id=%s, file_path=%s", story_id, file_path)

    user_story = await ask_user_story_agent_async(file_path, story_id)
    scenarios = await ask_planner_agent_async(user_story, output_dir, root_dir, max_acs=2)
    test_results = await ask_codetest_writer_agent_async(scenarios, output_dir, root_dir, max_scenarios=2)

    result = PipelineResult(
        story_id=story_id,
        user_story=user_story,
        scenarios=scenarios,
        test_results=test_results,
    )

    written_path = (file_writer or MarkdownPipelineResultWriter()).write(result, pipeline_output_dir)
    logger.info("Wrote pipeline result for story_id=%s to %s", story_id, written_path)

    run_tree = get_current_run_tree()
    if run_tree is not None:
        logger.info("Trace for story_id=%s: %s", story_id, run_tree.get_url())

    logger.info("Finished pipeline for story_id=%s", story_id)
    return result
