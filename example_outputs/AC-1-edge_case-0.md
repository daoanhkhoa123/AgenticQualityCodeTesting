# Leaderboard pop-up opens with empty player list

- **Story ID:** 1
- **AC ID:** AC-1
- **Category:** edge case
- **Priority:** P2
- **Test Type:** e2e

## Description

Verify that clicking the 'Leaderboard' button from the main menu when no players have registered yet still opens the pop-up window and displays the table structure (headers/columns) without crashing or showing undefined data.

## Preconditions

The application is at the main menu. The backend/database contains zero registered players. No other pop-ups are open.

## Steps

1. Navigate to the main menu.
2. Click the 'Leaderboard' button.
3. Observe the pop-up window that appears.
4. Verify the table structure (headers) is rendered.
5. Verify no data rows are present.
6. Check the browser console for any unhandled errors.
7. Close the pop-up window.

## Expected Result

The pop-up window opens successfully. The table is rendered with column headers visible but no data rows. No JavaScript errors are thrown. An appropriate empty state message (e.g., 'No players yet') is displayed or the table simply shows zero rows. The pop-up can be closed normally.
