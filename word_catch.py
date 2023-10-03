from pathlib import Path
from json import load

directory = Path("logs/")


def get_log_entries():
    def break_line(line):
        line = line.rstrip()
        labels = ["time", "action", "key"]
        parts = line.split(" - ")
        line_dict = {}
        for i, p in enumerate(parts):
            line_dict[labels[i]] = p
        return line_dict

    log_list = []
    p = directory.glob("**/*")
    files = [x for x in p if x.is_file()]
    for q in files:
        with q.open() as f:
            for line in f:
                log_list.append(break_line(line))
    return log_list


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


def prune_release(log_list):
    return list(filter(lambda a: not a["action"] == "released", log_list))


def find_words(log_list):
    def not_letter(a):
        # Since there are only two one-letter words in English:
        if a == "I" or a == "a":
            return True
        else:
            return not (len(a) == 1 and a.isalpha())

    def is_char(entry):
        k = entry["key"]
        return len(k) == 3 and k[0] == "'" and k[2] == "'"

    new_list = []
    for entry in log_list:
        if is_char(entry):
            new_list.append(entry["key"][1])
        elif "backspace" in entry["key"]:
            new_list.append("<-")
        else:
            new_list.append(" ")

    found_word_dict = {}
    word_builder = ""
    for entry in new_list:
        if entry == "<-":
            word_builder = word_builder[0 : len(word_builder) - 1]
        elif entry == " ":
            # Add only sequences that are words or symbols, not blank
            if not word_builder == "":
                word_builder = word_builder.lower()
                if not_letter(word_builder):
                    if word_builder in found_word_dict:
                        found_word_dict[word_builder] += 1
                    else:
                        found_word_dict[word_builder] = 1
                    word_builder = ""
        else:
            word_builder += entry

    return found_word_dict


def words_dict_to_list(word_dict, required=2):
    word_list = list(word_dict.items())
    word_list = filter(lambda a: a[1] > required, word_list)
    word_list = sorted(word_list, key=lambda a: a[1])
    word_list.reverse()
    return word_list


def print_words(words_list):
    print(
        f"Words found: {len(words_list)}\n",
        "\n".join(map(lambda a: f"{a[0]}: {a[1]}", words_list)),
    )


def filter_game_input(words_dict):
    # @todo filter out game input/strings that are only WASD and not actual words like "dad" and "was"
    def is_just(word, letter):
        return all(map(lambda l : l == letter, word))
    
    def is_repeat(word):
        word = word.lower()
        return any(map(lambda a : is_just(word, a), "wasd"))
    
    def is_nonsense(word, value):
        if not any(map(lambda a : a == "a", word)):
            # Just w, s, and d? Very likely to be nonsense
            return True
        elif word[0] == "a" and is_just(word[1:len(word)], "w"):
            # Some variation of awwwwww is not nonsense
            return False
        else:
            # If it's longer than 15 letters, nonsense
            return len(word) > 15
        
    def is_wasd(letter):
        letter = letter.lower()
        return letter == "w" or letter == "a" or letter == "s" or letter == "d"
    
    new_dict = {}
    for word, value in words_dict.items():
        if (not word == "www") and (not word == "a"):
            if all(map(is_wasd, word)):
                if is_repeat(word) or is_nonsense(word, value):
                    continue
        new_dict[word] = value
        
    return new_dict


def low_bar(words_dict, min_val=5):
    new_dict = {}
    
    for word, value in words_dict.items():
        if value > min_val:
            new_dict[word] = value
    
    return new_dict


def get_names_list():
    """Imports names list from PK export file."""
    with open("export.json", "r", encoding="utf-8") as f:
        export = load(f)
        return list(map(lambda a: a["name"], export["members"]))


def add_names(word_dict, weight=10):
    def set_min(string):        
        if string in word_dict:
            word_dict[string] = max(weight + 1, word_dict[string])
        else:
            word_dict[string] = weight + 1
        if string.lower() in word_dict:
            word_dict[string.lower()] = max(weight, word_dict[string.lower()])
        else:
            word_dict[string.lower()] = weight
            
    for name in get_names_list():
        set_min("-" + name)
        set_min(name)
        
    return word_dict


def get_word_dict():
    # Retrieve and parse all the new logs
    logs = get_log_entries()

    # Take out any hotkeys so they don't clog up words
    logs = catch_hotkeys(logs)

    # Pare those down into only when keys are pressed
    logs = prune_release(logs)

    # Retrieve and add old logs
    logs = logs + get_old_log()

    # Find any words in the logs
    word_dict = find_words(logs)

    # Filter out words that really don't show up much
    word_dict = low_bar(word_dict, min_val=5)
    
    # Add names from PK export
    word_dict = add_names(word_dict, weight=10)
    
    # Filter out WASD style inputs
    word_dict = filter_game_input(word_dict)

    # @todo figure out some way to filter out misspellings
    # Levenshtein distance from a common word?

    return word_dict
