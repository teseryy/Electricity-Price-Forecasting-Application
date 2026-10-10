from pydantic import BaseModel


class Message(BaseModel):
    """
    Message model for Kafka communication.

    This model represents a message structure used for communication between services
    through Kafka. It contains information about the status of an operation and
    the date for which the operation should be performed.

    Attributes:
        status (str): Current status of the operation (e.g., 'start', 'complete', 'error')
        date (str): Target date for the operation in format 'YYYY-MM-DD'
    """
    status: str
    date: str