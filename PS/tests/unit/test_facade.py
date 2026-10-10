import pytest
from datetime import datetime, timedelta
import pandas as pd
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.service.Facade import Facade
from app.service.adapter.Adapter import Adapter
from app.service.connection.RedisService import RedisService

@pytest.fixture
def mock_redis_service():
    """
    Fixture that provides a mock Redis service.

    Returns:
        AsyncMock: A mock object that mimics RedisService behavior
    """
    return AsyncMock(spec=RedisService)

@pytest.fixture
def mock_adapter():
    """
    Fixture that provides a mock Adapter.

    Returns:
        Mock: A mock object that mimics Adapter behavior
    """
    return Mock(spec=Adapter)

@pytest.fixture
def facade(mock_redis_service, mock_adapter):
    """
    Fixture that provides a Facade instance with mocked dependencies.

    Args:
        mock_redis_service: Mocked Redis service
        mock_adapter: Mocked Adapter

    Returns:
        Facade: A Facade instance configured with mock dependencies
    """
    return Facade(
        redis_dtable="daily_forecast",
        redis_htable="hourly_forecast",
        redis_client=mock_redis_service,
        adapter=mock_adapter
    )

@pytest.mark.asyncio
async def test_train(facade, mock_adapter, mock_redis_service):
    """
    Test the training process of the Facade.

    This test verifies that:
    1. Training data is correctly retrieved from the adapter
    2. Models are properly trained with the training data
    3. Predictions are made using the trained models
    4. Results are correctly saved to Redis

    Args:
        facade: Facade instance with mocked dependencies
        mock_adapter: Mocked Adapter
        mock_redis_service: Mocked Redis service
    """
    test_date = "2024-03-20"
    
    # Prepare test data with multiple rows
    daily_train_data = pd.DataFrame({
        'date': [
            datetime.strptime(test_date, "%Y-%m-%d").date(),
            (datetime.strptime(test_date, "%Y-%m-%d") + timedelta(days=1)).date()
        ],
        'price': [100.5, 101.5],
        'temperature': [20.5, 21.5],
        'inserted_at': [datetime.now(), datetime.now()]
    })
    
    hourly_train_data = pd.DataFrame({
        'date': [
            datetime.strptime(test_date, "%Y-%m-%d"),
            datetime.strptime(test_date, "%Y-%m-%d") + timedelta(hours=1)
        ],
        'price': [100.5, 101.5],
        'temperature': [20.5, 21.5],
        'inserted_at': [datetime.now(), datetime.now()]
    })
    
    daily_forecast_data = pd.DataFrame({
        'date': [
            datetime.strptime(test_date, "%Y-%m-%d").date(),
            (datetime.strptime(test_date, "%Y-%m-%d") + timedelta(days=1)).date()
        ],
        'price': [101.5, 102.5],
        'temperature': [21.5, 22.5],
        'inserted_at': [datetime.now(), datetime.now()]
    })
    
    hourly_forecast_data = pd.DataFrame({
        'date': [
            datetime.strptime(test_date, "%Y-%m-%d"),
            datetime.strptime(test_date, "%Y-%m-%d") + timedelta(hours=1)
        ],
        'price': [101.5, 102.5],
        'temperature': [21.5, 22.5],
        'inserted_at': [datetime.now(), datetime.now()]
    })
    
    # Configure mocks
    mock_adapter.get_train_data_daily.return_value = daily_train_data
    mock_adapter.get_train_data_hourly.return_value = hourly_train_data
    mock_adapter.get_forecast_data_daily.return_value = daily_forecast_data
    mock_adapter.get_forecast_data_hourly.return_value = hourly_forecast_data
    
    # Create mock instances
    mock_daily_model = Mock()
    mock_hourly_model = Mock()
    
    # Create expected prediction results
    daily_prediction = pd.DataFrame({
        'date': [
            datetime.strptime(test_date, "%Y-%m-%d").date(),
            (datetime.strptime(test_date, "%Y-%m-%d") + timedelta(days=1)).date()
        ],
        'price': [102.5, 103.5],
        'temperature': [21.5, 22.5],
        'lower_bound': [97.5, 98.5],
        'upper_bound': [107.5, 108.5]
    })
    
    hourly_prediction = pd.DataFrame({
        'date': [
            datetime.strptime(test_date, "%Y-%m-%d"),
            datetime.strptime(test_date, "%Y-%m-%d") + timedelta(hours=1)
        ],
        'price': [102.5, 103.5],
        'temperature': [21.5, 22.5],
        'lower_bound': [97.5, 98.5],
        'upper_bound': [107.5, 108.5]
    })
    
    # Configure mock instances
    def mock_train_model(data):
        return None
    
    def mock_predict_daily(data):
        return daily_prediction
    
    def mock_predict_hourly(data):
        return hourly_prediction
    
    mock_daily_model.train_model = Mock(side_effect=mock_train_model)
    mock_daily_model.predict = Mock(side_effect=mock_predict_daily)
    mock_hourly_model.train_model = Mock(side_effect=mock_train_model)
    mock_hourly_model.predict = Mock(side_effect=mock_predict_hourly)
    
    # Call the method under test with mock models
    await facade.train(test_date, mock_daily_model, mock_hourly_model)
    
    # Verify that methods were called with correct parameters
    mock_adapter.get_train_data_daily.assert_called_once_with(test_date)
    mock_adapter.get_train_data_hourly.assert_called_once_with(test_date)
    mock_adapter.get_forecast_data_daily.assert_called_once_with(test_date)
    mock_adapter.get_forecast_data_hourly.assert_called_once_with(test_date)
    
    # Verify that models were trained
    mock_daily_model.train_model.assert_called_once_with(daily_train_data)
    mock_hourly_model.train_model.assert_called_once_with(hourly_train_data)
    
    # Verify that predictions were made
    mock_daily_model.predict.assert_called_once_with(daily_forecast_data)
    mock_hourly_model.predict.assert_called_once_with(hourly_forecast_data)
    
    # Verify that data was saved to Redis
    assert mock_redis_service.insert_data.call_count == 2
    
    # Get the actual calls to insert_data
    calls = mock_redis_service.insert_data.call_args_list
    
    # Verify daily forecast data
    daily_call = calls[0]
    assert daily_call[0][0] == "daily_forecast"
    pd.testing.assert_frame_equal(daily_call[0][1], daily_prediction)
    
    # Verify hourly forecast data
    hourly_call = calls[1]
    assert hourly_call[0][0] == "hourly_forecast"
    pd.testing.assert_frame_equal(hourly_call[0][1], hourly_prediction)

