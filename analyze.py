from pathlib import Path

directory = Path("logs/")

logs = []

def break_line(line):
    line = line.rstrip()
    labels = ["time", "action", "key"]
    parts = line.split(' - ')
    dict = {}
    for i, p in enumerate(parts):
        dict[labels[i]] = p
    return dict
    
def get_log_entries():
    log_list = []
    p = directory.glob('**/*')
    files = [x for x in p if x.is_file()]
    print(len(files))
    for q in files:
        with q.open() as f:
            for line in f:
                log_list.append(break_line(line))
    return log_list

def collapse_keys_actions(log_list):
    """Compares keys to the keys pressed and released before and after and consolidates entries of keys pressed and released immediately"""
    new_list = []
    skip = False
    for i, this_entry in enumerate(log_list):
        if skip:
            skip = False
            continue
        elif i < len(log_list) - 1:
            next_entry = log_list[i + 1]
            if this_entry["action"] == next_entry["action"]:
                this_entry["action"] = "tapped"
                skip = True
        new_list.append(this_entry)
    return new_list


logs = get_log_entries()
print("Number of initial entries:", len(logs))
logs = collapse_keys_actions(logs)
print("Number of collapsed entries:", len(logs))