"""
Comprehensive Feature Testing Script
Tests all major features added: quick entry, schedule, attendance
"""

import sys
from datetime import datetime, timedelta


def test_quick_game_entry():
    """Test quick game entry module"""
    print("\n" + "="*60)
    print("TEST 1: Quick Game Entry")
    print("="*60)

    from src.quick_game_entry import (
        parse_scorers_text,
        validate_score,
        parse_quick_game_command
    )

    # Test 1.1: Parse simple scorers
    print("\n1.1 Parse 'Lukas 2G 1A, Felix 1G'")
    result = parse_scorers_text("Lukas 2G 1A, Felix 1G")
    expected = {
        'Lukas': {'goals': 2, 'assists': 1},
        'Felix': {'goals': 1, 'assists': 0}
    }
    assert result == expected, f"Expected {expected}, got {result}"
    print("  ✅ PASS")

    # Test 1.2: Hat trick
    print("\n1.2 Parse 'Michael hat trick'")
    result = parse_scorers_text("Michael hat trick")
    expected = {'Michael': {'goals': 3, 'assists': 0}}
    assert result == expected, f"Expected {expected}, got {result}"
    print("  ✅ PASS")

    # Test 1.3: Complex scoring
    print("\n1.3 Parse 'Lukas 1G 2A, Felix 2 goals, Stefan 3 assists'")
    result = parse_scorers_text("Lukas 1G 2A, Felix 2 goals, Stefan 3 assists")
    assert result['Lukas']['goals'] == 1
    assert result['Lukas']['assists'] == 2
    assert result['Felix']['goals'] == 2
    assert result['Stefan']['assists'] == 3
    print("  ✅ PASS")

    # Test 1.4: Validate score
    print("\n1.4 Validate score matches goals")
    stats = {'Lukas': {'goals': 2, 'assists': 1}, 'Felix': {'goals': 1, 'assists': 0}}
    is_valid, msg = validate_score(stats, 3)
    assert is_valid == True, f"Should be valid, got: {msg}"
    print("  ✅ PASS")

    # Test 1.5: Detect score mismatch
    print("\n1.5 Detect score mismatch (3 goals declared, 4 counted)")
    is_valid, msg = validate_score(stats, 2)
    assert is_valid == False, "Should detect mismatch"
    print(f"  ✅ PASS - Correctly detected: {msg}")

    # Test 1.6: Parse full command
    print("\n1.6 Parse 'Record 4-2 win vs Eagles, Lukas 2G 1A'")
    result = parse_quick_game_command("Record 4-2 win vs Eagles, Lukas 2G 1A")
    assert result['score_us'] == 4
    assert result['score_them'] == 2
    assert result['opponent'] == 'Eagles'
    assert 'Lukas' in result['scorers_text']
    print("  ✅ PASS")

    print("\n✅ Quick Game Entry: ALL TESTS PASSED\n")


