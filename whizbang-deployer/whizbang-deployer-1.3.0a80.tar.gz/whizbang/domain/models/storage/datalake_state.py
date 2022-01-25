from typing import List

from whizbang.domain.models.storage.storage_resource import StorageContainer


class DatalakeState:
    def __init__(self,
                 datalake_json: dict,
                 storage_container: StorageContainer):
        self.storage_container = storage_container
        self.datalake_json = datalake_json
