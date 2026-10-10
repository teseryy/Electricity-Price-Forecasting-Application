from pydantic import BaseModel


class DateMessage(BaseModel):
    """
    Pydantic model for validating Kafka messages.
    
    This class is used to validate and parse incoming messages from Kafka topic.
    It ensures that messages contain the required fields with correct types.
    
    Attributes:
        date (str): Target date for data processing in YYYY-MM-DD format.
                   Used to specify which date's data should be processed.
        mode (str): Operation mode for data processing.
                   Valid values are:
                   - 'init': Initial data loading mode
                   - 'night': Nightly update mode
                   
    Example:
        Valid message format:
        {
            "date": "2024-03-20",
            "mode": "init"
        }
    """
    
    date: str
    mode: str