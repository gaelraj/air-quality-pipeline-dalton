from datetime import datetime, timedelta, timezone

from air_quality.api_client import fetch_historical_air_quality
from air_quality.cities import CITIES
from air_quality.config import get_openweather_api_key
from air_quality.raw_storage import save_historical_raw_response


def main() -> None:
    api_key = get_openweather_api_key()
    collected_at = datetime.now(timezone.utc)

    end_datetime = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start_datetime = end_datetime - timedelta(days=1)

    for city in CITIES:
        api_response = fetch_historical_air_quality(
            latitude=city["latitude"],
            longitude=city["longitude"],
            api_key=api_key,
            start_timestamp=int(start_datetime.timestamp()),
            end_timestamp=int(end_datetime.timestamp()),
        )

        file_path = save_historical_raw_response(
            city=city,
            api_response=api_response,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            collected_at=collected_at,
        )

        print(f"Saved historical raw file: {file_path}")
        print(f"Measurements: {len(api_response['list'])}")


if __name__ == "__main__":
    main()


