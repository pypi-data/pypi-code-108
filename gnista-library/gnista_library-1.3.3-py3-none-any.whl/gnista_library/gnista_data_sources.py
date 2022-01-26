import uuid
from typing import Generator, List

from structlog import get_logger

from data_source_client import AuthenticatedClient
from data_source_client.api.data_source import data_source_get_all
from data_source_client.models import ProblemDetails
from data_source_client.models.data_source_response import DataSourceResponse

from .gnista_connetion import GnistaConnection
from .gnista_data_source import GnistaDataSource

log = get_logger()


class GnistaDataSources:
    def __init__(self, connection: GnistaConnection, verify_ssl=True):
        self.connection = connection
        self.verify_ssl = verify_ssl

    def get_data_source_list(self) -> Generator[GnistaDataSource, None, None]:
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datasource_base_url, token=token, verify_ssl=self.connection.verify_ssl
        )

        data_source_list = data_source_get_all.sync(client=client)
        if isinstance(data_source_list, ProblemDetails):
            problems: ProblemDetails = data_source_list
            raise Exception(problems)

        if isinstance(data_source_list, list):
            list_of_data_sources: List[DataSourceResponse] = data_source_list

        for data_source in list_of_data_sources:
            gnista_data_source = GnistaDataSource(
                connection=self.connection, data_source_id=uuid.UUID(data_source.data_source_id)
            )
            yield gnista_data_source
