import json


#  Loads raw JSON
def load_json(path):
    return json.load(open(path))


# Loads a JSON file as a json string
def load_json_string(path):
    json_dict = load_json(path)
    return json.dumps(json_dict)
