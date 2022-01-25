"""
API client to talk to deployment-api
"""
import typing as t
import urllib.parse

from taktile_types.schemas.deployment.model import Model, ModelDeployment

from taktile_client.config import settings
from taktile_client.exceptions import HTTPException, TaktileClientException
from taktile_client.http_client import API


class DeploymentApiClient(API):
    """deployment-api client object"""

    def __init__(
        self, api_key: t.Optional[str], headers: t.Optional[t.Dict[str, str]]
    ):
        super().__init__(settings.DEPLOYMENT_API_URL, api_key, headers)

    def get_models(self) -> t.List[Model]:
        """Get all models for a user

        Returns
        -------
        t.List[Model]
            List of models
        """
        return t.cast(
            t.List[Model],
            self.call(verb="get", path="/api/v1/models", model=Model),
        )

    def get_model_deployment_by_repo_full_name_and_branch(
        self, principal: str, repository: str, branch: str
    ) -> ModelDeployment:
        """Get a specific model deployment

        Parameters
        ----------
        principal : str
            principal to look for
        repository : str
            repository to look for
        branch : str
            branch to look for. Can be either "main" or "refs/heads/main"

        Raises
        ------
        TaktileClientException
            raised if model deployment is not found

        Returns
        -------
        ModelDeployment
            the deployment requested
        """
        try:
            params = {
                "principal": principal,
                "repository": repository,
                "branch": branch,
            }
            url = (
                f"/api/v1/models/deployment/?{urllib.parse.urlencode(params)}"
            )
            model_deployment = t.cast(
                ModelDeployment,
                self.call(verb="get", path=url, model=ModelDeployment),
            )
            return model_deployment
        except HTTPException as err:
            raise TaktileClientException(
                f"Deployment {principal} - {repository} - {branch} not found"
            ) from err

    def get_host(self, principal: str, repository: str, branch: str) -> str:
        """Get the host of a deployment

        Parameters
        ----------
        principal : str
            principal to look for
        repository : str
            repository to look for
        branch : str
            branch to look for. Can be either "main" or "refs/heads/main"

        Raises
        ------
        TaktileClientException
            raised if model deployment is not found

        Returns
        -------
        str
            the host of the deployment
        """
        deployment = self.get_model_deployment_by_repo_full_name_and_branch(
            principal, repository, branch
        )

        if deployment.public_docs_url is None:
            raise TaktileClientException(
                f"Deployment {principal} - {repository} - {branch} "
                "is not ready to be called"
            )

        return deployment.public_docs_url
