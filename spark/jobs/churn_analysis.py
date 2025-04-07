from utils import get_spark_session, log_df_info
from pyspark.sql.functions import col, datediff, current_date
from pyspark.sql.types import FloatType
from pyspark.sql.functions import to_date

def main():
    # 📦 Initialisation de la session Spark
    spark = get_spark_session("UserChurnAnalysis")

    # 📄 Lecture du fichier CSV
    df = spark.read.csv("/opt/data/users.csv", header=True, inferSchema=True)

    # 🧹 Nettoyage des données : suppression des lignes avec valeurs nulles
    df_clean = df.dropna(subset=["email", "last_login"]).dropDuplicates(["email"])

    # ✅ Convertir last_login en date si ce n’est pas déjà le cas
    df_clean = df_clean.withColumn("last_login", to_date(col("last_login")))

    log_df_info(df_clean, "Données pour churn analysis")

    # ⏱️ Calcul du nombre de jours d'inactivité
    df_churn = df_clean.withColumn("days_since_last_login", datediff(current_date(), col("last_login")))

    # 📊 Agrégation par type d’abonnement
    churn_stats = df_churn.groupBy("subscription_type").agg(
        {"days_since_last_login": "avg"}
    ).withColumnRenamed("avg(days_since_last_login)", "avg_days_inactive")

    # ✅ Cast pour compatibilité avec Pandas
    churn_stats = churn_stats.withColumn("avg_days_inactive", col("avg_days_inactive").cast(FloatType()))

    # 🔍 Logging
    log_df_info(churn_stats, "Churn statistics par abonnement")

    # 💾 Sauvegarde
    churn_stats.coalesce(1).write.mode("overwrite").parquet("/opt/data/churn_stats")
    churn_stats.toPandas().to_csv("/opt/data/churn_analysis.csv", index=False)

    print("✅ churn_analysis.csv exporté avec succès.")

if __name__ == "__main__":
    main()


