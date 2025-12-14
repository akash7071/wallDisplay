from datetime import datetime

def update_time(root, time_label, date_label):
    now = datetime.now()
    time_label.config(text=now.strftime("%I:%M %p"))
    date_label.config(text=now.strftime("%a, %b %d"))
    root.after(1000, lambda: update_time(root, time_label, date_label))
