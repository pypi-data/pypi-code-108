import os
import pickle

from iosdebug.constants import DATA_FILE


def store_mocked_implementation(protocol_to_mocked_contents, path):
    data = {"mock_implementations": protocol_to_mocked_contents}

    with open(path + os.sep + DATA_FILE, "wb") as file:
        pickle.dump(str(data), file)
