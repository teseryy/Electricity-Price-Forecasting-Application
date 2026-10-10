import os
from configparser import ConfigParser
from pathlib import Path

from faststream.kafka.fastapi import KafkaRouter


from app.model.Message import Message
from app.Depedencies import facade, get_models


configparser = ConfigParser()
base_dir = Path(__file__).resolve().parent.parent.parent
config_path = os.path.join(base_dir, "config.ini")
configparser.read(config_path)
kafka_host = configparser.get('kafka', 'host')
kafka_port = configparser.get('kafka', 'port')
kafka_topic = configparser.get('kafka', 'listen_topic')

kafka_router = KafkaRouter(f"{kafka_host}:{kafka_port}")

@kafka_router.subscriber(kafka_topic)
async def process_message(data: dict):
    """
    Process incoming Kafka messages and trigger forecast generation.

    This function is a Kafka subscriber that processes incoming messages
    containing forecast generation requests.

    Args:
        data (dict): Incoming message data containing:
            - date: str, The date for which to train the models (format: YYYY-MM-DD)
            - Other fields as defined in the Message model

    Note:
        This function is automatically triggered when a message is received
        on the configured Kafka topic.
    """
    mes = Message(**data)

    m1, m2 = get_models()

    await facade.train(mes.date, m1, m2)

