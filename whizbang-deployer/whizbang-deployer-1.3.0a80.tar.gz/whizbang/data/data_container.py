from dependency_injector import containers, providers

from whizbang.data.az_cli_context import AzCliContext
from whizbang.data.databricks.databricks_context_factory import DatabricksContextFactory
from whizbang.data.pyodbc.pyodbc_context_factory import PyodbcContextFactory


class DataContainer(containers.DeclarativeContainer):

    az_cli_context = providers.Factory(AzCliContext)

    pyodbc_context_factory = providers.Factory(PyodbcContextFactory)

    databricks_context_factory = providers.Factory(
        DatabricksContextFactory,
        az_cli_context=az_cli_context
    )
