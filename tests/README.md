# PuckMind Test Suite

Comprehensive test suite for the PuckMind hockey team management system.

## Test Coverage

### 🎯 European Points System (`test_european_points.py`)
- Point calculation (W=3, OTW=2, OTL=1, L=0)
- Season record structure
- Valid result types
- Points per game correctness

### ⚡ Quick Game Entry (`test_quick_game_entry.py`)
- Natural language parsing ("Player 2G 1A")
- Hat trick recognition
- Multiple scorer parsing
- Score validation
- Various input formats

### 📅 Schedule Management (`test_schedule.py`)
- Getting upcoming games
- Next game calculation
- Days until calculation (date-based)
- Game cancellation
- ICS calendar generation

### 👥 Attendance Tracking (`test_attendance.py`)
- Confirming/declining attendance
- Attendance breakdown
- Roster status warnings
- Upsert functionality
- Invalid player/game handling

### ⏱️ Ice Time Analysis (`test_ice_time_analysis.py`)
- Identifying developing players
- Ice time comparison vs team average
- Recommendations generation
- Excluding unavailable players

### 🏥 Player Availability (`test_player_availability.py`)
- Marking players unavailable with reason
- Clearing reason when available
- Unavailable count accuracy
- Reason retrieval

## Running Tests

### Using Nox (Recommended)

```bash
# Install nox
pip install nox

# Run all tests with coverage
nox -s tests

# Run tests quickly without coverage
nox -s quick_tests

# Run all checks (tests, lint, format, type, security)
nox -s full_check

# List all available sessions
nox --list
```

### Using Pytest Directly

```bash
# Activate virtual environment
source venv/bin/activate

# Install test dependencies
pip install pytest pytest-cov mongomock

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_european_points.py -v

# Run specific test
pytest tests/test_european_points.py::test_points_calculation -v
```

## Nox Sessions

| Session | Description |
|---------|-------------|
| `tests` | Run full test suite with coverage |
| `quick_tests` | Run tests without coverage (faster) |
| `lint` | Check code style with flake8 |
| `format` | Auto-format code with black |
| `format_check` | Check formatting without changes |
| `type_check` | Run type checking with mypy |
| `security` | Run security checks with bandit |
| `full_check` | Run all checks |
| `verify_database` | Verify database data integrity |
| `seed_db` | Reseed database with test data |

## Test Fixtures

Located in `conftest.py`:

- **`mock_db`** - Mock MongoDB database
- **`sample_players`** - 5 test players (goalie, forwards, defender, developing, injured)
- **`sample_games`** - 4 test games with European result types
- **`sample_scheduled_games`** - 2 upcoming scheduled games

## Writing New Tests

1. Create a new test file: `test_<feature>.py`
2. Import fixtures from `conftest.py`
3. Use `mock_db` fixture for database operations
4. Name tests descriptively: `test_<what_it_does>`

Example:

```python
def test_new_feature(mock_db, sample_players):
    \"\"\"Test description\"\"\"
    # Your test code
    assert something is True
```

## CI/CD Integration

The Nox pipeline is ready for CI/CD integration:

```yaml
# Example GitHub Actions
- name: Run tests
  run: nox -s tests

- name: Run linting
  run: nox -s lint
```

## Test Statistics

- **Total test files**: 6
- **Total test cases**: ~30+
- **Coverage target**: >80%
- **Test execution time**: <10 seconds

## Troubleshooting

### MongoDB Connection Issues
Tests use `mongomock` instead of real MongoDB, so no connection needed.

### Import Errors
Make sure you're in the project root directory and virtual environment is activated.

### Failed Tests
Check the test output for specific assertion errors and stack traces.
