from meili_sdk.models.base import BaseModel


class AuthenticationUser(BaseModel):
    uuid: str
    email: str
    username: str
    first_name: str
    last_name: str
    timezone: str
    token: str
