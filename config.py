import os
from pathlib import Path
from dotenv import load_dotenv

# Automatically look for a .env file in this directory and load it
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = BASE_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

# Google Gemini Model Settings
# Defaulting to gemini-1.5-flash for speed/cost, or gemini-1.5-pro for complex coding
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "60.0"))

# Sandbox Isolation Settings
USE_DOCKER_SANDBOX = os.getenv("USE_DOCKER_SANDBOX", "True").lower() in ("true", "1", "yes")
DOCKER_IMAGE = os.getenv("DOCKER_IMAGE", "python:3.11-slim")
EXECUTION_TIMEOUT_SECONDS = int(os.getenv("EXECUTION_TIMEOUT", "15"))