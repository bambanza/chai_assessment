CREATE TABLE IF NOT EXISTS staging_weather (
    id SERIAL PRIMARY KEY,
    city VARCHAR(50),
    temperature_c FLOAT,
    humidity INT,
    condition VARCHAR(50),
    observed_at TIMESTAMP,
    population INT,
    area_km2 FLOAT
);

CREATE TABLE IF NOT EXISTS mart_daily_city_weather (
    id SERIAL PRIMARY KEY,
    city VARCHAR(50),
    date DATE,
    avg_temperature_c FLOAT,
    avg_humidity FLOAT,
    dominant_condition VARCHAR(50),
    population INT,
    area_km2 FLOAT
);

CREATE TABLE IF NOT EXISTS mart_city_weather_summary (
    id SERIAL PRIMARY KEY,
    city VARCHAR(50),
    total_days_recorded INT,
    highest_temperature_c FLOAT,
    lowest_temperature_c FLOAT,
    average_humidity FLOAT
);