import pandas as pd

from app.service import RedisService, Adapter, Forecast


class Facade:
    """
    Facade class provides a unified interface for training and retrieving forecasts.

    This class coordinates the interaction between the data adapter, forecast models,
    and Redis storage. It allows training of daily and hourly models, saving results,
    and retrieving both forecast and historical data.
    """
    def __init__(self, redis_dtable: str, redis_htable: str,
                 redis_client: RedisService, adapter: Adapter):
        """
        Initialize the Facade.

        Args:
            redis_dtable (str): Name of the Redis table for daily forecasts.
            redis_htable (str): Name of the Redis table for hourly forecasts.
            redis_client (RedisService): Redis client instance for data storage.
            adapter (Adapter): Adapter instance for data access.
        """
        self.redis_client = redis_client
        self.adapter = adapter
        self.redis_htable = redis_htable
        self.redis_dtable = redis_dtable

    async def train(self, date: str, daily_model: Forecast,
                    hourly_model: Forecast):
        """
        Train daily and hourly forecast models and save results to Redis.

        Args:
            date (str): The date for which to train the models (format: YYYY-MM-DD).
            daily_model (Forecast): The model instance for daily forecasts.
            hourly_model (Forecast): The model instance for hourly forecasts.
        """
        df_daily = self.adapter.get_train_data_daily(date)
        df_hourly = self.adapter.get_train_data_hourly(date)

        daily_model.train_model(df_daily)
        hourly_model.train_model(df_hourly)

        df_forecast_daily = self.adapter.get_forecast_data_daily(date)
        df_forecast_hourly = self.adapter.get_forecast_data_hourly(date)

        res_daily_forecast = daily_model.predict(df_forecast_daily)
        res_hourly_forecast = hourly_model.predict(df_forecast_hourly)

        await self.redis_client.insert_data(self.redis_dtable, res_daily_forecast)
        await self.redis_client.insert_data(self.redis_htable, res_hourly_forecast)

    async def get_forecast_data_hourly(self):
        """
        Retrieve the entire hourly forecast table from Redis.

        Returns:
            pd.DataFrame: DataFrame containing hourly forecast data.
        """
        return await self.redis_client.get_table(self.redis_htable)

    async def get_forecast_data_daily(self):
        """
        Retrieve the entire daily forecast table from Redis.

        Returns:
            pd.DataFrame: DataFrame containing daily forecast data.
        """
        return await self.redis_client.get_table(self.redis_dtable)

    async def get_forecast_by_day_daily(self, date: str):
        """
        Retrieve daily forecast data for a specific date from Redis.

        Args:
            date (str): The date for which to retrieve the forecast (format: YYYY-MM-DD).

        Returns:
            pd.DataFrame: DataFrame containing daily forecast data for the given date.
        """
        return await self.redis_client.get_by_date(self.redis_dtable, date)

    async def get_forecast_by_day_hourly(self, date: str):
        """
        Retrieve hourly forecast data for a specific date from Redis.

        Args:
            date (str): The date for which to retrieve the forecast (format: YYYY-MM-DD).

        Returns:
            pd.DataFrame: DataFrame containing hourly forecast data for the given date.
        """
        return await self.redis_client.get_by_date(self.redis_htable, date)

    async def get_hist_data_daily(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Retrieve historical daily data for a given date range.

        Args:
            start_date (str): Start date of the range (format: YYYY-MM-DD).
            end_date (str): End date of the range (format: YYYY-MM-DD).

        Returns:
            pd.DataFrame: DataFrame containing historical daily data.
        """
        return self.adapter.get_old_data_daily(start_date, end_date)

    async def get_hist_data_hourly(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Retrieve historical hourly data for a given date range.

        Args:
            start_date (str): Start date of the range (format: YYYY-MM-DD).
            end_date (str): End date of the range (format: YYYY-MM-DD).

        Returns:
            pd.DataFrame: DataFrame containing historical hourly data.
        """
        return self.adapter.get_old_data_hourly(start_date, end_date)
