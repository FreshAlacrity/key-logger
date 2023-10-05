from find_conflicts import get_conflict_data
from timetest import time_test


@time_test("Generate keymap")  # pylint: disable=no-value-for-parameter
def generate_keymap():
    def print_key_arr():
        for index, keys in enumerate(key_arr):
            print(f"Key {index + 1}: {' '.join(keys)}")
        print("\n")

    @time_test("Highest total conflict")  # pylint: disable=no-value-for-parameter
    def highest_total_conflict():
        running_max = 0
        holds_max = ""
        for char_a, obj in conflict_dict.items():
            total = 0
            for _, value in obj.items():
                total += value
            if total > running_max:
                holds_max = char_a
                running_max = total
        return (holds_max, running_max)

    def assigned_chars():
        return [item for sublist in key_arr for item in sublist]

    @time_test("Conflict product dict")  # pylint: disable=no-value-for-parameter
    def conflict_product_dict(char_list):
        """Finds the product of conflicts with the set of characters"""
        temp_dict = {}
        for char_a in char_list:
            for char_b in conflict_dict[char_a]:
                if char_b not in char_list:
                    if char_b in temp_dict:
                        temp_dict[char_b] *= conflict_dict[char_a][char_b] + 1
                    else:
                        temp_dict[char_b] = conflict_dict[char_a][char_b] + 1
        return temp_dict

    @time_test("Most conflicting")  # pylint: disable=no-value-for-parameter
    def most_conflicting(char_list):
        """Finds the character that conflicts most with the set of characters"""
        temp_dict = conflict_product_dict(char_list)
        heck = max(temp_dict.values())
        return tuple(filter(lambda a: a[1] == heck, temp_dict.items()))[0]

    @time_test("Narrow conflict product")  # pylint: disable=no-value-for-parameter
    def narrow_conflict_product(char_b, char_lists):
        """Finds the index of the group of characters that conflicts least with this char"""
        products_by_index = [1] * len(char_lists)
        for index, sublist in enumerate(char_lists):
            for char_a in sublist:
                products_by_index[index] *= conflict_dict[char_a][char_b] + 1
        index_of_min = products_by_index.index(min(products_by_index))
        return index_of_min

    def add_to_key(char, index=-1):
        remaining_chars.remove(char)

        if index == -1:
            key_arr.append([char])
        else:
            key_arr[index].append(char)

    print("Getting conflict data...")
    conflict_dict = get_conflict_data()

    remaining_chars = list(conflict_dict.keys())

    MAX_KEYS = 6  # Conflict values currently drop around this point
    key_arr = []

    # Put the character with the highest total conflict as Key 1
    add_to_key(highest_total_conflict()[0], index=-1)

    # Fill in the first set of characters
    while len(key_arr) < MAX_KEYS:
        # Add as a new key the key that conflicts most with all assigned keys
        worst_bud = most_conflicting(assigned_chars())
        # print(worst_bud[1] ** (1.0 / len(assigned_chars())))
        add_to_key(worst_bud[0], index=-1)

    # Continue adding characters until there are none left
    while len(remaining_chars) >= 1:
        # Find the key that conflicts most with the assigned keys
        worst_bud = most_conflicting(assigned_chars())

        # Figure out the least worst place to put it
        best_place = narrow_conflict_product(worst_bud[0], key_arr)
        add_to_key(worst_bud[0], best_place)

    print_key_arr()
    
    # @todo add to layouts.json
    
    # @todo sort characters by frequency of letter press, for strict entry?

    # @todo Test if the relative number of presses per key are similar
    
    return key_arr


# Run a quick test of this module
if __name__ == "__main__":
    print(generate_keymap())
    
