from typing import List

from tktl.commands import BaseDeploymentApiCommand
from tktl.core.clients.http_client import interpret_response
from tktl.core.config import settings
from tktl.core.schemas.repository import Repository


class GetRepositories(BaseDeploymentApiCommand):
    def execute(self) -> List[Repository]:
        response = self.client.get(f"{settings.API_V1_STR}/models")
        return interpret_response(response=response, model=Repository)
