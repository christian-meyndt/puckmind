"""
Hockey Scout & Team Manager Agent
Day-1 Starter: Agent can query players and perform simple analyses.

Prerequisites:
  pip install google-adk pymongo python-dotenv
"""

import os
import ssl
from dotenv import load_dotenv
from pymongo import MongoClient
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from src.agent_enhanced import (
    get_smart_availability_warnings,
    analyze_opponent,
    track_player_form,
    generate_post_game_summary,
    predict_season_finish,
)

load_dotenv()

# Force use of Vertex AI
if "GOOGLE_API_KEY" in os.environ:
    del os.environ["GOOGLE_API_KEY"]
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

# ── MongoDB Connection ────────────────────────────────────────
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(
    MONGODB_URI,
    ssl=True,
    ssl_cert_reqs=ssl.CERT_NONE
)
db = client["hockey_agent"]


# ── Tools (Functions the agent can call) ──────────────────────

def get_all_players() -> list[dict]:
    """Returns all players of the team with statistics."""
    players = list(db.players.find({}, {"_id": 0}))
    return players


def get_available_players() -> list[dict]:
    """Returns only available players (not injured/suspended)."""
    players = list(db.players.find({"available": True}, {"_id": 0}))
    return players


def get_top_scorers(limit: int = 5) -> list[dict]:
    """
    Returns the top goal scorers.
    Args:
        limit: Number of players (default: 5)
    """
    players = list(
        db.players.find({}, {"_id": 0})
        .sort("goals", -1)
        .limit(limit)
    )
    return players


def get_recent_games(limit: int = 5) -> list[dict]:
    """
    Returns the most recent games.
    Args:
        limit: Number of games (default: 5)
    """
    games = list(
        db.games.find({}, {"_id": 0})
        .sort("date", -1)
        .limit(limit)
    )
    # Convert date to string for JSON serialization
    for g in games:
        g["date"] = g["date"].strftime("%d.%m.%Y")
    return games


def get_season_record() -> dict:
    """Returns the current season record (wins, losses, draws)."""
    games = list(db.games.find({}, {"_id": 0, "result": 1}))
    wins   = sum(1 for g in games if g["result"] == "W")
    losses = sum(1 for g in games if g["result"] == "L")
    draws  = sum(1 for g in games if g["result"] == "D")
    return {
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "total_games": len(games),
        "points": wins * 2 + draws,
    }


def suggest_lineup() -> dict:
    """
    Suggests a lineup based on available players with visual hockey rink layout.
    Automatically selects the goalie and the strongest lines based on performance.
    """
    from src.lineup_visualizer import format_lineup_card

    available = list(db.players.find({"available": True}, {"_id": 0}))

    goalie    = next((p for p in available if p["position"] == "Goalie"), None)
    defenders = sorted(
        [p for p in available if p["position"] == "Defense"],
        key=lambda p: p.get("plus_minus", 0),
        reverse=True
    )
    forwards  = sorted(
        [p for p in available if p["position"] == "Forward"],
        key=lambda p: p["goals"] + p["assists"],
        reverse=True,
    )

    lineup_data = {
        "goalie": goalie["name"] if goalie else "No goalie available!",
        "line_1": {
            "forwards": [p["name"] for p in forwards[:3]],
            "defense":  [p["name"] for p in defenders[:2]],
        },
        "line_2": {
            "forwards": [p["name"] for p in forwards[3:6]],
            "defense":  [p["name"] for p in defenders[2:4]],
        },
        "unavailable_players": [
            p["name"] for p in db.players.find({"available": False}, {"_id": 0})
        ],
    }

    # Add visual lineup card
    visual_card = format_lineup_card(lineup_data)

    # Add reasoning
    if forwards:
        top_scorer = forwards[0]
        lineup_data["reasoning"] = f"Line 1 built around {top_scorer['name']} ({top_scorer['goals']}G, {top_scorer['assists']}A)"

    lineup_data["visual_lineup"] = visual_card

    return lineup_data


def add_game_result(opponent: str, score_us: int, score_them: int, notes: str = "") -> dict:
    """
    Records a new game result.
    Args:
        opponent:   Name of the opponent
        score_us:   Our goals
        score_them: Opponent's goals
        notes:      Optional notes about the game
    """
    from datetime import datetime
    result = "W" if score_us > score_them else ("L" if score_us < score_them else "D")
    game = {
        "date": datetime.now(),
        "opponent": opponent,
        "home": True,
        "score_us": score_us,
        "score_them": score_them,
        "result": result,
        "scorers": [],
        "notes": notes,
    }
    db.games.insert_one(game)
    return {"status": "ok", "message": f"Game against {opponent} ({score_us}:{score_them}) saved."}


