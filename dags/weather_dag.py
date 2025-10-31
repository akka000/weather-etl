from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "retries": 1,
    "retry_delay": timedelta(minutes=2)
}

with DAG(
    dag_id="weather_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="*/10 * * * *",
    catchup=False,
) as dag:

    fetch_weather = BashOperator(
        task_id="fetch_weather",
        bash_command="python /opt/airflow/etl/fetch_weather.py"
    )
