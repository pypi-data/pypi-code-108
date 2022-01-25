from typing import Any, Optional

from gcip.core.job import Job, ScriptArgumentNotAllowedError


class Flake8(Job):
    def __init__(
        self,
        *,
        name: str = "flake8",
        stage: str = "lint",
        **kwargs: Any,
    ) -> None:
        """
        Runs:

        ```
        pip3 install --upgrade flake8
        flake8
        ```
        """
        if "script" in kwargs:
            raise ScriptArgumentNotAllowedError()

        super().__init__(
            name=name,
            stage=stage,
            script=[
                "pip3 install --upgrade flake8",
                "flake8",
            ],
            **kwargs,
        )


class Mypy(Job):
    def __init__(
        self,
        package_dir: str,
        *,
        name: str = "mypy",
        stage: str = "lint",
        mypy_version: str = "0.812",
        mypy_options: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Install mypy if not already installed.
        Execute mypy for `package_dir`.

        Args:
            package_dir (str): Package directory to type check.
            mypy_version (str, optional): If `mypy` is not already installed this version will be installed. Defaults to "0.812".
            mypy_options (Optional[str], optional): Adds arguments to mypy execution. Defaults to None.
            job_name (str): The jobs name used in pipeline. Defaults to "mypy".
            job_stage (str): The jobs stage used in pipeline. Defaults to "lint".
        Returns:
            Job: gcip.Job
        """
        if "script" in kwargs:
            raise ScriptArgumentNotAllowedError()

        script = [f'pip3 freeze | grep -q "^mypy==" || pip3 install mypy=={mypy_version}']

        if mypy_options:
            script.append(f"mypy {mypy_options} {package_dir}")
        else:
            script.append(f"mypy {package_dir}")

        super().__init__(
            name=name,
            stage=stage,
            script=script,
            **kwargs,
        )


class Isort(Job):
    def __init__(
        self,
        *,
        name: str = "isort",
        stage: str = "lint",
        **kwargs: Any,
    ) -> None:
        """
        Runs:

        ```
        pip3 install --upgrade isort
        isort --check .
        ```
        """
        if "script" in kwargs:
            raise ScriptArgumentNotAllowedError()

        super().__init__(
            name=name,
            stage=stage,
            script=[
                "pip3 install --upgrade isort",
                "isort --check .",
            ],
            **kwargs,
        )
