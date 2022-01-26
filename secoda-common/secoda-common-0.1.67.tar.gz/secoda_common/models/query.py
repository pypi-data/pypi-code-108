from typing import Optional

import attr
from marshmallow_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class Query:
    key: str
    query_text: str
    frequency: Optional[int] = None
    description: Optional[str] = None
    last_updated_timestamp: Optional[int] = None


class QuerySchema(AttrsSchema):
    class Meta:
        target = Query
        register_as_scheme = True