def get_player_detailed_stats(player_name: str = None) -> dict:
    """
    Returns detailed statistics for a specific player with position-relevant stats highlighted.
    Forwards: goals, assists, points, shooting %, faceoff %
    Defenders: plus/minus, blocked shots, hits, assists
    Args:
        player_name: Name of the player (optional, if not provided returns top performers)
    """
    if player_name:
        # Search for specific player (case-insensitive)
        player = db.players.find_one(
            {"name": {"$regex": player_name, "$options": "i"}},
            {"_id": 0}
        )
        if not player:
            return {"error": f"Player '{player_name}' not found"}

        # Add position-specific context
        position = player.get("position", "Unknown")
        if position == "Forward":
            player["key_stats_type"] = "offensive"
            player["primary_stats"] = ["goals", "assists", "shooting_pct", "faceoff_pct", "plus_minus"]
        elif position == "Defense":
            player["key_stats_type"] = "defensive"
            player["primary_stats"] = ["plus_minus", "blocked_shots", "hits", "assists", "shots"]

        return {"player": player}
    else:
        # Return top performers by position
        top_forwards = list(
            db.players.find(
                {"position": "Forward"},
                {"_id": 0}
            ).sort([("goals", -1), ("assists", -1)]).limit(3)
        )
        top_defenders = list(
            db.players.find(
                {"position": "Defense"},
                {"_id": 0}
            ).sort([("plus_minus", -1), ("blocked_shots", -1)]).limit(3)
        )
        return {
            "top_forwards": top_forwards,
            "top_defenders": top_defenders
        }


def get_goalie_stats() -> list[dict]:
    """Returns detailed goalie statistics including GAA, save percentage, and shutouts."""
    goalies = list(
        db.players.find(
            {"position": "Goalie"},
            {"_id": 0}
        ).sort("gaa", 1)  # Sort by GAA (lower is better)
    )
    return goalies


def get_top_forwards() -> list[dict]:
    """
    Returns top forwards ranked by offensive statistics.
    Focus: goals, assists, points, shooting percentage, faceoff wins.
    """
    forwards = list(
        db.players.find(
            {"position": "Forward"},
            {"_id": 0, "name": 1, "number": 1, "goals": 1, "assists": 1,
             "shooting_pct": 1, "faceoff_pct": 1, "plus_minus": 1, "games_played": 1, "shots": 1}
        ).sort([("goals", -1), ("assists", -1)]).limit(5)
    )

    # Calculate total points
    for f in forwards:
        f["points"] = f["goals"] + f["assists"]

    return forwards


def get_top_defenders() -> list[dict]:
    """
    Returns top defenders ranked by defensive statistics.
    Focus: plus/minus, blocked shots, hits, assists (playmaking).
    """
    defenders = list(
        db.players.find(
            {"position": "Defense"},
            {"_id": 0, "name": 1, "number": 1, "plus_minus": 1, "blocked_shots": 1,
             "hits": 1, "assists": 1, "goals": 1, "games_played": 1, "pim": 1}
        ).sort([("plus_minus", -1), ("blocked_shots", -1)]).limit(5)
    )

    # Calculate total points
    for d in defenders:
        d["points"] = d["goals"] + d["assists"]

    return defenders


