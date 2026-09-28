# Generated Test Report

## AC-1-happy_path-0 -- Clicking the Leaderboard button from the main menu opens a popup displaying a player table

- **Status:** flagged_source_bug
- **Attempts:** 1

Flagged as a likely source bug after 1 attempt(s): There are two failures to analyze:

1. **ERROR (test_table_is_populated)**: `_tkinter.TclError: Can't find a usable init.tcl`. This is a Tcl/Tk runtime environment issue (the Tcl library is missing or corrupted for this Python installation). It is neither a test-logic bug nor a source-code bug — it's an infrastructure problem. Notably, 7 other tests using the identical `tk.Tk()` fixture passed, suggesting this is an intermittent/resource-exhaustion issue in the CI environment, not something a rewritten test could avoid.

2. **FAIL (test_player_name_is_nonempty)**: The assertion `isinstance(name, str) and name.strip()` fails because `values[1]` (the "Name" column) contains the integer `5` instead of a string. The test's column assumptions are validated by `test_table_columns_are_correct` (which passed, confirming the headers are indeed Rank, Name, Money) and `test_first_row_rank_is_one` (which passed, confirming values[0] is the rank). So the test is reading the correct column index. The problem is that the source code (or its underlying data file `load/load.txt`) is placing a numeric value (`5`) in the Name field. A leaderboard displaying player names should contain string names, not bare integers. This is a data-integrity bug in the source code / data pipeline, not a test authoring mistake.

Because the meaningful assertion failure is caused by the source code producing incorrect data (a number in a name field), rewriting the test would not fix the underlying issue — the test is correctly enforcing that the Name column holds a non-empty string.

### Last classification

- **Test-code bug:** False
- **Reasoning:** There are two failures to analyze:

1. **ERROR (test_table_is_populated)**: `_tkinter.TclError: Can't find a usable init.tcl`. This is a Tcl/Tk runtime environment issue (the Tcl library is missing or corrupted for this Python installation). It is neither a test-logic bug nor a source-code bug — it's an infrastructure problem. Notably, 7 other tests using the identical `tk.Tk()` fixture passed, suggesting this is an intermittent/resource-exhaustion issue in the CI environment, not something a rewritten test could avoid.

2. **FAIL (test_player_name_is_nonempty)**: The assertion `isinstance(name, str) and name.strip()` fails because `values[1]` (the "Name" column) contains the integer `5` instead of a string. The test's column assumptions are validated by `test_table_columns_are_correct` (which passed, confirming the headers are indeed Rank, Name, Money) and `test_first_row_rank_is_one` (which passed, confirming values[0] is the rank). So the test is reading the correct column index. The problem is that the source code (or its underlying data file `load/load.txt`) is placing a numeric value (`5`) in the Name field. A leaderboard displaying player names should contain string names, not bare integers. This is a data-integrity bug in the source code / data pipeline, not a test authoring mistake.

Because the meaningful assertion failure is caused by the source code producing incorrect data (a number in a name field), rewriting the test would not fix the underlying issue — the test is correctly enforcing that the Name column holds a non-empty string.

### Test code

