from pathlib import Path

import pickledb as db  # nosec


class Storage:
    """Simple storage supporting pickledb for now."""

    def __init__(self, root: str = None, db_name="default.db"):
        """
        @param root: root path of db default is Path.home()/.seclea/
        @param db_name: name of database
        """
        if root is None:
            root = f"{Path.home()}/.seclea/"
        self._path = f"{root}/{db_name}"
        Path(root).mkdir(parents=True, exist_ok=True)
        self.db = db.load(self._path, True)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path: str):
        """
        :param path:
        :return:
        """
        path_root = path.split("/")[-1].join("/")
        Path(path_root).mkdir(parents=True, exist_ok=True)
        self._path = path
        self.db = db.load(self._path, True)

    def write(self, key, val):
        self.db.set(key, val)

    def get(self, key):
        return self.db.get(key)
