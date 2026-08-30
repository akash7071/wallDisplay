from datetime import datetime, timedelta

def schedule_next_update(root, target_time, callback):
    """Schedule a callback at the next HH:MM time and return the Tk job id."""
    if isinstance(target_time, int):
        hour, minute = target_time, 0
    else:
        hour, minute = map(int, target_time.split(":"))
    now = datetime.now()
    next_run = datetime(now.year, now.month, now.day, hour, minute)
    if now >= next_run:
        next_run += timedelta(days=1)
    delay = int((next_run - now).total_seconds() * 1000)
    return root.after(delay, callback)
