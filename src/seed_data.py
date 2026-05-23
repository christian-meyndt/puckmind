"""
Hockey Agent – Seed Script
Populates MongoDB Atlas with sample data for Day 1.

Usage:
  1. Set MONGODB_URI in .env (see README)
  2. python seed_data.py
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import ssl
import certifi

# Load environment variables from .env file
load_dotenv()

# ── Connection ────────────────────────────────────────────────
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

# Try connection with ssl=False (disable SSL verification - not for production!)
print("Connecting to MongoDB Atlas...")
print("Note: Using ssl_cert_reqs=CERT_NONE for compatibility\n")

import ssl as ssl_lib
client = MongoClient(
    MONGODB_URI,
    ssl=True,
    ssl_cert_reqs=ssl_lib.CERT_NONE,
    serverSelectionTimeoutMS=10000
)

# Test the connection
try:
    client.admin.command('ping')
    print("✓ MongoDB connection successful!\n")
except Exception as e:
    print(f"✗ Connection test failed: {e}\n")
    raise

db = client["hockey_agent"]

# ── Clear collections (for clean restart) ─────────────────────
db.players.drop()
db.games.drop()
db.lineups.drop()

# ── 1. Players ────────────────────────────────────────────────
players = [
    {"name": "Markus Huber",    "number": 1,  "position": "Goalie",     "shoots": "L", "goals": 0,  "assists": 2,  "available": True},
    {"name": "Stefan Bauer",    "number": 4,  "position": "Defense",    "shoots": "L", "goals": 3,  "assists": 8,  "available": True},
    {"name": "Jonas Kramer",    "number": 7,  "position": "Defense",    "shoots": "R", "goals": 2,  "assists": 5,  "available": False},  # injured
    {"name": "Lukas Schäfer",   "number": 10, "position": "Forward",   "shoots": "L", "goals": 12, "assists": 9,  "available": True},
    {"name": "Felix Wagner",    "number": 11, "position": "Forward",    "shoots": "R", "goals": 8,  "assists": 14, "available": True},
    {"name": "Tobias Klein",    "number": 14, "position": "Forward",    "shoots": "L", "goals": 6,  "assists": 7,  "available": True},
    {"name": "Michael Braun",   "number": 17, "position": "Forward",    "shoots": "R", "goals": 4,  "assists": 11, "available": True},
    {"name": "David Fischer",   "number": 21, "position": "Defense",    "shoots": "L", "goals": 1,  "assists": 6,  "available": True},
    {"name": "Kevin Müller",    "number": 23, "position": "Forward",    "shoots": "R", "goals": 9,  "assists": 5,  "available": False},  # suspended
    {"name": "Patrick Schulz",  "number": 27, "position": "Forward",    "shoots": "L", "goals": 5,  "assists": 8,  "available": True},
    {"name": "Thomas Weber",    "number": 33, "position": "Defense",    "shoots": "R", "goals": 2,  "assists": 9,  "available": True},
    {"name": "Andreas Richter", "number": 44, "position": "Goalie",     "shoots": "L", "goals": 0,  "assists": 0,  "available": True},
]

result = db.players.insert_many(players)
print(f"✅ {len(result.inserted_ids)} players inserted")

# ── 2. Games (last 5) ─────────────────────────────────────────
today = datetime.now()
games = [
    {
        "date": today - timedelta(days=28),
        "opponent": "EHC Eagles",
        "home": True,
        "score_us": 4,
        "score_them": 2,
        "result": "W",
        "scorers": ["Lukas Schäfer", "Felix Wagner", "Lukas Schäfer", "Tobias Klein"],
        "notes": "Good powerplay, weak PK in 2nd period",
    },
    {
        "date": today - timedelta(days=21),
        "opponent": "SC Falcons",
        "home": False,
        "score_us": 1,
        "score_them": 3,
        "result": "L",
        "scorers": ["Michael Braun"],
        "notes": "Too many penalties, goalie had an off day",
    },
    {
        "date": today - timedelta(days=14),
        "opponent": "EV Bears",
        "home": True,
        "score_us": 5,
        "score_them": 1,
        "result": "W",
        "scorers": ["Felix Wagner", "Felix Wagner", "Lukas Schäfer", "Patrick Schulz", "Stefan Bauer"],
        "notes": "Best performance of the season, very solid defense",
    },
    {
        "date": today - timedelta(days=7),
        "opponent": "HC Lions",
        "home": False,
        "score_us": 2,
        "score_them": 2,
        "result": "D",
        "scorers": ["Tobias Klein", "Michael Braun"],
        "notes": "Draw after overtime, lost shootout",
    },
    {
        "date": today - timedelta(days=2),
        "opponent": "EHC Eagles",
        "home": False,
        "score_us": 3,
        "score_them": 1,
        "result": "W",
        "scorers": ["Lukas Schäfer", "Felix Wagner", "Patrick Schulz"],
        "notes": "Disciplined game, goalie very strong",
    },
]

result = db.games.insert_many(games)
print(f"✅ {len(result.inserted_ids)} games inserted")

# ── 3. Lineup (last home game) ────────────────────────────────
lineups = [
    {
        "game_opponent": "EHC Eagles",
        "date": today - timedelta(days=28),
        "goalie": "Markus Huber",
        "lines": [
            {
                "line": 1,
                "left_wing": "Lukas Schäfer",
                "center": "Felix Wagner",
                "right_wing": "Tobias Klein",
                "left_defense": "Stefan Bauer",
                "right_defense": "David Fischer",
            },
            {
                "line": 2,
                "left_wing": "Michael Braun",
                "center": "Patrick Schulz",
                "right_wing": "Kevin Müller",
                "left_defense": "Jonas Kramer",
                "right_defense": "Thomas Weber",
            },
        ],
    }
]

result = db.lineups.insert_many(lineups)
print(f"✅ {len(result.inserted_ids)} lineups inserted")

print("\n🏒 Database ready! Collections:")
print(f"   players : {db.players.count_documents({})} documents")
print(f"   games   : {db.games.count_documents({})} documents")
print(f"   lineups : {db.lineups.count_documents({})} documents")

client.close()
