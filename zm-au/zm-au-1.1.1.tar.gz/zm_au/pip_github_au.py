import importlib
import json
import os
import subprocess
import sys
from typing import Optional

import packaging.version
from zetuptools import PipPackage

from .base_au import BaseAU, UpdateException


class PipGitHubAU(BaseAU):

    def __init__(self, name: str, github_location: str, check_prerelease: bool = False, dist: str = "whl", silent: bool = False):
        # If silent, redirect output of pip to the null device
        # Other parameters tell which uploads to look for and where (note that github_location's format is like "zmarffy/au")
        self._pip_package = PipPackage(name)
        self.github_location = github_location
        self.check_prerelease = check_prerelease
        self.dist = dist
        self.silent = silent
        super().__init__()

    @property
    def _o(self) -> Optional[int]:
        # Determines what to redirect output to
        if self.silent:
            return subprocess.DEVNULL
        else:
            return None

    def _get_current_version(self) -> str:
        return self._pip_package.version

    def _get_latest_version(self) -> str:
        # Uses `gh api` to find the latest version
        try:
            d = json.loads(subprocess.check_output(
                ["gh", "api", f"repos/{self.github_location}/releases"]))
        except subprocess.CalledProcessError:
            raise UpdateException(
                f"Either {self.github_location} doesn't exist or you need to authorize with GitHub (run `gh auth login`) before attempting to check for updates for it")
        if not self.check_prerelease:
            latest = next(x for x in d if not x["prerelease"])
        else:
            latest = d[0]
        return latest["tag_name"]

    def _download(self) -> str:
        # Uses `gh release download` to download the version found from _get_latest_version (doesn't blindly install the latest version to avoid a super rare race condition)
        subprocess.run(["gh", "release", "download", self.latest_version,
                        "-R", self.github_location, "-p", f"*.{self.dist}"], stdout=self._o)
        files = os.listdir()
        if len(files) != 1:
            raise ValueError(
                f"Ambiguous install instructions as multiple files were downloaded. Files: {files}")
        return files[0]

    def _update(self, update_file: str):
        # Installs a file with `pip install`
        subprocess.run([sys.executable, "-m", "pip",
                        "install", update_file], stdout=self._o)
        try:
            importlib.import_module(
                f"{self._pip_package.name}.install_directives")
            has_id = True
        except ModuleNotFoundError:
            has_id = False
        if has_id:
            subprocess.run(
                ["install-directives", self._pip_package.name, "install"])

    @property
    def currently_installed_version_is_unreleased(self) -> bool:
        module = importlib.import_module(self._pip_package.name)
        try:
            return module.__dev__
        except AttributeError:
            return bool(packaging.version.parse(module.__version__).local)
