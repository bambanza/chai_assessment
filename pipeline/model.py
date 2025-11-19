import time
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from .config import PROCESSED_DIR, DB_URI


def wait_for_db(retries: int = 10, delay: int = 3):
    """
    Wait until Postgres is ready, then return a SQLAlchemy engine.
    This is useful when running inside docker-compose.
    """
    for i in range(retries):
        try:
            engine = create_engine(DB_URI)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("[MODEL] Database is ready.")
            return engine
        except OperationalError as e:
            print(f"[MODEL] DB not ready yet ({e}), retry {i+1}/{retries}...")
            time.sleep(delay)
    raise RuntimeError("Database not available after retries")


def run_model():
    """
    Load step:
    - Reads data/processed/weather_clean.csv
    - Inserts all rows into staging_weather
    - Aggregates daily stats into mart_daily_city_weather
    """
    input_path = PROCESSED_DIR / "weather_clean.csv"
    df = pd.read_csv(input_path, parse_dates=["observed_at"])

    required_cols = {"city", "temperature_c", "humidity", "condition", "observed_at"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"[MODEL] Missing cols in weather_clean.csv: {missing}")

    engine = wait_for_db()

    records = df.to_dict(orient="records")

    # Ensure humidity None instead of NaN
    for r in records:
        if "humidity" in r and pd.isna(r["humidity"]):
            r["humidity"] = None

    insert_staging_sql = text("""
        INSERT INTO staging_weather (
            city,
            temperature_c,
            humidity,
            condition,
            observed_at,
            population,
            area_km2
        )
        VALUES (
            :city,
            :temperature_c,
            :humidity,
            :condition,
            :observed_at,
            :population,
            :area_km2
        );
    """)


    with engine.begin() as conn:
        conn.execute(insert_staging_sql, records)

    print(f"[MODEL] Inserted {len(records)} rows into staging_weather")

    agg_sql = text("""
        TRUNCATE mart_daily_city_weather;
        INSERT INTO mart_daily_city_weather (
            city,
            date,
            avg_temperature_c,
            avg_humidity,
            dominant_condition,
            population,
            area_km2
        )
        SELECT
            city,
            date_trunc('day', observed_at)::date AS date,
            AVG(temperature_c) AS avg_temperature_c,
            AVG(humidity::float) AS avg_humidity,
            MIN(condition) AS dominant_condition,
            MAX(population) AS population,      -- or MIN(population)
            MAX(area_km2) AS area_km2           -- area is constant
        FROM staging_weather
        GROUP BY city, date_trunc('day', observed_at)::date;
    """)


    with engine.begin() as conn:
        conn.execute(agg_sql)

    print("[MODEL] Aggregated into mart_daily_city_weather")


if __name__ == "__main__":
    run_model()