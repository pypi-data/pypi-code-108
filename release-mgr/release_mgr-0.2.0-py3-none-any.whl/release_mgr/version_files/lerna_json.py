import json

from release_mgr.git import git
from release_mgr.version_files.version_file import VersionFile


class LernaJSON(VersionFile):
    filename = "lerna.json"

    def update(self, version: str):
        with open("lerna.json") as pkg_json_file:
            pkg_json = json.loads(pkg_json_file.read())
            pkg_json["version"] = version

        with open("package.json", "w") as pkg_json_file:
            json.dump(
                pkg_json,
                pkg_json_file,
                indent=2,
            )

        git("add", self.filename)
        return True
