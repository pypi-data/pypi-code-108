from enum import Enum
from typing import List, Optional

from cognite.airworkflow.util import env
from cognite.airworkflow.util.projecthelpers import project_name_finder


class Project(Enum):
    NAME = project_name_finder()

    @classmethod
    def _missing_(cls, value):
        raise ValueError(f"{value} is not a valid AIR project, must be one of {[p.value for p in Project]}")


class ProjectInfo:
    def __init__(
        self,
        project: str,
        client_key_name: Optional[str] = None,
        base_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        secret_name: Optional[str] = None,
        token_url: Optional[str] = None,
        scopes: Optional[List[str]] = None,
    ):
        self.name: str = project
        self.project: str = project
        self._base_url: Optional[str] = base_url
        # legacy
        self.client_key_name: Optional[str] = client_key_name
        # oidc
        self.tenant_id: Optional[str] = tenant_id
        self.client_id: Optional[str] = client_id
        self.secret_name: Optional[str] = secret_name
        self.token_url: Optional[str] = token_url
        self.scopes: Optional[List[str]] = scopes
        # validate
        self.validate_auth()

    @property
    def oidc(self):
        return all(
            [i is not None for i in [self.tenant_id, self.client_id, self.secret_name, self.token_url, self.scopes]]
        ) and isinstance(self.scopes, list)

    def validate_auth(self):
        if not self.client_key_name and not self.oidc:
            raise ValueError("Either legacy or OIDC authentication needs to be specified.")

    @property
    def base_url(self):
        return self._base_url or "https://api.cognitedata.com"

    def get_client_api_key(self) -> str:
        return env.get_env_value(self.client_key_name)

    def get_client_secret(self) -> str:
        return env.get_env_value(self.secret_name)
