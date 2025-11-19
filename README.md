
# CHAI Weather Data Platform – Technical Assessment

Author: Emmanuel BAMBANZA
Role: Data Engineer, Tech Advisor CHAI, Assessment
Tech Stack: Python, Airflow, Docker, PostgreSQL, Metabase

Overview

This project implements a mini end-to-end data platform for CHAI’s technical assessment.
It ingests live weather data from the Open-Meteo API for multiple Rwandan cities, cleans
and transforms it, loads it into a PostgreSQL warehouse, and exposes a simple visualization
dashboard via Metabase.

The solution includes:

• Automated ETL Pipeline (Python + Docker)
• Airflow Orchestrated DAG (daily schedule)
• PostgreSQL Warehouse (staging + mart layers)
• Data Enrichment using local city metadata (population + area)
• Metabase Dashboard (auto-configured)
• Fully reproducible Docker Compose environment

                     ┌───────────────┐
                     │ Open-Meteo API│
                     └───────┬───────┘
                             │  Ingest
                             ▼
                   ┌─────────────────────┐
                   │  pipeline/ingest.py │
                   └─────────┬───────────┘
                             │ Clean/Enrich
                             ▼
                  ┌───────────────────────┐
                  │  pipeline/transform.py │
                  └──────────┬────────────┘
                             │ Load to DB
                             ▼
                  ┌────────────────────────┐
                  │ pipeline/model.py       │
                  │  - staging_weather      │
                  │  - mart_daily_city_*    │
                  └──────────┬─────────────┘
                             │ Orchestrate
                             ▼
                      ┌─────────────┐
                      │   Airflow   │
                      └──────┬──────┘
                             │ Query
                             ▼
                      ┌─────────────┐
                      │  Metabase   │
                      └─────────────┘


chaid_assessment/

 ├── airflow/                  # Airflow configs, logs excluded via .gitignore
 ├── airflow/dags/             # weather_etl_pipeline DAG
 ├── pipeline/
 │    ├── ingest.py            # API ingestion
 │    ├── transform.py         # cleaning + CSV output
 │    ├── model.py             # load to DB + aggregation
 │    └── run_pipeline.py      # CLI runner
 ├── db/init.sql               # PostgreSQL schema creation
 ├── data/raw/                 # raw CSV (generated)
 ├── data/processed/           # cleaned CSV (generated)
 ├── metabase-data/            # local config (ignored)
 ├── metabase-init/            # automated Metabase setup
 ├── docker-compose.yml        # full platform stack
 ├── Dockerfile                # pipeline image
 ├── Dockerfile.airflow        # Airflow custom build
 └── README.md

Running the Entire Platform

1. Clone the repository
git clone https://github.com/bambanza/chai_assessment.git
cd chai_assessment


Start the platform

docker compose up --build


This will automatically start:

Service	Description
postgres	Data warehouse
pipeline	One-off ingestion + transformation run
airflow	Webserver + scheduler
metabase	Dashboard UI
metabase-init	Automatically configures Metabase


3. Access Services
Component	URL
Airflow UI	http://localhost:8080
Metabase Dashboard	http://localhost:3000

Airflow Login:
username: admin
password: admin


Metabase is auto-initialized by metabase-init.

Features Implemented
Multi-City weather ingestion

Cities include:
  Kigali
  Musanze
  Huye

Raw → Clean → Warehouse flow

Stages:

Raw CSV: data/raw/weather_raw.csv
Clean CSV: data/processed/weather_clean.csv
Staging Table: staging_weather
Mart Table: mart_daily_city_weather

Enrichment using external CSV
data/raw/cities.csv includes:
city
population
area_km2

This is joined into the mart layer.

#Airflow DAG
DAG ID: weather_etl_pipeline
Pipeline:
ingest_weather  →  transform_weather  →  model_weather
Runs daily.
✔ Metabase Dashboard
Auto-created on startup:
Temperature & humidity tables
City-level daily aggregates
Population vs temperature insight

Notes for Reviewer

No secrets are included; all connection strings use local service names.
Logs and metabase database are excluded from Git thanks to .gitignore.

Everything is fully reproducible with a single command.
