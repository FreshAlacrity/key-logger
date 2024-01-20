import csv
import json
from datetime import date
from pathlib import Path


def lazy_version(word):
    if "'" in word or "-" in word or ";" in word:
        word = word.replace("'", '')
        word = word.replace("-", '')
        word = word.replace(";", '')
    return word


def break_string(string):
    # @todo handle these with the regex module
    # @todo allow groups of these without spaces (so like ?! and ... and ```)
    
    # Treat these symbols as independent words
    BREAK_AT = "\n | \" . , \\ / & = + [ ] ( ) { } : _ @ $ ? ! * ` “ ” -- – ‘ ’".split()
    for char in BREAK_AT:
        string = string.replace(char, f" {char} ")
        
    # Treat these as words if they occur at the start or end of a word
    string = f" {string} "
    for char in "' - ;".split():
        string = string.replace(f"{char} ", f" {char} ")
        string = string.replace(f" {char}", f" {char} ")
    
    # Break up html tags
    # @todo regex - make sure it's not >= that I'm breaking up
    string = string.replace(">", "> ")
    string = string.replace("<", " <")
    return string

    
def get_names_list():
    """Imports names list from PK export file."""
    with open("export.json", "r", encoding="utf-8") as f:
        export = json.load(f)
        return list(map(lambda a: a["name"], export["members"]))


def get_all_descriptions():
    """Imports description text from PK export file."""
    with open("export.json", "r", encoding="utf-8") as f:
        members = json.load(f)["members"]
        d = "description"
        descriptions = [m[d] for m in members if m[d] is not None]
        return descriptions


def get_samples():
    directory = Path("samples/")
    all_files = [x for x in directory.glob("*") if x.is_file()]

    all_samples = {}
    for q in all_files:
        new_file_name = str(q)[len("samples/") : str(q).index(".")]
        print(f"Retrieving sample {new_file_name}")
        with q.open(encoding="utf-8") as f:
            file_list = []
            for line in f:
                if ".csv" in str(q):
                    for cell in list(csv.reader([line]))[0]:
                        if cell not in file_list:
                            file_list.append(cell)
                else:
                    file_list.append(line)
            all_samples[new_file_name] = file_list
    return all_samples


def get_sample_dicts():
    print("Loading in sample dicts")

    directory = Path("samples/sample_dicts/")
    all_files = [x for x in directory.glob("*") if x.is_file()]
    
    dict_list = []
    for q in all_files:
        with q.open(encoding="utf-8") as f:
            dict_list.append(json.load(f))
            
    return dict_list


def get_log_entries():
    def break_line(line):
        line = line.rstrip()
        labels = ["time", "action", "key"]
        parts = line.split(" - ", 2)
        if not len(parts) == 3:
            # Partial lines occur when the logger is interrupted or the log edited
            raise KeyError(f"This line does not have the required parts: {line}")
        line_dict = {}
        for i, p in enumerate(parts):
            line_dict[labels[i]] = p
        return line_dict

    log_list = []
    directory = Path("logs/")
    p = directory.glob("**/*")
    files = [x for x in p if x.is_file()]
    for q in files:
        with q.open() as f:
            for line in f:
                log_list.append(break_line(line))
    return log_list


def format_as_rows(conflict_dict):
    rows = []
    for key, vals in conflict_dict.items():
        vals["Compare"] = key
        rows.append(vals)
    return rows


def conflict_csv_file_path():
    return f"exports/conflicts-{date.today()}.csv"


def json_file_path(dict_type, sample=False):
    if not sample:
        return f"exports/{dict_type}-{date.today()}.json"
    else:
        return f"samples/sample_dicts/{dict_type}.json"


def to_json(dict_obj, dict_type, sample=False):
    """Import a previously exported JSON file by string/reference"""
    file_path = json_file_path(dict_type, sample)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dict_obj, f, ensure_ascii=False, indent=4)


def read_in_dict_file(dict_type, sample=False):
    """Retrieve a JSON file with the word dictionary stored earlier today"""
    file_path = json_file_path(dict_type, sample)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def to_csv(conflict_dict):
    """Pulls in a CSV with row and column headers"""
    def safe(key):
        """Alters CSV headers to work with Google Sheets"""
        if key == "=":
            return '="="'
        elif key == "'":
            return '="\'"'
        else:
            return key

    new_dict = {}
    for key, entry in conflict_dict.items():
        new_dict[safe(key)] = {}
        for char, val in entry.items():
            new_dict[safe(key)][safe(char)] = val

    with open(conflict_csv_file_path(), "w", newline="", encoding="utf-8") as f:
        headers = list(new_dict.keys())
        headers.insert(0, "Compare")
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(format_as_rows(new_dict))


def get_dict(dict_type, get_with, live=False):
    """Return a completed dictionary of words
    with a value for how often they appear,
    either by generating one with all recent data
    or retrieving one generated earlier in the same day"""

    try:
        if live:
            # @later find a more elegant way to do this?
            raise FileNotFoundError("Don't use the file")
        result = read_in_dict_file(dict_type)
        print(f"Imported {dict_type} export from earlier today")
    except FileNotFoundError:
        print(f"Exported {dict_type} not found; making one now")
        
        result = get_with()
        to_json(result, dict_type)
        print(f"Exported {dict_type}")

    return result


if __name__ == "__main__":
    print(len(get_log_entries()))
    #print(break_string("  foo... 'Tuesday-morning' oh gosh! -why!?"))