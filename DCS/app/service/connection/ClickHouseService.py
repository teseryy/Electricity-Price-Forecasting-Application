import math
from datetime import datetime

import clickhouse_connect
import pandas as pd


class ClickHouseService:
    """
    Service for managing connections and operations with ClickHouse database.
    
    This service provides methods to connect to ClickHouse and perform database operations.
    It handles connection management and data retrieval from ClickHouse.
    
    Attributes:
        client: ClickHouse client instance
    """
    
    def __init__(self, host: str = "localhost", port: int = 8123, database: str = "default",
                 username: str = "default", password: str = "<PASSWORD>"):
        """
        Initialize the ClickHouseService and establish connection to the database.
        """
        self.client = clickhouse_connect.get_client(
            host=host,
            port=port,
            database=database,
            username=username,
            password=password
        )

    def insert_dataframe(self, table: str, df: pd.DataFrame):
        if df.empty:
            return

        df['inserted_at'] = datetime.now()

        chunk_size = 10_000
        num_chunks = math.ceil(len(df) / chunk_size)

        for i in range(num_chunks):
            chunk = df.iloc[i * chunk_size: (i + 1) * chunk_size]
            try:
                self.client.insert_df(table=table, df=chunk)
            except Exception as e:
                raise


    def close(self):
        self.client.close()