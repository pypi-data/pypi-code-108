
from dependency_injector import containers, providers

from whizbang.config.app_config import AppConfig
from whizbang.config.environment_config import EnvironmentConfig
from whizbang.data.data_container import DataContainer
from whizbang.domain.handler.handler_container import HandlerContainer
from whizbang.domain.manager.manager_container import ManagerContainer
from whizbang.domain.menu.menu_container import MenuContainer
from whizbang.domain.repository.repository_container import RepositoryContainer
from whizbang.domain.solution.solution_factory import SolutionFactory
from whizbang.domain.workflow.workflow_container import WorkflowContainer


class ApplicationContainer(containers.DeclarativeContainer):
    # config
    config = providers.Configuration()
    
    app_config = providers.Singleton(
        AppConfig,
        solution_rel_path=config.app_config['current_dir_path']
    )

    full_environment_config = config.environment_config
    """The full configuration dictionary from DI."""
    
    # TODO we need to allow implementors to specify children configs (beyond the base)
    # and while we don't want those attributes used in this app, we do want those attributes
    # available for the pluggable classes that call whizbang (the solutions).
    #
    # Below we have the base configuration, and above we have the full file.
        
    environment_config = providers.Singleton( 
        EnvironmentConfig,
        subscription_id=full_environment_config['subscription_id'],
        tenant_id=full_environment_config['tenant_id'],
        resource_group_name=full_environment_config['resource_group_name'],
        resource_group_location=full_environment_config['resource_group_location'],
        properties=full_environment_config,
        rbac_policies=full_environment_config['rbac_policies'],
        keyvault_access_policies=full_environment_config['keyvault_access_policies'],
    )

    data_package: DataContainer = providers.Container(
        DataContainer
    )

    repository_package: RepositoryContainer = providers.Container(
        RepositoryContainer,
        az_cli_context=data_package.az_cli_context,
        databricks_context_factory=data_package.databricks_context_factory,
        pyodbc_context_factory=data_package.pyodbc_context_factory
    )

    manager_package: ManagerContainer = providers.Container(
        ManagerContainer,
        az_account_repository=repository_package.az_account_repository,
        az_active_directory_repository=repository_package.az_active_directory_repository,
        az_resource_group_repository=repository_package.az_resource_group_repository,
        az_keyvault_repository=repository_package.az_keyvault_repository,
        az_rbac_repository=repository_package.az_rbac_repository,
        az_deployment_repository=repository_package.az_deployment_repository,
        az_storage_repository=repository_package.az_storage_repository,
        az_app_registration_repository=repository_package.az_app_registration_repository,
        az_sql_server_firewall_repository=repository_package.az_sql_server_firewall_repository,
        az_sql_database_repository=repository_package.az_sql_database_repository,
        az_service_principal_repository=repository_package.az_service_principal_repository,
        az_webapp_repository=repository_package.az_webapp_repository,
        az_datafactory_repository=repository_package.az_datafactory_repository,
        az_container_registry_repository=repository_package.az_container_registry_repository,

        databricks_pool_repository=repository_package.databricks_pool_repository,
        databricks_cluster_repository=repository_package.databricks_cluster_repository,
        databricks_library_repository=repository_package.databricks_library_repository,
        databricks_notebook_repository=repository_package.databricks_notebook_repository,
        databricks_job_repository=repository_package.databricks_job_repository,
        databricks_secret_scope_repository=repository_package.databricks_secret_scope_repository,
        databricks_token_repository=repository_package.databricks_token_repository,

        sql_script_repository=repository_package.sql_script_repository,

        app_config=app_config
    )

    workflow_package: WorkflowContainer = providers.Container(
        WorkflowContainer,
        bicep_deployment_manager=manager_package.bicep_deployment_manager,
        databricks_pool_manager=manager_package.databricks_pool_manager,
        databricks_cluster_manager=manager_package.databricks_cluster_manager,
        databricks_library_manager=manager_package.databricks_library_manager,
        databricks_notebook_manager=manager_package.databricks_notebook_manager,
        databricks_job_manager=manager_package.databricks_job_manager,
        databricks_secret_scope_manager=manager_package.databricks_secret_scope_manager,
        az_storage_manager=manager_package.az_storage_manager,
        az_account_manager=manager_package.az_account_manager,
        az_active_directory_repository=repository_package.az_active_directory_repository
    )

    handler_package: HandlerContainer = providers.Container(
        HandlerContainer,
        app_config=app_config,
        environment_config=environment_config,
        keyvault_manager=manager_package.az_keyvault_manager,
        deploy_bicep_workflow=workflow_package.bicep_deployment_workflow,
        datalake_deploy_workflow=workflow_package.datalake_deploy_workflow,
        rbac_manager=manager_package.az_rbac_manager,
        sql_script_manager=manager_package.sql_script_manager,
        databricks_job_manager=manager_package.databricks_job_manager,
        databricks_token_manager=manager_package.databricks_token_manager,
        databricks_deploy_workflow=workflow_package.databricks_deploy_workflow,
        sql_server_firewall_manager=manager_package.az_sql_server_firewall_manager,
        app_registration_manager=manager_package.az_app_registration_manager,
        az_account_manager=manager_package.az_account_manager,
        az_webapp_manager=manager_package.az_webapp_manager,
        az_datafactory_manager=manager_package.az_datafactory_manager,
        az_container_registry_manager=manager_package.az_container_registry_manager,
        storage_manager=manager_package.az_storage_manager,
        service_principal_manager=manager_package.az_service_principal_manager,
        sql_database_manager=manager_package.az_sql_database_manager
    )

    solution_factory = providers.Factory(
        SolutionFactory,
        environment_config=environment_config,
        handler=handler_package.handler_facade
    )

    menu_package: MenuContainer = providers.Container(
        MenuContainer,
        solution_factory=solution_factory
    )
