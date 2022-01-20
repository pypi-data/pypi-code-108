from typing import Optional, List, Dict
from secoda_common.models.user import User
from secoda_common.models.table import TableSummary
from secoda_common.models.dashboard import DashboardSummary
from secoda_common.models.tag import Tag

import attr
from marshmallow_annotations.ext.attrs import AttrsSchema

@attr.s(auto_attribs=True, kw_only=True)
class DictionaryTerm:
  key: str
  name: Optional[str]
  definition: Optional[str] = None
  sql: Optional[str] = None
  owner: Optional[User] = None
  created_at: Optional[int] = None
  updated_at: Optional[int] = None
  tags: Optional[List[Tag]] = None
  related_tables: Optional[List[TableSummary]] = None
  related_dashboards: Optional[List[DashboardSummary]] = None


class DictionaryTermSchema(AttrsSchema):
  class Meta:
    target = DictionaryTerm
    register_as_scheme = True