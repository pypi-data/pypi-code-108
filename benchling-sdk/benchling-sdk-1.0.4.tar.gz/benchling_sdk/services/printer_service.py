from typing import List

from benchling_api_client.api.printers import list_printers
from benchling_api_client.models.printer import Printer
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.services.base_service import BaseService


class PrinterService(BaseService):
    """
    Printers.

    List printers.

    See https://benchling.com/api/reference#/Printers
    """

    @api_method
    def get_list(self, registry_id: str) -> List[Printer]:
        """
        List printers.

        See https://benchling.com/api/reference#/Printers/listPrinters

        :param registry_id: ID of the registry to list printers from.
        :return: A list of printers
        :rtype: List[Printer]
        """
        response = list_printers.sync_detailed(client=self.client, registry_id=registry_id)
        results = model_from_detailed(response)
        return results.label_printers
