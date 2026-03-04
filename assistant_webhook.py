from flask import Flask, request
from services.counters_service import mark_done

app = Flask(__name__)

@app.route("/mark_done")
def mark_task_done():
    task = request.args.get("task")
    if task:
        mark_done(task)
        return f"{task} marked done", 200
    return "No task provided", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
