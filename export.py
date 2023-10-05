import csv
import json
from datetime import date


def format_as_rows(conflict_dict):
    rows = []
    for key, vals in conflict_dict.items():
        vals["Compare"] = key
        rows.append(vals)
    return rows


def conflict_csv_file_path():
    return f"exports/conflicts-{date.today()}.csv"


def json_file_path(dict_type):
    return f"exports/{dict_type}-{date.today()}.json"


def to_csv(conflict_dict):
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


def to_json(dict_obj, dict_type):
    with open(json_file_path(dict_type), "w", encoding="utf-8") as f:
        json.dump(dict_obj, f, ensure_ascii=False, indent=4)


def read_in_dict_file(dict_type):
    """Retrieve a JSON file with the word dictionary stored earlier today"""
    file_path = json_file_path(dict_type)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)