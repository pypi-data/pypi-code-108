from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.domain.manager.databricks.databricks_manager_base import DatabricksManagerBase
from whizbang.domain.models.databricks.databricks_token import DatabricksToken
from whizbang.domain.repository.databricks.databricks_token_repository import DatabricksTokenRepository


class DatabricksTokenManager(DatabricksManagerBase):
    def __init__(self, repository: DatabricksTokenRepository):
        DatabricksManagerBase.__init__(self, repository)

    def create(self, client_args: DatabricksClientArgs, token: DatabricksToken):
        return self.repository.create(client_args=client_args,
                                      t_object=token)
