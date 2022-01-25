from typing import Any

from gcip.core.job import Job, ScriptArgumentNotAllowedError
from gcip.addons.python.scripts import (
    pip_install_requirements,
)


class BdistWheel(Job):
    def __init__(
        self,
        *,
        name: str = "bdist_wheel",
        stage: str = "build",
        **kwargs: Any,
    ) -> None:
        """
        Runs `python3 setup.py bdist_wheel` and installs project requirements
        before (`scripts.pip_install_requirements()`)

        * Requires a `requirements.txt` in your project folder containing at least `setuptools`
        * Creates artifacts under the path `dist/`
        """
        if "script" in kwargs:
            raise ScriptArgumentNotAllowedError()

        super().__init__(
            name=name,
            stage=stage,
            script=[
                pip_install_requirements(),
                "python3 setup.py bdist_wheel",
            ],
            **kwargs,
        )
        self.artifacts.add_paths("dist/")
