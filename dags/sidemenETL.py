from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'owner': 'jerome',
    'start_date': datetime(2025, 8, 6, 0, 0),  # any date before today, NOT a Sunday
}

with DAG(
    dag_id='sidemen_etl_pipeline',
    default_args=default_args,
    schedule_interval='29 18 * * 0',  # every Sunday at 18:29 UTC = 11:59 PM IST
    catchup=False,
    description='Sidemen YouTube ETL pipeline: fetches new videos weekly at 11:59 PM IST'
) as dag:

    extract_and_load = BashOperator(
        task_id='extract_and_load',
        bash_command='python3 /opt/airflow/scripts/main.py',
    )

    extract_and_load
