import logging
from typing import List, Union

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.models import WellMergeRules

logger = logging.getLogger(__name__)


class WellMergeRulesAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def set(self, rules: Union[WellMergeRules, List[str]]) -> WellMergeRules:
        path = self._get_path("/wells/mergerules")

        # If the user passes a list, we will set this order for all attributes
        if isinstance(rules, list):
            rules = WellMergeRules(
                name=rules,
                description=rules,
                country=rules,
                quadrant=rules,
                region=rules,
                block=rules,
                field=rules,
                operator=rules,
                spud_date=rules,
                license=rules,
                well_type=rules,
                water_depth=rules,
                wellhead=rules,
            )

        response: Response = self.client.post(path, rules.json())
        merge_rules: WellMergeRules = WellMergeRules.parse_obj(response.json())
        return merge_rules

    def retrieve(self) -> WellMergeRules:
        path = self._get_path("/wells/mergerules")
        response: Response = self.client.get(path)
        merge_rules: WellMergeRules = WellMergeRules.parse_obj(response.json())
        return merge_rules
