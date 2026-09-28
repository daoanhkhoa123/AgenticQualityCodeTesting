```
"""
Pytest test: Clicking the Leaderboard button from the main menu opens a
pop-up window displaying a table of players.

Category : happy path
Preconditions:
    - Application is launched, main menu fully loaded.
    - 'Leaderboard' button present, visible, enabled.

Run with:  pytest test_leaderboard_happy_path.py -v
"""

import os
import sys
import types
import tkinter as tk
from tkinter import ttk
from unittest.mock import patch, mock_open

import pytest

# ---------------------------------------------------------------------------
# Stub the broken `Aboutus.aboutus` import so `test_GUI` can be imported.
# The repo ships `Aboutus/` with only images and no Python module, so the
# original import would raise ImportError.  We inject a minimal stub.
# ---------------------------------------------------------------------------
def _install_aboutus_stub() -> None:
    if "Aboutus" not in sys.modules:
        _pkg = types.ModuleType("Aboutus")
        _pkg.__path__ = []  # mark as a package so submodule imports work
        sys.modules["Aboutus"] = _pkg
    if "Aboutus.aboutus" not in sys.modules:
        _mod = types.ModuleType("Aboutus.aboutus")
        _mod.about_us = lambda *a, **kw: None
        sys.modules["Aboutus.aboutus"] = _mod


_install_aboutus_stub()

# Make sure the project root is on sys.path so `test_GUI` and `load.*` resolve.
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import test_GUI                                        # noqa: E402  – creates test_GUI.root (tk.Tk)
from load.leaderboard import Leaderboard              # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_button(parent: tk.Widget, text: str) -> tk.Button | None:
    """Recursively locate a tk.Button whose text label matches *text*."""
    for child in parent.winfo_children():
        if isinstance(child, tk.Button) and child.cget("text") == text:
            return child
        found = _find_button(child, text)
        if found is not None:
            return found
    return None


# ---------------------------------------------------------------------------
# Sample data used to mock `load/load.txt`
# ---------------------------------------------------------------------------
SAMPLE_LEADERBOARD_LINES = (
    "Alice 100\n"
    "Bob 250\n"
    "Charlie 50\n"
    "Diana 300\n"
    "Eve 150\n"
)
EXPECTED_ROW_COUNT = 5

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_leaderboard_guard():
    """Reset the module-level `leaderboard_window_open` flag between tests."""
    import load.leaderboard as _lb
    _lb.leaderboard_window_open = False
    yield
    _lb.leaderboard_window_open = False


@pytest.fixture(scope="module")
def main_menu():
    """Create the Tk root (already done at import time) and draw the menu."""
    root = test_GUI.root
    root.title("BlackJack Game")
    root.geometry("1250x500")
    root.deiconify()

    # load_home() builds the green frame + all menu buttons on test_GUI.root
    test_GUI.load_home()
    root.update()
    yield root

    # Module-level teardown: destroy any Toplevels left behind.
    for child in root.winfo_children():
        if isinstance(child, tk.Toplevel):
            child.destroy()
    root.update()
    root.destroy()


@pytest.fixture
def leaderboard_popup(main_menu):
    """
    Simulate the effect of clicking the 'Leaderboard' button:
    open a Toplevel and instantiate the Leaderboard app on it.

    Yields (toplevel_window, Leaderboard_instance).
    """
    popup = tk.Toplevel(main_menu)
    popup.title("Leaderboard")
    popup.geometry("400x400")

    # Mock the data file so the test is deterministic and independent of
    # whatever is (or isn't) in the repo's load/load.txt.
    with patch("builtins.open", mock_open(read_data=SAMPLE_LEADERBOARD_LINES)):
        app = Leaderboard(popup)

    popup.update()
    yield popup, app
    popup.destroy()
    main_menu.update()


# ---------------------------------------------------------------------------
# Tests – happy path
# ---------------------------------------------------------------------------

class TestLeaderboardHappyPath:
    """Happy-path: click Leaderboard → pop-up with a populated player table."""

    def test_1_main_menu_and_leaderboard_button(self, main_menu):
        """Step 1 – main menu is displayed; Leaderboard button is visible & enabled."""
        assert main_menu.winfo_exists(), "Main-menu root window does not exist"

        btn = _find_button(main_menu, "Leaderboard")
        assert btn is not None, "No button with text 'Leaderboard' found on main menu"
        assert btn.cget("state") == tk.NORMAL, "Leaderboard button is not enabled"
        assert btn.winfo_exists(), "Leaderboard button does not exist (destroyed?)"

    def test_2_popup_window_appears(self, main_menu, leaderboard_popup):
        """Step 3 – a pop-up window appears on top of the main menu."""
        popup, _app = leaderboard_popup
        assert popup.winfo_exists(), "Pop-up window was not created"
        assert popup.title() == "Leaderboard", "Pop-up title is incorrect"
        # The popup is a top-level widget (manager == 'tk' when mapped)
        assert popup.winfo_toplevel() is popup
        assert popup.winfo_reqwidth() > 0, "Pop-up has zero width"

    def test_3_popup_contains_table_structure(self, leaderboard_popup):
        """Step 4 – the pop-up contains a table with header row and data rows."""
        popup, app = leaderboard_popup
        tree = app.tree
        assert isinstance(tree, ttk.Treeview), "Leaderboard pop-up lacks a Treeview table"

        # Three expected column IDs
        cols = tree["columns"]
        assert "Rank" in cols, f"Column 'Rank' missing; got {cols}"
        assert "Name" in cols, f"Column 'Name' missing; got {cols}"
        assert "Money" in cols, f"Column 'Money' missing; got {cols}"

        # Headings (display labels) should match the spec
        headings = [tree.heading(c, "text") for c in cols]
        assert "Rank" in headings, f"Heading 'Rank' missing; got {headings}"
        assert "Player Name" in headings, f"Heading 'Player Name' missing; got {headings}"
        assert "Money" in headings, f"Heading 'Money' missing; got {headings}"

        # show='headings' means no tree column
        assert tree.cget("show") == "headings", "Treeview should use show='headings'"

    def test_4_table_populated_with_player_data(self, leaderboard_popup):
        """Step 5 – table rows contain player names and associated scores/ranks."""
        _popup, app = leaderboard_popup
        tree = app.tree
        row_ids = tree.get_children()

        assert len(row_ids) == EXPECTED_ROW_COUNT, (
            f"Expected {EXPECTED_ROW_COUNT} data rows, got {len(row_ids)}"
        )

        for row_id in row_ids:
            values = tree.item(row_id, "values")
            assert len(values) == 3, f"Row {row_id} has {len(values)} values, expected 3"
            rank, name, money = values
            assert rank is not None and str(rank) != "", "Rank value is empty"
            int(rank)  # raises if not numeric
            assert isinstance(name, str) and len(name) > 0, "Player name is empty"
            int(money)  # raises if not numeric

    def test_5_main_menu_still_visible_behind_popup(self, main_menu, leaderboard_popup):
        """Step 6 – the main menu is still visible behind the pop-up (not replaced)."""
        _popup, _app = leaderboard_popup

        # Root window still alive
        assert main_menu.winfo_exists(), "Main-menu root was destroyed"

        # The green menu frame is still a child of the root
        frames = [c for c in main_menu.winfo_children() if isinstance(c, tk.Frame)]
        assert frames, "Main-menu frame not found behind the pop-up"

        # Leaderboard button still present and mapped
        btn = _find_button(main_menu, "Leaderboard")
        assert btn is not None, "Leaderboard button disappeared after opening pop-up"
        assert btn.winfo_exists()

    def test_6_closing_popup_restores_main_menu(self, main_menu, leaderboard_popup):
        """Step 7 – closing the pop-up leaves the main menu fully visible."""
        popup, _app = leaderboard_popup

        # Close the pop-up (equivalent to clicking a close button / pressing Escape)
        popup.destroy()
        main_menu.update()

        # Pop-up is gone
        assert not popup.winfo_exists(), "Pop-up still exists after destroy()"

        # Main menu is fully functional
        assert main_menu.winfo_exists(), "Main-menu root lost after closing pop-up"
        btn = _find_button(main_menu, "Leaderboard")
        assert btn is not None, "Leaderboard button lost after closing pop-up"
        assert btn.cget("state") == tk.NORMAL, "Leaderboard button disabled after pop-up close"
```
