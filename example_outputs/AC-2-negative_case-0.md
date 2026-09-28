# Players with identical money values maintain a stable and consistent order in the descending-sorted table

- **Story ID:** 1
- **AC ID:** AC-2
- **Category:** negative case
- **Priority:** P1
- **Test Type:** unit

## Description

Verify that when two or more players share the exact same money value, the table still displays them in a stable, deterministic order (not shuffled or undefined) while the overall table remains sorted in descending order by money.

## Preconditions

The players table contains at least three players, where two of them have the identical money value (e.g., Player A: $5,000, Player B: $5,000, Player C: $10,000).

## Steps

1. Load the players table with the following data: Player A (money: $5,000), Player B (money: $5,000), Player C (money: $10,000).
2. Trigger the sort operation (or observe the table render, which applies the descending sort by money).
3. Observe the order of rows in the table.
4. Refresh or re-trigger the sort and observe the order again.

## Expected Result

The table displays all players in descending order by money. Players with equal money values appear in a stable, consistent order (e.g., insertion order or a defined tiebreaker such as player name alphabetically). No error, crash, or random reordering occurs. The overall descending order is preserved for all other players.
