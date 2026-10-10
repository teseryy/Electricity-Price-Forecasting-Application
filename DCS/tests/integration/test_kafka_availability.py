"""
Integration tests for Kafka service availability.

This module contains tests to verify the availability and basic functionality
of the Kafka message broker service, including:
- Broker connection
- Topic configuration
- Message publishing and consumption
- Message flow validation
"""

import pytest
import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import configparser
import os
import json


def get_kafka_config():
    """
    Get Kafka configuration from config.ini file.
    
    Returns:
        dict: Dictionary containing Kafka connection parameters:
            - bootstrap_servers: Kafka broker address
            - topic: Topic name for testing
            - group_id: Consumer group ID
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
        'group_id': 'dcs-group'
    }


@pytest.mark.asyncio
async def test_kafka_connection():
    """
    Test basic Kafka broker connection.
    
    Verifies that the application can connect to the Kafka broker
    using the configuration from config.ini.
    """
    config = get_kafka_config()
    
    # Test producer connection
    try:
        print(f"Attempting to connect to Kafka at {config['bootstrap_servers']}")
        producer = AIOKafkaProducer(
            bootstrap_servers=config['bootstrap_servers'],
            client_id='dcs_test-producer'
        )
        await producer.start()
        
        # Test consumer connection
        consumer = AIOKafkaConsumer(
            config['topic'],
            bootstrap_servers=config['bootstrap_servers'],
            group_id=config['group_id'],
            auto_offset_reset='earliest',
            client_id='dcs_test-consumer'
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
    Test Kafka broker health check.
    
    Verifies that:
    - Kafka broker is accessible and responding
    - Cluster metadata can be retrieved
    - Required topic exists in the cluster
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
    Test Kafka message publishing and consumption flow.
    
    Verifies that messages can be:
    - Published to the configured topic
    - Consumed from the topic
    - Properly processed by the consumer
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