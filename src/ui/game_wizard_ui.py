"""
Game Wizard UI Component
5-step guided workflow for adding games and updating statistics.
"""

import streamlit as st
from datetime import datetime
import time


def render_game_wizard(db, players):
    """
    Renders the 5-step game wizard workflow.

    Args:
        db: MongoDB database connection
        players: List of players with basic info (name, position, number, available)
    """
    st.subheader("➕ Add Game Result - Guided Workflow")
    st.info("💡 This wizard guides you through adding a game and updating all relevant statistics")

    # Initialize wizard state
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 1
    if "wizard_game_data" not in st.session_state:
        st.session_state.wizard_game_data = {}
    if "wizard_player_stats" not in st.session_state:
        st.session_state.wizard_player_stats = {}
    if "wizard_goalie_stats" not in st.session_state:
        st.session_state.wizard_goalie_stats = {}
    if "wizard_goals" not in st.session_state:
        st.session_state.wizard_goals = []
    if "wizard_goalie_list" not in st.session_state:
        st.session_state.wizard_goalie_list = []

    # Progress indicator
    progress_text = f"**Step {st.session_state.wizard_step} of 5**"
    st.write(progress_text)
    st.progress(st.session_state.wizard_step / 5)

    # Step 1: Basic Game Info
    if st.session_state.wizard_step == 1:
        _render_step1()

    # Step 2: Goal Scorers
    elif st.session_state.wizard_step == 2:
        _render_step2(players)

    # Step 3: Player Stats (optional)
    elif st.session_state.wizard_step == 3:
        _render_step3(players)

    # Step 4: Goalie Stats
    elif st.session_state.wizard_step == 4:
        _render_step4(players)

    # Step 5: Review and Submit
    elif st.session_state.wizard_step == 5:
        _render_step5(db)

    # Reset wizard button
    if st.session_state.wizard_step > 1:
        st.divider()
        if st.button("🔄 Start Over"):
            _reset_wizard()
            st.rerun()


def _render_step1():
    """Step 1: Basic Game Information"""
    st.write("### 1️⃣ Basic Game Information")
    with st.form("wizard_step1"):
        col1, col2 = st.columns(2)
        with col1:
            opponent = st.text_input("Opponent", placeholder="EHC Eagles",
                                    value=st.session_state.wizard_game_data.get("opponent", ""))
            score_us = st.number_input("Our Score", min_value=0, max_value=20,
                                      value=st.session_state.wizard_game_data.get("score_us", 3))
        with col2:
            game_date = st.date_input("Game Date")
            score_them = st.number_input("Their Score", min_value=0, max_value=20,
                                        value=st.session_state.wizard_game_data.get("score_them", 2))

        notes = st.text_area("Game Notes (optional)", placeholder="Strong defensive performance...",
                            value=st.session_state.wizard_game_data.get("notes", ""))

        # Result type (European system)
        st.write("**Result Type:**")
        if score_us > score_them:
            result_type = st.radio(
                "How did we win?",
                ["Regular Time (3 pts)", "Overtime/Shootout (2 pts)"],
                horizontal=True,
                key="result_type_win"
            )
        elif score_us < score_them:
            result_type = st.radio(
                "How did we lose?",
                ["Regular Time (0 pts)", "Overtime/Shootout (1 pt)"],
                horizontal=True,
                key="result_type_loss"
            )
        else:
            st.info("Score is tied - game must have gone to OT/Shootout. Please adjust the score to reflect the final result.")
            result_type = None

        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn2:
            if st.form_submit_button("Next: Goal Scorers →", use_container_width=True):
                if opponent and result_type is not None:
                    # Determine result code
                    if score_us > score_them:
                        result = "W" if "Regular" in result_type else "OTW"
                    else:
                        result = "L" if "Regular" in result_type else "OTL"

                    st.session_state.wizard_game_data = {
                        "opponent": opponent,
                        "score_us": score_us,
                        "score_them": score_them,
                        "date": datetime.combine(game_date, datetime.min.time()),
                        "result": result,
                        "notes": notes,
                        "scorers": [],
                        "assist_players": []
                    }
                    st.session_state.wizard_step = 2
                    st.rerun()
                elif not opponent:
                    st.error("Please enter opponent name")
                elif result_type is None:
                    st.error("Score is tied - adjust to show final result")


