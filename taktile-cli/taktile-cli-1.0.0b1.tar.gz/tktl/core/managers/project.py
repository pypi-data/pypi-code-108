import os
import pathlib
import pkgutil
import sys
from typing import Optional

from tktl import __version__
from tktl.core.loggers import LOG
from tktl.core.managers.base import BaseConfigManager
from tktl.core.managers.constants import TEMPLATE_PROJECT_DIRS, TEMPLATE_PROJECT_FILES
from tktl.core.t import TemplateT
from tktl.core.validation.project import validate_project_contents


class ProjectManager(BaseConfigManager):
    """Manages project configuration tktl.yaml file."""

    TKTL_DIR: Optional[str] = None
    CONFIG_FILE_NAME: str = "tktl.yaml"
    CONFIG: Optional[dict] = None

    @classmethod
    def set_path(cls, path: str) -> None:
        cls.TKTL_DIR = path

    @classmethod
    def init(cls, path: str, name: str, template: TemplateT) -> None:
        cls.create_dir(path)
        cls.set_path(path)
        cls.init_config(name)
        cls.create_template(template)

    @classmethod
    def init_project(cls, path: Optional[str], name: str, template: TemplateT) -> str:
        if not path:
            path = os.path.expanduser(".")
        project_path = os.path.join(path, name)
        if os.path.isdir(project_path):
            cls.safe_init(project_path, name, template)
        else:
            cls.init(project_path, name, template)
        return project_path

    @classmethod
    def safe_init(cls, path: str, name: str, template: TemplateT) -> None:
        LOG.log(
            "WARNING: Path specified already exists. "
            "Any configuration will be overwritten. Proceed?[Y/n]",
            color="yellow",
        )
        overwrite = input()
        if overwrite == "Y":
            cls.init(path, name, template)
        elif overwrite == "n":
            sys.exit()
        else:
            cls.safe_init(path, name, template)

    @classmethod
    def create_template(cls, template: TemplateT) -> None:
        cls.create_subdirs()
        cls.copy_dist_files(template)

    @classmethod
    def copy_dist_files(cls, template: TemplateT) -> None:
        for file in TEMPLATE_PROJECT_FILES[template]:
            file = str(pathlib.Path("templates", template.value, file))
            data = pkgutil.get_data("tktl", file)
            if data:
                cls._copy_file(file, data, template)

    @classmethod
    def create_subdirs(cls) -> None:
        for path in TEMPLATE_PROJECT_DIRS:
            full_path = os.path.join(cls.TKTL_DIR, path) if cls.TKTL_DIR else path
            os.makedirs(full_path, exist_ok=True)

    @classmethod
    def _copy_file(cls, file, data, template, replace_path=""):
        strip = f"templates/{template.value}/"
        file_path = file.replace(strip, replace_path)
        try:
            with open(os.path.join(cls.TKTL_DIR, file_path), "w") as f:
                f.write(data.decode("utf-8").replace("__version__", __version__))
        except UnicodeDecodeError:
            with open(os.path.join(cls.TKTL_DIR, file_path), "wb") as f:
                f.write(data)

    @classmethod
    def validate_project_config(cls, path="."):
        return validate_project_contents(path=path)
