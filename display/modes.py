from datetime import datetime, time
from config import (
    BRIGHTNESS_DAY,
    BRIGHTNESS_EVENING,
    BRIGHTNESS_SLEEP,
    COLOR_BACKGROUND,
    COLOR_PRIMARY_TEXT,
    COLOR_MUTED_TEXT,
    COLOR_NIGHT_BACKGROUND,
    COLOR_NIGHT_TEXT,
    FONT_FAMILY_PRIMARY,
    FONT_FAMILY_QUOTE,
)
from display.brightness import set_brightness
from display.runtime_state import set_mode
from services.dashboard_settings import (
    is_clock_enabled,
    is_quote_enabled,
    is_weather_enabled,
    load_settings,
)


# -------------------------
# TIME CHECK
# -------------------------
def is_sleep_time():
    schedule = load_settings()["schedule"]
    now = datetime.now().time()
    start = datetime.strptime(schedule["sleep"], "%H:%M").time()
    end = datetime.strptime(schedule["wake"], "%H:%M").time()
    return _in_time_range(now, start, end)


def is_dim_time():
    schedule = load_settings()["schedule"]
    now = datetime.now().time()
    start = datetime.strptime(schedule["dim"], "%H:%M").time()
    end = datetime.strptime(schedule["sleep"], "%H:%M").time()
    return not is_sleep_time() and _in_time_range(now, start, end)


def _in_time_range(now, start, end):
    if start < end:
        return start <= now < end
    return now >= start or now < end


# -------------------------
# MODES
# -------------------------
def go_to_sleep_mode(
    root,
    clock_frame,
    time_label,
    label,
    date_label,
    weather_container,
    footer_frame,
    show_counters=None,
    hide_counters=None,
):
    print("🌙 Entering Sleep Mode")

    set_brightness(BRIGHTNESS_SLEEP)
    set_mode("sleep")
    if hide_counters:
        hide_counters()

    root.configure(bg=COLOR_NIGHT_BACKGROUND)
    clock_frame.configure(bg=COLOR_NIGHT_BACKGROUND)

    label.pack_forget()
    date_label.pack_forget()
    weather_container.place_forget()
    footer_frame.place_forget()

    clock_frame.place_forget()
    if is_clock_enabled():
        clock_frame.place(relx=0.5, rely=0.5, anchor="center")

    time_label.configure(
        bg=COLOR_NIGHT_BACKGROUND,
        fg=COLOR_NIGHT_TEXT,
        font=(FONT_FAMILY_PRIMARY, 210, "bold"),
    )


def restore_day_mode(
    root,
    clock_frame,
    time_label,
    label,
    date_label,
    weather_container,
    footer_frame,
    show_counters=None,
    hide_counters=None,
):
    print("☀️ Restoring Day Mode")

    set_brightness(BRIGHTNESS_DAY)
    set_mode("day")

    root.configure(bg=COLOR_BACKGROUND)
    clock_frame.configure(bg=COLOR_BACKGROUND)

    clock_frame.place_forget()
    if is_clock_enabled():
        clock_frame.place(relx=1.0, y=0, anchor="ne")

    time_label.configure(
        bg=COLOR_BACKGROUND,
        fg=COLOR_PRIMARY_TEXT,
        font=(FONT_FAMILY_PRIMARY, 68, "bold"),
    )

    if is_quote_enabled():
        label.pack(expand=True, padx=80, pady=40)
    else:
        label.pack_forget()
    date_label.pack(anchor="e", padx=36, pady=(2, 10))
    if is_weather_enabled():
        weather_container.place(relx=0.0, y=0, anchor="nw")
    else:
        weather_container.place_forget()
    footer_frame.place(relx=1.0, rely=1.0, anchor="se")
    if show_counters:
        show_counters()


def dim_brightness(
    root,
    clock_frame,
    time_label,
    label,
    date_label,
    weather_container,
    footer_frame,
):
    print("💡 Evening Mode")
    set_brightness(BRIGHTNESS_EVENING)
    set_mode("dim")
