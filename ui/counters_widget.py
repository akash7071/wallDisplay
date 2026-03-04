import tkinter as tk
from services.counters_service import get_status

# Optional: set reminder threshold per task
REMINDER_THRESHOLDS = {
    "bedsheets": 10,
    "Bathroom": 30,
    "towels": 7
}

def get_color(days):
    """Return color based on how long since last done"""
    if days <= 6:
        return "green"   # 🟢 0–6 days
    elif days <= 13:
        return "yellow"  # 🟡 7–13 days
    else:
        return "red"     # 🔴 14+ days

def create_counters_widget(parent):
    frame = tk.Frame(parent, bg="black")
    frame.pack(pady=0, anchor="w")

    statuses = get_status()

    for name, days in statuses.items():
        # Show "Today" instead of 0 days
        display_days = "Today" if days == 0 else f"{days} days ago"

        color = get_color(days)

        

        text = f"{name.capitalize()}: {display_days}"

        tk.Label(
            frame,
            text=text,
            fg=color,
            bg="black",
            font=("Helvetica", 18)
        ).pack(anchor="w")

    return frame
