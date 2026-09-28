# Player table displays players in descending order by money

- **Story ID:** 1
- **AC ID:** AC-2
- **Category:** happy path
- **Priority:** P0
- **Test Type:** unit

## Description

Verify that when the player table is rendered, the rows are ordered from the player with the highest money value to the player with the lowest money value.

## Steps

1. Step 1: Ensure a dataset of 5 players exists with distinct money values: Player A ($10,000), Player B ($7,500), Player C ($3,200), Player D ($1,800), Player E ($500).
2. Step 2: Load the player table component/view.
3. Step 3: Observe the order of rows in the rendered table.
4. Step 4: Assert that row 1 corresponds to Player A ($10,000).
5. Step 5: Assert that row 2 corresponds to Player B ($7,500).
6. Step 6: Assert that row 3 corresponds to Player C ($3,200).
7. Step 7: Assert that row 4 corresponds to Player D ($1,800).
8. Step 8: Assert that row 5 corresponds to Player E ($500).

## Expected Result

The first row contains the player with the highest money amount, and each subsequent row contains a player with a strictly lower (or equal) money amount, resulting in a non-increasing sequence of money values from top to bottom.
