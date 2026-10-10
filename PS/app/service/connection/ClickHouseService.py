import clickhouse_connect
import pandas as pd


class ClickHouseService:
    """
    Service class for interacting with ClickHouse database.

    This class provides methods for retrieving data from ClickHouse database,
    including training data, forecast data, and historical data. It handles
    connection management and query execution.

    Attributes:
        client: ClickHouse client instance for database operations
    """

    def __init__(self, host: str = "localhost", port: int = 8123, database: str = "default",
                 username: str = "default", password: str = "<PASSWORD>"):
        """
        Initialize ClickHouse connection.

        Args:
            host (str): ClickHouse server hostname. Defaults to "localhost".
            port (int): ClickHouse server port. Defaults to 8123.
            database (str): Database name. Defaults to "default".
            username (str): Username for authentication. Defaults to "default".
            password (str): Password for authentication. Defaults to "<PASSWORD>".
        """
        self.client = clickhouse_connect.get_client(
            host=host,
            port=port,
            database=database,
            username=username,
            password=password
        )

    def __get_data(self, query: str) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame.

        Args:
            query (str): SQL query to execute.

        Returns:
            pd.DataFrame: Query results as pandas DataFrame.

        Raises:
            Exception: If query execution fails.
        """
        try:
            result = self.client.query_df(query)
            return result
        except Exception as e:
            raise

    def get_train_data(self, table: str, date: str) -> pd.DataFrame:
        """
        Retrieve training data from specified table up to given date.

        Args:
            table (str): Name of the table to query.
            date (str): Cutoff date in format 'YYYY-MM-DD'.

        Returns:
            pd.DataFrame: DataFrame containing:
                - date: Date of the record
                - price: Latest price value for each date
                - temperature: Latest temperature value for each date
        """
        query = f"""
            SELECT 
                date,
                argMax(price, inserted_at) AS price,
                argMax(temperature, inserted_at) AS temperature
            FROM '{table}'
            WHERE date < '{date}'
            GROUP BY date
        """

        return self.__get_data(query)

    def get_forecast_data(self, table: str, date: str) -> pd.DataFrame:
        """
        Retrieve forecast data from specified table starting from given date.

        Args:
            table (str): Name of the table to query.
            date (str): Start date in format 'YYYY-MM-DD'.

        Returns:
            pd.DataFrame: DataFrame containing:
                - date: Date of the record
                - price: Latest price value for each date
                - temperature: Latest temperature value for each date
        """
        query = f"""
            SELECT 
                date,
                argMax(price, inserted_at) AS price,
                argMax(temperature, inserted_at) AS temperature
            FROM '{table}'
            WHERE date >= '{date}'
            GROUP BY date
        """

        return self.__get_data(query)

    def get_old_data(self, table: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Retrieve historical data from specified table within date range.

        Args:
            table (str): Name of the table to query.
            start_date (str): Start date in format 'YYYY-MM-DD'.
            end_date (str): End date in format 'YYYY-MM-DD'.

        Returns:
            pd.DataFrame: DataFrame containing:
                - date: Date of the record
                - price: Latest price value for each date
                - temperature: Latest temperature value for each date
        """
        query = f"""
            SELECT 
                date,
                argMax(price, inserted_at) AS price,
                argMax(temperature, inserted_at) AS temperature
            FROM '{table}'
            WHERE date < '{end_date}' AND date >= '{start_date}'
            GROUP BY date
        """

        return self.__get_data(query)

    def close(self):
        """
        Close the ClickHouse connection.

        This method should be called when the service is no longer needed
        to properly clean up resources.
        """
        self.client.close()
