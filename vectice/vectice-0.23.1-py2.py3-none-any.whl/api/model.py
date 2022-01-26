from typing import Optional
from urllib.parse import urlencode

from vectice.api.project import ProjectApi
from vectice.entity import Model

from .Page import Page
from .json_object import JsonObject
from .output.model_output import ModelOutput
from .output.paged_response import PagedResponse


class ModelApi(ProjectApi):
    def __init__(self, project_token: str, _token: Optional[str] = None, allow_self_certificate=True):
        super().__init__(project_token=project_token, _token=_token, allow_self_certificate=allow_self_certificate)
        self._model_path = super().api_base_path + "/model"

    @property
    def api_base_path(self) -> str:
        return self._model_path

    def list_models(self, search: str = None, page_index=Page.index, page_size=Page.size) -> PagedResponse[ModelOutput]:
        queries = {"index": page_index, "size": page_size}
        if search:
            queries["search"] = search
        models = self._get(self.api_base_path + "?" + urlencode(queries))
        return PagedResponse(item_cls=ModelOutput, total=models["total"], page=models["page"], items=models["items"])

    def create_model(self, model: JsonObject) -> Model:
        if model.get("name") is None:
            raise ValueError('"name" must be provided in model.')
        if model.get("type") is None:
            model["type"] = "OTHER"
        return Model(self._post(self.api_base_path, model))

    def update_model(self, model_id: int, model: JsonObject) -> Model:
        return Model(self._put(self.api_base_path + "/" + str(model_id), model))
