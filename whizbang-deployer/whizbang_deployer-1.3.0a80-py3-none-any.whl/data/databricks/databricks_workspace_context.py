import abc

from databricks_cli.sdk import ApiClient
from databricks_cli.workspace.api import WorkspaceApi

from whizbang.data.databricks.databricks_context_base import DatabricksContextBase, IDatabricksContextBase


class IDatabricksWorkspaceContext(IDatabricksContextBase):
    """"""

    @abc.abstractmethod
    def upload_notebook(self, source_path: str, target_path: str, language: str,
                        import_format: str, overwrite: str):
        """"""

    @abc.abstractmethod
    def upload_notebook_directory(self, source_path: str, target_path: str,
                                  overwrite: str, exclude_hidden_files: str):
        """"""


class DatabricksWorkspaceContext(DatabricksContextBase, IDatabricksWorkspaceContext):
    def __init__(self, api_client: ApiClient, api: WorkspaceApi):
        super().__init__(api_client=api_client, api=api)

    def upload_notebook(self, source_path: str, target_path: str, language: str,
                        import_format: str, overwrite: str):

        def _upload_notebook(api: WorkspaceApi, source_path, target_path, language, import_format, overwrite):
            return api.import_workspace(
                source_path=source_path,
                target_path=target_path,
                language=language,
                fmt=import_format,
                is_overwrite=overwrite
            )

        return self._execute(func=_upload_notebook,
                             source_path=source_path,
                             target_path=target_path,
                             language=language,
                             import_format=import_format,
                             overwrite=overwrite)

    def upload_notebook_directory(self, source_path: str, target_path: str,
                                  overwrite: str, exclude_hidden_files: str):

        def _upload_notebooks(api: WorkspaceApi, source_path, target_path, overwrite, exclude_hidden_files):
            return api.import_workspace_dir(
                source_path=source_path,
                target_path=target_path,
                overwrite=overwrite,
                exclude_hidden_files=exclude_hidden_files
            )

        return self._execute(func=_upload_notebooks,
                             source_path=source_path,
                             target_path=target_path,
                             overwrite=overwrite,
                             exclude_hidden_files=exclude_hidden_files)
