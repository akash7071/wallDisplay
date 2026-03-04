# main.py

# -------------------------
# IMPORTS
# -------------------------
import threading
import sys

# Flask web logger
from web_logger import app as web_app  # adjust path if needed

# Tkinter UI imports
from ui.app import (
    root,
    label,
    clock_frame,
    time_label,
    date_label,
    weather_container,
    weather_frame,
)

from ui.clock import update_time
from ui.quote import update_quote
from ui.weather import update_weather
from ui.counters_widget import create_counters_widget

from display.modes import (
    is_sleep_time,
    go_to_sleep_mode,
    restore_day_mode,
)
from config import ENABLE_COUNTERS_WIDGET

# -------------------------
# PARSE COMMAND-LINE ARGUMENTS
# -------------------------
enable_counters = ENABLE_COUNTERS_WIDGET
for arg in sys.argv[1:]:
    if arg.startswith("counter="):
        value = arg.split("=")[1].lower()
        enable_counters = value in ("on", "true", "1", "yes")
        break

ENABLE_COUNTERS_WIDGET = enable_counters

# -------------------------
# FUNCTION TO RUN FLASK
# -------------------------
def run_web_logger():
    web_app.run(host="0.0.0.0", port=8000, debug=False)

# Start Flask in a background daemon thread
flask_thread = threading.Thread(target=run_web_logger, daemon=True)
flask_thread.start()

# -------------------------
# COUNTERS
# -------------------------
counters_frame = None

def show_counters():
    global counters_frame
    if ENABLE_COUNTERS_WIDGET and counters_frame is None:
        counters_frame = create_counters_widget(root)

def hide_counters():
    global counters_frame
    if counters_frame:
        counters_frame.destroy()
        counters_frame = None

def refresh_counters():
    if ENABLE_COUNTERS_WIDGET:
        hide_counters()
        show_counters()
        root.after(60 * 60 * 1000, refresh_counters)  # refresh hourly

# -------------------------
# START UPDATES
# -------------------------
update_time(root, time_label, date_label)
update_quote(root, label)
update_weather(root, weather_frame)

# -------------------------
# INITIAL MODE
# -------------------------
if is_sleep_time():
    hide_counters()
    go_to_sleep_mode(
        root,
        clock_frame,
        time_label,
        label,
        date_label,
        weather_container,
    )
else:
    restore_day_mode(
        root,
        clock_frame,
        time_label,
        label,
        date_label,
        weather_container,
    )
    show_counters()
    refresh_counters()

# -------------------------
# MAIN LOOP
# -------------------------
root.mainloop()
