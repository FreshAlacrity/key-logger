from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
from pathlib import Path
from time import monotonic_ns
from datetime import date

directory = Path("logs/")
MOUSE = {
    "moving": False,
    "location": [0, 0],
    "scrolling": False,
    "scroll": [0, 0]
}


def log_entry(action, key):
    file_name = str(date.today()) + ".txt"
    file_path = directory / file_name
    time = monotonic_ns()
    msg = ' - '.join(map(str, [time, action, key]))
    with file_path.open("a", encoding="utf-8") as f:
        f.write(f"{msg}\n")


def check_mouse():    
    if MOUSE["moving"]:
        x, y = MOUSE["location"]
        log_entry("released", f"Mouse.move({x},{y})")
        MOUSE["moving"] = False
    if MOUSE["scrolling"]:
        dx, dy = MOUSE["scroll"]
        log_entry("released", f"Mouse.scroll({dx},{dy})")
        MOUSE["scrolling"] = False


def on_press(key):
    check_mouse()
    log_entry("pressed", key)


def on_release(key):
    check_mouse()
    log_entry("released", key)


def on_move(x, y):
    MOUSE["location"] = [x, y]
    if not MOUSE["moving"]:
        log_entry("pressed", f"Mouse.move({x},{y})")
        MOUSE["moving"] = True


def on_scroll(x, y, dx, dy):
    MOUSE["location"] = [x, y]
    MOUSE["scroll"] = [dx, dy]
    if not MOUSE["scrolling"]:
        log_entry("pressed", f"Mouse.scroll({dx},{dy})")
        MOUSE["scrolling"] = True
        

def on_click(x, y, button, pressed):
    MOUSE["location"] = [x, y]
    
    check_mouse()
    string = f"Mouse.{button}.({x},{y})"
    if pressed:
        log_entry("pressed", string)
    else:
        log_entry("released", string)


# Setup the listener threads
keyboard_listener = KeyboardListener(on_press=on_press, on_release=on_release)
mouse_listener = MouseListener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)

# Start the threads and join them so the script doesn't end early
keyboard_listener.start()
mouse_listener.start()
keyboard_listener.join()
mouse_listener.join()