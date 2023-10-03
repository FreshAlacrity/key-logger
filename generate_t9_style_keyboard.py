import export
from word_catch import get_word_dict


def all_words(lowercase=True):
    # Get words from all the logs
    word_dict = get_word_dict()

    if not lowercase:
        return word_dict
    else:
        lowercase_word_dict = {}
        for word, occurances in word_dict.items():
            word = word.lower()
            if word in lowercase_word_dict:
                lowercase_word_dict[word] += occurances
            else:
                lowercase_word_dict[word] = occurances
        return lowercase_word_dict


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
        for char_b in all_chars:
            if not char_a == char_b and not in_conflict_dict(char_a, char_b):
                print(f"Comparing {char_a} and {char_b}")
                conflict_value = find_conflicts(word_dict, char_a, char_b)
                add_conflict(char_a, char_b, conflict_value)
                add_conflict(char_b, char_a, conflict_value)

    return conflict_dict


def generate_keymap():
    print("Retrieving words...")
    
    word_dict = all_words(lowercase=True)
    print("Word dict acquired...")
    
    conflict_dict = find_character_conflicts(word_dict)
    print("Conflicts found...")

    export.to_csv(conflict_dict)
    print("Conflicts exported...")
    
    # @todo read the wikipedia for "greedy algorithm" to see if those will help go from here


generate_keymap()
