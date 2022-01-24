import os
from typing import List, Optional


class DKIgnore(object):
    _defaults = [".DS_Store", ".dk", "compiled-recipe"]
    _ignore_file_name = ".dkignore"
    _ignore_these = []

    def __init__(self, dk_temp_folder: Optional[str]) -> None:
        self._ignore_these = None
        if dk_temp_folder:
            try:
                with open(os.path.join(dk_temp_folder, self._ignore_file_name), "r") as ignore_file:
                    self._ignore_these = self._defaults + [
                        l.strip() for l in ignore_file if not l.strip().startswith("#") and l.strip()
                    ]
            except IOError:
                # Ignore file is optional, so might not be present
                pass
        if not self._ignore_these:
            self._ignore_these = self._defaults

    def ignore(self, check_item: str) -> bool:
        matches = next((item for item in self._ignore_these if item in check_item), None)
        if matches is None:
            return False
        else:
            return True

    def add_ignore(self, ignore_this_item: str) -> None:
        self._ignore_these.append(ignore_this_item)

    def get_ignore_files(self) -> List[str]:
        return self._ignore_these
