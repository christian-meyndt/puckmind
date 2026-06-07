"""
Quick Database Verification Script
Check what's in MongoDB and verify UI displays it correctly
"""

from src.database import get_db
from datetime import datetime

db = get_db()

print("=" * 70)
print("PUCKMIND DATABASE VERIFICATION")
print("=" * 70)

# 1. Check Players
print("\n📊 PLAYERS")
print("-" * 70)
players = list(db.players.find({}, {"_id": 0}))
print(f"Total players: {len(players)}")
print(f"Available: {sum(1 for p in players if p.get('available'))}")
print(f"Unavailable: {sum(1 for p in players if not p.get('available'))}")

# Show players with new fields
print("\nPlayers with ice time data:")
for p in players[:5]:  # Show first 5
    age = p.get('age', 'N/A')
    status = p.get('status', 'N/A')
    ice_time = p.get('avg_ice_time', 'N/A')
    print(f"  {p['name']}: {age} yrs, {status}, {ice_time} min/game")

# 2. Check Games (European Points)
print("\n🏒 GAMES (European Points System)")
print("-" * 70)
games = list(db.games.find({}, {"_id": 0, "date": 1, "opponent": 1, "result": 1, "score_us": 1, "score_them": 1}).sort("date", -1))
print(f"Total games: {len(games)}")

# Count by result type
reg_wins = sum(1 for g in games if g.get("result") == "W")
ot_wins = sum(1 for g in games if g.get("result") == "OTW")
reg_losses = sum(1 for g in games if g.get("result") == "L")
ot_losses = sum(1 for g in games if g.get("result") in ["OTL", "D"])

print(f"Regular Wins (W): {reg_wins} × 3pts = {reg_wins * 3} pts")
print(f"OT/SO Wins (OTW): {ot_wins} × 2pts = {ot_wins * 2} pts")
print(f"OT/SO Losses (OTL): {ot_losses} × 1pt = {ot_losses * 1} pts")
print(f"Regular Losses (L): {reg_losses} × 0pts = 0 pts")
total_points = reg_wins * 3 + ot_wins * 2 + ot_losses * 1
print(f"TOTAL POINTS: {total_points}")
print(f"Record: {reg_wins + ot_wins}W - {reg_losses}L - {ot_losses}OTL")

print("\nRecent games:")
for game in games[:5]:
    result_label = {
        "W": "Win (3pts)",
        "OTW": "OT/SO Win (2pts)",
        "OTL": "OT/SO Loss (1pt)",
        "L": "Loss (0pts)",
        "D": "Draw (1pt)"
    }.get(game.get("result"), "Unknown")

    print(f"  {game['date'].strftime('%Y-%m-%d')}: {game['score_us']}-{game['score_them']} vs {game['opponent']} - {result_label}")

# 3. Check Scheduled Games
print("\n📅 SCHEDULED GAMES")
print("-" * 70)
now = datetime.now()
scheduled = list(db.scheduled_games.find(
    {"date": {"$gte": now}, "status": "scheduled"},
    {"_id": 0, "opponent": 1, "date": 1, "time": 1, "home": 1}
).sort("date", 1).limit(5))

print(f"Upcoming games: {len(scheduled)}")
for game in scheduled:
    days_until = (game["date"].date() - now.date()).days
    home_away = "vs" if game.get("home", True) else "at"
    print(f"  {game['date'].strftime('%Y-%m-%d')} ({days_until} days): {home_away} {game['opponent']} at {game.get('time', 'TBD')}")

# 4. Check Attendance
print("\n👥 ATTENDANCE RECORDS")
print("-" * 70)
attendance_count = db.game_attendance.count_documents({})
print(f"Total attendance records: {attendance_count}")

if scheduled:
    first_game_id = str(scheduled[0]["_id"]) if "_id" in scheduled[0] else None
    if first_game_id:
        attendance = list(db.game_attendance.find({"game_id": first_game_id}))
        confirmed = sum(1 for a in attendance if a.get("status") == "confirmed")
        declined = sum(1 for a in attendance if a.get("status") == "declined")
        print(f"\nNext game attendance:")
        print(f"  Confirmed: {confirmed}")
        print(f"  Declined: {declined}")
        print(f"  Pending: {len(players) - confirmed - declined}")

# 5. Top Scorers Check
print("\n⭐ TOP SCORERS")
print("-" * 70)
top_scorers = list(db.players.find(
    {"position": {"$ne": "Goalie"}},
    {"_id": 0, "name": 1, "goals": 1, "assists": 1}
).sort("goals", -1).limit(3))

for idx, player in enumerate(top_scorers, 1):
    points = player.get("goals", 0) + player.get("assists", 0)
    print(f"  {idx}. {player['name']}: {player.get('goals', 0)}G + {player.get('assists', 0)}A = {points} pts")

# 6. Goalies Check
print("\n🥅 GOALIES")
print("-" * 70)
goalies = list(db.players.find(
    {"position": "Goalie"},
    {"_id": 0, "name": 1, "save_pct": 1, "gaa": 1, "wins": 1, "games_played": 1}
))

for goalie in goalies:
    print(f"  {goalie['name']}: {goalie.get('games_played', 0)} GP, "
          f"{goalie.get('wins', 0)} W, "
          f"{goalie.get('save_pct', 0):.3f} SV%, "
          f"{goalie.get('gaa', 0):.2f} GAA")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print("\n✓ Compare these values with the UI dashboard")
print("✓ Check that European points (22 pts) matches dashboard")
print("✓ Verify upcoming games show correct 'days until'")
print("✓ Confirm attendance counts match schedule view")
print()
