import pandas as pd
import aiohttp


class TemperatureService:
    """
    Service for retrieving temperature data from Open-Meteo API.
    
    This service provides methods to fetch temperature data in both hourly and daily formats,
    including historical data and forecasts. It uses the Open-Meteo API
    to get temperature information for a specific location (Prague by default).
    
    Attributes:
        forecast_url (str): URL for the forecast API endpoint
        historical_url (str): URL for the historical data API endpoint
        latitude (float): Latitude coordinate for the location (default: 50.0755 for Prague)
        longitude (float): Longitude coordinate for the location (default: 14.4378 for Prague)
        timezone (str): Timezone for the location (default: "Europe/Prague")
    
    Example:
        >>> service = TemperatureService()
        >>> daily_data = await service.get_data_daily_range("2024-01-01", "2024-01-02")
        >>> print(daily_data)
    """
    
    def __init__(self):
        """
        Initialize the TemperatureService with default configuration for Prague.
        """
        self.forecast_url = "https://api.open-meteo.com/v1/forecast"
        self.historical_url = "https://archive-api.open-meteo.com/v1/archive"
        self.latitude = 50.0755 
        self.longitude = 14.4378
        self.timezone = "Europe/Prague"
    
    async def __fetch_data_(self, params: dict, url: str) -> dict:
        """
        Internal method to fetch data from the Open-Meteo API.
        
        Args:
            params (dict): Query parameters for the API request
            url (str): API endpoint URL
            
        Returns:
            dict: JSON response from the API
            
        Raises:
            Exception: If the API request fails or returns non-200 status code
        """
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Weather API error: {response.status}")
                return await response.json()
    
    async def get_data_hourly_range(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """
        Get hourly temperature data for the next 15 days.
        
        Args:
            start_date (str, optional): Start date in YYYY-MM-DD format. Defaults to "".
            end_date (str, optional): End date in YYYY-MM-DD format. Defaults to "".
            
        Returns:
            pd.DataFrame: DataFrame containing hourly temperature data with columns:
                - date_time: datetime index
                - temperature: temperature in Celsius (rounded to integer)
                
        Example:
            >>> df = await service.get_data_hourly_range()
            >>> print(df.head())
                   date_time  temperature
            0 2024-01-01 00:00:00          20
            1 2024-01-01 01:00:00          19
        """
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "hourly": "temperature_2m",
            "forecast_days": 15
        }

        df = pd.DataFrame()
        
        forecast = await self.__fetch_data_(params=params, url=self.forecast_url)
        
        df['date_time'] = pd.to_datetime(forecast['hourly']['time'])
        df['temperature'] = forecast['hourly']['temperature_2m']
        df['temperature'] = df['temperature'].round(0).astype(int)
        return df
    
    async def get_data_daily_range(self, start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """
        Get daily temperature data (max and min) for the next 15 days.
        
        Args:
            start_date (str, optional): Start date in YYYY-MM-DD format. Defaults to "".
            end_date (str, optional): End date in YYYY-MM-DD format. Defaults to "".
            
        Returns:
            pd.DataFrame: DataFrame containing daily temperature data with columns:
                - date_time: datetime index
                - temperature: average temperature in Celsius (rounded to integer)
                
        Example:
            >>> df = await service.get_data_daily_range()
            >>> print(df.head())
                   date_time  temperature
            0 2024-01-01          22
            1 2024-01-02          21
        """
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "daily": "temperature_2m_max,temperature_2m_min",
            "forecast_days": 15
        }

        forecast = await self.__fetch_data_(params=params, url=self.forecast_url)
       
        df = pd.DataFrame({
            'date_time': pd.to_datetime(forecast['daily']['time']),
            'temp_max': forecast['daily']['temperature_2m_max'],
            'temp_min': forecast['daily']['temperature_2m_min']
        })
        df['temperature'] = (df['temp_max'] + df['temp_min']) / 2
        df['temperature'] = df['temperature'].round().astype(int)

        df = df.drop(columns=['temp_max', 'temp_min'])
        
        return df
    
    async def get_historical_data_daily(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get historical daily temperature data for a specific date range.
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: DataFrame containing historical daily temperature data with columns:
                - date_time: datetime index
                - temperature: average temperature in Celsius (rounded to integer)
                
        Example:
            >>> df = await service.get_historical_data_daily("2023-01-01", "2023-01-31")
            >>> print(df.head())
                   date_time  temperature
            0 2023-01-01          15
            1 2023-01-02          16
        """
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "daily": "temperature_2m_max,temperature_2m_min",
            "start_date": start_date,
            "end_date": end_date
        }
        
        forecast = await self.__fetch_data_(params=params, url=self.historical_url)
        
        df = pd.DataFrame({
            'date_time': pd.to_datetime(forecast['daily']['time']),
            'temp_max': forecast['daily']['temperature_2m_max'],
            'temp_min': forecast['daily']['temperature_2m_min']
        })
        df['temperature'] = (df['temp_max'] + df['temp_min']) / 2
        df['temperature'] = df['temperature'].round().astype(int)

        df = df.drop(columns=['temp_max', 'temp_min'])

        return df
    
    async def get_historical_data_hourly(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get historical hourly temperature data for a specific date range.
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: DataFrame containing historical hourly temperature data with columns:
                - date_time: datetime index
                - temperature: temperature in Celsius (rounded to integer)
                
        Example:
            >>> df = await service.get_historical_data_hourly("2023-01-01", "2023-01-02")
            >>> print(df.head())
                   date_time  temperature
            0 2023-01-01 00:00:00          14
            1 2023-01-01 01:00:00          13
        """
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "hourly": "temperature_2m",
            "start_date": start_date,
            "end_date": end_date
        }  

        df = pd.DataFrame()
        
        forecast = await self.__fetch_data_(params=params, url=self.historical_url)
        
        df['date_time'] = pd.to_datetime(forecast['hourly']['time'])
        df['temperature'] = forecast['hourly']['temperature_2m']
        df['temperature'] = df['temperature'].round(0).astype(int)
        return df
    
    async def get_past_days_daily(self, days: int) -> pd.DataFrame:
        """
        Get daily temperature data for past days.
        
        Args:
            days (int): Number of past days to retrieve
            
        Returns:
            pd.DataFrame: DataFrame containing daily temperature data for past days with columns:
                - date_time: datetime index
                - temperature: average temperature in Celsius (rounded to integer)
                
        Example:
            >>> df = await service.get_past_days_daily(2)
            >>> print(df)
                   date_time  temperature
            0 2024-01-01          18
            1 2024-01-02          19
        """
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "daily": "temperature_2m_max,temperature_2m_min",
            "past_days": days,
            "forecast_days": 0
        }

        forecast = await self.__fetch_data_(params=params, url=self.forecast_url)
        
        df = pd.DataFrame({
            'date_time': pd.to_datetime(forecast['daily']['time']),
            'temp_max': forecast['daily']['temperature_2m_max'],
            'temp_min': forecast['daily']['temperature_2m_min']
        })
        df['temperature'] = (df['temp_max'] + df['temp_min']) / 2
        df['temperature'] = df['temperature'].round().astype(int)

        df = df.drop(columns=['temp_max', 'temp_min'])

        return df
    
    async def get_past_days_hourly(self, days: int) -> pd.DataFrame:
        """
        Get hourly temperature data for past days.
        
        Args:
            days (int): Number of past days to retrieve
            
        Returns:
            pd.DataFrame: DataFrame containing hourly temperature data for past days with columns:
                - date_time: datetime index
                - temperature: temperature in Celsius (rounded to integer)
                
        Example:
            >>> df = await service.get_past_days_hourly(2)
            >>> print(df.head())
                   date_time  temperature
            0 2024-01-01 00:00:00          17
            1 2024-01-01 01:00:00          16
        """
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "hourly": "temperature_2m",
            "past_days": days,
            "forecast_days": 0
        }

        df = pd.DataFrame()
        
        forecast = await self.__fetch_data_(params=params, url=self.forecast_url)
        
        df['date_time'] = pd.to_datetime(forecast['hourly']['time'])
        df['temperature'] = forecast['hourly']['temperature_2m']
        df['temperature'] = df['temperature'].round(0).astype(int)
        
        return df