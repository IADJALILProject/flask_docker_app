from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="etl_spark_pipeline",
    description="ETL Spark pipeline using PySpark container",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["spark", "etl", "pyspark"]
) as dag:

    spark_analytics = BashOperator(
        task_id="spark_analytics_summary",
        bash_command="docker exec spark_app python jobs/analytics_summary.py"
    )

    store_analytics = BashOperator(
        task_id="store_analytics_summary",
        bash_command="docker exec spark_app python jobs/store_to_postgres.py analytics_summary"
    )

    spark_churn = BashOperator(
        task_id="spark_churn_analysis",
        bash_command="docker exec spark_app python jobs/churn_analysis.py"
    )

    store_churn = BashOperator(
        task_id="store_churn_analysis",
        bash_command="docker exec spark_app python jobs/store_to_postgres.py churn_analysis"
    )

    spark_geo = BashOperator(
        task_id="spark_geo_segmentation",
        bash_command="docker exec spark_app python jobs/geo_segmentation.py"
    )

    store_geo = BashOperator(
        task_id="store_geo_segmentation",
        bash_command="docker exec spark_app python jobs/store_to_postgres.py geo_segmentation"
    )

    # Orchestration complète
    spark_analytics >> store_analytics >> spark_churn >> store_churn >> spark_geo >> store_geo
