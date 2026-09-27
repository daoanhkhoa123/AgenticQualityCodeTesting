from pathlib import Path

# Small, real, stable subdirectory of this repo used as a fixture -- deliberately
# narrow so an LLM-graded answer stays predictable.
FIXTURE_DIR = Path(__file__).resolve().parents[2] / "user_story_agent" / "tools"
READ_FILE_PATH = FIXTURE_DIR / "read_file.py"
