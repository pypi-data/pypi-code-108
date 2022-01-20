import os
import pickle
from ast import literal_eval

from iosdebug.constants import DATA_FILE, KEY_MOCK_IMPLEMENTATIONS


def get_stored_mock_implementation(path, repository_name):
    with open(path + os.sep + DATA_FILE, "rb") as file:
        content = pickle.load(file)
        dictionary = literal_eval(content)
        mock_implementations = dictionary[KEY_MOCK_IMPLEMENTATIONS]
        if repository_name in mock_implementations:
            return mock_implementations[repository_name]
