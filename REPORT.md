# Air Quality Data Pipeline Report

## 1. Introduction

This project implements an automated data pipeline for collecting, storing, cleaning, validating, and analyzing air quality data.

The pipeline collects air pollution data from the OpenWeather Air Pollution API for multiple cities, stores the raw API responses, rebuilds a clean CSV dataset, validates the data quality, and loads the result into a PostgreSQL data warehouse.

The project is designed to support both hourly data collection and historical backfill.

## 2. Project Objective

The objective of this project is to build a reliable data pipeline that can:

- collect air quality data for at least five cities;
- run automatically on an hourly basis;
- preserve raw API responses;
- generate a clean CSV dataset;
- validate the cleaned data;
- load the data into a dimensional data warehouse;
- support analytical SQL queries.

## 3. Data Source

The data source used in this project is the OpenWeather Air Pollution API.

The API provides air quality information, including:

- AQI;
- CO;
- NO;
- NO2;
- O3;
- SO2;
- PM2.5;
- PM10;
- NH3.

The pipeline uses two API endpoints:

```text
Current air pollution endpoint
Historical air pollution endpoint
```

The current endpoint is used for hourly collection, while the historical endpoint is used for backfill.

## 4. Monitored Cities

The pipeline currently monitors five cities in Madagascar:

| City | Country |
|---|---|
| Antananarivo | MG |
| Toamasina | MG |
| Mahajanga | MG |
| Fianarantsoa | MG |
| Antsiranana | MG |

Each city is associated with a latitude and longitude used to query the OpenWeather API.

## 5. Technical Stack

The project uses the following technologies:

| Component | Technology |
|---|---|
| Programming language | Python |
| Orchestrator | Apache Airflow |
| API client | Requests |
| Data processing | Pandas |
| Environment variables | python-dotenv |
| Data warehouse | PostgreSQL |
| Cloud database | Neon |
| Storage format | JSON and CSV |
| Version control | Git |

## 6. Pipeline Architecture

The global data flow is:

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
↓
SQL analysis
```

The architecture follows a layered data approach:

```text
Raw layer
→ stores original API responses

Clean layer
→ stores validated and deduplicated CSV data

Warehouse layer
→ stores dimensional analytical tables
```

## 7. Raw Data Layer

Raw API responses are stored as JSON files in:

```text
data/raw/
```

Each monitored city has its own folder.

Example:

```text
data/raw/city=antananarivo/
```

Raw files are not modified after being written.

This makes the pipeline reliable because the clean dataset can be rebuilt from raw files at any time.

## 8. Clean Data Layer

The clean dataset is stored in:

```text
data/clean/air_quality_clean.csv
```

The clean dataset has the following grain:

```text
one row per city per observation hour
```

The logical unique key is:

```text
city_name + observed_at_utc
```

The clean builder removes duplicate rows and keeps the latest ingested record for each city and observation hour.

## 9. Data Validation

Before loading data into the warehouse, the clean CSV is validated.

The validation step checks:

- required columns;
- missing city names;
- missing observation timestamps;
- missing AQI values;
- duplicate city/hour rows;
- chronological sorting.

If validation fails, the warehouse loading step is not executed.

This prevents invalid data from entering the analytical database.

## 10. Data Warehouse Model

The warehouse uses a star schema.

The schema contains two dimension tables and one fact table:

```text
dim_city
dim_time
fact_air_quality
```

### 10.1 `dim_city`

This table stores city information:

```text
city_id
city_name
country
latitude
longitude
```

### 10.2 `dim_time`

This table stores time information:

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

### 10.3 `fact_air_quality`

This table stores air quality measurements:

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

## 11. Orchestration with Airflow

Apache Airflow is used to orchestrate the hourly pipeline.

The DAG is named:

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

The DAG is scheduled hourly:

```text
schedule="@hourly"
```

The DAG uses:

```text
catchup=False
```

This means Airflow does not automatically replay all missed historical executions. Historical data is handled separately by the backfill script.

## 12. Historical Backfill

The project includes a historical backfill script:

```text
scripts/backfill_air_quality.py
```

The backfill script collects historical air quality data and stores it in the raw layer.

It does not directly load data into the warehouse.

After a backfill, the following steps are executed:

```text
rebuild clean CSV
validate clean CSV
load warehouse
```

This keeps the same data flow for both current and historical data.

## 13. Idempotency

The warehouse loading process uses upsert logic.

This means that running the loader multiple times does not create duplicate records.

The tables use conflict rules based on:

```text
dim_city: city_name + country + latitude + longitude
dim_time: observed_at_utc
fact_air_quality: city_id + time_id
```

If a record already exists, it is reused or updated instead of being duplicated.

## 14. Analytical Queries

The warehouse supports analytical queries such as:

- total number of measurements;
- measurements by city;
- covered observation period;
- average AQI by city;
- average PM2.5 by city;
- average AQI by hour;
- weekend vs weekday AQI comparison;
- worst AQI observations.

The analysis queries are stored in:

```text
sql/analysis_queries.sql
```

## 15. Tests Performed

The project has been tested with:

- current API client test;
- historical API client test;
- current data collection;
- historical raw data collection;
- clean CSV reconstruction;
- clean CSV validation;
- warehouse schema creation;
- warehouse loading;
- Airflow DAG test execution.

A small historical backfill was tested successfully before loading the data into the warehouse.

## 16. Current Status

The pipeline currently supports:

- hourly collection with Airflow;
- raw JSON storage;
- clean CSV generation;
- clean data validation;
- warehouse loading into PostgreSQL;
- historical backfill for a selected number of days;
- SQL analysis from the warehouse.

A larger historical backfill can be executed later during the group project phase.

## 17. Conclusion

This project demonstrates a complete data engineering workflow.

It includes data ingestion, raw storage, data cleaning, validation, warehouse modeling, orchestration, and SQL analysis.

The architecture is reliable because raw data is preserved, clean data can be rebuilt, invalid data is blocked before loading, and warehouse inserts are idempotent.


