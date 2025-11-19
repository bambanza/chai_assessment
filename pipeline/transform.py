import pandas as pd

from .config import RAW_DIR, PROCESSED_DIR, CITIES_CSV

WEATHER_CODE_MAP = {
    0: "Clear",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    61: "Slight rain",
    63: "Rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Snow",
    75: "Heavy snow",
    80: "Rain showers",
    95: "Thunderstorm",
}


def transform():
    """
    Transform step:
    - Reads weather_raw.csv (multi-city)
    - Parses timestamps, renames columns, maps weathercode → condition
    - JOINs with cities.csv (population + area_km2)
    - Writes weather_clean.csv
    """
    input_path = RAW_DIR / "weather_raw.csv"
    output_path = PROCESSED_DIR / "weather_clean.csv"

    df = pd.read_csv(input_path)

    # Basic cleaning / reshaping
    df["observed_at"] = pd.to_datetime(df["time"])
    df["temperature_c"] = df["temperature_2m"]
    df["humidity"] = df["relative_humidity_2m"].round().astype("Int64")
    df["condition"] = df["weathercode"].map(WEATHER_CODE_MAP).fillna("Unknown")

    df_out = df[["city", "temperature_c", "humidity", "condition", "observed_at"]].copy()
    df_out = df_out.dropna(subset=["temperature_c"])

    # --- Enrich with city dimension (CSV) ---
    dim_city = pd.read_csv(CITIES_CSV)[["city", "population", "area_km2"]]
    df_out = df_out.merge(dim_city, on="city", how="left")

    df_out.to_csv(output_path, index=False)
    print(f"[TRANSFORM] Saved cleaned data → {output_path}")


def run_transform():
    return transform()


if __name__ == "__main__":
    transform()
