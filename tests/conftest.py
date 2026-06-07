"""
Pytest Configuration and Fixtures
Provides test fixtures for database, players, and games
"""

import pytest
from datetime import datetime, timedelta
from mongomock import MongoClient


@pytest.fixture
def mock_db():
    """Create a mock MongoDB database for testing"""
    client = MongoClient()
    db = client.hockey_agent_test
    yield db
    client.close()


@pytest.fixture
def sample_players(mock_db):
    """Insert sample players into test database"""
    players = [
        {
            "name": "Test Goalie", "number": 1, "position": "Goalie",
            "age": 28, "status": "veteran", "available": True,
            "goals": 0, "assists": 2, "games_played": 10,
            "avg_ice_time": 60.0, "wins": 6, "losses": 4,
            "gaa": 2.5, "save_pct": 0.915, "shutouts": 1,
            "shots_against": 250, "saves": 229
        },
        {
            "name": "Test Forward", "number": 10, "position": "Forward",
            "age": 25, "status": "regular", "available": True,
            "goals": 15, "assists": 12, "games_played": 10,
            "avg_ice_time": 18.5, "plus_minus": 8, "pim": 6,
            "shots": 75, "shooting_pct": 20.0, "hits": 20, "faceoff_pct": 52.0
        },
        {
            "name": "Test Defender", "number": 4, "position": "Defense",
            "age": 29, "status": "veteran", "available": True,
            "goals": 3, "assists": 10, "games_played": 10,
            "avg_ice_time": 22.0, "plus_minus": 6, "pim": 14,
            "shots": 40, "blocked_shots": 25, "hits": 35
        },
        {
            "name": "Young Forward", "number": 91, "position": "Forward",
            "age": 19, "status": "developing", "available": True,
            "goals": 2, "assists": 3, "games_played": 8,
            "avg_ice_time": 8.5, "plus_minus": -2, "pim": 4,
            "shots": 20, "shooting_pct": 10.0, "hits": 10, "faceoff_pct": 45.0
        },
        {
            "name": "Injured Player", "number": 23, "position": "Forward",
            "age": 27, "status": "regular", "available": False,
            "unavailable_reason": "Knee injury",
            "goals": 10, "assists": 8, "games_played": 8,
            "avg_ice_time": 16.0, "plus_minus": 4, "pim": 8,
            "shots": 60, "shooting_pct": 16.7, "hits": 15, "faceoff_pct": 50.0
        }
    ]
    mock_db.players.insert_many(players)
    return players


@pytest.fixture
def sample_games(mock_db):
    """Insert sample games into test database"""
    today = datetime.now()
    games = [
        {
            "date": today - timedelta(days=7),
            "opponent": "Test Eagles",
            "home": True,
            "score_us": 4,
            "score_them": 2,
            "result": "W",  # Regular win (3 pts)
            "scorers": ["Test Forward", "Test Forward", "Test Defender", "Young Forward"],
            "notes": "Good team performance"
        },
        {
            "date": today - timedelta(days=14),
            "opponent": "Test Bears",
            "home": False,
            "score_us": 3,
            "score_them": 4,
            "result": "OTL",  # OT/SO loss (1 pt)
            "scorers": ["Test Forward", "Test Forward", "Test Defender"],
            "notes": "Lost in shootout"
        },
        {
            "date": today - timedelta(days=21),
            "opponent": "Test Lions",
            "home": True,
            "score_us": 2,
            "score_them": 1,
            "result": "OTW",  # OT/SO win (2 pts)
            "scorers": ["Test Forward", "Test Defender"],
            "notes": "Won in overtime"
        },
        {
            "date": today - timedelta(days=28),
            "opponent": "Test Wolves",
            "home": False,
            "score_us": 1,
            "score_them": 5,
            "result": "L",  # Regular loss (0 pts)
            "scorers": ["Young Forward"],
            "notes": "Bad game"
        }
    ]
    mock_db.games.insert_many(games)
    return games


@pytest.fixture
def sample_scheduled_games(mock_db):
    """Insert sample scheduled games into test database"""
    today = datetime.now()
    games = [
        {
            "date": today + timedelta(days=5),
            "opponent": "Future Team A",
            "home": True,
            "time": "19:00",
            "location": "Home Arena",
            "status": "scheduled",
            "notes": "Important game"
        },
        {
            "date": today + timedelta(days=12),
            "opponent": "Future Team B",
            "home": False,
            "time": "20:30",
            "location": "Away Arena",
            "status": "scheduled",
            "notes": ""
        }
    ]
    result = mock_db.scheduled_games.insert_many(games)
    # Add game IDs for attendance tracking
    for idx, game in enumerate(games):
        game["_id"] = result.inserted_ids[idx]
    return games
