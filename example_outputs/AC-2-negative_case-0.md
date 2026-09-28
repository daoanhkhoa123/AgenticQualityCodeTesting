# Player table is NOT sorted in descending order by money — displayed in ascending order (lowest first)

- **Story ID:** 1
- **AC ID:** AC-2
- **Category:** negative case
- **Priority:** P1
- **Test Type:** unit

## Description

A negative scenario where the player table fails to meet the sorting requirement by presenting players in ascending order of money (lowest money at the top, highest at the bottom), which is the exact opposite of the required descending order.

## Steps

1. Precondition: A player table exists with 5+ players having distinct money values (e.g., 500, 1200, 300, 4500, 800).
2. Step 1: The player table is rendered/displayed.
3. Step 2: Observe the order of rows from top to bottom.
4. Step 3: Verify that the money column values are in DESCENDING order (highest → lowest).
5. Assertion: The first row should have the HIGHEST money value (4500), and the last row should have the LOWEST money value (300).

## Expected Result

Per acceptance criteria, the table MUST be sorted in descending order by money (highest money first, lowest last). In this negative case, the table is in ascending order, violating the criterion.
