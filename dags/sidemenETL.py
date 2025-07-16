from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago


default_args = {
    'owner': 'jerome',
    'start_date': days_ago(1),
}

with DAG(
    dag_id='sidemen_etl_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    description='Sidemen YouTube ETL pipeline: fetches data and loads to MongoDB and JSONL'
) as dag:

    extract_and_load = BashOperator(
        task_id='extract_and_load',
        bash_command='python3 scripts/main.py',
    )

    extract_and_load