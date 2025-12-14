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
from display.modes import (
    is_sleep_time,
    go_to_sleep_mode,
    restore_day_mode,
)

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

# -------------------------
# MAIN LOOP
# -------------------------
root.mainloop()
