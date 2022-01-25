from whizbang.config.app_config import AppConfig
from whizbang.domain.handler.handler_base import HandlerBase
from whizbang.domain.manager.az.az_account_manager import AzAccountManager
from whizbang.domain.models.active_directory.az_account import AzAccount


class AccountHandler(HandlerBase):
    def __init__(self, app_config: AppConfig, az_account_manager: AzAccountManager):
        HandlerBase.__init__(self, app_config=app_config)
        self.__az_account_manager = az_account_manager

    def get_account(self) -> AzAccount:
        return self.__az_account_manager.get_account()

    def switch_subscription(self, subscription_id: str):
        return self.__az_account_manager.set_subscription(subscription_id=subscription_id)
