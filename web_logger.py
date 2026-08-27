from flask import Flask, render_template, redirect, request, jsonify
from services.counters_service import mark_done, get_status
from services.quote_service import get_current_quote, get_and_save_random_quote
from datetime import date, datetime
import ssl
import os

from config import (
    BRIGHTNESS_DAY,
    BRIGHTNESS_EVENING,
    BRIGHTNESS_SLEEP,
    DIM_HOUR,
    SLEEP_END_HOUR,
    SLEEP_START_HOUR,
)
from display.brightness import get_last_requested_brightness
from display.modes import is_sleep_time
from services.weather_service import get_latest_weather
from services.dashboard_settings import load_settings
from display.web_commands import command_queue

app = Flask(__name__)

# SSL context for HTTPS
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
cert_file = os.path.join(os.path.dirname(__file__), 'cert.pem')
key_file = os.path.join(os.path.dirname(__file__), 'key.pem')
if os.path.exists(cert_file) and os.path.exists(key_file):
    ssl_context.load_cert_chain(cert_file, key_file)

def current_mode():
    if is_sleep_time():
        return "sleep"
    if DIM_HOUR <= datetime.now().hour < SLEEP_START_HOUR:
        return "dim"
    return "day"


# Homepage dashboard
@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/dashboard/status")
def dashboard_status():
    mode = current_mode()
    brightness = get_last_requested_brightness()
    if brightness is None:
        brightness = {"day": BRIGHTNESS_DAY, "dim": BRIGHTNESS_EVENING, "sleep": BRIGHTNESS_SLEEP}[mode]
    return jsonify({
        "server_time": datetime.now().isoformat(),
        "quote": get_current_quote(),
        "weather": get_latest_weather(),
        "display": {
            "status": "sleeping" if mode == "sleep" else "active",
            "brightness": brightness,
            "mode": mode,
        },
        "schedule": {
            "wake": f"{SLEEP_END_HOUR:02d}:00",
            "dim": f"{DIM_HOUR:02d}:00",
            "sleep": f"{SLEEP_START_HOUR:02d}:00",
        },
        "widgets": load_settings()["widgets"],
        "weather_units": load_settings()["weather_units"],
    })


@app.route("/api/dashboard/widgets/clock", methods=["POST"])
def set_clock_widget():
    return queue_widget_update("clock")


@app.route("/api/dashboard/widgets/quote", methods=["POST"])
def set_quote_widget():
    return queue_widget_update("quote")


@app.route("/api/dashboard/widgets/weather", methods=["POST"])
def set_weather_widget():
    return queue_widget_update("weather")


def queue_widget_update(widget):
    data = request.get_json(silent=True) or {}
    enabled = data.get("enabled")
    if not isinstance(enabled, bool):
        return jsonify({"error": "'enabled' must be true or false"}), 400
    command_queue.put((f"set_{widget}_enabled", enabled))
    return jsonify({"status": "queued", "enabled": enabled}), 202


@app.route("/api/dashboard/weather/units", methods=["POST"])
def set_weather_units():
    data = request.get_json(silent=True) or {}
    units = data.get("units")
    if units not in ("imperial", "metric"):
        return jsonify({"error": "'units' must be 'imperial' or 'metric'"}), 400
    command_queue.put(("set_weather_units", units))
    return jsonify({"status": "queued", "units": units}), 202

# API endpoint to get a quote notification
@app.route("/api/send_quote_notification")
def send_quote_notification():
    quote = get_current_quote()
    return jsonify({
        "status": "success",
        "quote": quote,
        "title": "Daily Quote",
        "icon": "📜"
    })


@app.route("/quote")
def quote_page():
    return render_template("quote.html", quote=get_current_quote())

# Counters page
@app.route("/counters")
def counters():
    statuses = get_status()
    return render_template("counters.html", statuses=statuses, date=date)

# Mark a task done (default today)
@app.route("/mark/<task>")
def mark(task):
    mark_done(task, source="web")
    return redirect("/counters")

# Mark a task with a custom date
@app.route("/mark_custom", methods=["POST"])
def mark_custom():
    task = request.form["task"]
    date_str = request.form["date"]

    mark_done(task, event_date=date_str, source="web")
    return redirect("/counters")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, ssl_context=ssl_context)
