from time import sleep

import requests

from air_quality.config import (
    get_openweather_current_url,
    get_openweather_history_url,
)


def fetch_current_air_quality(
    latitude: float,
    longitude: float,
    api_key: str,
    max_attempts: int = 3,
) -> dict:
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
    }

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(
                get_openweather_current_url(),
                params=params,
                timeout=(20, 60),
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as error:
            if attempt == max_attempts:
                raise

            wait_seconds = attempt * 10
            print(
                f"OpenWeather current request failed. "
                f"Attempt {attempt}/{max_attempts}. "
                f"Retrying in {wait_seconds} seconds. "
                f"Error: {error}"
            )
            sleep(wait_seconds)


def fetch_historical_air_quality(
    latitude: float,
    longitude: float,
    api_key: str,
    start_timestamp: int,
    end_timestamp: int,
    max_attempts: int = 3,
) -> dict:
    params = {
        "lat": latitude,
        "lon": longitude,
        "start": start_timestamp,
        "end": end_timestamp,
        "appid": api_key,
    }

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(
                get_openweather_history_url(),
                params=params,
                timeout=(20, 60),
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as error:
            if attempt == max_attempts:
                raise

            wait_seconds = attempt * 10
            print(
                f"OpenWeather historical request failed. "
                f"Attempt {attempt}/{max_attempts}. "
                f"Retrying in {wait_seconds} seconds. "
                f"Error: {error}"
            )
            sleep(wait_seconds)


