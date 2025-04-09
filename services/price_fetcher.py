import requests

def get_xrp_price():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=ripple&vs_currencies=usd'
    try:
        response = requests.get(url)
        data = response.json()
        return data['ripple']['usd']
    except Exception as e:
        print("Error fetching price:", e)
        return None

