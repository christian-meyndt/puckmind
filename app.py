"""
PuckMind - Hockey Scout & Team Manager Agent
Web UI built with Streamlit
"""

import asyncio
import streamlit as st
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import centralized configuration
from src.config import APP_NAME, DEFAULT_WEB_USER_ID
from src.database import get_db
from src.ui import render_game_wizard
from src.ui.dashboard import render_dashboard
from src.agent import (
    get_all_players,
    get_available_players,
    get_top_scorers,
    get_recent_games,
    get_season_record,
    suggest_lineup,
    add_game_result,
    suggest_training_exercises,
    hockey_agent,
)

# Page config
st.set_page_config(
    page_title="PuckMind - Hockey Agent",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .example-query {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_session" not in st.session_state:
    st.session_state.agent_session = None
if "session_service" not in st.session_state:
    st.session_state.session_service = None
if "runner" not in st.session_state:
    st.session_state.runner = None


# Initialize agent (only once)
@st.cache_resource
def initialize_agent():
    """Initialize the agent, runner, and session."""
    session_service = InMemorySessionService()
    runner = Runner(
        agent=hockey_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    return session_service, runner


async def create_session(session_service):
    """Create a new agent session."""
    return await session_service.create_session(
        app_name=APP_NAME,
        user_id=DEFAULT_WEB_USER_ID,
    )


def get_agent_response(runner, session_id, user_message):
    """Get response from the agent."""
    content = types.Content(
        role="user",
        parts=[types.Part(text=user_message)],
    )

    events = runner.run(
        user_id="web_user",
        session_id=session_id,
        new_message=content,
    )

    for event in events:
        if event.is_final_response():
            return event.content.parts[0].text

    return "Sorry, I couldn't process that request."


# Header
st.markdown('<div class="main-header">🏒 PuckMind</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">AI-Powered Hockey Scout & Team Manager</div>',
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.header("About PuckMind")
    st.write("""
    PuckMind is an AI agent that helps amateur hockey teams with:

    - 📊 Player statistics & availability
    - 🎯 Lineup suggestions
    - 🏆 Game results & season records
    - 🏋️ Training planning & exercises
    - 📈 Team analytics
    """)

    st.divider()

    # Data Management Section
    st.header("📝 Data Management")

    with st.expander("➕ Add Game Result"):
        with st.form("add_game_form"):
            opponent = st.text_input("Opponent", placeholder="EHC Eagles")
            col1, col2 = st.columns(2)
            with col1:
                score_us = st.number_input("Our Score", min_value=0, max_value=20, value=3)
            with col2:
                score_them = st.number_input("Their Score", min_value=0, max_value=20, value=2)
            notes = st.text_area("Game Notes", placeholder="Great powerplay performance...")

            if st.form_submit_button("Record Game"):
                if opponent:
                    query = f"Record game result: {score_us}:{score_them} against {opponent}. Notes: {notes}"
                    st.session_state.trigger_query = query
                    st.rerun()
                else:
                    st.error("Please enter opponent name")

    with st.expander("🏥 Update Player Availability"):
        st.write("Use natural language in chat:")
        st.code('Mark Kevin Müller as available')
        st.code('Jonas Kramer is injured')
        st.info("Note: Availability updates require database access")

    st.divider()

    st.header("Example Queries")

    if st.button("💬 Top forwards", use_container_width=True):
        st.session_state.trigger_query = "Show me our top forwards with offensive stats like shooting % and faceoff %"
        st.rerun()

    if st.button("💬 Top defenders", use_container_width=True):
        st.session_state.trigger_query = "Who are our best defenders? Show defensive stats like blocked shots and plus/minus"
        st.rerun()

    if st.button("💬 Goalie stats", use_container_width=True):
        st.session_state.trigger_query = "What are our goalie statistics? Show GAA and save percentage"
        st.rerun()

    if st.button("💬 Player form", use_container_width=True):
        st.session_state.trigger_query = "Who's on a hot or cold streak?"
        st.rerun()

    if st.button("💬 Suggest lineup", use_container_width=True):
        st.session_state.trigger_query = "Suggest a lineup for the next game"
        st.rerun()

    if st.button("💬 Season prediction", use_container_width=True):
        st.session_state.trigger_query = "Predict our final standing this season"
        st.rerun()

    if st.button("💬 Analyze opponent", use_container_width=True):
        st.session_state.trigger_query = "Analyze our history against EHC Eagles"
        st.rerun()

    st.divider()

    st.header("Quick Actions")

    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.session_state.agent_session = None
        st.rerun()

    st.divider()

    st.write("**Built with:**")
    st.write("""
    - Google Gemini 2.5 Flash
    - MongoDB Atlas
    - Google ADK
    - Model Context Protocol (MCP)
    """)

# Initialize agent if not already done
if st.session_state.session_service is None:
    with st.spinner("Initializing PuckMind..."):
        session_service, runner = initialize_agent()
        st.session_state.session_service = session_service
        st.session_state.runner = runner

        # Create session
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        agent_session = loop.run_until_complete(create_session(session_service))
        st.session_state.agent_session = agent_session

# Initialize active tab state
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "home"

# Database connection (shared across tabs)
db = get_db()

# Custom tab navigation (allows programmatic control)
st.write("")  # Spacing
selected_tab = st.radio(
    "Navigation",
    ["🏠 Home", "💬 Chat", "📊 Data Management"],
    horizontal=True,
    key="tab_selector",
    label_visibility="collapsed"
)

# Map display name to internal name
tab_mapping = {
    "🏠 Home": "home",
    "💬 Chat": "chat",
    "📊 Data Management": "data"
}

# Update session state if user clicked a different tab
current_tab = tab_mapping[selected_tab]
if st.session_state.active_tab != current_tab:
    st.session_state.active_tab = current_tab

st.divider()

# Render the active tab
if st.session_state.active_tab == "home":
    render_dashboard(db)

elif st.session_state.active_tab == "data":
    st.header("Data Management")
    st.write("Manage your team's data directly through the interface.")

    # Load players data once at the top
    players = list(db.players.find({}, {"_id": 0, "name": 1, "available": 1, "position": 1, "number": 1}))

    # Schedule Management
    st.subheader("🗓️ Schedule Management")
    st.write("Manage upcoming games and view schedule.")

    with st.expander("➕ Add Scheduled Game", expanded=False):
        with st.form("add_scheduled_game"):
            col1, col2 = st.columns(2)
            with col1:
                sched_opponent = st.text_input("Opponent", placeholder="EHC Eagles")
                sched_date = st.date_input("Game Date")
            with col2:
                sched_time = st.time_input("Game Time", value=None)
                sched_location = st.text_input("Location", placeholder="City Ice Arena")

            sched_home = st.checkbox("Home Game", value=True)
            sched_notes = st.text_area("Notes (optional)", placeholder="Wear white jerseys, bring water bottles...")

            if st.form_submit_button("📅 Schedule Game", use_container_width=True):
                if sched_opponent and sched_date:
                    from src.schedule import add_scheduled_game
                    from datetime import datetime

                    # Combine date and time
                    if sched_time:
                        game_datetime = datetime.combine(sched_date, sched_time)
                        time_str = sched_time.strftime("%H:%M")
                    else:
                        game_datetime = datetime.combine(sched_date, datetime.min.time()).replace(hour=19)
                        time_str = "19:00"

                    result = add_scheduled_game(
                        db,
                        opponent=sched_opponent,
                        game_date=game_datetime,
                        location=sched_location,
                        time=time_str,
                        home=sched_home,
                        notes=sched_notes
                    )

                    if result["status"] == "success":
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])
                else:
                    st.error("Please enter opponent and date")

    # Show upcoming games
    from src.schedule import get_upcoming_games

    upcoming = get_upcoming_games(db, limit=10)

    if upcoming:
        st.write("**Upcoming Games:**")
        for game in upcoming:
            with st.expander(f"{'vs' if game.get('home', True) else 'at'} {game['opponent']} - {game['date_str']}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"📅 **Date:** {game['date_str']}")
                    st.write(f"🕐 **Time:** {game['time']}")
                    if game.get("location"):
                        st.write(f"📍 **Location:** {game['location']}")
                with col2:
                    home_away = "🏠 Home Game" if game.get("home", True) else "✈️ Away Game"
                    st.write(home_away)

                    if game['days_until'] == 0:
                        st.info("🔥 **TODAY!**")
                    elif game['days_until'] == 1:
                        st.info("⚡ **Tomorrow!**")
                    else:
                        st.write(f"📆 In {game['days_until']} days")

                if game.get("notes"):
                    st.write(f"📝 **Notes:** {game['notes']}")

                st.divider()

                # Attendance tracking section
                st.write("**👥 Attendance Tracking:**")

                from src.attendance import get_roster_status

                game_id = game["game_id"]
                roster = get_roster_status(db, game_id)

                if roster["status"] == "success":
                    summary = roster["summary"]

                    # Show summary metrics
                    col_conf, col_dec, col_pend = st.columns(3)
                    with col_conf:
                        st.metric("✅ Confirmed", summary["confirmed_count"])
                    with col_dec:
                        st.metric("❌ Declined", summary["declined_count"])
                    with col_pend:
                        st.metric("⏳ Pending", summary["pending_count"])

                    # Show position breakdown
                    st.caption(f"Confirmed: {summary['confirmed_forwards']}F / {summary['confirmed_defenders']}D / {summary['confirmed_goalies']}G")

                    # Show warnings/alerts
                    if roster["alerts"]:
                        for alert in roster["alerts"]:
                            st.error(alert)
                    if roster["warnings"]:
                        for warning in roster["warnings"]:
                            st.warning(warning)

                    if roster["ready_to_play"]:
                        st.success("✅ Roster looks good!")

                    # Quick attendance form
                    with st.form(f"attendance_{game_id}"):
                        st.write("**Quick Confirm:**")
                        col_player, col_status = st.columns([2, 1])

                        with col_player:
                            selected_player = st.selectbox(
                                "Player",
                                [p["name"] for p in players],
                                key=f"attend_player_{game_id}"
                            )
                        with col_status:
                            attend_status = st.radio(
                                "Status",
                                ["Coming ✅", "Not Coming ❌"],
                                horizontal=True,
                                key=f"attend_status_{game_id}"
                            )

                        if st.form_submit_button("Update Attendance", use_container_width=True):
                            from src.attendance import set_attendance

                            status = "confirmed" if "Coming" in attend_status else "declined"
                            result = set_attendance(db, game_id, selected_player, status)

                            if result["status"] == "success":
                                st.success(result["message"])
                                st.rerun()
                            else:
                                st.error(result["message"])

                    # View full roster button
                    if st.button(f"📋 View Full Roster", key=f"roster_{game_id}", use_container_width=True):
                        st.session_state[f"show_roster_{game_id}"] = True
                        st.rerun()

                    # Show full roster if requested
                    if st.session_state.get(f"show_roster_{game_id}", False):
                        from src.attendance import get_attendance_for_game

                        full_attendance = get_attendance_for_game(db, game_id)

                        if full_attendance["confirmed"]:
                            st.write("**✅ Confirmed:**")
                            for p in full_attendance["confirmed"]:
                                st.write(f"- {p['name']} (#{p['number']}, {p['position']})")

                        if full_attendance["declined"]:
                            st.write("**❌ Declined:**")
                            for p in full_attendance["declined"]:
                                notes_text = f" - {p['notes']}" if p.get('notes') else ""
                                st.write(f"- {p['name']} (#{p['number']}, {p['position']}){notes_text}")

                        if full_attendance["pending"]:
                            st.write("**⏳ Pending Response:**")
                            for p in full_attendance["pending"]:
                                st.write(f"- {p['name']} (#{p['number']}, {p['position']})")

            st.divider()

        # Calendar export
        if st.button("📥 Export Calendar (.ics)", use_container_width=True):
            from src.schedule import generate_ics_calendar

            ics_content = generate_ics_calendar(upcoming, "PuckMind Team")
            st.download_button(
                label="Download Calendar",
                data=ics_content,
                file_name="puckmind_schedule.ics",
                mime="text/calendar",
                use_container_width=True
            )
    else:
        st.info("No upcoming games scheduled")

    st.divider()

    # Add Game Result - Guided Wizard (extracted to separate module)
    render_game_wizard(db, players)

    st.divider()

    # Update Player Availability
    st.subheader("🏥 Update Player Availability")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("**Current Status:**")
        for player in players:
            status = "✅ Available" if player["available"] else "❌ Unavailable"
            st.write(f"{player['number']} - {player['name']} ({player['position']}): {status}")

    with col2:
        st.write("**Quick Actions:**")
        with st.form("update_availability"):
            selected_player = st.selectbox(
                "Select Player",
                [p["name"] for p in players]
            )
            new_status = st.radio("Status", ["Available", "Unavailable"], horizontal=True)
            reason = st.text_input("Reason (optional)", placeholder="Injury, suspension, etc.")

            if st.form_submit_button("Update Status", use_container_width=True):
                from src.agent import update_player_availability
                available = (new_status == "Available")
                result = update_player_availability(selected_player, available, reason)

                if result["status"] == "ok":
                    st.success(f"✅ {result['message']}")
                    st.rerun()
                else:
                    st.error(result["message"])

    st.divider()

    # Comprehensive Stats Editor
    st.subheader("📊 Edit Player Statistics")
    st.write("Complete stats editor - updates all player statistics")

    # Step 1: Select Player
    all_players_full = list(db.players.find({}, {"_id": 0}))
    selected_player_name = st.selectbox(
        "1️⃣ Select Player to Edit",
        [p["name"] for p in all_players_full],
        key="stats_editor_player"
    )

    if selected_player_name:
        # Get full player data
        player_data = next((p for p in all_players_full if p["name"] == selected_player_name), None)

        if player_data:
            st.divider()
            st.write(f"**Editing: {player_data['name']} (#{player_data['number']}) - {player_data['position']}**")

            # Step 2: Show current stats and edit form
            with st.form("comprehensive_stats_form"):
                st.write("**2️⃣ Current Stats → Edit Values**")

                if player_data["position"] == "Goalie":
                    # Goalie-specific stats
                    st.write("🥅 **Goalie Statistics**")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Current Games", player_data.get("games_played", 0))
                        new_games = st.number_input("Games Played", min_value=0, value=player_data.get("games_played", 0))

                        st.metric("Current Wins", player_data.get("wins", 0))
                        new_wins = st.number_input("Wins", min_value=0, value=player_data.get("wins", 0))

                    with col2:
                        st.metric("Current Losses", player_data.get("losses", 0))
                        new_losses = st.number_input("Losses", min_value=0, value=player_data.get("losses", 0))

                        st.metric("Current Shutouts", player_data.get("shutouts", 0))
                        new_shutouts = st.number_input("Shutouts", min_value=0, value=player_data.get("shutouts", 0))

                    with col3:
                        st.metric("Current GAA", f"{player_data.get('gaa', 0):.2f}")
                        new_gaa = st.number_input("Goals Against Avg", min_value=0.0, max_value=10.0, value=float(player_data.get("gaa", 0)), step=0.1, format="%.2f")

                        st.metric("Current Save%", f"{player_data.get('save_pct', 0):.3f}")
                        new_save_pct = st.number_input("Save %", min_value=0.0, max_value=1.0, value=float(player_data.get("save_pct", 0)), step=0.001, format="%.3f")

                    col4, col5 = st.columns(2)
                    with col4:
                        st.metric("Current Shots Against", player_data.get("shots_against", 0))
                        new_shots_against = st.number_input("Shots Against", min_value=0, value=player_data.get("shots_against", 0))

                    with col5:
                        st.metric("Current Saves", player_data.get("saves", 0))
                        new_saves = st.number_input("Saves", min_value=0, value=player_data.get("saves", 0))

                else:
                    # Forward/Defender stats
                    st.write(f"{'⚡️ Forward' if player_data['position'] == 'Forward' else '🛡️ Defender'} **Statistics**")

                    # Basic scoring stats
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Current Goals", player_data.get("goals", 0))
                        new_goals = st.number_input("Goals", min_value=0, value=player_data.get("goals", 0))

                    with col2:
                        st.metric("Current Assists", player_data.get("assists", 0))
                        new_assists = st.number_input("Assists", min_value=0, value=player_data.get("assists", 0))

                    with col3:
                        st.metric("Current +/-", player_data.get("plus_minus", 0))
                        new_plus_minus = st.number_input("Plus/Minus", min_value=-50, max_value=50, value=player_data.get("plus_minus", 0))

                    with col4:
                        st.metric("Current PIM", player_data.get("pim", 0))
                        new_pim = st.number_input("Penalty Minutes", min_value=0, value=player_data.get("pim", 0))

                    st.write("**Advanced Stats**")
                    col5, col6, col7 = st.columns(3)

                    with col5:
                        st.metric("Current Shots", player_data.get("shots", 0))
                        new_shots = st.number_input("Shots on Goal", min_value=0, value=player_data.get("shots", 0))

                        if player_data["position"] == "Forward":
                            st.metric("Current Shooting%", f"{player_data.get('shooting_pct', 0):.1f}%")
                            new_shooting_pct = st.number_input("Shooting %", min_value=0.0, max_value=100.0, value=float(player_data.get("shooting_pct", 0)), step=0.1, format="%.1f")

                    with col6:
                        st.metric("Current Hits", player_data.get("hits", 0))
                        new_hits = st.number_input("Hits", min_value=0, value=player_data.get("hits", 0))

                        if player_data["position"] == "Defense":
                            st.metric("Current Blocked Shots", player_data.get("blocked_shots", 0))
                            new_blocked = st.number_input("Blocked Shots", min_value=0, value=player_data.get("blocked_shots", 0))

                    with col7:
                        st.metric("Current Games", player_data.get("games_played", 0))
                        new_games_played = st.number_input("Games Played", min_value=0, value=player_data.get("games_played", 0))

                        if player_data["position"] == "Forward":
                            st.metric("Current Faceoff%", f"{player_data.get('faceoff_pct', 0):.1f}%")
                            new_faceoff_pct = st.number_input("Faceoff %", min_value=0.0, max_value=100.0, value=float(player_data.get("faceoff_pct", 0)), step=0.1, format="%.1f")

                # Submit button
                st.write("---")
                if st.form_submit_button("💾 Save All Changes", use_container_width=True):
                    # Build update dict based on position
                    update_dict = {}

                    if player_data["position"] == "Goalie":
                        update_dict = {
                            "games_played": new_games,
                            "wins": new_wins,
                            "losses": new_losses,
                            "shutouts": new_shutouts,
                            "gaa": new_gaa,
                            "save_pct": new_save_pct,
                            "shots_against": new_shots_against,
                            "saves": new_saves
                        }
                    else:
                        update_dict = {
                            "goals": new_goals,
                            "assists": new_assists,
                            "plus_minus": new_plus_minus,
                            "pim": new_pim,
                            "shots": new_shots,
                            "hits": new_hits,
                            "games_played": new_games_played
                        }

                        if player_data["position"] == "Forward":
                            update_dict["shooting_pct"] = new_shooting_pct
                            update_dict["faceoff_pct"] = new_faceoff_pct
                        elif player_data["position"] == "Defense":
                            update_dict["blocked_shots"] = new_blocked

                    # Update in database
                    db.players.update_one(
                        {"name": player_data["name"]},
                        {"$set": update_dict}
                    )

                    st.success(f"✅ Updated all stats for {player_data['name']}!")
                    st.balloons()
                    st.rerun()

    st.divider()

    # View Recent Games
    st.subheader("📅 Recent Games")
    games = list(db.games.find({}, {"_id": 0}).sort("date", -1).limit(10))

    for game in games:
        result_emoji = "🏆" if game["result"] == "W" else "😞" if game["result"] == "L" else "🤝"
        date_str = game["date"].strftime("%Y-%m-%d")
        st.write(f"{result_emoji} **{date_str}** - vs {game['opponent']}: {game['score_us']}-{game['score_them']} ({game['result']})")
        if game.get("notes"):
            st.caption(f"Notes: {game['notes']}")

elif st.session_state.active_tab == "chat":
    st.subheader("Chat with your Hockey Agent")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle triggered query from example buttons
    if st.session_state.get("trigger_query"):
        prompt = st.session_state.trigger_query
        st.session_state.trigger_query = None

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_agent_response(
                    st.session_state.runner,
                    st.session_state.agent_session.id,
                    prompt
                )
                st.markdown(response)

        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Chat input
    if prompt := st.chat_input("Ask about your team..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_agent_response(
                    st.session_state.runner,
                    st.session_state.agent_session.id,
                    prompt
                )
                st.markdown(response)

        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    Built for the Google Cloud Rapid Agent Hackathon |
    <a href="https://github.com/christian-meyndt/puckmind" target="_blank">GitHub</a> |
    Powered by Google Gemini & MongoDB
</div>
""", unsafe_allow_html=True)
