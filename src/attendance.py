"""
Game Attendance Tracking System
Track player confirmations for scheduled games.
"""

from datetime import datetime
from typing import List, Dict, Optional


def set_attendance(db, game_id: str, player_name: str, status: str, notes: str = "") -> Dict:
    """
    Set attendance status for a player for a specific game.

    Args:
        db: MongoDB database connection
        game_id: Scheduled game ID
        player_name: Player name
        status: "confirmed", "declined", or "pending"
        notes: Optional notes (reason for decline, late arrival, etc.)

    Returns:
        Result dictionary
    """
    from bson.objectid import ObjectId

    # Validate status
    if status not in ["confirmed", "declined", "pending"]:
        return {"status": "error", "message": "Status must be 'confirmed', 'declined', or 'pending'"}

    # Verify player exists
    player = db.players.find_one({"name": {"$regex": f"^{player_name}$", "$options": "i"}})
    if not player:
        return {"status": "error", "message": f"Player '{player_name}' not found"}

    player_name = player["name"]  # Use exact name from database

    # Verify game exists
    try:
        oid = ObjectId(game_id)
        game = db.scheduled_games.find_one({"_id": oid})
        if not game:
            return {"status": "error", "message": "Game not found"}
    except:
        return {"status": "error", "message": "Invalid game ID"}

    # Update or insert attendance record
    result = db.game_attendance.update_one(
        {
            "game_id": game_id,
            "player_name": player_name
        },
        {
            "$set": {
                "status": status,
                "notes": notes,
                "updated_at": datetime.now()
            },
            "$setOnInsert": {
                "created_at": datetime.now()
            }
        },
        upsert=True
    )

    status_text = {
        "confirmed": "✅ Confirmed",
        "declined": "❌ Declined",
        "pending": "⏳ Pending"
    }[status]

    return {
        "status": "success",
        "message": f"{player_name}: {status_text} for {game.get('opponent', 'game')}",
        "player": player_name,
        "attendance_status": status
    }


def get_attendance_for_game(db, game_id: str) -> Dict:
    """
    Get attendance status for all players for a specific game.

    Args:
        db: MongoDB database connection
        game_id: Scheduled game ID

    Returns:
        Dictionary with attendance breakdown
    """
    from bson.objectid import ObjectId

    # Verify game exists
    try:
        oid = ObjectId(game_id)
        game = db.scheduled_games.find_one({"_id": oid})
        if not game:
            return {"status": "error", "message": "Game not found"}
    except:
        return {"status": "error", "message": "Invalid game ID"}

    # Get all players
    all_players = list(db.players.find({}, {"_id": 0, "name": 1, "position": 1, "number": 1}))

    # Get attendance records for this game
    attendance_records = list(db.game_attendance.find(
        {"game_id": game_id},
        {"_id": 0, "player_name": 1, "status": 1, "notes": 1, "updated_at": 1}
    ))

    # Create attendance map
    attendance_map = {record["player_name"]: record for record in attendance_records}

    # Build response
    confirmed = []
    declined = []
    pending = []

    for player in all_players:
        name = player["name"]
        position = player["position"]
        number = player["number"]

        player_info = {
            "name": name,
            "position": position,
            "number": number
        }

        if name in attendance_map:
            attendance = attendance_map[name]
            player_info.update({
                "status": attendance["status"],
                "notes": attendance.get("notes", ""),
                "updated_at": attendance.get("updated_at")
            })

            if attendance["status"] == "confirmed":
                confirmed.append(player_info)
            elif attendance["status"] == "declined":
                declined.append(player_info)
            else:
                pending.append(player_info)
        else:
            # No response yet - mark as pending
            player_info["status"] = "pending"
            pending.append(player_info)

    # Count by position for confirmed players
    confirmed_forwards = sum(1 for p in confirmed if p["position"] == "Forward")
    confirmed_defenders = sum(1 for p in confirmed if p["position"] == "Defense")
    confirmed_goalies = sum(1 for p in confirmed if p["position"] == "Goalie")

    return {
        "status": "success",
        "game": {
            "opponent": game.get("opponent"),
            "date": game.get("date").strftime("%b %d, %Y"),
            "time": game.get("time")
        },
        "confirmed": confirmed,
        "declined": declined,
        "pending": pending,
        "summary": {
            "confirmed_count": len(confirmed),
            "declined_count": len(declined),
            "pending_count": len(pending),
            "confirmed_forwards": confirmed_forwards,
            "confirmed_defenders": confirmed_defenders,
            "confirmed_goalies": confirmed_goalies
        }
    }


