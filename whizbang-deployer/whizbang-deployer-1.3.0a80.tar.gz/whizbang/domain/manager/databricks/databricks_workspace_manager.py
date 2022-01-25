from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.domain.manager.databricks.databricks_manager_base import DatabricksManagerBase, IDatabricksManager
from whizbang.domain.models.databricks.databricks_notebook import DatabricksNotebook
from whizbang.domain.repository.databricks.databricks_workspace_repository import IDatabricksWorkspaceRepository


class IDatabricksWorkspaceManager(IDatabricksManager):
    """"""


class DatabricksWorkspaceManager(DatabricksManagerBase, IDatabricksWorkspaceManager):
    def __init__(self, repository: IDatabricksWorkspaceRepository):
        DatabricksManagerBase.__init__(self, repository)

    def save(self, client_args: DatabricksClientArgs, t_object: DatabricksNotebook):
        if t_object.source_path is None:
            return None
        else:
            return self.repository.create(client_args=client_args, t_object=t_object)