def _render_step2(players):
    """Step 2: Goals and Assists (Goal by Goal or Quick Text Entry)"""
    st.write("### 2️⃣ Goals & Assists")
    st.write(f"**Game:** {st.session_state.wizard_game_data['score_us']}-"
             f"{st.session_state.wizard_game_data['score_them']} vs "
             f"{st.session_state.wizard_game_data['opponent']}")

    forwards_defenders = [p for p in players if p["position"] in ["Forward", "Defense"]]
    player_names = [p["name"] for p in forwards_defenders]

    total_goals = st.session_state.wizard_game_data['score_us']

    # Entry mode toggle
    if "scorer_entry_mode" not in st.session_state:
        st.session_state.scorer_entry_mode = "Goal-by-Goal"

    entry_mode = st.radio(
        "Entry Mode",
        ["Goal-by-Goal", "Quick Text Entry"],
        horizontal=True,
        key="scorer_mode_radio"
    )

    if entry_mode != st.session_state.scorer_entry_mode:
        st.session_state.scorer_entry_mode = entry_mode
        st.rerun()

    # Quick Text Entry Mode
    if st.session_state.scorer_entry_mode == "Quick Text Entry":
        st.write("**Natural Language Entry:**")
        st.info("💡 Use first names or partial names, e.g., \"Lukas 2G 1A, Felix 1G, Michael hat trick\"")

        with st.form("quick_scorer_entry"):
            scorers_text = st.text_area(
                "Scorers",
                placeholder="e.g., Lukas 2G 1A, Felix 1G, Michael 1 goal 2 assists",
                height=100,
                help="Formats: '2G 1A', '1 goal', 'hat trick', '2 goals 1 assist'"
            )

            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if st.form_submit_button("← Back", use_container_width=True):
                    st.session_state.wizard_step = 1
                    st.rerun()
            with col_btn2:
                if st.form_submit_button("Parse & Match Players →", use_container_width=True):
                    if scorers_text.strip():
                        from src.quick_game_entry import parse_scorers_text, validate_score

                        # Parse the text
                        parsed = parse_scorers_text(scorers_text)

                        # Validate that goals match score
                        is_valid, error_msg = validate_score(parsed, total_goals)

                        if is_valid:
                            # Store for matching step
                            st.session_state.quick_parsed = parsed
                            st.session_state.quick_scorers_text = scorers_text
                            st.session_state.quick_entry_step = "matching"
                            st.rerun()
                        else:
                            st.error(f"⚠️ {error_msg}")
                    else:
                        # No scorers entered - skip
                        st.session_state.wizard_game_data["scorers_text"] = ""
                        st.session_state.wizard_game_data["parsed_scorers"] = {}
                        st.session_state.wizard_step = 3
                        st.rerun()

        # Player matching step
        if st.session_state.get("quick_entry_step") == "matching":
            st.divider()
            st.write("**🔗 Match Players:**")
            st.write("Link the parsed names to actual players from your roster:")

            parsed = st.session_state.quick_parsed

            # Initialize player matches if not exists
            if "quick_player_matches" not in st.session_state:
                st.session_state.quick_player_matches = {}

                # Try to auto-match players by partial name
                for parsed_name in parsed.keys():
                    # Find players whose full name contains the parsed name (case-insensitive)
                    matches = [p["name"] for p in forwards_defenders
                              if parsed_name.lower() in p["name"].lower()]
                    if len(matches) == 1:
                        # Auto-match if only one match
                        st.session_state.quick_player_matches[parsed_name] = matches[0]

            all_matched = True
            for parsed_name, stats in parsed.items():
                col_parsed, col_arrow, col_select = st.columns([2, 1, 3])

                with col_parsed:
                    st.write(f"**{parsed_name}**")
                    st.caption(f"{stats['goals']}G {stats['assists']}A")

                with col_arrow:
                    st.write("→")

                with col_select:
                    # Find potential matches
                    potential_matches = [p["name"] for p in forwards_defenders
                                       if parsed_name.lower() in p["name"].lower()]

                    if parsed_name in st.session_state.quick_player_matches:
                        default_index = player_names.index(st.session_state.quick_player_matches[parsed_name]) + 1
                    elif potential_matches:
                        default_index = player_names.index(potential_matches[0]) + 1
                    else:
                        default_index = 0
                        all_matched = False

                    matched = st.selectbox(
                        f"Match for {parsed_name}",
                        ["❌ Not matched"] + player_names,
                        index=default_index,
                        key=f"match_{parsed_name}",
                        label_visibility="collapsed"
                    )

                    if matched != "❌ Not matched":
                        st.session_state.quick_player_matches[parsed_name] = matched
                    elif parsed_name in st.session_state.quick_player_matches:
                        all_matched = False

            st.divider()
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if st.button("← Edit Text", use_container_width=True):
                    st.session_state.quick_entry_step = None
                    st.session_state.quick_player_matches = {}
                    st.rerun()
            with col_btn2:
                if st.button("Confirm & Continue →", use_container_width=True, type="primary", disabled=not all_matched):
                    # Apply matches and create wizard_player_stats
                    if "wizard_player_stats" not in st.session_state:
                        st.session_state.wizard_player_stats = {}

                    for parsed_name, full_name in st.session_state.quick_player_matches.items():
                        if parsed_name in parsed:
                            stats = parsed[parsed_name]
                            st.session_state.wizard_player_stats[full_name] = {
                                "goals": stats.get("goals", 0),
                                "assists": stats.get("assists", 0),
                                "shots": 0,
                                "plus_minus": 0,
                                "pim": 0,
                                "hits": 0,
                                "blocked_shots": 0
                            }

                    # Store in game data
                    st.session_state.wizard_game_data["scorers_text"] = st.session_state.quick_scorers_text
                    st.session_state.wizard_game_data["parsed_scorers"] = parsed

                    # Clean up temp state
                    st.session_state.quick_entry_step = None
                    st.session_state.quick_player_matches = {}
                    st.session_state.quick_parsed = None

                    st.session_state.wizard_step = 3
                    st.rerun()

        return

    # Goal-by-Goal Mode (existing code)
    # Initialize goal-by-goal tracking
    if "wizard_goals" not in st.session_state:
        st.session_state.wizard_goals = []

    # Show progress
    goals_entered = len(st.session_state.wizard_goals)
    st.progress(goals_entered / max(total_goals, 1))
    st.write(f"**Progress: {goals_entered} of {total_goals} goals entered**")

    if total_goals == 0:
        # No goals scored - skip directly
        st.info("No goals scored in this game. Skipping to next step.")
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("← Back", use_container_width=True):
                st.session_state.wizard_step = 1
                st.rerun()
        with col_btn2:
            if st.button("Next: Player Stats →", use_container_width=True):
                st.session_state.wizard_game_data["scorers"] = []
                st.session_state.wizard_step = 3
                st.rerun()
        return

    if goals_entered < total_goals:
        # Enter next goal
        st.divider()
        st.write(f"### ⚽ Goal #{goals_entered + 1}")

        with st.form(f"goal_form_{goals_entered}"):
            scorer = st.selectbox(
                "Who scored?",
                [""] + player_names,
                key=f"scorer_{goals_entered}"
            )

            st.write("**Assists (optional, max 2):**")
            assist1 = st.selectbox(
                "Primary assist",
                ["None"] + player_names,
                key=f"assist1_{goals_entered}"
            )

            assist2 = st.selectbox(
                "Secondary assist",
                ["None"] + player_names,
                key=f"assist2_{goals_entered}"
            )

            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if goals_entered > 0:
                    if st.form_submit_button("← Previous Goal", use_container_width=True):
                        # Remove last goal
                        st.session_state.wizard_goals.pop()
                        st.rerun()
                elif st.form_submit_button("← Back to Game Info", use_container_width=True):
                    st.session_state.wizard_step = 1
                    st.rerun()

            with col_btn2:
                if st.form_submit_button("✓ Save Goal", use_container_width=True):
                    if scorer:
                        goal_data = {
                            "scorer": scorer,
                            "assists": []
                        }
                        if assist1 and assist1 != "None":
                            goal_data["assists"].append(assist1)
                        if assist2 and assist2 != "None" and assist2 != assist1:
                            goal_data["assists"].append(assist2)

                        st.session_state.wizard_goals.append(goal_data)
                        st.rerun()
                    else:
                        st.error("Please select a goal scorer")

    else:
        # All goals entered - show summary and add goalies
        st.divider()
        st.success(f"✓ All {total_goals} goals entered!")

        st.write("**Goal Summary:**")
        for idx, goal in enumerate(st.session_state.wizard_goals, 1):
            assists_text = ""
            if goal["assists"]:
                assists_text = f" (Assists: {', '.join(goal['assists'])})"
            st.write(f"{idx}. {goal['scorer']}{assists_text}")

        st.divider()

        # Goalie section
        st.write("### 🥅 Goalies")
        st.write("**Who played in net? (Standard game: 60 minutes total)**")

        goalies = [p for p in players if p["position"] == "Goalie"]
        goalie_names = [g["name"] for g in goalies]

        # Initialize goalie tracking
        if "wizard_goalie_list" not in st.session_state:
            st.session_state.wizard_goalie_list = []

        # Add goalie form
        if len(st.session_state.wizard_goalie_list) < len(goalies):
            with st.form("add_goalie_form"):
                col1, col2, col3 = st.columns([2, 2, 1])

                available_goalies = [g for g in goalie_names
                                    if g not in [gg["name"] for gg in st.session_state.wizard_goalie_list]]

                with col1:
                    goalie_to_add = st.selectbox(
                        "Select goalie",
                        [""] + available_goalies,
                        key="goalie_to_add"
                    )

                with col2:
                    minutes = st.number_input(
                        "Minutes played",
                        min_value=1,
                        max_value=60,
                        value=60,
                        key="goalie_minutes",
                        help="Standard game: 60 minutes"
                    )

                with col3:
                    st.write("")  # Spacer
                    st.write("")  # Spacer
                    if st.form_submit_button("➕ Add", use_container_width=True):
                        if goalie_to_add:
                            # Check total minutes don't exceed 60
                            total_minutes = sum([g["minutes"] for g in st.session_state.wizard_goalie_list])
                            if total_minutes + minutes > 60:
                                st.error(f"Total minutes would exceed 60! Currently: {total_minutes} min")
                            else:
                                st.session_state.wizard_goalie_list.append({
                                    "name": goalie_to_add,
                                    "minutes": minutes
                                })
                                st.rerun()

        # Show added goalies
        if st.session_state.wizard_goalie_list:
            st.write("**Goalies added:**")
            total_minutes = 0
            for idx, goalie_info in enumerate(st.session_state.wizard_goalie_list):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"- **{goalie_info['name']}**: {goalie_info['minutes']} minutes")
                    total_minutes += goalie_info['minutes']
                with col2:
                    if st.button("🗑️", key=f"remove_goalie_{idx}", use_container_width=True):
                        st.session_state.wizard_goalie_list.pop(idx)
                        st.rerun()

            # Show total minutes
            if total_minutes < 60:
                st.warning(f"⚠️ Total: {total_minutes} min (Standard game: 60 min)")
            elif total_minutes == 60:
                st.success(f"✓ Total: {total_minutes} minutes")
            else:
                st.error(f"❌ Total: {total_minutes} min exceeds 60!")

        # Navigation buttons
        st.divider()
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("← Edit Last Goal", use_container_width=True):
                st.session_state.wizard_goals.pop()
                st.rerun()
        with col_btn2:
            # Check if at least one goalie added
            can_proceed = len(st.session_state.wizard_goalie_list) > 0
            if st.button("Next: Player Stats →", use_container_width=True, type="primary", disabled=not can_proceed):
                if not can_proceed:
                    st.error("Please add at least one goalie")
                else:
                    # Aggregate goals and assists by player
                    player_scoring = {}

                    for goal in st.session_state.wizard_goals:
                        scorer = goal["scorer"]
                        if scorer not in player_scoring:
                            player_scoring[scorer] = {"goals": 0, "assists": 0}
                        player_scoring[scorer]["goals"] += 1

                        for assist_player in goal["assists"]:
                            if assist_player not in player_scoring:
                                player_scoring[assist_player] = {"goals": 0, "assists": 0}
                            player_scoring[assist_player]["assists"] += 1

                    # Save to wizard state
                    for player_name, stats in player_scoring.items():
                        if player_name not in st.session_state.wizard_player_stats:
                            st.session_state.wizard_player_stats[player_name] = stats
                        else:
                            st.session_state.wizard_player_stats[player_name].update(stats)

                    st.session_state.wizard_game_data["scorers"] = [g["scorer"] for g in st.session_state.wizard_goals]
                    st.session_state.wizard_step = 3
                    st.rerun()

            if not can_proceed:
                st.error("⚠️ Add at least one goalie to proceed")


