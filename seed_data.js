// MongoDB Shell Seed Script for PuckMind
// Run with: mongosh "YOUR_MONGODB_URI" seed_data.js

// Switch to hockey_agent database
db = db.getSiblingDB('hockey_agent');

// Clear existing data
print('Clearing existing collections...');
db.players.drop();
db.games.drop();
db.lineups.drop();

// Insert players
print('Inserting players...');
db.players.insertMany([
    {"name": "Markus Huber",    "number": 1,  "position": "Goalie",   "shoots": "L", "goals": 0,  "assists": 2,  "available": true},
    {"name": "Stefan Bauer",    "number": 4,  "position": "Defense",  "shoots": "L", "goals": 3,  "assists": 8,  "available": true},
    {"name": "Jonas Kramer",    "number": 7,  "position": "Defense",  "shoots": "R", "goals": 2,  "assists": 5,  "available": false},
    {"name": "Lukas Schäfer",   "number": 10, "position": "Forward",  "shoots": "L", "goals": 12, "assists": 9,  "available": true},
    {"name": "Felix Wagner",    "number": 11, "position": "Forward",  "shoots": "R", "goals": 8,  "assists": 14, "available": true},
    {"name": "Tobias Klein",    "number": 14, "position": "Forward",  "shoots": "L", "goals": 6,  "assists": 7,  "available": true},
    {"name": "Michael Braun",   "number": 17, "position": "Forward",  "shoots": "R", "goals": 4,  "assists": 11, "available": true},
    {"name": "David Fischer",   "number": 21, "position": "Defense",  "shoots": "L", "goals": 1,  "assists": 6,  "available": true},
    {"name": "Kevin Müller",    "number": 23, "position": "Forward",  "shoots": "R", "goals": 9,  "assists": 5,  "available": false},
    {"name": "Patrick Schulz",  "number": 27, "position": "Forward",  "shoots": "L", "goals": 5,  "assists": 8,  "available": true},
    {"name": "Thomas Weber",    "number": 33, "position": "Defense",  "shoots": "R", "goals": 2,  "assists": 9,  "available": true},
    {"name": "Andreas Richter", "number": 44, "position": "Goalie",   "shoots": "L", "goals": 0,  "assists": 0,  "available": true}
]);
print('✅ ' + db.players.countDocuments() + ' players inserted');

// Insert games
print('Inserting games...');
const today = new Date();
db.games.insertMany([
    {
        "date": new Date(today.getTime() - 28 * 24 * 60 * 60 * 1000),
        "opponent": "EHC Eagles",
        "home": true,
        "score_us": 4,
        "score_them": 2,
        "result": "W",
        "scorers": ["Lukas Schäfer", "Felix Wagner", "Lukas Schäfer", "Tobias Klein"],
        "notes": "Good powerplay, weak PK in 2nd period"
    },
    {
        "date": new Date(today.getTime() - 21 * 24 * 60 * 60 * 1000),
        "opponent": "SC Falcons",
        "home": false,
        "score_us": 1,
        "score_them": 3,
        "result": "L",
        "scorers": ["Michael Braun"],
        "notes": "Too many penalties, goalie had an off day"
    },
    {
        "date": new Date(today.getTime() - 14 * 24 * 60 * 60 * 1000),
        "opponent": "EV Bears",
        "home": true,
        "score_us": 5,
        "score_them": 1,
        "result": "W",
        "scorers": ["Felix Wagner", "Felix Wagner", "Lukas Schäfer", "Patrick Schulz", "Stefan Bauer"],
        "notes": "Best performance of the season, very solid defense"
    },
    {
        "date": new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000),
        "opponent": "HC Lions",
        "home": false,
        "score_us": 2,
        "score_them": 2,
        "result": "D",
        "scorers": ["Tobias Klein", "Michael Braun"],
        "notes": "Draw after overtime, lost shootout"
    },
    {
        "date": new Date(today.getTime() - 2 * 24 * 60 * 60 * 1000),
        "opponent": "EHC Eagles",
        "home": false,
        "score_us": 3,
        "score_them": 1,
        "result": "W",
        "scorers": ["Lukas Schäfer", "Felix Wagner", "Patrick Schulz"],
        "notes": "Disciplined game, goalie very strong"
    }
]);
print('✅ ' + db.games.countDocuments() + ' games inserted');

// Insert lineup
print('Inserting lineups...');
db.lineups.insertMany([
    {
        "game_opponent": "EHC Eagles",
        "date": new Date(today.getTime() - 28 * 24 * 60 * 60 * 1000),
        "goalie": "Markus Huber",
        "lines": [
            {
                "line": 1,
                "left_wing": "Lukas Schäfer",
                "center": "Felix Wagner",
                "right_wing": "Tobias Klein",
                "left_defense": "Stefan Bauer",
                "right_defense": "David Fischer"
            },
            {
                "line": 2,
                "left_wing": "Michael Braun",
                "center": "Patrick Schulz",
                "right_wing": "Kevin Müller",
                "left_defense": "Jonas Kramer",
                "right_defense": "Thomas Weber"
            }
        ]
    }
]);
print('✅ ' + db.lineups.countDocuments() + ' lineups inserted');

print('\n🏒 Database ready! Collections:');
print('   players: ' + db.players.countDocuments() + ' documents');
print('   games:   ' + db.games.countDocuments() + ' documents');
print('   lineups: ' + db.lineups.countDocuments() + ' documents');
