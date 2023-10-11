# Key-Logger
A combination of simple keylogger and T9-style keyboard construction for minamal input composition

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
- https://github.com/barrust/pyspellchecker/tree/master

## To Do
- performance
  - [x] start timing different operations
- practice
  - [ ] make a practice arena where layouts can be tested that tracks average speed and where mistakes are made
- analysis
  - [ ] start tracking what words are most likely to follow other words
  - [x] import usage data
  - [ ] import samples of ideal usage
    - [x] gather samples
    - [x] include also pre-compiled word dictionaries
  - [x] find words
    - [x] first, find and remove hotkeys
    - [x] take into account delete presses
    - [x] make a dictionary of word frequency
    - [ ] filter out/correct common mispellings
      - [ ] redirect common mispellings to the correct word
      - [ ] keep 'in versions of 'ing words
      - [ ] install and test https://github.com/barrust/pyspellchecker/tree/master
      - [ ] seems handy: `unknown([words])`
    - [ ] track by number but remove commas and new lines, except where they happen most frequently
  - [ ] support abbreviations and things like "dont" to "don't" (for apostrophes, dashes, and semicolons)
  - [ ] layout scoring
    - [ ] by word collisions (divided by the number of word uses in the dictionary that goes with it?)
      - [ ] see how much conflict increases with i and e together just for curiosity's sake (since that would make a lot of common mispellings moot)
    - [ ] try using the time data from logs to calculate average conflicts per minute
  - [x] find what characters conflict most
  - [x] assemble conflicts into possible key arrangements
  - [ ] make a companion webapp to practice/test with arbitrary keys assigned
  - [ ] export usable dictionary + layout
- logging
  - [ ] mouse clicks
  - [ ] mouse movements (with delta if possible)
  - [ ] scrolling
  - [x] log key up and key down separately
  - save logs:
    - [x] in dated files
    - [x] within a logs folder