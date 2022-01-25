from dependency_injector import containers, providers

from whizbang.domain.repository.az.az_account_repository import AzAccountRepository
from whizbang.domain.repository.az.az_active_directory_repository import AzActiveDirectoryRepository
from whizbang.domain.repository.az.az_app_registration_repository import AzAppRegistrationRepository
from whizbang.domain.repository.az.az_container_registry_repository import AzContainerRegistryRepository
from whizbang.domain.repository.az.az_datafactory_repository import AzDatafactoryRepository
from whizbang.domain.repository.az.az_deployment_respository import AzDeploymentRepository
from whizbang.domain.repository.az.az_keyvault_repository import AzKeyVaultRepository
from whizbang.domain.repository.az.az_rbac_repository import AzRbacRepository
from whizbang.domain.repository.az.az_resource_group_repository import AzResourceGroupRepository
from whizbang.domain.repository.az.az_service_principal_repository import AzServicePrincipalRepository
from whizbang.domain.repository.az.az_sql_database_repository import AzSqlDatabaseRepository
from whizbang.domain.repository.az.az_sql_server_firewall_repository import AzSqlServerFirewallRepository
from whizbang.domain.repository.az.az_storage_repository import AzStorageRepository
from whizbang.domain.repository.az.az_webapp_repository import AzWebappRepository
from whizbang.domain.repository.databricks.databricks_cluster_repository import DatabricksClusterRepository
from whizbang.domain.repository.databricks.databricks_job_repository import DatabricksJobRepository
from whizbang.domain.repository.databricks.databricks_library_repository import DatabricksLibraryRepository
from whizbang.domain.repository.databricks.databricks_token_repository import DatabricksTokenRepository
from whizbang.domain.repository.databricks.databricks_workspace_repository import DatabricksWorkspaceRepository
from whizbang.domain.repository.databricks.databricks_pool_repository import DatabricksPoolRepository
from whizbang.domain.repository.databricks.databricks_secret_scope_repository import DatabricksSecretScopeRepository
from whizbang.domain.repository.sql_server.sql_script_repository import SqlScriptRepository


class RepositoryContainer(containers.DeclarativeContainer):
    # dependencies
    az_cli_context = providers.Dependency()
    databricks_context_factory = providers.Dependency()
    pyodbc_context_factory = providers.Dependency()

    # az cli
    az_account_repository = providers.Factory(
        AzAccountRepository,
        context=az_cli_context

    )

    az_active_directory_repository = providers.Factory(
        AzActiveDirectoryRepository,
        context=az_cli_context
    )

    az_resource_group_repository = providers.Factory(
        AzResourceGroupRepository,
        context=az_cli_context
    )

    az_keyvault_repository = providers.Factory(
        AzKeyVaultRepository,
        context=az_cli_context
    )

    az_storage_repository = providers.Factory(
        AzStorageRepository,
        context=az_cli_context,
        active_directory_repository=az_active_directory_repository
    )

    az_rbac_repository = providers.Factory(
        AzRbacRepository,
        context=az_cli_context,
        active_directory_repository=az_active_directory_repository
    )

    az_deployment_repository = providers.Factory(
        AzDeploymentRepository,
        context=az_cli_context,
        az_resource_group_repository=az_resource_group_repository
    )

    az_app_registration_repository = providers.Factory(
        AzAppRegistrationRepository,
        context=az_cli_context,
        az_active_directory_repository=az_active_directory_repository
    )

    az_sql_database_repository = providers.Factory(
        AzSqlDatabaseRepository,
        context=az_cli_context
    )

    az_sql_server_firewall_repository = providers.Factory(
        AzSqlServerFirewallRepository,
        context=az_cli_context
    )

    az_service_principal_repository = providers.Factory(
        AzServicePrincipalRepository,
        context=az_cli_context
    )

    az_webapp_repository = providers.Factory(
        AzWebappRepository,
        context=az_cli_context
    )

    az_datafactory_repository = providers.Factory(
        AzDatafactoryRepository,
        context=az_cli_context
    )

    az_container_registry_repository = providers.Factory(
        AzContainerRegistryRepository,
        context=az_cli_context
    )

    # databricks
    databricks_notebook_repository = providers.Factory(
        DatabricksWorkspaceRepository,
        context_factory=databricks_context_factory
    )

    databricks_job_repository = providers.Factory(
        DatabricksJobRepository,
        context_factory=databricks_context_factory
    )

    databricks_library_repository = providers.Factory(
        DatabricksLibraryRepository,
        context_factory=databricks_context_factory
    )

    databricks_pool_repository = providers.Factory(
        DatabricksPoolRepository,
        context_factory=databricks_context_factory
    )

    databricks_cluster_repository = providers.Factory(
        DatabricksClusterRepository,
        context_factory=databricks_context_factory
    )

    databricks_secret_scope_repository = providers.Factory(
        DatabricksSecretScopeRepository,
        context_factory=databricks_context_factory
    )

    databricks_token_repository = providers.Factory(
        DatabricksTokenRepository,
        context_factory=databricks_context_factory
    )



    #pyodbc
    sql_script_repository = providers.Factory(
        SqlScriptRepository,
        context_factory=pyodbc_context_factory
    )

