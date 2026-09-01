"""Persistent settings owned by the dashboard."""

import json
from pathlib import Path
from datetime import datetime

from config import DIM_HOUR, SLEEP_END_HOUR, SLEEP_START_HOUR, FOOTER_TEXT_LINE1, FOOTER_TEXT_LINE2

BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_FILE = BASE_DIR / "data" / "dashboard_settings.json"
DEFAULT_SETTINGS = {
    "widgets": {"clock": True, "quote": True, "weather": True, "counters": True},
    "weather_units": "imperial",
    "automation_enabled": True,
    "schedule": {
        "wake": f"{SLEEP_END_HOUR:02d}:00",
        "dim": f"{DIM_HOUR:02d}:00",
        "sleep": f"{SLEEP_START_HOUR:02d}:00",
    },
    "footer_text": {
        "line1": FOOTER_TEXT_LINE1,
        "line2": FOOTER_TEXT_LINE2,
        "highlight_mode": "auto",
    },
}


def load_settings():
    if not SETTINGS_FILE.exists():
        return _default_settings()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            settings = json.load(file)
        widgets = settings.get("widgets", {})
        weather_units = settings.get("weather_units", "imperial")
        if weather_units not in ("imperial", "metric"):
            weather_units = "imperial"
        schedule = settings.get("schedule", {})
        footer_text = settings.get("footer_text", {})
        line1 = footer_text.get("line1", FOOTER_TEXT_LINE1)
        line2 = footer_text.get("line2", FOOTER_TEXT_LINE2)
        highlight_mode = footer_text.get("highlight_mode", "auto")
        if not isinstance(line1, str):
            line1 = FOOTER_TEXT_LINE1
        if not isinstance(line2, str):
            line2 = FOOTER_TEXT_LINE2
        if highlight_mode not in ("auto", "line1", "line2"):
            highlight_mode = "auto"

        return {
            "widgets": {
                "clock": bool(widgets.get("clock", True)),
                "quote": bool(widgets.get("quote", True)),
                "weather": bool(widgets.get("weather", True)),
                "counters": bool(widgets.get("counters", True)),
            },
            "weather_units": weather_units,
            "automation_enabled": bool(settings.get("automation_enabled", True)),
            "schedule": {
                name: _valid_time(schedule.get(name, DEFAULT_SETTINGS["schedule"][name]), name)
                for name in ("wake", "dim", "sleep")
            },
            "footer_text": {
                "line1": line1,
                "line2": line2,
                "highlight_mode": highlight_mode,
            },
        }
    except (OSError, json.JSONDecodeError):
        return _default_settings()


def _default_settings():
    return {
        "widgets": dict(DEFAULT_SETTINGS["widgets"]),
        "weather_units": DEFAULT_SETTINGS["weather_units"],
        "automation_enabled": DEFAULT_SETTINGS["automation_enabled"],
        "schedule": dict(DEFAULT_SETTINGS["schedule"]),
        "footer_text": dict(DEFAULT_SETTINGS["footer_text"]),
    }


def _valid_time(value, name):
    if not isinstance(value, str):
        return DEFAULT_SETTINGS["schedule"][name]
    try:
        datetime.strptime(value, "%H:%M")
        return value
    except ValueError:
        return DEFAULT_SETTINGS["schedule"][name]


def _save(settings):
    SETTINGS_FILE.parent.mkdir(exist_ok=True)
    temporary_file = SETTINGS_FILE.with_suffix(".tmp")
    with open(temporary_file, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=2)
    temporary_file.replace(SETTINGS_FILE)


def set_clock_enabled(enabled):
    return set_widget_enabled("clock", enabled)


def set_quote_enabled(enabled):
    return set_widget_enabled("quote", enabled)


def set_widget_enabled(name, enabled):
    settings = load_settings()
    settings["widgets"][name] = bool(enabled)
    _save(settings)
    return settings


def is_clock_enabled():
    return load_settings()["widgets"]["clock"]


def is_quote_enabled():
    return load_settings()["widgets"]["quote"]


def set_weather_enabled(enabled):
    return set_widget_enabled("weather", enabled)


def is_weather_enabled():
    return load_settings()["widgets"]["weather"]


def set_counters_enabled(enabled):
    return set_widget_enabled("counters", enabled)


def are_counters_enabled():
    return load_settings()["widgets"]["counters"]


def set_weather_units(units):
    if units not in ("imperial", "metric"):
        raise ValueError("Weather units must be 'imperial' or 'metric'")
    settings = load_settings()
    settings["weather_units"] = units
    _save(settings)
    return settings


def get_weather_units():
    return load_settings()["weather_units"]


def set_schedule(schedule):
    if set(schedule) != {"wake", "dim", "sleep"}:
        raise ValueError("Schedule must include wake, dim, and sleep times")
    validated = {name: _valid_time(value, name) for name, value in schedule.items()}
    if len(set(validated.values())) != 3 or validated != schedule:
        raise ValueError("Schedule times must be three distinct HH:MM values")
    settings = load_settings()
    settings["schedule"] = validated
    _save(settings)
    return settings


def set_automation_enabled(enabled):
    settings = load_settings()
    settings["automation_enabled"] = bool(enabled)
    _save(settings)
    return settings


def set_footer_text(line1, line2, highlight_mode="auto"):
    if not isinstance(line1, str) or not isinstance(line2, str):
        raise ValueError("Footer text lines must be strings")
    if highlight_mode not in ("auto", "line1", "line2"):
        highlight_mode = "auto"
    settings = load_settings()
    settings["footer_text"] = {
        "line1": line1.strip(),
        "line2": line2.strip(),
        "highlight_mode": highlight_mode,
    }
    _save(settings)
    return settings


def get_footer_text():
    return load_settings()["footer_text"]

