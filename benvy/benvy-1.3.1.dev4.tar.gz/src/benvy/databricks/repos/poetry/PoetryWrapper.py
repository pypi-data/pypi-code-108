import re
import shutil
import tempfile
from typing import List
from logging import Logger
from penvy.shell.runner import run_with_live_output
from benvy.databricks.repos.uploader.RepoFileUploader import RepoFileUploader


class PoetryWrapper:
    def __init__(
        self,
        project_root_path: str,
        poetry_executable: str,
        repo_file_uploader: RepoFileUploader,
        logger: Logger,
    ):
        self._project_root_path = project_root_path
        self._poetry_executable = poetry_executable
        self._repo_file_uploader = repo_file_uploader
        self._logger = logger

    def run_command(self, args: List[str]):
        tmp_dir = tempfile.mkdtemp()

        self._copy_poetry_files_to_tmp_dir(tmp_dir)

        self._run_poetry_command(args, cwd=tmp_dir)

        self._upload_poetry_files_to_repo(tmp_dir)

    def _run_poetry_command(self, args: List[str], cwd: str):
        if len(args) == 0:
            run_with_live_output(self._poetry_executable, cwd=cwd, shell=True)
            return

        poetry_action = args[0]
        arguments = args[1:]

        if poetry_action in ["add", "update"]:
            command = self._create_add_or_update_command(poetry_action, arguments)

        elif poetry_action == "remove":
            self._check_remove_command_valid(arguments)
            self._remove_package_from_pyproject(f"{cwd}/pyproject.toml", arguments[0])

            command = self._create_remove_command()

        else:
            command = self._create_general_command(poetry_action, arguments)

        self._logger.info(f"Running: poetry {' '.join(args)}")

        try:
            run_with_live_output(command, cwd=cwd, shell=True)

        except Exception:
            self._logger.error("poetry failed")

    def _create_add_or_update_command(self, poetry_action: str, arguments: List[str]):
        if "--lock" not in arguments:
            arguments.append("--lock")

        return f"{self._poetry_executable} {poetry_action} {' '.join(arguments)}"

    def _create_remove_command(self):
        return f"{self._poetry_executable} lock --no-update"

    def _create_general_command(self, poetry_action: str, arguments: List[str]):
        return f"{self._poetry_executable} {poetry_action} {' '.join(arguments)}"

    def _check_remove_command_valid(self, arguments: List[str]):
        if len(arguments) != 1 or arguments[0].startswith("-"):
            raise Exception("Invalid remove command: remove command is allowed only in form 'poetry remove package'")

    def _remove_package_from_pyproject(self, pyproject_path: str, package_name):
        with open(pyproject_path, "r") as f:
            lines = f.read().splitlines()

        lines_without_package = []
        package_found = False
        in_dependencies_section = False

        for line in lines:
            if in_dependencies_section and "[" in line:
                in_dependencies_section = False

            if "[tool.poetry.dependencies]" in line or "[tool.poetry.dev-dependencies]" in line:
                in_dependencies_section = True

            if re.match(f"^({package_name})\\s*=\\s*(.*)$", line) and in_dependencies_section:
                package_found = True
                continue

            lines_without_package.append(line)

        if not package_found:
            raise Exception(f"Package '{package_name}' not found in pyproject.toml")

        with open(pyproject_path, "w") as f:
            f.write("\n".join(lines_without_package) + "\n")

    def _copy_poetry_files_to_tmp_dir(self, tmp_dir: str):
        shutil.copy(f"{self._project_root_path}/pyproject.toml", tmp_dir)
        shutil.copy(f"{self._project_root_path}/poetry.lock", tmp_dir)

    def _upload_poetry_files_to_repo(self, tmp_dir: str):
        repo_path = self._project_root_path.lstrip("/Workspace/")
        self._repo_file_uploader.upload_files_to_repo(f"{tmp_dir}/pyproject.toml", repo_path)
        self._repo_file_uploader.upload_files_to_repo(f"{tmp_dir}/poetry.lock", repo_path)
