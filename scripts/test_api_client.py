from air_quality.api_client import fetch_current_air_quality
from air_quality.config import get_openweather_api_key
from air_quality.cities import CITIES


def main() -> None:
    api_key = get_openweather_api_key()
    city = CITIES[0]

    data = fetch_current_air_quality(
        latitude=city["latitude"],
        longitude=city["longitude"],
        api_key=api_key,
    )

    print("City:", city["city_name"])
    print("AQI:", data["list"][0]["main"]["aqi"])
    print("Components:", data["list"][0]["components"])


if __name__ == "__main__":
    main()
