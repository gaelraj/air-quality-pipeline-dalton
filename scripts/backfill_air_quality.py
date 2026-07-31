import argparse
from datetime import datetime, timedelta, timezone
from time import sleep

from air_quality.api_client import fetch_historical_air_quality
from air_quality.cities import CITIES
from air_quality.config import get_openweather_api_key
from air_quality.raw_storage import save_historical_raw_response


def parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def parse_args():
    parser = argparse.ArgumentParser(description="Backfill historical air quality data")
    parser.add_argument("--days", type=int, default=None)
    parser.add_argument("--start-date", type=str, default=None)
    parser.add_argument("--end-date", type=str, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    api_key = get_openweather_api_key()
    collected_at = datetime.now(timezone.utc)

    if args.start_date and args.end_date:
        start_datetime = parse_date(args.start_date)
        end_datetime = parse_date(args.end_date)
    else:
        days = args.days or 7
        end_datetime = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        start_datetime = end_datetime - timedelta(days=days)

    if start_datetime >= end_datetime:
        raise ValueError("start_datetime must be before end_datetime")

    current_start = start_datetime

    while current_start < end_datetime:
        current_end = min(current_start + timedelta(days=1), end_datetime)

        print(f"Backfilling period: {current_start} -> {current_end}")

        for city in CITIES:
            print(f"Fetching city: {city['city_name']}")

            api_response = fetch_historical_air_quality(
                latitude=city["latitude"],
                longitude=city["longitude"],
                api_key=api_key,
                start_timestamp=int(current_start.timestamp()),
                end_timestamp=int(current_end.timestamp()),
            )

            file_path = save_historical_raw_response(
                city=city,
                api_response=api_response,
                start_datetime=current_start,
                end_datetime=current_end,
                collected_at=collected_at,
            )

            print(f"Saved historical raw file: {file_path}")
            print(f"Measurements: {len(api_response['list'])}")

            sleep(1)

        current_start = current_end


if __name__ == "__main__":
    main()
