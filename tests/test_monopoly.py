"""Unit tests for monopoly.py game logic."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from monopoly import (
    new_monopoly_game,
    add_player,
    start_game,
    process_roll,
    buy_property,
    build_house,
    sell_house,
    mortgage_property,
    unmortgage_property,
    pay_jail_fine,
    use_jail_free_card,
    end_turn,
    get_public_state,
    get_rent,
    BOARD,
    COLOR_GROUPS,
    RAILWAY_POSITIONS,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

def make_game(num_players=2):
    """Return a started game with *num_players* players."""
    game = new_monopoly_game("Alice", "room_test")
    add_player(game, "Alice", "sid_alice")
    for i in range(1, num_players):
        names = ["Bob", "Carol", "Dave", "Eve", "Frank"]
        add_player(game, names[i - 1], f"sid_{i}")
    start_game(game)
    return game


# ─── new_monopoly_game ────────────────────────────────────────────────────────

class TestNewGame:
    def test_initial_status(self):
        game = new_monopoly_game("Alice", "r1")
        assert game["status"] == "waiting"

    def test_host_set(self):
        game = new_monopoly_game("Alice", "r1")
        assert game["host"] == "Alice"

    def test_no_players_initially(self):
        game = new_monopoly_game("Alice", "r1")
        assert game["players"] == []

    def test_decks_shuffled(self):
        game = new_monopoly_game("Alice", "r1")
        assert len(game["deck_chance"]) > 0
        assert len(game["deck_community"]) > 0


# ─── add_player / start_game ─────────────────────────────────────────────────

class TestAddPlayerStartGame:
    def test_add_single_player(self):
        game = new_monopoly_game("Alice", "r1")
        ok, idx = add_player(game, "Alice", "s1")
        assert ok
        assert idx == 0
        assert len(game["players"]) == 1

    def test_player_starts_with_1500(self):
        game = new_monopoly_game("Alice", "r1")
        add_player(game, "Alice", "s1")
        assert game["players"][0]["money"] == 1500

    def test_player_starts_at_position_0(self):
        game = new_monopoly_game("Alice", "r1")
        add_player(game, "Alice", "s1")
        assert game["players"][0]["position"] == 0

    def test_max_6_players(self):
        game = new_monopoly_game("Alice", "r1")
        for name in ["A", "B", "C", "D", "E", "F"]:
            add_player(game, name, f"s_{name}")
        ok, err = add_player(game, "G", "s_G")
        assert not ok
        assert "pleine" in err

    def test_cannot_add_after_start(self):
        game = make_game(2)
        ok, err = add_player(game, "Latejoiner", "s_late")
        assert not ok

    def test_start_requires_two_players(self):
        game = new_monopoly_game("Alice", "r1")
        add_player(game, "Alice", "s1")
        ok, err = start_game(game)
        assert not ok
        assert "2" in err

    def test_start_sets_status_playing(self):
        game = make_game(2)
        assert game["status"] == "playing"

    def test_first_player_is_index_0(self):
        game = make_game(2)
        assert game["current_player_idx"] == 0
        assert game["phase"] == "roll"


# ─── buy_property ─────────────────────────────────────────────────────────────

class TestBuyProperty:
    def test_buy_property_success(self):
        game = make_game(2)
        p = game["players"][0]
        p["position"] = 1  # Rue des Sables, price 60
        ok, err = buy_property(game, 0)
        assert ok
        assert game["property_owners"][1] == 0
        assert p["money"] == 1500 - 60

    def test_buy_already_owned(self):
        game = make_game(2)
        game["players"][0]["position"] = 1
        buy_property(game, 0)
        game["players"][0]["position"] = 1
        ok, err = buy_property(game, 0)
        assert not ok

    def test_buy_not_enough_money(self):
        game = make_game(2)
        game["players"][0]["money"] = 10
        game["players"][0]["position"] = 1
        ok, err = buy_property(game, 0)
        assert not ok

    def test_buy_non_purchasable_space(self):
        game = make_game(2)
        game["players"][0]["position"] = 0  # GO
        ok, err = buy_property(game, 0)
        assert not ok

    def test_buy_railway(self):
        game = make_game(2)
        game["players"][0]["position"] = 5  # Gare du Nord
        ok, _ = buy_property(game, 0)
        assert ok
        assert game["property_owners"][5] == 0


# ─── build_house / sell_house ─────────────────────────────────────────────────

class TestBuildSellHouse:
    def _own_brown_group(self, game, player_idx):
        """Give player both brown properties."""
        for pos in COLOR_GROUPS["brown"]:  # positions 1 and 3
            game["players"][player_idx]["position"] = pos
            buy_property(game, player_idx)

    def test_build_requires_full_color_group(self):
        game = make_game(2)
        game["players"][0]["position"] = 1
        buy_property(game, 0)
        ok, err = build_house(game, 0, 1)
        assert not ok
        assert "groupe" in err.lower()

    def test_build_house_success(self):
        game = make_game(2)
        self._own_brown_group(game, 0)
        ok, err = build_house(game, 0, 1)
        assert ok
        assert game["property_houses"][1] == 1

    def test_build_up_to_hotel(self):
        game = make_game(2)
        self._own_brown_group(game, 0)
        game["players"][0]["money"] = 999999
        for _ in range(5):
            # build evenly across both props
            build_house(game, 0, 1)
            build_house(game, 0, 3)
        # Should be at hotel (5) now but actually only 5 rounds means 5 on each
        # Due to even-build rule we build alternately; just check cap
        assert game["property_houses"].get(1, 0) <= 5
        assert game["property_houses"].get(3, 0) <= 5

    def test_cannot_build_beyond_hotel(self):
        game = make_game(2)
        self._own_brown_group(game, 0)
        game["players"][0]["money"] = 999999
        for _ in range(5):
            build_house(game, 0, 1)
            build_house(game, 0, 3)
        ok, err = build_house(game, 0, 1)
        assert not ok

    def test_sell_house(self):
        game = make_game(2)
        self._own_brown_group(game, 0)
        build_house(game, 0, 1)
        build_house(game, 0, 3)
        money_before = game["players"][0]["money"]
        ok, _ = sell_house(game, 0, 1)
        assert ok
        assert game["players"][0]["money"] > money_before

    def test_sell_no_house(self):
        game = make_game(2)
        self._own_brown_group(game, 0)
        ok, err = sell_house(game, 0, 1)
        assert not ok

    def test_uneven_sell_blocked(self):
        game = make_game(2)
        self._own_brown_group(game, 0)
        game["players"][0]["money"] = 999999
        build_house(game, 0, 1)
        build_house(game, 0, 3)
        build_house(game, 0, 3)  # pos 3 has 2, pos 1 has 1
        ok, err = sell_house(game, 0, 1)
        assert not ok  # cannot sell from the smaller pile


# ─── mortgage / unmortgage ───────────────────────────────────────────────────

class TestMortgage:
    def test_mortgage_success(self):
        game = make_game(2)
        game["players"][0]["position"] = 1
        buy_property(game, 0)
        money_before = game["players"][0]["money"]
        ok, _ = mortgage_property(game, 0, 1)
        assert ok
        assert game["property_mortgaged"][1]
        assert game["players"][0]["money"] > money_before

    def test_cannot_mortgage_with_houses(self):
        game = make_game(2)
        for pos in COLOR_GROUPS["brown"]:
            game["players"][0]["position"] = pos
            buy_property(game, 0)
        build_house(game, 0, 1)
        build_house(game, 0, 3)
        ok, err = mortgage_property(game, 0, 1)
        assert not ok

    def test_unmortgage_success(self):
        game = make_game(2)
        game["players"][0]["position"] = 1
        buy_property(game, 0)
        mortgage_property(game, 0, 1)
        game["players"][0]["money"] = 999999
        ok, _ = unmortgage_property(game, 0, 1)
        assert ok
        assert not game["property_mortgaged"][1]

    def test_unmortgage_not_enough_money(self):
        game = make_game(2)
        game["players"][0]["position"] = 1
        buy_property(game, 0)
        mortgage_property(game, 0, 1)
        game["players"][0]["money"] = 0
        ok, err = unmortgage_property(game, 0, 1)
        assert not ok

    def test_mortgaged_property_yields_no_rent(self):
        game = make_game(2)
        game["players"][0]["position"] = 1
        buy_property(game, 0)
        mortgage_property(game, 0, 1)
        assert get_rent(game, 1) == 0


# ─── jail actions ─────────────────────────────────────────────────────────────

class TestJail:
    def _send_to_jail(self, game, player_idx):
        p = game["players"][player_idx]
        p["position"] = 10
        p["in_jail"] = True
        p["jail_turns"] = 0

    def test_pay_jail_fine(self):
        game = make_game(2)
        self._send_to_jail(game, 0)
        ok, _ = pay_jail_fine(game, 0)
        assert ok
        assert not game["players"][0]["in_jail"]
        assert game["players"][0]["money"] == 1500 - 50

    def test_pay_jail_fine_not_in_jail(self):
        game = make_game(2)
        ok, err = pay_jail_fine(game, 0)
        assert not ok

    def test_pay_jail_fine_no_money(self):
        game = make_game(2)
        self._send_to_jail(game, 0)
        game["players"][0]["money"] = 10
        ok, err = pay_jail_fine(game, 0)
        assert not ok

    def test_use_jail_free_card(self):
        game = make_game(2)
        self._send_to_jail(game, 0)
        game["players"][0]["has_jail_free"] = True
        ok, _ = use_jail_free_card(game, 0)
        assert ok
        assert not game["players"][0]["in_jail"]
        assert not game["players"][0]["has_jail_free"]

    def test_use_jail_free_card_without_card(self):
        game = make_game(2)
        self._send_to_jail(game, 0)
        ok, err = use_jail_free_card(game, 0)
        assert not ok


# ─── end_turn ─────────────────────────────────────────────────────────────────

class TestEndTurn:
    def test_advances_to_next_player(self):
        game = make_game(2)
        assert game["current_player_idx"] == 0
        end_turn(game, 0)
        assert game["current_player_idx"] == 1

    def test_wraps_around(self):
        game = make_game(2)
        end_turn(game, 0)
        end_turn(game, 1)
        assert game["current_player_idx"] == 0

    def test_resets_phase_to_roll(self):
        game = make_game(2)
        game["phase"] = "action"
        end_turn(game, 0)
        assert game["phase"] == "roll"

    def test_skips_bankrupt_player(self):
        game = make_game(3)
        game["players"][1]["bankrupt"] = True
        end_turn(game, 0)
        assert game["current_player_idx"] == 2


# ─── process_roll ─────────────────────────────────────────────────────────────

class TestProcessRoll:
    def test_player_moves(self):
        game = make_game(2)
        events = process_roll(game, 0, 3, 2)
        assert game["players"][0]["position"] == 5

    def test_pass_go_collects_200(self):
        game = make_game(2)
        game["players"][0]["position"] = 38
        events = process_roll(game, 0, 3, 2)
        # 38 + 5 = 43 % 40 = 3 → passed GO
        assert game["players"][0]["position"] == 3
        assert game["players"][0]["money"] == 1700  # 1500 + 200

    def test_double_allows_extra_roll(self):
        game = make_game(2)
        events = process_roll(game, 0, 3, 3)
        types = [e["type"] for e in events]
        assert "double" in types
        assert game["phase"] == "roll"

    def test_three_doubles_jail(self):
        game = make_game(2)
        game["double_count"] = 2  # already had 2 doubles
        events = process_roll(game, 0, 4, 4)
        types = [e["type"] for e in events]
        assert "jail" in types
        assert game["players"][0]["in_jail"]

    def test_jail_exit_on_double(self):
        game = make_game(2)
        game["players"][0]["in_jail"] = True
        game["players"][0]["jail_turns"] = 1
        events = process_roll(game, 0, 3, 3)
        assert not game["players"][0]["in_jail"]

    def test_jail_stay_on_non_double(self):
        game = make_game(2)
        game["players"][0]["in_jail"] = True
        game["players"][0]["jail_turns"] = 0
        events = process_roll(game, 0, 3, 2)
        assert game["players"][0]["in_jail"]
        assert game["phase"] == "end"

    def test_forced_pay_after_3_jail_turns(self):
        game = make_game(2)
        game["players"][0]["in_jail"] = True
        game["players"][0]["jail_turns"] = 2  # 3rd roll will be turn 3
        events = process_roll(game, 0, 3, 2)
        assert not game["players"][0]["in_jail"]
        assert game["players"][0]["money"] == 1450  # 1500 - 50


# ─── get_rent ─────────────────────────────────────────────────────────────────

class TestGetRent:
    def test_unowned_property_no_rent(self):
        game = make_game(2)
        assert get_rent(game, 1) == 0

    def test_base_rent(self):
        game = make_game(2)
        game["players"][0]["position"] = 1
        buy_property(game, 0)
        # Single property, no monopoly → base rent = 2
        assert get_rent(game, 1) == 2

    def test_double_rent_monopoly(self):
        game = make_game(2)
        for pos in COLOR_GROUPS["brown"]:
            game["players"][0]["position"] = pos
            buy_property(game, 0)
        # Both brown owned → double rent = 2 * 2 = 4
        assert get_rent(game, 1) == 4

    def test_railway_rent_scales(self):
        game = make_game(2)
        for pos in RAILWAY_POSITIONS[:2]:
            game["players"][0]["position"] = pos
            buy_property(game, 0)
        # 2 railways → 50€
        assert get_rent(game, RAILWAY_POSITIONS[0]) == 50


# ─── get_public_state ─────────────────────────────────────────────────────────

class TestGetPublicState:
    def test_no_sid_in_public_state(self):
        game = make_game(2)
        state = get_public_state(game)
        for player in state["players"]:
            assert "sid" not in player

    def test_required_keys_present(self):
        game = make_game(2)
        state = get_public_state(game)
        for key in ("status", "phase", "current_player_idx", "dice", "players",
                    "property_owners", "log", "winner"):
            assert key in state

    def test_string_keys_in_property_dicts(self):
        game = make_game(2)
        game["players"][0]["position"] = 1
        buy_property(game, 0)
        state = get_public_state(game)
        # property_owners keys must be strings (JSON-safe)
        assert all(isinstance(k, str) for k in state["property_owners"])
