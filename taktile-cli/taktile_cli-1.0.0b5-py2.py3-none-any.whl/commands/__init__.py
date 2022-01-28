from typing import Optional

from taktile_client import ArrowClient, RestClient
from taktile_client.config import collect_api_key
from taktile_types.enums.instance import ServiceType

from tktl.core.clients import DeploymentApiClient
from tktl.core.clients.taktile import TaktileApiClient
from tktl.core.config import settings
from tktl.core.loggers import LOG, Logger


class CommandBase(object):
    def __init__(self, api=None):
        self.api = api


class BaseClientCommand:
    def __init__(
        self,
        kind: ServiceType,
        api_key: Optional[str],
        repository: str,
        branch_name: str,
        local: bool = False,
    ):
        self.kind = kind
        self.client_params = {
            "api_key": api_key,
            "repository_name": repository,
            "branch_name": branch_name,
        }
        self.local = local
        self.client = self._get_client()

    def execute(self, *args, **kwargs):
        pass

    def _get_client(self):

        if self.local:
            return (
                RestClient.from_url(settings.LOCAL_REST_ENDPOINT, api_key=None)
                if self.kind == ServiceType.REST
                else ArrowClient.from_url(settings.LOCAL_ARROW_ENDPOINT, api_key=None)
            )
        return (
            RestClient(**self.client_params)
            if self.kind == ServiceType.REST
            else ArrowClient(**self.client_params)
        )


class BaseDeploymentApiCommand:
    def __init__(self, logger: Logger = LOG):
        self.client = DeploymentApiClient(logger=logger)


class BaseTaktileApiCommand:
    def __init__(self, logger: Logger = LOG):
        self.client = TaktileApiClient(logger=logger)


class BaseRestClientCommand(BaseClientCommand):
    def __init__(self, repository: str, branch_name: str, local: bool = False):
        super().__init__(
            kind=ServiceType.REST,
            api_key=collect_api_key(),
            repository=repository,
            branch_name=branch_name,
            local=local,
        )


class BaseGrpcClientCommand(BaseClientCommand):
    def __init__(
        self, repository: str, branch_name: str, local: bool = False,
    ):
        super().__init__(
            kind=ServiceType.GRPC,
            api_key=collect_api_key(),
            repository=repository,
            branch_name=branch_name,
            local=local,
        )