@pytest.mark.asyncio
async def test_get_forecast_data_hourly(facade, mock_redis_service):
    """
    Test retrieving hourly forecast data.

    This test verifies that:
    1. The correct Redis table is queried
    2. The returned data has the expected structure
    3. The data is returned as a pandas DataFrame

    Args:
        facade: Facade instance with mocked dependencies
        mock_redis_service: Mocked Redis service
    """
    test_data = pd.DataFrame({
        'date': [datetime.now()],
        'price': [100.5],
        'temperature': [20.5],
        'lower_bound': [95.5],
        'upper_bound': [105.5]
    })
    
    mock_redis_service.get_table.return_value = test_data
    
    result = await facade.get_forecast_data_hourly()
    
    mock_redis_service.get_table.assert_called_once_with("hourly_forecast")
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ['date', 'price', 'temperature', 'lower_bound', 'upper_bound']

@pytest.mark.asyncio
async def test_get_forecast_data_daily(facade, mock_redis_service):
    """
    Test retrieving daily forecast data.

    This test verifies that:
    1. The correct Redis table is queried
    2. The returned data has the expected structure
    3. The data is returned as a pandas DataFrame

    Args:
        facade: Facade instance with mocked dependencies
        mock_redis_service: Mocked Redis service
    """
    test_data = pd.DataFrame({
        'date': [datetime.now().date()],
        'price': [100.5],
        'temperature': [20.5],
        'lower_bound': [95.5],
        'upper_bound': [105.5]
    })
    
    mock_redis_service.get_table.return_value = test_data
    
    result = await facade.get_forecast_data_daily()
    
    mock_redis_service.get_table.assert_called_once_with("daily_forecast")
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ['date', 'price', 'temperature', 'lower_bound', 'upper_bound']

