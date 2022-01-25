from abc import abstractmethod

from whizbang.config.app_config import AppConfig
from whizbang.domain.handler.handler_base import IHandler, HandlerBase
from whizbang.domain.manager.az.az_storage_manager import IAzStorageManager
from whizbang.domain.models.storage.datalake_state import DatalakeState
from whizbang.domain.models.storage.storage_resource import StorageContainer
from whizbang.domain.workflow.datalake.datalake_deploy_workflow import DatalakeDeployWorkflow
from whizbang.util import path_defaults
from whizbang.util.json_helpers import import_local_json


class IStorageHandler(IHandler):
    """"""

    @abstractmethod
    def deploy_datalake_directories(self, solution_name, storage_account_name):
        """"""

    @abstractmethod
    def get_storage_account_key(self, storage_account_name: str) -> str:
        """"""


class StorageHandler(HandlerBase, IStorageHandler):
    def __init__(self, app_config: AppConfig, storage_manager: IAzStorageManager,
                 datalake_deploy_workflow: DatalakeDeployWorkflow):
        HandlerBase.__init__(self, app_config=app_config)
        self.__storage_manager = storage_manager
        self.__datalake_deploy_workflow = datalake_deploy_workflow

    def deploy_datalake_directories(self, solution_name, storage_account_name):
        datalake_state_path = path_defaults.get_datalake_state_path(app_config=self._app_config,
                                                                    solution_name=solution_name)
        datalake_json = import_local_json(f'{datalake_state_path}/datalake.json')

        for container in datalake_json['containers']:
            storage_container = StorageContainer(container_name=container['container-name'],
                                                 storage_account_name=storage_account_name)
            datalake_state = DatalakeState(storage_container=storage_container,
                                           datalake_json=container)
            self.__datalake_deploy_workflow.run(request=datalake_state)

    def get_storage_account_key(self, storage_account_name: str) -> str:
        return self.__storage_manager.get_storage_account_key(storage_account_name)
