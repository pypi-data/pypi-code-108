import os
import platform
import subprocess
from logging import Logger
from penvy.setup.SetupStepInterface import SetupStepInterface
from penvy.shell.runner import run_and_read_line


class BinExecutableFlagSetter(SetupStepInterface):
    def __init__(
        self,
        conda_executable_path: str,
        venv_dir: str,
        logger: Logger,
    ):
        self._conda_executable_path = conda_executable_path
        self._venv_dir = venv_dir
        self._logger = logger

    def get_description(self):
        return "Set executable flag to pyspark/bin files"

    def run(self):
        pyspark_bin_dir = self._get_pyspark_bin_dir()

        if not os.path.isdir(pyspark_bin_dir):
            raise Exception(f"pyspark bin dir does not exist: {pyspark_bin_dir}")

        self._logger.info(f"Setting executable permissions to {pyspark_bin_dir}")

        subprocess.check_call(["chmod", "-R", "+x", pyspark_bin_dir])

    def should_be_run(self) -> bool:
        return platform.system() != "Windows" and (
            not os.path.isdir(self._venv_dir) or not self._all_files_are_executable(self._get_pyspark_bin_dir())
        )

    def _get_pyspark_bin_dir(self):
        command = (
            f"{self._conda_executable_path} run -p {self._venv_dir} "
            f'python -c \'import sysconfig; print(sysconfig.get_paths()["purelib"], end="")\''
        )

        site_packages_dir = run_and_read_line(command, shell=True)

        return site_packages_dir + "/pyspark/bin"

    def _all_files_are_executable(self, path: str):
        files = os.listdir(path)

        for file in files:
            file_path = path + "/" + file
            os.chmod(file_path, 0o777)

            is_executable = os.access(file_path, os.X_OK)

            if not is_executable:
                return False

        return True
