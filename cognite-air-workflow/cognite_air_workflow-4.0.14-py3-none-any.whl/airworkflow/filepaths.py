import os
from pathlib import Path
from typing import List

from cognite.airworkflow.util import env

working_path = env.get_env_value("PWD")
ROOT_DIR = Path(working_path)
FUNCTIONS_PATH = ROOT_DIR / "functions"
IGNORE_MODELS_PATH = ROOT_DIR / ".ignore_models"

# Paths within a functions folder
FUNCTION_REL_PATH = Path("function")
FUNCTION_REL_CONFIG_PATH = FUNCTION_REL_PATH / "config.yaml"


def read_file_to_list(path: Path) -> List[str]:
    return path.read_text().split("\n")


def get_relative_function_path(path: Path) -> str:
    return "/".join(path.parts[path.parts.index("functions") + 1 :])  # noqa


def getpathstring(function_names: List[str]) -> None:
    start = '{"function":'
    escape_string = '"'
    escaped_string = list(map(lambda v: escape_string + v + escape_string, function_names))
    function_names_str = f"[{', '.join(escaped_string)}]"
    final_string = start + function_names_str + "}"
    print(final_string, flush=True)


def get_directory_paths() -> List[str]:
    ignore_models = read_file_to_list(IGNORE_MODELS_PATH)
    directory_contents = os.listdir(FUNCTIONS_PATH)
    directory_paths = list(
        map(lambda x: FUNCTIONS_PATH / x, filter(lambda x: x not in ignore_models, directory_contents))
    )
    function_paths = [x for x in directory_paths if os.path.isdir(x)]

    return sorted(map(get_relative_function_path, function_paths))


if __name__ == "__main__":
    function_names = get_directory_paths()
    getpathstring(function_names)
