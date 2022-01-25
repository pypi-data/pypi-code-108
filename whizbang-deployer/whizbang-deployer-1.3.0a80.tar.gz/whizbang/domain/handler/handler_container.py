from dependency_injector import containers, providers

from whizbang.domain.handler.account_handler import AccountHandler
from whizbang.domain.handler.app_registration_handler import AppRegistrationHandler
from whizbang.domain.handler.container_registry_handler import ContainerRegistryHandler
from whizbang.domain.handler.databricks_handler import DatabricksHandler
from whizbang.domain.handler.datafactory_handler import DatafactoryHandler
from whizbang.domain.handler.handler_facade import HandlerFacade
from whizbang.domain.handler.keyvault_handler import KeyVaultHandler
from whizbang.domain.handler.rbac_handler import RbacHandler
from whizbang.domain.handler.service_principal_handler import ServicePrincipalHandler
from whizbang.domain.handler.sql_server_handler import SqlServerHandler
from whizbang.domain.handler.bicep_handler import BicepHandler
from whizbang.domain.handler.storage_handler import StorageHandler
from whizbang.domain.handler.webapp_handler import WebappHandler


class HandlerContainer(containers.DeclarativeContainer):
    app_config = providers.Dependency()
    environment_config = providers.Dependency()

    keyvault_manager = providers.Dependency()
    deploy_bicep_workflow = providers.Dependency()
    rbac_manager = providers.Dependency()
    sql_script_manager = providers.Dependency()
    databricks_job_manager = providers.Dependency()
    databricks_token_manager = providers.Dependency()
    databricks_deploy_workflow = providers.Dependency()
    storage_manager = providers.Dependency()
    sql_server_firewall_manager = providers.Dependency()
    app_registration_manager = providers.Dependency()
    az_account_manager = providers.Dependency()
    az_webapp_manager = providers.Dependency()
    az_datafactory_manager = providers.Dependency()
    az_container_registry_manager = providers.Dependency()
    service_principal_manager = providers.Dependency()
    datalake_deploy_workflow = providers.Dependency()
    sql_database_manager = providers.Dependency()

    keyvault_handler = providers.Factory(
        KeyVaultHandler,
        app_config=app_config,
        environment_config=environment_config,
        keyvault_manager=keyvault_manager
    )

    bicep_handler = providers.Factory(
        BicepHandler,
        app_config=app_config,
        deploy_bicep_workflow=deploy_bicep_workflow
    )

    rbac_handler = providers.Factory(
        RbacHandler,
        app_config=app_config,
        environment_config=environment_config,
        rbac_manager=rbac_manager
    )

    sql_server_handler = providers.Factory(
        SqlServerHandler,
        app_config=app_config,
        sql_script_manager=sql_script_manager,
        sql_server_firewall_manager=sql_server_firewall_manager,
        sql_database_manager=sql_database_manager
    )

    storage_handler = providers.Factory(
        StorageHandler,
        app_config=app_config,
        storage_manager=storage_manager,
        datalake_deploy_workflow=datalake_deploy_workflow
    )

    app_registration_handler = providers.Factory(
        AppRegistrationHandler,
        app_config=app_config,
        app_registration_manager=app_registration_manager
    )

    account_handler = providers.Factory(
        AccountHandler,
        app_config=app_config,
        az_account_manager=az_account_manager
    )
    
    service_principal_handler = providers.Factory(
        ServicePrincipalHandler,
        app_config=app_config,
        service_principal_manager=service_principal_manager
    )

    webapp_handler = providers.Factory(
        WebappHandler,
        app_config=app_config,
        manager=az_webapp_manager
    )

    databricks_handler = providers.Factory(
        DatabricksHandler,
        app_config=app_config,
        databricks_deploy_workflow=databricks_deploy_workflow,
        databricks_job_manager=databricks_job_manager,
        databricks_token_manager=databricks_token_manager,
        az_keyvault_manager=keyvault_manager,
        account_handler=account_handler
    )

    datafactory_handler = providers.Factory(
        DatafactoryHandler,
        app_config=app_config,
        manager=az_datafactory_manager
    )

    container_registry_handler = providers.Factory(
        ContainerRegistryHandler,
        app_config=app_config,
        manager=az_container_registry_manager
    )

    # leave at bottom of class
    handler_facade = providers.Factory(
        HandlerFacade,
        keyvault_handler=keyvault_handler,
        bicep_handler=bicep_handler,
        rbac_handler=rbac_handler,
        sql_server_handler=sql_server_handler,
        databricks_handler=databricks_handler,
        storage_handler=storage_handler,
        app_registration_handler=app_registration_handler,
        account_handler=account_handler,
        service_principal_handler=service_principal_handler,
        webapp_handler=webapp_handler,
        datafactory_handler=datafactory_handler,
        container_registry_handler=container_registry_handler
    )
