from datetime import datetime, timedelta, timezone

from air_quality.api_client import fetch_historical_air_quality
from air_quality.cities import CITIES
from air_quality.config import get_openweather_api_key


def main() -> None:
    api_key = get_openweather_api_key()
    city = CITIES[0]

    end_datetime = datetime.now(timezone.utc)
    start_datetime = end_datetime - timedelta(days=1)

    data = fetch_historical_air_quality(
        latitude=city["latitude"],
        longitude=city["longitude"],
        api_key=api_key,
        start_timestamp=int(start_datetime.timestamp()),
        end_timestamp=int(end_datetime.timestamp()),
    )

    print("City:", city["city_name"])
    print("Number of historical measurements:", len(data["list"]))

    if data["list"]:
        first_measurement = data["list"][0]
        print("First AQI:", first_measurement["main"]["aqi"])
        print("First components:", first_measurement["components"])


if __name__ == "__main__":
    main()
