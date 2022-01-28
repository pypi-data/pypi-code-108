from benchling_api_client.api.warehouse import create_warehouse_credentials

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.models import WarehouseCredentials, WarehouseCredentialsCreate
from benchling_sdk.services.base_service import BaseService


class WarehouseService(BaseService):
    """
    Warehouse.

    Manage warehouse credentials.

    See https://benchling.com/api/reference#/Warehouse
    """

    @api_method
    def create_credentials(self, credentials: WarehouseCredentialsCreate) -> WarehouseCredentials:
        """
        Create Benchling Warehouse credentials.

        Allows for programmatically generating credentials to connect to the Benchling warehouse.
        You must have a warehouse configured to access this endpoint.

        The credentials will authenticate as the same user calling the API. Note that `expires_in` is required -
        only temporary credentials are currently allowed.

        See https://benchling.com/api/reference#/Warehouse/createWarehouseCredentials
        """
        response = create_warehouse_credentials.sync_detailed(client=self.client, json_body=credentials)
        return model_from_detailed(response)
