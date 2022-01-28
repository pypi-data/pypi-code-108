from benvy.databricks.DatabricksContext import DatabricksContext
from databricks_cli.workspace.api import WorkspaceApi
from databricks_cli.sdk import ApiClient


class WorkspaceApiFactory:
    def __init__(self, databricks_context: DatabricksContext):
        self._databricks_context = databricks_context

    def create(self):
        return WorkspaceApi(ApiClient(host=self._databricks_context.get_host(), token=self._databricks_context.get_token()))
