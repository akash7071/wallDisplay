import subprocess

def set_brightness(level):
    try:
        subprocess.run(["ddcutil", "setvcp", "10", str(level)], check=True)
    except Exception as e:
        print(f"Brightness error: {e}")
