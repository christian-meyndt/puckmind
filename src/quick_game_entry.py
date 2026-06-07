"""
Quick Game Entry - Natural Language Game Recording
Allows coaches to quickly record games via simple text commands.
"""

import re
from datetime import datetime
from typing import Dict, List, Tuple


def parse_scorers_text(scorers_text: str) -> Dict[str, Dict[str, int]]:
    """
    Parse scorer text into structured data.

    Examples:
        "Lukas 2G 1A" -> {"Lukas": {"goals": 2, "assists": 1}}
        "Felix 1G, Michael 2A" -> {"Felix": {"goals": 1, "assists": 0}, "Michael": {"goals": 0, "assists": 2}}
        "Lukas hat trick" -> {"Lukas": {"goals": 3, "assists": 0}}

    Args:
        scorers_text: Natural language scorer description

    Returns:
        Dict mapping player names to their goals and assists
    """
    player_stats = {}

    # Split by comma or semicolon
    entries = re.split(r'[,;]', scorers_text)

    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue

        # Check for "hat trick" or "hattrick"
        hat_trick_match = re.search(r'(.+?)\s+(hat\s*trick)', entry, re.IGNORECASE)
        if hat_trick_match:
            name = hat_trick_match.group(1).strip()
            player_stats[name] = {"goals": 3, "assists": 0}
            continue

        # Extract player name (everything before numbers)
        # Pattern: "Name XG YA" or "Name X goals Y assists"
        name_match = re.match(r'^([A-Za-z\s]+?)(?=\s+\d)', entry)
        if not name_match:
            # Try simple name only (assume 1G)
            name = entry.strip()
            if name:
                player_stats[name] = {"goals": 1, "assists": 0}
            continue

        name = name_match.group(1).strip()

        # Extract goals: "2G" or "2 goals"
        goals_match = re.search(r'(\d+)\s*(?:G|goals?)', entry, re.IGNORECASE)
        goals = int(goals_match.group(1)) if goals_match else 0

        # Extract assists: "1A" or "1 assist"
        assists_match = re.search(r'(\d+)\s*(?:A|assists?)', entry, re.IGNORECASE)
        assists = int(assists_match.group(1)) if assists_match else 0

        player_stats[name] = {"goals": goals, "assists": assists}

    return player_stats


def validate_score(player_stats: Dict[str, Dict[str, int]], declared_score: int) -> Tuple[bool, str]:
    """
    Validate that total goals match the declared score.

    Args:
        player_stats: Parsed player statistics
        declared_score: Score declared in game result

    Returns:
        Tuple of (is_valid, error_message)
    """
    total_goals = sum(stats["goals"] for stats in player_stats.values())

    if total_goals == declared_score:
        return True, ""
    elif total_goals < declared_score:
        return False, f"Total goals ({total_goals}) less than score ({declared_score}). Missing {declared_score - total_goals} goal(s)."
    else:
        return False, f"Total goals ({total_goals}) exceeds score ({declared_score}). Extra {total_goals - declared_score} goal(s)."


def quick_record_game(
    db,
    opponent: str,
    score_us: int,
    score_them: int,
    scorers_text: str = "",
    goalie_name: str = None,
    shots_against: int = 0,
    notes: str = "",
    overtime: bool = False
) -> Dict:
    """
    Quick game entry - bypasses wizard for fast recording.
    Records game outcome and scorer stats only. Does NOT update goalie stats unless explicitly provided.
    For complete goalie statistics, use the Game Wizard UI.

    Args:
        db: MongoDB database connection
        opponent: Opponent team name
        score_us: Our score
        score_them: Their score
        scorers_text: Natural language scorer text (e.g., "Lukas 2G 1A, Felix 1G")
        goalie_name: Name of goalie who played (optional, requires shots_against)
        shots_against: Shots against the goalie (required if goalie_name provided)
        notes: Game notes (optional)
        overtime: True if game went to OT/shootout (European scoring: W=3, OTW=2, OTL=1, L=0)

    Returns:
        Result dictionary with status and summary
    """
    from src.game_wizard import update_all_game_stats

    # Determine result (European points system)
    if score_us > score_them:
        result = "OTW" if overtime else "W"
    elif score_us < score_them:
        result = "OTL" if overtime else "L"
    else:
        result = "D"  # Tied (shouldn't happen in European hockey, but legacy support)

    # Parse scorer text
    player_stats = {}
    if scorers_text:
        player_stats = parse_scorers_text(scorers_text)

        # Validate goals match score
        is_valid, error_msg = validate_score(player_stats, score_us)
        if not is_valid:
            return {
                "status": "error",
                "message": f"Validation failed: {error_msg}",
                "parsed_stats": player_stats
            }

    # Build game data
    game_data = {
        "opponent": opponent,
        "score_us": score_us,
        "score_them": score_them,
        "date": datetime.now(),
        "result": result,
        "notes": notes,
        "scorers": [name for name, stats in player_stats.items() if stats["goals"] > 0]
    }

    # Build goalie stats - ONLY if explicitly provided with shots data
    goalie_stats = {}
    if goalie_name and shots_against > 0:
        goalie_stats[goalie_name] = {
            "shots_against": shots_against,
            "minutes": 60  # Assume full game
        }

    # Update all stats
    try:
        updates_summary = update_all_game_stats(db, game_data, player_stats, goalie_stats)

        message = f"✅ Game recorded: {score_us}-{score_them} vs {opponent} ({result})"
        if not goalie_stats:
            message += ". Note: Goalie stats not updated (use Game Wizard for complete stats)"

        return {
            "status": "success",
            "message": message,
            "updates": updates_summary,
            "parsed_stats": player_stats
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to record game: {str(e)}",
            "parsed_stats": player_stats
        }


def parse_quick_game_command(command: str) -> Dict:
    """
    Parse natural language game command.

    Examples:
        "Record 4-2 win vs Eagles"
        "Add game 3-5 loss against Bears, Lukas 2G 1A, Felix 1G"
        "Game result: 2-2 draw vs Lions, Michael 1G, Stefan 1G"

    Args:
        command: Natural language command

    Returns:
        Dict with parsed components or error
    """
    # Extract score pattern "X-Y" or "X:Y"
    score_match = re.search(r'(\d+)[:\-](\d+)', command)
    if not score_match:
        return {"error": "Could not find score (format: X-Y or X:Y)"}

    score_us = int(score_match.group(1))
    score_them = int(score_match.group(2))

    # Extract opponent (after "vs", "against", "v")
    opponent_match = re.search(r'(?:vs\.?|against|v)\s+([A-Za-z\s]+?)(?:[,\.]|$)', command, re.IGNORECASE)
    if not opponent_match:
        return {"error": "Could not find opponent (use 'vs' or 'against')"}

    opponent = opponent_match.group(1).strip()

    # Extract scorers (after opponent, until end or "goalie")
    scorers_text = ""
    after_opponent = command[opponent_match.end():].strip()
    if after_opponent:
        # Remove leading comma
        after_opponent = after_opponent.lstrip(',').strip()
        # Stop at "goalie" or "notes"
        scorers_match = re.match(r'([^\.]+?)(?:goalie|notes|$)', after_opponent, re.IGNORECASE)
        if scorers_match:
            scorers_text = scorers_match.group(1).strip()

    return {
        "score_us": score_us,
        "score_them": score_them,
        "opponent": opponent,
        "scorers_text": scorers_text
    }
