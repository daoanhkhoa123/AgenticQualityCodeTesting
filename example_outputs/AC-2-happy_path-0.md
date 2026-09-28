# Player table is sorted in descending order by money (highest first, lowest last)

- **Story ID:** 1
- **AC ID:** AC-2
- **Category:** happy path
- **Priority:** P1
- **Test Type:** unit

## Description

When multiple players are present in the player table, the table renders them in descending order of their money value so that the richest player appears at the top and the poorest at the bottom.

## Steps

1. Arrange: Create a player table with 5 players having distinct money values: Player A = 1200, Player B = 4500, Player C = 300, Player D = 7800, Player E = 1500
2. Act: Render / load the player table
3. Assert: The table row order (top to bottom) is: Player D (7800), Player B (4500), Player E (1500), Player A (1200), Player C (300)
4. Assert: The 'money' column values in each row, read top to bottom, form a strictly non-increasing sequence
5. Assert: The player with the highest money (7800) occupies row index 0 (first row)
6. Assert: The player with the lowest money (300) occupies row index 4 (last row)

## Expected Result

The player table displays players in descending order by the 'money' column: highest money value first, lowest money value last.
