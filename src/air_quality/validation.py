from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEAN_FILE = PROJECT_ROOT / "data" / "clean" / "air_quality_clean.csv"


REQUIRED_COLUMNS = [
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


def validate_clean_csv() -> None:
    if not CLEAN_FILE.exists():
        raise FileNotFoundError(f"Clean file not found: {CLEAN_FILE}")

    df = pd.read_csv(CLEAN_FILE)

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    duplicated_rows = df.duplicated(
        subset=["city_name", "observed_at_utc"],
        keep=False,
    )

    if duplicated_rows.any():
        duplicates = df.loc[duplicated_rows, ["city_name", "observed_at_utc"]]
        raise ValueError(f"Duplicated city/hour rows found:\n{duplicates}")

    if df["aqi"].isna().any():
        raise ValueError("AQI contains missing values")

    if df["city_name"].isna().any():
        raise ValueError("city_name contains missing values")

    if df["observed_at_utc"].isna().any():
        raise ValueError("observed_at_utc contains missing values")

    df["observed_at_utc"] = pd.to_datetime(df["observed_at_utc"], utc=True)

    sorted_df = df.sort_values(
        by=["observed_at_utc", "city_name"],
    )

    if not df[["observed_at_utc", "city_name"]].equals(
        sorted_df[["observed_at_utc", "city_name"]]
    ):
        raise ValueError("Clean CSV is not sorted by observed_at_utc and city_name")

    print("Clean CSV validation passed")
