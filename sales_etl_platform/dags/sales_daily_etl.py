from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from scripts.ingest import ingest_files

default_args = {
    "owner": "Yamir Palacios",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="sales_daily_etl",
    default_args=default_args,
    schedule=None,  # manual trigger for assessment
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["snowflake", "dbt", "sales"],
) as dag:

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    ingest_task = PythonOperator(
        task_id="ingest_raw_files",
        python_callable=ingest_files,
    )

    # ------------------------------------------------------------------
    # Silver Layer
    # ------------------------------------------------------------------

    dbt_run_silver = BashOperator(
        task_id="dbt_run_silver",
        bash_command="""
        cd /opt/airflow/dbt &&
        dbt run --select silver
        """,
    )

    # ------------------------------------------------------------------
    # Data Quality Tests
    # ------------------------------------------------------------------

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="""
        cd /opt/airflow/dbt &&
        dbt test
        """,
    )

    # ------------------------------------------------------------------
    # Gold Layer
    # ------------------------------------------------------------------

    dbt_run_gold = BashOperator(
        task_id="dbt_run_gold",
        bash_command="""
        cd /opt/airflow/dbt &&
        dbt run --select gold
        """,
    )

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------

    (
        ingest_task
        >> dbt_run_silver
        >> dbt_test
        >> dbt_run_gold
    )