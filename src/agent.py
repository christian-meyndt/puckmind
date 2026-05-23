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
    Suggests a lineup based on available players.
    Automatically selects the goalie and the strongest line.
    """
    available = list(db.players.find({"available": True}, {"_id": 0}))

    goalie    = next((p for p in available if p["position"] == "Goalie"), None)
    defenders = [p for p in available if p["position"] == "Defense"]
    forwards  = sorted(
        [p for p in available if p["position"] == "Forward"],
        key=lambda p: p["goals"] + p["assists"],
        reverse=True,
    )

    lineup = {
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
    return lineup


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


# ── Agent Definition ──────────────────────────────────────────

SYSTEM_PROMPT = """
You are the Hockey Scout & Team Manager Agent for an amateur ice hockey team.
You help the coach and manager with:
- Player statistics and availability
- Lineup suggestions
- Game reports and season record
- Simple analyses and recommendations

Always respond in a friendly and direct manner.
When suggesting lineups, briefly explain your choices.
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
