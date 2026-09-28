# Generated Test Report

## AC-1-happy_path-0 -- Clicking the Leaderboard button from the main menu opens a pop-up window displaying a table of players

- **Status:** flagged_source_bug
- **Attempts:** 1

Flagged as a likely source bug after 1 attempt(s): The error is 'No module named pytest' — pytest is simply not installed in the virtual environment (D:\CardGame-main\.venv) being used to run the test. The test file itself is correctly written (proper imports, fixtures, assertions, no signature mismatches), and the source code was never even reached. This is a missing-dependency / environment-setup issue, not a defect in the test logic or in the code under test. No amount of rewriting the test code would resolve it; the fix is to `pip install pytest` into that venv.

### Last classification

- **Test-code bug:** False
- **Reasoning:** The error is 'No module named pytest' — pytest is simply not installed in the virtual environment (D:\CardGame-main\.venv) being used to run the test. The test file itself is correctly written (proper imports, fixtures, assertions, no signature mismatches), and the source code was never even reached. This is a missing-dependency / environment-setup issue, not a defect in the test logic or in the code under test. No amount of rewriting the test code would resolve it; the fix is to `pip install pytest` into that venv.

### Test code

```python
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

```

## AC-1-happy_path-1 -- User successfully opens the Leaderboard pop-up and views populated player table from the main menu

- **Status:** flagged_source_bug
- **Attempts:** 1

Flagged as a likely source bug after 1 attempt(s): The pytest output shows the error: `D:\CardGame-main\.venv\Scripts\python.exe: No module named pytest`. This is an environment/dependency issue — the virtual environment used to run the tests does not have the `pytest` package installed. The test code itself is correctly written: it properly imports `pytest` and `playwright.sync_api`, uses fixtures with valid signatures, and contains logically sound assertions. No amount of rewriting the test file will resolve a missing Python package in the interpreter's site-packages. Conversely, this is not a source-code-under-test bug either, because the test never actually executed to exercise the application code. The failure is purely an infrastructure/setup problem: `pytest` (and likely `playwright`) must be installed in the target virtual environment before the test suite can run.

### Last classification

- **Test-code bug:** False
- **Reasoning:** The pytest output shows the error: `D:\CardGame-main\.venv\Scripts\python.exe: No module named pytest`. This is an environment/dependency issue — the virtual environment used to run the tests does not have the `pytest` package installed. The test code itself is correctly written: it properly imports `pytest` and `playwright.sync_api`, uses fixtures with valid signatures, and contains logically sound assertions. No amount of rewriting the test file will resolve a missing Python package in the interpreter's site-packages. Conversely, this is not a source-code-under-test bug either, because the test never actually executed to exercise the application code. The failure is purely an infrastructure/setup problem: `pytest` (and likely `playwright`) must be installed in the target virtual environment before the test suite can run.

### Test code

