import pandas
from export import conflict_csv_file_path
from export import to_json as export_to_json


def get_file():
    fp = conflict_csv_file_path()
    # with open(fp, encoding="utf-8", newline='') as f:
    data = pandas.read_csv(fp)
    raw_dict = data.set_index('Compare').to_dict()
    
    def raw(key):
        """Removes changes to CSV headers to work with Google Sheets"""
        if key[0:2] == '="':
            return key[2]
        else:
            return key

    new_dict = {}
    for key, entry in raw_dict.items():
        new_dict[raw(key)] = {}
        for char, val in entry.items():
            if not pandas.isna(val):
                new_dict[raw(key)][raw(char)] = int(val)
                # @later figure out how to import as integers directly

    return new_dict
        
def find_conflicts():
    try:
        word_dict = get_file()
        print("Imported conflict data exported earlier today")
    except FileNotFoundError:
        print("Conflict data export not found; making one now")
        # @todo
        # print("Conflict data exported...")

    # @todo figure out some way to filter out misspellings
    # Levenshtein distance from a common word?

    return word_dict