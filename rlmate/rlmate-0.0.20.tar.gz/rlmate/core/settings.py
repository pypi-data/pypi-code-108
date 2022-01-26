import git
import os
from copy import deepcopy
from pathlib import Path


def get_repo_path():
    try:
        repo = git.Repo(".", search_parent_directories=True)
        return repo.working_tree_dir
    # TODO what exception does gitpython throw if git is not available??
    except:
        raise RuntimeError("""
            Cannot use git repository root path as hermes root path, as git is not available!
            Please specify a root path manually with the --root option
        """)


# Dictionary of settings with default value:
DEFAULT_SETTINGS = {"path_to_experiments": "./", "threads": 1}


def add_to_dictionary(dictionary, line, delimiter, line_number):
    if line.startswith("bot_id") or line.startswith("chat_id"):
        return True
    try:
        key, value = line.split(delimiter)
    except:
        print("line " + str(line_number) + ": " + line + " does not fit convention")
        return False
    try:
        t = type(DEFAULT_SETTINGS[key])
    except:
        print("line " + str(line_number) + ": " + key + " setting does not exist")
        return False
    try:
        dictionary[key] = t(value)
    except:
        print(
            "line "
            + str(line_number)
            + ": "
            + value
            + " could not be casted to needed type ("
            + t
            + ")"
        )
        return False

    return True

def get_settings_fp(path_to_root=None):
    if path_to_root is None:
        path_to_root = get_repo_path()
    settings_file = os.path.join(path_to_root, ".hermes_settings")
    return path_to_root, settings_file

def load(path_to_root=None):
    """checks whether the repo has a .hermes_settings file
    loads the given settings if there os one is
    uses the default settings else"""
    settings = deepcopy(DEFAULT_SETTINGS)
    path_to_root, settings_file = get_settings_fp(path_to_root)
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            for i, line in enumerate(f):
                line = line.replace(" ", "")
                line = line.replace("\n", "")
                add_to_dictionary(settings, line, ":", i)

    relative_path = settings["path_to_experiments"]
    absolute_path = Path(path_to_root).absolute()
    settings["path_to_experiments"] = str(Path.joinpath(absolute_path, relative_path))
    return settings


def create_settings_file(path_to_root=None):
    """checks whether the repo has a .hermes_settings file
    gives an error if there is one
    else creates an hermes_settings file with the default values"""
    path_to_root, settings_file = get_settings_fp(path_to_root)
    if os.path.exists(settings_file):
        raise FileExistsError("A hermes settings file already exists!")
    else:
        with open(settings_file, "w") as f:
            for i, key in enumerate(DEFAULT_SETTINGS):
                s = str(key) + ":" + str(DEFAULT_SETTINGS[key])
                if i != len(DEFAULT_SETTINGS):
                    s += "\n"
                f.write(s)
