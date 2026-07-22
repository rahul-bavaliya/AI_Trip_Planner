import os
from utils.currency_converter import CurrencyConverter
from typing import List
from langchain.tools import tool
from dotenv import load_dotenv


""" Currency conversion tool for handling currency conversion logic """
class CurrencyConverterTool:
    
    """Initialize the CurrencyConverterTool with API key and setup tools"""
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Get the API key for currency conversion from environment variables
        self.api_key = os.environ.get("EXCHANGE_RATE_API_KEY")
        
        # CurrencyConverter instance for handling currency conversion logic
        self.currency_service = CurrencyConverter(self.api_key)
        
        # Setup tools for the currency converter tool
        self.currency_converter_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """Setup all tools for the currency converter tool"""
        @tool
        def convert_currency(amount:float, from_currency:str, to_currency:str):
            """Convert amount from one currency to another"""
            return self.currency_service.convert(amount, from_currency, to_currency)
        
        return [convert_currency]