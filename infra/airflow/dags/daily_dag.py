from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from kafka import KafkaProducer
import json

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

tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)


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


def send_night_message():
    try:
        producer = get_kafka_producer()
        today = datetime.now().strftime('%Y-%m-%d')
        message = {
            "mode": "night",
            "date": today
        }

        future = producer.send(KAFKA_TOPIC, message)
        record_metadata = future.get(timeout=10)

        producer.flush()
        producer.close()

        print(f"Sent night message: {message}")
        print(f"Message sent to partition {record_metadata.partition} at offset {record_metadata.offset}")

        return f"Successfully sent night message for {today}"
    except Exception as e:
        print(f"Error sending Kafka message: {e}")
        raise


with DAG(
        'kafka_nightly',
        default_args=default_args,
        description='DAG to send nightly messages to Kafka',
        schedule_interval='5 0 * * *',
        start_date=tomorrow,
        catchup=False,
        tags=['kafka', 'night'],
) as dag:
    night_task = PythonOperator(
        task_id='send_night_message',
        python_callable=send_night_message,
    )