def _render_step3(players):
    """Step 3: Player Stats (optional)"""
    st.write("### 3️⃣ Player Statistics (Optional)")
    st.write("Add detailed stats for players who participated. All fields optional.")

    forwards_defenders = [p for p in players if p["position"] in ["Forward", "Defense"]]

    # Get players who already have goals/assists from step 2
    players_with_scoring = list(st.session_state.wizard_player_stats.keys())

    # Show players with scoring first
    if players_with_scoring:
        st.info(f"✓ Already added: {', '.join(players_with_scoring)} (goals/assists from previous step)")

    # Two-column selection interface
    st.write("**Select additional players who played:**")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("**Available Players:**")
        # Show players not yet selected
        available_players = [p["name"] for p in forwards_defenders
                           if p["name"] not in players_with_scoring]

        if available_players:
            for player_name in available_players:
                player = next((p for p in forwards_defenders if p["name"] == player_name), None)
                if player:
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"{player_name} (#{player['number']}, {player['position']})")
                    with col_b:
                        if st.button("Add →", key=f"add_{player_name}", use_container_width=True):
                            if player_name not in st.session_state.wizard_player_stats:
                                st.session_state.wizard_player_stats[player_name] = {
                                    "goals": 0, "assists": 0, "shots": 0,
                                    "plus_minus": 0, "pim": 0, "hits": 0, "blocked_shots": 0
                                }
                            st.rerun()
        else:
            st.write("_All players added_")

    with col2:
        st.write("**Selected Players:**")
        if st.session_state.wizard_player_stats:
            for player_name in list(st.session_state.wizard_player_stats.keys()):
                player = next((p for p in forwards_defenders if p["name"] == player_name), None)
                if player:
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        stats = st.session_state.wizard_player_stats[player_name]
                        summary = f"{stats.get('goals', 0)}G {stats.get('assists', 0)}A" if stats.get('goals', 0) > 0 or stats.get('assists', 0) > 0 else "stats pending"
                        st.write(f"{player_name} - _{summary}_")
                    with col_b:
                        if st.button("Remove", key=f"remove_{player_name}", use_container_width=True):
                            del st.session_state.wizard_player_stats[player_name]
                            st.rerun()
        else:
            st.write("_No players selected_")

    # Get all players with stats (from step 2 and step 3)
    all_stat_players = list(st.session_state.wizard_player_stats.keys())

    if all_stat_players:
        st.divider()
        st.write("**Enter stats for each player:**")

        for player_name in all_stat_players:
            player = next((p for p in forwards_defenders if p["name"] == player_name), None)
            if player:
                with st.expander(f"📝 {player_name} (#{player['number']}, {player['position']})",
                                expanded=False):
                    col1, col2, col3 = st.columns(3)

                    current_stats = st.session_state.wizard_player_stats.get(player_name, {})

                    with col1:
                        assists = st.number_input("Assists", min_value=0, max_value=10,
                                                value=current_stats.get("assists", 0),
                                                key=f"assists_{player_name}")
                        shots = st.number_input("Shots", min_value=0, max_value=20,
                                              value=current_stats.get("shots", 0),
                                              key=f"shots_{player_name}")
                    with col2:
                        plus_minus = st.number_input("Plus/Minus", min_value=-10, max_value=10,
                                                    value=current_stats.get("plus_minus", 0),
                                                    key=f"pm_{player_name}")
                        pim = st.number_input("Penalty Minutes", min_value=0, max_value=20,
                                            value=current_stats.get("pim", 0),
                                            key=f"pim_{player_name}")
                    with col3:
                        hits = st.number_input("Hits", min_value=0, max_value=20,
                                             value=current_stats.get("hits", 0),
                                             key=f"hits_{player_name}")
                        blocked = st.number_input("Blocked Shots", min_value=0, max_value=20,
                                                value=current_stats.get("blocked_shots", 0),
                                                key=f"blocked_{player_name}")

                    # Update stats dict
                    if player_name in st.session_state.wizard_player_stats:
                        st.session_state.wizard_player_stats[player_name].update({
                            "assists": assists,
                            "shots": shots,
                            "plus_minus": plus_minus,
                            "pim": pim,
                            "hits": hits,
                            "blocked_shots": blocked
                        })
                    else:
                        st.session_state.wizard_player_stats[player_name] = {
                            "goals": 0,
                            "assists": assists,
                            "shots": shots,
                            "plus_minus": plus_minus,
                            "pim": pim,
                            "hits": hits,
                            "blocked_shots": blocked
                        }

    # Goalie section (for Quick Text Entry mode, otherwise populated in Step 2)
    st.divider()
    st.write("### 🥅 Goalies")
    st.write("**Who played in net? (Standard game: 60 minutes total)**")

    goalies = [p for p in players if p["position"] == "Goalie"]
    goalie_names = [g["name"] for g in goalies]

    # Initialize goalie tracking
    if "wizard_goalie_list" not in st.session_state:
        st.session_state.wizard_goalie_list = []

    # Add goalie form
    if len(st.session_state.wizard_goalie_list) < len(goalies):
        with st.form("add_goalie_form_step3"):
            col1, col2, col3 = st.columns([2, 2, 1])

            available_goalies = [g for g in goalie_names
                                if g not in [gg["name"] for gg in st.session_state.wizard_goalie_list]]

            with col1:
                goalie_to_add = st.selectbox(
                    "Select goalie",
                    [""] + available_goalies,
                    key="goalie_to_add_step3"
                )

            with col2:
                minutes = st.number_input(
                    "Minutes played",
                    min_value=1,
                    max_value=60,
                    value=60,
                    key="goalie_minutes_step3",
                    help="Standard game: 60 minutes"
                )

            with col3:
                st.write("")  # Spacer
                st.write("")  # Spacer
                if st.form_submit_button("➕ Add", use_container_width=True):
                    if goalie_to_add:
                        # Check total minutes don't exceed 60
                        total_minutes = sum([g["minutes"] for g in st.session_state.wizard_goalie_list])
                        if total_minutes + minutes > 60:
                            st.error(f"Total minutes would exceed 60! Currently: {total_minutes} min")
                        else:
                            st.session_state.wizard_goalie_list.append({
                                "name": goalie_to_add,
                                "minutes": minutes
                            })
                            st.rerun()

    # Show added goalies
    if st.session_state.wizard_goalie_list:
        st.write("**Goalies added:**")
        total_minutes = 0
        for idx, goalie_info in enumerate(st.session_state.wizard_goalie_list):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"- **{goalie_info['name']}**: {goalie_info['minutes']} minutes")
                total_minutes += goalie_info['minutes']
            with col2:
                if st.button("🗑️", key=f"remove_goalie_step3_{idx}", use_container_width=True):
                    st.session_state.wizard_goalie_list.pop(idx)
                    st.rerun()

        # Show total minutes
        if total_minutes < 60:
            st.warning(f"⚠️ Total: {total_minutes} min (Standard game: 60 min)")
        elif total_minutes == 60:
            st.success(f"✓ Total: {total_minutes} minutes")
        else:
            st.error(f"❌ Total: {total_minutes} min exceeds 60!")

    st.divider()
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("← Back", use_container_width=True, key="step3_back"):
            st.session_state.wizard_step = 2
            st.rerun()
    with col_btn2:
        if st.button("Next: Goalie Stats →", use_container_width=True,
                    type="primary", key="step3_next"):
            st.session_state.wizard_step = 4
            st.rerun()


