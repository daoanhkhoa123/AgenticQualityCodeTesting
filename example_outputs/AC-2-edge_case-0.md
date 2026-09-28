# All players have identical money values – table still renders in a stable, non-error state

- **Story ID:** 1
- **AC ID:** AC-2
- **Category:** edge case
- **Priority:** P2
- **Test Type:** e2e

## Description

When every player in the table has the exact same money value, the descending sort by money has no natural ordering to apply. The table must still render all players without errors, without dropping rows, and without an uncontrolled or random order that shifts on every re-render.

## Preconditions

The player table component is rendered with at least 3 players, all of whom have the identical money value (e.g., every player's money = 500).

## Steps

1. Set up a mock state where 3 players (Alice, Bob, Carol) each have money = 500.
2. Render the player table component.
3. Observe the order of rows in the table.
4. Trigger a re-render (e.g., dispatch an unrelated state update or resize the container).
5. Observe the order of rows again.

## Expected Result

The table displays all players (none missing, no duplicates), the sort does not throw an error, and the relative order of equal-valued players is deterministic (stable) across re-renders. No console errors or blank table.
