# Air Quality Pipeline Runbook

## 1. Purpose

This runbook explains how to run and verify the air quality data pipeline.

It covers:

- local execution;
- hourly GitHub Actions execution;
- historical backfill execution;
- warehouse verification;
- troubleshooting.

## 2. Local setup

Go to the project root directory:

```bash
cd air-quality-pipeline
```

Create a Python virtual environment if needed:

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Export the Python path:

```bash
export PYTHONPATH="$PWD/src:$PYTHONPATH"
```

## 3. Local environment file

For local execution only, create a `.env` file from the example file:

```bash
cp .env.example .env
```

Fill it with the local values used by the scripts.

The `.env` file must not be committed.

## 4. Test the current API client locally

```bash
python scripts/test_api_client.py
```

Expected result:

```text
City: Antananarivo
AQI: ...
Components: {...}
```

## 5. Test the historical API client locally

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

## 6. Run the local manual pipeline

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

## 7. Run a local historical backfill

Example for the last 3 days:

```bash
python scripts/backfill_air_quality.py --days 3
python scripts/rebuild_clean.py
python scripts/validate_clean.py
python scripts/run_schema.py
python scripts/load_warehouse.py
```

The backfill writes historical raw JSON files first, then rebuilds clean data and loads the warehouse.

## 8. GitHub Actions hourly pipeline

The hourly workflow file is:

```text
.github/workflows/aqi_hourly_pipeline.yml
```

It runs automatically every hour.

It can also be launched manually from the GitHub Actions tab.

Expected workflow order:

```text
Collect current raw data
↓
Rebuild clean CSV
↓
Validate clean CSV
↓
Create warehouse schema
↓
Load warehouse
↓
Commit generated raw and clean data
```

## 9. GitHub Actions backfill pipeline

The backfill workflow file is:

```text
.github/workflows/aqi_backfill_pipeline.yml
```

It is launched manually from the GitHub Actions tab.

The workflow asks for:

```text
Number of past days to backfill
```

Example value:

```text
7
```

Expected workflow order:

```text
Backfill historical raw data
↓
Rebuild clean CSV
↓
Validate clean CSV
↓
Create warehouse schema
↓
Load warehouse
↓
Commit generated raw and clean data
```

## 10. Verify generated repository data

After a successful GitHub Actions run, check that new files were committed under:

```text
data/raw/
data/clean/air_quality_clean.csv
```

Useful local checks after pulling latest `main`:

```bash
find data/raw -name "*.json" | wc -l
wc -l data/clean/air_quality_clean.csv
```

## 11. Verify warehouse data in Neon

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

## 12. Troubleshooting

### 12.1 OpenWeather timeout

Rerun the failed workflow or wait for the next hourly run.

The API client already includes retry logic.

### 12.2 No raw or clean files after a workflow run

Check that the workflow reached the final commit step.

The workflow must execute:

```text
git add -f data/raw data/clean
```

### 12.3 Warehouse tables are missing

Check that the `Create warehouse schema` step succeeded.

This step runs:

```bash
python scripts/run_schema.py
```

### 12.4 Warehouse has no data

Check that the `Load warehouse` step succeeded.

This step runs:

```bash
python scripts/load_warehouse.py
```

### 12.5 Validation fails

Inspect the clean CSV file:

```text
data/clean/air_quality_clean.csv
```

The warehouse loading step must not be trusted until validation passes.

## 13. Final evidence for submission

Collect the following evidence:

- successful hourly workflow run history;
- successful manual backfill run;
- committed raw JSON files;
- committed clean CSV file;
- Neon SQL query screenshots;
- dashboard screenshots if a BI tool is used.
