import pytest
import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import configparser
import os
import json


def get_kafka_config():
    """
    Read Kafka configuration from config.ini.

    This function reads the Kafka configuration settings from the config.ini file,
    including bootstrap servers, topic name, and group ID.

    Returns:
        dict: Dictionary containing Kafka configuration:
            - bootstrap_servers: Kafka server address
            - topic: Kafka topic name
            - group_id: Consumer group ID

    Raises:
        FileNotFoundError: If config.ini file is not found
        KeyError: If Kafka section is missing in config.ini
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found")
        
    config = configparser.ConfigParser()
    config.read(config_path)
    
    if 'kafka' not in config:
        raise KeyError("Kafka configuration section not found in config.ini")
    
    return {
        'bootstrap_servers': config['kafka']['bootstrap_servers'],
        'topic': config['kafka']['topic'],
        'group_id': 'ps-group'
    }


@pytest.mark.asyncio
async def test_kafka_connection():
    """
    Test Kafka connection and basic operations.

    This integration test verifies:
    1. Ability to establish connection to Kafka broker
    2. Producer can connect and send messages
    3. Consumer can connect and receive messages
    4. Basic message production and consumption works

    The test:
    - Creates a producer and consumer
    - Sends a test message
    - Verifies the message can be received
    - Cleans up connections

    Raises:
        pytest.fail: If any connection or operation fails
    """
    config = get_kafka_config()
    
    try:
        print(f"Attempting to connect to Kafka at {config['bootstrap_servers']}")
        producer = AIOKafkaProducer(
            bootstrap_servers=config['bootstrap_servers'],
            client_id='ps_test-producer'
        )
        await producer.start()
        
        # Test consumer connection
        consumer = AIOKafkaConsumer(
            config['topic'],
            bootstrap_servers=config['bootstrap_servers'],
            group_id=config['group_id'],
            auto_offset_reset='earliest',
            client_id='ps_test-consumer'
        )
        await consumer.start()
        
        # Test message production
        test_message = b'test message'
        await producer.send_and_wait(config['topic'], test_message)
        
        # Test message consumption
        async for message in consumer:
            if message.value == test_message:
                break
        
        # Cleanup
        await producer.stop()
        await consumer.stop()
        
    except Exception as e:
        pytest.fail(f"Failed to connect to Kafka at {config['bootstrap_servers']}: {str(e)}")


@pytest.mark.asyncio
async def test_kafka_health():
    """
    Test Kafka health check.

    This integration test verifies:
    1. Kafka cluster is accessible
    2. Cluster metadata can be retrieved
    3. Required topic exists in the cluster

    The test:
    - Creates a producer connection
    - Fetches cluster metadata
    - Verifies the required topic exists
    - Cleans up connection

    Raises:
        pytest.fail: If health check fails
        AssertionError: If metadata is missing or topic not found
    """
    config = get_kafka_config()
    
    try:
        # Create producer to test connection
        producer = AIOKafkaProducer(
            bootstrap_servers=config['bootstrap_servers']
        )
        await producer.start()
        
        # Get cluster metadata to verify connection
        metadata = await producer.client.fetch_all_metadata()
        assert metadata is not None, "Failed to fetch Kafka metadata"
        
        # Check if our topic exists
        topics = metadata.topics()
        assert config['topic'] in topics, f"Topic {config['topic']} not found in Kafka"
        
        await producer.stop()
        
    except Exception as e:
        pytest.fail(f"Kafka health check failed: {str(e)}")


@pytest.mark.asyncio
async def test_kafka_message_flow():
    """
    Test complete message flow through Kafka.

    This integration test verifies the end-to-end message flow:
    1. Producer can send messages
    2. Messages are properly delivered to the topic
    3. Consumer can receive messages
    4. Message content is preserved

    The test:
    - Creates both producer and consumer
    - Sends a test message
    - Verifies the message is received with correct content
    - Cleans up connections

    Raises:
        pytest.fail: If message flow test fails
    """
    config = get_kafka_config()
    
    try:
        # Create producer and consumer
        producer = AIOKafkaProducer(
            bootstrap_servers=config['bootstrap_servers']
        )
        consumer = AIOKafkaConsumer(
            config['topic'],
            bootstrap_servers=config['bootstrap_servers'],
            group_id=config['group_id'],
            auto_offset_reset='earliest'
        )
        
        await producer.start()
        await consumer.start()
        
        # Send test message
        test_message = b'test message flow'
        await producer.send_and_wait(config['topic'], test_message)
        
        # Set timeout for message consumption
        async for message in consumer:
            if message.value == test_message:
                break
        
        # Cleanup
        await producer.stop()
        await consumer.stop()
        
    except Exception as e:
        pytest.fail(f"Kafka message flow test failed: {str(e)}") 