
from timetest import time_test
from export import get_log_entries

@time_test("Keypress filter")  # pylint: disable=no-value-for-parameter
def filter_keypresses(log_list):
    """Removes any key entries that are not written characters and applies backspace uses"""
    # Time to beat is 3.5 seconds for 2487221 entries
    # @later Try making a tuple of the right length and then filling it in by tracking index?
    
    def is_char(entry):
        k = entry["key"]
        return (len(k) == 3 and k[0] == "'" and k[2] == "'") or k == '"\'"'

    new_list = []
    for entry in log_list:
        if is_char(entry):
            new_list.append(entry["key"][1])
        elif "backspace" in entry["key"]:
            del new_list[-1]
        else:
            new_list.append("\n")
    return new_list


@time_test("Word building")  # pylint: disable=no-value-for-parameter
def build_words(log_list):
    return "".join(filter_keypresses(log_list)).split()


def prune_release(log_list):
    return list(filter(lambda a: not a["action"] == "released", log_list))


def catch_hotkeys(log_list):
    def has_hotkey(key):
        return "ctrl" in key or "alt" in key

    new_list = []
    skip = 0
    for i, this_entry in enumerate(log_list):
        if skip > 0:
            skip = skip - 1
            continue
        elif this_entry["action"] == "pressed":
            if has_hotkey(this_entry["key"]):
                found = False
                while not found:
                    skip += 1
                    # This prevents an error when the word_catch is run *while* holding a key down from a hotkey:
                    if skip < len(log_list):
                        if this_entry["key"] == log_list[i + skip]["key"]:
                            found = True
                continue
        new_list.append(this_entry)
    return new_list


def get_old_log():
    log_list = []
    with open("old_log.txt", "r", encoding="utf-8") as f:
        for line in f:
            log_list.append({"key": line.rstrip(), "action": "pressed"})
    return log_list


# @todo recognize chunks of WASD input instead so things like "dad" and "sad" don't get overrepresented
def filter_game_input(words_list):
    """Filter out game input/strings that are only WASD and
    not actual words like 'dad' and 'was'"""

    def is_just(word, letter):
        return all(map(lambda l: l == letter, word))

    def is_repeat(word):
        word = word.lower()
        return any(map(lambda a: is_just(word, a), "wasd"))

    def is_nonsense(word):
        if not any(map(lambda a: a == "a", word)):
            # Just w, s, and d? Very likely to be nonsense
            return True
        elif word[0] == "a" and is_just(word[1 : len(word)], "w"):
            # Some variation of awwwwww is not nonsense
            return False
        else:
            # If it's longer than 15 letters, nonsense
            return len(word) > 15

    def is_wasd(letter):
        letter = letter.lower()
        return letter == "w" or letter == "a" or letter == "s" or letter == "d"

    new_list = []
    for word in words_list:
        if (not word == "www") and (not word == "a") and (not word == "wasd"):
            if all(map(is_wasd, word)):
                if is_repeat(word) or is_nonsense(word):
                    continue
        new_list.append(word)

    return new_list


def get_all_logged_words():
    """Pull in both the new and old style logs
    and simplify them into individual words"""

    # Retrieve and parse all the new logs
    logs = get_log_entries()

    # Take out any hotkeys so they don't clog up words
    logs = catch_hotkeys(logs)

    # Pare those down into only when keys are pressed
    logs = prune_release(logs)
    
    # Retrieve and add old logs
    logs = logs + get_old_log()

    # Return any words found in the logs
    logged_words = build_words(logs)
    print("Logged words found")
    
    logged_words = filter_game_input(logged_words)
    print("Logged words filtered")
    
    return logged_words
  
  
  # Run a quick test of this module
if __name__ == "__main__":
    get_all_logged_words()