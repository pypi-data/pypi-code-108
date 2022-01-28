from dataclasses import dataclass
from annotell.input_api.model.abstract.abstract_models import Response
from typing import Union


@dataclass
class ExportAnnotation(Response):
    annotation_id: int
    export_content: Union[list, dict]

    @staticmethod
    def from_json(js: dict):
        return ExportAnnotation(annotation_id=int(js["annotationId"]), export_content=js["exportContent"])
