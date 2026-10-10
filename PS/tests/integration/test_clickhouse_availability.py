import pytest
import asyncio
import aiohttp
import configparser
import os
from typing import Dict


def get_clickhouse_config() -> Dict[str, str]:
    """
    Read ClickHouse configuration from config.ini.

    This function reads the ClickHouse configuration settings from the config.ini file,
    including host, port, user, password, and database name.

    Returns:
        Dict[str, str]: Dictionary containing ClickHouse configuration:
            - host: ClickHouse server address
            - port: ClickHouse server port
            - database: Database name
            - user: Database username
            - password: Database password

    Raises:
        FileNotFoundError: If config.ini file is not found
        KeyError: If ClickHouse section is missing in config.ini
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
    Test ClickHouse connection.

    This integration test verifies:
    1. Ability to establish HTTP connection to ClickHouse server
    2. Server responds with 200 OK status
    3. Connection parameters are valid

    The test:
    - Creates an HTTP session
    - Attempts to connect to ClickHouse server
    - Verifies the response status
    - Cleans up connection

    Raises:
        pytest.fail: If connection fails
        AssertionError: If server response is not 200 OK
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
    Test ClickHouse tables existence.

    This integration test verifies:
    1. Required tables exist in the database
    2. Tables are accessible via HTTP interface
    3. Database user has proper permissions

    The test:
    - Connects to ClickHouse via HTTP
    - Executes a query to check table existence
    - Verifies required tables are present
    - Cleans up connection

    Raises:
        pytest.fail: If table check fails
        AssertionError: If required tables are missing or inaccessible
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
