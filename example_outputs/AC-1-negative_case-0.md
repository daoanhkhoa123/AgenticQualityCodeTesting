# Clicking the Leaderboard button when player data source is unavailable

- **Story ID:** 1
- **AC ID:** AC-1
- **Category:** negative case
- **Priority:** P1
- **Test Type:** unit

## Description

When the user clicks the 'Leaderboard' button from the main menu but the underlying player data service is unreachable or returns an error (e.g., 500 status, timeout, or null response), the system should NOT crash and should display an appropriate error message or empty state within the pop-up window instead of a broken table or blank screen.

## Preconditions

The user is on the main menu screen. The backend player data service is configured to return a 500 Internal Server Error (or equivalent failure) for the leaderboard query.

## Steps

1. Navigate to the main menu screen
2. Simulate the player data service returning a 500 error / timeout for the leaderboard API endpoint
3. Click the 'Leaderboard' button
4. Observe the pop-up window behavior
5. Check the browser console for unhandled exceptions

## Expected Result

The pop-up window opens but displays a user-friendly error message (e.g., 'Unable to load leaderboard. Please try again later.') rather than an empty/broken table or an unhandled exception. No uncaught JavaScript errors appear in the console.
