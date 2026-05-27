# Changelog

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
