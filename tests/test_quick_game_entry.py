"""
Test Quick Game Entry - Natural Language Parser
Tests parsing of "Lukas 2G 1A", "hat trick", etc.
"""

import pytest
from src.quick_game_entry import parse_scorers_text, validate_score


def test_parse_simple_scorer():
    """Test parsing 'Player 2G 1A'"""
    result = parse_scorers_text("Test Player 2G 1A")
    assert "Test Player" in result
    assert result["Test Player"]["goals"] == 2
    assert result["Test Player"]["assists"] == 1


def test_parse_hat_trick():
    """Test parsing 'Player hat trick'"""
    result = parse_scorers_text("Test Player hat trick")
    assert "Test Player" in result
    assert result["Test Player"]["goals"] == 3
    assert result["Test Player"]["assists"] == 0


def test_parse_multiple_scorers():
    """Test parsing multiple players separated by comma"""
    result = parse_scorers_text("Player A 2G 1A, Player B 1G, Player C 3A")
    assert len(result) == 3
    assert result["Player A"]["goals"] == 2
    assert result["Player A"]["assists"] == 1
    assert result["Player B"]["goals"] == 1
    assert result["Player B"]["assists"] == 0
    assert result["Player C"]["goals"] == 0
    assert result["Player C"]["assists"] == 3


def test_parse_long_form():
    """Test parsing '2 goals 1 assist' format"""
    result = parse_scorers_text("Test Player 2 goals 1 assist")
    assert "Test Player" in result
    assert result["Test Player"]["goals"] == 2
    assert result["Test Player"]["assists"] == 1


def test_validate_score_correct():
    """Test score validation with correct total"""
    stats = {
        "Player A": {"goals": 2, "assists": 1},
        "Player B": {"goals": 1, "assists": 0}
    }
    is_valid, msg = validate_score(stats, 3)
    assert is_valid is True


def test_validate_score_incorrect():
    """Test score validation with incorrect total"""
    stats = {
        "Player A": {"goals": 2, "assists": 1},
        "Player B": {"goals": 1, "assists": 0}
    }
    is_valid, msg = validate_score(stats, 5)
    assert is_valid is False
    assert "3" in msg  # Should mention counted goals
    assert "5" in msg  # Should mention declared score


def test_parse_empty_string():
    """Test parsing empty string returns empty dict"""
    result = parse_scorers_text("")
    assert result == {}


def test_parse_goals_only():
    """Test parsing goals without assists"""
    result = parse_scorers_text("Player A 3G")
    assert result["Player A"]["goals"] == 3
    assert result["Player A"]["assists"] == 0


def test_parse_assists_only():
    """Test parsing assists without goals"""
    result = parse_scorers_text("Player A 2A")
    assert result["Player A"]["goals"] == 0
    assert result["Player A"]["assists"] == 2
