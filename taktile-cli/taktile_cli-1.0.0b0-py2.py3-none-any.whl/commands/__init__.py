from typing import Optional

from taktile_client.config import collect_api_key
from taktile_types.enums.instance import ServiceType

from tktl.core.clients import DeploymentApiClient
from tktl.core.clients.arrow import ArrowFlightClient
from tktl.core.clients.rest import RestClient
from tktl.core.clients.taktile import TaktileApiClient
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
        endpoint_name: str = "",
        local: bool = False,
        logger: Logger = LOG,
        skip_auth: bool = False,
    ):
        self.kind = kind
        self.client_params = {
            "api_key": api_key,
            "repository_name": repository,
            "branch_name": branch_name,
            "endpoint_name": endpoint_name,
            "local": local,
            "logger": logger,
            "skip_auth": skip_auth,
        }
        self.client = self._get_client()

    def execute(self, *args, **kwargs):
        pass

    def _get_client(self):
        return (
            RestClient(**self.client_params)
            if self.kind == ServiceType.REST
            else ArrowFlightClient(**self.client_params)
        )


class BaseDeploymentApiCommand:
    def __init__(self, logger: Logger = LOG):
        self.client = DeploymentApiClient(logger=logger)


class BaseTaktileApiCommand:
    def __init__(self, logger: Logger = LOG):
        self.client = TaktileApiClient(logger=logger)


class BaseRestClientCommand(BaseClientCommand):
    def __init__(
        self,
        repository: str,
        branch_name: str,
        local: bool,
        logger: Logger = LOG,
        skip_auth: bool = False,
    ):
        super().__init__(
            kind=ServiceType.REST,
            api_key=collect_api_key(),
            repository=repository,
            branch_name=branch_name,
            local=local,
            logger=logger,
            skip_auth=skip_auth,
        )


class BaseGrpcClientCommand(BaseClientCommand):
    def __init__(
        self,
        repository: str,
        branch_name: str,
        local: bool,
        logger: Logger = LOG,
        skip_auth: bool = False,
    ):
        super().__init__(
            kind=ServiceType.GRPC,
            api_key=collect_api_key(),
            repository=repository,
            branch_name=branch_name,
            local=local,
            logger=logger,
            skip_auth=skip_auth,
        )
