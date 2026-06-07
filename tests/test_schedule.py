"""
Test Schedule Management
Tests adding games, getting upcoming games, calendar generation
"""

import pytest
from datetime import datetime, timedelta
from src.schedule import (
    get_upcoming_games,
    get_next_game,
    cancel_scheduled_game,
    generate_ics_calendar
)


def test_get_upcoming_games(mock_db, sample_scheduled_games):
    """Test getting upcoming games returns correct count"""
    upcoming = get_upcoming_games(mock_db, limit=10)
    assert len(upcoming) == 2
    assert all("game_id" in g for g in upcoming)
    assert all("days_until" in g for g in upcoming)


def test_get_upcoming_games_sorted(mock_db, sample_scheduled_games):
    """Test upcoming games are sorted by date"""
    upcoming = get_upcoming_games(mock_db, limit=10)
    dates = [g["date"] for g in upcoming]
    assert dates == sorted(dates)


def test_get_next_game(mock_db, sample_scheduled_games):
    """Test getting next game returns the closest one"""
    next_game = get_next_game(mock_db)
    assert next_game is not None
    assert next_game["opponent"] == "Future Team A"
    assert next_game["days_until"] == 5


def test_days_until_calculation(mock_db, sample_scheduled_games):
    """Test that days_until is calculated correctly (date-based)"""
    upcoming = get_upcoming_games(mock_db, limit=10)

    for game in upcoming:
        today = datetime.now().date()
        game_date = game["date"].date()
        expected_days = (game_date - today).days
        assert game["days_until"] == expected_days


def test_cancel_scheduled_game(mock_db, sample_scheduled_games):
    """Test canceling a scheduled game"""
    game_id = str(sample_scheduled_games[0]["_id"])
    result = cancel_scheduled_game(mock_db, game_id, "Bad weather")

    assert result["status"] == "success"

    # Verify game is marked as cancelled
    game = mock_db.scheduled_games.find_one({"_id": sample_scheduled_games[0]["_id"]})
    assert game["status"] == "cancelled"
    assert game["cancellation_reason"] == "Bad weather"


def test_cancel_invalid_game_id(mock_db):
    """Test canceling with invalid game ID returns error"""
    result = cancel_scheduled_game(mock_db, "invalid_id", "Test")
    assert result["status"] == "error"


def test_generate_ics_calendar(mock_db, sample_scheduled_games):
    """Test generating .ics calendar format"""
    upcoming = get_upcoming_games(mock_db, limit=10)
    ics = generate_ics_calendar(upcoming, "Test Team")

    assert "BEGIN:VCALENDAR" in ics
    assert "END:VCALENDAR" in ics
    assert "Future Team A" in ics
    assert "Future Team B" in ics
    assert "BEGIN:VEVENT" in ics


def test_cancelled_games_not_in_upcoming(mock_db, sample_scheduled_games):
    """Test that cancelled games don't appear in upcoming"""
    game_id = str(sample_scheduled_games[0]["_id"])
    cancel_scheduled_game(mock_db, game_id, "Test")

    upcoming = get_upcoming_games(mock_db, limit=10)
    assert len(upcoming) == 1  # Only 1 remaining
    assert upcoming[0]["opponent"] == "Future Team B"
