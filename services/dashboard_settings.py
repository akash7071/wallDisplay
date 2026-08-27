"""Persistent settings owned by the dashboard."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_FILE = BASE_DIR / "data" / "dashboard_settings.json"
DEFAULT_SETTINGS = {"widgets": {"clock": True, "quote": True}}


def load_settings():
    if not SETTINGS_FILE.exists():
        return {"widgets": dict(DEFAULT_SETTINGS["widgets"])}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            settings = json.load(file)
        widgets = settings.get("widgets", {})
        return {
            "widgets": {
                "clock": bool(widgets.get("clock", True)),
                "quote": bool(widgets.get("quote", True)),
            }
        }
    except (OSError, json.JSONDecodeError):
        return {"widgets": dict(DEFAULT_SETTINGS["widgets"])}


def set_clock_enabled(enabled):
    return set_widget_enabled("clock", enabled)


def set_quote_enabled(enabled):
    return set_widget_enabled("quote", enabled)


def set_widget_enabled(name, enabled):
    settings = load_settings()
    settings["widgets"][name] = bool(enabled)
    SETTINGS_FILE.parent.mkdir(exist_ok=True)
    temporary_file = SETTINGS_FILE.with_suffix(".tmp")
    with open(temporary_file, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=2)
    temporary_file.replace(SETTINGS_FILE)
    return settings


def is_clock_enabled():
    return load_settings()["widgets"]["clock"]


def is_quote_enabled():
    return load_settings()["widgets"]["quote"]
