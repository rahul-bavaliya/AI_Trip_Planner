import os
from typing import List
from dotenv import load_dotenv
from langchain.tools import tool

from logger.logging import get_logger
from utils.weather_info import WeatherForecastTool

logger = get_logger(__name__)

class WeatherInfoTool:
    def __init__(self):
        load_dotenv()
        self.api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
        self.weather_service = WeatherForecastTool(self.api_key)
        self.weather_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """Setup all tools for the weather forecast tool"""

        @tool
        def get_current_weather(city: str) -> str:
            """Get current weather for a city"""
            logger.debug(f"City: {city}")
            weather_data = self.weather_service.get_current_weather(city)
            # logger.debug(f"Weather Data: {weather_data}")

            features = weather_data.get("features", [])
            if features:
                props = features[0].get("properties", {})
                current = props.get("currentConditions", {})

                # Extract temperature
                temp_obj = current.get("temperature", {})
                # Safely gets 'en' value inside 'value', falls back to 'fr', or None if missing
                temp = temp_obj.get("value", {}).get("en") or temp_obj.get("value", {}).get("fr")
                temp_str = f"{temp}°C" if temp is not None else "N/A"
                logger.debug(f"Temprature: {temp_str} | Place: {city}")

                # Extract condition summary
                condition = current.get("condition", "N/A")
                if isinstance(condition, dict):
                    condition = condition.get("en", "N/A")

                location_name = props.get("name", {}).get("en", city)
                return f"Current weather in {location_name}: {temp_str}, {condition}"

            return f"Could not fetch weather for {city}"

        @tool
        def get_weather_forecast(city: str) -> str:
            """Get weather forecast for a city"""
            logger.debug(f"City: {city}")
            forecast_data = self.weather_service.get_forecast_weather(city)

            features = forecast_data.get("features", [])
            if features:
                props = features[0].get("properties", {})
                forecasts = props.get("forecastGroup", {}).get("forecasts", [])

                if forecasts:
                    forecast_summary = []
                    for item in forecasts:
                        period = item.get("period", {}).get("en", "Upcoming")
                        summary = item.get("textSummary", {}).get("en", "")
                        temp_summary = item.get("temperatures", {}).get("textSummary", {}).get("en", "")
                        
                        line = f"{period}: {summary}"
                        if temp_summary:
                            line += f" ({temp_summary})"
                        forecast_summary.append(line)

                    location_name = props.get("name", {}).get("en", city)
                    return f"Weather forecast for {location_name}:\n" + "\n".join(forecast_summary)

            return f"Could not fetch forecast for {city}"

        return [get_current_weather, get_weather_forecast]