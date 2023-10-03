from find_conflicts import get_conflict_data


def generate_keymap():
    conflict_dict = get_conflict_data()
    
    print(conflict_dict)
    
    # @todo read the wikipedia for "greedy algorithm" to see if those will help go from here


generate_keymap()
