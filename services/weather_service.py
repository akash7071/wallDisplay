import requests
from datetime import datetime
from config import OPENWEATHER_API_KEY, CITY_NAME, COUNTRY_CODE

def fetch_weather():
    if not all([OPENWEATHER_API_KEY, CITY_NAME, COUNTRY_CODE]):
        return []

    # Endpoint for CURRENT weather (The real "Now")
    current_url = "http://api.openweathermap.org/data/2.5/weather"
    # Endpoint for FORECAST (The future blocks)
    forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
    
    params = {
        "q": f"{CITY_NAME},{COUNTRY_CODE}",
        "appid": OPENWEATHER_API_KEY,
        "units": "imperial"
    }

    try:
        # 1. Get CURRENT conditions
        curr_r = requests.get(current_url, params=params, timeout=5)
        curr_data = curr_r.json()
        
        # 2. Get FORECAST conditions
        fore_r = requests.get(forecast_url, params=params, timeout=5)
        fore_data = fore_r.json()

        results = []
        
        # Add the true CURRENT weather first
        results.append({
            "time": datetime.fromtimestamp(curr_data["dt"]),
            "temp": int(curr_data["main"]["temp"]),
            "icon": curr_data["weather"][0]["icon"]
        })

        # Add the next 3 blocks from the forecast
        # We start from [0] in the forecast list because they are all in the future
        for item in fore_data["list"][:3]:
            results.append({
                "time": datetime.fromtimestamp(item["dt"]),
                "temp": int(item["main"]["temp"]),
                "icon": item["weather"][0]["icon"]
            })

        return results

    except Exception as e:
        print(f"Weather fetch error: {e}")
        return []