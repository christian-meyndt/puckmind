"""
Hockey Scout & Team Manager Agent with MongoDB MCP Server Integration
Uses Model Context Protocol to connect to MongoDB instead of direct pymongo connection.
"""

import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
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

# ── MCP Server Setup ──────────────────────────────────────────
# MongoDB MCP server will be started as a subprocess
# It communicates via stdio (stdin/stdout)

async def create_mcp_client():
    """Create and return an MCP client context manager."""
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mongodb-mcp-server@latest", "--readOnly"],
        env={
            "MDB_MCP_CONNECTION_STRING": MONGODB_URI
        }
    )
    return stdio_client(server_params)


# ── MCP-based Tools ──────────────────────────────────────────
# These tools will call the MongoDB MCP server instead of using pymongo directly

async def get_all_players_mcp(mcp_session: ClientSession) -> list[dict]:
    """Returns all players of the team with statistics using MCP."""
    result = await mcp_session.call_tool(
        "find",
        arguments={
            "database": "hockey_agent",
            "collection": "players",
            "query": {}
        }
    )
    return result.content


async def get_top_scorers_mcp(mcp_session: ClientSession, limit: int = 5) -> list[dict]:
    """Returns the top goal scorers using MCP aggregation."""
    result = await mcp_session.call_tool(
        "aggregate",
        arguments={
            "database": "hockey_agent",
            "collection": "players",
            "pipeline": [
                {"$sort": {"goals": -1}},
                {"$limit": limit}
            ]
        }
    )
    return result.content


async def get_season_record_mcp(mcp_session: ClientSession) -> dict:
    """Returns the current season record using MCP."""
    # Use count to get game counts
    result = await mcp_session.call_tool(
        "count",
        arguments={
            "database": "hockey_agent",
            "collection": "games",
            "query": {}
        }
    )

    # MCP returns TextContent objects, we need to parse them
    print(f"MCP Result type: {type(result)}")
    print(f"MCP Result: {result}")

    return {
        "test": "mcp_connected",
        "result": str(result)
    }


# ── Agent Definition ──────────────────────────────────────────

SYSTEM_PROMPT = """
You are the Hockey Scout & Team Manager Agent for an amateur ice hockey team.
You help the coach and manager with:
- Player statistics and availability
- Lineup suggestions
- Game reports and season record
- Simple analyses and recommendations

You are now connected to MongoDB via the Model Context Protocol (MCP).

Always respond in a friendly and direct manner.
When suggesting lineups, briefly explain your choices.
"""

# Note: We'll need to wrap MCP calls in synchronous functions for Google ADK
# This is a simplified version - full integration will require adapting the tool architecture

hockey_agent = Agent(
    name="hockey_scout",
    model="gemini-2.5-flash",
    description="Hockey Scout & Team Manager Agent with MCP Integration",
    instruction=SYSTEM_PROMPT,
    tools=[],  # We'll add MCP-based tools here
)


# ── Runner (local CLI session) ────────────────────────────────

async def main():
    print("🏒 Starting MongoDB MCP Server...")

    # Create MCP client as context manager
    client = await create_mcp_client()

    async with client as (read, write):
        # Initialize MCP client session
        async with ClientSession(read, write) as mcp_session:
            await mcp_session.initialize()
            print("✅ Connected to MongoDB via MCP")

            # List available tools from MCP server
            tools_result = await mcp_session.list_tools()
            print(f"\n📋 Available MCP Tools: {len(tools_result.tools)}")
            for tool in tools_result.tools[:10]:  # Show first 10
                print(f"   - {tool.name}: {tool.description}")

            # Test a simple query
            print("\n🧪 Testing MCP connection...")
            try:
                record = await get_season_record_mcp(mcp_session)
                print(f"Season Record: {record}")
            except Exception as e:
                print(f"Error: {e}")

            print("\n✅ MCP Integration test complete!")


if __name__ == "__main__":
    asyncio.run(main())
