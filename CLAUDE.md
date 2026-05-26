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

The agent has access to **17 function tools** across three files:

**Core Tools (`src/agent.py`):**
1. **get_all_players()** - Returns all team players with statistics
2. **get_available_players()** - Returns only available players (not injured/suspended)
3. **get_top_scorers(limit)** - Returns top goal scorers
4. **get_recent_games(limit)** - Returns recent game results
5. **get_season_record()** - Returns season win/loss/draw record
6. **suggest_lineup()** - Visual lineup card with hockey rink layout
7. **add_game_result(opponent, score_us, score_them, notes)** - Records new game results
8. **suggest_training_exercises()** - Analyzes weaknesses and suggests drills
9. **get_player_detailed_stats(player_name)** - Position-specific detailed stats
10. **get_goalie_stats()** - GAA, save %, wins, shutouts
11. **get_top_forwards()** - Top forwards with offensive stats (shooting %, faceoff %)
12. **get_top_defenders()** - Top defenders with defensive stats (plus/minus, blocked shots)

**Enhanced Analytics Tools (`src/agent_enhanced.py`):**
13. **get_smart_availability_warnings()** - Proactive lineup issue alerts
14. **analyze_opponent(opponent_name)** - Historical performance vs opponent
15. **track_player_form()** - Hot/cold streak identification
16. **generate_post_game_summary(opponent, score_us, score_them)** - Social media ready summaries
17. **predict_season_finish()** - Season standings projection

### Database Schema

MongoDB collections in the `hockey_agent` database:

**players** (17 players with comprehensive stats)
- Basic: name, number, position (Goalie/Defense/Forward), shoots (L/R), available
- Scoring: goals, assists, points
- Advanced (Forwards): shooting_pct, faceoff_pct, shots
- Advanced (Defenders): plus_minus, blocked_shots, hits, pim
- Advanced (Goalies): games_played, wins, losses, gaa, save_pct, shutouts, shots_against, saves

**games** (12 games of season history)
- date, opponent, home (boolean)
- score_us, score_them, result (W/L/D)
- scorers (list), notes (detailed game observations)

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

**Basic Queries:**
- "Who is available for Saturday?"
- "Show me the top 3 scorers"
- "What is our season record?"
- "Record result: 3:1 against EHC Eagles"

**Advanced Analytics:**
- "Suggest a lineup" → Visual hockey rink layout with full lineup
- "Show me our top forwards with offensive stats" → Goals, assists, shooting %, faceoff %
- "Who are our best defenders?" → Plus/minus, blocked shots, hits
- "What are our goalie statistics?" → GAA, save %, shutouts

**Wow-Factor Features:**
- "Check player availability and warn about lineup issues" → Smart proactive alerts
- "Who's on a hot or cold streak?" → Form tracking with recommendations
- "Analyze our history against EHC Eagles" → Opponent scouting report
- "Predict our final standing this season" → Season projections
- "Suggest training exercises based on our weaknesses" → Position-specific drills

## Project Status

- [x] Project structure set up
- [x] GitHub repo created
- [x] Sample data model defined (players, games, lineups)
- [x] Agent with 17 tools (up from 7) ✅
- [x] All documentation translated to English
- [x] MongoDB Atlas connected and seeded ✅
- [x] Agent running with Vertex AI (Gemini 2.5 Flash) ✅
- [x] MongoDB MCP server integrated ✅
- [x] Streamlit web UI built ✅
- [x] Visual lineup card (wow-factor) ✅
- [x] Position-specific analytics ✅
- [x] Enhanced statistics (shooting %, faceoff %, blocked shots, GAA, etc.) ✅
- [x] Wow-factor features (form tracking, opponent analysis, predictions) ✅
- [ ] Google Cloud Agent Builder deployment
- [ ] Demo video recorded
- [ ] Devpost submission completed

## Hackathon Requirements

- Must use Google Cloud Agent Builder
- Must integrate MongoDB MCP server
- Must be built with Gemini
- Needs public GitHub repo with MIT license
- Needs ~3 min demo video
- Needs hosted project URL

## Running the Agent

### Command Line Interface
```bash
cd /Users/christianmeyndt/PyCharmMiscProject/puckmind
source venv/bin/activate
python src/agent.py
```

### Web Interface (Recommended for Demo)
```bash
cd /Users/christianmeyndt/PyCharmMiscProject/puckmind
source venv/bin/activate
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

### Reseed Database (if needed)
```bash
source venv/bin/activate
python src/seed_data.py
```

## Next Steps (Hackathon Submission)

1. ✅ ~~Build agent with MongoDB MCP integration~~
2. ✅ ~~Create comprehensive statistics and analytics~~
3. ✅ ~~Build Streamlit web UI with wow-factor features~~
4. **Deploy to Google Cloud Agent Builder** (in progress)
5. **Record 3-minute demo video** showing key features
6. **Complete Devpost submission** (before June 11, 2026)

## Coding Conventions

- All code and comments in English
- Type hints on all functions
- Each tool function has a clear docstring (used by the agent for understanding tool capabilities)
