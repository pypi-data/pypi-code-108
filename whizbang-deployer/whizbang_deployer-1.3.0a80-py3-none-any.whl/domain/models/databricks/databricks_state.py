from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.domain.models.databricks.databricks_secret_scope import DatabricksSecretScope


class DatabricksState:
    def __init__(self, client: DatabricksClientArgs,
                 pool_state: list = None,
                 cluster_state: list = None,
                 library_state: list = None,
                 universal_library_state: list = None,
                 notebook_state: str = None,
                 job_state: list = None,
                 secret_scope: DatabricksSecretScope = None,
                 new_cluster_fields: dict = None):
        self.client = client
        self.notebook_state = notebook_state
        self.job_state = job_state or []
        self.cluster_state = cluster_state or []
        self.library_state = library_state or []
        self.universal_library_state = universal_library_state or []
        self.pool_state = pool_state or []
        self.secret_scope = secret_scope
        self.new_cluster_fields = new_cluster_fields or {}
