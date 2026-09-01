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
BRIGHTNESS_SLEEP = 0

# --- Colors ---
COLOR_BACKGROUND = "#f4f6f8"
COLOR_PRIMARY_TEXT = "#1e293b"
COLOR_MUTED_TEXT = "#64748b"
COLOR_NIGHT_BACKGROUND = "#000000"
COLOR_NIGHT_TEXT = "#33ff33"

# --- Typography ---
FONT_FAMILY_PRIMARY = "Segoe UI" if os.name == "nt" else "DejaVu Sans"
FONT_FAMILY_QUOTE = "Georgia" if os.name == "nt" else "DejaVu Serif"

# --- Widgets ---
ENABLE_COUNTERS_WIDGET = os.getenv("ENABLE_COUNTERS_WIDGET", "true").lower() == "true"

# --- Footer Text ---
FOOTER_TEXT_LINE1 = os.getenv("FOOTER_TEXT_LINE1", "A Ba T")
FOOTER_TEXT_LINE2 = os.getenv("FOOTER_TEXT_LINE2", "S Bi C")
FOOTER_FONT = (FONT_FAMILY_PRIMARY, 20)
FOOTER_NORMAL_FG = "#64748b"
FOOTER_HIGHLIGHT_FG = "#0f172a"
