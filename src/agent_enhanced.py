"""
Enhanced agent tools with wow-factor features
"""

import os
import ssl
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

# MongoDB Connection (same as in agent.py)
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(
    MONGODB_URI,
    ssl=True,
    ssl_cert_reqs=ssl.CERT_NONE
)
db = client["hockey_agent"]


def get_smart_availability_warnings() -> dict:
    """
    Proactively checks for availability issues and warns about lineup problems.
    """
    available = list(db.players.find({"available": True}, {"_id": 0}))
    unavailable = list(db.players.find({"available": False}, {"_id": 0}))

    defenders = [p for p in available if p["position"] == "Defense"]
    forwards = [p for p in available if p["position"] == "Forward"]
    goalies = [p for p in available if p["position"] == "Goalie"]

    warnings = []

    if len(goalies) == 0:
        warnings.append("🚨 CRITICAL: No goalie available! Need emergency backup.")
    elif len(goalies) == 1:
        warnings.append("⚠️ Only 1 goalie available - no backup if injured.")

    if len(defenders) < 4:
        warnings.append(f"⚠️ Only {len(defenders)} defenders available - consider calling up a forward to play defense.")

    if len(forwards) < 6:
        warnings.append(f"⚠️ Only {len(forwards)} forwards available - may need to shorten bench.")

    if len(unavailable) > 0:
        unavailable_names = [f"{p['name']} ({p['position']})" for p in unavailable]
        warnings.append(f"📋 Unavailable: {', '.join(unavailable_names)}")

    return {
        "status": "critical" if any("CRITICAL" in w for w in warnings) else "warning" if warnings else "ok",
        "warnings": warnings,
        "summary": f"{len(available)} available, {len(unavailable)} unavailable",
        "available_by_position": {
            "goalies": len(goalies),
            "defenders": len(defenders),
            "forwards": len(forwards)
        }
    }


def analyze_opponent(opponent_name: str) -> dict:
    """
    Analyzes past games against a specific opponent.
    Args:
        opponent_name: Name of the opponent to analyze
    """
    games_vs_opponent = list(db.games.find(
        {"opponent": {"$regex": opponent_name, "$options": "i"}},
        {"_id": 0}
    ).sort("date", -1))

    if not games_vs_opponent:
        return {
            "opponent": opponent_name,
            "games_played": 0,
            "analysis": f"No previous games found against {opponent_name}."
        }

    wins = sum(1 for g in games_vs_opponent if g["result"] == "W")
    losses = sum(1 for g in games_vs_opponent if g["result"] == "L")
    draws = sum(1 for g in games_vs_opponent if g["result"] == "D")

    total_goals_for = sum(g["score_us"] for g in games_vs_opponent)
    total_goals_against = sum(g["score_them"] for g in games_vs_opponent)

    recent_3 = games_vs_opponent[:3]
    recent_record = f"{sum(1 for g in recent_3 if g['result'] == 'W')}W-{sum(1 for g in recent_3 if g['result'] == 'L')}L-{sum(1 for g in recent_3 if g['result'] == 'D')}D"

    # Generate recommendations
    recommendations = []
    if wins > losses:
        recommendations.append("You have a winning record against this opponent - play with confidence.")
    if total_goals_for / len(games_vs_opponent) > 3:
        recommendations.append("High-scoring games against this opponent - focus on offensive pressure.")
    if total_goals_against / len(games_vs_opponent) > 3:
        recommendations.append("This opponent scores frequently - tighten up defensive coverage.")

    return {
        "opponent": opponent_name,
        "games_played": len(games_vs_opponent),
        "record": f"{wins}W-{losses}L-{draws}D",
        "recent_3_games": recent_record,
        "avg_goals_for": round(total_goals_for / len(games_vs_opponent), 1),
        "avg_goals_against": round(total_goals_against / len(games_vs_opponent), 1),
        "recommendations": recommendations
    }


