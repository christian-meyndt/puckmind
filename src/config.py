"""
Centralized Configuration for PuckMind
All environment variables and app settings in one place.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ── MongoDB Configuration ──────────────────────────────────────
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = "hockey_agent"

# ── Google Cloud / Vertex AI Configuration ─────────────────────
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "true")

# Force Vertex AI usage (disable Google AI API)
if "GOOGLE_API_KEY" in os.environ:
    del os.environ["GOOGLE_API_KEY"]
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = GOOGLE_GENAI_USE_VERTEXAI

# ── Model Configuration ────────────────────────────────────────
MODEL_NAME = "gemini-2.5-flash"
AGENT_NAME = "hockey_scout"
APP_NAME = "hockey_agent"

# ── Application Settings ───────────────────────────────────────
DEFAULT_USER_ID = "trainer"
DEFAULT_WEB_USER_ID = "web_user"
