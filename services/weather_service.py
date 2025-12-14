import requests
from datetime import datetime
from config import OPENWEATHER_API_KEY, CITY_NAME, COUNTRY_CODE

def fetch_weather():
    if not all([OPENWEATHER_API_KEY, CITY_NAME, COUNTRY_CODE]):
        return []

    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": f"{CITY_NAME},{COUNTRY_CODE}",
        "appid": OPENWEATHER_API_KEY,
        "units": "imperial"
    }

    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()

        return [
            {
                "time": datetime.fromtimestamp(item["dt"]),
                "temp": int(item["main"]["temp"]),
                "icon": item["weather"][0]["icon"]
            }
            for item in data["list"][:4]
        ]
    except Exception as e:
        print(f"Weather fetch error: {e}")
        return []
