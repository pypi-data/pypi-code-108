from tktl import __version__
from tktl.commands import BaseTaktileApiCommand, CommandBase
from tktl.core.clients.http_client import interpret_response
from tktl.core.config import set_api_key, settings
from tktl.core.exceptions import APIClientException
from tktl.core.loggers import LOG
from tktl.core.schemas.user import TaktileUser
from tktl.login import login, logout
from tktl.version import TaktileVersionChecker


class LogInCommand(BaseTaktileApiCommand):
    def execute(self, api_key=None):
        if login(api_key):
            response = self.client.get(f"{settings.API_V1_STR}/users/me")
            try:
                user = interpret_response(response, TaktileUser)
            except APIClientException as e:
                LOG.error(f"Authentication failed: {e.detail}")
                return False
            LOG.log(
                f"Authentication successful for user: {user.username}", color="green"
            )
            return True
        return False


class LogOutCommand(CommandBase):
    def execute(self):
        logout()


class ShowVersionCommand(CommandBase):
    def execute(self, check: bool = False):
        LOG.log(__version__)
        if check:
            TaktileVersionChecker.look_for_new_version()


class SetApiKeyCommand(CommandBase):
    def execute(self, api_key):
        if not api_key:
            LOG.error("API Key cannot be empty.")
            return
        set_api_key(api_key)
        LOG.log(
            f"Successfully added your API Key to {settings.TAKTILE_CONFIG_FILE} You're ready to go!"
        )
