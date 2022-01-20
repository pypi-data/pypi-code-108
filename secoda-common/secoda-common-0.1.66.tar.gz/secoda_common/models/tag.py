import attr

from typing import List, Optional
from marshmallow_annotations.ext.attrs import AttrsSchema

@attr.s(auto_attribs=True, kw_only=True)
class Tag:
    key: str
    tag_name: str
    tag_type: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    last_updated_timestamp: Optional[int] = None
    tag_count: Optional[int] = None


class TagSchema(AttrsSchema):
    class Meta:
        target = Tag
        register_as_scheme = True