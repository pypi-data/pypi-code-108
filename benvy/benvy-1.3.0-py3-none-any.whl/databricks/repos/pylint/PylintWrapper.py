import json
import tempfile
from typing import List, Dict
from penvy.shell.runner import run_and_read_line
from benvy.databricks.repos.export.NotebooksAndFilesExporter import NotebooksAndFilesExporter
from benvy.databricks.repos.pylint.PylintResultsEnhancer import PylintResultsEnhancer
from benvy.databricks.repos.pylint.PylintHTMLDisplayer import PylintHTMLDisplayer


class PylintWrapper:
    def __init__(
        self,
        project_root_path: str,
        pylint_executable: str,
        pylint_enhancer: PylintResultsEnhancer,
        pylint_displayer: PylintHTMLDisplayer,
        exporter: NotebooksAndFilesExporter,
    ):
        self._project_root_path = project_root_path
        self._project_root_path_no_workspace = project_root_path[10:]  # strip leading /Workspace
        self._pylint_executable = pylint_executable
        self._pylint_enhancer = pylint_enhancer
        self._pylint_displayer = pylint_displayer
        self._exporter = exporter

    def run(self, args: List[str]):
        temp_project_dir = tempfile.mkdtemp()

        export_objects = self._exporter.export(self._project_root_path_no_workspace, temp_project_dir)

        pylint_results = self._lint_and_get_results(args, temp_project_dir)

        self._pylint_enhancer.enhance(pylint_results, export_objects)

        self._pylint_displayer.display(pylint_results)

    def _lint_and_get_results(self, args: List[str], cwd: str) -> Dict:
        command = f"{self._pylint_executable} {' '.join(args)} --output-format=json"

        return json.loads(run_and_read_line(command, cwd=cwd, shell=True))
