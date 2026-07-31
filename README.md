# Air Quality Data Pipeline

This project is an automated data pipeline that collects air quality data from the OpenWeather Air Pollution API, stores raw responses, rebuilds a clean CSV dataset, validates the data, and loads it into a PostgreSQL data warehouse hosted on Neon.

## Project Objective

The objective is to collect air quality data for at least five cities and prepare the data for analytical use.

The pipeline supports:

- hourly air quality collection;
- raw data storage;
- clean CSV reconstruction;
- data validation;
- loading into a dimensional PostgreSQL warehouse;
- historical backfill for past data.

## Data Source

The data source is the OpenWeather Air Pollution API.

The collected data includes:

- AQI;
- CO;
- NO;
- NO2;
- O3;
- SO2;
- PM2.5;
- PM10;
- NH3.

Pollutant values are expressed in micrograms per cubic meter.

## Monitored Cities

The current monitored cities are:

| City | Country |
|---|---|
| Antananarivo | MG |
| Toamasina | MG |
| Mahajanga | MG |
| Fianarantsoa | MG |
| Antsiranana | MG |

The city coordinates are defined in:

```text
src/air_quality/cities.py
```

## Project Structure

```text
air-quality-pipeline/
├── dags/
│   └── air_quality_hourly_dag.py
├── src/
│   └── air_quality/
│       ├── api_client.py
│       ├── cities.py
│       ├── clean_builder.py
│       ├── config.py
│       ├── current_collector.py
│       ├── raw_storage.py
│       ├── validation.py
│       └── warehouse_loader.py
├── scripts/
│   ├── backfill_air_quality.py
│   ├── backfill_one_day.py
│   ├── collect_current.py
│   ├── load_warehouse.py
│   ├── rebuild_clean.py
│   ├── run_schema.py
│   ├── test_api_client.py
│   ├── test_history_api_client.py
│   └── validate_clean.py
├── sql/
│   └── 001_create_warehouse_schema.sql
├── data/
│   ├── raw/
│   └── clean/
├── ARCHITECTURE.md
├── DATA_CONTRACT.md
├── README.md
└── .env.example
```

## Pipeline Overview

The pipeline follows this flow:

```text
OpenWeather API
↓
Raw JSON files
↓
Clean CSV file
↓
Data validation
↓
PostgreSQL data warehouse
```

The raw files are stored in:

```text
data/raw/
```

The clean CSV file is stored in:

```text
data/clean/air_quality_clean.csv
```

## Environment Variables

The project requires a `.env` file at the project root.

Example:

```env
OPENWEATHER_API_KEY=your_openweather_api_key
DATABASE_URL=your_postgresql_connection_string
```

The `.env` file must not be committed to Git.

## Install Dependencies

Activate the Python virtual environment first:

```bash
source ~/airflow_project/airflow_venv/bin/activate
```

Then install the required dependencies if needed:

```bash
pip install requests pandas python-dotenv psycopg[binary] apache-airflow
```

## Manual Pipeline Execution

From the project root:

```bash
export PYTHONPATH="$PWD/src:$PYTHONPATH"
```

Collect current air quality data:

```bash
python scripts/collect_current.py
```

Rebuild the clean CSV file:

```bash
python scripts/rebuild_clean.py
```

Validate the clean CSV file:

```bash
python scripts/validate_clean.py
```

Create the warehouse schema:

```bash
python scripts/run_schema.py
```

Load the warehouse:

```bash
python scripts/load_warehouse.py
```

## Historical Backfill

The project includes a historical backfill script:

```bash
python scripts/backfill_air_quality.py --days 3
```

This script collects historical data and stores it in `data/raw/`.

The backfill does not directly load data into the warehouse. After running a backfill, the clean CSV must be rebuilt, validated, and loaded into PostgreSQL.

```bash
python scripts/rebuild_clean.py
python scripts/validate_clean.py
python scripts/load_warehouse.py
```

## Airflow Orchestration

The Airflow DAG is located in:

```text
dags/air_quality_hourly_dag.py
```

The DAG runs the following tasks:

```text
collect_raw_data
↓
rebuild_clean_data
↓
validate_clean_data
↓
load_data_warehouse
```

The DAG is scheduled hourly.

```text
schedule="@hourly"
```

The DAG uses `catchup=False`, so Airflow does not automatically rerun all missed historical hours. Historical data is handled separately by the backfill script.

## Data Warehouse Model

The PostgreSQL warehouse uses a star schema.

### Dimension Tables

```text
dim_city
dim_time
```

### Fact Table

```text
fact_air_quality
```

The fact table stores AQI and pollutant measurements. It references the city and time dimensions using foreign keys.

## Useful SQL Checks

Count all measurements:

```sql
SELECT COUNT(*) AS total_measurements
FROM fact_air_quality;
```

Count measurements by city:

```sql
SELECT 
    c.city_name,
    COUNT(*) AS measurement_count
FROM fact_air_quality f
JOIN dim_city c ON c.city_id = f.city_id
GROUP BY c.city_name
ORDER BY c.city_name;
```

Check the covered period:

```sql
SELECT 
    MIN(t.observed_at_utc) AS first_observation,
    MAX(t.observed_at_utc) AS last_observation
FROM fact_air_quality f
JOIN dim_time t ON t.time_id = f.time_id;
```

Average AQI by city:

```sql
SELECT 
    c.city_name,
    ROUND(AVG(f.aqi), 2) AS average_aqi
FROM fact_air_quality f
JOIN dim_city c ON c.city_id = f.city_id
GROUP BY c.city_name
ORDER BY average_aqi DESC;
```

Average PM2.5 by city:

```sql
SELECT 
    c.city_name,
    ROUND(AVG(f.pm2_5), 2) AS average_pm2_5
FROM fact_air_quality f
JOIN dim_city c ON c.city_id = f.city_id
GROUP BY c.city_name
ORDER BY average_pm2_5 DESC;
```

Average AQI by hour:

```sql
SELECT 
    t.hour_value,
    ROUND(AVG(f.aqi), 2) AS average_aqi
FROM fact_air_quality f
JOIN dim_time t ON t.time_id = f.time_id
GROUP BY t.hour_value
ORDER BY t.hour_value;
```

## Current Status

The pipeline has been tested with:

- current hourly collection;
- historical backfill for a small number of days;
- clean CSV reconstruction;
- validation;
- PostgreSQL warehouse loading;
- Airflow DAG execution.

The larger historical backfill can be executed later during the group project phase.
