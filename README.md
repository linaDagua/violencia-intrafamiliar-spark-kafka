# 🔍 Sistema de Análisis de Violencia Intrafamiliar en Colombia

Sistema de procesamiento y análisis de datos en tiempo real sobre violencia intrafamiliar utilizando Apache Spark, Kafka y Python.

## 📖 Descripción

Este proyecto implementa un pipeline completo de procesamiento de datos que combina:

- **Procesamiento por lotes (Batch)** con Apache Spark para limpieza y análisis histórico
- **Procesamiento en tiempo real (Streaming)** con Kafka y Spark Streaming para análisis continuo
- **Análisis exploratorio** de casos de violencia intrafamiliar por departamento y género

El sistema procesa datos de la Policía Nacional de Colombia sobre casos de violencia intrafamiliar, permitiendo tanto análisis históricos como monitoreo en tiempo real.

## ✨ Características

- ✅ Limpieza y transformación automática de datos
- ✅ Procesamiento batch para análisis histórico
- ✅ Streaming en tiempo real de eventos
- ✅ Agregaciones por departamento y género
- ✅ Interfaz de monitoreo con Spark UI
- ✅ Almacenamiento eficiente en formato Parquet
- ✅ Pipeline escalable y distribuido

## 🏗️ Arquitectura

```
┌─────────────────┐
│   CSV Source    │
│ (Kaggle Dataset)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Spark Batch    │◄─── Limpieza y EDA
│  Processing     │
└────────┬────────┘
         │
         ├──► violencia_clean.parquet
         └──► resultados_casos_departamento/
         
┌─────────────────┐
│ Kafka Producer  │◄─── Simula datos en tiempo real
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Kafka Topic    │
│ violencia_topic │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Spark Streaming │◄─── Análisis en tiempo real
│   Consumer      │
└─────────────────┘
```


### Librerías Python

```bash
pyspark==3.5.1
kafka-python==2.0.2
kaggle
```

## 📥 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/violencia-intrafamiliar-spark-kafka.git
cd violencia-intrafamiliar-spark-kafka
```

### 2. Configurar Kaggle API

```bash
# Instalar Kaggle CLI
pip install kaggle

# Crear directorio para credenciales
mkdir -p ~/.kaggle

# Mover archivo de credenciales (descargado de kaggle.com/account)
mv ~/Descargas/kaggle.json ~/.kaggle/

# Establecer permisos
chmod 600 ~/.kaggle/kaggle.json
```

### 3. Descargar Dataset

```bash
# Descargar dataset desde Kaggle
kaggle datasets download -d oscardavidperilla/domestic-violence-in-colombia
# Descomprimir
unzip domestic-violence-in-colombia.zip
# Renombrar archivo
mv Reporte_Delito_Violencia_Intrafamiliar_Polic_a_Nacional.csv violencia_intrafamiliar.csv
```
### 4. Instalar Dependencias Python
```bash
pip install -r requirements.txt
```

## ⚙️ Configuración

### Iniciar Servicios de Kafka

**Terminal 2: Kafka Server**
```bash
sudo /opt/Kafka/bin/kafka-server-start.sh /opt/Kafka/config/server.properties &
```

### Crear Topic de Kafka

```bash
/opt/kafka/bin/kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 1 \
  --topic violencia_topic
```

### Verificar Topic

```bash
/opt/Kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

## 🚀 Ejecución

### Paso 1: Procesamiento Batch

Ejecuta el procesamiento por lotes para limpieza inicial:

```bash
spark-submit spark_batch_violencia.py
```

### Paso 2: Iniciar Productor Kafka

En una nueva terminal, ejecuta el productor:

```bash
python3 kafka_producer_violencia.py
```

Este script enviará eventos al topic `violencia_topic` simulando llegada en tiempo real (1 registro por segundo).

### Paso 3: Iniciar Consumidor Spark Streaming

En otra terminal, ejecuta el consumidor:

```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3 spark_streaming_violencia.py
```

**Monitoreo en tiempo real:**
- Abre http://localhost:4040 en tu navegador
- Observa las pestañas: Jobs, Executors, SQL/DataFrame, Structured Streaming

### Detener la Ejecución

Para detener el streaming de forma limpia:
- Presiona `Ctrl+C` en la terminal del consumidor
- Detén el productor con `Ctrl+C`
- Detén Kafka y Zookeeper

## 📊 Resultados

### Procesamiento Batch

El procesamiento batch genera:

1. **Datos limpios** en formato Parquet para consultas eficientes
2. **Agregación por departamento** mostrando:
   - Total de casos por departamento
   - Ranking de departamentos con mayor incidencia

### Streaming en Tiempo Real

Streaming en Tiempo Real

La aplicación de Spark Structured Streaming consume datos de violencia intrafamiliar desde Kafka, mostrando analítica en vivo a medida que llegan nuevos casos.

Los indicadores que se visualizan en tiempo real son:

✅ Total de casos por departamento y Armas -medios
✅ Total de casos por genero y año

Cada micro-batch procesado por Spark actualiza la consola automáticamente.

Ejemplo de salida en consola

A continuación se muestra cómo se visualizan los resultados de los micro-batches:

Casos por Arma/Medio
Batch: 13

```bash
-------------------------------------------
+--------------------+-----------+
|ARMAS MEDIOS        |TOTAL_CASOS|
+--------------------+-----------+
|CONTUNDENTES        |        82 |
|NO REPORTADO        |         7 |
|ARMA BLANCA / COR...|         5 |
|CORTANTES           |         3 |
|NO REPORTA          |         3 |
|ARMA DE FUEGO       |         1 |
|CORTOPUNZANTES      |         1 |
+--------------------+-----------+
```

```bash
Casos por Género
Batch: 13
-------------------------------------------
+---------+-----+
|GENERO   |CASOS|
+---------+-----+
|FEMENINO |   80|
|MASCULINO|   23|
+---------+-----+
```

```bash
Evolución Temporal por Año
Batch: 13
-------------------------------------------
+----+--------------+
|ANIO|CASOS_POR_ANIO|
+----+--------------+
|2010|           104|
+----+--------------+
```

```bash
Casos por Departamento
Batch: 14
-------------------------------------------
+------------------+-----------+
|DEPARTAMENTO      |TOTAL_CASOS|
+------------------+-----------+
|VALLE             |        26 |
|SANTANDER         |         9 |
|BOYACÁ            |         9 |
|ANTIOQUIA         |         8 |
|META              |         7 |
|SUCRE             |         7 |
...
+------------------+-----------+
```

## 👨‍💻 Autor

**Lina Magali Dagua Taquinas**
- Universidad: Universidad Nacional Abierta y a Distancia
- Curso: Big Data


## 🙏 Agradecimientos

- Dataset proporcionado por Oscar David Perilla en Kaggle
- Policía Nacional de Colombia por la recopilación de datos