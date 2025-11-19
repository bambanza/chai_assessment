
# CHAI Weather Data Platform – Technical Assessment

Author: Emmanuel BAMBANZARole: Data Engineer, Tech Advisor CHAI, AssessmentTech
Stack: Python, Airflow, Docker, PostgreSQL, Metabase

ἰ Overview

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
