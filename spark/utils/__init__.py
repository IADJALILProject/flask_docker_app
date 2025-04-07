import os
from pyspark.sql import SparkSession, DataFrame

def get_spark_session(app_name: str = "MySparkApp") -> SparkSession:
    spark_master = os.environ.get("SPARK_MASTER_URL", "local[*]")

    spark = SparkSession.builder \
        .appName(app_name) \
        .master(spark_master) \
        .config("spark.executor.memory", "1g") \
        .config("spark.driver.memory", "1g") \
        .getOrCreate()

    return spark

def log_df_info(df: DataFrame, title: str = "DataFrame") -> None:
    print(f"\n🔍 [{title}]")
    df.printSchema()
    df.show(truncate=False)
    print(f"📈 Nombre de lignes : {df.count()}")
    print(f"📊 Nombre de colonnes : {len(df.columns)}"
          f" | Colonnes : {df.columns}")
    print(f"🔍 Aperçu des données :"
          f" {df.head(5)}")
