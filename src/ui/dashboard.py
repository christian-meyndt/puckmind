"""
Dashboard Home Screen
Landing page showing key information and quick actions.
"""

import streamlit as st
from datetime import datetime, timedelta


def render_dashboard(db):
    """
    Render the home dashboard with key information and quick actions.

    Args:
        db: MongoDB database connection
    """
    st.title("🏒 PuckMind - Hockey Team Manager")
    st.write("Your AI-powered hockey assistant")

    st.divider()

    # Main dashboard layout: 2 columns
    col1, col2 = st.columns([2, 1])

    with col1:
        _render_main_content(db)

    with col2:
        _render_sidebar_widgets(db)

    st.divider()

    # Quick Actions
    _render_quick_actions()


def _render_main_content(db):
    """Render main dashboard content (left column)"""

    # Season Record Card
    st.subheader("📊 Current Season")

    games = list(db.games.find({}, {"_id": 0, "result": 1}))
    wins = sum(1 for g in games if g["result"] == "W")
    losses = sum(1 for g in games if g["result"] == "L")
    draws = sum(1 for g in games if g["result"] == "D")
    total_games = len(games)
    points = wins * 2 + draws

    col_w, col_l, col_d, col_p = st.columns(4)

    with col_w:
        st.metric("Wins", wins, delta=None, delta_color="normal")
    with col_l:
        st.metric("Losses", losses, delta=None, delta_color="inverse")
    with col_d:
        st.metric("Draws", draws)
    with col_p:
        st.metric("Points", points, help="2 points per win, 1 per draw")

    # Win percentage
    if total_games > 0:
        win_pct = (wins / total_games) * 100
        st.progress(wins / total_games, text=f"Win Rate: {win_pct:.1f}%")
    else:
        st.info("No games recorded yet. Start by adding a game!")

    st.divider()

    # Recent Results
    st.subheader("📅 Recent Results")

    recent_games = list(
        db.games.find({}, {"_id": 0})
        .sort("date", -1)
        .limit(5)
    )

    if recent_games:
        for game in recent_games:
            game_date = game["date"].strftime("%b %d")
            result = game["result"]
            score = f"{game['score_us']}-{game['score_them']}"
            opponent = game["opponent"]

            # Color based on result
            if result == "W":
                badge = "🟢"
                result_text = "Win"
            elif result == "L":
                badge = "🔴"
                result_text = "Loss"
            else:
                badge = "🟡"
                result_text = "Draw"

            st.write(f"{badge} **{game_date}** - {result_text} {score} vs {opponent}")
    else:
        st.info("No recent games")

    st.divider()

    # Top Performers This Week
    st.subheader("⭐ Top Performers")

    # Get top 3 scorers
    top_scorers = list(
        db.players.find(
            {"position": {"$ne": "Goalie"}},
            {"_id": 0, "name": 1, "goals": 1, "assists": 1, "position": 1, "number": 1}
        ).sort("goals", -1).limit(3)
    )

    if top_scorers:
        col_top1, col_top2, col_top3 = st.columns(3)

        for idx, player in enumerate(top_scorers):
            with [col_top1, col_top2, col_top3][idx]:
                medal = ["🥇", "🥈", "🥉"][idx]
                points = player["goals"] + player["assists"]
                st.metric(
                    f"{medal} {player['name']}",
                    f"{player['goals']}G {player['assists']}A",
                    delta=f"{points} pts"
                )
    else:
        st.info("No player stats yet")


def _render_sidebar_widgets(db):
    """Render sidebar widgets (right column)"""

    # Next Game Widget
    st.subheader("🗓️ Next Game")

    from src.schedule import get_next_game

    next_game = get_next_game(db)

    if next_game:
        st.success(f"**{next_game['opponent']}**")
        st.write(f"📅 {next_game['date_str']}")
        st.write(f"🕐 {next_game['time']}")

        if next_game.get('location'):
            st.write(f"📍 {next_game['location']}")

        home_away = "🏠 Home" if next_game.get('home', True) else "✈️ Away"
        st.write(home_away)

        # Days until game
        days = next_game['days_until']
        if days == 0:
            st.info("🔥 **TODAY!**")
        elif days == 1:
            st.info("⚡ **Tomorrow!**")
        else:
            st.info(f"📆 In {days} days")
    else:
        st.info("No upcoming games scheduled.\nUse the schedule feature to add games!")

    st.divider()

    # Team Status
    st.subheader("👥 Team Status")

    players = list(db.players.find({}, {"_id": 0, "name": 1, "available": 1, "position": 1}))

    available_count = sum(1 for p in players if p["available"])
    unavailable_count = len(players) - available_count

    st.metric("Available", available_count, delta=None)
    st.metric("Unavailable", unavailable_count, delta=None, delta_color="inverse")

    # Show unavailable players
    if unavailable_count > 0:
        unavailable = [p for p in players if not p["available"]]
        st.warning(f"⚠️ **Unavailable:**")
        for p in unavailable:
            st.write(f"- {p['name']} ({p['position']})")

    st.divider()

    # Goalie Status
    st.subheader("🥅 Goalie Stats")

    goalies = list(
        db.players.find(
            {"position": "Goalie"},
            {"_id": 0, "name": 1, "save_pct": 1, "gaa": 1, "wins": 1}
        ).sort("save_pct", -1)
    )

    if goalies:
        for goalie in goalies:
            st.write(f"**{goalie['name']}**")
            col_sv, col_gaa = st.columns(2)
            with col_sv:
                st.caption(f"SV%: {goalie.get('save_pct', 0):.3f}")
            with col_gaa:
                st.caption(f"GAA: {goalie.get('gaa', 0):.2f}")
    else:
        st.info("No goalie stats")


def _render_quick_actions():
    """Render quick action buttons"""

    st.subheader("⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("➕ Add Game", use_container_width=True, type="primary"):
            st.session_state.active_tab = "data"
            st.rerun()

    with col2:
        if st.button("👥 Update Availability", use_container_width=True):
            st.session_state.active_tab = "data"
            st.rerun()

    with col3:
        if st.button("📊 View Stats", use_container_width=True):
            st.session_state.active_tab = "chat"
            st.rerun()

    st.divider()

    # Chat Shortcuts
    st.subheader("💬 Ask the Agent")

    questions = [
        "Suggest a lineup for next game",
        "Who are our top scorers?",
        "Analyze our recent performance",
        "Show me goalie statistics",
        "Who needs more ice time?"
    ]

    for question in questions:
        if st.button(f"💭 {question}", use_container_width=True, key=f"q_{question}"):
            st.session_state.trigger_query = question
            st.session_state.active_tab = "chat"
            st.rerun()
