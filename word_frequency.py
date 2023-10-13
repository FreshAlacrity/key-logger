
import export
from spellchecker import SpellChecker
from get_logs import get_all_logged_words


# Filter out any words that occur fewer than N times:
MIN = 5


def print_words_dict(word_dict):
    word_list = list(word_dict.items())
    word_list = sorted(word_list, key=lambda a: a[1])
    word_list.reverse()
    print(', '.join([f"'{x[0]}': {x[1]}" for x in word_list]))


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


def add_pk_export_names(word_dict, weight=10):
    """Sets a minimum frequency for all names from the PK export file
    in capitalized and lowercase forms, with and without preceding hypens."""
    
    names = export.get_names_list()

    def set_min(string):
        word_dict[string] = max(weight, word_dict.get(string, 0))
        string = string.lower()
        word_dict[string] = max(weight // 2, word_dict.get(string, 0))

    for name in names:
        set_min("-" + name)
        set_min(name)

    return word_dict


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
    string = export.break_string(string)
    return words_list_to_dict(string.split())


def make_dicts_for_samples():
    samples_dict = export.get_samples()
    for name, sample in samples_dict.items():
        sample_dict = {}
        
        for line in sample:
            combine_dict(sample_dict, string_to_dict(line), add=True)
        
        print(f"Exporting frequency dict for sample {name}")
        export.to_json(sample_dict, name, sample=True)
        
    # Add dict for descriptions from PK export
    descriptions = string_to_dict("\n".join(export.get_all_descriptions()))
    export.to_json(descriptions, "pk_descriptions", sample=True)


def sum_of_frequencies(word_dict):
    running_total = 0
    for value in word_dict.values():
        running_total += value
    return running_total


def include_sample_dicts(word_dict):
    cap = sum_of_frequencies(word_dict) // 4
    sample_dict_list = export.get_sample_dicts()
    for q in sample_dict_list:
        word_dict = combine_dict(word_dict, q, add=True, cap=cap)
    return word_dict


def check_for_mispelled_words(word_dict):
    spelling = SpellChecker()
    
    # @todo filter out kebab case by looking for words with hypens that aren't in the dictionary
    
    # @todo add a reference dicts folder to compare words to
    # and gather those words here to mark as known
    
    # print("\n".join(spelling.unknown(word_dict.keys())))
    # @todo
    return word_dict


def generate_word_dict():
    """Gets word data from logs and output samples
    and trims low quality words"""

    print("\nGetting logged words")
    word_dict = string_to_dict(' '.join(get_all_logged_words()))
    print(f"Words: {len(word_dict.keys())}")
    
    print("\nRemoving low frequency words")
    word_dict = low_bar(word_dict, min_val=MIN)
    print(f"Words: {len(word_dict.keys())}")
    
    print("\nAdding words from output samples")
    word_dict = include_sample_dicts(word_dict)
    print(f"Words: {len(word_dict.keys())}")

    # @todo add 'in versions of 'ing words
    
    print("\nChecking for mispellings")
    word_dict = check_for_mispelled_words(word_dict)
    print(f"Words: {len(word_dict.keys())}")
    
    # @todo troubleshoot why some BREAK_AT characters are included in words
    # they should each be registered as their own words

    print("\nAdding names from PK export")
    word_dict = add_pk_export_names(word_dict, weight=(MIN * 2))
    print(f"Words: {len(word_dict.keys())}")

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
        word_dict = export.read_in_dict_file("usage_dictionary")
        print("Imported dictionary export from earlier today")
    except FileNotFoundError:
        print("Dictionary export not found; making one now")
        
        word_dict = generate_word_dict()
        export.to_json(word_dict, "usage_dictionary")
        print("Dictionary exported...")

    return word_dict


# Run a quick test of this module
if __name__ == "__main__":
    # Doesn't need to always be running:
    make_dicts_for_samples()

    words_dict = get_word_dict(live=True)
    print_words_dict(words_dict)
    # get_word_dict()
