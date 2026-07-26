# Air Quality Pipeline Architecture

## 1. Overview

This project uses an automated batch data pipeline to collect, store, clean, validate, and load air quality data into a PostgreSQL data warehouse.

The architecture follows these principles:

- raw data is preserved;
- clean data is rebuilt from raw data;
- validation runs before warehouse loading;
- warehouse loading is idempotent;
- hourly collection and historical backfill share the same raw-to-clean-to-warehouse flow;
- GitHub Actions is the orchestrator.

## 2. Global architecture

```text
OpenWeather Air Pollution API
        ↓
GitHub Actions workflow
        ↓
Python collector scripts
        ↓
Raw JSON storage
        ↓
Clean CSV builder
        ↓
Data validation
        ↓
PostgreSQL warehouse on Neon
        ↓
SQL analysis / BI dashboard
```

## 3. Main components

## 3.1 OpenWeather Air Pollution API

The API is the external data source.

It provides air quality measurements such as:

- AQI;
- CO;
- NO;
- NO2;
- O3;
- SO2;
- PM2.5;
- PM10;
- NH3.

The project uses two API modes:

```text
Current API
→ used by the hourly GitHub Actions workflow

Historical API
→ used by the manual backfill workflow
```

## 3.2 Python source code

The main business logic is located in:

```text
src/air_quality/
```

### `cities.py`

Defines the monitored cities and their coordinates.

### `config.py`

Loads environment values required by the pipeline.

### `api_client.py`

Contains functions that call OpenWeather API:

```text
fetch_current_air_quality()
fetch_historical_air_quality()
```

### `current_collector.py`

Collects current air quality data for all monitored cities.

### `raw_storage.py`

Stores API responses as raw JSON files in:

```text
data/raw/
```

Raw files are not modified after being written.

### `clean_builder.py`

Reads all raw JSON files and rebuilds:

```text
data/clean/air_quality_clean.csv
```

The clean builder removes duplicates based on:

```text
city_name + observed_at_utc
```

### `validation.py`

Validates the clean CSV before loading it into the warehouse.

It checks:

- required columns;
- duplicate city/hour rows;
- missing AQI values;
- missing city names;
- missing observation timestamps;
- chronological sorting.

### `warehouse_loader.py`

Loads the clean CSV file into Neon PostgreSQL.

It inserts data into:

```text
dim_city
dim_time
fact_air_quality
```

It uses upsert logic to avoid duplicate records.

## 4. GitHub Actions orchestration

The orchestrator is GitHub Actions.

The workflows are stored in:

```text
.github/workflows/
```

### 4.1 Hourly workflow

File:

```text
.github/workflows/aqi_hourly_pipeline.yml
```

Purpose:

```text
Collect new air quality data every hour.
```

Task order:

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
commit data/raw and data/clean
```

### 4.2 Backfill workflow

File:

```text
.github/workflows/aqi_backfill_pipeline.yml
```

Purpose:

```text
Manually collect historical data for a selected number of past days.
```

Task order:

```text
backfill_air_quality.py
        ↓
rebuild_clean.py
        ↓
validate_clean.py
        ↓
run_schema.py
        ↓
load_warehouse.py
        ↓
commit data/raw and data/clean
```

## 5. Storage layers

## 5.1 Raw layer

Raw data is stored in:

```text
data/raw/
```

Each city has its own folder:

```text
data/raw/city=antananarivo/
data/raw/city=toamasina/
data/raw/city=mahajanga/
data/raw/city=fianarantsoa/
data/raw/city=antsiranana/
```

Raw files are JSON files.

The raw layer is important because it allows the clean dataset to be rebuilt at any time.

## 5.2 Clean layer

Clean data is stored in:

```text
data/clean/air_quality_clean.csv
```

This file contains one row per city and per observation hour.

The clean layer is rebuilt from raw files.

## 5.3 Generated data and Git

The generated data folders are ignored for normal local commits.

GitHub Actions commits generated data explicitly using:

```text
git add -f data/raw data/clean
```

This prevents accidental local commits while still preserving automated pipeline outputs.

## 6. Data warehouse

The warehouse is hosted on Neon PostgreSQL.

The schema follows a star model:

```text
            dim_city
                |
                |
        fact_air_quality
                |
                |
            dim_time
```

## 6.1 `dim_city`

Stores city information:

```text
city_id
city_name
country
latitude
longitude
```

## 6.2 `dim_time`

Stores time information:

```text
time_id
observed_at_utc
date_value
hour_value
day_value
month_value
year_value
day_of_week
is_weekend
```

## 6.3 `fact_air_quality`

Stores air quality measurements:

```text
fact_id
city_id
time_id
aqi
co
no
no2
o3
so2
pm2_5
pm10
nh3
source
ingested_at_utc
```

The fact table references `dim_city` and `dim_time` using foreign keys.

## 7. Historical backfill

The backfill workflow uses:

```text
scripts/backfill_air_quality.py
```

It collects historical air quality data from OpenWeather and writes raw JSON files.

After raw files are generated, the same pipeline flow is used:

```text
raw → clean → validation → warehouse
```

## 8. Why this architecture is reliable

This architecture is reliable because:

- raw data is preserved;
- clean data can be rebuilt from raw files;
- validation prevents bad data from entering the warehouse;
- warehouse loading uses upsert logic;
- GitHub Actions provides scheduled and manual runs;
- GitHub Actions keeps execution logs and run history;
- generated raw and clean files are committed after successful runs.

## 9. Final data flow

```text
Hourly collection:
GitHub Actions → OpenWeather Current API → raw → clean → validation → warehouse → commit generated data

Historical collection:
GitHub Actions manual backfill → OpenWeather Historical API → raw → clean → validation → warehouse → commit generated data
```
