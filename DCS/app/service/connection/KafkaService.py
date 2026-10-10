import asyncio

from faststream.kafka import KafkaBroker

from app.model import DateMessage
from app.service.adapter import Adapter
from app.service.connection import ClickHouseService


class KafkaService:
    """
    Service for managing Kafka message processing and data synchronization.
    
    This service handles message processing from Kafka topics and coordinates data operations
    between Kafka and ClickHouse. It manages data initialization and nightly updates.
    
    Attributes:
        adapter (Adapter): Adapter instance for data operations
        broker (KafkaBroker): Kafka broker instance
        daily_table (str): Name of the daily data table
        hourly_table (str): Name of the hourly data table
        listen_topic (str): Kafka topic for receiving messages
        clickhouse_service (ClickHouseService): Service for ClickHouse operations
        confirm_topic (str): Kafka topic for sending confirmations
    """
    
    def __init__(self, adapter: Adapter, broker: KafkaBroker, clickhouse_service: ClickHouseService,
                 daily_table: str, hourly_table: str, listen_topic: str, confirm_topic: str):
        """
        Initialize the KafkaService with required dependencies.
        
        Args:
            adapter (Adapter): Adapter instance for data operations
            broker (KafkaBroker): Kafka broker instance
            clickhouse_service (ClickHouseService): Service for ClickHouse operations
            daily_table (str): Name of the daily data table
            hourly_table (str): Name of the hourly data table
            listen_topic (str): Kafka topic for receiving messages
            confirm_topic (str): Kafka topic for sending confirmations
        """
        self.adapter = adapter
        self.broker = broker
        self.daily_table = daily_table
        self.hourly_table = hourly_table
        self.listen_topic = listen_topic
        self.clickhouse_service = clickhouse_service
        self.confirm_topic = confirm_topic
        self.__register_handlers()

    def __register_handlers(self):
        """
        Register message handlers for Kafka topics.
        Sets up the subscriber for the listen topic.
        """
        self.broker.subscriber(self.listen_topic)(self.process_data)


    async def send_data(self, mode: str, timeframe: str, date: str):
        """
        Send data to ClickHouse based on mode and timeframe.
        
        Args:
            mode (str): Operation mode ('init' or 'night')
            timeframe (str): Data timeframe ('daily' or 'hourly')
            date (str): Target date in YYYY-MM-DD format
        """
        table = ""
        df = None

        if mode == "init":
            if timeframe == "daily":
                df = await self.adapter.initialize_daily(date)
                table = self.daily_table
            elif timeframe == "hourly":
                df = await self.adapter.initialize_hourly(date)
                table = self.hourly_table
        elif mode == "night":
            if timeframe == "daily":
                df = await self.adapter.night_get_daily(date)
                table = self.daily_table
            elif timeframe == "hourly":
                df = await self.adapter.night_get_hourly(date)
                table = self.hourly_table

        if df is not None and table:
            await asyncio.to_thread(self.clickhouse_service.insert_dataframe, table, df)

    async def process_data(self, data: dict):
        """
        Process incoming data message and trigger data operations.
        
        Args:
            data (dict): Message data containing mode and date
        """
        msg = DateMessage(**data)

        await self.send_data(msg.mode, "daily", msg.date)
        await self.send_data(msg.mode, "hourly", msg.date)

        await self.broker.publish(
            {"status": "completed", "date": msg.date},
            topic=self.confirm_topic)