@pytest.mark.asyncio
async def test_get_forecast_by_day_daily(facade, mock_redis_service):
    """
    Test retrieving daily forecast data for a specific date.

    This test verifies that:
    1. The correct Redis table is queried with the right date
    2. The returned data has the expected structure
    3. The data is returned as a pandas DataFrame

    Args:
        facade: Facade instance with mocked dependencies
        mock_redis_service: Mocked Redis service
    """
    test_date = "2024-03-20"
    test_data = pd.DataFrame({
        'date': [datetime.strptime(test_date, "%Y-%m-%d").date()],
        'price': [100.5],
        'temperature': [20.5],
        'lower_bound': [95.5],
        'upper_bound': [105.5]
    })
    
    mock_redis_service.get_by_date.return_value = test_data
    
    result = await facade.get_forecast_by_day_daily(test_date)
    
    mock_redis_service.get_by_date.assert_called_once_with("daily_forecast", test_date)
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ['date', 'price', 'temperature', 'lower_bound', 'upper_bound']

@pytest.mark.asyncio
async def test_get_forecast_by_day_hourly(facade, mock_redis_service):
    """
    Test retrieving hourly forecast data for a specific date.

    This test verifies that:
    1. The correct Redis table is queried with the right date
    2. The returned data has the expected structure
    3. The data is returned as a pandas DataFrame

    Args:
        facade: Facade instance with mocked dependencies
        mock_redis_service: Mocked Redis service
    """
    test_date = "2024-03-20"
    test_data = pd.DataFrame({
        'date': [datetime.strptime(test_date, "%Y-%m-%d")],
        'price': [100.5],
        'temperature': [20.5],
        'lower_bound': [95.5],
        'upper_bound': [105.5]
    })
    
    mock_redis_service.get_by_date.return_value = test_data
    
    result = await facade.get_forecast_by_day_hourly(test_date)
    
    mock_redis_service.get_by_date.assert_called_once_with("hourly_forecast", test_date)
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ['date', 'price', 'temperature', 'lower_bound', 'upper_bound']

@pytest.mark.asyncio
async def test_get_hist_data_daily(facade, mock_adapter):
    """
    Test retrieving historical daily data.

    This test verifies that:
    1. The adapter is called with correct date range
    2. The returned data has the expected structure
    3. The data is returned as a pandas DataFrame

    Args:
        facade: Facade instance with mocked dependencies
        mock_adapter: Mocked Adapter
    """
    start_date = "2024-03-01"
    end_date = "2024-03-20"
    test_data = pd.DataFrame({
        'date': [datetime.strptime(start_date, "%Y-%m-%d").date()],
        'price': [100.5],
        'temperature': [20.5]
    })
    
    mock_adapter.get_old_data_daily.return_value = test_data
    
    result = await facade.get_hist_data_daily(start_date, end_date)
    
    mock_adapter.get_old_data_daily.assert_called_once_with(start_date, end_date)
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ['date', 'price', 'temperature']

@pytest.mark.asyncio
async def test_get_hist_data_hourly(facade, mock_adapter):
    """
    Test retrieving historical hourly data.

    This test verifies that:
    1. The adapter is called with correct date range
    2. The returned data has the expected structure
    3. The data is returned as a pandas DataFrame

    Args:
        facade: Facade instance with mocked dependencies
        mock_adapter: Mocked Adapter
    """
    start_date = "2024-03-01"
    end_date = "2024-03-20"
    test_data = pd.DataFrame({
        'date': [datetime.strptime(start_date, "%Y-%m-%d")],
        'price': [100.5],
        'temperature': [20.5]
    })
    
    mock_adapter.get_old_data_hourly.return_value = test_data
    
    result = await facade.get_hist_data_hourly(start_date, end_date)
    
    mock_adapter.get_old_data_hourly.assert_called_once_with(start_date, end_date)
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ['date', 'price', 'temperature'] 