from flask import Flask, render_template, redirect, request, jsonify
from services.counters_service import mark_done, get_status
from services.quote_service import get_current_quote, get_and_save_random_quote
from datetime import date

app = Flask(__name__)

# Homepage showing quote
@app.route("/")
def index():
    quote = get_current_quote()
    return render_template("quote.html", quote=quote)

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
    app.run(host="0.0.0.0", port=8000)
