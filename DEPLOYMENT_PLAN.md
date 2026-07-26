# Air Quality Pipeline Deployment Plan

## 1. Purpose

This document describes the deployment strategy for the air quality data pipeline.

The project is deployed through GitHub Actions. No local machine or dedicated server is required for the scheduled pipeline.

## 2. Deployment objective

The deployment objective is to run the pipeline automatically every hour.

The deployed system must:

- execute the hourly workflow;
- collect new air quality data;
- store raw API responses;
- rebuild the clean CSV file;
- validate the clean dataset;
- load validated data into Neon PostgreSQL;
- commit generated raw and clean files to the repository;
- keep execution logs and run history.

## 3. Target deployment architecture

```text
GitHub Actions schedule
        ↓
Python pipeline scripts
        ↓
OpenWeather API
        ↓
Raw JSON storage in repository
        ↓
Clean CSV file in repository
        ↓
Neon PostgreSQL warehouse
        ↓
SQL analysis / dashboard
```

## 4. Deployment components

The deployment uses:

- GitHub repository;
- GitHub Actions workflows;
- Python;
- OpenWeather API client;
- raw and clean data folders;
- Neon PostgreSQL;
- SQL warehouse schema;
- warehouse loader.

## 5. Workflows

## 5.1 Hourly workflow

File:

```text
.github/workflows/aqi_hourly_pipeline.yml
```

Trigger:

```text
Every hour
Manual run
```

Purpose:

```text
Collect current air quality data and load it into Neon.
```

## 5.2 Backfill workflow

File:

```text
.github/workflows/aqi_backfill_pipeline.yml
```

Trigger:

```text
Manual run only
```

Purpose:

```text
Collect historical air quality data for a selected number of past days.
```

## 6. Hourly pipeline steps

```text
Checkout repository
↓
Install Python dependencies
↓
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

## 7. Backfill pipeline steps

```text
Checkout repository
↓
Install Python dependencies
↓
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

## 8. Data persistence strategy

Raw and clean files are generated during workflow execution.

The repository ignores these folders for normal local commits:

```text
data/raw/
data/clean/
```

However, GitHub Actions explicitly commits generated outputs with:

```text
git add -f data/raw data/clean
```

This keeps local development clean while preserving pipeline outputs after automated runs.

## 9. Historical backfill strategy

Historical backfill is executed manually with the backfill workflow.

The workflow input is:

```text
days
```

Example:

```text
90
```

Recommended approach:

- first test with a small value such as `3` or `7`;
- verify raw files, clean CSV, validation, and Neon loading;
- then run the larger required backfill period.

## 10. Monitoring plan

The deployed pipeline must be monitored through:

- GitHub Actions run status;
- workflow logs;
- generated raw files;
- clean CSV validation result;
- Neon row counts;
- SQL analysis queries.

Useful repository checks:

```bash
find data/raw -name "*.json" | wc -l
wc -l data/clean/air_quality_clean.csv
```

Useful warehouse check:

```sql
SELECT COUNT(*) AS total_measurements
FROM fact_air_quality;
```

## 11. Failure handling

If an API request fails:

- the API client retries the request;
- the workflow fails if all attempts fail;
- the failed run can be inspected in GitHub Actions logs;
- the next scheduled run can collect new data again.

If validation fails:

- the warehouse loading step must not be trusted;
- inspect the clean CSV and raw files;
- fix the transformation or data issue;
- rerun the workflow.

If warehouse loading fails:

- check the `Create warehouse schema` step;
- check the `Load warehouse` step;
- inspect the Python error in GitHub Actions logs.

## 12. Production readiness checklist

Before final submission, verify that:

- the hourly workflow runs successfully;
- the manual backfill workflow runs successfully;
- generated raw files are committed;
- the clean CSV is committed;
- validation passes;
- Neon tables exist;
- Neon tables contain data;
- SQL analysis queries return results;
- workflow run history contains enough evidence;
- dashboard screenshots are available if required.
