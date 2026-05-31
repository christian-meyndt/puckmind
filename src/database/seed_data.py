"""
Hockey Agent – Seed Script
Populates MongoDB Atlas with sample data for Day 1.

Usage:
  1. Set MONGODB_URI in .env (see README)
  2. python -m src.database.seed_data
"""

from datetime import datetime, timedelta
from src.database.connection import get_db

# ── Connection ────────────────────────────────────────────────
print("Connecting to MongoDB Atlas...")
print("Note: Using centralized database connection\n")

db = get_db()

# Test the connection
try:
    from src.database.connection import get_client
    client = get_client()
    client.admin.command('ping')
    print("✓ MongoDB connection successful!\n")
except Exception as e:
    print(f"✗ Connection test failed: {e}\n")
    raise

# ── Clear collections (for clean restart) ─────────────────────
db.players.drop()
db.games.drop()
db.lineups.drop()

# ── 1. Players ────────────────────────────────────────────────
# Added fields: age, avg_ice_time (minutes per game), status (veteran/regular/developing)
players = [
    # Goalies
    {
        "name": "Markus Huber", "number": 1, "position": "Goalie", "shoots": "L",
        "age": 28, "status": "veteran",
        "goals": 0, "assists": 2, "available": True,
        "games_played": 8, "avg_ice_time": 55.0, "wins": 5, "losses": 2, "gaa": 2.3, "save_pct": 0.918, "shutouts": 1,
        "shots_against": 245, "saves": 225
    },
    {
        "name": "Andreas Richter", "number": 44, "position": "Goalie", "shoots": "L",
        "age": 22, "status": "developing",
        "goals": 0, "assists": 0, "available": True,
        "games_played": 4, "avg_ice_time": 55.0, "wins": 2, "losses": 2, "gaa": 2.8, "save_pct": 0.892, "shutouts": 0,
        "shots_against": 120, "saves": 107
    },

    # Defense
    {
        "name": "Stefan Bauer", "number": 4, "position": "Defense", "shoots": "L",
        "age": 30, "status": "veteran",
        "goals": 5, "assists": 12, "available": True,
        "games_played": 12, "avg_ice_time": 22.5, "plus_minus": 8, "pim": 14, "shots": 48, "blocked_shots": 28, "hits": 45
    },
    {
        "name": "Jonas Kramer", "number": 7, "position": "Defense", "shoots": "R",
        "age": 27, "status": "regular",
        "goals": 2, "assists": 5, "available": False,  # injured
        "games_played": 8, "avg_ice_time": 18.5, "plus_minus": 2, "pim": 22, "shots": 28, "blocked_shots": 18, "hits": 32
    },
    {
        "name": "David Fischer", "number": 21, "position": "Defense", "shoots": "L",
        "age": 26, "status": "regular",
        "goals": 3, "assists": 10, "available": True,
        "games_played": 12, "avg_ice_time": 20.8, "plus_minus": 6, "pim": 8, "shots": 42, "blocked_shots": 32, "hits": 38
    },
    {
        "name": "Thomas Weber", "number": 33, "position": "Defense", "shoots": "R",
        "age": 29, "status": "regular",
        "goals": 2, "assists": 9, "available": True,
        "games_played": 12, "avg_ice_time": 19.3, "plus_minus": 4, "pim": 18, "shots": 35, "blocked_shots": 25, "hits": 41
    },
    {
        "name": "Marco Schmidt", "number": 5, "position": "Defense", "shoots": "L",
        "age": 21, "status": "developing",
        "goals": 1, "assists": 7, "available": True,
        "games_played": 10, "avg_ice_time": 14.2, "plus_minus": 1, "pim": 12, "shots": 22, "blocked_shots": 20, "hits": 28
    },

    # Forwards - Top line (hot streak players)
    {
        "name": "Lukas Schäfer", "number": 10, "position": "Forward", "shoots": "L",
        "age": 29, "status": "veteran",
        "goals": 18, "assists": 15, "available": True,
        "games_played": 12, "avg_ice_time": 20.5, "plus_minus": 12, "pim": 6, "shots": 95, "shooting_pct": 18.9, "hits": 22, "faceoff_pct": 54.2
    },
    {
        "name": "Felix Wagner", "number": 11, "position": "Forward", "shoots": "R",
        "age": 27, "status": "veteran",
        "goals": 14, "assists": 19, "available": True,
        "games_played": 12, "avg_ice_time": 19.8, "plus_minus": 15, "pim": 4, "shots": 88, "shooting_pct": 15.9, "hits": 18, "faceoff_pct": 48.5
    },
    {
        "name": "Kevin Müller", "number": 23, "position": "Forward", "shoots": "R",
        "age": 26, "status": "regular",
        "goals": 12, "assists": 8, "available": False,  # suspended
        "games_played": 10, "avg_ice_time": 17.2, "plus_minus": 8, "pim": 38, "shots": 72, "shooting_pct": 16.7, "hits": 35, "faceoff_pct": 51.8
    },

    # Forwards - Second line
    {
        "name": "Tobias Klein", "number": 14, "position": "Forward", "shoots": "L",
        "age": 25, "status": "regular",
        "goals": 9, "assists": 11, "available": True,
        "games_played": 12, "avg_ice_time": 16.5, "plus_minus": 5, "pim": 10, "shots": 65, "shooting_pct": 13.8, "hits": 28, "faceoff_pct": 52.3
    },
    {
        "name": "Michael Braun", "number": 17, "position": "Forward", "shoots": "R",
        "age": 28, "status": "regular",
        "goals": 7, "assists": 14, "available": True,
        "games_played": 12, "avg_ice_time": 15.8, "plus_minus": 6, "pim": 8, "shots": 58, "shooting_pct": 12.1, "hits": 24, "faceoff_pct": 49.2
    },
    {
        "name": "Patrick Schulz", "number": 27, "position": "Forward", "shoots": "L",
        "age": 24, "status": "regular",
        "goals": 8, "assists": 10, "available": True,
        "games_played": 12, "avg_ice_time": 15.3, "plus_minus": 4, "pim": 16, "shots": 62, "shooting_pct": 12.9, "hits": 31, "faceoff_pct": 50.5
    },

    # Forwards - Third line / depth (developing players with low ice time)
    {
        "name": "Simon Hoffmann", "number": 19, "position": "Forward", "shoots": "R",
        "age": 22, "status": "developing",
        "goals": 6, "assists": 5, "available": True,
        "games_played": 11, "avg_ice_time": 12.3, "plus_minus": 2, "pim": 12, "shots": 48, "shooting_pct": 12.5, "hits": 26, "faceoff_pct": 47.8
    },
    {
        "name": "Florian Meyer", "number": 25, "position": "Forward", "shoots": "L",
        "age": 20, "status": "developing",
        "goals": 4, "assists": 7, "available": True,
        "games_played": 12, "avg_ice_time": 10.8, "plus_minus": 1, "pim": 6, "shots": 42, "shooting_pct": 9.5, "hits": 19, "faceoff_pct": 45.2
    },
    {
        "name": "Dominik Schneider", "number": 28, "position": "Forward", "shoots": "R",
        "age": 21, "status": "developing",
        "goals": 3, "assists": 4, "available": True,
        "games_played": 10, "avg_ice_time": 9.5, "plus_minus": -1, "pim": 8, "shots": 35, "shooting_pct": 8.6, "hits": 21, "faceoff_pct": 46.5
    },
    {
        "name": "Jan Becker", "number": 91, "position": "Forward", "shoots": "L",
        "age": 19, "status": "developing",
        "goals": 2, "assists": 3, "available": True,  # cold streak, needs development
        "games_played": 9, "avg_ice_time": 8.2, "plus_minus": -3, "pim": 14, "shots": 28, "shooting_pct": 7.1, "hits": 16, "faceoff_pct": 42.8
    },
]

