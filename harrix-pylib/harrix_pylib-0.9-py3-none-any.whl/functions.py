from pathlib import Path
from typing import Union
import shutil
import re


def path_to_pathlib(path: Union[Path, str]) -> Path:
    """If a string is passed to the function, it turns into Path from pathlib.

    Args:
      path: string of path or Path from pathlib.

    Returns:
      Path from pathlib.
    """
    return Path(path) if isinstance(path, str) else path


def clear_directory(path: Union[Path, str]) -> None:
    """This function clear directory with sub-directories.

    Args:
      path: path of directory from pathlib.

    Returns:
      None.
    """
    path = path_to_pathlib(path)
    if path.is_dir():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def open_file(filename: Union[Path, str]) -> str:
    """This function open file as UTF8 text file.

    Args:
      filename: name of the file to open.

    Returns:
      Text file content.
    """
    filename = path_to_pathlib(filename)
    s = ""
    with open(filename, "r", encoding="utf8") as file:
        s = file.read()
    return s


def save_file(text: str, full_filename: Union[Path, str]) -> None:
    """This function save file as UTF8 text file.

    Args:
      text: text for saving.
      full_filename: name of the file to save.

    Returns:
      None.
    """
    filename = path_to_pathlib(full_filename)
    with open(filename, "w", encoding="utf8") as file:
        file.write(text)


def remove_yaml_from_markdown(markdown_text: str) -> str:
    """Function remove YAML from text of markdown file.

    Args:
      markdown_text: text of markdown file.

    Returns:
      Text of markdown file without YAML.
    """
    return re.sub(r"^---(.|\n)*?---\n", "", markdown_text.lstrip()).lstrip()
