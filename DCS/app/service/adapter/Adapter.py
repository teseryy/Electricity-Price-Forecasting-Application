import asyncio
from datetime import datetime, timedelta

import pandas as pd
from dateutil.relativedelta import relativedelta

from app.service.request import *


class Adapter:
    """
    Adapter class for handling data operations between different services.
    
    This class coordinates data operations between various services including price, temperature,
    climate standard, and connection services. It manages data initialization and nightly updates
    for both hourly and daily data.
    
    Attributes:
        price_service (PriceService): Service for price data operations
        temperature_service (TemperatureService): Service for temperature data operations
        climate_standard_service (ClimateStandardService): Service for climate standard data
        connection_service (ConnectionService): Service for connection data operations
    """

    def __init__(self, climate_standard: ClimateStandardService,
                 prices: PriceService, temperature: TemperatureService):
        """
        Initialize the Adapter with required services.
        
        Args:
            price_service (PriceService): Service for price data operations
            temperature_service (TemperatureService): Service for temperature data operations
            climate_standard_service (ClimateStandardService): Service for climate standard data
            connection_service (ConnectionService): Service for connection data operations
        """
        self.climate_standard = climate_standard_service
        self.prices = price_service
        self.temperature = temperature_service

    async def __get_prices_hourly(self, start_date: str, end_date: str):
        """
        Process hourly price data.
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: Processed hourly price data
        """

        df = await self.prices.get_data_hourly_range(start_date, end_date)
        return df

    async def __get_prices_daily(self, start_date: str, end_date: str):
        """
        Process daily price data by aggregating hourly data.
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: Processed daily price data with mean prices
        """
        df = await self.prices.get_data_hourly_range(start_date, end_date)
        df_daily = df.resample('1D', on='date_time').agg({'price': 'mean'}).reset_index()

        return df_daily

    async def night_get_daily(self, date: str) -> pd.DataFrame:
        """
        Get daily data for nightly updates, combining price, temperature and climate data.
        
        Args:
            date (str): Target date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: Combined daily data with prices and temperatures
        """
        date_object = datetime.strptime(date, "%Y-%m-%d")

        day_before_yest = date_object - timedelta(days=2)
        after_14 = date_object + timedelta(days=14)
        after_29 = date_object + timedelta(days=30)

        df = await self.__get_prices_daily(str(day_before_yest.date()), str(date_object.date()))
        df = df.drop(1)

        df2 = await self.temperature.get_data_daily_range(str(date_object.date()), str(after_14.date()))

        df3 = await self.temperature.get_past_days_daily(2)
        df3 = df3.drop(1)

        df2 = pd.concat([df2, df3], axis=0, ignore_index=True)

        day_month = f"{after_29.month:02d}" + '-' + f"{after_29.day:02d}"

        df3 = self.climate_standard.get_data_daily_range(day_month, day_month)
        df3['date_time'] = pd.to_datetime(f'{after_29.year}-' + df3['month_day'] + ' 00:00:00')
        df3 = df3.rename(columns={'date_time': 'date_time', 'avg_temp': 'temperature'})
        df3 = df3[['date_time', 'temperature']]
        df2 = pd.concat([df2, df3], axis=0, ignore_index=True)

        df = df.merge(df2, on='date_time', how='outer')
        df = df.rename(columns={'date_time': 'date'})

        return df

    async def night_get_hourly(self, date: str) -> pd.DataFrame:
        """
        Get hourly data for nightly updates, combining price, temperature and climate data.
        
        Args:
            date (str): Target date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: Combined hourly data with prices and temperatures
        """
        date_object = datetime.strptime(date, "%Y-%m-%d")

        day_before_yest = date_object - timedelta(days=2)
        after_14 = date_object + timedelta(days=14)
        after_29 = date_object + timedelta(days=30)

        df = await self.__get_prices_hourly(str(day_before_yest.date()), str(date_object.date()))
        df = df[~df['date_time'].dt.date.eq(pd.to_datetime(date_object - timedelta(days=1)).date())]

        df2 = await self.temperature.get_data_hourly_range(str(date_object.date()), str(after_14.date()))
        df3 = await self.temperature.get_past_days_hourly(2)
        df3 = df3[~df3['date_time'].dt.date.eq(pd.to_datetime(date_object - timedelta(days=1)).date())]
        df2 = pd.concat([df2, df3], axis=0, ignore_index=True)

        day_month = f"{after_29.month:02d}" + '-' + f"{after_29.day:02d}"

        df3 = self.climate_standard.get_data_hourly_range(day_month + ' 00:00', day_month + ' 23:00')
        df3['date_time'] = pd.to_datetime(f'{after_29.year}-' + df3['date'])
        df3 = df3.rename(columns={'date_time': 'date_time', 'avg_temp': 'temperature'})
        df3 = df3[['date_time', 'temperature']]
        df2 = pd.concat([df2, df3], axis=0, ignore_index=True)

        df = df.merge(df2, on='date_time', how='outer')
        df = df.rename(columns={'date_time': 'date'})

        return df


    async def initialize_daily(self, date: str) -> pd.DataFrame:
        """
        Initialize daily data for a specific date, combining historical and forecast data.
        
        Args:
            date (str): Target date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: Combined daily data with prices and temperatures
        """
        date_object = datetime.strptime(date, "%Y-%m-%d")

        old_date = date_object - relativedelta(years=2)
        after_14 = date_object + timedelta(days=14)
        after_29 = date_object + timedelta(days=30)

        df = await self.__get_prices_daily(str(old_date.date()), str(date_object.date()))

        df2 = await self.temperature.get_historical_data_daily(str(old_date.date()),
                                                               str((date_object - timedelta(days=2)).date()))
        df3 = await self.temperature.get_past_days_daily(2)
        df2 = pd.concat([df2, df3], axis=0, ignore_index=True)
        df3 = await self.temperature.get_data_daily_range(str((date_object - timedelta(days=2)).date()),
                                                          str(after_14.date()))
        df2 = pd.concat([df2, df3], axis=0, ignore_index=True)

        day_month_after_29 = f"{after_29.month:02d}" + '-' + f"{after_29.day:02d}"
        day_month_after_14 = f"{after_14.month:02d}" + '-' + f"{after_14.day:02d}"
        df3 = self.climate_standard.get_data_daily_range(day_month_after_14 + ' 00:00', day_month_after_29 + ' 23:00')
        df3['date_time'] = pd.to_datetime(f'{after_29.year}-' + df3['month_day'])
        df3 = df3.rename(columns={'date_time': 'date_time', 'avg_temp': 'temperature'})
        df3 = df3[['date_time', 'temperature']]
        df2 = pd.concat([df2, df3], axis=0, ignore_index=True)

        df = df.merge(df2, on='date_time', how='outer')
        df = df.rename(columns={'date_time': 'date'})

        return df

    async def initialize_hourly(self, date: str) -> pd.DataFrame:
        """
        Initialize hourly data for a specific date, combining historical and forecast data.
        
        Args:
            date (str): Target date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: Combined hourly data with prices and temperatures
        """
        date_object = datetime.strptime(date, "%Y-%m-%d")

        old_date = date_object - relativedelta(years=2)
        after_14 = date_object + timedelta(days=14)
        after_29 = date_object + timedelta(days=30)

        df = await self.__get_prices_hourly(str(old_date.date()), str(date_object.date()))
        df2 = await self.temperature.get_historical_data_hourly(str(old_date.date()),
                                                               str((date_object - timedelta(days=2)).date()))
        df3 = await self.temperature.get_past_days_hourly(2)
        df2 = pd.concat([df2, df3], axis=0, ignore_index=True)
        df3 = await self.temperature.get_data_hourly_range(str((date_object - timedelta(days=2)).date()),
                                                          str(after_14.date()))
        df2 = pd.concat([df2, df3], axis=0, ignore_index=True)

        day_month_after_29 = f"{after_29.month:02d}" + '-' + f"{after_29.day:02d}"
        day_month_after_14 = f"{after_14.month:02d}" + '-' + f"{after_14.day:02d}"
        df3 = self.climate_standard.get_data_hourly_range(day_month_after_14 + ' 00:00', day_month_after_29 + ' 23:00')
        df3['date_time'] = pd.to_datetime(f'{after_29.year}-' + df3['date'])
        df3 = df3.rename(columns={'date_time': 'date_time', 'avg_temp': 'temperature'})
        df3 = df3[['date_time', 'temperature']]
        df2 = pd.concat([df2, df3], axis=0, ignore_index=True)

        df = df.merge(df2, on='date_time', how='outer')
        df = df.rename(columns={'date_time': 'date'})

        return df