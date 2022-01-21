import os
from pathlib import Path
from typing import Union

from ._error import CommandError


def _find_app_dir(base_dir: Path):
    for name in os.listdir(base_dir):
        subdir = base_dir / name
        check_file = subdir / "migration" / "alembic.ini"
        if check_file.is_file():
            return subdir
    raise CommandError("migration directory not exists")


class MigrationDirectory:
    def __init__(self, app_dir: Path) -> None:
        self._app_dir = app_dir.absolute()

    @classmethod
    def from_app_dir(cls, app_dir: Union[str, Path]):
        return cls(Path(app_dir))

    @classmethod
    def from_base_dir(cls, base_dir: Union[str, Path] = "."):
        return cls(_find_app_dir(Path(base_dir)))

    @property
    def app_dir(self):
        return self._app_dir

    @property
    def app_name(self):
        return self._app_dir.name

    @property
    def migration(self):
        return self.app_dir / "migration"

    @property
    def alembic_ini(self):
        return self.migration / "alembic.ini"

    @property
    def versions(self):
        return self.migration / "versions"

    @property
    def ddl(self):
        return self.migration / "ddl"

    @property
    def env_py(self):
        return self.migration / "env.py"

    @property
    def script_py_mako(self):
        return self.migration / "script.py.mako"

    @property
    def template(self):
        return Path(__file__).parent / "template"

    @property
    def template_alembic_ini(self):
        return self.template / "alembic.ini"

    @property
    def template_env_py(self):
        return self.template / "env.py.txt"

    @property
    def template_script_py_mako(self):
        return self.template / "script.py.mako"
