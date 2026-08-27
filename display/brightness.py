import subprocess

_last_requested_brightness = None

def set_brightness(level):
    global _last_requested_brightness
    _last_requested_brightness = int(level)
    try:
        subprocess.run(["ddcutil", "setvcp", "10", str(level)], check=True)
    except Exception as e:
        print(f"Brightness error: {e}")


def get_last_requested_brightness():
    """Brightness last requested by this app (DDC does not provide a portable read)."""
    return _last_requested_brightness
