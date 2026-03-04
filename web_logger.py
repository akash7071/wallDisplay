from flask import Flask, render_template, redirect, request
from services.counters_service import mark_done, get_status
from datetime import date

app = Flask(__name__)

# Homepage showing all tasks
@app.route("/")
def index():
    statuses = get_status()
    return render_template("index.html", statuses=statuses, date=date)

# Mark a task done (default today)
@app.route("/mark/<task>")
def mark(task):
    mark_done(task, source="web")
    return redirect("/")

# Mark a task with a custom date
@app.route("/mark_custom", methods=["POST"])
def mark_custom():
    task = request.form["task"]
    date_str = request.form["date"]

    mark_done(task, event_date=date_str, source="web")
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
