from datetime import datetime, timedelta

def schedule_next_update(root, target_hour, callback):
    now = datetime.now()
    next_run = datetime(now.year, now.month, now.day, target_hour)
    if now >= next_run:
        next_run += timedelta(days=1)
    delay = int((next_run - now).total_seconds() * 1000)
    root.after(delay, callback)
