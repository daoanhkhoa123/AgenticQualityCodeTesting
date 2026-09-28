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
