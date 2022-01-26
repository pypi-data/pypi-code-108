from pydantic import BaseModel

from ..client.base import BaseClient


class ApiBaseClass(BaseModel):
    client: BaseClient
    skip_response_parsing: bool = False
