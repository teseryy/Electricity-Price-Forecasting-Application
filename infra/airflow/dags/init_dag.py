from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from kafka import KafkaProducer
import json
import os
from airflow.utils.trigger_rule import TriggerRule

KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
KAFKA_TOPIC = 'ltopic'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
}


def get_kafka_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=5,
            retry_backoff_ms=500
        )
        return producer
    except Exception as e:
        print(f"Error creating Kafka producer: {e}")
        raise


def send_init_message():
    marker_file = '/opt/airflow/init_completed'
    if os.path.exists(marker_file):
        print("Initialization already completed, skipping")
        return "Initialization already completed"

    try:
        producer = get_kafka_producer()
        today = datetime.now().strftime('%Y-%m-%d')
        message = {
            "mode": "init",
            "date": today
        }

        future = producer.send(KAFKA_TOPIC, message)
        record_metadata = future.get(timeout=10)

        producer.flush()
        producer.close()

        print(f"Sent init message: {message}")
        print(f"Message sent to partition {record_metadata.partition} at offset {record_metadata.offset}")

        with open(marker_file, 'w') as f:
            f.write(datetime.now().isoformat())

        return f"Successfully sent init message for {today}"
    except Exception as e:
        print(f"Error sending Kafka message: {e}")
        raise


with DAG(
        'kafka_init',
        default_args=default_args,
        description='DAG to send initialization message to Kafka',
        schedule_interval='@once',
        start_date=datetime(2000, 1, 1),
        catchup=False,
        tags=['kafka', 'init'],
) as dag:
    init_task = PythonOperator(
        task_id='send_init_message',
        python_callable=send_init_message,
    )