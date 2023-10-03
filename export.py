import csv
import json
from datetime import date


def format_as_rows(conflict_dict):
    rows = []
    for key, vals in conflict_dict.items():
        vals["Compare"] = key
        rows.append(vals)
    return rows


def to_csv(conflict_dict):
    # @todo replace = with ="=" and ' with ="'"
    with open(f"exports/conflicts-{date.today()}.csv", "w", newline="") as f:
        headers = list(conflict_dict.keys())
        headers.insert(0, "Compare")
        print(headers)
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(format_as_rows(conflict_dict))


def to_json(word_dict):
    with open(f"exports/dictionary-{date.today()}.json", "w", encoding="utf-8") as f:
        json.dump(word_dict, f, ensure_ascii=False, indent=4)
