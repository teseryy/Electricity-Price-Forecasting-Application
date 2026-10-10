from datetime import datetime, timedelta

import pandas as pd

from app.service import ClickHouseService

class Adapter:
    """
    Adapter class for data transformation and retrieval from ClickHouse.

    This class serves as an intermediary between the application and ClickHouse database,
    handling data transformations and providing methods for retrieving data in different
    formats (daily and hourly). It manages data preprocessing and format standardization.

    Attributes:
        clickhouse_service (ClickHouseService): Service for ClickHouse database operations
        daily_table (str): Name of the table containing daily data
        hourly_table (str): Name of the table containing hourly data
    """

    def __init__(self, daily_table, hourly_table, clickhouse_service: ClickHouseService):
        """
        Initialize the Adapter with table names and ClickHouse service.

        Args:
            daily_table (str): Name of the table containing daily data
            hourly_table (str): Name of the table containing hourly data
            clickhouse_service (ClickHouseService): Service for ClickHouse operations
        """
        self.clickhouse_service = clickhouse_service
        self.daily_table = daily_table
        self.hourly_table = hourly_table

    def __get_train_data(self, table: str, date: str):
        """
        Retrieve and preprocess training data from specified table.

        Args:
            table (str): Name of the table to query
            date (str): Cutoff date in format 'YYYY-MM-DD'

        Returns:
            pd.DataFrame: Preprocessed training data with standardized column names
        """
        df = self.clickhouse_service.get_train_data(table, date)
        df.rename(columns={'temp:': 'temperature'})

        return df

    def __get_forecast_data(self, table: str, date: str):
        """
        Retrieve and preprocess forecast data from specified table.

        Args:
            table (str): Name of the table to query
            date (str): Start date in format 'YYYY-MM-DD'

        Returns:
            pd.DataFrame: Preprocessed forecast data with standardized column names
        """
        df = self.clickhouse_service.get_forecast_data(table, date)
        df.rename(columns={'temp:': 'temperature'})

        return df

    def __get_old_data(self, table: str, start_date: str, end_date: str):
        """
        Retrieve and preprocess historical data from specified table.

        Args:
            table (str): Name of the table to query
            start_date (str): Start date in format 'YYYY-MM-DD'
            end_date (str): End date in format 'YYYY-MM-DD'

        Returns:
            pd.DataFrame: Preprocessed historical data with:
                - Standardized column names
                - Missing values filled with mean values
        """
        df = self.clickhouse_service.get_old_data(table, start_date, end_date)
        df.rename(columns={'temp:': 'temperature'}, inplace=True)
        df = df.fillna(df.mean(numeric_only=True))

        return df

    def get_train_data_hourly(self, date: str) -> pd.DataFrame:
        """
        Retrieve hourly training data up to the specified date.

        Args:
            date (str): Cutoff date in format 'YYYY-MM-DD'

        Returns:
            pd.DataFrame: Hourly training data with standardized format
        """
        input_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = input_date + timedelta(days=1)

        return self.__get_train_data(self.hourly_table, str(end_date))

    def get_train_data_daily(self, date: str) -> pd.DataFrame:
        """
        Retrieve daily training data up to the specified date.

        Args:
            date (str): Cutoff date in format 'YYYY-MM-DD'

        Returns:
            pd.DataFrame: Daily training data with standardized format
        """
        input_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = input_date + timedelta(days=1)

        return self.__get_train_data(self.daily_table, str(end_date.date()))

    def get_forecast_data_hourly(self, date: str) -> pd.DataFrame:
        """
        Retrieve hourly forecast data starting from the specified date.

        Args:
            date (str): Start date in format 'YYYY-MM-DD'

        Returns:
            pd.DataFrame: Hourly forecast data with standardized format
        """
        input_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = input_date + timedelta(days=1)

        return self.__get_forecast_data(self.hourly_table, str(end_date))

    def get_forecast_data_daily(self, date: str) -> pd.DataFrame:
        """
        Retrieve daily forecast data starting from the specified date.

        Args:
            date (str): Start date in format 'YYYY-MM-DD'

        Returns:
            pd.DataFrame: Daily forecast data with standardized format
        """
        input_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = input_date + timedelta(days=1)

        return self.__get_forecast_data(self.daily_table, str(end_date.date()))

    def get_old_data_daily(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Retrieve historical daily data within the specified date range.

        Args:
            start_date (str): Start date in format 'YYYY-MM-DD'
            end_date (str): End date in format 'YYYY-MM-DD'

        Returns:
            pd.DataFrame: Historical daily data with standardized format
        """
        start_date_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_date = datetime.strptime(end_date, "%Y-%m-%d")
        end_date_date = end_date_date + timedelta(days=1)

        return self.__get_old_data(self.daily_table, str(start_date_date.date()), str(end_date_date.date()))

    def get_old_data_hourly(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Retrieve historical hourly data within the specified date range.

        Args:
            start_date (str): Start date in format 'YYYY-MM-DD'
            end_date (str): End date in format 'YYYY-MM-DD'

        Returns:
            pd.DataFrame: Historical hourly data with standardized format
        """
        start_date_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_date = datetime.strptime(end_date, "%Y-%m-%d")
        end_date_date = end_date_date + timedelta(days=1)

        return self.__get_old_data(self.hourly_table, str(start_date_date), str(end_date_date))