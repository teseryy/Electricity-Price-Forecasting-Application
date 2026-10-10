from meteostat import Daily
import pandas as pd
import numpy as np
from datetime import datetime

class ClimateStandardService():
    """
    Service for retrieving climate standard data using Meteostat library.
    
    This service provides methods to fetch climate standard data in both hourly and daily formats.
    It uses the Meteostat library to get climate information for a specific location (Prague by default).
    
    Attributes:
        station_id (str): ID of the weather station
        start_date (datetime): Start date for climate data collection
        end_date (datetime): End date for climate data collection
        _data (pd.DataFrame): Raw climate data
        daily_climate_norms (pd.DataFrame): Processed daily climate norms
        hourly_temperatures (pd.DataFrame): Calculated hourly temperature data
    """
    
    def __init__(self):
        """
        Initialize the ClimateStandardService with default configuration for Prague.
        Sets up the station ID, date range and initializes climate data.
        """
        self.station_id = '11520'
        self.start_date = datetime(2014, 1, 1)
        self.end_date = datetime(2024, 12, 31)
        
        self.__initialize_data()
        self.__calculate_climate_norms()
        self.__calculate_hourly_temperatures()
    
    def __initialize_data(self):
        """
        Internal method to initialize and process raw climate data.
        Fetches data from Meteostat and calculates basic temperature metrics.
        
        Raises:
            ValueError: If required temperature data (TMAX/TMIN) is not available
        """
        self._data = Daily(self.station_id, start=self.start_date, end=self.end_date).fetch()
        
        if 'tmax' in self._data.columns and 'tmin' in self._data.columns:
            self._data['amplitude'] = self._data['tmax'] - self._data['tmin']
            self._data['avg_temp'] = (self._data['tmax'] + self._data['tmin']) / 2
        else:
            raise ValueError("ERROR: TMAX/TMIN data is not presented")
            
        self._data['month'] = self._data.index.month
        self._data['day'] = self._data.index.day
        self._data['month_day'] = self._data.index.strftime('%m-%d')
    
    def __calculate_climate_norms(self):
        """
        Internal method to calculate climate norms from raw data.
        Processes daily averages and temperature amplitudes.
        """
        daily_avg_ampl = self._data.groupby('month_day')['amplitude'].mean().reset_index()
        daily_avg_ampl.columns = ['month_day', 'avg_amplitude']
        
        self.daily_climate_norms = self._data.groupby("month_day")[["avg_temp"]].mean().reset_index()
        self.daily_climate_norms['avg_temp'] = self.daily_climate_norms['avg_temp'].round(0).astype(int)
        
        self._daily_climate = self._data.groupby(['month', 'day'])[['tmax', 'tmin']].mean().reset_index()
        self._daily_climate.columns = ['month', 'day', 'avg_tmax', 'avg_tmin']
        self._daily_climate["avg_amplitude"] = self._daily_climate["avg_tmax"] - self._daily_climate["avg_tmin"]
    
    def __get_temp_time(self, month: int):
        """
        Internal method to determine temperature peak times based on month.
        
        Args:
            month (int): Month number (1-12)
            
        Returns:
            tuple: (T_min_time, T_max_time) - hours of minimum and maximum temperatures
        """
        if month in [1, 2, 10, 11, 12]:
            return 7, 14
        elif month in [3, 4, 9]:
            return 6, 15
        elif month in [5, 6, 7, 8]:
            return 5, 15

    def __temperature_gen(self, hour, t_min, t_max, t_max_time):
        """
        Internal method to generate temperature for a specific hour using a mathematical model.
        
        Args:
            hour (int): Hour of the day (0-23)
            t_min (float): Minimum temperature
            t_max (float): Maximum temperature
            t_max_time (int): Hour of maximum temperature
            
        Returns:
            float: Calculated temperature for the given hour
        """
        return t_min + (t_max - t_min) * np.exp(-((hour - t_max_time) / 4) ** 2)

    def __calculate_hourly_temperatures(self):
        """
        Internal method to calculate hourly temperature data for all days.
        Uses temperature generation model to create hourly temperature profiles.
        """
        hourly_data = []

        for _, row in self._daily_climate.iterrows():
            T_min_time, T_max_time = self.__get_temp_time(row['month'])
            date = f"{int(row['month']):02d}-{int(row['day']):02d}"

            T_min = row['avg_tmin']
            T_max = row['avg_tmax']
            A = row['avg_amplitude'] / 2

            for hour in range(24):
                date_time = f"{date} {hour:02d}:00"
                t = self.__temperature_gen(hour, T_min, T_max, T_max_time)
                hourly_data.append({
                    'date': date_time,
                    'temperature': t
                })
        
        self.hourly_temperatures = pd.DataFrame(hourly_data)
        self.hourly_temperatures['temperature'] = self.hourly_temperatures['temperature'].round(0).astype(int)
    
    def get_data_hourly_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get hourly temperature data for a date range.
        
        Args:
            start_date (str): Start date in MM-DD format
            end_date (str): End date in MM-DD format
            
        Returns:
            pd.DataFrame: DataFrame containing hourly temperature data with columns:
                - date: datetime string in MM-DD HH:00 format
                - temperature: temperature in Celsius (rounded to integer)
        """
        return self.hourly_temperatures[
            (self.hourly_temperatures['date'] >= start_date) &
            (self.hourly_temperatures['date'] <= end_date)
        ].sort_values('date')
    
    def get_data_daily_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get daily temperature data for a date range.
        
        Args:
            start_date (str): Start date in MM-DD format
            end_date (str): End date in MM-DD format
            
        Returns:
            pd.DataFrame: DataFrame containing daily temperature data with columns:
                - month_day: date in MM-DD format
                - avg_temp: average temperature in Celsius (rounded to integer)
        """
        return self.daily_climate_norms[
            (self.daily_climate_norms['month_day'] >= start_date) &
            (self.daily_climate_norms['month_day'] <= end_date)
        ].sort_values('month_day')