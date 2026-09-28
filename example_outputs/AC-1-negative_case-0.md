# Leaderboard popup displays an error state when player data cannot be fetched

- **Story ID:** 1
- **AC ID:** AC-1
- **Category:** negative case
- **Priority:** P1
- **Test Type:** integration

## Description

Verify that when the Leaderboard button is clicked from the main menu but the system is unable to retrieve player data (e.g., due to a server error, timeout, or empty dataset), the popup window still opens and displays an appropriate error or empty-state message instead of a blank or broken table.

## Preconditions

1. The application is running and the main menu is visible.
2. The Leaderboard data source (API/service) is intentionally unavailable, returning a 500/timeout, OR the player collection is empty.
3. The user has a valid session (authenticated).

## Steps

1. 1. Navigate to the main menu.
2. 2. Click the 'Leaderboard' button.
3. 3. Observe the popup window that appears.
4. 4. Inspect the table area within the popup for an error/empty-state message.
5. 5. Attempt to close the popup using its close button or Escape key.

## Expected Result

A popup window opens in response to the click. The popup does NOT display a malformed or infinitely loading table. Instead, it shows a user-facing message such as 'No players available' or 'Failed to load leaderboard. Please try again later.' with a valid option to retry or close the popup. The popup must not crash the application or leave an unresponsive dialog.
