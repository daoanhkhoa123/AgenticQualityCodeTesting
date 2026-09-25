## Keep my money balance and profile saved across sessions

**Story description:** As a returning player, I want my money balance to be saved automatically and reloaded the next time I play, and I want to be able to browse and load a previously saved player profile, so that my progress persists between sessions.

**Application technical description:** On startup, the game reads `saves/<player_name>.txt` (line 1 = balance, defaulting to 500 if it reads as 0; line 2 = `maxMoney`) and initializes `Hand.money`/`Hand.maxMoney` from it. `Hand.money` is a validated property that raises `ValueError` for non-integer or negative assignments. Balance changes (paying the play fee, winning a round) are written back to the save file. The "Load" screen reads `load/load.txt` (a list of `name money` pairs) and lets the player pick a profile via `LineByLineLoad`, though applying the selection (`apply_change()`) is currently a no-op stub that doesn't yet swap the active profile into the running game.

**Test description:** Start the app with a save file containing a nonzero balance and confirm it loads correctly; play rounds and confirm the balance and save file update after wins and losses; open the Load screen, select a different profile, and check whether the active game session actually switches to it.

**Acceptance criteria:**

- On startup, the player's balance and max balance load from their save file; a missing or zero balance defaults to 500.
- The displayed balance always matches the player's actual `Hand.money`, updating immediately after fee payments and payouts.
- Assigning a non-integer or negative value to the balance is rejected rather than silently corrupting state.
- The Load screen lists every player found in `load/load.txt` and lets the user select one.
- Selecting and applying a saved profile actually switches the active game session to that profile's name/money — currently a known gap, since `apply_change()` is a stub.
