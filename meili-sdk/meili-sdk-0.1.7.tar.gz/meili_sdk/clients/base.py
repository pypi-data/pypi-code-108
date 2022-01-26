from meili_sdk.resources.organizations import OrganizationResource
from meili_sdk.resources.teams import TeamResource
from meili_sdk.resources.users import UserResource
from meili_sdk.resources.forms import FormResource
from meili_sdk.site import get_host

__all__ = ("BaseAPIClient",)


class BaseAPIClient:
    """
    Base API client class
    """

    AUTHORIZATION_TOKEN_HEADER = None

    def __init__(self, token, override_host=None):
        self.token = token
        self.host = override_host or get_host()

    def get_authorization_header(self):
        return f"{self.get_authorization_token_header()} {self.token}"

    def get_authorization_token_header(self):
        if not self.AUTHORIZATION_TOKEN_HEADER:
            raise ValueError("AUTHORIZATION_TOKEN_HEADER is not set")
        return self.AUTHORIZATION_TOKEN_HEADER

    def get_authorization_headers(self):
        return {"Authorization": self.get_authorization_header()}

    def get_user_resources(self):
        return UserResource(self)

    def get_team_resources(self):
        return TeamResource(self)

    def get_organization_resources(self):
        return OrganizationResource(self)

    def get_form_resources(self):
        return FormResource(self)
