# Air Quality Pipeline Deployment Plan

## 1. Purpose

This document describes the planned deployment strategy for the air quality data pipeline.

The pipeline has currently been tested locally. The production deployment will be completed later during the group project phase.

## 2. Current Status

The current implementation supports:

- OpenWeather API collection;
- raw JSON storage;
- clean CSV generation;
- data validation;
- PostgreSQL warehouse loading;
- local Airflow orchestration;
- small historical backfill tests.

The current pipeline is not yet deployed on an always-on server.

## 3. Deployment Objective

The deployment objective is to run the pipeline automatically 24 hours a day.

The deployed system must:

- execute the Airflow DAG every hour;
- keep collecting new air quality data;
- store raw API responses;
- rebuild the clean CSV file;
- validate the clean dataset;
- load validated data into PostgreSQL;
- keep the warehouse available for analysis.

## 4. Target Deployment Architecture

```text
Cloud or VPS server
        ↓
Airflow scheduler
        ↓
Airflow DAG
        ↓
OpenWeather API
        ↓
Raw JSON storage
        ↓
Clean CSV file
        ↓
Neon PostgreSQL warehouse
```

## 5. Required Deployment Components

The deployment environment must include:

- Python;
- project source code;
- virtual environment;
- project dependencies;
- Airflow;
- `.env` file with real secrets;
- access to the Neon PostgreSQL database;
- persistent storage for raw and clean data;
- a running Airflow scheduler.

## 6. Environment Variables

The deployed environment must provide the following variables:

```env
OPENWEATHER_API_KEY=your_openweather_api_key
DATABASE_URL=your_postgresql_connection_string
OPENWEATHER_CURRENT_URL=https://api.openweathermap.org/data/2.5/air_pollution
OPENWEATHER_HISTORY_URL=https://api.openweathermap.org/data/2.5/air_pollution/history
```

The `.env` file must not be committed to Git.

## 7. Deployment Steps

### 7.1 Clone the repository

```bash
git clone <repository-url>
cd air-quality-pipeline
```

### 7.2 Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 7.3 Install dependencies

```bash
pip install -r requirements.txt
```

### 7.4 Create the environment file

```bash
cp .env.example .env
```

Then fill in the real values.

### 7.5 Export Python path

```bash
export PYTHONPATH="$PWD/src:$PYTHONPATH"
```

### 7.6 Create the warehouse schema

```bash
python scripts/run_schema.py
```

### 7.7 Test the manual pipeline

```bash
python scripts/collect_current.py
python scripts/rebuild_clean.py
python scripts/validate_clean.py
python scripts/load_warehouse.py
```

### 7.8 Configure Airflow

The Airflow DAG file is located in:

```text
dags/air_quality_hourly_dag.py
```

Airflow must be configured to detect this DAG.

If needed, create a symbolic link:

```bash
mkdir -p ~/airflow/dags
ln -sf "$PWD/dags/air_quality_hourly_dag.py" ~/airflow/dags/air_quality_hourly_dag.py
```

### 7.9 Check DAG import

```bash
airflow dags list-import-errors --local
```

Expected result:

```text
No data found
```

### 7.10 Start Airflow

```bash
airflow standalone
```

The DAG must be unpaused in the Airflow UI.

## 8. Scheduling

The DAG is scheduled hourly:

```text
schedule="@hourly"
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

## 9. Historical Backfill Strategy

Historical backfill will be executed manually before or during deployment.

Example:

```bash
python scripts/backfill_air_quality.py --days 90
```

After the backfill:

```bash
python scripts/rebuild_clean.py
python scripts/validate_clean.py
python scripts/load_warehouse.py
```

The backfill must be tested with a small number of days before running a larger period.

## 10. Monitoring Plan

The deployed pipeline must be monitored through:

- Airflow DAG status;
- Airflow task logs;
- raw file generation;
- clean CSV validation result;
- warehouse row counts;
- SQL analysis queries.

Useful checks:

```bash
find data/raw -name "*.json" | wc -l
wc -l data/clean/air_quality_clean.csv
```

Warehouse check:

```sql
SELECT COUNT(*) AS total_measurements
FROM fact_air_quality;
```

## 11. Failure Handling

If an API timeout happens:

- the API client retry logic attempts the request again;
- Airflow can retry failed tasks;
- failed runs can be inspected in Airflow logs.

If validation fails:

- the warehouse loading task must not run;
- the clean CSV must be inspected;
- raw files can be used to rebuild the clean dataset.

If warehouse loading fails:

- check `DATABASE_URL`;
- check Neon availability;
- rerun `scripts/load_warehouse.py` after fixing the issue.

## 12. Security Notes

The following files must not be committed:

```text
.env
```

Secrets must be stored only in the deployment environment.

The repository should only contain:

```text
.env.example
```

## 13. Production Readiness Checklist

Before final deployment, verify that:

- the repository is clean and pushed;
- `.env` exists on the server;
- dependencies are installed;
- Airflow detects the DAG;
- the DAG runs successfully;
- the DAG is unpaused;
- raw files are generated;
- the clean CSV is rebuilt;
- validation passes;
- the warehouse receives data;
- SQL analysis queries return results.

## 14. Final Note

This document is a deployment plan.

It does not claim that the pipeline is already deployed.

The actual 24/7 deployment will be completed later during the group project phase.


