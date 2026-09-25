## Play a full round of Blackjack: bet, hit, stand, and let the dealer respond

**Story description:** As a player, I want to pay a play fee to start a round, draw ("hit") cards to improve my hand, and then "stand" to let the dealer play its turn automatically, so that I can play a complete hand of Blackjack against the house.

**Application technical description:** `game_start()` deducts a fixed `PLAY_FEE` (100) from the player's balance (blocking the round with a message if funds are insufficient), deals 2 cards to both the player and dealer hands from a fresh `Deck()`. The "Hit Card" button calls `hit_deck(deck)` to draw one more card (up to a 5-card hand limit) and updates the displayed score. The "Stand" button triggers `bot_hit()`, which plays the dealer automatically: always hits below a score of 16, never hits at 21+, and hits probabilistically in between (chance = `(21 - score) / 13`), before revealing all cards and resolving the round.

**Test description:** Start a round with sufficient funds and confirm the fee is deducted and both hands get 2 cards; attempt to start with insufficient funds and confirm it's blocked with a message. Hit several times and confirm cards are added and the score updates, up to the 5-card limit. Stand and confirm the dealer draws according to its strategy, then all cards are revealed and Hit/Stand become disabled.

**Acceptance criteria:**

- Starting a round with sufficient funds deducts exactly 100 and deals 2 cards to each hand; insufficient funds blocks the round with an informative message and deducts nothing.
- Each "Hit Card" click adds exactly one new card (without replacement) and updates the displayed score, up to a maximum of 5 cards.
- Clicking "Stand" runs the dealer's automatic turn, then reveals both hands and disables further hitting/standing until the next round.
- The dealer always hits below score 16, never hits at score 21 or above, and hits only probabilistically between 16 and 20.
