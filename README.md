# 🏒 Hockey Scout & Team Manager Agent

An AI agent for amateur ice hockey teams – built with Google Gemini, Google ADK, and MongoDB.

Submitted for the **Google Cloud Rapid Agent Hackathon** (MongoDB Track).

---

## What can the agent do?

- Query player statistics and availability
- Automatically suggest lineups (based on available players)
- Record game results
- Display season record
- Identify top scorers

**Example queries:**
```
"Who is available for Saturday?"
"Suggest a lineup"
"Record result: 3:1 against EHC Eagles"
"Show me the top 3 scorers"
"What is our season record?"
```

---

## Setup

### 1. Clone repository
```bash
git clone https://github.com/YOUR_USERNAME/hockey-agent
cd hockey-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set environment variables
```bash
cp .env.example .env
# Open .env and add your MongoDB URI + Google API Key
```

### 4. Seed the database
```bash
python seed_data.py
```

### 5. Start the agent
```bash
python agent.py
```

---

## Technology Stack

| Component | Technology |
|---|---|
| AI Model | Google Gemini 2.0 Flash |
| Agent Framework | Google ADK (Agent Development Kit) |
| Database | MongoDB Atlas (Free Tier) |
| Language | Python 3.11+ |

---

## Project Structure

```
hockey-agent/
├── agent.py          # Main agent with tools
├── seed_data.py      # Sample data for MongoDB
├── requirements.txt
├── .env.example      # Template for environment variables
└── README.md
```

---

## License

MIT License – see LICENSE
