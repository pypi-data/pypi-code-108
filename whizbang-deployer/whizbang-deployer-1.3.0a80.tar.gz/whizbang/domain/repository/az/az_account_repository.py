from typing import Optional

from whizbang.data.az_cli_context import AzCliContext
from whizbang.data.az_cli_response import AzCliResponse
from whizbang.domain.models.active_directory.az_account import AzAccount
from whizbang.domain.repository.az.az_repository_base import AzRepositoryBase

class AzAccountRepository(AzRepositoryBase):
    def __init__(self, context: AzCliContext):
        AzRepositoryBase.__init__(self, context)

    @property
    def _resource_provider(self) -> str:
        return "account"

    def get_account(self) -> Optional[AzAccount]:
        """[summary] Returns the current account that is logged in.

        Returns:
            AzAccount: [description] representing the account type and name.
            None: [description] if no account is logged in.
        """
        account_details: dict = self._execute("show").results
        
        # If we have no results, we return None
        if account_details is None:
            return None
    
        account_type = account_details['user']['type']
        name = account_details['user']['name']
        
        return AzAccount(account_type=account_type, name=name)
            
    def set_subscription(self, subscription_id: str) -> AzCliResponse:
        """[summary] Sets the selected subscription.

        Args:
            subscription (str): [description] the id of the subscription to be selected.

        Returns:
            AzCliResponse: [description]
        """
        return self._execute(f'set --subscription \'{subscription_id}\'')
