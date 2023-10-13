from pathlib import Path
from export import read_in_dict_file
from export import to_json as export_to_json
from timetest import time_test
from json import load
from csv import reader as csv_reader

# Filters out any words that occur fewer than N times:
MIN = 10


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
    directory = Path("logs/")
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


@time_test("Keypress filter")  # pylint: disable=no-value-for-parameter
def filter_keypresses(log_list):
    """Removes any key entries that are not written characters and applies backspace uses"""
    # Time to beat is 3.5 seconds for 2487221 entries
    # Try making a tuple of the right length and then filling it in by tracking index?

    def is_char(entry):
        k = entry["key"]
        return len(k) == 3 and k[0] == "'" and k[2] == "'"

    new_list = []
    for entry in log_list:
        if is_char(entry):
            new_list.append(entry["key"][1])
        elif "backspace" in entry["key"]:
            del new_list[-1]
        else:
            new_list.append(" ")
    return new_list


def words_list_to_dict(word_list):
    def not_letter(a):
        # @todo also remove things like "b
        allowed = "abixy"
        a = a.lower()
        return a in allowed or not (len(a) == 1 and a.isalpha())

    def add_to_dict(word):
        found_word_dict[word] = found_word_dict.get(word, 0) + 1

    found_word_dict = {}
    for entry in word_list:
        if not_letter(entry):
            add_to_dict(entry)

    return found_word_dict


@time_test("Word building")  # pylint: disable=no-value-for-parameter
def build_words(new_list):
    return words_list_to_dict("".join(new_list).split())


def find_words_in_log(log_list):
    return build_words(filter_keypresses(log_list))


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

    new_dict = {}
    for word, value in words_dict.items():
        if (not word == "www") and (not word == "a"):
            if all(map(is_wasd, word)):
                if is_repeat(word) or is_nonsense(word):
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


@time_test("Get descriptions")  # pylint: disable=no-value-for-parameter
def get_all_descriptions():
    """Imports description text from PK export file."""
    with open("export.json", "r", encoding="utf-8") as f:
        members = load(f)["members"]
        d = "description"
        descriptions = [m[d] for m in members if m[d] is not None]
        return "\n".join(descriptions)


def dict_from_word_list(word_list, weight=10):
    word_dict = {}

    def set_min(string):
        word_dict[string] = max(weight + 1, word_dict.get(string, 0))
        string = string.lower()
        word_dict[string] = max(weight, word_dict.get(string, 0))

    for word in word_list:
        set_min("-" + word)
        set_min(word)

    return word_dict


def combine_dict(word_dict, dict_2, add=True, cap=None):
    multiply_by = 1
    if cap:
        total = sum_of_frequencies(dict_2)
        if total > cap:
            # Reduce the weight of dict entries
            multiply_by = cap // total
        
    for key in dict_2:
        value = multiply_by * dict_2[key]
        if add:
            word_dict[key] = word_dict.get(key, 0) + value
        else:
            word_dict[key] = max(word_dict.get(key, 0), value)

    return word_dict


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

    # Find any words in the logs
    return find_words_in_log(logs)


def string_to_dict(string):
    separate_words = ["\n", ".", ",", "\\", "/", "&", "=", "[", "]", ":", ";", "_"]
    # @later maybe also _ and - and other dividers?
    # @todo pull out elipses also so it doesn't just go like . . .
    for char in separate_words:
        string = string.replace(char, f" {char} ")
    return words_list_to_dict(string.split())


def make_dicts_for_samples():
    directory = Path("samples/")
    all_files = [x for x in directory.glob("*") if x.is_file()]

    for q in all_files:
        new_file_name = str(q)[len("samples/") : str(q).index(".")]
        print(f"Converting {new_file_name} into dict")
        with q.open(encoding="utf-8") as f:
            new_dict = {}
            for line in f:
                if ".csv" in str(q):
                    for cell in list(csv_reader([line]))[0]:
                        new_dict = combine_dict(new_dict, string_to_dict(cell), add=True)
                else:
                    new_dict = combine_dict(new_dict, string_to_dict(line), add=True)
            export_to_json(new_dict, new_file_name, sample=True)

    # Add dict for names from PK export
    names = dict_from_word_list(get_names_list(), weight=(MIN * 2))
    export_to_json(names, "pk_names", sample=True)

    # Add dict for descriptions from PK export
    descriptions = string_to_dict(get_all_descriptions())
    export_to_json(descriptions, "pk_descriptions", sample=True)


def sum_of_frequencies(word_dict):
    running_total = 0
    for value in word_dict.values():
        running_total += value
    return running_total


def include_sample_dicts(word_dict):
    print("Loading in sample dicts")

    directory = Path("samples/sample_dicts/")
    all_files = [x for x in directory.glob("*") if x.is_file()]
    cap = sum_of_frequencies(word_dict) // 4

    for q in all_files:
        with q.open(encoding="utf-8") as f:
            file_dict = load(f)
            word_dict = combine_dict(word_dict, file_dict, add=True, cap=cap)
    return word_dict
    

def tailor_word_dict(word_dict):
    """Increase the overall quality of the dictionary
    by removing spurious input and
    adding high quality data from other sources"""

    # Filter out WASD style inputs
    word_dict = filter_game_input(word_dict)

    # Retrieve and add any output samples (/samples directory)
    word_dict = include_sample_dicts(word_dict)
    
    print(f"Total word count: {sum_of_frequencies(word_dict)}")

    # Filter out words that really don't show up much
    word_dict = low_bar(word_dict, min_val=MIN)
    
    print(f"Total word count: {sum_of_frequencies(word_dict)}")

    # @todo filter out misspellings here using pyspellcheck

    return word_dict


def get_word_dict(live=False):
    """Return a completed dictionary of words
    with a value for how often they appear,
    either by generating one with all recent data
    or retrieving one generated earlier in the same day"""

    try:
        if live:
            # @later find a more elegant way to do this?
            raise FileNotFoundError("Don't use the file")
        word_dict = read_in_dict_file("usage_dictionary")
        print("Imported dictionary export from earlier today")
    except FileNotFoundError:
        print("Dictionary export not found; making one now")

        word_dict = get_all_logged_words()

        word_dict = tailor_word_dict(word_dict)

        export_to_json(word_dict, "usage_dictionary")
        print("Dictionary exported...")

    return word_dict


# Run a quick test of this module
if __name__ == "__main__":
    # Doesn't need to always be running:
    # make_dicts_for_samples()
    #218155
    #1645660978
    get_word_dict(live=True)
    # get_word_dict()
