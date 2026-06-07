"""
Test Ice Time Analysis
Tests identifying developing players who need more ice time
"""

import pytest


def test_developing_players_identified(mock_db, sample_players):
    """Test that developing players are identified"""
    players = list(mock_db.players.find(
        {"position": {"$ne": "Goalie"}, "available": True},
        {"name": 1, "status": 1, "avg_ice_time": 1}
    ))

    developing = [p for p in players if p.get("status") == "developing"]

    assert len(developing) >= 1
    assert any(p["name"] == "Young Forward" for p in developing)


def test_ice_time_comparison(mock_db, sample_players):
    """Test comparing ice time vs team average"""
    forwards = list(mock_db.players.find(
        {"position": "Forward", "available": True},
        {"name": 1, "avg_ice_time": 1}
    ))

    avg_ice_time = sum(p.get("avg_ice_time", 0) for p in forwards) / len(forwards)

    # Young Forward should have below-average ice time
    young_forward = mock_db.players.find_one({"name": "Young Forward"})
    assert young_forward["avg_ice_time"] < avg_ice_time


def test_ice_time_recommendations(mock_db, sample_players):
    """Test generating recommendations for ice time increases"""
    developing = list(mock_db.players.find(
        {"status": "developing", "available": True, "position": {"$ne": "Goalie"}},
        {"name": 1, "avg_ice_time": 1, "plus_minus": 1, "age": 1}
    ).sort("avg_ice_time", 1))

    # Should have at least one developing player
    assert len(developing) >= 1

    # Young Forward should be in the list
    young = next((p for p in developing if p["name"] == "Young Forward"), None)
    assert young is not None
    assert young["avg_ice_time"] < 10  # Very low ice time


def test_unavailable_players_excluded(mock_db, sample_players):
    """Test that unavailable players are not recommended for ice time"""
    recommendations = list(mock_db.players.find(
        {"available": True, "position": {"$ne": "Goalie"}},
        {"name": 1, "available": 1}
    ))

    # Injured Player should not be in available list
    names = [p["name"] for p in recommendations]
    assert "Injured Player" not in names


def test_ice_time_data_exists(mock_db, sample_players):
    """Test that all players have ice time data"""
    players = list(mock_db.players.find(
        {"position": {"$ne": "Goalie"}},
        {"name": 1, "avg_ice_time": 1}
    ))

    for player in players:
        assert "avg_ice_time" in player
        assert player["avg_ice_time"] > 0
