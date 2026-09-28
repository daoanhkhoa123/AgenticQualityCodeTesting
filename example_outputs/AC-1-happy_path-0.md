# Clicking the Leaderboard button from the main menu opens a popup displaying a player table

- **Story ID:** 1
- **AC ID:** AC-1
- **Category:** happy path
- **Priority:** P1
- **Test Type:** integration

## Description

Validates the end-to-end happy path: a user on the main menu clicks the 'Leaderboard' button and is presented with a popup window containing a properly rendered table of players.

## Preconditions

The user is on the main menu screen and at least one player entry exists in the leaderboard data source.

## Steps

1. Step 1: Navigate to the main menu screen where the 'Leaderboard' button is visible.
2. Step 2: Click the 'Leaderboard' button.
3. Step 3: Observe the UI for the appearance of a popup/modal window.
4. Step 4: Verify the popup window contains a table element.
5. Step 5: Verify the table is populated with player rows (name, score, or equivalent columns).
6. Step 6: Verify the popup is displayed above/over the main menu content (overlay behavior).

## Expected Result

A popup window opens over the main menu and displays a table with at least one column per player attribute (e.g., rank, name, score). The table is visible, readable, and populated with player entries.