def suggest_training_exercises() -> dict:
    """
    Analyzes team weaknesses and suggests training exercises.
    Looks at player stats and recent game results to identify areas for improvement.
    """
    players = list(db.players.find({}, {"_id": 0}))
    games = list(db.games.find({}, {"_id": 0}).sort("date", -1).limit(5))

    # Analyze team statistics
    total_players = len(players)
    total_goals = sum(p["goals"] for p in players)
    total_assists = sum(p["assists"] for p in players)
    avg_goals_per_player = total_goals / total_players if total_players > 0 else 0

    # Count low performers
    low_scorers = [p for p in players if p["goals"] < avg_goals_per_player and p["position"] == "Forward"]

    # Recent game performance
    recent_losses = sum(1 for g in games if g["result"] == "L")
    recent_wins = sum(1 for g in games if g["result"] == "W")

    # Build recommendations
    weaknesses = []
    exercises = []

    if len(low_scorers) > 2:
        weaknesses.append("offensive_production")
        exercises.append({
            "area": "Offensive Skills",
            "weakness": f"{len(low_scorers)} forwards scoring below team average",
            "exercises": [
                "Shooting drill: 100 shots per player (wrist shots, snap shots, one-timers)",
                "2-on-1 breakout drills to improve scoring chances",
                "Power play setups with focus on net-front presence",
                "Quick release shooting from different angles"
            ]
        })

    if recent_losses > recent_wins and recent_losses >= 2:
        weaknesses.append("defensive_stability")
        exercises.append({
            "area": "Defensive Skills",
            "weakness": f"Lost {recent_losses} of last {len(games)} games",
            "exercises": [
                "Defensive zone coverage drills (box formation)",
                "Backchecking drills with emphasis on gap control",
                "1-on-1 defensive positioning in front of net",
                "Penalty kill practice (4-on-5 situations)"
            ]
        })

    if total_assists < total_goals * 1.5:
        weaknesses.append("team_play")
        exercises.append({
            "area": "Team Play & Passing",
            "weakness": "Low assist-to-goal ratio suggests limited team play",
            "exercises": [
                "Cycle drills in offensive zone (wall play)",
                "Cross-ice passing drills under pressure",
                "3-on-2 rush drills focusing on give-and-go passes",
                "Breakout drills with multiple passing options"
            ]
        })

    # Always include conditioning
    exercises.append({
        "area": "Conditioning",
        "weakness": "General fitness maintenance",
        "exercises": [
            "Interval training: 30-second sprints with 30-second rest (10 reps)",
            "Edge work drills for skating agility",
            "Suicide sprints (blue line to red line progressions)",
            "Battle drills along the boards for stamina"
        ]
    })

    return {
        "identified_weaknesses": weaknesses,
        "training_plan": exercises,
        "summary": f"Analyzed {total_players} players and {len(games)} recent games. Found {len(weaknesses)} areas needing improvement."
    }


# ── Agent Definition ──────────────────────────────────────────

SYSTEM_PROMPT = """
You are the Hockey Scout & Team Manager Agent for an amateur ice hockey team.
You help the coach and manager with:
- Player statistics and availability (with proactive warnings about lineup issues)
- Lineup suggestions with visual formatting
- Game reports and season record
- Training planning - suggest exercises based on team weaknesses
- Opponent analysis and scouting reports
- Player form tracking (hot/cold streaks)
- Post-game summaries for social media
- Season predictions and standings
- Position-specific analytics (forwards vs defenders)
- Simple analyses and recommendations

When analyzing player statistics, consider position-specific metrics:
- **Forwards**: Focus on goals, assists, points, shooting %, faceoff %, offensive zone time
- **Defenders**: Focus on plus/minus, blocked shots, hits, defensive reliability, transition play
- **Goalies**: Focus on GAA, save %, shutouts, wins

When suggesting lineups, ALWAYS display the visual_lineup field to show the hockey rink formation.
This gives coaches an immediate visual understanding of the lineup structure.

Always respond in a friendly and direct manner.
When suggesting lineups or training exercises, briefly explain your choices.
Proactively warn about potential lineup issues (e.g., low defender count).
"""

# Configure to use Vertex AI by setting environment variable
# ADK will automatically use Vertex AI when GOOGLE_CLOUD_PROJECT is set
# and Application Default Credentials are configured

hockey_agent = Agent(
    name="hockey_scout",
    model="gemini-2.5-flash",  # Vertex AI model
    description="Hockey Scout & Team Manager Agent",
    instruction=SYSTEM_PROMPT,
    tools=[
        FunctionTool(get_all_players),
        FunctionTool(get_available_players),
        FunctionTool(get_top_scorers),
        FunctionTool(get_recent_games),
        FunctionTool(get_season_record),
        FunctionTool(suggest_lineup),
        FunctionTool(add_game_result),
        FunctionTool(suggest_training_exercises),
        FunctionTool(get_smart_availability_warnings),
        FunctionTool(analyze_opponent),
        FunctionTool(track_player_form),
        FunctionTool(generate_post_game_summary),
        FunctionTool(predict_season_finish),
        FunctionTool(get_player_detailed_stats),
        FunctionTool(get_goalie_stats),
        FunctionTool(get_top_forwards),
        FunctionTool(get_top_defenders),
    ],
)


# ── Runner (local CLI session) ────────────────────────────────

import asyncio

async def main():
    session_service = InMemorySessionService()
    runner = Runner(
        agent=hockey_agent,
        app_name="hockey_agent",
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name="hockey_agent",
        user_id="trainer",
    )

    print("🏒 Hockey Agent ready! (Exit with 'exit')\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break
        if not user_input:
            continue

        from google.genai import types
        content = types.Content(
            role="user",
            parts=[types.Part(text=user_input)],
        )

        events = runner.run(
            user_id="trainer",
            session_id=session.id,
            new_message=content,
        )

        for event in events:
            if event.is_final_response():
                print(f"\nAgent: {event.content.parts[0].text}\n")


if __name__ == "__main__":
    asyncio.run(main())
