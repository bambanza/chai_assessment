CHAI Weather ETL – README

This project implements a simple end-to-end weather ETL pipeline for the CHAI Data Engineer Technical Assessment.
It uses Docker, Airflow, PostgreSQL, and Metabase to demonstrate ingestion, transformation, loading, and visualization.

1. How to Run the Pipeline End-to-End
---
Step 1 — Start everything
--------------------------
docker compose up --build
This will automatically:

Start PostgreSQL and create all tables via db/init.sql.
Run the Python ETL pipeline once (ingest → transform → model).
Start Airflow with the DAG weather_etl_pipeline.
Start Metabase for visualization.

Step 2 — Trigger the scheduled ETL
----
Open Airflow UI: http://localhost:8080
User: admin
Password: admin
Turn on the DAG: weather_etl_pipeline
Click Trigger DAG to run a full cycle.

2. Dependencies and Setup
-------------------------------
No manual installation required — everything runs in Docker.

You only need:
Docker
Docker Compose
Git

Services started:

Service	Purpose	URL/Port
Postgres	Data warehouse	localhost:5433
Airflow	Orchestration	http://localhost:8080
Metabase : http://localhost:3000
Pipeline Standalone ETL runner which runs once at startup

Database credentials (inside Docker):
----
DB: chaidb
User: chai
Pass: chai123
Host: postgres

3. Data Sources Used
---------------------
Weather API (Open-Meteo)
The pipeline fetches live hourly weather for:
    Kigali
    Huye
    Musanze

Example endpoint:

https://api.open-meteo.com/v1/forecast?latitude=<lat>&longitude=<lon>&hourly=temperature_2m,relative_humidity_2m,weathercode&timezone=UTC

City Metadata (CSV) (data/cities.csv) provides: coordinates, population and area_km2 used to enrich the final analytic mart.

4. How to Validate Data Movement Through Each Stage
---------------------------------------------------
1 — Extract (Raw) Check raw file generated:  data/raw/weather_raw.csv

2 — Transform (Processed) data/processed/weather_clean.csv

3 — Load (Database) Connect to Postgres: psql -h localhost -p 5433 -U chai -d chaidb

    Check staging: SELECT COUNT(*) FROM staging_weather;
    Check mart: SELECT * FROM mart_daily_city_weather ORDER BY date DESC;

4 — Airflow Orchestration

In the Airflow UI, confirm all tasks:

ingest_weather
transform_weather
model_weather
turn green and logs show processing steps.

5 — Visualization in Metabase
---------------------------
Open Metabase:
http://localhost:3000
Verify tables appear under chaidb
Explore mart_daily_city_weather
Dashboard updates after each DAG run
