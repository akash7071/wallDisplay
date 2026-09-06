import tkinter as tk
from datetime import datetime
from config import (
    COLOR_BACKGROUND,
    COLOR_PRIMARY_TEXT,
    COLOR_MUTED_TEXT,
    FONT_FAMILY_PRIMARY,
    FONT_FAMILY_QUOTE,
    FOOTER_TEXT_LINE1,
    FOOTER_TEXT_LINE2,
    FOOTER_FONT,
    FOOTER_NORMAL_FG,
    FOOTER_HIGHLIGHT_FG,
)

from services.dashboard_settings import get_footer_text

# -------------------------
# ROOT WINDOW
# -------------------------
root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg=COLOR_BACKGROUND)
root.config(cursor="none")

# -------------------------
# QUOTE / MEDIA (CENTER)
# -------------------------
center_frame = tk.Frame(root, bg=COLOR_BACKGROUND)
center_frame.pack(expand=True, fill="both")

label = tk.Label(
    center_frame,
    text="Loading...",
    font=(FONT_FAMILY_QUOTE, 44, "bold"),
    fg=COLOR_PRIMARY_TEXT,
    bg=COLOR_BACKGROUND,
    wraplength=max(root.winfo_screenwidth() - 320, 600) if root.winfo_screenwidth() > 1 else 1000,
    justify="center",
)
# label.pack(expand=True, padx=80, pady=40)  # We will pack this dynamically

media_label = tk.Label(
    center_frame,
    bg=COLOR_BACKGROUND
)
# media_label.pack(expand=True, padx=80, pady=40) # We will pack this dynamically


# -------------------------
# WEATHER (TOP-LEFT)
# -------------------------
weather_container = tk.Frame(root, bg=COLOR_BACKGROUND)
weather_container.place(relx=0.0, y=0, anchor="nw")

weather_frame = tk.Frame(weather_container, bg=COLOR_BACKGROUND)
weather_frame.pack(anchor="w", padx=36, pady=24)

# -------------------------
# CLOCK (TOP-RIGHT)
# -------------------------
clock_frame = tk.Frame(root, bg=COLOR_BACKGROUND)
clock_frame.place(relx=1.0, y=0, anchor="ne")

time_label = tk.Label(
    clock_frame,
    font=(FONT_FAMILY_PRIMARY, 68, "bold"),
    fg=COLOR_PRIMARY_TEXT,
    bg=COLOR_BACKGROUND,
    anchor="e",
)
time_label.pack(anchor="e", padx=36, pady=(24, 0))

date_label = tk.Label(
    clock_frame,
    font=(FONT_FAMILY_PRIMARY, 22, "bold"),
    fg=COLOR_MUTED_TEXT,
    bg=COLOR_BACKGROUND,
    anchor="e",
)
date_label.pack(anchor="e", padx=36, pady=(2, 10))

# -------------------------
# FOOTER (BOTTOM-RIGHT)
# -------------------------
footer_frame = tk.Frame(root, bg=COLOR_BACKGROUND)
footer_frame.place(relx=1.0, rely=1.0, anchor="se")

initial_footer = get_footer_text()
footer_label1 = tk.Label(
    footer_frame,
    text=initial_footer.get("line1", FOOTER_TEXT_LINE1),
    font=FOOTER_FONT,
    fg=FOOTER_NORMAL_FG,
    bg=COLOR_BACKGROUND,
    anchor="e",
    justify="right",
)
footer_label1.pack(anchor="e", padx=36, pady=(0, 0))

footer_label2 = tk.Label(
    footer_frame,
    text=initial_footer.get("line2", FOOTER_TEXT_LINE2),
    font=FOOTER_FONT,
    fg=FOOTER_NORMAL_FG,
    bg=COLOR_BACKGROUND,
    anchor="e",
    justify="right",
)
footer_label2.pack(anchor="e", padx=36, pady=(0, 20))


def update_footer(root, label1, label2, schedule_next=True):
    footer_data = get_footer_text()
    mode = footer_data.get("highlight_mode", "auto")
    inverted = footer_data.get("inverted", False)

    if mode == "line1":
        highlight_first = True
    elif mode == "line2":
        highlight_first = False
    else:  # "auto"
        week_number = datetime.now().isocalendar()[1]
        highlight_first = week_number % 2 == 1
        if inverted:
            highlight_first = not highlight_first

    if highlight_first:
        label1.config(fg=FOOTER_HIGHLIGHT_FG, font=(FOOTER_FONT[0], FOOTER_FONT[1], "bold"))
        label2.config(fg=FOOTER_NORMAL_FG, font=FOOTER_FONT)
    else:
        label1.config(fg=FOOTER_NORMAL_FG, font=FOOTER_FONT)
        label2.config(fg=FOOTER_HIGHLIGHT_FG, font=(FOOTER_FONT[0], FOOTER_FONT[1], "bold"))

    if schedule_next:
        root.after(60 * 1000, lambda: update_footer(root, label1, label2))

# -------------------------
# EXIT BINDING
# -------------------------
root.bind("<Escape>", lambda e: root.destroy())
