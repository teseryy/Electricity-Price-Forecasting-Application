from pydantic import BaseModel
from datetime import datetime

class DatetimeRequest(BaseModel):
    """
    Request model for single datetime operations.

    This model represents a request structure for operations that require
    a single datetime value, such as retrieving data for a specific point
    in time or generating forecasts for a specific date. It is used for
    validating HTTP request bodies in FastAPI endpoints.

    Attributes:
        datetime (datetime): Target datetime for the operation

    Note:
        The datetime should be in the correct timezone and format
        as expected by the operation.
        The model automatically validates the request body format and
        converts string datetime to datetime object.
    """
    datetime: datetime