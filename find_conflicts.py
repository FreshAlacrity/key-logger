import pandas  # pylint: disable=import-error
from export import conflict_csv_file_path
from export import to_csv as export_to_csv
from word_frequency import get_word_dict
from word_frequency import low_bar
from word_frequency import make_dicts_for_samples
from timetest import time_test

# Minimum occurances for both words and characters
MIN = 2

def char_frequency(word_dict):
    char_dict = {}
    for word in word_dict:
        for letter in word:
            char_dict[letter] = char_dict.get(letter, 0) + 1
    return char_dict


@time_test("Find character pair conflict")  # pylint: disable=no-value-for-parameter
def find_conflicts(word_dict, char_a, char_b):
    # @todo break this down into two functions: one that lists groups of conflicting words and another that adds up the penalties (since it'd be interesting to see)
    # Needs to be something that isn't in the characters already in the dict:
    not_a_char = " "
    penalty = 0
    censored_dict = {}
    for word, num in word_dict.items():
        if char_a in word or char_b in word:
            # Censor the char and add to the set
            censored = word.replace(char_a, not_a_char)
            censored = censored.replace(char_b, not_a_char)
            censored_dict[censored] = censored_dict.get(censored, []) + [num]
    for _, penalties in censored_dict.items():
        if len(penalties) > 1:
            penalties.remove(max(*penalties))
            for val in penalties:
                penalty += val
    return penalty


def find_unique_chars(word_dict):
    # Find all unique characters that occur more often than just by themselves
    all_chars_dict = char_frequency(word_dict)
    all_chars = [x for x in all_chars_dict.keys() if all_chars_dict[x] > 2]
    print(f"Characters assembled: {''.join(all_chars)}")
    return all_chars


def add_synonyms(word_dict):
    """Strip the 's out of words and add those versions to the dict"""
    
    new_dict = {}
    for word, value in word_dict.items():
        new_dict[word] = value
        if "'" in word or "-" in word or ";" in word:
            s = word.replace("'", '')
            s = word.replace("-", '')
            s = word.replace(";", '')
            new_dict[s] = new_dict.get(s, 0) + value
            # print(s)  # @todo figure out why this is catching *a lot* of things
    return new_dict
    
# @todo split this into sub-functions
@time_test("Find character conflicts")  # pylint: disable=no-value-for-parameter
def find_character_conflicts(word_dict):
    """Finds the data you want for minimizing collisions on an overloaded keyboard."""
    
    word_dict = add_synonyms(word_dict)
    
    def in_conflict_dict(char_a, char_b):
        return char_b in char_a

    def add_conflict(char_a, char_b, conflict):
        if not char_a in conflict_dict:
            conflict_dict[char_a] = {char_b: conflict}
        else:
            conflict_dict[char_a][char_b] = conflict

    # Remove low-frequency words:
    word_dict = low_bar(word_dict, MIN)
    
    all_chars = find_unique_chars(word_dict)

    conflict_dict = {}

    # For every combination of characters, see how many are in both sets:
    for char_a in all_chars:
        print(f"Finding conflicts for {char_a}")
        for char_b in all_chars:
            if not char_a == char_b and not in_conflict_dict(char_a, char_b):
                conflict_value = find_conflicts(word_dict, char_a, char_b)
                add_conflict(char_a, char_b, conflict_value)
                add_conflict(char_b, char_a, conflict_value)

    return conflict_dict


# @todo move this to export.py
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
    lowercase_version = {}
    for word, occurances in word_dict.items():
        word = word.lower()
        lowercase_version[word] = lowercase_version.get(word, 0) + occurances
    return lowercase_version


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
    # Refresh the word frequency dictionary
    make_dicts_for_samples()
    get_word_dict(live=True)
    test_export_import()