result = db.players.insert_many(players)
print(f"✅ {len(result.inserted_ids)} players inserted")

# ── 2. Games (expanded season: 12 games with European points system) ──
# European system: W=3pts, OTW=2pts, OTL=1pt, L=0pts
today = datetime.now()
games = [
    # Early season
    {
        "date": today - timedelta(days=84),
        "opponent": "HC Lions",
        "home": True,
        "score_us": 3,
        "score_them": 2,
        "result": "OTW",  # Overtime win (2 points)
        "scorers": ["Lukas Schäfer", "Felix Wagner", "Stefan Bauer"],
        "notes": "Season opener, thrilling OT finish. Schäfer scored winner in OT.",
    },
    {
        "date": today - timedelta(days=77),
        "opponent": "EV Bears",
        "home": False,
        "score_us": 2,
        "score_them": 4,
        "result": "L",  # Regular loss (0 points)
        "scorers": ["Tobias Klein", "Michael Braun"],
        "notes": "Struggled on the road, weak penalty kill. Lost in regulation.",
    },
    {
        "date": today - timedelta(days=70),
        "opponent": "SC Falcons",
        "home": True,
        "score_us": 5,
        "score_them": 2,
        "result": "W",  # Regular win (3 points)
        "scorers": ["Lukas Schäfer", "Lukas Schäfer", "Felix Wagner", "Kevin Müller", "Patrick Schulz"],
        "notes": "Dominated from start to finish. Schäfer with 2 goals.",
    },
    {
        "date": today - timedelta(days=63),
        "opponent": "EHC Eagles",
        "home": False,
        "score_us": 2,
        "score_them": 3,
        "result": "OTL",  # Overtime loss (1 point)
        "scorers": ["Felix Wagner", "Kevin Müller"],
        "notes": "Tough defensive battle, lost in shootout. At least earned 1 point.",
    },
    # Mid-season
    {
        "date": today - timedelta(days=56),
        "opponent": "HC Thunder",
        "home": True,
        "score_us": 6,
        "score_them": 3,
        "result": "W",  # Regular win (3 points)
        "scorers": ["Lukas Schäfer", "Lukas Schäfer", "Felix Wagner", "Felix Wagner", "Kevin Müller", "Stefan Bauer"],
        "notes": "Offensive explosion, Wagner and Schäfer on fire. Dominant win.",
    },
    {
        "date": today - timedelta(days=49),
        "opponent": "HC Lions",
        "home": False,
        "score_us": 2,
        "score_them": 3,
        "result": "OTL",  # Overtime loss (1 point)
        "scorers": ["Michael Braun", "Tobias Klein"],
        "notes": "Close loss in overtime. Need better 3rd period execution.",
    },
    {
        "date": today - timedelta(days=42),
        "opponent": "EV Bears",
        "home": True,
        "score_us": 4,
        "score_them": 1,
        "result": "W",  # Regular win (3 points)
        "scorers": ["Felix Wagner", "Lukas Schäfer", "Patrick Schulz", "David Fischer"],
        "notes": "Revenge game! Dominated in all zones after last week's loss.",
    },
    {
        "date": today - timedelta(days=35),
        "opponent": "SC Falcons",
        "home": False,
        "score_us": 2,
        "score_them": 5,
        "result": "L",  # Regular loss (0 points)
        "scorers": ["Kevin Müller", "Tobias Klein"],
        "notes": "Bad penalties killed us, 5 powerplay goals against. Rough night.",
    },
    # Recent games
    {
        "date": today - timedelta(days=28),
        "opponent": "EHC Eagles",
        "home": True,
        "score_us": 4,
        "score_them": 3,
        "result": "OTW",  # Overtime win (2 points)
        "scorers": ["Lukas Schäfer", "Felix Wagner", "Lukas Schäfer", "Tobias Klein"],
        "notes": "Exciting comeback! Down 3-2 in 3rd, tied it late, won in OT.",
    },
    {
        "date": today - timedelta(days=21),
        "opponent": "HC Thunder",
        "home": False,
        "score_us": 3,
        "score_them": 4,
        "result": "OTL",  # Overtime loss (1 point)
        "scorers": ["Felix Wagner", "Lukas Schäfer", "Michael Braun"],
        "notes": "Lost in shootout after tie game. At least got a point on the road.",
    },
    {
        "date": today - timedelta(days=14),
        "opponent": "HC Lions",
        "home": True,
        "score_us": 5,
        "score_them": 1,
        "result": "W",  # Regular win (3 points)
        "scorers": ["Felix Wagner", "Felix Wagner", "Lukas Schäfer", "Patrick Schulz", "Stefan Bauer"],
        "notes": "Best performance of the season! Wagner with 2 goals, complete team effort.",
    },
    {
        "date": today - timedelta(days=7),
        "opponent": "EHC Eagles",
        "home": False,
        "score_us": 3,
        "score_them": 1,
        "result": "W",  # Regular win (3 points)
        "scorers": ["Lukas Schäfer", "Felix Wagner", "Patrick Schulz"],
        "notes": "Disciplined game, goalie Markus Weber was outstanding. 3-game streak!",
    },
]

# Points summary for reference:
# Regular wins (W): 5 games × 3 pts = 15 pts
# OT/SO wins (OTW): 2 games × 2 pts = 4 pts
# OT/SO losses (OTL): 3 games × 1 pt = 3 pts
# Regular losses (L): 2 games × 0 pts = 0 pts
# Total: 22 points from 12 games (7W-2L-3OTL = 22pts)

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
