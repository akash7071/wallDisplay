"""Persistent settings owned by the dashboard."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_FILE = BASE_DIR / "data" / "dashboard_settings.json"
DEFAULT_SETTINGS = {"widgets": {"clock": True}}


def load_settings():
    if not SETTINGS_FILE.exists():
        return {"widgets": dict(DEFAULT_SETTINGS["widgets"])}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            settings = json.load(file)
        clock_enabled = bool(settings.get("widgets", {}).get("clock", True))
        return {"widgets": {"clock": clock_enabled}}
    except (OSError, json.JSONDecodeError):
        return {"widgets": dict(DEFAULT_SETTINGS["widgets"])}


def set_clock_enabled(enabled):
    settings = load_settings()
    settings["widgets"]["clock"] = bool(enabled)
    SETTINGS_FILE.parent.mkdir(exist_ok=True)
    temporary_file = SETTINGS_FILE.with_suffix(".tmp")
    with open(temporary_file, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=2)
    temporary_file.replace(SETTINGS_FILE)
    return settings


def is_clock_enabled():
    return load_settings()["widgets"]["clock"]
