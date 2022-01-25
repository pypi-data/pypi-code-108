import abc

from whizbang.core.workflow_task import IWorkflowTask, WorkflowTask
from whizbang.domain.manager.az.az_account_manager import AzAccountManager
from whizbang.domain.manager.az.az_storage_manager import IAzStorageManager
from whizbang.domain.models.storage.datalake_state import DatalakeState
from whizbang.domain.repository.az.az_active_directory_repository import AzActiveDirectoryRepository


class IDatalakeTask(IWorkflowTask):

    @abc.abstractmethod
    def run(self, request: DatalakeState):
        """"""

class CreateDatalakeFileSystemTask(WorkflowTask, IDatalakeTask):
    def __init__(self, manager: IAzStorageManager):
        WorkflowTask.__init__(self)
        self.manager = manager

    @property
    def task_name(self) -> str:
        return "create_datalake_file_system"

    def run(self, request: DatalakeState):
        self.manager.create_file_system(file_system=request.storage_container)



class DatalakeDeployTask(WorkflowTask, IDatalakeTask):
    def __init__(
            self,
            active_directory_repository: AzActiveDirectoryRepository,
            account_manager: AzAccountManager
    ):
        WorkflowTask.__init__(self)
        self.account_manager = account_manager
        self.ad_repository = active_directory_repository

    @property
    def __get_object_id_strategy(self):
        return {
            "user": self.__get_user_object_id,
            "servicePrincipal": self.__get_service_principal_id,
        }

    def _get_object_id(self) -> str:
        account = self.account_manager.get_account()
        object_id = self.__get_object_id_strategy[account.account_type](account.name)
        return object_id

    def __get_user_object_id(self, email: str):
        return self.ad_repository.get_object_id(lookup_type='email', lookup_value=email)

    def __get_service_principal_id(self, app_id: str):
        return self.ad_repository.get_object_id(lookup_type='serviceprincipal', lookup_value=app_id)


class UpdateDatalakeAclTask(DatalakeDeployTask, IDatalakeTask):
    def __init__(self, manager: IAzStorageManager, active_directory_repository, account_manager):
        DatalakeDeployTask.__init__(self, active_directory_repository=active_directory_repository, account_manager=account_manager)
        self.manager = manager

    @property
    def task_name(self) -> str:
        return "update_acl"

    def run(self, request: DatalakeState):
        object_id = self._get_object_id()
        self.manager.update_datalake_container_acl(
            datalake_container=request.storage_container, object_id=object_id, permissions='rwx')


class CreateDatalakeFoldersTask(WorkflowTask, IDatalakeTask):
    def __init__(self, manager: IAzStorageManager):
        WorkflowTask.__init__(self)
        self.manager = manager

    @property
    def task_name(self) -> str:
        return "create_datalake_folders"

    def run(self, request: DatalakeState):
        self.manager.create_datalake_directories(directories=request.datalake_json['folder-names'],
                                                 storage_container=request.storage_container)


class RemoveDatalakeAclTask(DatalakeDeployTask, IDatalakeTask):
    def __init__(self, manager: IAzStorageManager, active_directory_repository, account_manager):
        DatalakeDeployTask.__init__(self, active_directory_repository=active_directory_repository, account_manager=account_manager)
        self.manager = manager

    @property
    def task_name(self) -> str:
        return "remove_acl"

    def run(self, request: DatalakeState):
        object_id = self._get_object_id()
        self.manager.remove_datalake_container_acl(datalake_container=request.storage_container, object_id=object_id)
