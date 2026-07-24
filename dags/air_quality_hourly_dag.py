from datetime import datetime, timedelta
from pathlib import Path
import sys

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from air_quality.clean_builder import rebuild_clean_csv
from air_quality.current_collector import collect_current_air_quality
from air_quality.validation import validate_clean_csv
from air_quality.warehouse_loader import load_warehouse

default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="air_quality_hourly_pipeline",
    description="Hourly air quality pipeline from OpenWeather to PostgreSQL warehouse",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["air-quality", "aqi", "warehouse"],
) as dag:

    collect_raw_data = PythonOperator(
        task_id="collect_raw_data",
        python_callable=collect_current_air_quality,
        do_xcom_push=False,
    )

    rebuild_clean_data = PythonOperator(
        task_id="rebuild_clean_data",
        python_callable=rebuild_clean_csv,
        do_xcom_push=False,
    )

    validate_clean_data = PythonOperator(
        task_id="validate_clean_data",
        python_callable=validate_clean_csv,
        do_xcom_push=False,
    )

    load_data_warehouse = PythonOperator(
        task_id="load_data_warehouse",
        python_callable=load_warehouse,
        do_xcom_push=False,
    )

    collect_raw_data >> rebuild_clean_data >> validate_clean_data >> load_data_warehouse


