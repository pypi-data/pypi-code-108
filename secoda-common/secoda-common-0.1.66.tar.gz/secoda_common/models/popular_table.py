
from typing import Optional

import attr
from marshmallow_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class PopularTable:
    """
    DEPRECATED. Use TableSummary
    """
    database: str = attr.ib()
    cluster: str = attr.ib()
    schema: str = attr.ib()
    name: str = attr.ib()
    description: Optional[str] = None
    last_updated_timestamp: Optional[int] = None


class PopularTableSchema(AttrsSchema):
    """
    DEPRECATED. Use TableSummary
    """
    class Meta:
        target = PopularTable
        register_as_scheme = True
