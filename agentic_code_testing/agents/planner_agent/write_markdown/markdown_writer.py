from pathlib import Path

from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario
from agentic_code_testing.agents.planner_agent.write_markdown.base import BaseScenarioWriter


class MarkdownScenarioWriter(BaseScenarioWriter):
    def write(self, scenarios: list[Scenario], output_dir: str | Path) -> list[Path]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        written_paths = []
        for scenario in scenarios:
            path = output_dir / f"{scenario.scenario_id}.md"
            path.write_text(self._render(scenario), encoding="utf-8")
            written_paths.append(path)

        return written_paths

    def _render(self, scenario: Scenario) -> str:
        lines = [
            f"# {scenario.title}",
            "",
            f"- **Story ID:** {scenario.story_id}",
            f"- **AC ID:** {scenario.ac_id}",
            f"- **Category:** {scenario.category}",
            f"- **Priority:** {scenario.priority}",
            f"- **Test Type:** {scenario.test_type}",
            "",
            "## Description",
            "",
            scenario.description,
        ]

        if scenario.preconditions:
            lines += ["", "## Preconditions", "", scenario.preconditions]

        lines += ["", "## Steps", ""]
        lines += [f"{i}. {step}" for i, step in enumerate(scenario.steps, start=1)]

        lines += ["", "## Expected Result", "", scenario.expected_result]

        return "\n".join(lines) + "\n"
