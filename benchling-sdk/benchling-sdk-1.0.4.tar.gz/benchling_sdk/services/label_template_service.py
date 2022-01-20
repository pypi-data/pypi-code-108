from typing import List

from benchling_api_client.api.label_templates import list_label_templates
from benchling_api_client.models.label_template import LabelTemplate
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.services.base_service import BaseService


class LabelTemplateService(BaseService):
    """
    Label Templates.

    List label templates.

    See https://benchling.com/api/reference#/Label%20Templates
    """

    @api_method
    def get_list(self, registry_id: str) -> List[LabelTemplate]:
        """
        List label templates.

        See https://benchling.com/api/reference#/Label%20Templates/listLabelTemplates

        :param registry_id: The ID of the registry for which to list label templates
        :return: A list of label templates
        :rtype: List[LabelTemplate]
        """
        response = list_label_templates.sync_detailed(client=self.client, registry_id=registry_id)
        results = model_from_detailed(response)
        return results.label_templates
