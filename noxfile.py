"""
Nox Configuration for PuckMind
Automated testing, linting, and code quality checks
"""

import nox

# Default sessions to run
nox.options.sessions = ["tests", "lint"]

# Python version to test against
PYTHON_VERSION = "3.12"


@nox.session(python=PYTHON_VERSION)
def tests(session):
    """Run the test suite with pytest"""
    session.install("-r", "requirements.txt")
    session.install("pytest", "pytest-cov", "mongomock")

    # Run tests with coverage
    session.run(
        "pytest",
        "tests/",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-v"
    )


@nox.session(python=PYTHON_VERSION)
def lint(session):
    """Run code linting with flake8"""
    session.install("flake8", "flake8-docstrings")

    # Run flake8
    session.run(
        "flake8",
        "src/",
        "--max-line-length=120",
        "--ignore=D100,D101,D102,D103,D104,D105,D107,W503,E203",
        "--exclude=__pycache__,venv,.nox"
    )


@nox.session(python=PYTHON_VERSION)
def format_check(session):
    """Check code formatting with black"""
    session.install("black")

    session.run(
        "black",
        "src/",
        "tests/",
        "--check",
        "--line-length=120"
    )


@nox.session(python=PYTHON_VERSION)
def format(session):
    """Auto-format code with black"""
    session.install("black")

    session.run(
        "black",
        "src/",
        "tests/",
        "--line-length=120"
    )


@nox.session(python=PYTHON_VERSION)
def type_check(session):
    """Run type checking with mypy"""
    session.install("mypy")
    session.install("-r", "requirements.txt")

    session.run(
        "mypy",
        "src/",
        "--ignore-missing-imports",
        "--no-strict-optional"
    )


@nox.session(python=PYTHON_VERSION)
def security(session):
    """Run security checks with bandit"""
    session.install("bandit")

    session.run(
        "bandit",
        "-r",
        "src/",
        "-ll",  # Only show medium and high severity issues
        "--skip=B101"  # Skip assert_used warnings
    )


@nox.session(python=PYTHON_VERSION)
def quick_tests(session):
    """Run tests quickly without coverage report"""
    session.install("-r", "requirements.txt")
    session.install("pytest", "mongomock")

    session.run("pytest", "tests/", "-v", "--tb=short")


@nox.session(python=PYTHON_VERSION)
def full_check(session):
    """Run all checks: tests, lint, format, type, security"""
    session.notify("tests")
    session.notify("lint")
    session.notify("format_check")
    session.notify("type_check")
    session.notify("security")


@nox.session(python=PYTHON_VERSION)
def verify_database(session):
    """Verify database data integrity"""
    session.install("-r", "requirements.txt")

    session.run("python", "verify_database.py")


@nox.session(python=PYTHON_VERSION)
def seed_db(session):
    """Reseed the database with test data"""
    session.install("-r", "requirements.txt")

    session.run("python", "-m", "src.database.seed_data")
