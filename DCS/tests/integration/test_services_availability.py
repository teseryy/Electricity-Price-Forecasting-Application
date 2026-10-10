"""
Integration tests for external services availability.

This module contains tests to verify the availability and basic functionality
of external services used by the application, including:
- Price service (OTE-CR)
- Temperature service (Meteostat)
- Climate standard service
"""

import pytest
import asyncio
import aiohttp
from meteostat import Daily
from datetime import datetime

@pytest.mark.asyncio
async def test_weather_api():
    """
    Test weather API availability.
    
    Verifies that the Open-Meteo weather service is accessible and responding.
    Checks the forecast endpoint for Prague location and validates the response format
    containing temperature data.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 50.0755,
        "longitude": 14.4378,
        "timezone": "Europe/Prague",
        "daily": "temperature_2m_max,temperature_2m_min",
        "forecast_days": 1
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            assert response.status == 200, f"Weather API is not available: {response.status}"
            data = await response.json()
            assert 'daily' in data, "Invalid weather API response format"
            assert 'temperature_2m_max' in data['daily'], "Missing maximum temperature data"
            assert 'temperature_2m_min' in data['daily'], "Missing minimum temperature data"


@pytest.mark.asyncio
async def test_price_api():
    """
    Test price API availability.
    
    Verifies that the OTE-CR price service is accessible and responding.
    Checks the WSDL endpoint for the PublicDataService.
    """
    url = "http://www.ote-cr.cz/services/PublicDataService/wsdl"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            assert response.status == 200, f"Price API is not available: {response.status}"
            content = await response.text()
            assert "<?xml" in content, "Invalid WSDL format"
            assert "wsdl:definitions" in content, "Invalid WSDL format"


@pytest.mark.asyncio
async def test_climate_api():
    """
    Test climate data API availability using Meteostat.
    
    Verifies that the Meteostat service is accessible and can provide
    climate data for a specific date range.
    """
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2)
    
    try:
        data = Daily('11520', start=start, end=end).fetch()
        assert not data.empty, "Received empty data from Meteostat"
        assert 'tmax' in data.columns, "Missing tmax column"
        assert 'tmin' in data.columns, "Missing tmin column"
    except Exception as e:
        pytest.fail(f"Error while fetching data from Meteostat: {str(e)}")