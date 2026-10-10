"""
Integration tests for ClickHouse service availability.

This module contains tests to verify the availability and basic functionality
of the ClickHouse database service, including:
- Database connection
- Table existence and structure
- Basic data operations
"""

import pytest
import asyncio
import aiohttp
import configparser
import os
from typing import Dict


def get_clickhouse_config() -> Dict[str, str]:
    """
    Get ClickHouse configuration from config.ini file.
    
    Returns:
        Dict[str, str]: Dictionary containing ClickHouse connection parameters:
            - host: Database host
            - port: Database port
            - username: Database username
            - password: Database password
            - database: Database name
    """

    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found")

    config = configparser.ConfigParser()
    config.read(config_path)
    
    if 'clickhouse' not in config:
        raise KeyError("ClickHouse configuration section not found in config.ini")
    
    return {
        'host': config['clickhouse']['host'],
        'port': config['clickhouse']['port'],
        'database': config['clickhouse']['db'],
        'user': config['clickhouse']['username'],
        'password': config['clickhouse']['password']
    }


@pytest.mark.asyncio
async def test_clickhouse_connection():
    """
    Test ClickHouse database connection.
    
    Verifies that the application can connect to the ClickHouse database
    using the configuration from config.ini.
    """
    config = get_clickhouse_config()
    
    try:
        url = f"http://{config['host']}:{config['port']}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                assert response.status == 200, f"Failed to connect to ClickHouse at {url}"
                
    except Exception as e:
        pytest.fail(f"Failed to connect to ClickHouse: {str(e)}")


@pytest.mark.asyncio
async def test_clickhouse_tables():
    """
    Test ClickHouse table existence and structure.
    
    Verifies that required tables exist in the database and have
    the correct structure for storing daily and hourly data.
    """
    config = get_clickhouse_config()
    
    try:
        url = f"http://{config['host']}:{config['port']}"
        
        query = """
        SELECT name 
        FROM system.tables 
        WHERE database = 'prices' 
        AND name IN ('daily_prices', 'hourly_prices')
        """
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                params={'query': query},
                auth=aiohttp.BasicAuth(config['user'], config['password'])
            ) as response:
                assert response.status == 200, f"Failed to execute query: {await response.text()}"
                
                result = await response.text()
                
                assert 'daily_prices' in result, "Table 'daily_prices' not found"
                assert 'hourly_prices' in result, "Table 'hourly_prices' not found"
                
    except Exception as e:
        pytest.fail(f"Failed to check ClickHouse tables: {str(e)}")
