import os
import pickle
import re
from ast import literal_eval

from iosdebug.constants import DATA_FILE
from iosdebug.templates import SHAKABLE_NC_INSTANCE


def set_original_root_view_controller(swift_files, path_to_content_map, path):
    print("Assigning original rootViewController instance...")
    with open(path + os.sep + DATA_FILE, "rb") as file:
        data = pickle.load(file)
        data = literal_eval(data)

    for file_path in swift_files:
        with open(file_path, "r") as file:
            content = file.read()
            path_to_content_map[file_path] = content
            root_vc_property = re.findall(
                r"= (ShakableNavigationController.*)", content
            )
            if root_vc_property:
                content = content.replace(
                    root_vc_property[0], data["original_root_view_controller"]
                )
                content = content.split("\n// MARK: - Debug mode helper classes")[0]
                with open(file_path, "w") as file:
                    file.write(content)
    print("Original rootViewController instance assinged.")
