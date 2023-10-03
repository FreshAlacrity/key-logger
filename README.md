# Key-Logger
 A simple keylogger to gather data locally for analysing possible keyboard layouts

## Setup
This will need to be done any time the file is moved!

Windows Defender Antivirus picks this up - it needs to be manually allowed to be able to run/not get deleted;
To exclude the folder on my version of Windows 11 (and to change it back again later) go to:
Settings -> Windows Security settings -> Virus & Threat Protection -> Virus  & threat protections settings (header) -> Manage settings -> Exclusions -> Add or remove exclusions

To run on startup, make a shortcut to main.pyw and add it to your startup folder or add the file to the windows registry (HKCU\Software\Microsoft\Windows\CurrentVersion\Run)

## Resources
- https://docs.python.org/3/library/pathlib.html
- https://pynput.readthedocs.io/en/latest/keyboard.html
- https://www.askpython.com/python/examples/python-keylogger
- https://docs.python.org/3/library/functions.html#open

## To Do
- analysis
  - [x] find words
    - [x] first, find and remove hotkeys
    - [x] take into account delete presses
    - [x] make a dictionary of word frequency
    - [ ] filter out common mispellings
  - [x] find what characters conflict most
  - [ ] assemble conflicts into possible key arrangements
- logging
  - [ ] add logging for:
    - [ ] mouse clicks
    - [ ] mouse movements (with delta if possible)
    - [ ] scrolling
  - [x] log key up and key down separately
  - save logs:
    - [x] in dated files
    - [x] within a logs folder