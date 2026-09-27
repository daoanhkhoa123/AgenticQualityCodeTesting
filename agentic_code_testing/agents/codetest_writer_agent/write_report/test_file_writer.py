from pathlib import Path

from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import TestWriteResult
from agentic_code_testing.agents.codetest_writer_agent.write_report.base import BaseTestWriter


class GeneratedTestWriter(BaseTestWriter):
    """Writes each scenario's drafted test file plus one combined markdown report.

    Test files are written for every result that has drafted code, including
    flagged_source_bug/unresolved outcomes -- the last draft stays inspectable
    even when the loop didn't fully resolve, rather than only keeping passing
    tests.
    """

    def write(self, results: list[TestWriteResult], output_dir: str | Path) -> list[Path]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        written_paths = []
        for result in results:
            if result.test_code:
                path = output_dir / f"test_{result.scenario_id}.py"
                path.write_text(result.test_code, encoding="utf-8")
                written_paths.append(path)

        report_path = output_dir / "report.md"
        report_path.write_text(self._render_report(results), encoding="utf-8")
        written_paths.append(report_path)

        return written_paths

    def _render_report(self, results: list[TestWriteResult]) -> str:
        lines = ["# Generated Test Report", ""]

        for result in results:
            lines += [
                f"## {result.scenario_id} -- {result.title}",
                "",
                f"- **Status:** {result.status}",
                f"- **Attempts:** {result.attempts}",
            ]
            if result.notes:
                lines += ["", result.notes]
            if result.classification is not None:
                lines += [
                    "",
                    "### Last classification",
                    "",
                    f"- **Test-code bug:** {result.classification.is_test_code_bug}",
                    f"- **Reasoning:** {result.classification.reasoning}",
                ]
            if result.test_code:
                lines += ["", "### Test code", "", "```python", result.test_code, "```"]
            lines.append("")

        return "\n".join(lines) + "\n"
