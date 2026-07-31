# Air Quality Pipeline Runbook

## 1. Purpose

This runbook explains how to run and verify the air quality data pipeline.

It covers:

- environment setup;
- manual execution;
- historical backfill;
- Airflow execution;
- warehouse verification.

## 2. Set Up the Python Environment

Go to the project root directory:

```bash
cd air-quality-pipeline
```

Or, if the project is located elsewhere:

```bash
cd <project-root>
```

Create a Python virtual environment if it does not already exist:

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Export the Python path:

```bash
export PYTHONPATH="$PWD/src:$PYTHONPATH"
```

## 3. Required Environment Variables

The project requires a `.env` file at the project root.

Required variables:

```env
OPENWEATHER_API_KEY=your_openweather_api_key
DATABASE_URL=your_postgresql_connection_string
OPENWEATHER_CURRENT_URL=https://api.openweathermap.org/data/2.5/air_pollution
OPENWEATHER_HISTORY_URL=https://api.openweathermap.org/data/2.5/air_pollution/history
```

The `.env` file must never be committed to Git.

## 4. Test the Current API Client

```bash
python scripts/test_api_client.py
```

Expected result:

```text
City: Antananarivo
AQI: ...
Components: {...}
```

## 5. Test the Historical API Client

```bash
python scripts/test_history_api_client.py
```

Expected result:

```text
City: Antananarivo
Number of historical measurements: ...
First AQI: ...
First components: {...}
```

## 6. Run the Manual Pipeline

### 6.1 Collect current air quality data

```bash
python scripts/collect_current.py
```

This creates raw JSON files in:

```text
data/raw/
```

### 6.2 Rebuild the clean CSV

```bash
python scripts/rebuild_clean.py
```

This creates or updates:

```text
data/clean/air_quality_clean.csv
```

### 6.3 Validate the clean CSV

```bash
python scripts/validate_clean.py
```

Expected result:

```text
Clean CSV validation passed
```

### 6.4 Create the warehouse schema

```bash
python scripts/run_schema.py
```

Expected result:

```text
Warehouse schema created successfully
```

### 6.5 Load the warehouse

```bash
python scripts/load_warehouse.py
```

Expected result:

```text
Warehouse loaded successfully: ... rows processed
```

## 7. Historical Backfill

To test a small historical backfill:

```bash
python scripts/backfill_air_quality.py --days 3
```

This only writes historical raw JSON files.

After the backfill, rebuild and load the warehouse:

```bash
python scripts/rebuild_clean.py
python scripts/validate_clean.py
python scripts/load_warehouse.py
```

A larger backfill can be executed later during the group phase.

## 8. Airflow DAG

The Airflow DAG is:

```text
dags/air_quality_hourly_dag.py
```

The DAG name is:

```text
air_quality_hourly_pipeline
```

The task order is:

```text
collect_raw_data
↓
rebuild_clean_data
↓
validate_clean_data
↓
load_data_warehouse
```

## 9. Link the DAG to Airflow

If Airflow does not automatically detect the DAG, create a symbolic link from the project DAG file to the Airflow DAGs folder.

Default local Airflow DAGs folder:

```bash
mkdir -p ~/airflow/dags
```

Create the symbolic link from the project root:

```bash
ln -sf "$PWD/dags/air_quality_hourly_dag.py" ~/airflow/dags/air_quality_hourly_dag.py
```

If your Airflow home directory is different, replace `~/airflow/dags` with your own Airflow DAGs folder.

## 10. Check Airflow Import Errors

```bash
airflow dags list-import-errors --local
```

Expected result:

```text
No data found
```

## 11. Check if the DAG is Detected

```bash
airflow dags list --local | grep air_quality
```

Expected result:

```text
air_quality_hourly_pipeline
```

## 12. Test the DAG Manually

```bash
airflow dags test air_quality_hourly_pipeline 2026-07-04
```

Expected result:

```text
Dag run in success state
```

## 13. Run Airflow Locally

```bash
airflow standalone
```

Open the Airflow UI in the browser:

```text
http://localhost:8080
```

The DAG must be unpaused to run automatically every hour.

## 14. Verify Warehouse Data in Neon

### 14.1 Count all measurements

```sql
SELECT COUNT(*) AS total_measurements
FROM fact_air_quality;
```

### 14.2 Count measurements by city

```sql
SELECT 
    c.city_name,
    COUNT(*) AS measurement_count
FROM fact_air_quality f
JOIN dim_city c ON c.city_id = f.city_id
GROUP BY c.city_name
ORDER BY c.city_name;
```

### 14.3 Check the covered period

```sql
SELECT 
    MIN(t.observed_at_utc) AS first_observation,
    MAX(t.observed_at_utc) AS last_observation
FROM fact_air_quality f
JOIN dim_time t ON t.time_id = f.time_id;
```

### 14.4 Average AQI by city

```sql
SELECT 
    c.city_name,
    ROUND(AVG(f.aqi), 2) AS average_aqi
FROM fact_air_quality f
JOIN dim_city c ON c.city_id = f.city_id
GROUP BY c.city_name
ORDER BY average_aqi DESC;
```

### 14.5 Average PM2.5 by city

```sql
SELECT 
    c.city_name,
    ROUND(AVG(f.pm2_5), 2) AS average_pm2_5
FROM fact_air_quality f
JOIN dim_city c ON c.city_id = f.city_id
GROUP BY c.city_name
ORDER BY average_pm2_5 DESC;
```

## 15. Troubleshooting

### 15.1 OpenWeather timeout

If the API times out, rerun the failed task or wait for the next Airflow execution.

The API client already includes retry logic.

### 15.2 Airflow does not detect the DAG

Check the symbolic link:

```bash
ls -l ~/airflow/dags
```

Then check import errors:

```bash
airflow dags list-import-errors --local
```

### 15.3 Warehouse loading is slow

The loader inserts data row by row and prints progress logs.

This is normal for small test datasets.

### 15.4 `.env` is missing

Create a `.env` file from `.env.example` and fill in the real values.

Do not commit `.env`.

## 16. Current Project Status

The project has been tested with:

- current API collection;
- historical API collection;
- raw JSON storage;
- clean CSV generation;
- clean CSV validation;
- PostgreSQL warehouse loading;
- Airflow DAG execution.
