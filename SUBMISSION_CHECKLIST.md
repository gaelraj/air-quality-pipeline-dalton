# Air Quality Pipeline Submission Checklist

## 1. Purpose

This checklist maps the project requirements to the current implementation.

It helps verify what is already implemented, what has been tested, and what evidence must be collected before final submission.

## 2. Requirement coverage

| Requirement | Status | Project file / evidence |
|---|---|---|
| Air quality API | Done | OpenWeather Air Pollution API |
| At least 5 cities | Done | `src/air_quality/cities.py` |
| Hourly collection | Done | `.github/workflows/aqi_hourly_pipeline.yml` |
| Orchestrator | Done | GitHub Actions |
| Raw storage | Done | `data/raw/` |
| One raw file per city and API call | Done | `src/air_quality/raw_storage.py` |
| Clean CSV file | Done after pipeline run | `data/clean/air_quality_clean.csv` |
| Clean CSV rebuilt from raw | Done | `src/air_quality/clean_builder.py` |
| Data validation | Done | `src/air_quality/validation.py` |
| PostgreSQL warehouse | Done | Neon PostgreSQL |
| Star schema | Done | `dim_city`, `dim_time`, `fact_air_quality` |
| Warehouse schema | Done | `sql/001_create_warehouse_schema.sql` |
| Warehouse loading | Done | `src/air_quality/warehouse_loader.py` |
| Historical backfill support | Done | `.github/workflows/aqi_backfill_pipeline.yml` |
| Documentation | Done | `README.md`, `ARCHITECTURE.md`, `DATA_CONTRACT.md`, `RUNBOOK.md` |
| Final report | Drafted | `REPORT.md` |
| Execution evidence | To collect | GitHub Actions screenshots, Neon SQL results |
| Video/demo | To complete later | Final group submission |

## 3. Implemented components

### 3.1 Source code

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

### 3.3 GitHub Actions workflows

```text
.github/workflows/aqi_hourly_pipeline.yml
.github/workflows/aqi_backfill_pipeline.yml
```

The hourly workflow orchestrates:

```text
collect current raw data
↓
rebuild clean CSV
↓
validate clean CSV
↓
create warehouse schema
↓
load warehouse
↓
commit generated raw and clean data
```

The backfill workflow orchestrates:

```text
backfill historical raw data
↓
rebuild clean CSV
↓
validate clean CSV
↓
create warehouse schema
↓
load warehouse
↓
commit generated raw and clean data
```

### 3.4 SQL

```text
sql/
```

Contains the warehouse schema creation script.

## 4. Checks to complete

Before final submission, verify:

- the hourly workflow runs successfully;
- the manual backfill workflow runs successfully;
- generated raw files are committed;
- the clean CSV is committed;
- validation passes;
- Neon tables are created;
- Neon tables contain rows;
- SQL analysis queries return results.

## 5. Useful verification commands

After pulling the latest `main`:

```bash
find data/raw -name "*.json" | wc -l
wc -l data/clean/air_quality_clean.csv
```

Warehouse checks:

```sql
SELECT COUNT(*) AS total_measurements
FROM fact_air_quality;
```

```sql
SELECT
    c.city_name,
    COUNT(*) AS measurement_count
FROM fact_air_quality f
JOIN dim_city c ON c.city_id = f.city_id
GROUP BY c.city_name
ORDER BY c.city_name;
```

```sql
SELECT
    MIN(t.observed_at_utc) AS first_observation,
    MAX(t.observed_at_utc) AS last_observation
FROM fact_air_quality f
JOIN dim_time t ON t.time_id = f.time_id;
```

## 6. Evidence to collect

Collect screenshots or proof of:

- successful GitHub Actions hourly runs;
- successful GitHub Actions backfill run;
- generated raw JSON files in the repository;
- generated clean CSV in the repository;
- Neon table list;
- Neon row counts;
- SQL query results;
- dashboard visualizations if used.

## 7. Final submission reminder

Before the final submission, verify that:

- `.env` is not committed;
- `requirements.txt` is present;
- documentation files are consistent with GitHub Actions;
- the hourly workflow runs successfully;
- the backfill workflow runs successfully;
- raw files are generated;
- clean CSV is generated;
- validation passes;
- warehouse tables contain data;
- SQL analysis queries work;
- execution proof is available;
- video/demo is ready.
