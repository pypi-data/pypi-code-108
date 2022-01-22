# social
from typing import Optional

from pydantic import BaseModel


class SocialModel(BaseModel):
    project_client_id: str
    project_api_host: str
    client_id: str
    client_secret: str


class SocialUserResponse(BaseModel):
    id: str
    username: Optional[str]
    pw_login: bool
    provider: str
    token: Optional[str]
    refresh: Optional[str]
