CREATE TABLE IF NOT EXISTS dim_city (
    city_id BIGSERIAL PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    country VARCHAR(10) NOT NULL,
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,

    CONSTRAINT uq_dim_city_name_country
        UNIQUE (city_name, country)
);


CREATE TABLE IF NOT EXISTS dim_time (
    time_id BIGSERIAL PRIMARY KEY,
    observed_at_utc TIMESTAMPTZ NOT NULL,
    date_value DATE NOT NULL,
    hour_value SMALLINT NOT NULL,
    day_value SMALLINT NOT NULL,
    month_value SMALLINT NOT NULL,
    year_value SMALLINT NOT NULL,
    day_of_week SMALLINT NOT NULL,
    is_weekend BOOLEAN NOT NULL,

    CONSTRAINT uq_dim_time_observed_at
        UNIQUE (observed_at_utc),

    CONSTRAINT chk_dim_time_hour
        CHECK (hour_value BETWEEN 0 AND 23),

    CONSTRAINT chk_dim_time_day
        CHECK (day_value BETWEEN 1 AND 31),

    CONSTRAINT chk_dim_time_month
        CHECK (month_value BETWEEN 1 AND 12),

    CONSTRAINT chk_dim_time_day_of_week
        CHECK (day_of_week BETWEEN 0 AND 6)
);


CREATE TABLE IF NOT EXISTS fact_air_quality (
    fact_id BIGSERIAL PRIMARY KEY,
    city_id BIGINT NOT NULL,
    time_id BIGINT NOT NULL,
    aqi INTEGER NOT NULL,
    co DOUBLE PRECISION,
    no DOUBLE PRECISION,
    no2 DOUBLE PRECISION,
    o3 DOUBLE PRECISION,
    so2 DOUBLE PRECISION,
    pm2_5 DOUBLE PRECISION,
    pm10 DOUBLE PRECISION,
    nh3 DOUBLE PRECISION,
    source VARCHAR(50) NOT NULL,
    ingested_at_utc TIMESTAMPTZ NOT NULL,

    CONSTRAINT fk_fact_air_quality_city
        FOREIGN KEY (city_id)
        REFERENCES dim_city (city_id),

    CONSTRAINT fk_fact_air_quality_time
        FOREIGN KEY (time_id)
        REFERENCES dim_time (time_id),

    CONSTRAINT uq_fact_air_quality_city_time
        UNIQUE (city_id, time_id)
);


CREATE INDEX IF NOT EXISTS idx_fact_air_quality_city_id
    ON fact_air_quality (city_id);


CREATE INDEX IF NOT EXISTS idx_fact_air_quality_time_id
    ON fact_air_quality (time_id);
