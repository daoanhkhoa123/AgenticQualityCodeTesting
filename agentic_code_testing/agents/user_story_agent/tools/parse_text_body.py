import re

def _extract_section(text: str, label: str) -> str | None:
    """
    Grab the text of a `**<label>:**` field, up to the next `**...:**`
    field or the end of the document.
    """
    pattern = rf"\*\*\s*{label}\s*:\s*\*\*\s*(.*?)(?=\n\s*\*\*[^*\n]+:\*\*|\Z)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None


def parse_re_story_file(text: str) -> dict[str, str | None]:
    """
    Parse the content of a markdown user-story file that follows this
    project's convention:

    Returns a dict keyed to match `StoryAgentState`'s fields
    (`name`, `description`, `techinal_description`, `test_description`,
    `acceptance_criteria`).
    """
    name_match = re.search(r"^#{1,6}\s*(.+)$", text, re.MULTILINE)
    if not name_match:
        name_match = re.search(r"\*{0,2}\s*name\s*\*{0,2}\s*:\s*(.+)", text, re.IGNORECASE)
    name = name_match.group(1).strip() if name_match else None

    return {
        "name": name,
        "description": _extract_section(text, "Story description"),
        "techinal_description": _extract_section(
            text, r"(?:Application\s+)?[Tt]echnical description"
        ),
        "test_description": _extract_section(text, "Test description"),
        "acceptance_criteria": _extract_section(text, "Acceptance criteria"),
    }

