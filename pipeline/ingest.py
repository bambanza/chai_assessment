import requests
import pandas as pd

from .config import RAW_DIR, CITIES_CSV


def ingest():
    """
    Extract step:
    - Reads city dimension from cities.csv
    - Calls Open-Meteo API for each city (based on latitude/longitude)
    - Stores combined hourly data into data/raw/weather_raw.csv
    """
    cities_df = pd.read_csv(CITIES_CSV)

    frames = []

    for _, row in cities_df.iterrows():
        city = row["city"]
        lat = row["latitude"]
        lon = row["longitude"]

        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&hourly=temperature_2m,relative_humidity_2m,weathercode"
            "&forecast_days=2"
            "&timezone=UTC"
        )

        print(f"[INGEST] Requesting {city}: {url}")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        hourly = data["hourly"]
        df_city = pd.DataFrame(
            {
                "time": hourly["time"],
                "temperature_2m": hourly["temperature_2m"],
                "relative_humidity_2m": hourly["relative_humidity_2m"],
                "weathercode": hourly["weathercode"],
            }
        )
        df_city["city"] = city

        frames.append(df_city)

    df_all = pd.concat(frames, ignore_index=True)

    output_path = RAW_DIR / "weather_raw.csv"
    df_all.to_csv(output_path, index=False)
    print(f"[INGEST] Saved raw data → {output_path}")


def run_ingest():
    return ingest()


if __name__ == "__main__":
    ingest()
