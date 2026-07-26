# Air Quality Data Pipeline

This project is an automated data pipeline that collects air quality data from the OpenWeather Air Pollution API, stores raw responses, rebuilds a clean CSV dataset, validates the data, and loads it into a PostgreSQL data warehouse hosted on Neon.

## Project objective

The objective is to collect air quality data for at least five cities and make it available for analysis.

The pipeline supports:

- hourly air quality collection;
- historical backfill;
- raw JSON storage;
- clean CSV reconstruction;
- data validation;
- PostgreSQL warehouse loading;
- automatic orchestration with GitHub Actions.

## Data source

The data source is the OpenWeather Air Pollution API.

The collected measurements include:

- AQI;
- CO;
- NO;
- NO2;
- O3;
- SO2;
- PM2.5;
- PM10;
- NH3.

Pollutant values are stored as returned by the API.

## Monitored cities

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

## Project structure

```text
air-quality-pipeline/
├── .github/
│   └── workflows/
│       ├── aqi_hourly_pipeline.yml
│       └── aqi_backfill_pipeline.yml
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
├── RUNBOOK.md
├── DEPLOYMENT_PLAN.md
├── REPORT.md
├── SUBMISSION_CHECKLIST.md
└── .env.example
```

## Pipeline overview

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
PostgreSQL data warehouse on Neon
```

The raw files are stored in:

```text
data/raw/
```

The clean CSV file is stored in:

```text
data/clean/air_quality_clean.csv
```

## GitHub Actions orchestration

The project uses GitHub Actions as the orchestrator.

There are two workflows:

```text
.github/workflows/aqi_hourly_pipeline.yml
.github/workflows/aqi_backfill_pipeline.yml
```

### Hourly pipeline

The hourly workflow runs every hour and can also be started manually.

It executes the following steps:

```text
collect_current.py
↓
rebuild_clean.py
↓
validate_clean.py
↓
run_schema.py
↓
load_warehouse.py
↓
commit generated raw and clean data
```

### Backfill pipeline

The backfill workflow is manual.

It receives the number of past days to backfill, generates historical raw files, rebuilds the clean CSV, validates it, creates the warehouse schema if needed, loads Neon, and commits generated raw and clean files.

## Data storage rule

The `data/raw/` and `data/clean/` folders are ignored for normal local commits because they contain generated data.

GitHub Actions is allowed to commit generated data explicitly with:

```bash
git add -f data/raw data/clean
```

This keeps local development clean while preserving pipeline outputs in the repository after automated runs.

## Local execution

From the project root, install dependencies:

```bash
pip install -r requirements.txt
```

Export the Python path:

```bash
export PYTHONPATH="$PWD/src:$PYTHONPATH"
```

Run the manual pipeline:

```bash
python scripts/collect_current.py
python scripts/rebuild_clean.py
python scripts/validate_clean.py
python scripts/run_schema.py
python scripts/load_warehouse.py
```

## Historical backfill locally

To backfill the last 3 days locally:

```bash
python scripts/backfill_air_quality.py --days 3
python scripts/rebuild_clean.py
python scripts/validate_clean.py
python scripts/run_schema.py
python scripts/load_warehouse.py
```

## Data warehouse model

The PostgreSQL warehouse uses a star schema.

Dimension tables:

```text
dim_city
dim_time
```

Fact table:

```text
fact_air_quality
```

The fact table stores AQI and pollutant measurements. It references the city and time dimensions using foreign keys.

## Useful SQL checks

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

## Current status

The project now supports:

- current API collection;
- historical API collection;
- raw JSON storage;
- clean CSV generation;
- clean CSV validation;
- PostgreSQL warehouse loading;
- hourly automation through GitHub Actions;
- manual historical backfill through GitHub Actions.

The final submission evidence must include successful GitHub Actions runs, generated raw and clean files, and Neon SQL query results.
