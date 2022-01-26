from meili_sdk.models.user import AuthenticationUser
from meili_sdk.resources.base import BaseResource


class UserResource(BaseResource):
    def get_token_user(self):
        """
        Get the user that is connected to the given token
        """
        return self.get("api/auth/", expected_class=AuthenticationUser)
