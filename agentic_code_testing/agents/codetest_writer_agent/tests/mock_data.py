from pathlib import Path

from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "sample_target"
MATHY_PATH = FIXTURE_DIR / "mathy.py"

SCENARIO_ADD_HAPPY_PATH = Scenario(
    scenario_id="mathy-add-happy",
    story_id=1,
    ac_id="AC-1",
    category="happy path",
    priority="P1",
    test_type="unit",
    title="add returns the sum of two integers",
    description="Calling add(2, 3) from mathy.py should return 5.",
    steps=["Call add(2, 3)", "Assert the result equals 5"],
    expected_result="add(2, 3) returns 5",
)

SCENARIO_IS_EVEN_BUGGY = Scenario(
    scenario_id="mathy-is-even-happy",
    story_id=1,
    ac_id="AC-2",
    category="happy path",
    priority="P1",
    test_type="unit",
    title="is_even returns True for even numbers",
    description="Calling is_even(4) from mathy.py should return True, since 4 is even.",
    steps=["Call is_even(4)", "Assert the result is True"],
    expected_result="is_even(4) returns True",
)
