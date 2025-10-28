from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, count, year, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType

spark = SparkSession.builder \
    .appName("StreamingViolenciaIntrafamiliar") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Esquema del JSON recibido desde Kafka
schema = StructType([
    StructField("DEPARTAMENTO", StringType()),
    StructField("MUNICIPIO", StringType()),
    StructField("CODIGO DANE", StringType()),
    StructField("ARMAS MEDIOS", StringType()),
    StructField("FECHA HECHO", StringType()),  # fecha string dd/MM/yyyy
    StructField("GENERO", StringType()),
    StructField("GRUPO ETARIO", StringType()),
    StructField("CANTIDAD", StringType())
])

# Leer datos desde Kafka en tiempo real
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "violencia_topic") \
    .load()

# Extraer JSON y columnas
json_df = df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# Convertir fecha dd/MM/yyyy a timestamp
json_df = json_df.withColumn("FECHA_TS", to_timestamp(col("FECHA HECHO"), "d/M/yyyy"))

###############################################
# 1 Total por Departamento
casos_departamento = json_df.groupBy("DEPARTAMENTO") \
    .agg(count("*").alias("TOTAL_CASOS")) \
    .orderBy(col("TOTAL_CASOS").desc())

query_departamento = casos_departamento.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("numRows", 50) \
    .start()

###############################################
# 2 Casos por Género
casos_genero = json_df.groupBy("GENERO") \
    .agg(count("*").alias("CASOS")) \
    .orderBy(col("CASOS").desc())

query_genero = casos_genero.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

###############################################
# 3 Clasificación por Arma/Medio
casos_armas = json_df.groupBy("ARMAS MEDIOS") \
    .agg(count("*").alias("TOTAL_CASOS")) \
    .orderBy(col("TOTAL_CASOS").desc())

query_armas = casos_armas.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

###############################################
# 4 Evolución temporal por Año
evolucion_anual = json_df.withColumn("ANIO", year(col("FECHA_TS"))) \
    .groupBy("ANIO") \
    .agg(count("*").alias("CASOS_POR_ANIO")) \
    .orderBy("ANIO")

query_anual = evolucion_anual.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

###############################################
# Mantener streaming activo
spark.streams.awaitAnyTermination()