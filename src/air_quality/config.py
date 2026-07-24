import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


def get_openweather_api_key() -> str:
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        raise RuntimeError("OPENWEATHER_API_KEY is missing from the .env file")

    return api_key


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is missing from the .env file")

    return database_url

def get_openweather_current_url() -> str:
    return os.getenv(
        "OPENWEATHER_CURRENT_URL",
        "https://api.openweathermap.org/data/2.5/air_pollution",
    )


def get_openweather_history_url() -> str:
    return os.getenv(
        "OPENWEATHER_HISTORY_URL",
        "https://api.openweathermap.org/data/2.5/air_pollution/history",
    )


