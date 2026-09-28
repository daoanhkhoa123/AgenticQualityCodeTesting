# Agentic Code Testing

Turns a user story into acceptance-criteria test plans and pytest tests for a
target codebase. Input is a user story markdown file and the root path of the
codebase under test; output is the generated test plans and a code test
report.

## Agents

[`user_story_agent`](agentic_code_testing/agents/user_story_agent/README.md)

![user_story_agent](docs/parsing_graph.png)

[`planner_agent`](agentic_code_testing/agents/planner_agent/README.md)

![planner_agent](docs/planner_agent_once_ac.png)

[`codetest_writer_agent`](agentic_code_testing/agents/codetest_writer_agent/README.md)

![codetest_writer_agent](docs/codetest_writer_once_scenario.png)

[`code_reader_agent`](agentic_code_testing/agents/code_reader_agent/README.md)

![code_reader_agent](docs/code_reader_agent.png)

## Workflow

    user_story_agent -> planner_agent [interruptable to code_reader_agent] -> codetest_writer_agent [interruptable to code_reader_agent]

A thin orchestrator (`agentic_code_testing/orchestrator`) chains the three
stages over A2A. `planner_agent` and `codetest_writer_agent` each pause
mid-run to ask `code_reader_agent` about the target codebase before
continuing -- the orchestrator never sees those questions, they're resolved
one layer down.

## Running it

- `scripts\run_all_agents.cmd` -- starts all four agents as A2A servers, one per window
- `scripts\run_pipeline.cmd` -- runs the full pipeline end to end against a story file

## Example run

The pipeline was tested end to end against [CardGame](https://github.com/daoanhkhoa123/CardGame)
as the target codebase, using
[`user_inputs/user_stories/05_leaderboard_no_format.md`](user_inputs/user_stories/05_leaderboard_no_format.md)
as the input user story. Generated acceptance-criteria test plans, the pytest
tests written against it, and the resulting test report are in
[`example_outputs`](example_outputs).