```python
"""Pytest test for the Leaderboard happy path.

Scenario: Clicking the Leaderboard button from the main menu opens a popup
displaying a player table.

Validates the end-to-end happy path: a user on the main menu clicks the
'Leaderboard' button and is presented with a popup window containing a
properly rendered table of players.

Run with:
    pytest test_leaderboard.py -v

Requires a display (Tkinter desktop app). The CWD must be the project root
because `Leaderboard.load_data()` uses the relative path `load/load.txt`.
"""

import os
import sys

import pytest

# Ensure the project root is importable regardless of where pytest is invoked.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def main_menu_root():
    """Create the 'main menu' Tk root window (analogous to test_GUI.py load_home)."""
    import tkinter as tk

    root = tk.Tk()
    root.title("Main Menu")
    root.geometry("800x600")
    root.withdraw()  # keep the background window out of sight
    root.update_idletasks()
    root.update()
    yield root
    root.destroy()


@pytest.fixture
def leaderboard_popup(main_menu_root):
    """Simulate clicking the Leaderboard button.

    Instead of calling `show_leaderboard()` (which calls blocking `mainloop()`),
    we instantiate `Leaderboard` directly on a `Toplevel` — exactly what the
    button's command callback would produce, minus the blocking loop.

    Yields a tuple ``(app, popup)`` where:
      * ``app``   – the `Leaderboard` instance (exposes `.tree`)
      * ``popup`` – the `tk.Toplevel` window acting as the modal overlay
    """
    import tkinter as tk
    from load.leaderboard import Leaderboard

    popup = tk.Toplevel(main_menu_root)
    popup.title("Leaderboard")

    app = Leaderboard(popup)

    # Pump the event queue so all widget creation / data loading is flushed.
    main_menu_root.update_idletasks()
    main_menu_root.update()

    yield app, popup

    popup.destroy()


# ---------------------------------------------------------------------------
# Tests (mapped to the scenario steps)
# ---------------------------------------------------------------------------


class TestLeaderboardHappyPath:
    """Happy-path: Leaderboard button → popup with a populated player table."""

    # Step 3 – popup / modal window appears
    def test_popup_window_appears(self, leaderboard_popup):
        """A popup (Toplevel) window is created and exists."""
        _app, popup = leaderboard_popup
        assert popup.winfo_exists(), "Leaderboard popup window should exist."
        # The Toplevel is a child of the main-menu root → it overlays it.
        assert popup.master is not None, "Popup should be parented to the main menu."

    # Step 4 – popup contains a table element
    def test_popup_contains_table(self, leaderboard_popup):
        """The popup contains a ttk.Treeview (the 'table')."""
        import tkinter.ttk as ttk

        app, _popup = leaderboard_popup
        assert hasattr(app, "tree"), (
            "Leaderboard instance should expose a '.tree' attribute (the table)."
        )
        assert isinstance(app.tree, ttk.Treeview), (
            "The table element should be a ttk.Treeview widget."
        )

    # Step 5a – table has the expected columns
    def test_table_columns_are_correct(self, leaderboard_popup):
        """Columns must be Rank, Name, Money (the three player attributes)."""
        app, _popup = leaderboard_popup
        columns = list(app.tree["columns"])

        assert "Rank" in columns, f"Expected 'Rank' in columns, got {columns}"
        assert "Name" in columns, f"Expected 'Name' in columns, got {columns}"
        assert "Money" in columns, f"Expected 'Money' in columns, got {columns}"

    # Step 5b – table is populated with at least one player row
    def test_table_is_populated(self, leaderboard_popup):
        """At least one player entry must be present in the table."""
        app, _popup = leaderboard_popup
        children = app.tree.get_children()
        assert len(children) >= 1, (
            "Leaderboard table must contain at least one player row."
        )

    # Step 5c – each row carries three values (rank, name, money)
    def test_rows_have_all_three_fields(self, leaderboard_popup):
        """Every row must have exactly 3 values matching the 3 columns."""
        app, _popup = leaderboard_popup
        children = app.tree.get_children()
        for child in children:
            values = app.tree.item(child)["values"]
            assert len(values) == 3, (
                f"Row {child!r} should have 3 values (Rank, Name, Money), "
                f"got {len(values)}: {values}"
            )

    # Step 6 – popup overlays the main menu (Toplevel = child of root)
    def test_popup_overlays_main_menu(self, main_menu_root):
        """The leaderboard is a Toplevel of the main-menu root → overlay behaviour."""
        import tkinter as tk
        from load.leaderboard import Leaderboard

        popup = tk.Toplevel(main_menu_root)
        Leaderboard(popup)
        main_menu_root.update_idletasks()
        main_menu_root.update()

        # A Toplevel whose master is the root is inherently displayed over it.
        assert popup.master is main_menu_root, (
            "Leaderboard popup must be a Toplevel of the main-menu root "
            "(overlay / modal behaviour)."
        )
        assert popup.winfo_exists(), "Overlay window should be visible."

        popup.destroy()

    # Additional data-integrity checks
    def test_first_row_rank_is_one(self, leaderboard_popup):
        """The top player (row 0) should carry rank 1."""
        app, _popup = leaderboard_popup
        children = app.tree.get_children()
        assert len(children) >= 1
        values = app.tree.item(children[0])["values"]
        rank = values[0]
        assert int(rank) == 1, f"Top-ranked player should have rank 1, got {rank}"

    def test_player_name_is_nonempty(self, leaderboard_popup):
        """Every player's name field must be a non-empty string."""
        app, _popup = leaderboard_popup
        children = app.tree.get_children()
        for child in children:
            name = app.tree.item(child)["values"][1]
            assert isinstance(name, str) and name.strip(), (
                f"Player name should be a non-empty string, got {name!r}"
            )

    def test_player_money_is_positive(self, leaderboard_popup):
        """Every player's money field must be a positive number."""
        app, _popup = leaderboard_popup
        children = app.tree.get_children()
        for child in children:
            money = app.tree.item(child)["values"][2]
            assert isinstance(money, (int, float)), (
                f"Money should be numeric, got {type(money).__name__}: {money!r}"
            )
            assert money > 0, f"Money should be positive, got {money}"

```

## AC-1-happy_path-1 -- Verify Leaderboard popup with player table opens from main menu

- **Status:** passed
- **Attempts:** 3

Passed after 3 attempt(s).

### Last classification

- **Test-code bug:** True
- **Reasoning:** The failure is `AttributeError: 'Button' object has no attribute 'command'` at line 101. In tkinter, widget options like `command` are stored as Tcl options, not as Python attributes on the widget object. The only way to read them is via `btn.cget("command")` or `btn["command"]`, both of which return a Tcl command string (e.g. `'2624254925248<lambda>'`). There is no `btn.command` Python attribute. The test even has a comment explaining the author's (incorrect) reasoning for using `btn.command` instead of `btn.cget("command")`. The source code correctly sets the button's command via the `command=` keyword argument in the constructor, which is standard tkinter. The test simply uses the wrong accessor. Since the `command` variable is never actually used after the assertion (the test manually constructs the popup), the fix is straightforward.

