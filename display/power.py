import subprocess

_last_requested_power = None

def set_display_power(state):
    global _last_requested_power
    _last_requested_power = state
    try:
        subprocess.run(["ddcutil", "setvcp", "D6", str(state)], check=True)
    except Exception as e:
        print(f"Display power error: {e}")


def get_last_requested_power():
    return _last_requested_power
