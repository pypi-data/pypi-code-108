import logging
from typing import List, Union

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.models import WellboreMergeRules

logger = logging.getLogger(__name__)


class WellboreMergeRulesAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def set(
        self,
        rules: Union[WellboreMergeRules, List[str]],
    ) -> WellboreMergeRules:
        path = self._get_path("/wellbores/mergerules")

        # If the user passes a list, we will set this order for all attributes
        if isinstance(rules, list):
            rules = WellboreMergeRules(name=rules, description=rules, datum=rules, parents=rules, well_tops=rules)

        response: Response = self.client.post(path, rules.json())
        merge_rules: WellboreMergeRules = WellboreMergeRules.parse_obj(response.json())
        return merge_rules

    def retrieve(self) -> WellboreMergeRules:
        path = self._get_path("/wellbores/mergerules")
        response: Response = self.client.get(path)
        merge_rules: WellboreMergeRules = WellboreMergeRules.parse_obj(response.json())
        return merge_rules
