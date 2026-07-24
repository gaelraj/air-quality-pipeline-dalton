# Air Quality Pipeline Submission Checklist

## 1. Purpose

This checklist maps the project requirements to the current implementation.

It helps verify what is already implemented, what has been tested locally, and what still needs to be completed during the group phase.

## 2. Requirement Coverage

| Requirement | Status | Project File / Evidence |
|---|---|---|
| Air quality API | Done | OpenWeather Air Pollution API |
| At least 5 cities | Done | `src/air_quality/cities.py` |
| Hourly collection | Done locally | `dags/air_quality_hourly_dag.py` |
| Orchestrator | Done locally | Apache Airflow |
| Raw storage | Done | `data/raw/` |
| One raw file per city and API call | Done | `src/air_quality/raw_storage.py` |
| Clean CSV file | Done | `data/clean/air_quality_clean.csv` |
| Clean CSV rebuilt from raw | Done | `src/air_quality/clean_builder.py` |
| Data validation | Done | `src/air_quality/validation.py` |
| PostgreSQL warehouse | Done locally with Neon | `sql/001_create_warehouse_schema.sql` |
| Star schema | Done | `dim_city`, `dim_time`, `fact_air_quality` |
| Warehouse loading | Done | `src/air_quality/warehouse_loader.py` |
| SQL analysis queries | Done | `sql/analysis_queries.sql` |
| Historical backfill support | Done locally | `scripts/backfill_air_quality.py` |
| 24/7 deployment | Planned | `DEPLOYMENT_PLAN.md` |
| Documentation | Done | `README.md`, `ARCHITECTURE.md`, `DATA_CONTRACT.md`, `RUNBOOK.md` |
| Final report | Drafted | `REPORT.md` |
| Execution evidence | To complete after deployment | Airflow screenshots, Neon SQL results |
| Video/demo | To complete later | Final group submission |

## 3. Implemented Components

### 3.1 Source Code

```text
src/air_quality/
```

Contains the main business logic:

- API client;
- city configuration;
- environment configuration;
- raw data storage;
- clean CSV builder;
- data validation;
- warehouse loader.

### 3.2 Scripts

```text
scripts/
```

Contains manual execution scripts:

- API tests;
- current collection;
- historical backfill;
- clean rebuild;
- validation;
- warehouse schema creation;
- warehouse loading.

### 3.3 Airflow DAG

```text
dags/air_quality_hourly_dag.py
```

Orchestrates the hourly pipeline:

```text
collect_raw_data
↓
rebuild_clean_data
↓
validate_clean_data
↓
load_data_warehouse
```

### 3.4 SQL

```text
sql/
```

Contains:

- warehouse schema creation;
- analytical SQL queries.

## 4. Local Tests Completed

The following tests have been completed locally:

- current API client test;
- historical API client test;
- current raw data collection;
- historical raw data collection for a small period;
- clean CSV rebuild;
- clean CSV validation;
- warehouse schema creation;
- warehouse loading into Neon;
- Airflow DAG test execution.

## 5. Current Limitations

The pipeline has not yet been deployed on an always-on server.

The current execution is local.

This means that the hourly Airflow pipeline runs only when the local Airflow scheduler is running.

## 6. Remaining Work for Group Phase

The following tasks remain for the group phase:

- choose the final deployment environment;
- deploy the project on an always-on server;
- configure production environment variables;
- run Airflow continuously;
- execute the final historical backfill period;
- collect execution evidence;
- capture Airflow screenshots;
- capture Neon SQL result screenshots;
- prepare the final video/demo;
- finalize the report with real deployment results.

## 7. Final Submission Reminder

Before the final submission, verify that:

- `.env` is not committed;
- `requirements.txt` is present;
- documentation files are complete;
- the Airflow DAG runs successfully;
- raw files are generated;
- clean CSV is generated;
- validation passes;
- warehouse tables contain data;
- SQL analysis queries work;
- deployment proof is available;
- video/demo is ready.


