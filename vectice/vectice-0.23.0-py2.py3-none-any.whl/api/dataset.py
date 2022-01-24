from typing import Optional
from urllib.parse import urlencode

from vectice.entity.dataset import Dataset

from .Page import Page
from .json_object import JsonObject
from .output.dataset_output import DatasetOutput
from .output.paged_response import PagedResponse
from .project import ProjectApi


class DatasetApi(ProjectApi):
    def __init__(self, project_token: str, _token: Optional[str] = None, allow_self_certificate=True):
        super().__init__(project_token=project_token, _token=_token, allow_self_certificate=allow_self_certificate)
        self._dataset_path = super().api_base_path + "/dataset"

    @property
    def api_base_path(self) -> str:
        return self._dataset_path

    def list_datasets(
        self, search: str = None, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[DatasetOutput]:
        queries = {"index": page_index, "size": page_size}
        if search:
            queries["search"] = search
        datasets = self._get(self.api_base_path + "?" + urlencode(queries))
        return PagedResponse(
            item_cls=DatasetOutput, total=datasets["total"], page=datasets["page"], items=datasets["items"]
        )

    def create_dataset(self, dataset: JsonObject) -> Dataset:
        if dataset.get("name") is None:
            raise ValueError('"name" must be provided in dataset.')
        return Dataset(self._post(self.api_base_path, dataset))

    def update_dataset(self, dataset_id: int, dataset: JsonObject) -> Dataset:
        return Dataset(self._put(self.api_base_path + "/" + str(dataset_id), dataset))
