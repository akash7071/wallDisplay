import tkinter as tk
from config import COLOR_BACKGROUND

# -------------------------
# ROOT WINDOW
# -------------------------
root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg=COLOR_BACKGROUND)
root.config(cursor="none")

# -------------------------
# QUOTE (CENTER)
# -------------------------
label = tk.Label(
    root,
    text="Loading...",
    font=("Arial", 70, "bold"),
    fg="black",
    bg=COLOR_BACKGROUND,
    wraplength=root.winfo_screenwidth() - 150,
    justify="center",
)
label.pack(expand=True)

# -------------------------
# WEATHER (TOP-LEFT)
# -------------------------
weather_container = tk.Frame(root, bg=COLOR_BACKGROUND)
weather_container.place(relx=0.0, y=0, anchor="nw")

weather_frame = tk.Frame(weather_container, bg=COLOR_BACKGROUND)
weather_frame.pack(anchor="w", padx=40, pady=20)

# -------------------------
# CLOCK (TOP-RIGHT)
# -------------------------
clock_frame = tk.Frame(root, bg=COLOR_BACKGROUND)
clock_frame.place(relx=1.0, y=0, anchor="ne")

time_label = tk.Label(
    clock_frame,
    font=("Arial", 70, "bold"),
    fg="black",
    bg=COLOR_BACKGROUND,
    anchor="e",
)
time_label.pack(anchor="e", padx=40, pady=(20, 0))

date_label = tk.Label(
    clock_frame,
    font=("Arial", 30),
    fg="black",
    bg=COLOR_BACKGROUND,
    anchor="e",
)
date_label.pack(anchor="e", padx=40, pady=(0, 10))

# -------------------------
# EXIT BINDING
# -------------------------
root.bind("<Escape>", lambda e: root.destroy())
