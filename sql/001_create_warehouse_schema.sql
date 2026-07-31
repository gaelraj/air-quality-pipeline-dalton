-- =========================================================
-- City dimension table
-- Stores descriptive information about each monitored city.
-- No air quality measurements should be stored here.
-- =========================================================
CREATE TABLE IF NOT EXISTS dim_city (
    city_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city_name TEXT NOT NULL,
    country TEXT NOT NULL,
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,

    CONSTRAINT uq_dim_city UNIQUE (city_name, country, latitude, longitude)
);

-- =========================================================
-- Time dimension table
-- Stores descriptive time attributes for each observation hour.
-- This allows analytical queries by date, hour, month, weekday, or weekend.
-- =========================================================
CREATE TABLE IF NOT EXISTS dim_time (
    time_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    observed_at_utc TIMESTAMPTZ NOT NULL,
    date_value DATE NOT NULL,
    hour_value INTEGER NOT NULL,
    day_value INTEGER NOT NULL,
    month_value INTEGER NOT NULL,
    year_value INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL,

    CONSTRAINT uq_dim_time UNIQUE (observed_at_utc)
);

-- =========================================================
-- Air quality fact table
-- Stores AQI and pollutant measurements.
-- It only contains measures and foreign keys to dimensions.
-- =========================================================
CREATE TABLE IF NOT EXISTS fact_air_quality (
    fact_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    city_id BIGINT NOT NULL REFERENCES dim_city(city_id),
    time_id BIGINT NOT NULL REFERENCES dim_time(time_id),

    aqi INTEGER NOT NULL,
    co NUMERIC,
    no NUMERIC,
    no2 NUMERIC,
    o3 NUMERIC,
    so2 NUMERIC,
    pm2_5 NUMERIC,
    pm10 NUMERIC,
    nh3 NUMERIC,

    source TEXT NOT NULL,
    ingested_at_utc TIMESTAMPTZ NOT NULL,

    CONSTRAINT uq_fact_air_quality UNIQUE (city_id, time_id)
);

-- =========================================================
-- Index on city foreign key
-- Speeds up analytical queries filtered or grouped by city.
-- =========================================================
CREATE INDEX IF NOT EXISTS idx_fact_air_quality_city_id
ON fact_air_quality(city_id);

-- =========================================================
-- Index on time foreign key
-- Speeds up analytical queries filtered or grouped by time.
-- =========================================================
CREATE INDEX IF NOT EXISTS idx_fact_air_quality_time_id
ON fact_air_quality(time_id);
