import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CLEAN_DIR = PROJECT_ROOT / "data" / "clean"
CLEAN_FILE = CLEAN_DIR / "air_quality_clean.csv"


CLEAN_COLUMNS = [
    "city_name",
    "country",
    "latitude",
    "longitude",
    "observed_at_utc",
    "aqi",
    "co",
    "no",
    "no2",
    "o3",
    "so2",
    "pm2_5",
    "pm10",
    "nh3",
    "source",
    "ingested_at_utc",
]


def round_to_hour(timestamp: int) -> str:
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    rounded_dt = dt.replace(minute=0, second=0, microsecond=0)
    return rounded_dt.isoformat()


def extract_rows(raw_payload: dict[str, Any]) -> list[dict[str, Any]]:
    metadata = raw_payload["metadata"]
    api_response = raw_payload["api_response"]

    rows = []

    for measurement in api_response["list"]:
        components = measurement["components"]

        rows.append(
            {
                "city_name": metadata["city_name"],
                "country": metadata["country"],
                "latitude": metadata["latitude"],
                "longitude": metadata["longitude"],
                "observed_at_utc": round_to_hour(measurement["dt"]),
                "aqi": measurement["main"]["aqi"],
                "co": components.get("co"),
                "no": components.get("no"),
                "no2": components.get("no2"),
                "o3": components.get("o3"),
                "so2": components.get("so2"),
                "pm2_5": components.get("pm2_5"),
                "pm10": components.get("pm10"),
                "nh3": components.get("nh3"),
                "source": metadata["source"],
                "ingested_at_utc": metadata["collected_at_utc"],
            }
        )

    return rows


def rebuild_clean_csv() -> Path:
    rows = []

    for raw_file in sorted(RAW_DIR.glob("city=*/*.json")):
        with raw_file.open("r", encoding="utf-8") as file:
            raw_payload = json.load(file)

        rows.extend(extract_rows(raw_payload))

    if not rows:
        raise RuntimeError("No raw files found. Run collect_current.py first.")

    df = pd.DataFrame(rows, columns=CLEAN_COLUMNS)

    df["observed_at_utc"] = pd.to_datetime(df["observed_at_utc"], utc=True)
    df["ingested_at_utc"] = pd.to_datetime(df["ingested_at_utc"], utc=True)

    df = df.sort_values(
        by=["observed_at_utc", "city_name", "ingested_at_utc"],
    )

    df = df.drop_duplicates(
        subset=["city_name", "observed_at_utc"],
        keep="last",
    )

    df = df.sort_values(
        by=["observed_at_utc", "city_name"],
    )

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_FILE, index=False)

    return CLEAN_FILE
