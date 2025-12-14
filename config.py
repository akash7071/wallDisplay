import os
from dotenv import load_dotenv

load_dotenv()

# --- Google Keep ---
KEEP_USER = os.getenv("KEEP_USER")
MASTER_TOKEN = os.getenv("MASTER_TOKEN")

# --- Weather ---
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY_NAME = os.getenv("CITY_NAME")
COUNTRY_CODE = os.getenv("COUNTRY_CODE")

# --- Display Power ---
DISPLAY_POWER_ON = 1
DISPLAY_POWER_OFF = 4

# --- Time Rules ---
SLEEP_START_HOUR = 22
SLEEP_END_HOUR = 8
DIM_HOUR = 18

# --- Brightness ---
BRIGHTNESS_DAY = 100
BRIGHTNESS_EVENING = 20
BRIGHTNESS_SLEEP = 1

# --- Colors ---
COLOR_BACKGROUND = "#f2f2f2"
COLOR_NIGHT_BACKGROUND = "black"
COLOR_NIGHT_TEXT = "#33ff33"
