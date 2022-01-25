from typing import Literal
import shutil

from ._errors import DataIceExists
from ._base_archive import BaseArchiveHandler
from ._utils import PathType


class FileHandler:
    def __init__(self, parent_dir, file_name, mode="r"):
        self.file_obj = open(parent_dir / file_name, mode=mode)

    def __enter__(self):
        return self.file_obj

    def __exit__(self, type, value, traceback):
        self.file_obj.close()


class DirectoryHandler(BaseArchiveHandler):
    """A handler for saving/loading files to/from a directory."""

    _archive_type = "directory"

    def __init__(self, dir_path: PathType, mode: Literal["r", "w", "a"] = "r"):
        """

        Args:
            dir_path
        """
        super().__init__(dir_path)

        if mode == "r" and not self.path.exists():
            raise FileNotFoundError

        if mode == "w" and self.path.exists():
            shutil.rmtree(self.path)

        if not self.path.exists():
            self.path.mkdir()

    def open_file(self, file_name, mode="r"):
        return FileHandler(self.path, file_name, mode=mode)

    def save(self, **kwargs):
        """Save JSON strings to file with names from keyword arguments."""
        for arg, val in kwargs.items():
            with open(self.path / f"{arg}.json", "w") as open_file:
                open_file.write(val)

    def _read_key(self, key):
        with open(self.path / f"{key}.json", "r") as jf:
            return jf.read()

    def iter_json(self):
        """"""
        for key in self.keys():
            contents = self._read_key(key)
            yield key, contents

    def keys(self):
        """"""
        return tuple(json_file.stem for json_file in self.path.glob("*.json"))

    def __getitem__(self, item):
        """"""
        if item not in self.keys():
            raise KeyError(f"{item} is not a valid key")

        return self._read_key(item)
