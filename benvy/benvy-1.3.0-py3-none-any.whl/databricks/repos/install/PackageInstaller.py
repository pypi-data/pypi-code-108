import os
import shutil
import tempfile
import IPython
from logging import Logger
from penvy.setup.SetupStepInterface import SetupStepInterface
from penvy.shell.runner import run_shell_command


class PackageInstaller(SetupStepInterface):
    def __init__(
        self,
        project_root_path: str,
        poetry_executable: str,
        logger: Logger,
        include_dev_dependencies: bool,
    ):
        self._project_root_path = project_root_path
        self._poetry_executable = poetry_executable
        self._logger = logger
        self.__include_dev_dependencies = include_dev_dependencies

    def run(self):
        self._logger.info("Installing dependencies")
        self._install_using_pip()

    def get_description(self):
        return "Install dependencies"

    def should_be_run(self) -> bool:
        return "DAIPE_BOOTSTRAPPED" not in os.environ

    def _install_using_pip(self):
        temp_dir = tempfile.mkdtemp()
        pyproject_path = f"{self._project_root_path}/pyproject.toml"
        poetry_lock_path = f"{self._project_root_path}/poetry.lock"
        requirements_txt_path = f"{temp_dir}/requirements.txt"

        shutil.copy(pyproject_path, temp_dir)
        shutil.copy(poetry_lock_path, temp_dir)

        options = ["--without-hashes", f"-o {requirements_txt_path}"]

        if self.__include_dev_dependencies:
            options.append("--dev")

        run_shell_command(f"{self._poetry_executable} export {' '.join(options)}", cwd=temp_dir, shell=True)

        IPython.get_ipython().run_line_magic("pip", f"install -r {requirements_txt_path}")
