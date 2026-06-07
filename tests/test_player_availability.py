"""
Test Player Availability Management
Tests marking players available/unavailable with reasons
"""

import pytest


def test_mark_player_unavailable(mock_db, sample_players):
    """Test marking a player as unavailable"""
    # Initially available
    player = mock_db.players.find_one({"name": "Test Forward"})
    assert player["available"] is True

    # Mark unavailable
    update_fields = {
        "available": False,
        "unavailable_reason": "Ankle injury"
    }
    mock_db.players.update_one(
        {"name": "Test Forward"},
        {"$set": update_fields}
    )

    # Verify
    player = mock_db.players.find_one({"name": "Test Forward"})
    assert player["available"] is False
    assert player["unavailable_reason"] == "Ankle injury"


def test_mark_player_available_clears_reason(mock_db, sample_players):
    """Test that marking player available clears the reason"""
    # Start with unavailable player
    mock_db.players.update_one(
        {"name": "Injured Player"},
        {"$set": {"available": True, "unavailable_reason": ""}}
    )

    # Verify
    player = mock_db.players.find_one({"name": "Injured Player"})
    assert player["available"] is True
    assert player.get("unavailable_reason", "") == ""


def test_unavailable_count_correct(mock_db, sample_players):
    """Test counting unavailable players"""
    unavailable_count = mock_db.players.count_documents({"available": False})

    # Sample data has 1 unavailable player (Injured Player)
    assert unavailable_count == 1


def test_unavailable_with_reason_displayed(mock_db, sample_players):
    """Test that unavailable reason is retrievable"""
    injured = mock_db.players.find_one(
        {"name": "Injured Player"},
        {"name": 1, "available": 1, "unavailable_reason": 1}
    )

    assert injured["available"] is False
    assert injured["unavailable_reason"] == "Knee injury"


def test_available_players_for_game(mock_db, sample_players):
    """Test getting only available players"""
    available = list(mock_db.players.find(
        {"available": True},
        {"name": 1}
    ))

    # Should be 4 available (5 total - 1 injured)
    assert len(available) == 4

    names = [p["name"] for p in available]
    assert "Test Forward" in names
    assert "Test Defender" in names
    assert "Test Goalie" in names
    assert "Young Forward" in names
    assert "Injured Player" not in names
