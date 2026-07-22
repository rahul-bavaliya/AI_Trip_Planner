import os
from dotenv import load_dotenv
load_dotenv()
from langchain.tools import tool
from langchain_community.utilities.alpha_vantage import AlphaVantageAPIWrapper


""" Calculate the multiply of two integers """
@tool
def multiply(a: int, b: int) -> int:
    """
    Multiply two integers.

    Args:
        a (int): The first integer.
        b (int): The second integer.

    Returns:
        int: The product of a and b.
    """
    return a * b


""" Calculate the addition of two integers """
@tool
def add(a: int, b: int) -> int:
    """
    Add two integers.

    Args:
        a (int): The first integer.
        b (int): The second integer.

    Returns:
        int: The sum of a and b.
    """
    return a + b

""" Calculate the subtraction of two integers """
@tool
def substract(a: int, b: int) -> int:
    """
    Substract two integers.

    Args:
        a (int): The first integer.
        b (int): The second integer.

    Returns:
        int: The difference of a and b.
    """
    return a - b


""" Calculate the division of two integers """
@tool
def divide(a: int, b: int) -> int:
    """
    Divide two integers.

    Args:
        a (int): The first integer.
        b (int): The second integer.

    Returns:
        int: The quotient of a and b.
    """
    return a / b

""" Calculate the percentage of a with respect to b """
@tool
def perc(a: int, b: int) -> int:
    """
    Calculate the percentage of a with respect to b.

    Args:
        a (int): The first integer.
        b (int): The second integer.

    Returns:
        int: The percentage of a with respect to b.
    """
    return (a / b) * 100

""" Currency conversion tool for handling currency conversion logic """
@tool
def currency_converter(from_curr: str, to_curr: str, value: float)->float:
    alpha_vantage = AlphaVantageAPIWrapper()
    response = alpha_vantage._get_exchange_rate(from_curr, to_curr)
    exchange_rate = response['Realtime Currency Exchange Rate']['5. Exchange Rate']
    return value * float(exchange_rate)