from pathlib import Path

from agentic_code_testing.orchestrator.typed_schemas import PipelineResult
from agentic_code_testing.orchestrator.write_markdown.base import BasePipelineResultWriter


class MarkdownPipelineResultWriter(BasePipelineResultWriter):
    def write(self, result: PipelineResult, output_dir: str | Path) -> Path:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        path = output_dir / f"story-{result.story_id}.md"
        path.write_text(self._render(result), encoding="utf-8")
        return path

    def _render(self, result: PipelineResult) -> str:
        user_story = result.user_story

        lines = [
            f"# Pipeline Result: {user_story.name or f'Story {result.story_id}'}",
            "",
            f"- **Story ID:** {result.story_id}",
            f"- **Scenarios Generated:** {len(result.scenarios)}",
            f"- **Tests Written:** {len(result.test_results)}",
            "",
            "## User Story",
            "",
            user_story.story_body,
        ]

        if user_story.acceptance_criteria:
            lines += ["", "## Acceptance Criteria", "", user_story.acceptance_criteria]

        lines += ["", "## Scenarios", ""]
        if not result.scenarios:
            lines.append("_No scenarios were generated._")
        for scenario in result.scenarios:
            lines += [
                f"### {scenario.scenario_id}: {scenario.title}",
                "",
                f"- **Category:** {scenario.category}",
                f"- **Priority:** {scenario.priority}",
                f"- **Test Type:** {scenario.test_type}",
                "",
                scenario.description,
                "",
            ]

        lines += ["## Test Results", ""]
        if not result.test_results:
            lines.append("_No tests were written._")
        for test_result in result.test_results:
            lines += [
                f"### {test_result.scenario_id}: {test_result.title}",
                "",
                f"- **Status:** {test_result.status}",
                f"- **Attempts:** {test_result.attempts}",
            ]
            if test_result.notes:
                lines.append(f"- **Notes:** {test_result.notes}")
            if test_result.test_code:
                lines += ["", "```python", test_result.test_code, "```"]
            lines.append("")

        return "\n".join(lines) + "\n"