def _render_step4(players):
    """Step 4: Goalie Shots Against"""
    st.write("### 4️⃣ Goalie Statistics - Shots Against")
    st.write("Enter shots against for each goalie. Save percentage will be calculated automatically.")

    # Show goalies from step 2
    if "wizard_goalie_list" not in st.session_state or not st.session_state.wizard_goalie_list:
        st.error("No goalies found from step 2. Please go back.")
        if st.button("← Back", use_container_width=True):
            st.session_state.wizard_step = 3
            st.rerun()
        return

    st.write(f"**Goals against: {st.session_state.wizard_game_data['score_them']}**")
    st.divider()

    with st.form("wizard_step4"):
        shots_data = {}

        for goalie_info in st.session_state.wizard_goalie_list:
            goalie_name = goalie_info["name"]
            minutes = goalie_info["minutes"]

            st.write(f"**{goalie_name}** - {minutes} minutes")

            col_shots, col_goals = st.columns(2)

            with col_shots:
                shots_against = st.number_input(
                    f"Shots Against",
                    min_value=0,
                    max_value=100,
                    value=st.session_state.wizard_goalie_stats.get(goalie_name, {}).get("shots_against", 0),
                    key=f"shots_{goalie_name}",
                    help=f"Total shots this goalie faced in {minutes} minutes"
                )

            with col_goals:
                # Default: distribute goals proportionally if multiple goalies
                goals_against_total = st.session_state.wizard_game_data['score_them']
                if len(st.session_state.wizard_goalie_list) == 1:
                    default_goals = goals_against_total
                else:
                    default_goals = round(goals_against_total * (minutes / 60))

                goals_against = st.number_input(
                    f"Goals Against",
                    min_value=0,
                    max_value=goals_against_total,
                    value=st.session_state.wizard_goalie_stats.get(goalie_name, {}).get("goals_against", default_goals),
                    key=f"goals_{goalie_name}",
                    help=f"Goals scored against this goalie (Total game: {goals_against_total})"
                )

            # Calculate and show save percentage
            if shots_against > 0:
                from src.game_wizard import calculate_save_percentage
                save_pct = calculate_save_percentage(shots_against, goals_against)
                st.metric("Calculated Save %", f"{save_pct:.3f}",
                         help=f"Saves: {shots_against - goals_against} / Shots: {shots_against}")
            else:
                st.info("Enter shots and goals to calculate save %")

            shots_data[goalie_name] = {
                "shots_against": shots_against,
                "goals_against": goals_against,
                "minutes": minutes
            }

            st.divider()

        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.form_submit_button("← Back", use_container_width=True):
                st.session_state.wizard_step = 3
                st.rerun()
        with col_btn2:
            if st.form_submit_button("Next: Review & Submit →", use_container_width=True):
                # Save shots data
                for goalie_name, data in shots_data.items():
                    st.session_state.wizard_goalie_stats[goalie_name] = data

                st.session_state.wizard_step = 5
                st.rerun()


