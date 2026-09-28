# Clicking the Leaderboard button from the main menu opens a pop-up window displaying a table of players

- **Story ID:** 1
- **AC ID:** AC-1
- **Category:** happy path
- **Priority:** P0
- **Test Type:** e2e

## Description

Verify the normal, expected flow: user clicks the Leaderboard button on the main menu and a pop-up window appears showing a table of players with their respective data.

## Preconditions

The application is launched and the main menu screen is fully loaded and visible. The 'Leaderboard' button is present, visible, and enabled on the main menu.

## Steps

1. 1. Confirm the main menu is displayed with the 'Leaderboard' button visible and clickable.
2. 2. Click the 'Leaderboard' button on the main menu.
3. 3. Observe that a pop-up window appears on top of the main menu.
4. 4. Verify the pop-up window contains a table structure (header row and data rows).
5. 5. Verify the table displays player entries (player names and associated scores/ranks).
6. 6. Verify the main menu is still visible behind the pop-up (not replaced or hidden).
7. 7. Optionally, close the pop-up (e.g., click a close button or press Escape) and confirm the main menu is fully visible again.

## Expected Result

A pop-up window opens over the main menu. The pop-up contains a visible table listing players with relevant columns (e.g., rank, player name, score). The table is populated with player data. The main menu remains visible behind the pop-up.
