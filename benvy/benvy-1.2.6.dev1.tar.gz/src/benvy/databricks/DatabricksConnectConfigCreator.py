import os
from logging import Logger
from penvy.setup.SetupStepInterface import SetupStepInterface


class DatabricksConnectConfigCreator(SetupStepInterface):
    def __init__(
        self,
        logger: Logger,
    ):
        self._databricks_connect_config_path = os.path.expanduser("~") + "/.databricks-connect"
        self._logger = logger

    def get_description(self):
        return "Creates empty ~./databricks-connect file"

    def run(self):
        """
        .databricks-connect file must always exist and contain at least empty JSON for the Databricks Connect to work properly
        specific cluster connection credentials must be set when creating the SparkSession instance
        """
        self._logger.info(f"Creating empty {self._databricks_connect_config_path} file")

        with open(self._databricks_connect_config_path, "w", encoding="utf-8") as f:
            f.write("{}")

    def should_be_run(self) -> bool:
        return not os.path.isfile(self._databricks_connect_config_path)
