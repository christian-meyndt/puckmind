# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**PuckMind** is a Hockey Scout & Team Manager Agent for amateur ice hockey teams. Built for the **Google Cloud Rapid Agent Hackathon** (MongoDB Track), it uses Google Gemini 2.0 Flash, Google ADK (Agent Development Kit), and MongoDB to help coaches and managers with player statistics, lineup suggestions, game results, and team analysis.

The agent provides conversational assistance for common team management tasks through natural language queries.

**Hackathon Deadline: June 11, 2026**

## Technology Stack

- **AI Model**: Google Gemini 2.0 Flash
- **Agent Framework**: Google ADK (Agent Development Kit)
- **Database**: MongoDB Atlas (Free Tier)
- **Language**: Python 3.11+
- **IDE**: PyCharm
- **Key Dependencies**: google-adk, pymongo, python-dotenv

## Common Commands

### Setup & Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Edit .env and add your MONGODB_URI and GOOGLE_API_KEY

# Seed the database with sample data
python src/seed_data.py

# Run the agent CLI
python src/agent.py
```

### Development

```bash
# Run the agent interactively
python src/agent.py

# Reseed the database (WARNING: drops all existing data)
python src/seed_data.py
```

## Architecture

### Agent Tools

The agent has access to 7 function tools defined in `src/agent.py`:

1. **get_all_players()** - Returns all team players with statistics
2. **get_available_players()** - Returns only available players (not injured/suspended)
3. **get_top_scorers(limit)** - Returns top goal scorers
4. **get_recent_games(limit)** - Returns recent game results
5. **get_season_record()** - Returns season win/loss/draw record
6. **suggest_lineup()** - Suggests optimal lineup based on available players and performance
7. **add_game_result(opponent, score_us, score_them, notes)** - Records new game results

### Database Schema

MongoDB collections in the `hockey_agent` database:

**players**
- name, number, position (Goalie/Defense/Forward), shoots (L/R)
- goals, assists
- available (boolean - tracks injuries/suspensions)

**games**
- date, opponent, home (boolean)
- score_us, score_them, result (W/L/D)
- scorers (list), notes

**lineups**
- game_opponent, date
- goalie, lines (array of line configurations with forwards and defense)

### Agent Configuration

The agent uses a system prompt that defines its role as a helpful scout and team manager. It's designed to:
- Provide friendly, direct responses
- Explain reasoning behind lineup suggestions
- Handle queries about player statistics, availability, and team performance

### Session Management

The agent uses Google ADK's `InMemorySessionService` for local CLI sessions. Each session is tied to a "trainer" user and maintains conversation context.

## Environment Variables

Required in `.env`:
- `MONGODB_URI` - MongoDB Atlas connection string
- `GOOGLE_CLOUD_PROJECT` - Google Cloud project ID (required for Vertex AI)

**Note**: The agent now uses Vertex AI (not Google AI API) for better quotas. Authentication is via `gcloud auth application-default login`.

## Example Agent Queries

- "Who is available for Saturday?"
- "Suggest a lineup"
- "Record result: 3:1 against EHC Eagles"
- "Show me the top 3 scorers"
- "What is our season record?"

## Project Status

- [x] Project structure set up
- [x] GitHub repo created
- [x] Sample data model defined (players, games, lineups)
- [x] Basic agent.py with 7 tools written
- [x] All documentation translated to English
- [x] MongoDB Atlas connected and seeded ✅
- [x] Agent running with Vertex AI ✅
- [x] MongoDB MCP server integrated ✅
- [ ] Google Cloud Agent Builder deployment
- [ ] Frontend / demo UI
- [ ] Demo video recorded
- [ ] Devpost submission completed

## Hackathon Requirements

- Must use Google Cloud Agent Builder
- Must integrate MongoDB MCP server
- Must be built with Gemini
- Needs public GitHub repo with MIT license
- Needs ~3 min demo video
- Needs hosted project URL

## Next Steps (in priority order)

1. Run `python src/seed_data.py` to populate MongoDB Atlas
2. Run `python src/agent.py` and test basic queries
3. Fix any import/dependency issues with Google ADK
4. Add MongoDB MCP server integration
5. Deploy to Google Cloud Agent Builder
6. Build simple web UI for demo
7. Record demo video
8. Complete Devpost submission

## Coding Conventions

- All code and comments in English
- Type hints on all functions
- Each tool function has a clear docstring (used by the agent for understanding tool capabilities)
