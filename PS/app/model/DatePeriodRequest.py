from datetime import datetime
from pydantic import BaseModel


class DatePeriodRequest(BaseModel):
    """
    Request model for date period operations.

    This model represents a request structure for operations that require
    a date range, such as retrieving historical data or generating forecasts
    for a specific time period. It is used for validating HTTP request bodies
    in FastAPI endpoints.

    Attributes:
        start_date (datetime): Start date of the period
        end_date (datetime): End date of the period

    Note:
        Both dates should be in datetime format and end_date should be
        greater than or equal to start_date.
        The model automatically validates the request body format and
        converts string dates to datetime objects.
    """
    start_date: datetime
    end_date: datetime