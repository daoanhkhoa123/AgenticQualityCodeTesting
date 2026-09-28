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
