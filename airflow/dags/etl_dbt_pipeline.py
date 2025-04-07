
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import csv
import psycopg2
import os

default_args = {
    'start_date': datetime(2024, 1, 1),
    'catchup': False
}

with DAG(
    dag_id='etl_dbt_pipeline',
    default_args=default_args,
    schedule_interval=None,
    description="Pipeline ETL + dbt dans Docker"
) as dag:

    def extract():
        with open("/opt/airflow/dags/data/users.csv", newline='') as f:
            reader = csv.DictReader(f)
            data = [row for row in reader]
        return data

    def transform(**kwargs):
        from datetime import datetime
        ti = kwargs['ti']
        data = ti.xcom_pull(task_ids='extract')
        transformed = []
        for row in data:
            try:
                row["name"] = row["name"].strip().upper()
                row["email"] = row["email"].strip().lower()
                row["age"] = int(row["age"])
                row["monthly_spend"] = round(float(row["monthly_spend"]), 2)
                row["is_active"] = str(row["is_active"]).strip().lower() in ["true", "1", "yes"]
                row["signup_date"] = datetime.strptime(row["signup_date"], "%Y-%m-%d").date()
                row["last_login"] = datetime.strptime(row["last_login"], "%Y-%m-%d").date()
                row["subscription_type"] = row["subscription_type"].capitalize()
                row["country"] = row["country"].strip()
                row["city"] = row["city"].strip()
                transformed.append(row)
            except Exception as e:
                print("Erreur transformation:", e)
        return transformed

    def load(**kwargs):
        ti = kwargs['ti']
        records = ti.xcom_pull(task_ids='transform')
        conn = psycopg2.connect(
            host='db',
            database='flaskdb',
            user='flaskuser',
            password='flaskpass'
        )
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users_csv (
                id SERIAL PRIMARY KEY,
                name TEXT,
                email TEXT,
                age INTEGER,
                country TEXT,
                city TEXT,
                signup_date DATE,
                last_login DATE,
                is_active BOOLEAN,
                subscription_type TEXT,
                monthly_spend NUMERIC
            );
        """)
        cur.execute("DELETE FROM users_csv")
        for row in records:
            cur.execute("""
                INSERT INTO users_csv (name, email, age, country, city, signup_date, last_login, is_active, subscription_type, monthly_spend)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row["name"], row["email"], row["age"], row["country"], row["city"],
                row["signup_date"], row["last_login"], row["is_active"], row["subscription_type"], row["monthly_spend"]
            ))
        conn.commit()
        cur.close()
        conn.close()

    extract_task = PythonOperator(task_id='extract', python_callable=extract)
    transform_task = PythonOperator(task_id='transform', python_callable=transform)
    load_task = PythonOperator(task_id='load', python_callable=load)
    run_dbt = BashOperator(
    task_id='run_dbt',
    bash_command='docker exec flask_docker_app-dbt-1 dbt run --project-dir /dbt/dbt_project --profiles-dir /root/.dbt'
    )

    dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command='docker exec flask_docker_app-dbt-1 dbt test --project-dir /dbt/dbt_project --profiles-dir /root/.dbt'
    )

    dbt_docs_generate = BashOperator(
    task_id='dbt_docs_generate',
    bash_command='docker exec flask_docker_app-dbt-1 dbt docs generate --project-dir /dbt/dbt_project --profiles-dir /root/.dbt'
    )

    dbt_docs_serve = BashOperator(
    task_id='dbt_docs_serve',
    bash_command='docker exec flask_docker_app-dbt-1 dbt docs serve --port 8082'
    )

    extract_task >> transform_task >> load_task >> run_dbt >> dbt_test >> dbt_docs_generate >> dbt_docs_serve
