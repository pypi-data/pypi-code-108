import re
import shutil
from pathlib import Path
from typing import List


def read_file_to_list(path: Path) -> List[str]:
    return path.read_text().split("\n")


def get_file_paths(folder_path: Path, file_path: Path, ignore_dirs: List[str] = None) -> List[Path]:
    return [
        d / file_path
        for d in folder_path.iterdir()
        if d.is_dir() and (d / file_path).exists() and (ignore_dirs is not None and d.name not in ignore_dirs)
    ]


def sub_file_content(path: Path, regex: str, new_content: str) -> None:
    content = path.read_text()
    path.write_text(re.sub(regex, new_content, content))


def write(path: Path, content: str) -> None:
    path.write_text(content)


def copy_dir(src: Path, dest: Path) -> None:
    shutil.copytree(src, dest, dirs_exist_ok=True)  # type: ignore
