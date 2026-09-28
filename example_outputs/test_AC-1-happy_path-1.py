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