def test_schedule_module():
    """Test schedule management module"""
    print("\n" + "="*60)
    print("TEST 2: Schedule Management")
    print("="*60)

    from src.schedule import (
        add_scheduled_game,
        get_upcoming_games,
        get_next_game,
        generate_ics_calendar,
        get_schedule_summary
    )
    from src.database import get_db

    db = get_db()

    # Clean up test data
    print("\n2.0 Cleaning up old test data...")
    db.scheduled_games.delete_many({"opponent": {"$regex": "TEST.*"}})
    print("  ✅ Cleanup done")

    # Test 2.1: Add a game
    print("\n2.1 Add scheduled game")
    future_date = datetime.now() + timedelta(days=7)
    result = add_scheduled_game(
        db,
        opponent="TEST Eagles",
        game_date=future_date,
        location="Test Arena",
        time="19:30",
        home=True,
        notes="Test game"
    )
    assert result["status"] == "success", f"Failed to add game: {result}"
    game_id = result["game_id"]
    print(f"  ✅ PASS - Game ID: {game_id}")

    # Test 2.2: Get upcoming games
    print("\n2.2 Get upcoming games")
    upcoming = get_upcoming_games(db, limit=10)
    test_games = [g for g in upcoming if g['opponent'] == 'TEST Eagles']
    assert len(test_games) > 0, "Test game not found in upcoming"
    assert test_games[0]['days_until'] >= 6, f"Days until should be 6-7, got {test_games[0]['days_until']}"
    print(f"  ✅ PASS - Found {len(test_games)} test game(s), {test_games[0]['days_until']} days away")

    # Test 2.3: Get next game
    print("\n2.3 Get next game")
    next_game = get_next_game(db)
    assert next_game is not None, "Should have at least one upcoming game"
    print(f"  ✅ PASS - Next game: {next_game['opponent']} on {next_game['date_str']}")

    # Test 2.4: Generate calendar
    print("\n2.4 Generate .ics calendar")
    ics = generate_ics_calendar(test_games, "Test Team")
    assert "BEGIN:VCALENDAR" in ics
    assert "TEST Eagles" in ics
    assert "END:VCALENDAR" in ics
    print("  ✅ PASS - Calendar generated")

    # Test 2.5: Schedule summary
    print("\n2.5 Get schedule summary")
    summary = get_schedule_summary(db)
    assert summary['upcoming'] > 0
    print(f"  ✅ PASS - {summary['upcoming']} upcoming games")

    # Cleanup
    print("\n2.6 Cleanup test data")
    db.scheduled_games.delete_many({"opponent": {"$regex": "TEST.*"}})
    print("  ✅ Cleanup done")

    print("\n✅ Schedule Management: ALL TESTS PASSED\n")
    return game_id  # Return for attendance tests


def test_attendance_module():
    """Test attendance tracking module"""
    print("\n" + "="*60)
    print("TEST 3: Attendance Tracking")
    print("="*60)

    from src.attendance import (
        set_attendance,
        get_attendance_for_game,
        get_roster_status
    )
    from src.schedule import add_scheduled_game
    from src.database import get_db

    db = get_db()

    # Setup: Create a test game
    print("\n3.0 Setup: Create test game")
    future_date = datetime.now() + timedelta(days=3)
    result = add_scheduled_game(
        db,
        opponent="TEST Bears",
        game_date=future_date,
        location="Test Rink",
        time="20:00",
        home=False
    )
    game_id = result["game_id"]
    print(f"  ✅ Test game created: {game_id}")

    # Get first 3 players for testing
    players = list(db.players.find({}, {"_id": 0, "name": 1, "position": 1}).limit(3))
    if len(players) < 3:
        print("  ⚠️ WARNING: Need at least 3 players in database for full tests")
        return

    player1, player2, player3 = players[0]['name'], players[1]['name'], players[2]['name']

    # Test 3.1: Confirm attendance
    print(f"\n3.1 Confirm {player1} attending")
    result = set_attendance(db, game_id, player1, "confirmed")
    assert result["status"] == "success"
    print("  ✅ PASS")

    # Test 3.2: Decline attendance
    print(f"\n3.2 Mark {player2} declined")
    result = set_attendance(db, game_id, player2, "declined", "Injured")
    assert result["status"] == "success"
    print("  ✅ PASS")

    # Test 3.3: Get attendance
    print("\n3.3 Get attendance for game")
    attendance = get_attendance_for_game(db, game_id)
    assert attendance["status"] == "success"
    assert len(attendance["confirmed"]) >= 1
    assert len(attendance["declined"]) >= 1
    assert any(p['name'] == player1 for p in attendance["confirmed"])
    assert any(p['name'] == player2 for p in attendance["declined"])
    print(f"  ✅ PASS - Confirmed: {len(attendance['confirmed'])}, Declined: {len(attendance['declined'])}, Pending: {len(attendance['pending'])}")

    # Test 3.4: Roster status
    print("\n3.4 Get roster status with warnings")
    roster = get_roster_status(db, game_id)
    assert roster["status"] == "success"
    assert "summary" in roster
    assert "warnings" in roster
    assert "alerts" in roster
    print(f"  ✅ PASS - {len(roster['warnings'])} warnings, {len(roster['alerts'])} alerts")
    if roster['alerts']:
        print(f"       Alerts: {roster['alerts']}")
    if roster['warnings']:
        print(f"       Warnings: {roster['warnings']}")

    # Test 3.5: Invalid game ID
    print("\n3.5 Test error handling (invalid game ID)")
    result = set_attendance(db, "invalid_id", player1, "confirmed")
    assert result["status"] == "error"
    print("  ✅ PASS - Error correctly caught")

    # Test 3.6: Invalid player
    print("\n3.6 Test error handling (invalid player)")
    result = set_attendance(db, game_id, "NonExistent Player", "confirmed")
    assert result["status"] == "error"
    print("  ✅ PASS - Error correctly caught")

    # Cleanup
    print("\n3.7 Cleanup test data")
    db.scheduled_games.delete_many({"opponent": {"$regex": "TEST.*"}})
    db.game_attendance.delete_many({"game_id": game_id})
    print("  ✅ Cleanup done")

    print("\n✅ Attendance Tracking: ALL TESTS PASSED\n")


