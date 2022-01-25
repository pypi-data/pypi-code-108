from databricks_cli.tokens.api import TokensApi
from databricks_cli.sdk import ApiClient

from whizbang.data.databricks.databricks_context_base import DatabricksContextBase
from whizbang.domain.models.databricks.databricks_token import DatabricksToken


class DatabricksTokenContext(DatabricksContextBase):
    def __init__(self, api_client: ApiClient, api):
        DatabricksContextBase.__init__(self, api_client=api_client, api=api)

    def create_token(self, token: DatabricksToken):
        def _create_token(api: TokensApi, token_lifespan_seconds, comment):
            return api.create(lifetime_seconds=token_lifespan_seconds,
                              comment=comment)

        return self._execute(func=_create_token,
                             token_lifespan_seconds=token.token_lifespan_seconds,
                             comment=token.comment)

    def get_tokens(self):
        def _get(api: TokensApi):
            return api.list()

        return self._execute(func=_get)
