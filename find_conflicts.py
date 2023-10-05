import pandas  # pylint: disable=import-error
from export import conflict_csv_file_path
from export import to_csv as export_to_csv
from word_catch import get_word_dict
from timetest import time_test


def char_frequency(word_dict):
    char_dict = {}
    for word, num in word_dict.items():
        for letter in word:
            if letter in char_dict:
                char_dict[letter] += num
            else:
                char_dict[letter] = num
    return char_dict


def find_conflicts(word_dict, char_a, char_b):
    # @todo break this down into two functions: one that lists groups of conflicting words and another that adds up the penalties (since it'd be interesting to see)
    # Needs to be something that isn't in the characters already in the dict:
    not_a_char = " "
    penalty = 0
    censored_dict = {}
    for word, num in word_dict.items():
        if num > 5 and (char_a in word or char_b in word):
            # Censor the char and add to the set
            censored = word.replace(char_a, not_a_char)
            censored = censored.replace(char_b, not_a_char)
            if censored in censored_dict:
                censored_dict[censored].append(num)
            else:
                censored_dict[censored] = [num]
    for _, penalties in censored_dict.items():
        if len(penalties) > 1:
            penalties.remove(max(*penalties))
            for val in penalties:
                penalty += val
    return penalty


@time_test("Find character conflicts")  # pylint: disable=no-value-for-parameter
def find_character_conflicts(word_dict):
    """Finds the data you want for minimizing collisions on an overloaded keyboard."""

    # @todo split this into sub-functions

    # Find all unique characters
    all_chars = char_frequency(word_dict).keys()
    print("Characters counted...")

    conflict_dict = {}

    def in_conflict_dict(char_a, char_b):
        return char_b in char_a

    def add_conflict(char_a, char_b, conflict):
        if not char_a in conflict_dict:
            conflict_dict[char_a] = {char_b: conflict}
        else:
            conflict_dict[char_a][char_b] = conflict

    find_conflicts(word_dict, "e", "x")

    # For every combination of characters, see how many are in both sets:
    for char_a in all_chars:
        print(f"Finding conflicts for {char_a}")
        for char_b in all_chars:
            if not char_a == char_b and not in_conflict_dict(char_a, char_b):
                conflict_value = find_conflicts(word_dict, char_a, char_b)
                add_conflict(char_a, char_b, conflict_value)
                add_conflict(char_b, char_a, conflict_value)

    return conflict_dict


def get_file():
    fp = conflict_csv_file_path()
    
    # Read in the data (and automatically close the file)
    data = pandas.read_csv(fp)
    raw_dict = data.set_index("Compare").to_dict()

    def raw(key):
        """Removes changes to CSV headers to work with Google Sheets"""
        if key[0:2] == '="':
            return key[2]
        else:
            return key

    new_dict = {}
    for key, entry in raw_dict.items():
        new_dict[raw(key)] = {}
        for char, val in entry.items():
            if not pandas.isna(val):
                new_dict[raw(key)][raw(char)] = int(val)
                # @later figure out how to import as integers directly

    return new_dict


def lowercase(word_dict):
    lowercase_word_dict = {}
    for word, occurances in word_dict.items():
        word = word.lower()
        if word in lowercase_word_dict:
            lowercase_word_dict[word] += occurances
        else:
            lowercase_word_dict[word] = occurances
    return lowercase_word_dict


def get_conflict_data(live=False):
    try:
        if live:
            # @later find a more elegant way to do this?
            raise FileNotFoundError("Don't use the file")
        conflict_data = get_file()
        print("Imported conflict data exported earlier today")
    except FileNotFoundError:
        print("Conflict data export not found; making one now")
        conflict_data = find_character_conflicts(lowercase(get_word_dict()))
        export_to_csv(conflict_data)
        print("Conflict data exported...")

    return conflict_data


@time_test("Test import/export")  # pylint: disable=no-value-for-parameter
def test_export_import():
    test_1 = get_conflict_data(live=True)
    test_2 = get_conflict_data()
    errors_found = False
    for char_a, entries in test_1.items():
        for char_b in entries.keys():
            q = test_1[char_a][char_b]
            r = test_2[char_a][char_b]
            if not q == r:
                errors_found = True
    if not errors_found:
        print("Import/Export test successful")


# Run a quick test of this module
if __name__ == "__main__":
    test_export_import()
