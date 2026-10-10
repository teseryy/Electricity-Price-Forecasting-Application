"""
Dependencies module.

This module contains the Dependencies class for managing application dependencies,
as well as helper functions for Kafka and ClickHouse operations.
"""

import os
from configparser import ConfigParser

from faststream.kafka import KafkaBroker

from app.service import Adapter, ClimateStandardService, PriceService, TemperatureService, KafkaService
from app.service.connection.ClickHouseService import ClickHouseService


class Dependencies:
    """
    Dependency injection container for application services.
    
    This class manages the initialization and configuration of all application services.
    
    Attributes:
        clickhouse_service (ClickHouseService): Service for ClickHouse database operations
        kafka_service (KafkaService): Service for Kafka message processing
    """
    
    def __init__(self):
        """
        Initialize Dependencies container.
        
        Reads configuration from config.ini and initializes all required services:
        - ClickHouse service with database connection parameters
        - Kafka service with broker configuration
        - Adapter with all required services for data processing
        """
        configparser = ConfigParser()
        base_dir = os.path.dirname(__file__)
        config_path = os.path.join(base_dir, "config.ini")
        configparser.read(config_path)

        db_host = configparser.get('clickhouse', 'host')
        db_user = configparser.get('clickhouse', 'username')
        db_password = configparser.get('clickhouse', 'password')
        db_name = configparser.get('clickhouse', 'db')
        db_port = configparser.get('clickhouse', 'port')
        db_table_daily = configparser.get('clickhouse', 'table_daily')
        db_table_hourly = configparser.get('clickhouse', 'table_hourly')

        kafka_host = configparser.get('kafka', 'host')
        kafka_port = configparser.get('kafka', 'port')
        kafka_listen_topic = configparser.get('kafka', 'listen_topic')
        kafka_publish_topic = configparser.get('kafka', 'publish_topic')

        a = Adapter(climate_standard=ClimateStandardService(), prices=PriceService(),
                    temperature=TemperatureService())

        self.clickhouse_service = ClickHouseService(host=db_host, port=int(db_port), database=db_name,
                                       username=db_user, password=db_password)

        broker = KafkaBroker(f"{kafka_host}:{kafka_port}")

        self.kafka_service = KafkaService(adapter=a, broker=broker, clickhouse_service=self.clickhouse_service,
                                          daily_table=db_table_daily, hourly_table=db_table_hourly,
                                          listen_topic=kafka_listen_topic, confirm_topic=kafka_publish_topic)


dependencies = Dependencies()

def get_broker():
    """
    Get Kafka broker instance.
    
    Returns:
        KafkaBroker: Configured Kafka broker instance
    """
    return dependencies.kafka_service.broker

def shutdown_clickhouse():
    """
    Shutdown ClickHouse connection.
    
    This function is called during application shutdown to properly close
    the ClickHouse database connection.
    """
    dependencies.clickhouse_service.close()