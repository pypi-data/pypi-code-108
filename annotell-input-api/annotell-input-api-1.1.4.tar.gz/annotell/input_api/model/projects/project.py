from dataclasses import dataclass
from datetime import datetime

from annotell.input_api.model.abstract.abstract_models import Response
from annotell.input_api.util import ts_to_dt


@dataclass
class Project(Response):
    created: datetime
    title: str
    description: str
    status: str
    project: str

    @staticmethod
    def from_json(js: dict):
        return Project(
            created=ts_to_dt(js["created"]), title=js["title"], description=js["description"], status=js["status"], project=js["project"]
        )
