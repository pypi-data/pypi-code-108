import attr

from typing import List, Optional
from secoda_common.models.tag import Tag
from marshmallow_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class JobSummary:
    uri: str = attr.ib()
    product: str = attr.ib()
    name: str = attr.ib()
    url: Optional[str] = None
    description: Optional[str] = None
    last_successful_run_timestamp: Optional[int] = None


class JobSummarySchema(AttrsSchema):
    class Meta:
        target = JobSummary
        register_as_scheme = True
