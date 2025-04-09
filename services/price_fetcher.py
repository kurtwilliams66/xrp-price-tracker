import requests
from datetime import datetime


def get_xrp_price():
    """
    Fetches the current XRP price in USD.
    Returns:
        float: Current price rounded to 4 decimals or None on failure.
    """
    url = "https://min-api.cryptocompare.com/data/price?fsym=XRP&tsyms=USD"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        price = data.get("USD")
        if price is not None:
            return round(price, 4)
        else:
            print("XRP price not found in response.")
            return None
    except requests.RequestException as e:
        print("Error fetching XRP price:", e)
        return None


def get_price_history(range="1D"):
    """
    Fetches historical XRP price data depending on the range selected.
    Args:
        range (str): One of ["1D", "1W", "1M", "1Y"]
    Returns:
        list of tuples: Each tuple contains (timestamp, close_price)
    """
    url_map = {
        "1D": "https://min-api.cryptocompare.com/data/v2/histominute?fsym=XRP&tsym=USD&limit=1440",  # 1 day, minute data
        "1W": "https://min-api.cryptocompare.com/data/v2/histohour?fsym=XRP&tsym=USD&limit=168",    # 1 week, hourly data
        "1M": "https://min-api.cryptocompare.com/data/v2/histoday?fsym=XRP&tsym=USD&limit=30",      # 1 month, daily data
        "1Y": "https://min-api.cryptocompare.com/data/v2/histoday?fsym=XRP&tsym=USD&limit=365",     # 1 year, daily data
    }

    url = url_map.get(range.upper())
    if not url:
        raise ValueError(f"Invalid range '{range}'. Use one of: 1D, 1W, 1M, 1Y")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        raw_data = response.json()["Data"]["Data"]
        return [(point["time"], point["close"]) for point in raw_data]
    except requests.RequestException as e:
        print(f"Error fetching XRP historical data for range '{range}':", e)
        return []
    except (KeyError, TypeError) as e:
        print("Unexpected response format:", e)
        return []