def test_agent_tools():
    """Test agent tools are properly configured"""
    print("\n" + "="*60)
    print("TEST 4: Agent Configuration")
    print("="*60)

    from src.agent import hockey_agent

    # Test 4.1: Agent loaded
    print("\n4.1 Agent loaded successfully")
    assert hockey_agent is not None
    print("  ✅ PASS")

    # Test 4.2: Tool count
    print("\n4.2 Check tool count")
    tool_count = len(hockey_agent.tools)
    print(f"  Agent has {tool_count} tools")
    assert tool_count == 26, f"Expected 26 tools, got {tool_count}"
    print("  ✅ PASS - 26 tools configured")

    # Test 4.3: New tools present
    print("\n4.3 Verify new tools present")
    # Get tool names from the callable attribute
    tool_names = []
    for tool in hockey_agent.tools:
        if hasattr(tool, '_callable'):
            tool_names.append(tool._callable.__name__)
        elif hasattr(tool, 'name'):
            tool_names.append(tool.name)

    new_tools = [
        "record_game_quick",
        "schedule_game",
        "get_schedule",
        "get_next_game_info",
        "confirm_attendance",
        "check_game_roster",
        "get_game_attendance"
    ]

    for tool_name in new_tools:
        assert tool_name in tool_names, f"Tool '{tool_name}' not found in {tool_names}"
        print(f"  ✅ {tool_name}")

    print("\n✅ Agent Configuration: ALL TESTS PASSED\n")


def test_database_connections():
    """Test database connections work"""
    print("\n" + "="*60)
    print("TEST 5: Database Connections")
    print("="*60)

    from src.database import get_db, get_client

    # Test 5.1: Get client
    print("\n5.1 Get MongoDB client")
    client = get_client()
    assert client is not None
    print("  ✅ PASS")

    # Test 5.2: Get database
    print("\n5.2 Get database")
    db = get_db()
    assert db is not None
    print("  ✅ PASS")

    # Test 5.3: Check collections exist
    print("\n5.3 Check collections")
    collections = db.list_collection_names()
    print(f"  Found collections: {', '.join(collections)}")

    required = ['players', 'games']
    for coll in required:
        assert coll in collections, f"Missing collection: {coll}"
    print("  ✅ PASS - Required collections present")

    # Test 5.4: Count documents
    print("\n5.4 Check data exists")
    player_count = db.players.count_documents({})
    game_count = db.games.count_documents({})
    print(f"  Players: {player_count}")
    print(f"  Games: {game_count}")

    if player_count == 0:
        print("  ⚠️ WARNING: No players in database - run seed_data.py")
    else:
        print("  ✅ PASS - Data present")

    print("\n✅ Database Connections: ALL TESTS PASSED\n")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PUCKMIND - COMPREHENSIVE FEATURE TESTS")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Test modules in order
        test_database_connections()
        test_quick_game_entry()
        test_schedule_module()
        test_attendance_module()
        test_agent_tools()

        # Summary
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("="*60)
        print("\n✅ Quick Game Entry: Working")
        print("✅ Schedule Management: Working")
        print("✅ Attendance Tracking: Working")
        print("✅ Agent Configuration: Working")
        print("✅ Database Connections: Working")
        print("\n" + "="*60)
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

        return 0

    except AssertionError as e:
        print("\n" + "="*60)
        print("❌ TEST FAILED")
        print("="*60)
        print(f"Error: {e}")
        print("\n")
        return 1

    except Exception as e:
        print("\n" + "="*60)
        print("💥 UNEXPECTED ERROR")
        print("="*60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
