import json
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
COUNTERS_FILE = BASE_DIR / "data" / "counters.json"
HISTORY_FILE = BASE_DIR / "data" / "history.json"


def load_json(path, default):
    if not path.exists():
        return default
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# -------------------------
# Counters (last-done state)
# -------------------------
def load_counters():
    return load_json(COUNTERS_FILE, {})


def save_counters(counters):
    save_json(COUNTERS_FILE, counters)


def days_since(date_str):
    last = date.fromisoformat(date_str)
    return (date.today() - last).days


def get_status():
    counters = load_counters()
    return {k: days_since(v) for k, v in counters.items()}


# -------------------------
# History logging (NEW)
# -------------------------
def log_event(task, event_date, source="web"):
    history = load_json(HISTORY_FILE, [])
    history.append({
        "task": task,
        "date": event_date,
        "source": source
    })
    save_json(HISTORY_FILE, history)


def mark_done(task, event_date=None, source="web"):
    if event_date is None:
        event_date = date.today().isoformat()

    # update counters
    counters = load_counters()
    counters[task] = event_date
    save_counters(counters)

    # log history
    log_event(task, event_date, source)
