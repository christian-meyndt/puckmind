# 🏒 Hockey Scout & Team Manager Agent

An AI agent for amateur ice hockey teams – built with Google Gemini, Google ADK, and MongoDB.

Submitted for the **Google Cloud Rapid Agent Hackathon** (MongoDB Track).

---

## What can the agent do?

### 🎯 Core Features
- **Visual lineup suggestions** with hockey rink layout
- **Position-specific analytics** (forwards vs defenders vs goalies)
- **Comprehensive player statistics** (shooting %, faceoff %, blocked shots, GAA, save %)
- **Game tracking** and season records
- **MongoDB MCP server integration** (hackathon requirement)

### 🌟 Wow-Factor Features
- **Smart availability warnings** - "Only 3 defenders available - consider calling up a forward"
- **Player form tracking** - Identifies hot/cold streaks with recommendations
- **Opponent analysis** - Historical performance and tactical insights
- **Season predictions** - "At current pace you'll finish 3rd place"
- **Training suggestions** - Position-specific drills based on weaknesses
- **Post-game summaries** - Auto-generated for WhatsApp/website/Twitter

### 📊 Advanced Analytics
- 17 specialized agent tools
- 17 players with professional-grade statistics
- 12 games of season history
- Position-aware recommendations

**Example queries:**
```
"Suggest a lineup for the next game"
"Show me our top forwards with offensive stats"
"Who are our best defenders? Show defensive stats"
"Check player availability and warn about lineup issues"
"Who's on a hot or cold streak?"
"Analyze our history against EHC Eagles"
"Predict our final standing this season"
"Suggest training exercises based on our weaknesses"
```

---

## Setup

### 1. Clone repository
```bash
git clone https://github.com/christian-meyndt/puckmind
cd puckmind
```

### 2. Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set environment variables
Create a `.env` file with:
```
MONGODB_URI=your_mongodb_atlas_connection_string
GOOGLE_CLOUD_PROJECT=your_google_cloud_project_id
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_LOCATION=us-central1
```

### 4. Authenticate with Google Cloud
```bash
gcloud auth application-default login
```

### 5. Seed the database
```bash
python -m src.database.seed_data
```

### 6. Start the web UI (recommended)
```bash
streamlit run app.py
```
Then open http://localhost:8501

Or run the CLI version:
```bash
python src/agent.py
```

---

## Technology Stack

| Component | Technology |
|---|---|
| AI Model | Google Gemini 2.5 Flash (via Vertex AI) |
| Agent Framework | Google ADK (Agent Development Kit) |
| Database | MongoDB Atlas |
| Protocol | Model Context Protocol (MCP) |
| Web UI | Streamlit |
| Language | Python 3.12+ |

---

## Project Structure

```
puckmind/
├── app.py                      # Streamlit web UI (506 lines, refactored)
├── src/
│   ├── config.py               # Centralized configuration
│   ├── database/
│   │   ├── connection.py       # Singleton MongoDB connection
│   │   └── seed_data.py        # Sample data with 17 players, 12 games
│   ├── ui/
│   │   └── game_wizard_ui.py   # 5-step game addition wizard
│   ├── agent.py                # Main agent with 14 tools
│   ├── agent_enhanced.py       # Wow-factor features (5 analytics tools)
│   ├── game_wizard.py          # Game stats helper functions
│   └── lineup_visualizer.py    # Visual lineup card generator
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in git)
├── CLAUDE.md                   # Developer documentation
├── ARCHITECTURE_REVIEW.md      # Architecture analysis & recommendations
├── CHANGELOG.md                # Project changelog
├── MONGODB_MCP_INTEGRATION.md  # MCP integration details
├── VERTEX_AI_SETUP.md          # Vertex AI setup guide
└── README.md
```

---

## Key Features Showcase

### 🏒 Visual Lineup Card
When you ask "Suggest a lineup", the agent displays a visual hockey rink layout:

```
═══════════════════════════════════════════════════════════
                      🏒 LINEUP CARD 🏒
═══════════════════════════════════════════════════════════

                         LINE 1

                    [ Markus Huber  ]
                           🥅

          [ Stefan Bauer  ]    [ David Fischer ]
                      🛡️                  🛡️

  [ Lukas Schäfer ] [ Felix Wagner  ] [ Michael Braun ]
           ⚡️                 ⚡️                 ⚡️
```

This instant visual understanding is what makes the agent memorable!

### 📊 Position-Specific Analytics

**Forwards** (Offensive Focus):
- Goals, Assists, Shooting %, Faceoff %
- Example: "Lukas Schäfer - 18.9% shooting, 54.2% faceoff wins"

**Defenders** (Defensive Focus):
- Plus/Minus, Blocked Shots, Hits
- Example: "Stefan Bauer - +8 plus/minus, 28 blocked shots"

**Goalies** (Performance Focus):
- GAA, Save %, Wins, Shutouts
- Example: "Markus Huber - 2.3 GAA, .918 save %"

---

## Deployment

**Live Demo:** Deployed on Google Cloud Run (URL available after deployment completes)

See [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

**Quick Deploy:**
```bash
# With Docker installed
./deploy-local.sh

# Or via Google Cloud Shell
# See DEPLOYMENT_GUIDE.md for step-by-step instructions
```

---

## Testing

**Run Test Suite:**
```bash
# Install nox
pip install nox

# Run all tests with coverage
nox -s tests

# Run quick tests
nox -s quick_tests

# Run all quality checks (tests, lint, format, type, security)
nox -s full_check
```

**Test Coverage:**
- 38 test cases across 6 modules
- European points system
- Quick game entry parser
- Schedule management
- Attendance tracking
- Ice time analysis
- Player availability

See [`tests/README.md`](tests/README.md) for detailed test documentation.

---

## Demo Video

Coming soon - will showcase all key features in 3 minutes!

---

## Development

**Built with modern AI-assisted development practices** using Claude Code to accelerate prototyping and iteration. All architecture decisions, feature design, integration work, and testing were directed by the developer.

---

## License

MIT License – see LICENSE
