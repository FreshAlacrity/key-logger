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


## Known Issues
- newline isn't showing up as a word
- emojis that occur frequently in PK descriptions are being over-represented
  - lock those in frequency to the corresponding names?
- emojis assigned to single keys would be hard to use: instead use the discord word-name + synonyms and abbreviate common ones, so all I'd need to do to get the :ram: emoji is get to "ram" and then hit the "next" key
- no support for having a word immediately followed by another character or word
 - space, backspace and then new word?
- repeating strings of BREAK_AT characters won't be recognized well
  - so ??? and ... etc
- some strings aren't being broken correctly by BREAK_AT strings
- not sure how to handle emojis and other unusual characters
- WASD input filtering is so-so
  - filter by blocks of text so things like "sad" and "dad" aren't overcounted

### Fixed
- project ids (C59D6EC4 etc) are over-represented
  - now only allowing unique cells from csv samples
  - exported project sheet with only text cells, removing ID columns
- names often register as mispelled
  - add names after checking spelling

## To Do
- performance
  - [x] start timing different operations
- practice
  - [ ] export usable dictionary + layout
  - [ ] make a companion webapp to practice/test with arbitrary keys assigned
      - [ ] track average speed and where mistakes are made
- analysis
  - [ ] what words are most likely to precede and follow a given word
    - [ ] if a word is extremely often followed or preceded by another, group them into one word (so for example, ".py" and ".png" should be considered words)
    - [ ] catch strings with : on either end since those are emoji references
  - [x] import usage data
  - [ ] import and include samples of ideal usage
    - [x] gather samples
      - [ ] add a list of countries, major cities, and names of language (in English and in the native language)
    - [x] include also pre-compiled word dictionaries
  - [x] find words
    - [x] first, find and remove hotkeys
    - [x] take into account delete presses
    - [x] make a dictionary of word frequency
  - [ ] filter out/correct common mispellings
    - [x] install and test https://github.com/barrust/pyspellchecker/tree/master
    - [ ] import keys from the reference dictionary of *not* mispelled words
    - [ ] redirect common mispellings to the correct word
    - [ ] don't correct 'in versions of 'ing words
    - [ ] seems handy: `unknown([words])`
  - [x] track by number but remove commas and new lines
    - [ ] track where they happen most frequently and re-include those as "words"
    - [x] filter commas out of CSVs correctly
  - [x] support abbreviations and things like "dont" to "don't" (for apostrophes, dashes, and semicolons)
  - [ ] layout scoring
    - [ ] by word collisions (divided by the number of word uses in the dictionary that goes with it?)
      - [ ] see how much conflict increases with i and e together just for curiosity's sake (since that would make a lot of common mispellings moot)
    - [ ] try using the time data from logs to calculate average conflicts per minute
  - [x] find what characters conflict most
  - [x] assemble conflicts into possible key arrangements
- logging
  - [ ] mouse clicks
  - [ ] mouse movements (with delta if possible)
  - [ ] scrolling
  - [x] log key up and key down separately
  - save logs:
    - [x] in dated files
    - [x] within a logs folder