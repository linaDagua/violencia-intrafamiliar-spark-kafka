from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, count
from pyspark.sql.types import StructType, StructField, StringType

spark = SparkSession.builder \
    .appName("StreamingViolenciaIntrafamiliar") \
    .getOrCreate()

# Esquema para leer mensajes del topic
schema = StructType([
    StructField("DEPARTAMENTO", StringType()),
    StructField("MUNICIPIO", StringType()),
    StructField("CODIGO DANE", StringType()),
    StructField("ARMAS MEDIOS", StringType()),
    StructField("FECHA HECHO", StringType()),
    StructField("GENERO", StringType()),
    StructField("GRUPO ETARIO", StringType()),
    StructField("CANTIDAD", StringType())
])

# Leer datos desde Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "violencia_topic") \
    .load()

# Convertir JSON
json_df = df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# Conteo por género en tiempo real
conteo_genero = json_df.groupBy("GENERO").agg(count("*").alias("CASOS"))

query = conteo_genero.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

query.awaitTermination()