def get_roster_status(db, game_id: str) -> Dict:
    """
    Get roster status and warnings for a specific game.

    Args:
        db: MongoDB database connection
        game_id: Scheduled game ID

    Returns:
        Dictionary with roster status and warnings
    """
    attendance = get_attendance_for_game(db, game_id)

    if attendance.get("status") == "error":
        return attendance

    summary = attendance["summary"]
    warnings = []
    alerts = []

    # Check minimum requirements
    MIN_FORWARDS = 6  # 2 lines
    MIN_DEFENDERS = 4  # 2 pairs
    MIN_GOALIES = 1

    if summary["confirmed_goalies"] == 0:
        alerts.append("🚨 No goalie confirmed!")
    elif summary["confirmed_goalies"] < MIN_GOALIES:
        warnings.append(f"⚠️ Only {summary['confirmed_goalies']} goalie confirmed")

    if summary["confirmed_defenders"] < MIN_DEFENDERS:
        if summary["confirmed_defenders"] < 3:
            alerts.append(f"🚨 Only {summary['confirmed_defenders']} defenders confirmed (need {MIN_DEFENDERS})")
        else:
            warnings.append(f"⚠️ Only {summary['confirmed_defenders']} defenders confirmed (recommended {MIN_DEFENDERS}+)")

    if summary["confirmed_forwards"] < MIN_FORWARDS:
        if summary["confirmed_forwards"] < 4:
            alerts.append(f"🚨 Only {summary['confirmed_forwards']} forwards confirmed (need {MIN_FORWARDS})")
        else:
            warnings.append(f"⚠️ Only {summary['confirmed_forwards']} forwards confirmed (recommended {MIN_FORWARDS}+)")

    # Check total players
    total_confirmed = summary["confirmed_count"]
    if total_confirmed < 10:
        alerts.append(f"🚨 Only {total_confirmed} players confirmed total!")
    elif total_confirmed < 12:
        warnings.append(f"⚠️ Only {total_confirmed} players confirmed (recommended 12+)")

    # Pending reminders
    if summary["pending_count"] > 5:
        warnings.append(f"📢 {summary['pending_count']} players haven't responded yet")

    return {
        "status": "success",
        "game": attendance["game"],
        "summary": summary,
        "warnings": warnings,
        "alerts": alerts,
        "ready_to_play": len(alerts) == 0
    }


def get_player_attendance_history(db, player_name: str, limit: int = 10) -> Dict:
    """
    Get attendance history for a specific player.

    Args:
        db: MongoDB database connection
        player_name: Player name
        limit: Maximum number of games to return

    Returns:
        Dictionary with attendance history
    """
    # Verify player exists
    player = db.players.find_one({"name": {"$regex": f"^{player_name}$", "$options": "i"}})
    if not player:
        return {"status": "error", "message": f"Player '{player_name}' not found"}

    player_name = player["name"]

    # Get attendance records
    records = list(db.game_attendance.find(
        {"player_name": player_name},
        {"_id": 0, "game_id": 1, "status": 1, "notes": 1, "updated_at": 1}
    ).sort("updated_at", -1).limit(limit))

    # Enrich with game info
    from bson.objectid import ObjectId

    history = []
    for record in records:
        game_id = record["game_id"]
        try:
            game = db.scheduled_games.find_one({"_id": ObjectId(game_id)})
            if game:
                history.append({
                    "opponent": game.get("opponent"),
                    "date": game.get("date").strftime("%b %d, %Y"),
                    "status": record["status"],
                    "notes": record.get("notes", "")
                })
        except:
            continue

    # Calculate stats
    total = len(history)
    confirmed = sum(1 for r in history if r["status"] == "confirmed")
    declined = sum(1 for r in history if r["status"] == "declined")
    attendance_rate = (confirmed / total * 100) if total > 0 else 0

    return {
        "status": "success",
        "player": player_name,
        "history": history,
        "stats": {
            "total_games": total,
            "confirmed": confirmed,
            "declined": declined,
            "attendance_rate": round(attendance_rate, 1)
        }
    }


def send_attendance_reminder(db, game_id: str) -> Dict:
    """
    Get list of players who need to confirm attendance (pending status).

    Args:
        db: MongoDB database connection
        game_id: Scheduled game ID

    Returns:
        Dictionary with list of players to remind
    """
    attendance = get_attendance_for_game(db, game_id)

    if attendance.get("status") == "error":
        return attendance

    pending_players = attendance["pending"]

    return {
        "status": "success",
        "game": attendance["game"],
        "pending_players": pending_players,
        "pending_count": len(pending_players),
        "message": f"{len(pending_players)} player(s) need to confirm attendance"
    }


def bulk_set_attendance(db, game_id: str, confirmations: Dict[str, str]) -> Dict:
    """
    Set attendance for multiple players at once.

    Args:
        db: MongoDB database connection
        game_id: Scheduled game ID
        confirmations: Dictionary mapping player names to status

    Returns:
        Result dictionary with summary
    """
    results = []
    errors = []

    for player_name, status in confirmations.items():
        result = set_attendance(db, game_id, player_name, status)

        if result["status"] == "success":
            results.append(result["message"])
        else:
            errors.append(result["message"])

    return {
        "status": "success" if not errors else "partial",
        "updated": len(results),
        "errors": len(errors),
        "messages": results,
        "error_messages": errors
    }
