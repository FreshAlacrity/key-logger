import export
from spellchecker import SpellChecker
from get_logs import get_all_logged_words


# Filter out any words that occur fewer than N times:
MIN = 2
MISPELLED = {}

def print_words_dict(word_dict):
    word_list = list(word_dict.items())
    word_list = sorted(word_list, key=lambda a: a[1])
    word_list.reverse()
    print(", ".join([f"'{x[0]}': {x[1]}" for x in word_list]))


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
    with and without preceding hypens."""

    names = export.get_names_list()

    def set_min(string):
        word_dict[string] = max(weight, word_dict.get(string, 0))

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
        # @later figure out how to say what source things are from?
        q = spellcheck(q)
        word_dict = combine_dict(word_dict, q, add=True, cap=cap)
    return word_dict


def spellcheck(word_dict):
    def is_known(word, value):
        tests = [word]
        unknown = spelling.unknown(tests)
        if len(word) == 1:
            return True
        elif not unknown:
            return True
        else:
            # Check for camel case:
            new_word = ""
            for i, c in enumerate(word):
                new_word += c
                if i < len(word) - 1:
                    n = word[i + 1]
                    if c == c.lower() and n == n.upper():
                        new_word += "-"
            tests = [new_word]

            # Check for breaks in the word
            for char in "-–—_/#<>":
                new_tests = []
                for l in [x.split(char) for x in tests]:
                    for e in l:
                        new_tests.append(e)
                tests = new_tests
            
            tests = [x for x in tests if not x == '']
            unknown = spelling.unknown(tests)
            for subword in unknown:
                MISPELLED[subword] = MISPELLED.get(subword, 0) + value
            if not unknown:
                return True
        MISPELLED[word] = MISPELLED.get(word, 0) + value
        return False

    print("\nChecking for misspellings")
    spelling = SpellChecker()
    new_dict = {}

    # Mark words in the _words.json sample dict as known
    known_words = export.read_in_dict_file("_words", sample=True)
    spelling.word_frequency.load_words(known_words.keys())

    for word, value in word_dict.items():
        # @later consider how strict to be here with MIN
        # Checking first if it's known to make a complete dict of 'mispellings'
        if is_known(word, value) or value > MIN:
            new_dict[word] = value
        #else:
            #if word_dict[word] >= 2:  # MIN:
            #    print(f"{word} ({value})")
        # Finding corrections takes a LONG time
        # print(f"{word} - {spelling.correction(word)}?")

        # Get a list of `likely` options
        # print(spelling.candidates(word))

    # @todo
    return word_dict


def generate_word_dict():
    """Gets word data from logs and output samples
    and trims low quality words"""

    print("\nGetting logged words")
    # @todo have this import a list of lines instead
    word_dict = words_list_to_dict(get_all_logged_words())
    print(f"Words: {len(word_dict.keys())}")
    word_dict = spellcheck(word_dict)
    print(f"Words: {len(word_dict.keys())}")

    # print("\nRemoving low frequency words")
    # word_dict = low_bar(word_dict, min_val=MIN)

    print("\nAdding words from output samples")
    word_dict = include_sample_dicts(word_dict)
    print(f"Words: {len(word_dict.keys())}")

    # @todo add 'in versions of 'ing words
    # @todo troubleshoot why some WASD input is still ending up in misspellings
    # @todo troubleshoot why some BREAK_AT characters are included in words
    # they should each be registered as their own words

    print("\nAdding names from PK export")
    word_dict = add_pk_export_names(word_dict, weight=(MIN * 2))
    print(f"Words: {len(word_dict.keys())}")

    return word_dict


def get_word_dict(live=False):
    return export.get_dict("usage_dictionary", generate_word_dict, live=live)


# Run a quick test of this module
if __name__ == "__main__":
    # Doesn't need to always be running:
    # @later just check for ones that haven't been compiled?
    make_dicts_for_samples()

    # @later make a way to get an archived version of logged words only?
    words_dict = get_word_dict(live=True)
    # words_dict = get_word_dict()
    # print_words_dict(words_dict)

    #personal_dict = export.read_in_dict_file("alacrity", sample=True)
    # spellcheck({ "hard-of-hearing": 2, "some-day": 4 })
    MISPELLED = low_bar(MISPELLED, min_val=5)
    export.to_json(MISPELLED, "misspelled")