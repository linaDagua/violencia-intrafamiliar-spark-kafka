from kafka import KafkaProducer
import csv
import json
import time

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic_name = "violencia_topic"
csv_file = "violencia_intrafamiliar.csv"

with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        producer.send(topic_name, row)
        print(f"Enviado: {row}")
        time.sleep(1)  # simula llegada en tiempo real

producer.flush()
producer.close()
