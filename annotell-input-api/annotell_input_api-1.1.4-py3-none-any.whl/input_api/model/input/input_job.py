from dataclasses import dataclass
from typing import Dict
from annotell.input_api.model.abstract.abstract_models import Response


@dataclass
class InputJobCreated(Response):
    input_uuid: str
    files: Dict[str, str]

    @staticmethod
    def from_json(js: dict):
        return InputJobCreated(js["internalId"], js["files"])

    def __str__(self):
        return f"{self.__class__.__name__}(input_uuid={self.input_uuid}, files={{...}})"


@dataclass
class CreateInputResponse:
    input_uuid: str

    @staticmethod
    def from_input_job_response(input_job: InputJobCreated):
        return CreateInputResponse(input_job.input_uuid)
