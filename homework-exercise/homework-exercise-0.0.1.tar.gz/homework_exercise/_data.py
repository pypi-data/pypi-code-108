import json
import os

with open(os.path.join(os.path.dirname(__file__), "data_file.json"), encoding="utf-8") as f_p:
    DATA_DICT = json.load(f_p)

_DATA2_DICT = None

def delay_data():
    global _DATA2_DICT
    if _DATA2_DICT is not None:
        return _DATA2_DICT

    import toml

    _DATA2_DICT = toml.load(os.path.join(os.path.dirname(__file__), "data_file_2.toml"))
    return _DATA2_DICT