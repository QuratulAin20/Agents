import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = BASE_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "60.0"))
MAX_REVIEW_CYCLES = int(os.getenv("MAX_REVIEW_CYCLES", "5"))

USE_DOCKER_SANDBOX = os.getenv("USE_DOCKER_SANDBOX", "True").lower() in ("true", "1", "yes")
DOCKER_IMAGE = os.getenv("DOCKER_IMAGE", "python:3.11-slim")
EXECUTION_TIMEOUT_SECONDS = int(
    os.getenv("EXECUTION_TIMEOUT_SECONDS") or os.getenv("EXECUTION_TIMEOUT") or "15"
)
