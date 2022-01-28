import pathlib
from typing import Optional

import attr


@attr.s(slots=True)
class Plan:
    lrn: str = attr.ib()
    catalog: pathlib.Path = attr.ib()
    workspace_id: str = attr.ib()
    name: Optional[str] = attr.ib(default=None)

    def iter_suite(self):
        return (self.catalog / self.name).iterdir()
