from pathlib import Path

directory = Path("logs/")

logs = []


def valid_line(line, index):
    parts = line.split(" - ")
    if len(parts) < 3:
        # print(index, line)
        return False
    else:
        return True


def break_line(line):
    line = line.rstrip()
    labels = ["time", "action", "key"]
    parts = line.split(" - ")
    d = {}
    # Note that this strips out mouse movement details
    for i, p in enumerate(parts):
        if i < 3:
            d[labels[i]] = p
    return d


def get_log_entries():
    log_list = []
    p = directory.glob("**/*")
    line_count = 0
    invalid = 0
    files = [x for x in p if x.is_file()]
    print(len(files))
    for q in files:
        print(q)
        with q.open() as f:
            for line in f:
                line_count += 1
                if valid_line(line, line_count):
                    log_list.append(break_line(line))
                else:
                    invalid += 1
            if invalid > 0:
                percent = round(100 * invalid / line_count, 2)
                print(f"Invalid lines: {percent}%")
    return log_list


def key(log_list, index):
    if index < len(log_list):
        return log_list[index]["key"]
    else:
        return "None"


def simplify_key_names(log_list):
    for entry in log_list:
        if len(entry["key"]) == 3:
            if entry["key"][0] == "'":
                if entry["key"][2] == "'":
                    entry["key"] = entry["key"][1]
    return log_list


def collapse_key_taps(log_list):
    """Consolidates entries of keys that were pressed and then released immediately."""

    skip = False
    new_list = []
    for i, this_entry in enumerate(log_list):
        if skip:
            skip = False
            continue
        elif i < len(log_list) - 1:
            if this_entry["key"] == key(log_list, i + 1):
                this_entry["action"] = "tapped"
                skip = True
        new_list.append(this_entry)
    return new_list


def collapse_hot_keys(log_list):
    skip = False
    new_list = []
    hot_keys = []
    for i, this_entry in enumerate(log_list):
        if skip > 0:
            skip = skip - 1
            continue
        elif i < len(log_list) - 2:
            if this_entry["action"] == "pressed":
                if key(log_list, i) == key(log_list, i + 2):
                    if "ctrl" in this_entry["key"] or "alt" in this_entry["key"]:
                        combo = f'{this_entry["key"]} + {key(log_list, i + 1)}'
                        hot_keys.append(combo)
                        this_entry["key"] = combo
                        skip = 2
                        continue
                    elif "shift" in this_entry["key"]:
                        next_entry = log_list[i + 1]
                        new_list.append(next_entry)
                        skip = 2
                        continue
        new_list.append(this_entry)
    print("Hot keys found:", len(hot_keys), "\n\n".join(hot_keys))
    return new_list


def collapse_key_rolling(log_list):
    """Consolidates keys that were pressed and released in a quick alternation."""

    # @todo look for rolls with three letters?
    def skip_key_same_key(index):
        if (index + 2) < len(log_list):
            if key(log_list, index) == key(log_list, index + 2):
                if log_list[index]["action"] == "pressed":
                    if log_list[index + 2]["action"] == "released":
                        return True
        return False

    def roll_found(index):
        return all([skip_key_same_key(index), skip_key_same_key(index + 1)])

    roll_count = 0
    skip = 0
    new_list = []
    for i, this_entry in enumerate(log_list):
        if skip > 0:
            skip = skip - 1
            continue
        if roll_found(i):
            new_list.append({"key": "ROLL FOUND", "action": "note"})
            # skip = 3
            roll_count += 1
        new_list.append(this_entry)
    # print("Rolls found:", roll_count)
    return new_list


# Run a quick test of this module
if __name__ == "__main__":
    logs = get_log_entries()
    print("Number of initial entries:", len(logs))
    logs = simplify_key_names(logs)
    logs = collapse_key_taps(logs)
    logs = collapse_hot_keys(logs)
    logs = collapse_hot_keys(logs)
    logs = collapse_key_rolling(logs)
    print("Number of collapsed entries:", len(logs))