def _render_step5(db):
    """Step 5: Review and Submit"""
    st.write("### 5️⃣ Review & Submit")
    st.write("Review all data before submitting. This will update all player and goalie statistics.")

    # Display summary
    st.write("**Game Info:**")
    st.write(f"- **Opponent:** {st.session_state.wizard_game_data['opponent']}")
    st.write(f"- **Score:** {st.session_state.wizard_game_data['score_us']}-"
             f"{st.session_state.wizard_game_data['score_them']}")
    st.write(f"- **Result:** {st.session_state.wizard_game_data['result']}")
    st.write(f"- **Date:** {st.session_state.wizard_game_data['date'].strftime('%Y-%m-%d')}")

    st.divider()
    st.write("**Player Stats to Update:**")
    if st.session_state.wizard_player_stats:
        for player_name, stats in st.session_state.wizard_player_stats.items():
            stat_summary = ", ".join([f"{k}={v}" for k, v in stats.items() if v > 0])
            st.write(f"- **{player_name}:** {stat_summary}")
    else:
        st.write("- No player stats entered (only goal scorers will be updated)")

    st.divider()
    st.write("**Goalie Stats:**")
    if st.session_state.wizard_goalie_stats:
        for goalie_name, stats in st.session_state.wizard_goalie_stats.items():
            from src.game_wizard import calculate_save_percentage
            goals_against = stats.get('goals_against', st.session_state.wizard_game_data['score_them'])
            save_pct = calculate_save_percentage(stats['shots_against'], goals_against)
            saves = stats['shots_against'] - goals_against
            st.write(f"- **{goalie_name}:** {stats['shots_against']} shots, {goals_against} goals against, "
                    f"{saves} saves → {save_pct:.3f} save%")
    else:
        st.write("- No goalie stats entered")

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("← Back", use_container_width=True):
            st.session_state.wizard_step = 4
            st.rerun()
    with col_btn2:
        if st.button("✅ Submit & Update All Stats", use_container_width=True, type="primary"):
            _submit_game_data(db)


def _submit_game_data(db):
    """Submit game data and update all statistics"""
    from src.game_wizard import update_all_game_stats

    try:
        updates_summary = update_all_game_stats(
            db,
            st.session_state.wizard_game_data,
            st.session_state.wizard_player_stats,
            st.session_state.wizard_goalie_stats
        )

        st.success("✅ Game and all statistics updated successfully!")
        st.write("**Updates:**")
        for update in updates_summary:
            st.write(f"- {update}")

        st.balloons()

        # Reset wizard
        _reset_wizard()

        # Wait a moment before rerun
        time.sleep(2)
        st.rerun()

    except Exception as e:
        st.error(f"Error updating stats: {str(e)}")


def _reset_wizard():
    """Reset wizard state"""
    st.session_state.wizard_step = 1
    st.session_state.wizard_game_data = {}
    st.session_state.wizard_player_stats = {}
    st.session_state.wizard_goalie_stats = {}
    st.session_state.wizard_goals = []
    st.session_state.wizard_goalie_list = []
