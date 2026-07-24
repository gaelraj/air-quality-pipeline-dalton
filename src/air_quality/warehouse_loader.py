from pathlib import Path
from typing import Any

import pandas as pd
import psycopg

from air_quality.config import get_database_url
from air_quality.validation import validate_clean_csv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEAN_FILE = PROJECT_ROOT / "data" / "clean" / "air_quality_clean.csv"


def nullable_float(value: Any) -> float | None:
    """Convert a pandas value to a Python float or None."""
    if pd.isna(value):
        return None

    return float(value)


def upsert_city(cursor: psycopg.Cursor, row: pd.Series) -> int:
    cursor.execute(
        """
        INSERT INTO dim_city (
            city_name,
            country,
            latitude,
            longitude
        )
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (city_name, country)
        DO UPDATE SET
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude
        RETURNING city_id;
        """,
        (
            str(row["city_name"]),
            str(row["country"]),
            float(row["latitude"]),
            float(row["longitude"]),
        ),
    )

    result = cursor.fetchone()

    if result is None:
        raise RuntimeError("Unable to retrieve city_id")

    return int(result[0])


def upsert_time(cursor: psycopg.Cursor, observed_at: pd.Timestamp) -> int:
    cursor.execute(
        """
        INSERT INTO dim_time (
            observed_at_utc,
            date_value,
            hour_value,
            day_value,
            month_value,
            year_value,
            day_of_week,
            is_weekend
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (observed_at_utc)
        DO UPDATE SET
            date_value = EXCLUDED.date_value,
            hour_value = EXCLUDED.hour_value,
            day_value = EXCLUDED.day_value,
            month_value = EXCLUDED.month_value,
            year_value = EXCLUDED.year_value,
            day_of_week = EXCLUDED.day_of_week,
            is_weekend = EXCLUDED.is_weekend
        RETURNING time_id;
        """,
        (
            observed_at.to_pydatetime(),
            observed_at.date(),
            int(observed_at.hour),
            int(observed_at.day),
            int(observed_at.month),
            int(observed_at.year),
            int(observed_at.dayofweek),
            bool(observed_at.dayofweek >= 5),
        ),
    )

    result = cursor.fetchone()

    if result is None:
        raise RuntimeError("Unable to retrieve time_id")

    return int(result[0])


def upsert_air_quality_fact(
    cursor: psycopg.Cursor,
    city_id: int,
    time_id: int,
    row: pd.Series,
) -> None:
    ingested_at = pd.Timestamp(row["ingested_at_utc"])

    cursor.execute(
        """
        INSERT INTO fact_air_quality (
            city_id,
            time_id,
            aqi,
            co,
            no,
            no2,
            o3,
            so2,
            pm2_5,
            pm10,
            nh3,
            source,
            ingested_at_utc
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (city_id, time_id)
        DO UPDATE SET
            aqi = EXCLUDED.aqi,
            co = EXCLUDED.co,
            no = EXCLUDED.no,
            no2 = EXCLUDED.no2,
            o3 = EXCLUDED.o3,
            so2 = EXCLUDED.so2,
            pm2_5 = EXCLUDED.pm2_5,
            pm10 = EXCLUDED.pm10,
            nh3 = EXCLUDED.nh3,
            source = EXCLUDED.source,
            ingested_at_utc = EXCLUDED.ingested_at_utc;
        """,
        (
            city_id,
            time_id,
            int(row["aqi"]),
            nullable_float(row["co"]),
            nullable_float(row["no"]),
            nullable_float(row["no2"]),
            nullable_float(row["o3"]),
            nullable_float(row["so2"]),
            nullable_float(row["pm2_5"]),
            nullable_float(row["pm10"]),
            nullable_float(row["nh3"]),
            str(row["source"]),
            ingested_at.to_pydatetime(),
        ),
    )


def load_warehouse() -> int:
    if not CLEAN_FILE.exists():
        raise FileNotFoundError(f"Clean CSV not found: {CLEAN_FILE}")

    validate_clean_csv()

    dataframe = pd.read_csv(
        CLEAN_FILE,
        parse_dates=["observed_at_utc", "ingested_at_utc"],
    )

    database_url = get_database_url()

    print(f"Reading clean file: {CLEAN_FILE}")
    print(f"Starting warehouse load: {len(dataframe)} rows")

    with psycopg.connect(database_url) as connection:
        print("Database connection opened")

        with connection.cursor() as cursor:
            for _, row in dataframe.iterrows():
                observed_at = pd.Timestamp(row["observed_at_utc"])

                city_id = upsert_city(cursor, row)
                time_id = upsert_time(cursor, observed_at)

                upsert_air_quality_fact(
                    cursor=cursor,
                    city_id=city_id,
                    time_id=time_id,
                    row=row,
                )

        connection.commit()
        print("Database transaction committed")

    return len(dataframe)
