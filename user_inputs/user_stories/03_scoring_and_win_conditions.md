## Have my hand scored correctly and the round winner determined fairly

**Story description:** As a player, I want my hand's score to be calculated correctly (including special cases like aces, blackjack, and a full 5-card hand), and the round's winner and payout determined fairly based on that score, so that I can trust the outcome of every round.

**Application technical description:** `Hand.score` sums card ranks (face cards = 10; aces add 11 each, then downgrade to 1 one at a time if the total exceeds 21). `checkmate()` detects an immediate "blackjack" (ace + 10-value card) or "double blackjack" (two aces) right after the initial 2-card deal. `royalcheck()` declares an immediate winner if a hand fills all 5 card slots with a score <= 21. Otherwise, `game_restart()` compares final scores: ties favor the dealer, valid (16–21) scores beat busted or under-16 scores, and among two valid or two busted/under-16 hands the better score wins. `printwinner()` credits the winner with `PLAY_FEE * 2` (200) if the player wins, persists the updated balance to their save file, and displays a "won with ace" or "won!" message.

**Test description:** Test hands covering: Ace+King (should score 21, not 31); multiple aces adjusting from 11 to 1 as needed; an Ace+10-value starting hand (immediate blackjack win); two-ace starting hand (double blackjack); a 5-card hand at or under 21 (immediate royal win); a tie, a bust-vs-valid, and an under-16-vs-valid comparison. Confirm the correct winner is chosen in each case and that a win credits exactly 200 to the player's balance.

**Acceptance criteria:**

- Aces are automatically counted as 11 or downgraded to 1 so a hand is never falsely reported as busted.
- A starting hand of Ace + 10/J/Q/K is immediately declared a "blackjack" win; two starting aces are declared a "double blackjack" win.
- A 5-card hand with a score of 21 or less is immediately declared the winner ("royal"), without needing to compare to the opponent's score.
- When neither applies, ties are awarded to the dealer, and a valid (16–21) score always beats a busted or under-16 score.
- Winning a round credits the player with 200 (net +100 after the 100 entry fee) and updates/saves their balance; losing forfeits the entry fee.
- A clear on-screen message announces the winner ("<name> won with ace" for blackjack, "<name> won!" otherwise) for about 2 seconds.
