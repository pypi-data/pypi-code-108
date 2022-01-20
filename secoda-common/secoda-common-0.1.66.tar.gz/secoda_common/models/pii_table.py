from typing import Optional, List

import attr
from marshmallow_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class PiiTable:
    database: str = attr.ib()
    cluster: str = attr.ib()
    schema: str = attr.ib()
    name: str = attr.ib()
    columns: List[str] = attr.ib()


class PiiTableSchema(AttrsSchema):
    class Meta:
        target = PiiTable
        register_as_scheme = True
