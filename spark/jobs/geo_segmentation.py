from utils import get_spark_session, log_df_info
from pyspark.sql.functions import col, countDistinct, count

def main():
    spark = get_spark_session("GeoSegmentation")

    df = spark.read.csv("/opt/data/users.csv", header=True, inferSchema=True)
    df_clean = df.dropna(subset=["email", "country"]).dropDuplicates(["email"])

    log_df_info(df_clean, "Données géographiques nettoyées")

    geo_stats = df_clean.groupBy("country").agg(
        count("email").alias("nb_users"),
        countDistinct("subscription_type").alias("subscription_variety")
    )

    geo_stats.coalesce(1).write.mode("overwrite").parquet("/opt/data/geo_segmentation")
    log_df_info(geo_stats, "Statistiques géographiques")
        # ✅ Enregistrement aussi en CSV (pour PostgreSQL)
    geo_stats.toPandas().to_csv("/opt/data/geo_segmentation.csv", index=False)

if __name__ == "__main__":
    main()