def track_player_form() -> dict:
    """
    Identifies players on hot or cold streaks based on their statistics.
    """
    players = list(db.players.find({}, {"_id": 0}))

    # Calculate team averages
    avg_goals = sum(p["goals"] for p in players) / len(players)
    avg_assists = sum(p["assists"] for p in players)  / len(players)

    hot_players = []
    cold_players = []

    for player in players:
        if player["position"] == "Goalie":
            continue

        total_points = player["goals"] + player["assists"]
        expected_points = avg_goals + avg_assists

        if total_points > expected_points * 1.3:  # 30% above average
            hot_players.append({
                "name": player["name"],
                "position": player["position"],
                "goals": player["goals"],
                "assists": player["assists"],
                "total_points": total_points,
                "status": "🔥 Hot streak"
            })
        elif total_points < expected_points * 0.5:  # 50% below average
            cold_players.append({
                "name": player["name"],
                "position": player["position"],
                "goals": player["goals"],
                "assists": player["assists"],
                "total_points": total_points,
                "status": "❄️ Cold streak"
            })

    recommendations = []
    if hot_players:
        top_hot = hot_players[0]
        recommendations.append(f"Put {top_hot['name']} on Line 1 - they're on fire with {top_hot['total_points']} points!")
    if cold_players:
        recommendations.append(f"{len(cold_players)} player(s) struggling - consider extra shooting practice.")

    return {
        "hot_players": hot_players,
        "cold_players": cold_players,
        "recommendations": recommendations
    }


def generate_post_game_summary(opponent: str, score_us: int, score_them: int) -> dict:
    """
    Generates a formatted match report for social media/website.
    Args:
        opponent: Name of the opponent
        score_us: Our goals
        score_them: Opponent's goals
    """
    result = "W" if score_us > score_them else ("L" if score_us < score_them else "D")
    result_text = "WIN" if result == "W" else ("LOSS" if result == "L" else "DRAW")

    # Get season record
    games = list(db.games.find({}, {"_id": 0}))
    wins = sum(1 for g in games if g["result"] == "W")
    losses = sum(1 for g in games if g["result"] == "L")
    draws = sum(1 for g in games if g["result"] == "D")

    # Format for different platforms
    whatsapp_format = f"""
🏒 GAME RESULT 🏒

{result_text}: {score_us}-{score_them} vs {opponent}

Season Record: {wins}W-{losses}L-{draws}D
Points: {wins * 2 + draws}

Great game team! 💪
"""

    website_format = f"""
# Match Report

**Result:** {result_text}
**Score:** {score_us}-{score_them}
**Opponent:** {opponent}
**Date:** {datetime.now().strftime('%B %d, %Y')}

## Season Update
Current Record: {wins}W-{losses}L-{draws}D
Total Points: {wins * 2 + draws}

{"The team continues their strong performance this season!" if result == "W" else "A tough loss, but the team will bounce back stronger!"}
"""

    return {
        "result": result_text,
        "score": f"{score_us}-{score_them}",
        "whatsapp": whatsapp_format.strip(),
        "website": website_format.strip(),
        "twitter": f"🏒 {result_text}! {score_us}-{score_them} vs {opponent}. Season: {wins}W-{losses}L-{draws}D. #{opponent.replace(' ', '')} #Hockey"
    }


def predict_season_finish() -> dict:
    """
    Predicts final season standing based on current performance.
    """
    games = list(db.games.find({}, {"_id": 0}))

    if len(games) == 0:
        return {"prediction": "Not enough games played to make a prediction."}

    wins = sum(1 for g in games if g["result"] == "W")
    losses = sum(1 for g in games if g["result"] == "L")
    draws = sum(1 for g in games if g["result"] == "D")
    points = wins * 2 + draws

    # Assume 20-game season (typical for amateur leagues)
    games_played = len(games)
    games_remaining = max(0, 20 - games_played)

    # Calculate points per game
    ppg = points / games_played if games_played > 0 else 0

    # Project final points
    projected_points = points + (ppg * games_remaining)

    # Estimate standing (rough amateur league points)
    # 1st: ~32+ points, 2nd: ~28+, 3rd: ~24+, 4th: ~20+
    if projected_points >= 32:
        standing = "1st place"
    elif projected_points >= 28:
        standing = "2nd place"
    elif projected_points >= 24:
        standing = "3rd place"
    elif projected_points >= 20:
        standing = "4th place"
    else:
        standing = "5th place or lower"

    # What's needed for next tier
    next_tier_points = None
    if projected_points < 32:
        next_tier = 32 if projected_points >= 28 else 28 if projected_points >= 24 else 24
        points_needed = next_tier - points
        wins_needed = (points_needed + 1) // 2  # Round up
        next_tier_points = f"Need {wins_needed} win(s) from last {games_remaining} games for next tier."

    return {
        "current_record": f"{wins}W-{losses}L-{draws}D",
        "current_points": points,
        "games_played": games_played,
        "games_remaining": games_remaining,
        "projected_points": round(projected_points, 1),
        "projected_standing": standing,
        "improvement_tip": next_tier_points or "On track for top finish!"
    }
