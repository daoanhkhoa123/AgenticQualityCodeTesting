# Codetest Writer Agent

Consumes the `Scenario` list produced by `planner_agent` and, for each one,
drafts a pytest test against a target codebase, runs it, and self-corrects.

This package is a logic wrapper around the
[`write_one_scenario_agent`](write_one_scenario_agent/README.md) graph, which
does the actual per-scenario drafting/running/retrying. `agent.py` compiles
that graph once, loops it over the scenario list, and handles the
interrupt/resume plumbing for code-context questions; `agent_executor.py`
exposes that loop over A2A.

The graph never references `code_reader_agent` directly -- if a draft needs
more information about the target codebase, it asks for it by suspending
itself, and `agent.py` exposes two ways to drive it end-to-end:

- `invoke_codetest_writer_agent(...)` -- blocking; resolves each question
  in-process via a `code_context_resolver` callback (falling back to "No code
  context available." if none is given).
- `iter_codetest_writer_agent_steps(...)` -- a generator that `yield`s each
  `code_context_question` and resumes on `.send(answer)`, letting a caller pause
  and resume across a network boundary instead of resolving inline. `invoke_codetest_writer_agent`
  is now just a thin blocking wrapper around this generator.

This package's A2A wrapper (`agent_executor.py`) drives
`iter_codetest_writer_agent_steps` directly: when a question comes up it
surfaces the task as A2A input-required (`TaskUpdater.requires_input(...)`)
and keeps the in-flight generator keyed by `task_id`, resuming it with
`gen.send(answer)` once the next message for that task arrives with the
answer. It still doesn't call `code_reader_agent` itself -- answering the
question over a real A2A round trip (e.g. to `code_reader_agent`) is the
orchestrator's job, once `agentic_code_testing/orchestrator` implements it;
this executor only makes that hand-off possible.

Entry points (`agent.py`):

- `invoke_codetest_writer_agent(llm, scenarios, file_writer, output_dir, root_dir, max_attempts=3, code_context_resolver=None)`
  -- compiles the per-scenario subgraph with a checkpointer (needed to resume
  interrupts), loops scenarios, and for each one resolves any
  `code_context_question` interrupt by calling `code_context_resolver(question)`
  (falling back to "No code context available." if none is given), then writes
  results via a `BaseTestWriter` (see `write_report/`).
- `iter_codetest_writer_agent_steps(llm, scenarios, file_writer, output_dir, root_dir, max_attempts=3)`
  -- same driver loop, but as a generator: `yield`s each `code_context_question`
  instead of resolving it, resumes via `.send(answer)`, and returns the final
  `list[TestWriteResult]` as the generator's `StopIteration.value`. This is what
  `agent_executor.py` drives to answer questions across separate A2A requests.

See [`write_one_scenario_agent/README.md`](write_one_scenario_agent/README.md)
for what actually happens inside each scenario (the graph, its nodes, and the
v1 execution-isolation scope).
