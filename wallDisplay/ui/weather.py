import tkinter as tk
from services.weather_service import fetch_weather

# -------------------------
# WEATHER ICON MAPPING
# -------------------------
def get_weather_icon(icon_code):
    if icon_code.startswith("01"):
        return "☀️" if "d" in icon_code else "🌙"
    elif icon_code.startswith(("02", "03", "04")):
        return "☁️"
    elif icon_code.startswith(("09", "10")):
        return "☔"
    elif icon_code.startswith("11"):
        return "⛈️"
    elif icon_code.startswith("13"):
        return "❄️"
    else:
        return "☁️"


# -------------------------
# WEATHER UI UPDATE
# -------------------------
def update_weather(root, weather_frame):
    forecasts = fetch_weather()

    # Clear old widgets
    for widget in weather_frame.winfo_children():
        widget.destroy()

    bg_color = root.cget("bg")

    for forecast in forecasts:
        time_str = forecast["time"].strftime("%-I%p")
        temp = forecast["temp"]
        icon = get_weather_icon(forecast["icon"])

        col = tk.Frame(weather_frame, bg=bg_color, padx=10)
        col.pack(side="left")

        tk.Label(
            col,
            text=f"{temp}°",
            font=("Arial", 35, "bold"),
            fg="black",
            bg=bg_color,
        ).pack()

        tk.Label(
            col,
            text=icon,
            font=("Noto Color Emoji", 35),
            bg=bg_color,
        ).pack()

        tk.Label(
            col,
            text=time_str,
            font=("Arial", 20),
            fg="black",
            bg=bg_color,
        ).pack()

    # Refresh every hour
    root.after(60 * 60 * 1000, lambda: update_weather(root, weather_frame))
