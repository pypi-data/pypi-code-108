from whizbang.core.workflow import Workflow, IWorkflow
from whizbang.core.workflow_task import IWorkflowTask
from whizbang.domain.manager.az.az_account_manager import AzAccountManager
from whizbang.domain.workflow.databricks.databricks_tasks import CreateJobsTask, CreateNotebooksTask, \
    CreateClustersTask, \
    CreatePoolsTask, CreateLibrariesTask, UpdateClusterSecretScopeTask, PinClustersTask, \
    UpdateUniversalClusterFieldsTask


class IDatabricksDeployWorkflow(IWorkflow):
    """"""


class DatabricksDeployWorkflow(Workflow, IDatabricksDeployWorkflow):
    def __init__(self, create_pools_task: CreatePoolsTask,
                 create_cluster_secret_scope_task: UpdateClusterSecretScopeTask,
                 update_universal_cluster_env_variables_task: UpdateUniversalClusterFieldsTask,
                 create_clusters_task: CreateClustersTask,
                 pin_clusters_task: PinClustersTask,
                 create_libraries_task: CreateLibrariesTask,
                 create_notebooks_task: CreateNotebooksTask,
                 create_jobs_task: CreateJobsTask):
        self.create_pools_task = create_pools_task
        self.create_clusters_task = create_clusters_task
        self.update_universal_cluster_env_variables_task = update_universal_cluster_env_variables_task
        self.pin_clusters_task = pin_clusters_task
        self.create_libraries_task = create_libraries_task
        self.create_notebooks_task = create_notebooks_task
        self.create_jobs_task = create_jobs_task
        self.create_cluster_secret_scope_task = create_cluster_secret_scope_task

    def _get_workflow_tasks(self) -> 'list[IWorkflowTask]':
        workflow: list[IWorkflowTask] = [self.create_pools_task,
                                         self.create_cluster_secret_scope_task,
                                         self.update_universal_cluster_env_variables_task,
                                         self.create_clusters_task,
                                         self.pin_clusters_task,
                                         self.create_libraries_task,
                                         self.create_notebooks_task,
                                         self.create_jobs_task]
        return workflow
