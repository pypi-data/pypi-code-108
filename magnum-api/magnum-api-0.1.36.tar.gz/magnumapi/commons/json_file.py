import json

def read(json_file_path: str) -> dict:
    """ Static method reading a json file and returning a list of dictionaries with block definitions.

    :param json_file_path: a path to a json file
    :return: a list of dictionaries with geometry definition (block definition)
    """
    #todo: add check if the file exists - as a decorator
    with open(json_file_path) as f:
        return json.load(f)