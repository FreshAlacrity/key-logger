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
