Orchestrator:

Pipeline conductor, not a fifth agent — no LLM, no LangGraph, just three sequential A2A calls chained together (`agent.py:run_pipeline`):

- `user_story_agent` parses `file_path`/`story_id` into a `StoryAgentState`
- `planner_agent` turns that story into `list[Scenario]` (may return `[]` if an AC can't be grounded in `root_dir` — not an error, carried through as-is)
- `codetest_writer_agent` turns those scenarios into `list[TestWriteResult]`
- results are assembled into a `PipelineResult` and written to markdown

Code-context questions (`planner_agent`/`codetest_writer_agent` pausing mid-run to ask about the codebase) are answered one layer down, inside each leaf agent's own A2A wrapper via `code_reader_agent` — the orchestrator never sees them. Any raised exception (unreachable file, unreachable downstream agent, timeout) propagates uncaught.

Files:
- `typed_schemas.py` — `PipelineResult` (story_id, user_story, scenarios, test_results)
- `agent.py` — `run_pipeline`, the async happy-path chaining the three stages and writing the result
- `clients/_transport.py` — `send_and_get_text` (single request/response), `send_with_code_context` (resumes a task through `TASK_STATE_INPUT_REQUIRED` via `code_reader_agent`)
- `clients/user_story_client.py`, `clients/planner_client.py`, `clients/codetest_writer_client.py` — one `ask_*_async` per downstream agent, matching the table in `outputs/orchestator_plan.md` §3
- `clients/code_reader_client.py` — `ask_code_reader_async`, answers a paused task's code-context question
- `write_markdown/base.py`, `write_markdown/markdown_writer.py` — `BasePipelineResultWriter` / `MarkdownPipelineResultWriter`, renders a `PipelineResult` to `outputs/pipeline_outputs/story-{id}.md`
- `config.py` — host/port for each downstream agent + per-stage timeouts, backed by `.env`

Not yet implemented: an A2A server for the orchestrator itself (`agent_executor.py`/`__main__.py`) — see `outputs/orchestator_plan.md` for the design. `run_pipeline` is currently called directly, not served over A2A.
