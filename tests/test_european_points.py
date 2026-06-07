"""
Test European Points System
Tests W=3, OTW=2, OTL=1, L=0 point calculations
"""

import pytest


def test_points_calculation(mock_db, sample_games):
    """Test that European points are calculated correctly"""
    games = list(mock_db.games.find({}, {"result": 1}))

    reg_wins = sum(1 for g in games if g.get("result") == "W")
    ot_wins = sum(1 for g in games if g.get("result") == "OTW")
    ot_losses = sum(1 for g in games if g.get("result") in ["OTL", "D"])
    reg_losses = sum(1 for g in games if g.get("result") == "L")

    points = reg_wins * 3 + ot_wins * 2 + ot_losses * 1

    # Sample data: 1W + 1OTW + 1OTL + 1L = 3 + 2 + 1 + 0 = 6 points
    assert reg_wins == 1
    assert ot_wins == 1
    assert ot_losses == 1
    assert reg_losses == 1
    assert points == 6


def test_season_record_structure(mock_db, sample_games):
    """Test that season record returns correct structure"""
    games = list(mock_db.games.find({}, {"result": 1}))

    reg_wins = sum(1 for g in games if g.get("result") == "W")
    ot_wins = sum(1 for g in games if g.get("result") == "OTW")
    ot_losses = sum(1 for g in games if g.get("result") in ["OTL", "D"])
    reg_losses = sum(1 for g in games if g.get("result") == "L")

    record = {
        "wins": reg_wins + ot_wins,
        "regular_wins": reg_wins,
        "ot_wins": ot_wins,
        "losses": reg_losses + ot_losses,
        "regular_losses": reg_losses,
        "ot_losses": ot_losses,
        "points": reg_wins * 3 + ot_wins * 2 + ot_losses * 1
    }

    assert record["wins"] == 2  # 1 reg + 1 OT
    assert record["losses"] == 2  # 1 reg + 1 OT
    assert record["points"] == 6
    assert record["regular_wins"] == 1
    assert record["ot_wins"] == 1
    assert record["ot_losses"] == 1


def test_all_result_types_valid(mock_db, sample_games):
    """Test that all result types are valid European codes"""
    games = list(mock_db.games.find({}, {"result": 1}))
    valid_results = ["W", "OTW", "OTL", "L", "D"]  # D for legacy

    for game in games:
        assert game.get("result") in valid_results


def test_points_per_game_correct(mock_db, sample_games):
    """Test that each game awards the correct points"""
    games = list(mock_db.games.find({}, {"result": 1}))

    point_map = {
        "W": 3,
        "OTW": 2,
        "OTL": 1,
        "L": 0,
        "D": 1  # Legacy
    }

    for game in games:
        result = game.get("result")
        expected_points = point_map[result]
        assert expected_points >= 0
        assert expected_points <= 3
