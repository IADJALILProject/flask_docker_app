from utils import get_spark_session, log_df_info
from pyspark.sql.functions import col, avg, count, sum as spark_sum

def run_subscription_summary(input_path: str, output_path: str):
    """
    Analyse le revenu moyen par type d'abonnement à partir d'un fichier CSV.
    Args:
        input_path (str): Chemin du fichier CSV source.
        output_path (str): Répertoire où stocker le fichier Parquet de sortie.
    """
    spark = get_spark_session("SubscriptionAnalytics")

    # Lecture du fichier CSV
    df = spark.read.option("header", True).option("inferSchema", True).csv(input_path)
    log_df_info(df, "Données brutes (CSV)")

    # Nettoyage de base
    df_clean = df.dropna(subset=["email", "age", "monthly_spend"]).dropDuplicates(["email"])

    # Analyse du revenu par type d'abonnement
    avg_spend_by_type = df_clean.groupBy("subscription_type").agg(
        count("email").alias("nb_users"),
        spark_sum("monthly_spend").alias("total_revenue"),
        avg("monthly_spend").alias("avg_spend")
    )

    # Export Parquet (un seul fichier pour compatibilité DBT ou autre outil BI)
    avg_spend_by_type.coalesce(1).write.mode("overwrite").parquet(output_path)

    # Affichage console pour debug
    log_df_info(avg_spend_by_type, "Résumé des abonnements")

    # ✅ Enregistrement aussi en CSV (pour PostgreSQL)
    avg_spend_by_type.toPandas().to_csv("/opt/data/analytics_summary.csv", index=False)

def main():
    input_path = "/opt/data/users.csv"
    output_path = "/opt/data/summary_subscription"
    run_subscription_summary(input_path, output_path)

if __name__ == "__main__":
    main()
