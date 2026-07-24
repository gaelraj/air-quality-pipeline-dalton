# Air Quality Pipeline Architecture

## 1. Overview

This project uses a batch-oriented data pipeline to collect, store, clean, validate, and load air quality data into a PostgreSQL data warehouse.

The pipeline is designed around the following principles:

- raw data must be preserved without modification;
- clean data must be rebuilt from raw data;
- data must be validated before warehouse loading;
- the warehouse must support analytical queries;
- the hourly pipeline and the historical backfill must share the same data flow.

## 2. Global Architecture

```text
OpenWeather Air Pollution API
        ↓
Python Collector
        ↓
Raw JSON Storage
        ↓
Clean CSV Builder
        ↓
Data Validation
        ↓
PostgreSQL Data Warehouse
        ↓
SQL Analysis
```

## 3. Main Components

### 3.1 OpenWeather Air Pollution API

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
→ used by the hourly Airflow pipeline

Historical API
→ used by the manual backfill script
```

## 4. Python Source Code

The main business logic is located in:

```text
src/air_quality/
```

### 4.1 `cities.py`

Defines the monitored cities and their coordinates.

### 4.2 `config.py`

Loads environment variables from the `.env` file.

It provides:

```text
OPENWEATHER_API_KEY
DATABASE_URL
```

### 4.3 `api_client.py`

Contains functions that call OpenWeather API.

It supports:

```text
fetch_current_air_quality()
fetch_historical_air_quality()
```

### 4.4 `current_collector.py`

Collects current air quality data for all monitored cities.

It is used by the Airflow hourly DAG.

### 4.5 `raw_storage.py`

Stores API responses as raw JSON files.

Raw files are saved in:

```text
data/raw/
```

The raw layer is immutable. Files are not modified after being written.

### 4.6 `clean_builder.py`

Reads all raw JSON files and rebuilds the clean CSV dataset.

The clean file is saved as:

```text
data/clean/air_quality_clean.csv
```

The clean builder also removes duplicates based on:

```text
city_name + observed_at_utc
```

### 4.7 `validation.py`

Validates the clean CSV file before loading it into the warehouse.

It checks:

- required columns;
- duplicate city/hour rows;
- missing AQI values;
- missing city names;
- missing observation timestamps;
- chronological sorting.

### 4.8 `warehouse_loader.py`

Loads the clean CSV file into the PostgreSQL data warehouse.

It inserts data into:

```text
dim_city
dim_time
fact_air_quality
```

It uses upsert logic to avoid duplicate records.

## 5. Storage Layers

## 5.1 Raw Layer

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

Example:

```text
history_20260715T060000Z_20260716T060000Z_collected_20260716T061053Z.json
```

The raw layer is important because it allows the clean dataset to be rebuilt at any time.

## 5.2 Clean Layer

Clean data is stored in:

```text
data/clean/air_quality_clean.csv
```

This file contains one row per city and per observation hour.

The clean layer is rebuilt from raw files.

## 6. Data Warehouse

The warehouse is hosted on PostgreSQL using Neon.

The schema follows a star model.

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

Stores city information.

Example columns:

```text
city_id
city_name
country
latitude
longitude
```

A city is inserted only once.

## 6.2 `dim_time`

Stores time information.

Example columns:

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

This dimension allows time-based analysis.

## 6.3 `fact_air_quality`

Stores air quality measurements.

Example columns:

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

## 7. Airflow Orchestration

The Airflow DAG is located in:

```text
dags/air_quality_hourly_dag.py
```

The DAG runs every hour.

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

### 7.1 `collect_raw_data`

Collects current air quality data from OpenWeather and stores raw JSON files.

### 7.2 `rebuild_clean_data`

Rebuilds the clean CSV file from all raw files.

### 7.3 `validate_clean_data`

Validates the clean CSV file.

If validation fails, the warehouse loading task is not executed.

### 7.4 `load_data_warehouse`

Loads the validated clean data into PostgreSQL.

## 8. Historical Backfill

The historical backfill script is located in:

```text
scripts/backfill_air_quality.py
```

It collects past data from the OpenWeather historical API.

The backfill only writes raw JSON files.

After running a backfill, the following steps must be executed:

```text
rebuild clean CSV
validate clean CSV
load warehouse
```

This keeps the same architecture for both current and historical data.

## 9. Why This Architecture Is Reliable

This architecture is reliable because:

- raw data is preserved;
- clean data can be rebuilt from raw files;
- validation prevents bad data from entering the warehouse;
- warehouse loading is idempotent;
- Airflow controls task order;
- historical and hourly data follow the same pipeline structure.

## 10. Final Data Flow

```text
Hourly collection:
Airflow → OpenWeather Current API → raw → clean → validation → warehouse

Historical collection:
Backfill script → OpenWeather Historical API → raw → clean → validation → warehouse
```

## 11. Current Status

The architecture has been tested with:

- current data collection;
- small historical backfill;
- clean CSV reconstruction;
- data validation;
- PostgreSQL warehouse loading;
- Airflow DAG execution.

A larger historical backfill can be executed later during the group phase.


