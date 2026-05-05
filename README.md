# LocalChess

A local-network multiplayer gaming platform featuring two games:

- **Chess Arena** — Human vs Human or Human vs AI (Stockfish) chess with clocks, spectators, move history, and jokers.
- **Property Tycoon** — An original Monopoly-inspired board game (French language, original content) supporting 2–6 players.

Both games run in a single Flask + SocketIO server designed to be hosted on a LAN so anyone on the same network can join from a browser.

---

## Features

### Chess Arena
- Human vs Human (HvH) with matchmaking lobby
- Human vs AI (HvA) with 10 difficulty levels (1–2 random, 3–6 Stockfish depth, 7–10 Stockfish time)
- Increment clocks (configurable base time + increment per move)
- Move history with SAN notation
- 3 jokers per game (undo last move)
- Spectator mode
- Rematch system (colour swap)
- Leaderboard (wins / losses / draws persisted in SQLite)
- PGN export of completed games

### Property Tycoon
- 2–6 players on a 40-space board with original French names
- Full property purchase, house/hotel building, mortgage/unmortgage
- Chance & Community Chest card decks (shuffled, full deck)
- Jail mechanics (doubles to escape, fine, or Jail-Free card)
- Trade system between players
- Bankruptcy with property transfer
- Game result persisted in SQLite

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+ · Flask · Flask-SocketIO |
| Chess engine | python-chess · Stockfish (optional) |
| Frontend | Vanilla JS · Socket.IO client |
| Database | SQLite (via `sqlite3` stdlib) |
| Tests | pytest |

---

## Requirements

```
flask>=3.0
flask-socketio>=5.3
python-chess>=1.10
pytest>=7.0
```

Install with:

```bash
pip install -r requirements.txt
```

Stockfish is optional but required for AI difficulty levels 3–10. Install it via your package manager (e.g. `sudo apt install stockfish`) or set the `STOCKFISH_PATH` environment variable to point to a custom binary.

---

## Running the server

```bash
python app.py
```

The server starts on `http://0.0.0.0:5000`. The home page displays the best LAN IP address so other devices on the same network can connect.

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `chess_arena_dev_key_change_me_in_prod` | Flask session secret — **change in production** |
| `STOCKFISH_PATH` | `/usr/games/stockfish` | Path to Stockfish binary |

---

## Running the tests

```bash
pytest tests/
```

Tests cover the Property Tycoon game logic in `monopoly.py` (pure Python, no server required).

---

## Project structure

```
LocalChess/
├── app.py               # Flask app, SocketIO events, routes
├── monopoly.py          # Property Tycoon game logic
├── requirements.txt
├── chess_arena.db       # SQLite database (auto-created on first run)
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── templates/
│   ├── login.html
│   ├── index.html          # Chess Arena
│   ├── monopoly_lobby.html # Property Tycoon lobby
│   └── monopoly.html       # Property Tycoon game
└── tests/
    └── test_monopoly.py
```

---

## Routes

| Method | Path | Description |
|---|---|---|
| GET | `/` | Chess Arena lobby (requires login) |
| GET/POST | `/login` | Username login |
| GET | `/logout` | Clear session |
| GET | `/api/leaderboard` | JSON leaderboard (top 10) |
| GET | `/api/pgn/<room_id>` | Download PGN for a chess game |
| GET | `/tycoon` | Property Tycoon lobby |
| GET | `/tycoon/game/<room_id>` | Property Tycoon game room |

---

## Socket events (Chess)

| Event (client→server) | Description |
|---|---|
| `create_room` | Create a new chess game room |
| `join_room` | Join or spectate an existing room |
| `move` | Submit a chess move (UCI format) |
| `abort_resign` | Abort (< 2 moves) or resign |
| `use_joker` | Undo last move (max 3 per game) |
| `chat_msg` | Send a chat message |
| `request_rematch` / `accept_rematch` | Request or accept a rematch |
| `get_public_rooms` | List open HvH rooms |

## Socket events (Property Tycoon)

| Event (client→server) | Description |
|---|---|
| `mono_create` | Create a new Property Tycoon room |
| `mono_join` | Join or reconnect to a room |
| `mono_start` | Start the game (host only) |
| `mono_roll` | Roll the dice |
| `mono_buy` | Buy the current property |
| `mono_build` | Build a house/hotel |
| `mono_sell_house` | Sell a house/hotel |
| `mono_mortgage` / `mono_unmortgage` | Mortgage or unmortgage a property |
| `mono_pay_jail` | Pay 50 € jail fine |
| `mono_use_jail_free` | Use Jail-Free card |
| `mono_end_turn` | End your turn |
| `mono_trade_offer` | Propose a trade |
| `mono_trade_respond` | Accept or decline a trade |
| `mono_chat` | Send a chat message |
| `mono_get_state` | Request full game state |
| `mono_get_rooms` | List open lobby rooms |
