import json
from datetime import datetime

import pandas as pd
import redis.asyncio as redis
from redis.asyncio.lock import Lock

class RedisService:
    """
    A service class for handling Redis operations with thread-safe data access.

    This class provides methods for storing and retrieving forecast data from Redis,
    with built-in locking mechanism to ensure thread safety during concurrent operations.
    It handles data serialization/deserialization and maintains data consistency.

    Attributes:
        client (redis.Redis): Redis client instance with automatic response decoding.
    """
    def __init__(self,
                 host: str = "localhost", port: int = 6379, db: int = 0):
        """
        Initialize Redis connection.

        Args:
            host (str, optional): Redis server hostname. Defaults to "localhost".
            port (int, optional): Redis server port. Defaults to 6379.
            db (int, optional): Redis database number. Defaults to 0.
        """
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    async def insert_data(self, table_name: str, df: pd.DataFrame):
        """
        Insert or update forecast data in Redis with thread safety.

        This method uses Redis locks to ensure thread safety during data insertion.
        It first deletes existing data for the table, then inserts new data.

        Args:
            table_name (str): Name of the Redis hash table to store data.
            df (pd.DataFrame): DataFrame containing forecast data with columns:
                - date: datetime or string in datetime format
                - price: float, forecasted price
                - temperature: float, temperature value
                - lower_bound: float, lower bound of prediction interval
                - upper_bound: float, upper bound of prediction interval
        """
        lock = Lock(self.client, f"lock:{table_name}", timeout=10)

        async with lock:
            await self.client.delete(table_name)

            async with self.client.pipeline() as pipe:
                for _, row in df.iterrows():
                    pipe.hset(
                        table_name,
                        str(row["date"]),
                        json.dumps({
                            "price": row["price"],
                            "temperature": row["temperature"],
                            "lower_bound": row["lower_bound"],
                            "upper_bound": row["upper_bound"]
                        })
                    )
                await pipe.execute()

    async def get_table(self, table_name: str) -> pd.DataFrame:
        """
        Retrieve all forecast data from a Redis table with thread safety.

        Args:
            table_name (str): Name of the Redis hash table to retrieve data from.

        Returns:
            pd.DataFrame: DataFrame containing all forecast data with columns:
                - date: datetime
                - price: float
                - temperature: float
                - lower_bound: float
                - upper_bound: float

        Raises:
            Exception: If unable to acquire Redis lock.
        """
        lock = Lock(self.client, f"lock:{table_name}")
        acquired = await lock.acquire(blocking=True)
        try:
            if acquired:
                raw_data = await self.client.hgetall(table_name)
                if not raw_data:
                    return pd.DataFrame()
                data = [{"date": k, **json.loads(v)} for k, v in raw_data.items()]

                df = pd.DataFrame(data)
                df = df.sort_values(by='date')

                return df
            else:
                raise Exception("Could not acquire Redis lock")
        finally:
            if acquired:
                await lock.release()

    async def get_by_date(self, table_name: str, date: str) -> pd.DataFrame:
        """
        Retrieve forecast data for a specific date from Redis with thread safety.

        Args:
            table_name (str): Name of the Redis hash table to retrieve data from.
            date (str): Date to retrieve data for (format: YYYY-MM-DD).

        Returns:
            pd.DataFrame: DataFrame containing forecast data for the specified date with columns:
                - date: datetime
                - price: float
                - temperature: float
                - lower_bound: float
                - upper_bound: float

        Raises:
            Exception: If unable to acquire Redis lock.
        """
        lock = Lock(self.client, f"lock:{table_name}")
        acquired = await lock.acquire(blocking=True)

        try:
            if acquired:
                raw_data = await self.client.hget(table_name, date)
                if not raw_data:
                    return pd.DataFrame()
                data = [{"date": date, **json.loads(raw_data)}]
                return pd.DataFrame(data)
            else:
                raise Exception("Could not acquire Redis lock")
        finally:
            if acquired:
                await lock.release()

    async def close(self):
        """
        Close the Redis connection.

        This method should be called when the service is no longer needed
        to properly clean up resources.
        """
        await self.client.close()

