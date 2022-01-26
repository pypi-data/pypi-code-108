from typing import List, Dict, Optional
from benvy.databricks.repos.export.ExportObject import ExportObject


class PylintResultsEnhancer:
    def enhance(self, pylint_results: Dict, export_objects: List[ExportObject]):
        for index, result in enumerate(pylint_results):
            path = result["path"]
            line_number = result["line"]
            export_object = self._get_export_object_by_path(path, export_objects)

            if export_object is None:
                pylint_results[index]["file_type"] = "OTHER"
                continue

            if export_object.databricks_object_type == "NOTEBOOK":
                notebook_id = export_object.databricks_object_id
                cell_number = self._get_cell_number(export_object.src_content, line_number)
                cell_id = self._get_cell_id(export_object.dbc_content, cell_number)
                cell_line = self._get_cell_line_number(export_object.src_content, line_number)

                pylint_results[index]["file_type"] = "NOTEBOOK"
                pylint_results[index]["notebook_id"] = notebook_id
                pylint_results[index]["cell_number"] = cell_number + 1
                pylint_results[index]["cell_line"] = cell_line
                pylint_results[index]["cell_id"] = cell_id

            if export_object.databricks_object_type == "FILE":
                pylint_results[index]["file_type"] = "FILE"
                pylint_results[index]["file_id"] = export_object.databricks_object_id

    def _get_export_object_by_path(self, path: str, export_objects: List[ExportObject]) -> Optional[ExportObject]:
        for obj in export_objects:
            if path in obj.local_path:
                return obj

        return None

    def _get_cell_number(self, notebook_source: str, line_number: int) -> int:
        cell_number = 0

        for index, line in enumerate(notebook_source.split("\n"), 1):
            if index == line_number:
                return cell_number

            if line == "# COMMAND ----------":
                cell_number += 1

        raise Exception(f"Line with number {line_number} not found in source")

    def _get_cell_line_number(self, notebook_source: str, line_number: int) -> int:
        cell_line_number = 0

        for index, line in enumerate(notebook_source.split("\n"), 1):
            if line == "# COMMAND ----------":
                cell_line_number = 0
                continue

            if index == line_number:
                return cell_line_number

            cell_line_number += 1

        raise Exception(f"Line with number {line_number} not found in source")

    def _get_cell_id(self, notebook_dbc: Dict, cell_number: int) -> int:
        commands = [command for command in notebook_dbc["commands"] if command["subtype"] == "command"]

        return commands[cell_number]["origId"]
