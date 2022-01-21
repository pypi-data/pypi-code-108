import os
import re

from release_mgr.git import git


class VersionFile:
    """
    Represents a file which would contain the version.
    """

    filename = ""
    pattern = re.compile("")
    replace_pattern = "{new_version}"

    def __init__(self, content=""):
        self.content = content

    @classmethod
    def from_file(cls):
        if os.path.exists(cls.filename):
            obj = cls()
            obj.load_content()
            return obj

        return None

    def load_content(self):
        with open(self.filename, encoding="utf-8") as existing:
            self.content = existing.read()

    def subst(self, version):
        return self.pattern.sub(
            self.replace_pattern.format(new_version=version),
            self.content,
        )

    def update(self, version: str):
        if not self.pattern:
            raise Exception("Tried to update a file without a pattern!")

        if not self.content:
            self.load_content()

        if self.pattern.search(self.content) is None:
            return False

        new_content = self.subst(version)

        with open(self.filename, "w", encoding="utf-8") as new:
            new.write(new_content)

        git("add", self.filename)
        return True
