import requests

class CurrencyConverter:
    def __init__(self):
        # Using recent=1 fetches the latest available observation
        self.base_url = "https://www.bankofcanada.ca/valet/observations/{series_key}/json?recent=1"

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Convert an amount between CAD and a foreign currency using Bank of Canada rates.
        Example: convert(100, "USD", "CAD") or convert(100, "CAD", "USD")
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency == to_currency:
            return amount

        # Bank of Canada series keys follow the format FX<FOREIGN>CAD (e.g., FXUSDCAD)
        series_key = f"FX{from_currency}{to_currency}"

        url = self.base_url.format(series_key=series_key)
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception("API call failed:", response.text)

        data = response.json()
        observations = data.get("observations", [])

        if not observations:
            raise ValueError(f"No rate data available for {series_key}.")

        # Get the latest observation object
        latest_obs = observations[-1]

        if series_key not in latest_obs:
            raise ValueError(f"Series key {series_key} not found in response.")

        # Extract the value string 'v' and convert to float
        rate = float(latest_obs[series_key]["v"])

        # FXUSDCAD = 1.4088 means 1 USD = 1.4088 CAD
        return amount * rate