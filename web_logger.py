from flask import Flask, render_template, redirect, request, jsonify
from services.counters_service import mark_done, get_status
from services.quote_service import (
    get_current_quote,
    get_and_save_random_quote,
    get_all_quotes,
    add_quote,
    delete_quote,
    set_current_quote,
    sync_with_google_keep,
)
from auth.keep_client import is_authenticated as is_keep_authenticated
from datetime import date, datetime
import ssl
import os

from config import (
    BRIGHTNESS_DAY,
    BRIGHTNESS_EVENING,
    BRIGHTNESS_SLEEP,
)
from display.brightness import get_last_requested_brightness
from display.power import get_last_requested_power
from display.runtime_state import get_mode
from display.modes import is_dim_time, is_sleep_time
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
    inferred_mode = "day"
    if is_sleep_time():
        inferred_mode = "sleep"
    elif is_dim_time():
        inferred_mode = "dim"
    return get_mode(inferred_mode)


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
    settings = load_settings()
    power_state = get_last_requested_power()
    return jsonify({
        "server_time": datetime.now().isoformat(),
        "quote": get_current_quote(),
        "weather": get_latest_weather(),
        "display": {
            "status": "sleeping" if mode == "sleep" else "active",
            "brightness": brightness,
            "mode": mode,
            "power": "on" if power_state in (None, 1) else "off",
        },
        "schedule": settings["schedule"],
        "automation_enabled": settings["automation_enabled"],
        "widgets": settings["widgets"],
        "weather_units": settings["weather_units"],
        "footer_text": settings["footer_text"],
    })


@app.route("/api/dashboard/footer", methods=["POST"])
def set_dashboard_footer():
    data = request.get_json(silent=True) or {}
    line1 = data.get("line1")
    line2 = data.get("line2")
    highlight_mode = data.get("highlight_mode", "auto")
    if not isinstance(line1, str) or not isinstance(line2, str):
        return jsonify({"error": "'line1' and 'line2' must be string values"}), 400
    if highlight_mode not in ("auto", "line1", "line2"):
        return jsonify({"error": "'highlight_mode' must be 'auto', 'line1', or 'line2'"}), 400
    line1_clean = line1.strip()
    line2_clean = line2.strip()
    command_queue.put(("set_footer_text", {"line1": line1_clean, "line2": line2_clean, "highlight_mode": highlight_mode}))
    return jsonify({"status": "queued", "footer_text": {"line1": line1_clean, "line2": line2_clean, "highlight_mode": highlight_mode}}), 202


@app.route("/api/dashboard/widgets/clock", methods=["POST"])
def set_clock_widget():
    return queue_widget_update("clock")


@app.route("/api/dashboard/widgets/quote", methods=["POST"])
def set_quote_widget():
    return queue_widget_update("quote")


@app.route("/api/dashboard/widgets/weather", methods=["POST"])
def set_weather_widget():
    return queue_widget_update("weather")


@app.route("/api/dashboard/widgets/counters", methods=["POST"])
def set_counters_widget():
    return queue_widget_update("counters")


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


@app.route("/api/dashboard/display/brightness", methods=["POST"])
def set_dashboard_brightness():
    data = request.get_json(silent=True) or {}
    brightness = data.get("brightness")
    if not isinstance(brightness, int) or not 0 <= brightness <= 100:
        return jsonify({"error": "'brightness' must be a whole number from 0 to 100"}), 400
    command_queue.put(("set_brightness", brightness))
    return jsonify({"status": "queued", "brightness": brightness}), 202


@app.route("/api/dashboard/display/power", methods=["POST"])
def set_dashboard_power():
    data = request.get_json(silent=True) or {}
    power = data.get("power")
    if power not in ("on", "off"):
        return jsonify({"error": "'power' must be 'on' or 'off'"}), 400
    command_queue.put(("set_display_power", power))
    return jsonify({"status": "queued", "power": power}), 202


@app.route("/api/dashboard/display/mode", methods=["POST"])
def set_dashboard_mode():
    data = request.get_json(silent=True) or {}
    mode = data.get("mode")
    if mode not in ("sleep", "wake"):
        return jsonify({"error": "'mode' must be 'sleep' or 'wake'"}), 400
    command_queue.put(("set_display_mode", mode))
    return jsonify({"status": "queued", "mode": mode}), 202


@app.route("/api/dashboard/schedule", methods=["POST"])
def set_dashboard_schedule():
    data = request.get_json(silent=True) or {}
    schedule = data.get("schedule")
    if not isinstance(schedule, dict) or set(schedule) != {"wake", "dim", "sleep"}:
        return jsonify({"error": "Schedule requires wake, dim, and sleep times"}), 400
    try:
        parsed = [datetime.strptime(value, "%H:%M") for value in schedule.values()]
    except (TypeError, ValueError):
        return jsonify({"error": "Schedule times must use HH:MM"}), 400
    if len({item.time() for item in parsed}) != 3:
        return jsonify({"error": "Wake, dim, and sleep times must be different"}), 400
    command_queue.put(("set_schedule", schedule))
    return jsonify({"status": "queued", "schedule": schedule}), 202


@app.route("/api/dashboard/automation", methods=["POST"])
def set_dashboard_automation():
    data = request.get_json(silent=True) or {}
    enabled = data.get("enabled")
    if not isinstance(enabled, bool):
        return jsonify({"error": "'enabled' must be true or false"}), 400
    command_queue.put(("set_automation_enabled", enabled))
    return jsonify({"status": "queued", "enabled": enabled}), 202


# -------------------------
# QUOTE LIBRARY & MANAGEMENT APIs
# -------------------------
@app.route("/api/quotes", methods=["GET"])
def list_quotes():
    quotes = get_all_quotes()
    return jsonify({
        "quotes": quotes,
        "count": len(quotes),
        "current": get_current_quote(),
        "keep_connected": is_keep_authenticated(),
    })


@app.route("/api/quotes", methods=["POST"])
def create_quote():
    data = request.get_json(silent=True) or {}
    quote_text = data.get("quote", "").strip()
    if not quote_text:
        return jsonify({"error": "Quote text is required"}), 400
    success, result = add_quote(quote_text)
    if not success:
        return jsonify({"error": result}), 400
    return jsonify({"status": "added", "data": result}), 201


@app.route("/api/quotes", methods=["DELETE"])
def remove_quote():
    data = request.get_json(silent=True) or {}
    quote_text = data.get("quote", "").strip()
    if not quote_text:
        return jsonify({"error": "Quote text is required"}), 400
    success, result = delete_quote(quote_text)
    if not success:
        return jsonify({"error": result}), 404
    current = get_current_quote()
    command_queue.put(("set_current_quote", current))
    return jsonify({"status": "deleted", "data": result, "new_current": current}), 200


@app.route("/api/quotes/current", methods=["POST"])
def set_active_quote():
    data = request.get_json(silent=True) or {}
    quote_text = data.get("quote", "").strip()
    if not quote_text:
        return jsonify({"error": "Quote text is required"}), 400
    set_current_quote(quote_text)
    command_queue.put(("set_current_quote", quote_text))
    return jsonify({"status": "queued", "quote": quote_text}), 202


@app.route("/api/quotes/random", methods=["POST"])
def cycle_random_quote():
    quote = get_and_save_random_quote()
    command_queue.put(("set_current_quote", quote))
    return jsonify({"status": "queued", "quote": quote}), 202


@app.route("/api/quotes/sync", methods=["POST"])
def sync_quotes():
    success, result = sync_with_google_keep()
    if not success:
        return jsonify({"error": result}), 400
    return jsonify({"status": "synced", "data": result}), 200


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
