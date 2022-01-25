import abc

from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.data.databricks.databricks_context_factory import IDatabricksContextFactory
from whizbang.data.databricks.databricks_workspace_context import DatabricksWorkspaceContext
from whizbang.domain.repository.databricks.databricks_repository_base import DatabricksRepositoryBase, IDatabricksRepository
from whizbang.domain.models.databricks.databricks_notebook import DatabricksNotebook
from whizbang.domain.shared_types.databricks_api_type import DatabricksApiType


class IDatabricksWorkspaceRepository(IDatabricksRepository):
    @abc.abstractmethod
    def create_notebook(self, client_args: DatabricksClientArgs, notebook: DatabricksNotebook):
        """"""


class DatabricksWorkspaceRepository(DatabricksRepositoryBase, IDatabricksWorkspaceRepository):
    def __init__(self, context_factory: IDatabricksContextFactory):
        DatabricksRepositoryBase.__init__(self, databricks_context_factory=context_factory)

    @property
    def context_type(self) -> str: return DatabricksApiType.workspace

    def create_notebook(self, client_args: DatabricksClientArgs, notebook: DatabricksNotebook):
        context: DatabricksWorkspaceContext = self._get_context(client_args)

        result = context.upload_notebook(
            source_path=notebook.source_path,
            target_path=notebook.target_path,
            language=notebook.language,
            import_format='SOURCE',
            overwrite='true'
        )

        return result

    def create(self, client_args: DatabricksClientArgs, t_object: DatabricksNotebook):
        context: DatabricksWorkspaceContext = self._get_context(client_args)

        result = context.upload_notebook_directory(
            source_path=t_object.source_path,
            target_path=t_object.target_path,
            overwrite='true',
            exclude_hidden_files='true'
        )

        return result

    def get(self, client_args: DatabricksClientArgs):
        # TODO implement
        pass

    def update(self, client_args: DatabricksClientArgs, t_object):
        # TODO implement
        pass
