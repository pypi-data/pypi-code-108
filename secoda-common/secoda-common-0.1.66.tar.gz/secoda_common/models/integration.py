from typing import Optional

import attr
from marshmallow_annotations.ext.attrs import AttrsSchema

@attr.s(auto_attribs=True, kw_only=True)
class Integration:
  name: Optional[str] = None
  short_name: Optional[str] = None
  picture: Optional[str] = None
  owner_id: Optional[str] = None
  owner_name: Optional[str] = None
  region: Optional[str] = None
  connection_url: Optional[str] = None
  host: Optional[str] = None
  account: Optional[str] = None
  database: Optional[str] = None
  warehouse: Optional[str] = None
  project: Optional[str] = None
  port: Optional[int] = None
  credentials: Optional[str] = None
  access_key_name: Optional[str] = None
  access_key: Optional[str] = None
  secret: Optional[str] = None
  user: Optional[str] = None
  password: Optional[str] = None
  deleted: Optional[bool] = False

class IntegrationSchema(AttrsSchema):
  class Meta:
    target = Integration
    register_as_scheme = True