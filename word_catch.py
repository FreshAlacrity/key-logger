
from pathlib import Path

directory = Path("logs/")


def get_log_entries():
    def break_line(line):
        line = line.rstrip()
        labels = ["time", "action", "key"]
        parts = line.split(" - ")
        line_dict = {}
        for i, p in enumerate(parts):
            line_dict[labels[i]] = p
        return line_dict
    log_list = []
    p = directory.glob("**/*")
    files = [x for x in p if x.is_file()]
    for q in files:
        with q.open() as f:
            for line in f:
                log_list.append(break_line(line))
    return log_list


def get_old_log():
    log_list = []
    with open("old_log.txt", "r", encoding="utf-8") as f:
        for line in f:
            log_list.append({ "key": line.rstrip(), "action": "pressed" })
    return log_list


def prune_release(log_list):
    return list(filter(lambda a: not a["action"] == "released", log_list))


def find_words(log_list):
    def not_letter(a):
        # Since there are only two one-letter words in English:
        if a == "I" or a == "a":
            return True
        else:
            return not (len(a) == 1 and a.isalpha())
        
    def is_char(entry):
        k = entry["key"]
        return (len(k) == 3 and k[0] == "'" and k[2] == "'")
    
    new_list = []
    for entry in log_list:
        if is_char(entry):
            new_list.append(entry["key"][1])
        elif "backspace" in entry["key"]:
            new_list.append("<-")
        else:
            new_list.append(" ")

    found_word_dict = {}
    word_builder = ""
    for entry in new_list:
        if entry == "<-":
            word_builder = word_builder[0:len(word_builder) - 1]
        elif entry == " ":
            # Add only sequences that are words or symbols, not blank
            if not word_builder == '':
                word_builder = word_builder.lower()
                if not_letter(word_builder):
                    if word_builder in found_word_dict:
                        found_word_dict[word_builder] += 1
                    else:
                        found_word_dict[word_builder] = 1
                    word_builder = ""
        else:
            word_builder += entry

    return found_word_dict


def words_dict_to_list(word_dict, required=2):
    word_list = list(word_dict.items())
    word_list = filter(lambda a : a[1] > required, word_list)
    word_list = sorted(word_list, key=lambda a : a[1])
    word_list.reverse()
    return word_list


def print_words(words_list):
    print(
        f"Words found: {len(words_list)}\n",
        "\n".join(map(lambda a : f"{a[0]}: {a[1]}", words_list)),
    )


def get_word_dict():
    # Retrieve and parse all the new logs
    logs = get_log_entries()
    
    # Pare those down into only when keys are pressed
    logs = prune_release(logs)
    
    # Retrieve and parse the old log file
    old_logs = get_old_log()
    
    # Combine both lists
    logs = logs + old_logs
    
    # Find any words in the logs
    word_dict = find_words(logs)
    
    return word_dict