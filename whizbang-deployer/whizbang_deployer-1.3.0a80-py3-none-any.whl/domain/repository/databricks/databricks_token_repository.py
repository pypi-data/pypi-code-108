from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.data.databricks.databricks_context_factory import IDatabricksContextFactory
from whizbang.data.databricks.databricks_token_context import DatabricksTokenContext
from whizbang.domain.models.databricks.databricks_token import DatabricksToken
from whizbang.domain.repository.databricks.databricks_repository_base import DatabricksRepositoryBase
from whizbang.domain.shared_types.databricks_api_type import DatabricksApiType


class DatabricksTokenRepository(DatabricksRepositoryBase):
    def __init__(self, context_factory: IDatabricksContextFactory):
        DatabricksRepositoryBase.__init__(self, databricks_context_factory=context_factory)

    @property
    def context_type(self) -> str:
        return DatabricksApiType.token

    def create(self, client_args: DatabricksClientArgs, t_object: DatabricksToken):
        context: DatabricksTokenContext = self._get_context(client_args)

        result = context.create_token(
            token=t_object
        )
        return result

    def get(self, client_args: DatabricksClientArgs):
        context: DatabricksTokenContext = self._get_context(client_args)

        result = context.get_tokens()
        return result

    def update(self, client_args: DatabricksClientArgs, t_object):
        """update doesn't make sense at this point"""
        pass
