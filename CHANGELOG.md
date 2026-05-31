# Changelog

## [Unreleased] - 2026-05-31

### Added
- **European Points System** (W=3pts, OTW=2pts, OTL=1pt, L=0pts)
  - Dashboard shows 5 metrics: Wins, OT/SO Wins, Losses, OT/SO Losses, Points
  - Points calculation tooltip with breakdown (e.g., "5×3 + 2×2 + 3×1 = 22 pts")
  - Game wizard: result type selection (Regular Time vs OT/Shootout)
  - Recent results show OT/SO labels with correct badges
  - Agent system prompt updated to explain European system
  - Documentation: `EUROPEAN_POINTS_SYSTEM.md`
- **Schedule Calendar View** in Data Management tab
  - Toggle between List View and Calendar View
  - Monthly calendar grid with 🏒 icons on game days
  - Month/year selector dropdowns
  - Shows time and opponent abbreviation on calendar dates
  - Expandable game list below calendar for selected month
- **Enhanced Game Wizard - Quick Text Entry Mode**
  - Natural language scorer input: "Lukas 2G 1A, Felix 1G, Michael hat trick"
  - Player matching step: links parsed names to roster (e.g., "Lukas" → "Lukas Schäfer")
  - Auto-matching for unique names, manual selection for ambiguous
  - Validates goals match score
- **Ice Time Analysis Tool**
  - New agent tool: `analyze_ice_time()`
  - Identifies developing players with low ice time
  - Compares individual vs team average
  - Considers age, status (veteran/regular/developing), performance metrics
  - Answers: "Who needs more ice time?"
- **Enhanced Goalie Stats in Game Wizard**
  - Goalie section now in Step 3 (accessible from both entry modes)
  - Step 4: Added "Goals Against" input field per goalie
  - Can specify exact goals against for each goalie
  - Shows calculated save %: (Shots - Goals) / Shots
- **Player Data Enhancements**
  - Added `age` field (19-30 years)
  - Added `status` field: "veteran", "regular", or "developing"
  - Added `avg_ice_time` field: minutes per game (8.2-22.5)

### Changed
- **Seed data updated with European points games**
  - 12 games: 5W, 2OTW, 3OTL, 2L = 22 points total
  - Detailed notes explaining OT/SO context for each game
  - All 17 players now include age, status, and avg_ice_time
- **Agent improvements**
  - `get_season_record()`: Returns European points breakdown
  - `record_game_quick()`: Added `overtime` parameter
  - Agent now asks "Was this decided in regulation or OT/SO?" when recording games
  - Tool count: 27 tools (added analyze_ice_time, cancel_scheduled_game)
- **Dashboard point calculation**
  - Changed from 2pts/win + 1pt/draw to European system
  - Win rate now includes both regular and OT/SO wins
- **Navigation improvements**
  - Custom button-based tab navigation (replaced st.tabs for programmatic control)
  - Quick action buttons now properly navigate between tabs
  - Fixed indentation issues in Data Management tab

### Fixed
- **Attendance tracking bug**: "Not Coming ❌" now correctly marks as declined (was marking as confirmed)
  - Root cause: `"Coming" in "Not Coming"` evaluated to True
  - Fixed: Changed to exact string comparison
- **Days until calculation**: Now accurate (date-based, not datetime)
  - Issue: Game on June 16 showed "15 days" when should be "16 days"
  - Fixed: Compare dates only, not datetimes with time-of-day
- **Calendar export button**: Moved outside game loop to prevent duplicate key errors
- **Goalie save % on review page**: Now uses actual goals_against per goalie
  - Previously used total game goals (incorrect for multiple goalies)
  - Now shows: shots, goals against, saves, calculated save %
- **Navigation syntax errors**: Fixed indentation in calendar view implementation

### Documentation
- Updated `CLAUDE.md` with new features and tool count
- Created `EUROPEAN_POINTS_SYSTEM.md` with full explanation
- Updated agent examples to reflect European system

## [Unreleased] - 2026-05-27

### Added
- **5-Step Game Wizard** in Streamlit UI for guided game addition workflow
  - Step 1: Basic game info (opponent, scores, date)
  - Step 2: Goal scorers selection
  - Step 3: Optional player stats (assists, shots, plus/minus, PIM, hits, blocked shots)
  - Step 4: Goalie stats with automatic save % calculation
  - Step 5: Review and submit all updates at once
- **New modular architecture:**
  - `src/config.py` - Centralized configuration for all settings
  - `src/database/` - Database module with connection management
    - `connection.py` - Singleton MongoDB connection (eliminates duplication)
    - `seed_data.py` - Database seeding script (moved from src/)
  - `src/ui/` - UI components module
    - `game_wizard_ui.py` - Extracted 280-line wizard component from app.py
- `src/game_wizard.py` - Helper functions for game stats workflow
  - `calculate_save_percentage()` - Goalie save % calculation
  - `calculate_shooting_percentage()` - Player shooting % calculation
  - `update_all_game_stats()` - Comprehensive stats update function
- `ARCHITECTURE_REVIEW.md` - Project structure analysis and improvement recommendations
- `CHANGELOG.md` - This file

### Changed
- **Major refactoring:** Reduced `app.py` from 800+ lines to 506 lines (37% reduction)
- Eliminated duplicate MongoDB connection code (was in 3 files, now centralized)
- All modules now use centralized configuration from `src/config.py`
- Wizard workflow extracted to dedicated UI module for maintainability
- `src/agent.py` now uses centralized config and database connection
- `src/agent_enhanced.py` now uses centralized config and database connection
- Updated `.gitignore` to include `.DS_Store` and `.idea/` directory
- Database seeding moved to proper module location: `src/database/seed_data.py`

### Removed
- `seed_data.js` - Obsolete JavaScript seed script (replaced by Python version)
- `src/agent_mcp.py` - Incomplete MCP integration experiment (156 lines)
- `src/agent_with_mcp.py` - Incomplete MCP integration experiment (248 lines)
- `.DS_Store` files from repository (macOS system metadata)
- Duplicate MongoDB connection code across multiple files

### Fixed
- Game addition now properly updates all player and goalie statistics
- Shooting percentage automatically recalculated when updating goals/shots
- Goalie save percentage calculated from shots against and goals against

## [0.1.0] - 2026-05-26

### Added
- Initial release for Google Cloud Rapid Agent Hackathon
- 19 agent tools for team management
- Streamlit web UI with chat and data management tabs
- MongoDB Atlas integration
- Google Gemini 2.5 Flash via Vertex AI
- Visual lineup card with hockey rink layout
- Position-specific analytics (forwards, defenders, goalies)
- Enhanced analytics: opponent analysis, player form tracking, season predictions
- 17 players with comprehensive statistics
- 12 games of season history
