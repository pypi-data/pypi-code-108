from dependency_injector import containers, providers

from whizbang.domain.workflow.bicep.deploy_bicep_workflow import DeployBicepWorkflow
from whizbang.domain.workflow.bicep.bicep_tasks import WriteBicepParametersFileTask, DeployBicepTemplateTask
from whizbang.domain.workflow.databricks.databricks_deploy_workflow import DatabricksDeployWorkflow
from whizbang.domain.workflow.databricks.databricks_tasks import CreatePoolsTask, CreateJobsTask, CreateNotebooksTask, \
    CreateLibrariesTask, CreateClustersTask, UpdateClusterSecretScopeTask, PinClustersTask, \
    UpdateUniversalClusterFieldsTask
from whizbang.domain.workflow.datalake.datalake_deploy_workflow import DatalakeDeployWorkflow
from whizbang.domain.workflow.datalake.datalake_task import UpdateDatalakeAclTask, RemoveDatalakeAclTask, \
    CreateDatalakeFoldersTask, CreateDatalakeFileSystemTask


class WorkflowContainer(containers.DeclarativeContainer):

    # dependencies
    bicep_deployment_manager = providers.Dependency()
    databricks_pool_manager = providers.Dependency()
    databricks_cluster_manager = providers.Dependency()
    databricks_library_manager = providers.Dependency()
    databricks_notebook_manager = providers.Dependency()
    databricks_job_manager = providers.Dependency()
    databricks_secret_scope_manager = providers.Dependency()
    az_storage_manager = providers.Dependency()
    az_account_manager = providers.Dependency()
    az_active_directory_repository = providers.Dependency()

    # tasks
    write_bicep_parameters_file_task = providers.Factory(WriteBicepParametersFileTask)

    create_pools_task = providers.Factory(
        CreatePoolsTask,
        manager=databricks_pool_manager
    )

    create_cluster_secret_scope_task = providers.Factory(
        UpdateClusterSecretScopeTask,
        manager=databricks_secret_scope_manager,
        account_manager=az_account_manager
    )

    update_universal_cluster_env_variables_task = providers.Factory(
        UpdateUniversalClusterFieldsTask,
        manager=databricks_cluster_manager
    )

    create_clusters_task = providers.Factory(
        CreateClustersTask,
        manager=databricks_cluster_manager
    )

    pin_clusters_task = providers.Factory(
        PinClustersTask,
        manager=databricks_cluster_manager
    )

    create_libraries_task = providers.Factory(
        CreateLibrariesTask,
        manager=databricks_library_manager,
    )

    create_notebooks_task = providers.Factory(
        CreateNotebooksTask,
        manager=databricks_notebook_manager
    )

    create_jobs_task = providers.Factory(
        CreateJobsTask,
        manager=databricks_job_manager
    )

    deploy_bicep_template_task = providers.Factory(
        DeployBicepTemplateTask,
        bicep_deployment_manager=bicep_deployment_manager
    )

    update_datalake_acl_task = providers.Factory(
        UpdateDatalakeAclTask,
        manager=az_storage_manager,
        active_directory_repository=az_active_directory_repository,
        account_manager=az_account_manager
    )

    create_datalake_file_system_task = providers.Factory(
        CreateDatalakeFileSystemTask,
        manager=az_storage_manager
    )

    create_datalake_folders_task = providers.Factory(
        CreateDatalakeFoldersTask,
        manager=az_storage_manager
    )

    remove_datalake_acl_task = providers.Factory(
        RemoveDatalakeAclTask,
        manager=az_storage_manager,
        active_directory_repository=az_active_directory_repository,
        account_manager=az_account_manager
    )

    # workflows
    bicep_deployment_workflow = providers.Factory(
        DeployBicepWorkflow,
        write_bicep_parameters_file_task=write_bicep_parameters_file_task,
        deploy_bicep_template_task=deploy_bicep_template_task
    )

    databricks_deploy_workflow = providers.Factory(
        DatabricksDeployWorkflow,
        create_pools_task=create_pools_task,
        create_cluster_secret_scope_task=create_cluster_secret_scope_task,
        update_universal_cluster_env_variables_task=update_universal_cluster_env_variables_task,
        create_clusters_task=create_clusters_task,
        pin_clusters_task=pin_clusters_task,
        create_libraries_task=create_libraries_task,
        create_notebooks_task=create_notebooks_task,
        create_jobs_task=create_jobs_task,
    )

    datalake_deploy_workflow = providers.Factory(
        DatalakeDeployWorkflow,
        create_datalake_file_system_task=create_datalake_file_system_task,
        update_datalake_acl_task=update_datalake_acl_task,
        create_datalake_folders_task=create_datalake_folders_task,
        remove_datalake_acl_task=remove_datalake_acl_task
    )