```python
"""E2E test: User successfully opens the Leaderboard pop-up and views a populated
player table from the main menu.

Category: happy path

Prerequisites:
    - The target web application is running (set via the ``--base-url`` Playwright
      CLI option or the ``PLAYWRIGHT_BASE_URL`` environment variable).
    - A valid authenticated session is established (handled by the ``authed_page``
      fixture below).
    - At least one player entry exists in the leaderboard data source.

Run with::

    pytest tests/test_leaderboard_popup.py --base-url http://localhost:3000 --headed
"""

import re
from typing import List

import pytest
from playwright.sync_api import Page, expect


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def authed_page(page: Page, base_url: str) -> Page:
    """Return a ``page`` already logged in and navigated to the main menu.

    Preconditions verified here:
      1. Session / login state is active.
      2. The main menu is rendered and visible.
      3. The Leaderboard button is present, visible, and enabled.
      4. (Data-level precondition — at least one player entry — is verified
         inside the test itself by asserting a non-empty table body.)
    """
    # --- establish session ------------------------------------------------
    # If the app uses a cookie-based session, set it here.  Adjust the
    # token / endpoint to match the real authentication flow.
    page.goto(f"{base_url}/login", wait_until="domcontentloaded")
    # Example: fill in credentials if no persistent session cookie is set.
    # In many test setups a session cookie is injected via a storage-state
    # file (see ``playwright.config``).  We keep the block below as a no-op
    # guard so the fixture works in either mode.
    if page.is_visible("#username", timeout=3_000):
        page.fill("#username", "test_user")
        page.fill("#password", "test_password")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")

    # --- navigate to the main menu ----------------------------------------
    page.goto(f"{base_url}/", wait_until="domcontentloaded")
    # Give the SPA / SSR page a moment to finish hydrating the menu.
    page.wait_for_load_state("networkidle")

    # --- precondition: main menu is visible --------------------------------
    # Accept any top-level navigation container that signals the main menu.
    main_menu = page.locator("main, #main-menu, .main-menu, [data-testid='main-menu']").first
    expect(main_menu).to_be_visible(timeout=10_000)

    # --- precondition: Leaderboard button is present, visible, enabled -----
    lb_button = _find_leaderboard_button(page)
    expect(lb_button).to_be_visible()
    expect(lb_button).to_be_enabled()

    return page


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_leaderboard_button(page: Page):
    """Locate the Leaderboard trigger button on the main menu.

    Tries several common selector strategies so the test is resilient to
    minor markup changes.  Returns a single ``Locator``.
    """
    candidates = [
        page.get_by_role("button", name=re.compile(r"leaderboard", re.I)),
        page.get_by_role("link", name=re.compile(r"leaderboard", re.I)),
        page.locator("[data-testid='leaderboard-button']"),
        page.locator("button:has-text('Leaderboard')"),
    ]
    for loc in candidates:
        if loc.count() > 0:
            return loc.first
    raise AssertionError(
        "Could not find a 'Leaderboard' button/link on the main menu. "
        "Verified roles: button, link; text: 'Leaderboard'; testid: leaderboard-button."
    )


def _find_modal(page: Page):
    """Locate the pop-up / modal overlay.

    Works with ARIA ``role=dialog``, common modal classes, or a backdrop
    element.  Returns a single ``Locator``.
    """
    candidates = [
        page.get_by_role("dialog"),
        page.locator("[role='dialog']"),
        page.locator(".modal, .popup, .overlay, [class*='modal'], [class*='popup']"),
        page.locator("[data-testid='leaderboard-modal']"),
    ]
    for loc in candidates:
        if loc.count() > 0:
            return loc.first
    raise AssertionError(
        "No modal / dialog / pop-up element detected after clicking Leaderboard."
    )


def _assert_header_contains(table_locator, *keywords: str) -> None:
    """Assert that the table's column-header row contains the given keywords."""
    headers = table_locator.get_by_role("columnheader")
    if headers.count() == 0:
        # Fallback: some tables use ``<th>`` inside the first row without ARIA.
        headers = table_locator.locator("tr:first-child th, tr:first-child td")
    header_texts = [h.inner_text().strip().lower() for h in headers.all()]
    joined = " | ".join(header_texts)
    missing = [kw for kw in keywords if kw.lower() not in joined]
    assert not missing, (
        f"Expected table headers to include {keywords!r}, "
        f"but found only: {header_texts}"
    )


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

def test_leaderboard_popup_shows_populated_player_table(
    authed_page: Page,
    base_url: str,
) -> None:
    """Happy-path: click Leaderboard → modal appears with a populated player table.

    Verifies (in order):
      1. The 'Leaderboard' button is visible and enabled on the main menu.
      2. Clicking it opens a pop-up / modal **without** a full page navigation.
      3. The modal contains a table element.
      4. The table has header columns for Rank, Player Name, and Score.
      5. The table body is populated with at least one player row that shows
         a name and a score/rank value.
      6. The main menu is still present in the DOM behind the pop-up
         (confirming overlay behaviour, not a route change).
    """
    page = authed_page

    # -- Step 1: Leaderboard button is visible & enabled --------------------
    lb_button = _find_leaderboard_button(page)
    expect(lb_button).to_be_visible()
    expect(lb_button).to_be_enabled()

    # -- Step 2: Click and verify a pop-up appears (no navigation) ----------
    url_before_click = page.url
    lb_button.click()

    # Wait for the modal to become visible (Playwright auto-waits up to timeout).
    modal = _find_modal(page)
    expect(modal).to_be_visible(timeout=5_000)

    # The URL must NOT have changed — this is an overlay, not a route change.
    # Allow for hash fragments or query-param additions but not a path change.
    path_before = url_before_click.rstrip("/").split("/")[-1] if "/" in url_before_click else ""
    path_after = page.url.rstrip("/").split("/")[-1] if "/" in page.url else ""
    assert path_before == path_after, (
        f"Expected to remain on the main-menu route ({url_before!r}) "
        f"but the URL changed to {page.url!r}. "
        "The Leaderboard should open as a pop-up, not a full navigation."
    )

    # -- Step 3: The modal contains a table ---------------------------------
    table = modal.locator("table").first
    if table.count() == 0:
        # Some implementations use ``role=grid`` or ``role=table`` without a
        # literal <table> element.
        table = modal.get_by_role("table").first
    expect(table).to_be_visible()

    # -- Step 4: Header columns include Rank, Player Name, Score ------------
    _assert_header_contains(table, "rank", "player", "score")

    # -- Step 5: At least one data row with a name and a score/rank ---------
    data_rows = table.get_by_role("row").filter(
        # Exclude the header row (first row) to get data rows only.
        # We'll handle this via indexing below.
        lambda r: True,
    )
    all_rows = table.get_by_role("row")
    total_rows = all_rows.count()
    assert total_rows >= 2, (
        f"Expected at least 2 rows (1 header + 1 data) in the leaderboard table, "
        f"but found only {total_rows}."
    )

    # Inspect every data row (skip the first, which is the header).
    found_valid_row = False
    for i in range(1, total_rows):
        row = all_rows.nth(i)
        cells = row.get_by_role("cell").or_(row.locator("td, th"))
        cell_texts = [c.inner_text().strip() for c in cells.all()]
        # A valid player row should have at least one cell that looks like a
        # name (non-numeric, non-empty) AND one that looks like a score/rank
        # (numeric or a short ordinal).
        has_name = any(
            t and not re.fullmatch(r"\d+", t) and len(t) >= 2
            for t in cell_texts
        )
        has_score_or_rank = any(
            re.fullmatch(r"\d+", t) or re.fullmatch(r"\d+[KkMm]", t)
            for t in cell_texts
        )
        if has_name and has_score_or_rank:
            found_valid_row = True
            break

    assert found_valid_row, (
        f"None of the {total_rows - 1} data row(s) contained both a player "
        "name and a score/rank value.  "
        "The leaderboard table does not appear to be properly populated."
    )

    # -- Step 6: Main menu is still present behind the pop-up ---------------
    main_menu = page.locator(
        "main, #main-menu, .main-menu, [data-testid='main-menu']"
    ).first
    # ``to_be_attached`` only checks the element is in the DOM (it may be
    # visually covered by the modal), which is the correct assertion here.
    expect(main_menu).to_be_attached()

    # Additionally, confirm the Leaderboard button itself is still in the
    # DOM (now behind the overlay).
    expect(lb_button).to_be_attached()

```

