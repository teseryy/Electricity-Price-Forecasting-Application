"""
Unit tests for the Adapter class.

This module contains tests for the Adapter class functionality, including:
- Price data processing (hourly and daily)
- Data initialization
- Nightly data updates
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.service.adapter.Adapter import Adapter
from app.service.request.ClimateStandardService import ClimateStandardService
from app.service.request.PriceService import PriceService
from app.service.request.TemperatureService import TemperatureService


@pytest.fixture
def mock_services():
    """
    Fixture providing mock services for testing.
    
    Returns:
        tuple: Mock instances of PriceService, TemperatureService, and ClimateStandardService
    """
    climate_standard = Mock(spec=ClimateStandardService)
    prices = Mock(spec=PriceService)
    temperature = Mock(spec=TemperatureService)
    
    return climate_standard, prices, temperature


@pytest.fixture
def adapter(mock_services):
    """
    Fixture providing an Adapter instance with mock services.
    
    Args:
        mock_services: Fixture providing mock services
        
    Returns:
        Adapter: Configured Adapter instance
    """
    climate_standard, prices, temperature = mock_services
    return Adapter(climate_standard, prices, temperature)


@pytest.mark.asyncio
async def test_get_prices_hourly(adapter, mock_services):
    """
    Test hourly price data retrieval and processing.
    
    Args:
        adapter: Fixture providing Adapter instance
        mock_services: Fixture providing mock services
    """
    _, prices, _ = mock_services
    
    # Prepare test data
    test_data = pd.DataFrame({
        'date_time': pd.date_range(start='2024-01-01', periods=24, freq='h'),
        'price': [100.0] * 24
    })
    
    # Configure mock
    prices.get_data_hourly_range = AsyncMock(return_value=test_data)
    
    # Call the method under test
    result = await adapter._Adapter__get_prices_hourly('2024-01-01', '2024-01-02')
    
    # Check results
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 24
    assert 'date_time' in result.columns
    assert 'price' in result.columns
    prices.get_data_hourly_range.assert_called_once_with('2024-01-01', '2024-01-02')


@pytest.mark.asyncio
async def test_get_prices_daily(adapter, mock_services):
    """
    Test daily price data retrieval and processing.
    
    Args:
        adapter: Fixture providing Adapter instance
        mock_services: Fixture providing mock services
    """
    _, prices, _ = mock_services
    
    # Prepare test data
    test_data = pd.DataFrame({
        'date_time': pd.date_range(start='2024-01-01', periods=24, freq='h'),
        'price': [100.0] * 24
    })
    
    # Configure mock
    prices.get_data_hourly_range = AsyncMock(return_value=test_data)
    
    # Call the method under test
    result = await adapter._Adapter__get_prices_daily('2024-01-01', '2024-01-02')
    
    # Check results
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1  # Should be one day after aggregation
    assert 'date_time' in result.columns
    assert 'price' in result.columns
    prices.get_data_hourly_range.assert_called_once_with('2024-01-01', '2024-01-02')


@pytest.mark.asyncio
async def test_night_get_daily(adapter, mock_services):
    """
    Test nightly daily data retrieval and processing.
    
    Args:
        adapter: Fixture providing Adapter instance
        mock_services: Fixture providing mock services
    """
    climate_standard, prices, temperature = mock_services
    
    # Prepare test data
    test_date = '2024-01-01'
    date_object = datetime.strptime(test_date, "%Y-%m-%d")
    
    # Mock for prices
    prices_data = pd.DataFrame({
        'date_time': pd.date_range(start=date_object - timedelta(days=2), periods=2, freq='D'),
        'price': [100.0, 200.0]
    })
    prices.get_data_hourly_range = AsyncMock(return_value=prices_data)
    
    # Mock for temperature
    temp_data = pd.DataFrame({
        'date_time': pd.date_range(start=date_object, periods=15, freq='D'),
        'temperature': [20] * 15
    })
    temperature.get_data_daily_range = AsyncMock(return_value=temp_data)
    
    past_temp_data = pd.DataFrame({
        'date_time': pd.date_range(start=date_object - timedelta(days=2), periods=2, freq='D'),
        'temperature': [15, 16]
    })
    temperature.get_past_days_daily = AsyncMock(return_value=past_temp_data)
    
    # Mock for climate data
    climate_data = pd.DataFrame({
        'month_day': ['01-30'],
        'avg_temp': [25]
    })
    climate_standard.get_data_daily_range = Mock(return_value=climate_data)
    
    # Call the method under test
    result = await adapter.night_get_daily(test_date)
    
    # Check results
    assert isinstance(result, pd.DataFrame)
    assert 'date' in result.columns
    assert 'price' in result.columns
    assert 'temperature' in result.columns


@pytest.mark.asyncio
async def test_night_get_hourly(adapter, mock_services):
    """
    Test hourly data retrieval and processing for nightly updates.
    
    Args:
        adapter: Fixture providing Adapter instance
        mock_services: Fixture providing mock services
    """
    climate_standard, prices, temperature = mock_services
    
    # Prepare test data
    test_date = '2024-01-01'
    date_object = datetime.strptime(test_date, "%Y-%m-%d")
    
    # Mock for prices
    prices_data = pd.DataFrame({
        'date_time': pd.date_range(start=date_object - timedelta(days=2), periods=48, freq='h'),
        'price': [100.0] * 48
    })
    prices.get_data_hourly_range = AsyncMock(return_value=prices_data)
    
    # Mock for temperature
    temp_data = pd.DataFrame({
        'date_time': pd.date_range(start=date_object, periods=360, freq='h'),
        'temperature': [20] * 360
    })
    temperature.get_data_hourly_range = AsyncMock(return_value=temp_data)
    
    past_temp_data = pd.DataFrame({
        'date_time': pd.date_range(start=date_object - timedelta(days=2), periods=48, freq='h'),
        'temperature': [15] * 48
    })
    temperature.get_past_days_hourly = AsyncMock(return_value=past_temp_data)
    
    # Mock for climate data
    climate_data = pd.DataFrame({
        'date': ['01-30 00:00', '01-30 23:00'],
        'avg_temp': [25, 26]
    })
    climate_standard.get_data_hourly_range = Mock(return_value=climate_data)
    
    # Call the method under test
    result = await adapter.night_get_hourly(test_date)
    
    # Check results
    assert isinstance(result, pd.DataFrame)
    assert 'date' in result.columns
    assert 'price' in result.columns
    assert 'temperature' in result.columns


@pytest.mark.asyncio
async def test_initialize_daily(adapter, mock_services):
    """
    Test daily data initialization process.
    
    Args:
        adapter: Fixture providing Adapter instance
        mock_services: Fixture providing mock services
    """
    climate_standard, prices, temperature = mock_services
    
    # Prepare test data
    test_date = '2024-01-01'
    date_object = datetime.strptime(test_date, "%Y-%m-%d")
    
    # Mock for prices
    prices_data = pd.DataFrame({
        'date_time': pd.date_range(start=date_object - timedelta(days=730), periods=730, freq='D'),
        'price': [100.0] * 730
    })
    prices.get_data_hourly_range = AsyncMock(return_value=prices_data)
    
    # Mock for temperature
    historical_temp_data = pd.DataFrame({
        'date_time': pd.date_range(start=date_object - timedelta(days=730), periods=728, freq='D'),
        'temperature': [20] * 728
    })
    temperature.get_historical_data_daily = AsyncMock(return_value=historical_temp_data)
    
    past_temp_data = pd.DataFrame({
        'date_time': pd.date_range(start=date_object - timedelta(days=2), periods=2, freq='D'),
        'temperature': [15, 16]
    })
    temperature.get_past_days_daily = AsyncMock(return_value=past_temp_data)
    
    future_temp_data = pd.DataFrame({
        'date_time': pd.date_range(start=date_object - timedelta(days=2), periods=16, freq='D'),
        'temperature': [20] * 16
    })
    temperature.get_data_daily_range = AsyncMock(return_value=future_temp_data)
    
    # Mock for climate data
    climate_data = pd.DataFrame({
        'month_day': ['01-14', '01-30'],
        'avg_temp': [25, 26]
    })
    climate_standard.get_data_daily_range = Mock(return_value=climate_data)
    
    # Call the method under test
    result = await adapter.initialize_daily(test_date)
    
    # Check results
    assert isinstance(result, pd.DataFrame)
    assert 'date' in result.columns
    assert 'price' in result.columns
    assert 'temperature' in result.columns


@pytest.mark.asyncio
async def test_initialize_hourly(adapter, mock_services):
    """
    Test hourly data initialization process.
    
    Args:
        adapter: Fixture providing Adapter instance
        mock_services: Fixture providing mock services
    """
    climate_standard, prices, temperature = mock_services
    
    # Prepare test data
    test_date = '2024-01-01'
    date_object = datetime.strptime(test_date, "%Y-%m-%d")
    
    # Mock for prices
    prices_data = pd.DataFrame({
        'date_time': pd.date_range(start=date_object - timedelta(days=730), periods=17520, freq='h'),
        'price': [100.0] * 17520
    })
    prices.get_data_hourly_range = AsyncMock(return_value=prices_data)
    
    # Mock for temperature
    historical_temp_data = pd.DataFrame({
        'date_time': pd.date_range(start=date_object - timedelta(days=730), periods=17472, freq='h'),
        'temperature': [20] * 17472
    })
    temperature.get_historical_data_hourly = AsyncMock(return_value=historical_temp_data)
    
    past_temp_data = pd.DataFrame({
        'date_time': pd.date_range(start=date_object - timedelta(days=2), periods=48, freq='h'),
        'temperature': [15] * 48
    })
    temperature.get_past_days_hourly = AsyncMock(return_value=past_temp_data)
    
    future_temp_data = pd.DataFrame({
        'date_time': pd.date_range(start=date_object - timedelta(days=2), periods=384, freq='h'),
        'temperature': [20] * 384
    })
    temperature.get_data_hourly_range = AsyncMock(return_value=future_temp_data)
    
    # Mock for climate data
    climate_data = pd.DataFrame({
        'date': ['01-14 00:00', '01-30 23:00'],
        'avg_temp': [25, 26]
    })
    climate_standard.get_data_hourly_range = Mock(return_value=climate_data)
    
    # Call the method under test
    result = await adapter.initialize_hourly(test_date)
    
    # Check results
    assert isinstance(result, pd.DataFrame)
    assert 'date' in result.columns
    assert 'price' in result.columns
    assert 'temperature' in result.columns 