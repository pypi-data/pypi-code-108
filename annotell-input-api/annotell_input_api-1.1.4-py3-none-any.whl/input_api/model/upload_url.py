from typing import Dict
from dataclasses import dataclass
from annotell.input_api.model.abstract.abstract_models import Response


@dataclass
class UploadUrls(Response):
    files_to_url: Dict[str, str]
    input_uuid: int

    @staticmethod
    def from_json(js: dict):
        return UploadUrls(
            # property names does not match.
            files_to_url=js["files"],
            input_uuid=js["jobId"]
        )
