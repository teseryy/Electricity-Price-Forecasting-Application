import httpx
import pandas as pd
from zeep import AsyncClient
from zeep.transports import AsyncTransport


class PriceService():
    """
    Service for retrieving electricity price data from OTE API.
    
    This service provides methods to fetch electricity price data in both hourly and daily formats.
    It uses the OTE API to get price information for the Czech electricity market.
    
    Attributes:
        wsdl (str): WSDL URL for the OTE PublicDataService
    """
    
    def __init__(self):
        """
        Initialize the PriceService with WSDL configuration for OTE API.
        """
        self.wsdl = 'http://www.ote-cr.cz/services/PublicDataService/wsdl'

    async def get_data_hourly_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get hourly electricity price data for the specified date range.
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: DataFrame containing hourly price data with columns:
                - date_time: datetime index
                - price: electricity price in EUR/MWh
        """
        async with httpx.AsyncClient(verify=False, timeout=180.0) as http_client:
            transport = AsyncTransport(client=http_client)
            client = AsyncClient(self.wsdl, transport=transport)
            response = await client.service.GetDamPriceE(
                StartDate=start_date,
                EndDate=end_date,
                StartHour=1,
                EndHour=24,
                InEur=False
            )

            parsed_data = []

            for item in response:
                date = item.Date
                hour = item.Hour
                price = item.Price

                date_time = pd.to_datetime(date) + pd.to_timedelta(hour - 1, unit='h')
                parsed_data.append({
                    'date_time': date_time,
                    'price': float(price)
                })
                
            df = pd.DataFrame(parsed_data)
            return df
        