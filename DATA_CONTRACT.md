# Air Quality Data Contract

## 1. Purpose

This document defines the structure and rules of the clean air quality dataset.

The clean dataset is generated from raw OpenWeather API responses and is used as the input for the PostgreSQL data warehouse.

Clean file location:

```text
data/clean/air_quality_clean.csv
```

## 2. Dataset Grain

The grain of the clean dataset is:

```text
one row per city per observation hour
```

This means that for a given city and a given hour, there must be only one row.

Example:

```text
Antananarivo + 2026-07-16T06:00:00+00:00 = one row only
```

## 3. Primary Business Key

The logical unique key is:

```text
city_name + observed_at_utc
```

Duplicate rows with the same city and observation hour are not allowed in the final clean CSV.

## 4. Clean CSV Columns

| Column | Type | Required | Description |
|---|---|---|---|
| city_name | text | yes | Name of the monitored city |
| country | text | yes | Country code |
| latitude | decimal | yes | City latitude used for the API request |
| longitude | decimal | yes | City longitude used for the API request |
| observed_at_utc | timestamp | yes | Observation timestamp in UTC |
| aqi | integer | yes | Air Quality Index returned by OpenWeather |
| co | decimal | no | Carbon monoxide concentration |
| no | decimal | no | Nitrogen monoxide concentration |
| no2 | decimal | no | Nitrogen dioxide concentration |
| o3 | decimal | no | Ozone concentration |
| so2 | decimal | no | Sulphur dioxide concentration |
| pm2_5 | decimal | no | Fine particles PM2.5 concentration |
| pm10 | decimal | no | Particulate matter PM10 concentration |
| nh3 | decimal | no | Ammonia concentration |
| source | text | yes | Data source name |
| ingested_at_utc | timestamp | yes | Timestamp when the data was collected by the pipeline |

## 5. Column Order

The clean CSV must use the following column order:

```text
city_name,
country,
latitude,
longitude,
observed_at_utc,
aqi,
co,
no,
no2,
o3,
so2,
pm2_5,
pm10,
nh3,
source,
ingested_at_utc
```

## 6. Timestamp Rules

All timestamps must be stored in UTC.

### 6.1 `observed_at_utc`

This column represents the air quality observation time.

It is rounded to the hour.

Example:

```text
2026-07-16T06:00:00+00:00
```

### 6.2 `ingested_at_utc`

This column represents the time when the pipeline collected the data.

Example:

```text
2026-07-16T06:10:53.000000+00:00
```

## 7. AQI Rules

The `aqi` column is required.

Rows with missing AQI values are invalid.

The AQI value is stored as an integer.

## 8. Pollutant Rules

The pollutant columns are:

```text
co
no
no2
o3
so2
pm2_5
pm10
nh3
```

These values are stored as decimal numbers.

They represent pollutant concentration values returned by the OpenWeather Air Pollution API.

## 9. Deduplication Rule

If multiple raw files contain the same city and observation hour, the clean builder keeps the latest ingested record.

Deduplication key:

```text
city_name + observed_at_utc
```

Sorting before deduplication:

```text
observed_at_utc
city_name
ingested_at_utc
```

Final sorting:

```text
observed_at_utc
city_name
```

## 10. Validation Rules

The clean CSV must pass the following validation rules before being loaded into the warehouse:

- all required columns must exist;
- `city_name` must not be empty;
- `observed_at_ required columns must exist;
- `city_name` must not be empty;
- `observed_at_utc` must not be empty;
- `aqi` must not be empty;
- there must be no duplicate rows for the same city and observation hour;
- rows must be sorted by `observed_at_utc` and `city_name`.

## 11. Raw-to-Clean Transformation

Raw OpenWeather API responses are stored as JSON files in:

```text
data/raw/
```

The clean builder reads all raw JSON files and extracts:

- city metadata;
- observation timestamp;
- AQI;
- pollutant values;
- source;
- ingestion timestamp.

The result is written to:

```text
data/clean/air_quality_clean.csv
```

## 12. Warehouse Mapping

The clean CSV is loaded into the PostgreSQL warehouse using the following mapping.

### 12.1 City fields

The following columns are loaded into `dim_city`:

```text
city_name
country
latitude
longitude
```

### 12.2 Time fields

The following column is loaded into `dim_time`:

```text
observed_at_utc
```

Additional time attributes are derived from it:

```text
date_value
hour_value
day_value
month_value
year_value
day_of_week
is_weekend
```

### 12.3 Measurement fields

The following columns are loaded into `fact_air_quality`:

```text
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

The fact table also stores:

```text
city_id
time_id
```

These are foreign keys referencing `dim_city` and `dim_time`.

## 13. Example Row

```csv
city_name,country,latitude,longitude,observed_at_utc,aqi,co,no,no2,o3,so2,pm2_5,pm10,nh3,source,ingested_at_utc
Antananarivo,MG,-18.9137,47.5361,2026-07-16T06:00:00+00:00,1,100.49,0.03,0.12,52.65,0.24,3.65,5.46,0.68,openweather,2026-07-16T06:10:53+00:00
```

## 14. Data Quality Objective

The goal of this contract is to guarantee that the clean dataset is:

- consistent;
- deduplicated;
- chronologically sorted;
- ready for warehouse loading;
- ready for analytical queries.
