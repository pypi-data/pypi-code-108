from dependency_injector import containers, providers

from whizbang.domain.manager.az.az_account_manager import AzAccountManager
from whizbang.domain.manager.az.az_app_registration_manager import AzAppRegistrationManager
from whizbang.domain.manager.az.az_container_registry_manager import AzContainerRegistryManager
from whizbang.domain.manager.az.az_datafactory_manager import AzDatafactoryManager
from whizbang.domain.manager.az.az_keyvault_manager import AzKeyVaultManager
from whizbang.domain.manager.az.az_rbac_manager import AzRbacManager
from whizbang.domain.manager.az.az_resource_group_manager import AzResourceGroupManager
from whizbang.domain.manager.az.az_service_principal_manager import AzServicePrincipalManager
from whizbang.domain.manager.az.az_sql_server_firewall_manager import AzSqlServerFirewallManager
from whizbang.domain.manager.az.az_storage_manager import AzStorageManager
from whizbang.domain.manager.az.az_sql_database_manager import AzSqlDatabaseManager
from whizbang.domain.manager.az.az_webapp_manager import AzWebappManager
from whizbang.domain.manager.bicep.bicep_deployment_manager import BicepDeploymentManager
from whizbang.domain.manager.databricks.databricks_cluster_manager import DatabricksClusterManager
from whizbang.domain.manager.databricks.databricks_job_manager import DatabricksJobManager
from whizbang.domain.manager.databricks.databricks_library_manager import DatabricksLibraryManager
from whizbang.domain.manager.databricks.databricks_token_manager import DatabricksTokenManager
from whizbang.domain.manager.databricks.databricks_workspace_manager import DatabricksWorkspaceManager
from whizbang.domain.manager.databricks.databricks_pool_manager import DatabricksPoolManager
from whizbang.domain.manager.databricks.databricks_secret_scope_manager import DatabricksSecretScopeManager
from whizbang.domain.manager.pyodbc.sql_script_manager import SqlScriptManager
from whizbang.domain.repository.az.az_container_registry_repository import AzContainerRegistryRepository


class ManagerContainer(containers.DeclarativeContainer):
    # dependencies
    az_account_repository = providers.Dependency()
    az_active_directory_repository = providers.Dependency()
    az_resource_group_repository = providers.Dependency()
    az_keyvault_repository = providers.Dependency()
    az_rbac_repository = providers.Dependency()
    az_deployment_repository = providers.Dependency()
    az_storage_repository = providers.Dependency()
    az_app_registration_repository = providers.Dependency()
    az_sql_database_repository = providers.Dependency()
    az_sql_server_firewall_repository = providers.Dependency()
    az_service_principal_repository = providers.Dependency()
    az_webapp_repository = providers.Dependency()
    az_datafactory_repository = providers.Dependency()
    az_container_registry_repository = providers.Dependency()

    databricks_pool_repository = providers.Dependency()
    databricks_cluster_repository = providers.Dependency()
    databricks_library_repository = providers.Dependency()
    databricks_notebook_repository = providers.Dependency()
    databricks_job_repository = providers.Dependency()
    databricks_secret_scope_repository = providers.Dependency()
    databricks_token_repository = providers.Dependency()

    sql_script_repository = providers.Dependency()

    app_config = providers.Dependency()

    # az cli
    az_account_manager = providers.Factory(
        AzAccountManager,
        repository=az_account_repository
    )

    az_resource_group_manager = providers.Factory(
        AzResourceGroupManager,
        repository=az_resource_group_repository
    )

    az_keyvault_manager = providers.Factory(
        AzKeyVaultManager,
        repository=az_keyvault_repository,
        active_directory_repository=az_active_directory_repository,
        app_config=app_config
    )

    az_rbac_manager = providers.Factory(
        AzRbacManager,
        repository=az_rbac_repository
    )

    az_storage_manager = providers.Factory(
        AzStorageManager,
        repository=az_storage_repository
    )
    
    az_app_registration_manager = providers.Factory(
        AzAppRegistrationManager,
        repository=az_app_registration_repository
    )

    az_sql_database_manager = providers.Factory(
        AzSqlDatabaseManager,
        repository=az_sql_database_repository
    )

    az_sql_server_firewall_manager = providers.Factory(
        AzSqlServerFirewallManager,
        repository=az_sql_server_firewall_repository
    )

    az_service_principal_manager = providers.Factory(
        AzServicePrincipalManager,
        repository=az_service_principal_repository,
        az_app_registration_manager=az_app_registration_manager
    )

    az_webapp_manager = providers.Factory(
        AzWebappManager,
        repository=az_webapp_repository
    )

    az_datafactory_manager = providers.Factory(
        AzDatafactoryManager,
        repository=az_datafactory_repository
    )

    az_container_registry_manager = providers.Factory(
        AzContainerRegistryManager,
        repository=az_container_registry_repository
    )

    # databricks
    databricks_pool_manager = providers.Factory(
        DatabricksPoolManager,
        repository=databricks_pool_repository
    )

    databricks_cluster_manager = providers.Factory(
        DatabricksClusterManager,
        repository=databricks_cluster_repository,
        pool_manager=databricks_pool_manager
    )

    databricks_library_manager = providers.Factory(
        DatabricksLibraryManager,
        repository=databricks_library_repository,
        cluster_manager=databricks_cluster_manager
    )

    databricks_notebook_manager = providers.Factory(
        DatabricksWorkspaceManager,
        repository=databricks_notebook_repository
    )

    databricks_job_manager = providers.Factory(
        DatabricksJobManager,
        repository=databricks_job_repository,
        cluster_manager=databricks_cluster_manager
    )

    databricks_secret_scope_manager = providers.Factory(
        DatabricksSecretScopeManager,
        repository=databricks_secret_scope_repository
    )

    databricks_token_manager = providers.Factory(
        DatabricksTokenManager,
        repository=databricks_token_repository
    )

    # pyodbc
    sql_script_manager = providers.Factory(
        SqlScriptManager,
        repository=sql_script_repository
    )

    # bicep
    bicep_deployment_manager = providers.Factory(
        BicepDeploymentManager,
        app_config=app_config,
        repository=az_deployment_repository,
        resource_group_manager=az_resource_group_manager
    )
