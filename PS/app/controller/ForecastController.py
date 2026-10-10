from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.model import DatetimeRequest, DatePeriodRequest
from app.service import Facade
from app.Depedencies import get_facade

router = APIRouter(prefix="/forecast",
                   tags=["Forecast"])

@router.get("/daily")
async def get_daily(facade: Facade = Depends(get_facade)):
    """
    Get all daily forecast data.

    This endpoint retrieves all available daily forecast data from the system.
    The data is returned as a list of records containing date, price, and temperature.

    Args:
        facade (Facade): Injected Facade service instance

    Returns:
        dict: Either a list of forecast records or a message indicating no data is available
    """
    df = await facade.get_forecast_data_daily()

    if df is None or df.empty:
        return {"message": "No data available"}

    return df.to_dict(orient="records")

@router.get("/hourly")
async def get_hourly(facade: Facade = Depends(get_facade)):
    """
    Get all hourly forecast data.

    This endpoint retrieves all available hourly forecast data from the system.
    The data is returned as a list of records containing datetime, price, and temperature.

    Args:
        facade (Facade): Injected Facade service instance

    Returns:
        dict: Either a list of forecast records or a message indicating no data is available
    """
    df = await facade.get_forecast_data_hourly()

    if df is None or df.empty:
        return {"message": "No data available"}

    return df.to_dict(orient="records")

@router.get("/daily/date")
async def get_daily_date(request: DatetimeRequest, facade: Facade = Depends(get_facade)):
    """
    Get daily forecast data for a specific date.

    This endpoint retrieves daily forecast data for the specified date.
    The request body is validated using DatetimeRequest model.

    Args:
        request (DatetimeRequest): Request containing the target date
        facade (Facade): Injected Facade service instance

    Returns:
        dict: Either a list of forecast records for the specified date or a message indicating no data is available
    """
    df = await facade.get_forecast_by_day_daily(str(request.datetime))

    if df is None or df.empty:
        return {"message": "No data available"}

    return df.to_dict(orient="records")

@router.get("/hourly/date")
async def get_hourly_date(request: DatetimeRequest, facade: Facade = Depends(get_facade)):
    """
    Get hourly forecast data for a specific date.

    This endpoint retrieves hourly forecast data for the specified date.
    The request body is validated using DatetimeRequest model.

    Args:
        request (DatetimeRequest): Request containing the target date
        facade (Facade): Injected Facade service instance

    Returns:
        dict: Either a list of forecast records for the specified date or a message indicating no data is available
    """
    df = await facade.get_forecast_by_day_hourly(str(request.datetime))

    if df is None or df.empty:
        return {"message": "No data available"}

    return df.to_dict(orient="records")

def validate_date(date_str: str) -> str:
    """
    Validate date string format.

    This helper function validates that the provided date string is in the correct format (YYYY-MM-DD).
    Raises an HTTPException if the format is invalid.

    Args:
        date_str (str): Date string to validate

    Returns:
        str: Validated date string

    Raises:
        HTTPException: If the date format is invalid
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be in YYYY-MM-DD format")

@router.get("/daily/oldData")
async def get_daily_old_data(
    start_date: str,
    end_date: str,
    facade: Facade = Depends(get_facade)
):
    """
    Get historical daily data for a date range.

    This endpoint retrieves historical daily data between the specified start and end dates.
    Both dates are validated to ensure they are in the correct format (YYYY-MM-DD).

    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        facade (Facade): Injected Facade service instance

    Returns:
        dict: Either a list of historical records or a message indicating no data is available

    Raises:
        HTTPException: If either date is in an invalid format
    """
    validate_date(start_date)
    validate_date(end_date)

    df = await facade.get_hist_data_daily(start_date, end_date)

    if df is None or df.empty:
        return {"message": "No data available"}

    return df.to_dict(orient="records")

@router.get("/hourly/oldData")
async def get_hourly_old_data(
    start_date: str,
    end_date: str,
    facade: Facade = Depends(get_facade)
):
    """
    Get historical hourly data for a date range.

    This endpoint retrieves historical hourly data between the specified start and end dates.
    Both dates are validated to ensure they are in the correct format (YYYY-MM-DD).

    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        facade (Facade): Injected Facade service instance

    Returns:
        dict: Either a list of historical records or a message indicating no data is available

    Raises:
        HTTPException: If either date is in an invalid format
    """
    validate_date(start_date)
    validate_date(end_date)

    df = await facade.get_hist_data_hourly(start_date, end_date)

    if df is None or df.empty:
        return {"message": "No data available"}

    return df.to_dict(orient="records")