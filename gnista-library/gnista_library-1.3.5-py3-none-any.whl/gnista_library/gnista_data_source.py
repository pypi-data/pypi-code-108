import uuid
from typing import List, Type, TypeVar, Union

from structlog import get_logger

from data_source_client import AuthenticatedClient
from data_source_client.api.data_source import (
    data_source_create_data_source,
    data_source_create_data_source_2,
    data_source_get,
    data_source_get_2,
)
from data_source_client.models.auto_detect_task_config import AutoDetectTaskConfig
from data_source_client.models.data_import_description_config import DataImportDescriptionConfig
from data_source_client.models.data_source_details_dto import DataSourceDetailsDTO
from data_source_client.models.en_data_source_state import EnDataSourceState
from data_source_client.models.problem_details import ProblemDetails
from data_source_client.models.update_data_source_request import UpdateDataSourceRequest
from data_source_client.types import UNSET, Unset

from .gnista_connetion import GnistaConnection

log = get_logger()

# pylint: disable=C0103
T = TypeVar("T", bound="GnistaDataSource")


class GnistaDataSource:

    data_source_id: uuid.UUID
    data_import_description: Union[Unset, None, DataImportDescriptionConfig] = UNSET
    auto_detect_task_configs: Union[Unset, None, List[AutoDetectTaskConfig]] = UNSET
    details: Union[Unset, None, DataSourceDetailsDTO] = UNSET
    created_data_points: Union[Unset, None, List[str]] = UNSET
    state: Union[Unset, EnDataSourceState] = UNSET

    @classmethod
    def create_new(
        cls: Type[T],
        connection: GnistaConnection,
        request: UpdateDataSourceRequest,
    ) -> Union[T, None]:
        token = connection.get_access_token()
        client = AuthenticatedClient(
            base_url=connection.datasource_base_url, token=token, verify_ssl=connection.verify_ssl
        )

        new_id = uuid.uuid4()
        if connection.id_token:
            response = data_source_create_data_source.sync(data_source_id=str(new_id), client=client, json_body=request)
        else:
            response = data_source_create_data_source_2.sync(
                client=client, data_source_id=str(new_id), tenant_name=connection.tenant_name, json_body=request
            )

        if isinstance(response, ProblemDetails):
            log.error(response)
            return None

        data_source = cls(connection=connection, data_source_id=new_id)
        return data_source

    def __init__(self, connection: GnistaConnection, data_source_id: uuid.UUID):
        self.connection = connection
        self.data_source_id = data_source_id
        self._load_details()

    def __str__(self):
        return "GnistaDataSource " + self.data_source_id

    def _load_details(self):
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datasource_base_url, token=token, verify_ssl=self.connection.verify_ssl
        )
        if self.connection.id_token:
            data_source = data_source_get.sync(client=client, data_source_id=str(self.data_source_id))
        else:
            data_source = data_source_get_2.sync(
                client=client,
                data_source_id=str(self.data_source_id),
                tenant_name=self.connection.tenant_name,
            )
        if data_source is None:
            raise Exception("Cannot load Datasource")

        self.data_import_description = data_source.data_import_description
        self.auto_detect_task_configs = data_source.auto_detect_task_configs
        self.details = data_source.details
        self.created_data_points = data_source.created_data_points
        self.state = data_source.state

    def update(self, request: UpdateDataSourceRequest):
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datasource_base_url, token=token, verify_ssl=self.connection.verify_ssl
        )

        if self.connection.id_token:
            response = data_source_create_data_source.sync(
                data_source_id=str(self.data_source_id), client=client, json_body=request
            )
        else:
            response = data_source_create_data_source_2.sync(
                client=client,
                data_source_id=str(self.data_source_id),
                tenant_name=self.connection.tenant_name,
                json_body=request,
            )

        if isinstance(response, ProblemDetails):
            log.error(response)
            return
