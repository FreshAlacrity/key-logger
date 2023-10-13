from pathlib import Path
from export import read_in_dict_file
from export import to_json as export_to_json
from timetest import time_test
from json import load
from csv import reader as csv_reader
from spellchecker import SpellChecker
from get_logs import get_all_logged_words

# Filters out any words that occur fewer than N times:
MIN = 10

# Treats these symbols as independent words:
BREAK_AT = "\n | \" . , \\ / & = + [ ] ( ) : ; _ @ $ ? ! **".split()
# @todo allow groups of these without spaces once preceding/following words are supported


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


def add_pk_export_names(word_dict, weight=10):
    """Sets a minimum frequency for all names from the PK export file
    in capitalized and lowercase forms, with and without preceding hypens."""
    
    names = get_names_list()

    def set_min(string):
        word_dict[string] = max(weight, word_dict.get(string, 0))
        string = string.lower()
        word_dict[string] = max(weight // 2, word_dict.get(string, 0))

    for name in names:
        set_min("-" + name)
        set_min(name)

    return word_dict


# @todo track precedes and follows here
def words_list_to_dict(word_list):
    def not_letter(a):
        # Letters allowed to be words by themselves:
        allowed = "abixyz"
        a = a.lower()
        return a in allowed or not (len(a) == 1 and a.isalpha())

    def add_to_dict(word):
        found_word_dict[word] = found_word_dict.get(word, 0) + 1

    found_word_dict = {}
    for entry in word_list:
        if not_letter(entry):
            add_to_dict(entry)

    return found_word_dict


def combine_dict(word_dict, dict_2, add=True, cap=None):
    multiply_by = 1
    if cap:
        total = sum_of_frequencies(dict_2)
        if total > cap:
            # Reduce the weight of dict entries
            multiply_by = cap / total

    for key in dict_2:
        # Tamp down the frequency of words from large dictionaries
        value = max(int(dict_2[key] * multiply_by), 1)
        if add:
            word_dict[key] = word_dict.get(key, 0) + value
        else:
            word_dict[key] = max(word_dict.get(key, 0), value)

    return word_dict


def string_to_dict(string):
    for char in BREAK_AT:
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
                    unique_strings = []
                    for cell in list(csv_reader([line]))[0]:
                        if cell not in unique_strings:
                            unique_strings.append(cell)
                    for s in unique_strings:
                        new_dict = combine_dict(new_dict, string_to_dict(s), add=True)
                else:
                    new_dict = combine_dict(new_dict, string_to_dict(line), add=True)
            export_to_json(new_dict, new_file_name, sample=True)

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


def check_for_mispelled_words(word_dict):
    spelling = SpellChecker()
    
    # @todo filter out kebab case by looking for words with hypens that aren't in the dictionary
    
    # @todo add a reference dicts folder to compare words to
    # and gather those words here to mark as known
    
    # print("\n".join(spelling.unknown(word_dict.keys())))
    # @todo


def tailor_word_dict(word_dict):
    """Includes data from previously analysed output samples
    and trims low quality words"""

    print(f"Words: {len(word_dict.keys())}")
    
    print("Removing low frequency words")
    word_dict = low_bar(word_dict, min_val=MIN)
    
    print(f"Words: {len(word_dict.keys())}")
    
    print("Adding words from output samples")
    word_dict = include_sample_dicts(word_dict)

    print(f"Words: {len(word_dict.keys())}")

    # @todo add 'in versions of 'ing words
    
    print("Checking for mispellings")
    check_for_mispelled_words(word_dict)
    # @todo troubleshoot why some BREAK_AT characters are included in words

    print("Adding names from PK export")
    word_dict = add_pk_export_names(word_dict, weight=(MIN * 2))

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
            
        word_dict = string_to_dict(' '.join(get_all_logged_words()))
        
        print(f"Words: {len(word_dict.keys())}")
        
        word_dict = tailor_word_dict(word_dict)
        
        print(f"Words: {len(word_dict.keys())}")

        export_to_json(word_dict, "usage_dictionary")
        print("Dictionary exported...")

    return word_dict


# Run a quick test of this module
if __name__ == "__main__":
    # Doesn't need to always be running:
    # make_dicts_for_samples()

    get_word_dict(live=True)
    # get_word_dict()
