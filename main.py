# main.py

# -------------------------
# IMPORTS
# -------------------------
import threading
import sys
from queue import Empty

# Flask web logger
from web_logger import app as web_app, ssl_context  # adjust path if needed

# Tkinter UI imports
from ui.app import (
    root,
    label,
    clock_frame,
    time_label,
    date_label,
    weather_container,
    weather_frame,
    footer_frame,
    footer_label1,
    footer_label2,
    update_footer,
)

from ui.clock import update_time
from ui.quote import update_quote
from ui.weather import update_weather
from ui.counters_widget import create_counters_widget

from services.quote_service import save_keep_quote_list
from display.modes import (
    is_sleep_time,
    go_to_sleep_mode,
    restore_day_mode,
)
from config import ENABLE_COUNTERS_WIDGET
from display.web_commands import command_queue
from services.dashboard_settings import (
    is_clock_enabled,
    is_quote_enabled,
    set_clock_enabled,
    set_quote_enabled,
    set_weather_units,
)

# -------------------------
# PARSE COMMAND-LINE ARGUMENTS
# -------------------------
enable_counters = ENABLE_COUNTERS_WIDGET
quote_list = False
quote_list_file = None
for arg in sys.argv[1:]:
    if arg.startswith("counter="):
        value = arg.split("=", 1)[1].lower()
        enable_counters = value in ("on", "true", "1", "yes")
    elif arg.startswith("quote_list="):
        value = arg.split("=", 1)[1].lower()
        quote_list = value in ("1", "true", "on", "yes")
    elif arg.startswith("quote_list_file="):
        quote_list_file = arg.split("=", 1)[1]

ENABLE_COUNTERS_WIDGET = enable_counters

if quote_list:
    output_path = save_keep_quote_list(quote_list_file)
    print(f"Keep quote list saved to: {output_path}")

# -------------------------
# FUNCTION TO RUN FLASK
# -------------------------
def run_web_logger():
    web_app.run(host="0.0.0.0", port=8000, debug=False, ssl_context=ssl_context)

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
update_footer(root, footer_label1, footer_label2)

# Honor dashboard widget settings before choosing the initial display mode.
if not is_clock_enabled():
    clock_frame.place_forget()
if not is_quote_enabled():
    label.pack_forget()

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
        footer_frame,
    )
else:
    restore_day_mode(
        root,
        clock_frame,
        time_label,
        label,
        date_label,
        weather_container,
        footer_frame,
    )
    show_counters()
    refresh_counters()


# -------------------------
# DASHBOARD COMMANDS
# -------------------------
def apply_dashboard_commands():
    """Apply web commands on Tk's main thread."""
    while True:
        try:
            action, value = command_queue.get_nowait()
        except Empty:
            break

        if action == "set_clock_enabled":
            enabled = set_clock_enabled(value)["widgets"]["clock"]
            clock_frame.place_forget()
            if enabled:
                if is_sleep_time():
                    clock_frame.place(relx=0.5, rely=0.5, anchor="center")
                else:
                    clock_frame.place(relx=1.0, y=0, anchor="ne")

        if action == "set_quote_enabled":
            enabled = set_quote_enabled(value)["widgets"]["quote"]
            if enabled and not is_sleep_time():
                label.pack(expand=True)
            else:
                label.pack_forget()

        if action == "set_weather_units":
            set_weather_units(value)
            update_weather(root, weather_frame)

    root.after(150, apply_dashboard_commands)


apply_dashboard_commands()

# -------------------------
# MAIN LOOP
# -------------------------
root.mainloop()
