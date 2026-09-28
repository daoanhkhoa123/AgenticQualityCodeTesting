# Leaderboard popup opens with an empty table when no players exist

- **Story ID:** 1
- **AC ID:** AC-1
- **Category:** edge case
- **Priority:** P2
- **Test Type:** e2e

## Description

Verify that when the player list is empty (zero registered players), clicking the 'Leaderboard' button from the main menu still opens the popup window successfully, but the table displays an empty/zero-row state without errors or a blank/broken layout.

## Preconditions

1. The application is logged in (or accessible per its auth model).
2. The backend/database contains zero player records (fresh install or all players deleted).
3. The main menu is visible and the 'Leaderboard' button is enabled and clickable.

## Steps

1. Navigate to the main menu of the application.
2. Verify the 'Leaderboard' button is visible and in a clickable (enabled) state.
3. Click the 'Leaderboard' button.
4. Observe whether a popup/modal window appears (not a new tab, not a full page redirect).
5. Inspect the table inside the popup: confirm the table element exists with column headers.
6. Verify the table body has zero <tr> data rows (or displays an 'No players yet' / empty-state message).
7. Check the browser console and network tab for any unhandled errors, failed API calls, or exceptions.
8. Attempt to close the popup (click close button or press Escape).
9. Verify the main menu is fully interactive again after the popup closes.

## Expected Result

1. User navigates to the main menu.
2. User clicks the 'Leaderboard' button.
3. A popup window opens (not a full-page navigation).
4. The popup contains a table structure/headers (e.g., Rank, Player Name, Score).
5. The table body contains zero data rows.
6. No JavaScript errors, 4xx/5xx API responses, or unhandled exceptions are thrown.
7. The popup can be closed normally (e.g., via a close button or Escape key).
8. The main menu remains fully functional behind/after the popup.
