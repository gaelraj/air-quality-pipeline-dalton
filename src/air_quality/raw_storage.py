import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def slugify_city_name(city_name: str) -> str:
    return city_name.lower().replace(" ", "_").replace("-", "_").replace("'", "")


def save_raw_response(
    city: dict[str, Any],
    api_response: dict[str, Any],
    collected_at: datetime | None = None,
) -> Path:
    if collected_at is None:
        collected_at = datetime.now(timezone.utc)

    city_slug = slugify_city_name(city["city_name"])
    timestamp = collected_at.strftime("%Y%m%dT%H%M%SZ")

    city_dir = RAW_DIR / f"city={city_slug}"
    city_dir.mkdir(parents=True, exist_ok=True)

    file_path = city_dir / f"{timestamp}.json"

    if file_path.exists():
        raise FileExistsError(f"Raw file already exists: {file_path}")

    raw_payload = {
        "metadata": {
            "city_name": city["city_name"],
            "country": city["country"],
            "latitude": city["latitude"],
            "longitude": city["longitude"],
            "source": "openweather",
            "collected_at_utc": collected_at.isoformat(),
        },
        "api_response": api_response,
    }

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(raw_payload, file, ensure_ascii=False, indent=2)

    return file_path


def save_historical_raw_response(
    city: dict[str, Any],
    api_response: dict[str, Any],
    start_datetime: datetime,
    end_datetime: datetime,
    collected_at: datetime | None = None,
) -> Path:
    if collected_at is None:
        collected_at = datetime.now(timezone.utc)

    city_slug = slugify_city_name(city["city_name"])

    start_label = start_datetime.strftime("%Y%m%dT%H%M%SZ")
    end_label = end_datetime.strftime("%Y%m%dT%H%M%SZ")
    collected_label = collected_at.strftime("%Y%m%dT%H%M%SZ")

    city_dir = RAW_DIR / f"city={city_slug}"
    city_dir.mkdir(parents=True, exist_ok=True)

    file_path = city_dir / f"history_{start_label}_{end_label}_collected_{collected_label}.json"

    if file_path.exists():
        raise FileExistsError(f"Raw file already exists: {file_path}")

    raw_payload = {
        "metadata": {
            "city_name": city["city_name"],
            "country": city["country"],
            "latitude": city["latitude"],
            "longitude": city["longitude"],
            "source": "openweather",
            "request_type": "history",
            "period_start_utc": start_datetime.isoformat(),
            "period_end_utc": end_datetime.isoformat(),
            "collected_at_utc": collected_at.isoformat(),
        },
        "api_response": api_response,
    }

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(raw_payload, file, ensure_ascii=False, indent=2)

    return file_path
