import subprocess

def set_display_power(state):
    try:
        subprocess.run(["ddcutil", "setvcp", "D6", str(state)], check=True)
    except Exception as e:
        print(f"Display power error: {e}")
