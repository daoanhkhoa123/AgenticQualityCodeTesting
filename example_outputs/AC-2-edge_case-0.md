# Player with negative money (debt) sorts correctly at the bottom of the descending list

- **Story ID:** 1
- **AC ID:** AC-2
- **Category:** edge case
- **Priority:** P1
- **Test Type:** integration

## Description

Verify that when a player has a negative money value (i.e., they are in debt), the descending sort by money correctly places that player at the very bottom of the table, below all players with zero or positive balances, without causing a crash or misordering.

## Preconditions

The game/session has ended and the results table is being displayed. There are at least 3 players: Player A has 1500.00, Player B has 0.00, Player C has -250.00 (debt from a forfeit or penalty).

## Steps

1. Open the results/table view for the completed game session.
2. Observe the ordering of the player rows.
3. Confirm Player A (1500.00) is in row 1.
4. Confirm Player B (0.00) is in row 2.
5. Confirm Player C (-250.00) is in row 3 (last position).
6. Verify no UI errors, blank cells, or NaN values are displayed for Player C.

## Expected Result

The player with negative money appears last in the table. Players with money 0 appear before them. The sort does not throw an error or skip the negative-valued player.
