from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from pipeline.ingest import run_ingest
from pipeline.transform import run_transform
from pipeline.model import run_model

default_args = {
    "owner": "chai",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="weather_etl_pipeline",
    description="Weather ETL: ingest (API) → transform → load to Postgres",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["chai", "assessment", "weather"],
) as dag:

    ingest_task = PythonOperator(
        task_id="ingest_weather",
        python_callable=run_ingest,
    )

    transform_task = PythonOperator(
        task_id="transform_weather",
        python_callable=run_transform,
    )

    model_task = PythonOperator(
        task_id="model_weather",
        python_callable=run_model,
    )

ingest_task >> transform_task >> model_task
