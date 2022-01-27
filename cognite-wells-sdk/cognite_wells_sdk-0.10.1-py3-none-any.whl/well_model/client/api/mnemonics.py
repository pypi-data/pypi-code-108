import logging
from typing import List

from requests import Response

from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import MnemonicMatchList
from cognite.well_model.models import MnemonicMatchGroup, MnemonicMatchItems, MnemonicSearch

logger = logging.getLogger(__name__)


class MnemonicsAPI(BaseAPI):
    def search(self, mnemonics: List[str]) -> MnemonicMatchList:
        """Search for measurement types using mnemonics

        Args:
            mnemonics (List[str]): List of mnemonics

        Returns:
            List[MnemonicMatchGroup]: List of match _groups_. There is one group for each mnemonic in the search term.
        """
        path = self._get_path("/mnemonics/search")
        json = MnemonicSearch(mnemonics=mnemonics).json()
        response: Response = self.client.post(path, json)
        groups: List[MnemonicMatchGroup] = MnemonicMatchItems.parse_obj(response.json()).items
        return MnemonicMatchList(groups)
