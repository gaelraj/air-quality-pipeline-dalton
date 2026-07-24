from datetime import datetime, timezone
from pathlib import Path

from air_quality.api_client import fetch_current_air_quality
from air_quality.cities import CITIES
from air_quality.config import get_openweather_api_key
from air_quality.raw_storage import save_raw_response


def collect_current_air_quality() -> list[Path]:
    api_key = get_openweather_api_key()
    collected_at = datetime.now(timezone.utc)

    saved_files = []

    for city in CITIES:
        api_response = fetch_current_air_quality(
            latitude=city["latitude"],
            longitude=city["longitude"],
            api_key=api_key,
        )

        file_path = save_raw_response(
            city=city,
            api_response=api_response,
            collected_at=collected_at,
        )

        saved_files.append(file_path)
        print(f"Saved raw file: {file_path}")

    return saved_files


