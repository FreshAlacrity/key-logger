import csv

def format_as_rows(conflict_dict):
    rows = []
    for key, vals in conflict_dict.items():
        vals["Compare"] = key
        rows.append(vals)
    return rows

def export_to_csv(conflict_dict):
    # @todo date the export
    # @todo replace = with ="=" and ' with ="'"
    with open('conflicts.csv', 'w', newline='') as file: 
        headers = list(conflict_dict.keys())
        headers.insert(0, "Compare")
        print(headers)
        writer = csv.DictWriter(file, fieldnames = headers)
        writer.writeheader()
        writer.writerows(format_as_rows(conflict_dict))
