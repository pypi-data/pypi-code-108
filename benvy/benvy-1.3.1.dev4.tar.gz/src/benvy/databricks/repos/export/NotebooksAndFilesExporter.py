import os
import io
import json
import shutil
import tempfile
from typing import List
from zipfile import ZipFile, ZIP_DEFLATED
from databricks_cli.workspace.api import WorkspaceApi
from databricks_cli.workspace.api import WorkspaceFileInfo
from benvy.databricks.notebook.NotebookConverter import NotebookConverter
from benvy.databricks.repos.export.ExportObject import ExportObject


class NotebooksAndFilesExporter:

    _dbc_content: ZipFile = None

    def __init__(
        self,
        project_root_path: str,
        workspace_api: WorkspaceApi,
        notebook_converter: NotebookConverter,
    ):
        self._project_root_path = project_root_path
        self._workspace_api = workspace_api
        self._notebook_converter = notebook_converter

    def export(self, workspace_path: str, local_path: str) -> List[ExportObject]:
        return self._export_notebooks(workspace_path, local_path) + self._export_files(workspace_path, local_path)

    def _export_notebooks(self, workspace_path: str, local_path: str) -> List[ExportObject]:
        dbc_content = self._load_dbc_content(workspace_path)
        notebook_files = [file for file in dbc_content.filelist if file.filename.endswith(".python")]
        object_type = "NOTEBOOK"
        export_objects = []

        for notebook_file in notebook_files:
            notebook_dbc_content = json.loads(dbc_content.read(notebook_file.filename).decode("utf-8"))
            notebook_src_content = self._notebook_converter.from_dbc_notebook(notebook_dbc_content)
            notebook_relative_path = "/".join(notebook_file.filename.strip("/").split("/")[1:]).replace(".python", ".py")
            dbx_path = f"{workspace_path}/{notebook_relative_path}"
            target_path = os.path.join(local_path, notebook_relative_path)
            object_id = notebook_dbc_content["origId"]

            export_objects.append(ExportObject(object_id, object_type, dbx_path, target_path, notebook_src_content, notebook_dbc_content))

            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            with open(target_path, "w") as f:
                f.write(notebook_src_content)

        return export_objects

    def _export_files(self, workspace_path: str, local_path: str) -> List[ExportObject]:
        files = self._list_files(workspace_path)
        object_type = "FILE"
        export_objects = []

        for file in files:
            dbx_filesystem_path = "/Workspace" + file.path
            file_relative_path = os.path.relpath(dbx_filesystem_path, self._project_root_path)
            target_path = os.path.join(local_path, file_relative_path)
            object_id = file.object_id

            export_objects.append(ExportObject(object_id, object_type, file.path, target_path))

            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            shutil.copy2(dbx_filesystem_path, target_path)

        return export_objects

    def _list_notebooks(self, workspace_path: str) -> List[WorkspaceFileInfo]:
        return [obj for obj in self._list_objects(workspace_path) if obj.object_type == "NOTEBOOK"]

    def _list_files(self, workspace_path: str) -> List[WorkspaceFileInfo]:
        return [obj for obj in self._list_objects(workspace_path) if obj.object_type == "FILE"]

    def _list_objects(self, workspace_path: str) -> List[WorkspaceFileInfo]:
        objects_to_return = []

        objects = self._workspace_api.list_objects(workspace_path)

        for obj in objects:
            if obj.is_dir:
                objects_to_return += self._list_objects(obj.path)

            else:
                objects_to_return += [obj]

        return objects_to_return

    def _load_dbc_content(self, workspace_path: str) -> ZipFile:
        if self._dbc_content:
            return self._dbc_content

        dbc_temp_file = tempfile.mktemp()

        self._workspace_api.export_workspace(workspace_path, dbc_temp_file, fmt="DBC", is_overwrite=True)

        with open(dbc_temp_file, "rb") as f:
            buffer = io.BytesIO()
            buffer.write(f.read())

        return ZipFile(buffer, "r", ZIP_DEFLATED)
