import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

# 🔹 Vérifie l'argument
if len(sys.argv) != 2:
    print("❌ Usage: python store_to_postgres.py <base_name>")
    sys.exit(1)

table_name = sys.argv[1]
csv_path = f"/opt/data/{table_name}.csv"

if not os.path.exists(csv_path):
    print(f"❌ File not found: {csv_path}")
    sys.exit(1)

# 🔹 Connexion PostgreSQL
POSTGRES_USER = os.getenv("POSTGRES_USER", "flaskuser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "flaskpass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "flaskdb")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

db_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(db_url)

# 🔹 Création du schéma si besoin (avec transaction explicite)
with engine.begin() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS analytics"))

# 🔹 Lecture du CSV
df = pd.read_csv(csv_path)

# 🔹 Écriture dans la base de données
df.to_sql(table_name, engine, schema="analytics", if_exists="replace", index=False)

print(f"✅ Table 'analytics.{table_name}' écrite avec succès.")
print("✅ Table 'analytics.{table_name}' écrite avec succès.")
print("✅ Table 'analytics.{table_name}' écrite avec succès.")
