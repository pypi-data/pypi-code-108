from typing import Optional

from vectice.api._auth import Auth


class ProjectApi(Auth):
    def __init__(
        self, project_token: str, _token: Optional[str] = None, auto_connect=True, allow_self_certificate=True
    ):
        super().__init__(_token=_token, auto_connect=auto_connect, allow_self_certificate=allow_self_certificate)
        self._project_token = project_token
        self._project_path = "/metadata/project/" + str(project_token)

    @property
    def project_token(self) -> str:
        return self._project_token

    @property
    def api_base_path(self) -> str:
        return self._project_path
