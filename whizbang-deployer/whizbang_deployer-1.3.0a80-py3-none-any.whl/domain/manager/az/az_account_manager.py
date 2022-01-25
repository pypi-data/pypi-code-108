from whizbang.domain.manager.az.az_manager_base import AzManagerBase
from whizbang.domain.models.active_directory.az_account import AzAccount
from whizbang.domain.repository.az.az_account_repository import AzAccountRepository


class AzAccountManager(AzManagerBase):
    def __init__(self, repository: AzAccountRepository):
        super().__init__(repository)
        self._repository: AzAccountRepository

    def get_account(self) -> AzAccount:
        return self._repository.get_account()

    def set_subscription(self, subscription_id: str):
        return self._repository.set_subscription(subscription_id=subscription_id)
