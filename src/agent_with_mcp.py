"""
Hockey Scout & Team Manager Agent with MongoDB MCP Server Integration
Fully integrated version using MCP for all MongoDB operations.
"""

import os
import asyncio
import json
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

# Force use of Vertex AI
if "GOOGLE_API_KEY" in os.environ:
    del os.environ["GOOGLE_API_KEY"]
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

# MongoDB connection details
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

# Global MCP session (initialized in main)
mcp_session: ClientSession = None


#── MCP Helper Functions ──────────────────────────────────────

def parse_mcp_result(result) -> str:
    """Parse MCP CallToolResult into a readable string."""
    if hasattr(result, 'content') and result.content:
        if len(result.content) > 0:
            return result.content[0].text
    return str(result)


async def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    """Call an MCP tool and return the result as a string."""
    global mcp_session
    result = await mcp_session.call_tool(tool_name, arguments=arguments)
    return parse_mcp_result(result)


# ── Agent Tools (wrapping MCP calls) ──────────────────────────

def get_all_players() -> list[dict]:
    """Returns all players of the team with statistics."""
    # Run async MCP call in sync context
    loop = asyncio.get_event_loop()
    result_text = loop.run_until_complete(
        call_mcp_tool("aggregate", {
            "database": "hockey_agent",
            "collection": "players",
            "pipeline": [{"$project": {"_id": 0}}]
        })
    )
    # Parse the response - MCP returns descriptive text, not JSON
    # For now, return the text response
    return [{"info": result_text}]


def get_available_players() -> list[dict]:
    """Returns only available players (not injured/suspended)."""
    loop = asyncio.get_event_loop()
    result_text = loop.run_until_complete(
        call_mcp_tool("aggregate", {
            "database": "hockey_agent",
            "collection": "players",
            "pipeline": [
                {"$match": {"available": True}},
                {"$project": {"_id": 0}}
            ]
        })
    )
    return [{"info": result_text}]


def get_top_scorers(limit: int = 5) -> list[dict]:
    """
    Returns the top goal scorers.
    Args:
        limit: Number of players (default: 5)
    """
    loop = asyncio.get_event_loop()
    result_text = loop.run_until_complete(
        call_mcp_tool("aggregate", {
            "database": "hockey_agent",
            "collection": "players",
            "pipeline": [
                {"$sort": {"goals": -1}},
                {"$limit": limit},
                {"$project": {"_id": 0, "name": 1, "goals": 1, "assists": 1, "number": 1, "position": 1}}
            ]
        })
    )
    return [{"info": result_text}]


def get_recent_games(limit: int = 5) -> list[dict]:
    """
    Returns the most recent games.
    Args:
        limit: Number of games (default: 5)
    """
    loop = asyncio.get_event_loop()
    result_text = loop.run_until_complete(
        call_mcp_tool("aggregate", {
            "database": "hockey_agent",
            "collection": "games",
            "pipeline": [
                {"$sort": {"date": -1}},
                {"$limit": limit},
                {"$project": {"_id": 0}}
            ]
        })
    )
    return [{"info": result_text}]


def get_season_record() -> dict:
    """Returns the current season record (wins, losses, draws)."""
    loop = asyncio.get_event_loop()
    result_text = loop.run_until_complete(
        call_mcp_tool("count", {
            "database": "hockey_agent",
            "collection": "games",
            "query": {}
        })
    )
    return {"info": f"Season statistics: {result_text}"}


def get_db_stats() -> dict:
    """Returns database statistics."""
    loop = asyncio.get_event_loop()
    result_text = loop.run_until_complete(
        call_mcp_tool("db-stats", {
            "database": "hockey_agent"
        })
    )
    return {"stats": result_text}


# ── Agent Definition ──────────────────────────────────────────

SYSTEM_PROMPT = """
You are the Hockey Scout & Team Manager Agent for an amateur ice hockey team.
You help the coach and manager with:
- Player statistics and availability
- Lineup suggestions based on available players
- Game reports and season record
- Simple analyses and recommendations

You are connected to MongoDB via the Model Context Protocol (MCP), which provides
secure and structured access to the team's database.

Always respond in a friendly and direct manner.
When suggesting lineups, briefly explain your choices based on the player data.
"""

hockey_agent = Agent(
    name="hockey_scout",
    model="gemini-2.5-flash",
    description="Hockey Scout & Team Manager Agent with MongoDB MCP Integration",
    instruction=SYSTEM_PROMPT,
    tools=[
        FunctionTool(get_all_players),
        FunctionTool(get_available_players),
        FunctionTool(get_top_scorers),
        FunctionTool(get_recent_games),
        FunctionTool(get_season_record),
        FunctionTool(get_db_stats),
    ],
)


# ── Runner (local CLI session) ────────────────────────────────

async def main():
    global mcp_session

    print("🏒 Starting MongoDB MCP Server...")

    # Create MCP client
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mongodb-mcp-server@latest", "--readOnly"],
        env={"MDB_MCP_CONNECTION_STRING": MONGODB_URI}
    )

    client_context = stdio_client(server_params)

    async with client_context as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_session = session

            print("✅ Connected to MongoDB via MCP\n")

            # Create session service and runner
            session_service = InMemorySessionService()
            runner = Runner(
                agent=hockey_agent,
                app_name="hockey_agent",
                session_service=session_service,
            )

            agent_session = await session_service.create_session(
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

                content = types.Content(
                    role="user",
                    parts=[types.Part(text=user_input)],
                )

                events = runner.run(
                    user_id="trainer",
                    session_id=agent_session.id,
                    new_message=content,
                )

                for event in events:
                    if event.is_final_response():
                        print(f"\nAgent: {event.content.parts[0].text}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
