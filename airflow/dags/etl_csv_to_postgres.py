from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os, csv, psycopg2

# Arguments par défaut du DAG
default_args = {
    'start_date': datetime(2025, 4, 1),
    'owner': 'airflow',
}

with DAG(
    dag_id='etl_csv_to_postgres',
    schedule_interval=None,  # Exécution manuelle
    catchup=False,
    default_args=default_args,
    description="ETL depuis CSV vers Postgres dans la table users_csv",
    tags=["etl", "csv", "postgres"],
) as dag:

    def extract_func(**kwargs):
        """Lecture du fichier CSV et renvoi des données brutes."""
        # Construit le chemin vers le CSV (assure-toi qu'il se trouve dans airflow/dags/data/)
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'users.csv')
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Fichier CSV introuvable : {csv_path}")
        data = []
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
        print(f">>> ✅ {len(data)} lignes extraites depuis CSV")
        return data

    def transform_func(**kwargs):
        """Nettoyage et transformation des données extraites."""
        ti = kwargs['ti']
        raw_data = ti.xcom_pull(task_ids='extract')
        if not raw_data:
            return []
        transformed_data = []
        for row in raw_data:
            try:
                row["name"] = row["name"].strip().upper()
                row["email"] = row["email"].strip().lower()
                row["age"] = int(row["age"])
                row["monthly_spend"] = round(float(row["monthly_spend"]), 2)

                row["country"] = row["country"].strip()
                row["city"] = row["city"].strip()

                row["is_active"] = str(row["is_active"]).strip().lower() in ["true", "1", "yes"]

                # Conversion des dates (assure-toi que le format dans le CSV est YYYY-MM-DD)
                row["signup_date"] = datetime.strptime(row["signup_date"], "%Y-%m-%d").date()
                row["last_login"] = datetime.strptime(row["last_login"], "%Y-%m-%d").date()

                row["subscription_type"] = row["subscription_type"].capitalize()

                transformed_data.append(row)
            except Exception as e:
                print(f"❌ Erreur de transformation pour la ligne: {row} | Erreur: {e}")
        print(f">>> ✅ {len(transformed_data)} lignes prêtes après transformation")
        return transformed_data

    def load_func(**kwargs):
        """Insertion des données transformées dans la table users_csv de PostgreSQL."""
        ti = kwargs['ti']
        records = ti.xcom_pull(task_ids='transform')
        if not records:
            print("Aucun enregistrement à charger.")
            return "No records loaded"
        # Connexion à PostgreSQL
        conn = psycopg2.connect(
            host='db',
            database='flaskdb',
            user='flaskuser',
            password='flaskpass'
        )
        cur = conn.cursor()

        # Création de la table users_csv
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
        conn.commit()

        # Pour les tests : vider la table avant insertion
        cur.execute("DELETE FROM users_csv;")
        conn.commit()

        # Préparation de la requête d'insertion
        columns = list(records[0].keys())
        col_names = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        insert_query = f"INSERT INTO users_csv ({col_names}) VALUES ({placeholders})"

        for row in records:
            values = tuple(row[col] for col in columns)
            cur.execute(insert_query, values)

        conn.commit()
        cur.close()
        conn.close()
        inserted_count = len(records)
        print(f">>> ✅ {inserted_count} lignes insérées dans la table users_csv")
        return f"{inserted_count} records inserted"

    extract_task = PythonOperator(
        task_id='extract',
        python_callable=extract_func
    )

    transform_task = PythonOperator(
        task_id='transform',
        python_callable=transform_func
    )

    load_task = PythonOperator(
        task_id='load',
        python_callable=load_func
    )

    extract_task >> transform_task >> load_task
