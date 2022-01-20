import os
import pickle
from ast import literal_eval

from iosdebug.constants import DATA_FILE


def store_mocked_implementations(path_to_content_map, root_path):
    print("Removing and storing mock implementations...")
    with open(root_path + os.sep + DATA_FILE, "rb") as file:
        data = pickle.load(file)
        data = literal_eval(data)
    for protocol in data["mock_implementations"]:
        for path in path_to_content_map:
            content = path_to_content_map[path]
            if "class Mock" + protocol in content:
                content_split = content.split("\n// MARK: - Mock implementation")
                if len(content_split) > 1:
                    data["mock_implementations"][protocol] = content_split[1]
                    with open(path, "w") as file:
                        file.write(content_split[0])
    with open(root_path + os.sep + DATA_FILE, "wb") as file:
        pickle.dump(str(data), file)
    print("Mock implementations removed and stored.")
