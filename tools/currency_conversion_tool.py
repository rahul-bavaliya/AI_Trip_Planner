import os
from utils.currency_converter import CurrencyConverter
from typing import List
from langchain.tools import tool
from dotenv import load_dotenv


""" Currency conversion tool for handling currency conversion logic """
class CurrencyConverterTool:
    
    """Initialize the CurrencyConverterTool with API key and setup tools"""
    def __init__(self):
        # CurrencyConverter instance for handling currency conversion logic
        self.currency_service = CurrencyConverter()
        
        # Setup tools for the currency converter tool
        self.currency_converter_tool_list = self._setup_tools()

    """ Setup all tools for the currency converter tool"""
    def _setup_tools(self) -> List:
        
        # Tool for converting currency from one type to another
        @tool
        def convert_currency(amount:float, from_currency:str, to_currency:str):
            # Convert the amount from one currency to another using the CurrencyConverter service
            return self.currency_service.convert(amount, from_currency, to_currency)
        # Return the list of tools for the currency converter tool
        return [convert_currency]