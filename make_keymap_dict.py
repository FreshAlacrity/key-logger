from generate_layout import generate_keymap
from word_frequency import get_word_dict
from timetest import time_test
from export import lazy_version
from export import get_dict


@time_test("Assemble keymapped dictionary")  # pylint: disable=no-value-for-parameter
def assemble_dictionary(key_arr, word_dict):
    
    """Takes an array of what characters are assigned to which keys and assembles a dictionary of words that can be produced with different keycode sequences"""
    
    def build_translation_dict():
        """Take the characters in the word and turn them into key index numbers"""
        trans_x = ""
        trans_y = ""
        for index, sublist in enumerate(key_arr):
            index = str(index)
            for char in sublist:
                trans_y += index + index
                trans_x += char + char.upper()
        return str.maketrans(trans_x, trans_y)
    
    def get_keycode(word):
        return word.translate(key_dict)
    
    # Makes a translation key for translating key letters into key index numbers
    key_dict = build_translation_dict()
    
    final_dict = {}
    for word, num in word_dict.items():
        key = get_keycode(word)
        final_dict[key] = final_dict.get(key, []) + [(word, num)]
        
        # Also add contractions, abbreviations etc:
        if lazy_version(word) != word:
            key_2 = get_keycode(lazy_version(word))
            final_dict[key_2] = final_dict.get(key_2, []) + [(word, num)]
        
    # Sort each list by frequency
    for keycode in final_dict:
        if len(final_dict[keycode]) > 1:
            final_dict[keycode].sort(reverse=True, key=lambda w : w[1])
            #if final_dict[keycode][1][1] > 100:
                #print(final_dict[keycode])

    return { "keymap": key_arr, "dictionary": final_dict }


def make_keymap_dict():
    return assemble_dictionary(generate_keymap(), get_word_dict())


def get_keymap_dict(live=False):
    return get_dict("keymap_dictionary", make_keymap_dict, live=live)


# Run a quick test of this module
if __name__ == "__main__":
    print(get_keymap_dict(live=True))
