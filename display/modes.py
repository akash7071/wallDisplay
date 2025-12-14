from datetime import datetime, time
from config import (
    SLEEP_START_HOUR,
    SLEEP_END_HOUR,
    DIM_HOUR,
    BRIGHTNESS_DAY,
    BRIGHTNESS_EVENING,
    BRIGHTNESS_SLEEP,
    COLOR_BACKGROUND,
    COLOR_NIGHT_BACKGROUND,
    COLOR_NIGHT_TEXT,
)
from display.brightness import set_brightness
from utils.scheduler import schedule_next_update


# -------------------------
# TIME CHECK
# -------------------------
def is_sleep_time():
    now = datetime.now().time()
    start = time(SLEEP_START_HOUR, 0)
    end = time(SLEEP_END_HOUR, 0)

    if SLEEP_START_HOUR < SLEEP_END_HOUR:
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
):
    print("🌙 Entering Sleep Mode")

    set_brightness(BRIGHTNESS_SLEEP)

    root.configure(bg=COLOR_NIGHT_BACKGROUND)
    clock_frame.configure(bg=COLOR_NIGHT_BACKGROUND)

    label.pack_forget()
    date_label.pack_forget()
    weather_container.place_forget()

    clock_frame.place_forget()
    clock_frame.place(relx=0.5, rely=0.5, anchor="center")

    time_label.configure(
        bg=COLOR_NIGHT_BACKGROUND,
        fg=COLOR_NIGHT_TEXT,
    )

    schedule_next_update(
        root,
        SLEEP_END_HOUR,
        lambda: restore_day_mode(
            root,
            clock_frame,
            time_label,
            label,
            date_label,
            weather_container,
        ),
    )


def restore_day_mode(
    root,
    clock_frame,
    time_label,
    label,
    date_label,
    weather_container,
):
    print("☀️ Restoring Day Mode")

    set_brightness(BRIGHTNESS_DAY)

    root.configure(bg=COLOR_BACKGROUND)
    clock_frame.configure(bg=COLOR_BACKGROUND)

    clock_frame.place_forget()
    clock_frame.place(relx=1.0, y=0, anchor="ne")

    time_label.configure(bg=COLOR_BACKGROUND, fg="black")

    label.pack(expand=True)
    date_label.pack(anchor="e", padx=40, pady=(0, 10))
    weather_container.place(relx=0.0, y=0, anchor="nw")

    schedule_next_update(
        root,
        DIM_HOUR,
        lambda: dim_brightness(
            root,
            clock_frame,
            time_label,
            label,
            date_label,
            weather_container,
        ),
    )

    schedule_next_update(
        root,
        SLEEP_START_HOUR,
        lambda: go_to_sleep_mode(
            root,
            clock_frame,
            time_label,
            label,
            date_label,
            weather_container,
        ),
    )

    if DIM_HOUR <= datetime.now().hour < SLEEP_START_HOUR:
        dim_brightness(
            root,
            clock_frame,
            time_label,
            label,
            date_label,
            weather_container,
        )


def dim_brightness(
    root,
    clock_frame,
    time_label,
    label,
    date_label,
    weather_container,
):
    print("💡 Evening Mode")
    set_brightness(BRIGHTNESS_EVENING)
