## Navigate the main menu to start playing or explore other features

**Story description:** As a player, I want to launch the application and use a main menu to start a game, view a tutorial, check the leaderboard, load a saved profile, view "About Us," or exit, so that I can access every part of the app from one starting screen.

**Application technical description:** `load_home()` builds the main menu window with a background image and six buttons: `Play` (calls `playgame()`), `Tutorial` (calls `tutorial()`), `Leaderboard` (calls `show_leaderboard()`), `Load` (calls `load_player()`), `Exit` (bound to `root.quit`), and `About Us` (calls `about_us()`). Note: `playgame()` and `tutorial()` are currently stub functions that don't yet perform their intended action (starting gameplay / showing rules).

**Test description:** Launch the app, verify all six buttons render and are clickable, then click each one in turn and confirm it produces the expected result (game starts, tutorial content shown, leaderboard opens, load screen opens, app closes, about-us content shown).

**Acceptance criteria:**

- The main menu opens with a background image, title, and all six buttons visible and enabled.
- Clicking "Exit" closes the application.
- Clicking "Leaderboard," "Load," and "About Us" each open their respective screens without error.
- Clicking "Play" starts an actual game session (deals cards, enables Hit/Stand) — currently a known gap, as `playgame()` is a stub.
- Clicking "Tutorial" displays rules/instructions — currently a known gap, as `tutorial()` is a stub.
