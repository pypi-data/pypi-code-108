from .Settings import Settings
from PyQt6.QtGui import QIcon
from pathlib import Path
import platform
import json
import os


class Enviroment():
    def __init__(self):
        self.program_dir = os.path.dirname(os.path.realpath(__file__))
        self.data_dir = self._get_data_path()

        try:
            os.makedirs(self.data_dir)
        except Exception:
            pass

        self.version = "3.0"

        self.icon = QIcon(os.path.join(self.program_dir, "Icon.svg"))

        self.settings = Settings()
        self.settings.load(os.path.join(self.data_dir, "settings.json"))

        try:
            with open(os.path.join(self.data_dir, "recentfiles.json"), "r", encoding="utf-8") as f:
                self.recent_files = json.load(f)
        except Exception:
            self.recent_files = []

        with open(os.path.join(self.program_dir, "data", "metadata_licenses.json"), "r", encoding="utf-8") as f:
            self.metadata_license_list = json.load(f)

        # Source: https://github.com/spdx/license-list-data/blob/master/json/licenses.json
        with open(os.path.join(self.program_dir, "data", "project_licenses.json"), "r", encoding="utf-8") as f:
            self.project_license_list = json.load(f)

        with open(os.path.join(self.program_dir, "data", "categories.txt"), "r", encoding="utf-8") as f:
            self.categories = f.read().splitlines()

        with open(os.path.join(self.program_dir, "data", "langcodes.txt"), "r", encoding="utf-8") as f:
            self.language_codes = f.read().splitlines()

        # Source: https://github.com/ximion/appstream/blob/master/data/platforms.yml
        self.platform_list = []
        with open(os.path.join(self.program_dir, "data", "platform.json"), "r", encoding="utf-8") as f:
            platform_data = json.load(f)
            for architecture in platform_data["architectures"]:
                for kernel in platform_data["os_kernels"]:
                    for environment in platform_data["os_environments"]:
                        self.platform_list.append(architecture + "-" + kernel + "-" + environment)

    def _get_data_path(self) -> str:
        if platform.system() == "Windows":
            return os.path.join(os.getenv("appdata"), "jdAppdataEdit")
        elif platform.system() == "Darwin":
            return os.path.join(str(Path.home()), "Library", "Application Support", "jdAppdataEdit")
        elif platform.system() == "Haiku":
            return os.path.join(str(Path.home()), "config", "settings", "jdAppdataEdit")
        else:
            if os.getenv("XDG_DATA_HOME"):
                return os.path.join(os.getenv("XDG_DATA_HOME"), "jdAppdataEdit")
            else:
                return os.path.join(str(Path.home()), ".local", "share", "jdAppdataEdit")

    def save_recent_files(self):
        save_path = os.path.join(self.data_dir, "recentfiles.json")
        if len(self.recent_files) == 0 and not os.path.isfile(save_path):
            return
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.recent_files, f, ensure_ascii=False, indent=4)