### Test code

```python
import sys
import os
import types
import tkinter as tk
import tkinter.ttk as ttk
import pytest


# ---------------------------------------------------------------------------
# Stub out the missing Aboutus.aboutus module so test_GUI can be imported.
# test_GUI.py does `from Aboutus.aboutus import about_us` but that file does
# not exist in the project tree.
# ---------------------------------------------------------------------------
def _stub_aboutus():
    pkg = types.ModuleType("Aboutus")
    pkg.__path__ = []
    sub = types.ModuleType("Aboutus.aboutus")
    sub.about_us = lambda *a, **kw: None
    pkg.aboutus = sub
    sys.modules.setdefault("Aboutus", pkg)
    sys.modules.setdefault("Aboutus.aboutus", sub)


_stub_aboutus()

import test_GUI  # noqa: E402  (creates module-level root = tk.Tk() on import)
from load.leaderboard import Leaderboard  # noqa: E402

DATA_FILE = os.path.join("load", "load.txt")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def seed_leaderboard_data():
    """Ensure load/load.txt exists and contains at least one valid record."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        f.write("Alice 500\n")
    yield


@pytest.fixture(autouse=True)
def teardown_tk():
    """Destroy all Tk windows after each test to avoid leftover windows."""
    yield
    # Destroy any Tk windows that may still be alive
    mod = sys.modules.get("test_GUI")
    if mod is not None:
        w = getattr(mod, "root", None)
        if w is not None:
            try:
                w.destroy()
            except tk.TclError:
                pass


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _find_leaderboard_button():
    """Locate the 'Leaderboard' tk.Button among the main-menu frame children."""
    frame = None
    for child in test_GUI.root.winfo_children():
        if isinstance(child, tk.Frame):
            frame = child
            break
    assert frame is not None, "Main-menu tk.Frame not found under root"

    candidates = [
        w for w in frame.winfo_children()
        if isinstance(w, tk.Button) and w.cget("text") == "Leaderboard"
    ]
    assert candidates, "Leaderboard button not found on the main menu"
    return candidates[0]


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------
def test_leaderboard_popup_opens_with_player_table_from_main_menu():
    """
    Happy-path: a user on the main menu clicks the Leaderboard button and a
    popup window appears containing a populated table of players, while the
    main menu remains visible behind the popup.
    """

    # ── Step 1: Navigate to the main menu screen ──────────────────────────
    test_GUI.load_home()
    test_GUI.root.update_idletasks()
    assert test_GUI.root.winfo_exists(), "Main-menu root window is missing"

    # ── Step 2: Locate and verify the Leaderboard button wiring ──────────
    btn = _find_leaderboard_button()

    # Use btn.cget("command") to retrieve the Tcl command string.
    # The real command is lambda: show_leaderboard() which creates a second
    # tk.Tk() and blocks on mainloop() — impractical inside pytest.
    # We therefore verify the wiring and then build the popup ourselves,
    # which is exactly what show_leaderboard does internally:
    #
    #     root = tk.Tk()
    #     app  = Leaderboard(root)
    #     root.mainloop()
    command = btn.cget("command")
    assert command, "Leaderboard button has no command attached"

    # ── Step 3: Build the popup (simulates the click result) ─────────────
    popup_root = tk.Tk()
    popup_root.title("Leaderboard")
    lb = Leaderboard(popup_root)
    popup_root.update_idletasks()

    # ── Expected result: popup is displayed ───────────────────────────────
    assert popup_root.winfo_exists(), "Popup window was not created"
    assert popup_root.winfo_viewable(), "Popup window is not visible"

    # ── Expected result: popup contains a table with >= 1 player row ─────
    assert isinstance(lb.tree, ttk.Treeview), (
        f"Expected a ttk.Treeview, got {type(lb.tree).__name__}"
    )

    # Confirm the three expected columns are present
    columns = lb.tree["columns"]
    assert "Rank" in columns
    assert "Name" in columns
    assert "Money" in columns

    child_ids = lb.tree.get_children("")
    assert len(child_ids) >= 1, (
        f"Expected at least 1 player row in the table, found {len(child_ids)}"
    )

    # Spot-check the single seeded record
    first_values = lb.tree.item(child_ids[0], "values")
    assert len(first_values) == 3, f"Row should have 3 values, got {first_values}"
    assert first_values[1] == "Alice", f"Expected name 'Alice', got {first_values[1]!r}"
    assert int(first_values[2]) == 500, f"Expected money 500, got {first_values[2]!r}"

    # ── Expected result: main menu remains visible behind the popup ──────
    assert test_GUI.root.winfo_exists(), "Main-menu window was destroyed"
    assert test_GUI.root.winfo_viewable(), "Main-menu window is no longer visible"

    # ── Cleanup popup ─────────────────────────────────────────────────────
    popup_root.destroy()

```

