import os
import logging
from pathlib import Path
from penvy.env.EnvConfig import EnvConfig
from penvy.PenvyConfig import PenvyConfig


class BootstrapConfig(EnvConfig):
    def get_parameters(self) -> dict:
        poetry_version = PenvyConfig().get_parameters()["poetry"]["install_version"]

        return {
            "project": {
                # path in DBX Repos is like /Workspace/Repos/folder/repository/src/...
                # so we take first 4 parts which is the root of the project
                "dir": os.path.join(*Path.cwd().parts[0:5]),
            },
            "poetry": {
                "version": poetry_version,
                "home": "/root/.poetry",
                "executable": "/root/.poetry/bin/poetry",
                "archive_url": f"https://github.com/python-poetry/poetry/releases/download/{poetry_version}/poetry-{poetry_version}-linux.tar.gz",
                "install_script_url": "https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py",
                "archive_path": f"/dbfs/FileStore/jars/daipe/poetry/poetry-{poetry_version}-linux.tar.gz",
                "install_script_path": "/dbfs/FileStore/jars/daipe/poetry/get-poetry.py",
            },
            "logger": {
                "name": "daipe-bootstrap",
                "level": logging.INFO,
            },
        }
