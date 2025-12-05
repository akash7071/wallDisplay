import os
import random
import gkeepapi
import tkinter as tk
from datetime import datetime, timedelta, time
from dotenv import load_dotenv
import subprocess
import requests 

# Load environment variables from the .env file
load_dotenv()

# -------------------------
# CONFIGURATION
# -------------------------
USERNAME = os.environ.get("KEEP_USER")
MASTER_TOKEN = os.environ.get("MASTER_TOKEN")

# --- Authentication Check ---
if not USERNAME or not MASTER_TOKEN:
    raise ValueError("KEEP_USER or MASTER_TOKEN not found in environment variables. Check your .env file.")

# --- Display & Time Config ---
DISPLAY_POWER_ON = 1
DISPLAY_POWER_OFF = 4
SLEEP_START_HOUR = 22  # 10 PM
SLEEP_END_HOUR = 8     # 8 AM
DIM_HOUR = 18          # 6 PM
BRIGHTNESS_DAY = 100
BRIGHTNESS_EVENING = 10

# --- Weather Config ---
WEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
WEATHER_CITY = os.environ.get("CITY_NAME")
WEATHER_COUNTRY = os.environ.get("COUNTRY_CODE")


# -------------------------
# GOOGLE KEEP LOGIN
# -------------------------
keep = gkeepapi.Keep()
keep.authenticate(USERNAME, MASTER_TOKEN)


def get_random_quote():
    """Fetch a random quote from the Google Keep note titled 'Wisdom'."""
    for note in keep.all():
        if note.title == "Wisdom":
            # Split quotes by double newline and filter out empty strings
            quotes = [q.strip() for q in note.text.split("\n\n") if q.strip()]
            if quotes:
                return random.choice(quotes)
    return "No quotes found."


# -------------------------
# DISPLAY CONTROL FUNCTIONS
# -------------------------
def set_display_power(state):
    """Turn display ON or OFF using ddcutil."""
    try:
        subprocess.run(["ddcutil", "setvcp", "D6", str(state)], check=True)
        print(f"Display power set to {state}")
    except Exception as e:
        print(f"Failed to set display power: {e}")


def set_brightness(level):
    """Set display brightness using ddcutil."""
    try:
        subprocess.run(["ddcutil", "setvcp", "10", str(level)], check=True)
        print(f"Brightness set to {level}%")
    except Exception as e:
        print(f"Failed to set brightness: {e}")


def is_sleep_time():
    """Return True if current time is within sleep period."""
    now = datetime.now().time()
    start = time(SLEEP_START_HOUR, 0)
    end = time(SLEEP_END_HOUR, 0)

    # Handles time ranges that cross midnight
    if SLEEP_START_HOUR < SLEEP_END_HOUR:
        return start <= now < end
    else:
        return now >= start or now < end


# -------------------------
# WEATHER FUNCTIONS
# -------------------------
def fetch_weather():
    """Fetches hourly forecast from OpenWeatherMap."""
    # Check that all necessary keys are defined before making the request
    if not all([WEATHER_API_KEY, WEATHER_CITY, WEATHER_COUNTRY]):
        print("Weather API key, city, or country not configured in .env.")
        return []

    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": f"{WEATHER_CITY},{WEATHER_COUNTRY}",
        "appid": WEATHER_API_KEY,
        "units": "imperial"  # Use "metric" for Celsius
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()  
        data = response.json()
        
        # Extract 4 forecast items (starting from the next 3-hour block)
        forecast_list = []
        for item in data.get('list', [])[0:4]: 
            time_obj = datetime.fromtimestamp(item['dt'])
            temp = int(item['main']['temp'])
            icon_code = item['weather'][0]['icon'] 
            forecast_list.append({
                "time": time_obj,
                "temp": temp,
                "icon": icon_code
            })
        return forecast_list
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return []


def get_weather_icon(icon_code):
    """Maps OpenWeatherMap icon code to a simple Unicode symbol."""
    if icon_code.startswith('01'): # Clear sky
        return u'\u2600\ufe0f' # Sun
    elif icon_code.startswith('02') or icon_code.startswith('03') or icon_code.startswith('04'): # Clouds
        return u'\u2601\ufe0f' # Cloud
    elif icon_code.startswith('09') or icon_code.startswith('10'): # Rain
        return u'\u2614\ufe0f' # Umbrella with Rain Drops
    elif icon_code.startswith('11'): # Thunderstorm
        return u'\u26c8\ufe0f' # Cloud with Lightning
    elif icon_code.startswith('13'): # Snow
        return u'\u2744\ufe0f' # Snowflake
    else:
        return u'\u2601\ufe0f' # Default to Cloud


