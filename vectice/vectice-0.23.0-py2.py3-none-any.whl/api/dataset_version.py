from typing import Optional, List, Union
from urllib.parse import urlencode

from vectice.api.dataset import DatasetApi
from vectice.entity import DatasetVersion

from .Page import Page
from .json_object import JsonObject
from .output.dataset_version_output import DatasetVersionOutput
from .output.paged_response import PagedResponse
from .output.property_output import EntityPropertyOutput


class DatasetVersionApi(DatasetApi):
    def __init__(self, project_token: str, dataset_id: int, _token: Optional[str] = None, allow_self_certificate=True):
        super().__init__(project_token=project_token, _token=_token, allow_self_certificate=allow_self_certificate)
        self._dataset_id = dataset_id
        self._dataset_version_path = super().api_base_path + "/" + str(dataset_id) + "/version"

    @property
    def dataset_id(self) -> int:
        return self._dataset_id

    @property
    def api_base_path(self) -> str:
        return self._dataset_version_path

    def list_dataset_versions(self, page_index=Page.index, page_size=Page.size) -> PagedResponse[DatasetVersionOutput]:
        queries = {"index": page_index, "size": page_size}
        dataset_versions = self._get(self.api_base_path + "?" + urlencode(queries))
        return PagedResponse(
            item_cls=DatasetVersionOutput,
            total=dataset_versions["total"],
            page=dataset_versions["page"],
            items=dataset_versions["items"],
        )

    def get_dataset_version(
        self, search: str, page_index=Page.index, page_size=Page.size
    ) -> Optional[DatasetVersionOutput]:
        queries = {"index": page_index, "size": page_size, "search": search}
        try:
            dataset_version = self._get(self.api_base_path + "?" + urlencode(queries)).get("items")[0]  # type: ignore
        except IndexError:
            return None
        return DatasetVersionOutput(**dataset_version)

    def create_dataset_version(self, dataset_version: JsonObject) -> DatasetVersion:
        return DatasetVersion(self._post(self.api_base_path, dataset_version))

    def update_dataset_version(self, dataset_id: int, dataset_version) -> DatasetVersion:
        return DatasetVersion(self._put(self.api_base_path + "/" + str(dataset_id), dataset_version))

    def create_dataset_version_properties(self, dataset_version_id: int, properties: Union[List[dict], dict]):
        if isinstance(properties, dict):
            DatasetVersion(self._post(self.api_base_path + f"/{dataset_version_id}/entityProperty/", properties))
        elif len(properties) >= 1:
            for prop in properties:
                DatasetVersion(self._post(self.api_base_path + f"/{dataset_version_id}/entityProperty/", prop))

    def update_dataset_version_properties(self, dataset_version_id: int, property_id: int, properties: JsonObject):
        return DatasetVersion(
            self._put(self.api_base_path + f"/{dataset_version_id}/entityProperty/{property_id}", properties)
        )

    def list_dataset_version_properties(
        self, dataset_version_id: int, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[EntityPropertyOutput]:
        queries = {"index": page_index, "size": page_size}
        model_version_properties = self._get(
            self.api_base_path + f"/{dataset_version_id}/entityProperty?" + urlencode(queries)
        )
        properties = [
            EntityPropertyOutput.from_dict(property).as_dict() for property in model_version_properties["items"]
        ]
        return PagedResponse(
            item_cls=EntityPropertyOutput,
            total=model_version_properties["total"],
            page=model_version_properties["page"],
            items=properties,
        )
