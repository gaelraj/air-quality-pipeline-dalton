from pathlib import Path

import psycopg

from air_quality.config import get_database_url


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = PROJECT_ROOT / "sql" / "001_create_warehouse_schema.sql"


def main() -> None:
    database_url = get_database_url()

    schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema_sql)

        connection.commit()

    print("Warehouse schema created successfully")


if __name__ == "__main__":
    main()
