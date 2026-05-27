"""
Game Stats Wizard - Guided workflow for adding games and updating all stats
"""

def calculate_save_percentage(shots_against: int, goals_against: int) -> float:
    """Calculate goalie save percentage"""
    if shots_against == 0:
        return 0.0
    saves = shots_against - goals_against
    return round(saves / shots_against, 3)


def calculate_shooting_percentage(shots: int, goals: int) -> float:
    """Calculate player shooting percentage"""
    if shots == 0:
        return 0.0
    return round((goals / shots) * 100, 1)


def update_all_game_stats(db, game_data: dict, player_stats: dict, goalie_stats: dict):
    """
    Updates all player and goalie stats after a game.

    Args:
        db: MongoDB database connection
        game_data: Basic game info (opponent, scores, date, result, notes)
        player_stats: Dict of player stats to update {player_name: {goals, assists, shots, plus_minus, pim}}
        goalie_stats: Dict of goalie stats {goalie_name: {shots_against, goals_against}}

    Returns:
        Summary of updates
    """
    from datetime import datetime

    updates_summary = []

    # 1. Insert game record
    game_record = {
        "date": game_data.get("date", datetime.now()),
        "opponent": game_data["opponent"],
        "home": game_data.get("home", True),
        "score_us": game_data["score_us"],
        "score_them": game_data["score_them"],
        "result": game_data["result"],
        "scorers": game_data.get("scorers", []),
        "notes": game_data.get("notes", ""),
    }
    db.games.insert_one(game_record)
    updates_summary.append(f"Game recorded: {game_data['score_us']}-{game_data['score_them']} vs {game_data['opponent']}")

    # 2. Update player stats
    for player_name, stats in player_stats.items():
        player = db.players.find_one({"name": player_name})
        if not player:
            continue

        update_fields = {}

        # Increment goals and assists
        if stats.get("goals", 0) > 0:
            update_fields["$inc"] = update_fields.get("$inc", {})
            update_fields["$inc"]["goals"] = stats["goals"]

        if stats.get("assists", 0) > 0:
            update_fields["$inc"] = update_fields.get("$inc", {})
            update_fields["$inc"]["assists"] = stats["assists"]

        if stats.get("pim", 0) > 0:
            update_fields["$inc"] = update_fields.get("$inc", {})
            update_fields["$inc"]["pim"] = stats["pim"]

        # Set new values for other stats
        set_fields = {}

        if "plus_minus" in stats:
            # Plus/minus is cumulative
            new_plus_minus = player.get("plus_minus", 0) + stats["plus_minus"]
            set_fields["plus_minus"] = new_plus_minus

        if "shots" in stats:
            # Add shots to total
            new_shots = player.get("shots", 0) + stats["shots"]
            set_fields["shots"] = new_shots

            # Recalculate shooting %
            new_total_goals = player.get("goals", 0) + stats.get("goals", 0)
            if new_shots > 0:
                set_fields["shooting_pct"] = calculate_shooting_percentage(new_shots, new_total_goals)

        if "hits" in stats:
            new_hits = player.get("hits", 0) + stats["hits"]
            set_fields["hits"] = new_hits

        if "blocked_shots" in stats:
            new_blocked = player.get("blocked_shots", 0) + stats["blocked_shots"]
            set_fields["blocked_shots"] = new_blocked

        # Increment games played
        set_fields["games_played"] = player.get("games_played", 0) + 1

        # Apply updates
        if update_fields.get("$inc") or set_fields:
            if set_fields:
                update_fields["$set"] = set_fields
            db.players.update_one({"name": player_name}, update_fields)
            updates_summary.append(f"✅ {player_name}: +{stats.get('goals', 0)}G, +{stats.get('assists', 0)}A")

    # 3. Update goalie stats
    for goalie_name, stats in goalie_stats.items():
        goalie = db.players.find_one({"name": goalie_name})
        if not goalie:
            continue

        shots_against = stats.get("shots_against", 0)
        goals_against = game_data["score_them"]

        # Calculate save %
        save_pct = calculate_save_percentage(shots_against, goals_against)
        saves = shots_against - goals_against

        # Update cumulative stats
        new_shots_against = goalie.get("shots_against", 0) + shots_against
        new_saves = goalie.get("saves", 0) + saves
        new_games_played = goalie.get("games_played", 0) + 1

        # Calculate new overall save %
        if new_shots_against > 0:
            new_save_pct = round(new_saves / new_shots_against, 3)
        else:
            new_save_pct = 0.0

        update_fields = {
            "$inc": {
                "games_played": 1,
                "shots_against": shots_against,
                "saves": saves,
            },
            "$set": {
                "save_pct": new_save_pct
            }
        }

        # Update win/loss record
        if game_data["result"] == "W":
            update_fields["$inc"]["wins"] = 1
        elif game_data["result"] == "L":
            update_fields["$inc"]["losses"] = 1

        # Check for shutout
        if goals_against == 0 and game_data["result"] == "W":
            update_fields["$inc"]["shutouts"] = 1

        # Recalculate GAA (simplified - assumes 60 min games)
        # GAA = (goals_against * 60) / minutes_played
        # For simplicity: total_goals / games_played
        new_games = goalie.get("games_played", 0) + 1
        # We need to track total goals against
        # For now, calculate based on current data

        db.players.update_one({"name": goalie_name}, update_fields)
        updates_summary.append(f"✅ {goalie_name} (G): {shots_against} shots, {save_pct:.3f} save%, {game_data['result']}")

    return updates_summary
