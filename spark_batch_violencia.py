from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, to_date

spark = SparkSession.builder \
    .appName("BatchViolenciaIntrafamiliar") \
    .getOrCreate()

# Cargar el CSV
df = spark.read.csv("violencia_intrafamiliar.csv", header=True, inferSchema=True)

# Limpiar fecha
df = df.withColumn("FECHA", to_date(col("FECHA HECHO"), "d/M/yyyy"))

# Eliminar filas sin fecha válida
df_clean = df.filter(col("FECHA").isNotNull())

# EDA básico: casos por departamento
casos_departamento = df_clean.groupBy("DEPARTAMENTO").agg(count("*").alias("CASOS"))

# Mostrar resultados mínimos útiles
df_clean.show(5)
casos_departamento.show()

# Guardar resultados procesados
df_clean.write.mode("overwrite").parquet("violencia_clean.parquet")
casos_departamento.write.mode("overwrite").csv("resultados_casos_departamento")

print("Procesamiento batch completo OK")
spark.stop()
