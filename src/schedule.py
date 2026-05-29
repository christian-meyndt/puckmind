"""
Schedule Management System
Manages upcoming games, next game info, and calendar integration.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import io


def add_scheduled_game(db, opponent: str, game_date: datetime, location: str = "", time: str = "19:00", home: bool = True, notes: str = "") -> Dict:
    """
    Add a game to the schedule.

    Args:
        db: MongoDB database connection
        opponent: Opponent team name
        game_date: Date and time of the game
        location: Game location/rink
        time: Game time (HH:MM format)
        home: True if home game, False if away
        notes: Additional notes (uniform color, special instructions, etc.)

    Returns:
        Result dictionary with status and game_id
    """
    # Check for duplicate
    existing = db.scheduled_games.find_one({
        "opponent": opponent,
        "date": game_date
    })

    if existing:
        return {
            "status": "error",
            "message": f"Game against {opponent} on {game_date.strftime('%Y-%m-%d')} already scheduled"
        }

    game = {
        "opponent": opponent,
        "date": game_date,
        "time": time,
        "location": location,
        "home": home,
        "notes": notes,
        "created_at": datetime.now(),
        "status": "scheduled"  # scheduled, completed, cancelled
    }

    result = db.scheduled_games.insert_one(game)

    return {
        "status": "success",
        "message": f"Game scheduled: {opponent} on {game_date.strftime('%b %d, %Y')} at {time}",
        "game_id": str(result.inserted_id)
    }


def get_upcoming_games(db, limit: int = 10) -> List[Dict]:
    """
    Get upcoming scheduled games.

    Args:
        db: MongoDB database connection
        limit: Maximum number of games to return

    Returns:
        List of upcoming games
    """
    now = datetime.now()

    games = list(
        db.scheduled_games.find(
            {
                "date": {"$gte": now},
                "status": "scheduled"
            },
            {"_id": 1, "opponent": 1, "date": 1, "time": 1, "location": 1, "home": 1, "notes": 1}
        ).sort("date", 1).limit(limit)
    )

    # Convert ObjectId to string and add days_until
    for game in games:
        game["game_id"] = str(game.pop("_id"))
        days_until = (game["date"] - now).days
        game["days_until"] = days_until
        game["date_str"] = game["date"].strftime("%b %d, %Y")

    return games


def get_next_game(db) -> Optional[Dict]:
    """
    Get the next scheduled game.

    Args:
        db: MongoDB database connection

    Returns:
        Next game dict or None if no upcoming games
    """
    games = get_upcoming_games(db, limit=1)
    return games[0] if games else None


def get_all_scheduled_games(db) -> List[Dict]:
    """
    Get all scheduled games (past and future).

    Args:
        db: MongoDB database connection

    Returns:
        List of all scheduled games
    """
    games = list(
        db.scheduled_games.find(
            {},
            {"_id": 1, "opponent": 1, "date": 1, "time": 1, "location": 1, "home": 1, "notes": 1, "status": 1}
        ).sort("date", -1)
    )

    # Convert ObjectId to string
    for game in games:
        game["game_id"] = str(game.pop("_id"))
        game["date_str"] = game["date"].strftime("%b %d, %Y")

    return games


def cancel_scheduled_game(db, game_id: str, reason: str = "") -> Dict:
    """
    Cancel a scheduled game.

    Args:
        db: MongoDB database connection
        game_id: Game ID to cancel
        reason: Cancellation reason

    Returns:
        Result dictionary
    """
    from bson.objectid import ObjectId

    try:
        oid = ObjectId(game_id)
    except:
        return {"status": "error", "message": "Invalid game ID"}

    result = db.scheduled_games.update_one(
        {"_id": oid},
        {
            "$set": {
                "status": "cancelled",
                "cancelled_at": datetime.now(),
                "cancellation_reason": reason
            }
        }
    )

    if result.matched_count == 0:
        return {"status": "error", "message": "Game not found"}

    return {
        "status": "success",
        "message": f"Game cancelled{': ' + reason if reason else ''}"
    }


def mark_game_completed(db, game_id: str) -> Dict:
    """
    Mark a scheduled game as completed (links to actual game result).

    Args:
        db: MongoDB database connection
        game_id: Game ID to mark complete

    Returns:
        Result dictionary
    """
    from bson.objectid import ObjectId

    try:
        oid = ObjectId(game_id)
    except:
        return {"status": "error", "message": "Invalid game ID"}

    result = db.scheduled_games.update_one(
        {"_id": oid},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.now()
            }
        }
    )

    if result.matched_count == 0:
        return {"status": "error", "message": "Game not found"}

    return {
        "status": "success",
        "message": "Game marked as completed"
    }


def generate_ics_calendar(games: List[Dict], team_name: str = "Hockey Team") -> str:
    """
    Generate iCalendar (.ics) file content for scheduled games.

    Args:
        games: List of scheduled games
        team_name: Team name for event titles

    Returns:
        .ics file content as string
    """
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//PuckMind//Hockey Schedule//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{team_name} Schedule",
        "X-WR-TIMEZONE:UTC"
    ]

    for game in games:
        if game.get("status") == "cancelled":
            continue

        # Parse date and time
        game_date = game["date"]
        time_str = game.get("time", "19:00")
        try:
            hour, minute = map(int, time_str.split(":"))
            game_datetime = game_date.replace(hour=hour, minute=minute)
        except:
            game_datetime = game_date

        # Format datetime for iCal (YYYYMMDDTHHMMSS)
        dtstart = game_datetime.strftime("%Y%m%dT%H%M%S")
        # Assume 2 hour duration
        dtend = (game_datetime + timedelta(hours=2)).strftime("%Y%m%dT%H%M%S")

        location = game.get("location", "TBD")
        opponent = game["opponent"]
        home_away = "vs" if game.get("home", True) else "at"

        summary = f"{team_name} {home_away} {opponent}"
        description = game.get("notes", "")

        # Generate unique ID
        uid = game.get("game_id", game_datetime.strftime("%Y%m%d%H%M%S"))

        ics_content.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}@puckmind.app",
            f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            f"LOCATION:{location}",
            "STATUS:CONFIRMED",
            "END:VEVENT"
        ])

    ics_content.append("END:VCALENDAR")

    return "\n".join(ics_content)


def get_schedule_summary(db) -> Dict:
    """
    Get summary statistics about the schedule.

    Args:
        db: MongoDB database connection

    Returns:
        Dictionary with schedule statistics
    """
    now = datetime.now()

    total_scheduled = db.scheduled_games.count_documents({"status": "scheduled"})
    upcoming = db.scheduled_games.count_documents({
        "status": "scheduled",
        "date": {"$gte": now}
    })
    past = db.scheduled_games.count_documents({
        "status": "scheduled",
        "date": {"$lt": now}
    })
    cancelled = db.scheduled_games.count_documents({"status": "cancelled"})

    next_game = get_next_game(db)

    return {
        "total_scheduled": total_scheduled,
        "upcoming": upcoming,
        "past_unplayed": past,
        "cancelled": cancelled,
        "next_game": next_game
    }