def update_weather():
    """Fetches and updates the weather widget."""
    forecasts = fetch_weather()

    # Clear old widgets
    for widget in weather_frame.winfo_children():
        widget.destroy()

    for forecast in forecasts:
        temp = forecast['temp']
        icon_symbol = get_weather_icon(forecast['icon'])
        # Use %-I to remove leading zero on Linux/Raspberry Pi OS
        time_str = forecast['time'].strftime("%-I%p") 

        # Create a frame for each forecast column
        hour_col = tk.Frame(weather_frame, bg="#f2f2f2", padx=10)
        hour_col.pack(side="left")

        # 1. Temperature Label
        temp_label = tk.Label(
            hour_col,
            text=f"{temp}°",
            font=("Arial", 35, "bold"),
            fg="black",
            bg="#f2f2f2"
        )
        temp_label.pack()

        # 2. Icon Label
        icon_label = tk.Label(
            hour_col,
            text=icon_symbol,
            font=("Arial", 35), 
            fg="green", 
            bg="#f2f2f2"
        )
        icon_label.pack()
        
        # 3. Time Label
        time_label_hourly = tk.Label(
            hour_col,
            text=time_str,
            font=("Arial", 20),
            fg="black",
            bg="#f2f2f2"
        )
        time_label_hourly.pack()

    # Schedule the next weather update (every 60 minutes = 1,800,000 ms)
    root.after(60 * 60 * 1000, update_weather)


# -------------------------
# TKINTER FULLSCREEN SETUP (Widget Definition)
# -------------------------
root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg="#f2f2f2") 
root.config(cursor="none")

# --- CENTERED QUOTE LABEL ---
label = tk.Label(
    root,
    text="Loading...",
    font=("Arial", 70, "bold"),
    fg="black",
    bg="#f2f2f2",
    wraplength=root.winfo_screenwidth() - 150,
    justify="center"
)
label.pack(expand=True)


# --- TOP-LEFT WEATHER WIDGET ---
weather_container = tk.Frame(root, bg="#f2f2f2")
# Use place() for positioning (no padx/pady allowed here)
weather_container.place(relx=0.0, y=0, anchor="nw") 

# This frame holds the hourly columns
weather_frame = tk.Frame(weather_container, bg="#f2f2f2")
# Use pack() for the inner frame and apply padding here
# This fixes the NameError and the TclError
weather_frame.pack(anchor="w", padx=40, pady=20) 


# --- TOP-RIGHT TIME + DATE DISPLAY ---
clock_frame = tk.Frame(root, bg="#f2f2f2")
clock_frame.place(relx=1.0, y=0, anchor="ne") # Top Right

time_label = tk.Label(
    clock_frame,
    font=("Arial", 70, "bold"),
    fg="black",
    bg="#f2f2f2",
    anchor="e"
)
time_label.pack(anchor="e", padx=40, pady=(20, 0))

date_label = tk.Label(
    clock_frame,
    font=("Arial", 30),
    fg="black",
    bg="#f2f2f2",
    anchor="e"
)
date_label.pack(anchor="e", padx=40, pady=(0, 10))


# -------------------------
# SCHEDULING AND DISPLAY CONTROL
# -------------------------
def update_time():
    """Update time and date every second."""
    now = datetime.now()
    time_label.config(text=now.strftime("%I:%M %p"))
    date_label.config(text=now.strftime("%a, %b %d"))
    root.after(1000, update_time)


def schedule_next_update(target_hour, function_to_run):
    now = datetime.now()
    next_run = datetime(now.year, now.month, now.day, target_hour, 0, 0)
    if now >= next_run:
        next_run += timedelta(days=1)
    delay_ms = int((next_run - now).total_seconds() * 1000)
    print(f"Scheduling {function_to_run.__name__} in {(next_run - now)}")
    root.after(delay_ms, function_to_run)


def update_quote():
    """Update label with new random quote daily."""
    quote = get_random_quote()
    label.config(text=quote)
    # Schedule next update for 9 AM
    schedule_next_update(9, update_quote)


def turn_off_display():
    set_display_power(DISPLAY_POWER_OFF)
    schedule_next_update(SLEEP_END_HOUR, turn_on_display)


def turn_on_display():
    set_display_power(DISPLAY_POWER_ON)
    set_brightness(BRIGHTNESS_DAY)
    schedule_next_update(SLEEP_START_HOUR, turn_off_display)
    schedule_next_update(DIM_HOUR, dim_brightness)


def dim_brightness():
    set_brightness(BRIGHTNESS_EVENING)
    schedule_next_update(SLEEP_END_HOUR, restore_brightness)


def restore_brightness():
    set_brightness(BRIGHTNESS_DAY)
    schedule_next_update(DIM_HOUR, dim_brightness)


# -------------------------
# PROGRAM START (Function Calls)
# -------------------------
root.bind("<Escape>", lambda e: root.destroy())

update_time()
update_quote()
update_weather()

# Determine initial display state based on current time
if is_sleep_time():
    print("It's sleep time. Turning display OFF until morning.")
    turn_off_display()
else:
    turn_on_display()
    # Check if the current time is already in the dim period
    if datetime.now().hour >= DIM_HOUR and datetime.now().hour < SLEEP_START_HOUR:
        dim_brightness()

root.mainloop()