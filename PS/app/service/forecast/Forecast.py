import pandas as pd
from prophet import Prophet

class Forecast:
    """
    A class for time series forecasting using Meta Prophet.

    This class implements price forecasting with temperature as a regressor.
    It uses Prophet's capabilities for handling seasonality and holidays,
    specifically configured for Czech Republic holidays.

    Attributes:
        model (Prophet): The Prophet model instance with configured seasonality
                        and holiday settings.
    """
    def __init__(self):
        """
        Initialize the Forecast model with Prophet configuration.

        Sets up a Prophet model with yearly, weekly, and daily seasonality,
        and adds Czech Republic holidays as a feature.
        """
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True
        )
        self.model.add_country_holidays(country_name='CZ')

    def __prepare_data(self, df):
        """
        Prepare input data for Prophet model.

        Converts the input DataFrame to Prophet's required format,
        including datetime conversion and feature preparation.

        Args:
            df (pd.DataFrame): Input DataFrame with columns:
                - date: datetime or string in datetime format
                - price: float, target variable
                - temperature: float, regressor variable

        Returns:
            pd.DataFrame: Prepared DataFrame with Prophet's required format:
                - ds: datetime column
                - y: target variable (price)
                - temperature: regressor variable
        """
        prophet_df = pd.DataFrame()
        prophet_df['ds'] = pd.to_datetime(df['date'])
        prophet_df['y'] = df['price']

        prophet_df['temperature'] = df['temperature']

        return prophet_df

    def train_model(self, df):
        """
        Train the Prophet model on historical data.

        Args:
            df (pd.DataFrame): Training data with columns:
                - date: datetime or string in datetime format
                - price: float, target variable
                - temperature: float, regressor variable

        Returns:
            self: Returns self for method chaining
        """
        prepared_df = self.__prepare_data(df)

        self.model.add_regressor('temperature')

        self.model.fit(prepared_df)

        return self

    def predict(self, df: pd.DataFrame):
        """
        Generate price forecasts using the trained model.

        Args:
            df (pd.DataFrame): Input data for prediction with columns:
                - date: datetime or string in datetime format
                - price: can be None (not used for prediction)
                - temperature: float, required for prediction

        Returns:
            pd.DataFrame: Forecast results with columns:
                - date: datetime
                - price: predicted price
                - lower_bound: lower bound of prediction interval
                - upper_bound: upper bound of prediction interval
                - temperature: temperature value for the prediction
        """
        future_df = self.__prepare_data(df)
        future_df = future_df[['ds', 'temperature']]

        temperature_map = future_df[['ds', 'temperature']].set_index('ds')['temperature']

        future_df = future_df.sort_values(by='ds')

        print(future_df)

        forecast = self.model.predict(future_df)

        components = self.model.predictive_samples(future_df)
        print("Predictive samples (components):")
        # Выводим ключи и первые значения (так как это dict)
        for key, value in list(components.items())[:5]:  # Первые 5 элементов
            print(f"{key}: {value[:5]}...")

        # Тренд
        trend = forecast[['ds', 'trend']]
        print("Trend component:")
        print(trend.head())

        # Сезонные компоненты (если они включены)
        seasonal_components = forecast[['ds', 'yearly', 'weekly', 'daily']].dropna(axis=1, how='all')
        if not seasonal_components.empty:
            print("Seasonal components:")
            print(seasonal_components.head())

        # Интервалы уверенности
        confidence_intervals = forecast[['ds', 'yhat_lower', 'yhat_upper']]
        print("Confidence intervals:")
        print(confidence_intervals.head())

        # Параметры модели (если доступны)
        params = self.model.params
        if params is not None:
            print("Model parameters:")
            print(params)

        result = pd.DataFrame()
        result['date'] = forecast['ds']
        result['price'] = forecast['yhat']
        result['lower_bound'] = forecast['yhat_lower']
        result['upper_bound'] = forecast['yhat_upper']

        result = result.sort_values(by='date')
        result['temperature'] = result['date'].map(temperature_map)

        print("res: ")
        print(result)

        return result
