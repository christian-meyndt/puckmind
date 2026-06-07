"""
Test Attendance Tracking
Tests confirming/declining attendance, roster status
"""

import pytest
from src.attendance import (
    set_attendance,
    get_attendance_for_game,
    get_roster_status
)


def test_set_attendance_confirmed(mock_db, sample_players, sample_scheduled_games):
    """Test confirming player attendance"""
    game_id = str(sample_scheduled_games[0]["_id"])

    result = set_attendance(mock_db, game_id, "Test Forward", "confirmed")

    assert result["status"] == "success"
    assert "Test Forward" in result["message"]
    assert "✅" in result["message"]


def test_set_attendance_declined(mock_db, sample_players, sample_scheduled_games):
    """Test declining player attendance"""
    game_id = str(sample_scheduled_games[0]["_id"])

    result = set_attendance(mock_db, game_id, "Test Forward", "declined", "Injured")

    assert result["status"] == "success"
    assert "❌" in result["message"]

    # Verify notes saved
    record = mock_db.game_attendance.find_one({"game_id": game_id, "player_name": "Test Forward"})
    assert record["notes"] == "Injured"


def test_set_attendance_invalid_player(mock_db, sample_scheduled_games):
    """Test setting attendance for non-existent player"""
    game_id = str(sample_scheduled_games[0]["_id"])

    result = set_attendance(mock_db, game_id, "Non Existent", "confirmed")

    assert result["status"] == "error"


def test_set_attendance_invalid_game(mock_db, sample_players):
    """Test setting attendance for non-existent game"""
    result = set_attendance(mock_db, "invalid_game_id", "Test Forward", "confirmed")

    assert result["status"] == "error"


def test_get_attendance_for_game(mock_db, sample_players, sample_scheduled_games):
    """Test getting attendance breakdown for a game"""
    game_id = str(sample_scheduled_games[0]["_id"])

    # Confirm some players
    set_attendance(mock_db, game_id, "Test Forward", "confirmed")
    set_attendance(mock_db, game_id, "Test Defender", "declined")

    result = get_attendance_for_game(mock_db, game_id)

    assert result["status"] == "success"
    assert len(result["confirmed"]) >= 1
    assert len(result["declined"]) >= 1
    assert len(result["pending"]) >= 1

    # Check Test Forward is in confirmed
    confirmed_names = [p["name"] for p in result["confirmed"]]
    assert "Test Forward" in confirmed_names

    # Check Test Defender is in declined
    declined_names = [p["name"] for p in result["declined"]]
    assert "Test Defender" in declined_names


def test_get_roster_status_warnings(mock_db, sample_players, sample_scheduled_games):
    """Test that roster status generates warnings for insufficient players"""
    game_id = str(sample_scheduled_games[0]["_id"])

    # Decline most players
    set_attendance(mock_db, game_id, "Test Forward", "declined")
    set_attendance(mock_db, game_id, "Test Defender", "declined")

    result = get_roster_status(mock_db, game_id)

    assert result["status"] == "success"
    # Should have warnings about low player count
    assert len(result["warnings"]) > 0 or len(result["alerts"]) > 0


def test_attendance_upsert(mock_db, sample_players, sample_scheduled_games):
    """Test that attendance updates existing records (upsert)"""
    game_id = str(sample_scheduled_games[0]["_id"])

    # Confirm first
    set_attendance(mock_db, game_id, "Test Forward", "confirmed")

    # Change to declined
    set_attendance(mock_db, game_id, "Test Forward", "declined", "Changed mind")

    # Should only have 1 record
    count = mock_db.game_attendance.count_documents({
        "game_id": game_id,
        "player_name": "Test Forward"
    })
    assert count == 1

    # Should be declined now
    record = mock_db.game_attendance.find_one({
        "game_id": game_id,
        "player_name": "Test Forward"
    })
    assert record["status"] == "declined"
    assert record["notes"] == "Changed mind"
