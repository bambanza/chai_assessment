import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

DB_URI = os.getenv(
    "DB_URI",
    "postgresql+psycopg2://chai:chai123@postgres:5432/chaidb",
)

# City dimension CSV: used for API coordinates + enrichment
CITIES_CSV = DATA_DIR / "cities.csv"
