from pathlib import Path

import psycopg

from air_quality.config import get_database_url


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = PROJECT_ROOT / "sql" / "001_create_warehouse_schema.sql"


def run_schema() -> None:
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_FILE}")

    database_url = get_database_url()
    schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")

    print(f"Executing schema file: {SCHEMA_FILE}")

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema_sql, prepare=False)

        connection.commit()

    print("Warehouse schema created successfully")


def main() -> None:
    run_schema()


if __name__ == "__main__":
    main()
