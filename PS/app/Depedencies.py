import asyncio
import os
from configparser import ConfigParser
from contextlib import asynccontextmanager

from faststream.kafka.fastapi import KafkaRouter

from app.model.Message import Message
from app.service.connection.ClickHouseService import ClickHouseService
from app.service.connection.RedisService import RedisService
from fastapi import FastAPI, Request

from app.service import Forecast, Adapter, Facade

configparser = ConfigParser()
base_dir = os.path.dirname(__file__)
config_path = os.path.join(base_dir, "config.ini")
configparser.read(config_path)

daily_table_name = configparser.get('clickhouse', 'table_daily')
hourly_table_name = configparser.get('clickhouse', 'table_hourly')

ch_host = configparser.get('clickhouse', 'host')
ch_port = int(configparser.get('clickhouse', 'port'))
ch_db = configparser.get('clickhouse', 'database')
ch_password = configparser.get('clickhouse', 'password')
ch_username = configparser.get('clickhouse', 'username')

clickhouse_client = ClickHouseService(host=ch_host, port=ch_port, database=ch_db, username=ch_username,
                                      password=ch_password)

adapter = Adapter(daily_table=daily_table_name, hourly_table=hourly_table_name,
                  clickhouse_service=clickhouse_client)

redis_host = configparser.get('redis', 'host')
redis_port = int(configparser.get('redis', 'port'))
redis_db = int(configparser.get('redis', 'db'))

redis_client = RedisService(redis_host, redis_port, redis_db)

redis_dtable = configparser.get('redis', 'daily_table')
redis_htable = configparser.get('redis', 'hourly_table')
facade = Facade(redis_dtable=redis_dtable, redis_htable=redis_htable,
                adapter=adapter, redis_client=redis_client)

def get_models():
    """
    Create and return instances of Forecast models for daily and hourly predictions.

    Returns:
        tuple: A tuple containing two Forecast instances:
            - First instance for daily predictions
            - Second instance for hourly predictions
    """
    return Forecast(), Forecast()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application lifecycle.

    This function handles the initialization and cleanup of application resources.
    It sets up database connections and services at startup and ensures proper
    cleanup when the application shuts down.

    Args:
        app (FastAPI): The FastAPI application instance

    Yields:
        None: Control is yielded to the application

    Note:
        This function is used as the lifespan handler for the FastAPI application.
        It ensures proper resource management throughout the application lifecycle.
    """
    app.state.clickhouse_client = clickhouse_client
    app.state.adapter = adapter
    app.state.redis_client = redis_client
    app.state.facade = facade

    yield

    await asyncio.gather(
        asyncio.to_thread(app.state.clickhouse_client.close),
        app.state.redis_client.close()
    )


def get_clickhouse_client(request: Request):
    """
    Dependency injection function for ClickHouse client.

    Args:
        request (Request): FastAPI request object

    Returns:
        ClickHouseService: ClickHouse client instance from application state
    """
    return request.app.state.clickhouse_client

def get_adapter(request: Request):
    """
    Dependency injection function for Adapter service.

    Args:
        request (Request): FastAPI request object

    Returns:
        Adapter: Adapter instance from application state
    """
    return request.app.state.adapter

def get_redis_client(request: Request):
    """
    Dependency injection function for Redis client.

    Args:
        request (Request): FastAPI request object

    Returns:
        RedisService: Redis client instance from application state
    """
    return request.app.state.redis_client

def get_facade(request: Request):
    """
    Dependency injection function for Facade service.

    Args:
        request (Request): FastAPI request object

    Returns:
        Facade: Facade instance from application state
    """
    return request.app.state.facade

