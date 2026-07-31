from pathlib import Path

import pandas as pd
import psycopg

from air_quality.config import get_database_url


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEAN_FILE = PROJECT_ROOT / "data" / "clean" / "air_quality_clean.csv"


def upsert_city(cursor, row) -> int:
    cursor.execute(
        """
        INSERT INTO dim_city (city_name, country, latitude, longitude)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (city_name, country, latitude, longitude)
        DO NOTHING
        RETURNING city_id;
        """,
        (
            row["city_name"],
            row["country"],
            row["latitude"],
            row["longitude"],
        ),
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute(
        """
        SELECT city_id
        FROM dim_city
        WHERE city_name = %s
          AND country = %s
          AND latitude = %s
          AND longitude = %s;
        """,
        (
            row["city_name"],
            row["country"],
            row["latitude"],
            row["longitude"],
        ),
    )

    return cursor.fetchone()[0]


def upsert_time(cursor, observed_at_utc) -> int:
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
        DO NOTHING
        RETURNING time_id;
        """,
        (
            observed_at_utc,
            observed_at_utc.date(),
            observed_at_utc.hour,
            observed_at_utc.day,
            observed_at_utc.month,
            observed_at_utc.year,
            observed_at_utc.weekday(),
            observed_at_utc.weekday() >= 5,
        ),
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute(
        """
        SELECT time_id
        FROM dim_time
        WHERE observed_at_utc = %s;
        """,
        (observed_at_utc,),
    )

    return cursor.fetchone()[0]


def upsert_fact(cursor, row, city_id: int, time_id: int) -> None:
    ingested_at_utc = pd.to_datetime(
        row["ingested_at_utc"],
        utc=True,
    ).to_pydatetime()

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
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            row["aqi"],
            row["co"],
            row["no"],
            row["no2"],
            row["o3"],
            row["so2"],
            row["pm2_5"],
            row["pm10"],
            row["nh3"],
            row["source"],
            ingested_at_utc,
        ),
    )


def get_latest_observation(cursor):
    cursor.execute(
        """
        SELECT MAX(t.observed_at_utc)
        FROM fact_air_quality f
        JOIN dim_time t ON t.time_id = f.time_id;
        """
    )

    return cursor.fetchone()[0]

def load_warehouse() -> None:
    if not CLEAN_FILE.exists():
        raise FileNotFoundError(f"Clean file not found: {CLEAN_FILE}")

    print(f"Reading clean file: {CLEAN_FILE}")

    df = pd.read_csv(CLEAN_FILE)
    df["observed_at_utc"] = pd.to_datetime(
        df["observed_at_utc"],
        utc=True,
    )

    database_url = get_database_url()
    current_utc_hour = pd.Timestamp.now(tz="UTC").floor("h")

    with psycopg.connect(database_url) as connection:
        print("Database connection opened")

        with connection.cursor() as cursor:
            latest_observation = get_latest_observation(cursor)

            if latest_observation is None:
                rows_to_load = df[
                    df["observed_at_utc"] <= current_utc_hour
                ].copy()

                print(
                    "Warehouse is empty: loading all available "
                    "observations up to the current UTC hour"
                )
            else:
                latest_observation = pd.Timestamp(latest_observation)

                rows_to_load = df[
                    (
                        df["observed_at_utc"]
                        >= latest_observation
                    )
                    & (
                        df["observed_at_utc"]
                        <= current_utc_hour
                    )
                ].copy()

                print(
                    "Latest warehouse observation:",
                    latest_observation,
                )

            print("Current UTC hour:", current_utc_hour)
            print(
                "Starting incremental warehouse load: "
                f"{len(rows_to_load)} rows"
            )

            if rows_to_load.empty:
                print("No new warehouse observations to load")
                return

            for row_number, (_, row) in enumerate(
                rows_to_load.iterrows(),
                start=1,
            ):
                if row_number == 1 or row_number % 10 == 0:
                    print(
                        f"Processing row "
                        f"{row_number}/{len(rows_to_load)}"
                    )

                observed_at_utc = row[
                    "observed_at_utc"
                ].to_pydatetime()

                city_id = upsert_city(cursor, row)
                time_id = upsert_time(cursor, observed_at_utc)

                upsert_fact(
                    cursor=cursor,
                    row=row,
                    city_id=city_id,
                    time_id=time_id,
                )

        connection.commit()
        print("Database transaction committed")

    print(
        "Warehouse loaded successfully: "
        f"{len(rows_to_load)} rows processed"
    )
