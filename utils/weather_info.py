import requests
from logger.logging import get_logger

logger = get_logger(__name__)

class WeatherForecastTool:
    def __init__(self, api_key: str = None):
        # API key kept for signature compatibility if passed from caller
        self.base_url = "https://api.weather.gc.ca/collections"

    def get_current_weather(self, place: str) -> dict:
        """Get current realtime weather of a Canadian city/place"""
        try:
            params = {
                "q": place,
                "f": "json",
                "limit": 1
            }
            url = f"{self.base_url}/citypageweather-realtime/items"
            response = requests.get(url, params=params, timeout=10)
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return {}

    def get_forecast_weather(self, place: str) -> dict:
        """Get forecast weather data of a Canadian city/place"""
        try:
            params = {
                "q": place,
                "f": "json",
                "limit": 1
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            logger.error(f"Error fetching forecast weather: {e}")
            return {}