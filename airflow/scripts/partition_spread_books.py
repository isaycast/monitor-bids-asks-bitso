from pyspark.sql import SparkSession
from pyspark.sql.functions import col,date_format
from datetime import datetime, timedelta


spark = SparkSession.builder \
    .appName("Process Spread Books") \
    .config("spark.jars.packages", "org.postgresql:postgresql:42.6.0") \
    .getOrCreate()




url = "jdbc:postgresql://postgres:5432/airflow"

properties = {
    "user": "airflow",
    "password": "1234",
    "driver": "org.postgresql.Driver"
}

now = datetime.now()
ten_minutes_ago = now - timedelta(minutes=10)

query = f"""
(SELECT * FROM spread_books 
WHERE TO_TIMESTAMP(orderbook_timestamp, 'YYYY-MM-DD"T"HH24:MI:SS') BETWEEN '{ten_minutes_ago}' AND '{now}') as spread_books
"""

df = spark.read.jdbc(url=url, table=query, properties=properties)

df.show(20)


current_time_str = now.strftime("%Y%m%d%H%M%S")
ten_minutes_ago_str = ten_minutes_ago.strftime("%Y%m%d%H%M%S")


df.write \
    .csv(f"/opt/airflow/s3_datalake/spread_book_{current_time_str}_{ten_minutes_ago_str}.csv")

df_filtered = df.withColumn("year", date_format(col("orderbook_timestamp"), "yyyy")) \
                         .withColumn("month", date_format(col("orderbook_timestamp"), "MM")) \
                         .withColumn("day", date_format(col("orderbook_timestamp"), "dd")) \
                         .withColumn("hour", date_format(col("orderbook_timestamp"), "HH")) \
                         .withColumn("minute", date_format(col("orderbook_timestamp"), "mm"))

df_filtered.write \
    .partitionBy("year", "month", "day", "hour", "minute") \
    .mode('append') \
    .format("csv") \
    .save("/opt/airflow/s3_datalake/spread_books_partitioned")

spark.stop()
