from typing import List, Optional

import attr
from marshmallow_annotations.ext.attrs import AttrsSchema
from secoda_common.models.tag import Tag


@attr.s(auto_attribs=True, kw_only=True)
class Badge:
    badge_name: str = attr.ib()
    category: str = attr.ib()


class BadgeSchema(AttrsSchema):
    class Meta:
        target = Badge
        register_as_scheme = True


@attr.s(auto_attribs=True, kw_only=True)
class DashboardSummary:
    uri: str = attr.ib()
    cluster: str = attr.ib()
    group_name: str = attr.ib()
    group_url: str = attr.ib()
    product: str = attr.ib()
    name: str = attr.ib()
    url: str = attr.ib()
    description: Optional[str] = None
    last_successful_run_timestamp: Optional[int] = None
    chart_names: Optional[List[str]] = []
    badges: Optional[List[Badge]] = []
    tags: Optional[List[Tag]] = []


class DashboardSummarySchema(AttrsSchema):
    class Meta:
        target = DashboardSummary
        register_as_scheme = True
