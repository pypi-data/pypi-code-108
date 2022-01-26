from typing import Union, Optional, List
from uuid import UUID

from datalogue.clients._http import _HttpClient, HttpMethod
from datalogue.models.organization import (
    User,
    _user_from_payload,
    _users_from_payload,
    TokenCreateResult,
    PublicToken,
)
from datalogue.errors import DtlError
from datalogue.dtl_utils import _parse_list


class UserClient:
    """
    Client to interact with the User objects
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client

    def get_current_user(self) -> Union[DtlError, User]:
        """
        Get information for current user

        :return: Error if it fails or user otherwise
        """
        res = self.http_client.make_authed_request("/user", HttpMethod.GET)

        if isinstance(res, DtlError):
            return DtlError("Could not retrieve user.", res)

        return _user_from_payload(res)

    def generate_reset_password_url(self, user_id: UUID) -> Union[DtlError, str]:
        """
        Get url which can be used to create new user password

        :return: Error if it fails or url otherwise
        """
        res = self.http_client.make_authed_request(f"/password/{user_id}/request-change", HttpMethod.POST)

        if isinstance(res, DtlError):
            return DtlError("Could not retrieve reset url.", res)
        return res

    def get(self, user_id: UUID) -> Union[DtlError, User]:
        """
        Get public user information: first_name, last_name, email
        for a given user_id .

        :param user_id: UUID
        :return: Error if it fails or user otherwise
        """

        params = {"id": str(user_id)}

        res = self.http_client.make_authed_request(f"/user/public", HttpMethod.GET, params=params)

        if isinstance(res, DtlError):
            return DtlError("Could not retreive user.", res)

        return _users_from_payload(res)

    def search_by_email(self, text_in_email: str, page: int = 1, item_per_page: int = 25) -> Union[DtlError, User]:
        """
        Search for info of the user (within the organization) given a text in the user email. The search will look for
        that string in the email. (i.e.: will include the user `some_email@domain.com` if you search for the text `some`)

        :param text_in_email:
        :param page: page to be retrieved (default 1)
        :param item_per_page: number of items to be put in a page (default 25)
        :return: The users containing that text in the email field (will be empty if there is no users with that text
        in the email) or an Error as a string
        """

        res = self.http_client.make_authed_request(
            f"/organization/users/search?email={text_in_email}&page={page}&size={item_per_page}", HttpMethod.GET,
        )

        if isinstance(res, DtlError):
            return DtlError("Could not retreive users.", res)

        return _parse_list(_users_from_payload)(res)

    def create_token(self, user_id: Union[UUID, str], name: str) -> Union[DtlError, TokenCreateResult]:
        """
        Create a token for the specified user

        This token can be passed to the DtlToken() method, in turn passed to Dtl(), for sustained, encrypted login
        """

        res = self.http_client.make_authed_request(f"/users/{str(user_id)}/tokens", HttpMethod.POST, {"name": name})
        if isinstance(res, DtlError):
            return DtlError("Could not create token.", res)

        return TokenCreateResult._from_payload(res)

    def list_tokens(
        self, user_id: Union[UUID, str], page: int = 1, item_per_page: int = 25
    ) -> Union[DtlError, List[PublicToken]]:
        """
        List all tokens created by the specified user account
        :param page: page to be retrieved (optional)
        :param item_per_page: number of items to be put in a page (optional)
        """

        params = {
            "page": page,
            "size": item_per_page,
        }

        res = self.http_client.make_authed_request(f"/users/{str(user_id)}/tokens", HttpMethod.GET, params=params)

        if isinstance(res, DtlError):
            return DtlError("Could not get tokens.", res)
        return _parse_list(PublicToken._from_payload)(res)

    def delete_token(self, token_id: Union[UUID, str]) -> Union[DtlError, bool]:
        """
        Delete a specified token
        """
        current_user = self.get_current_user()
        if isinstance(current_user, DtlError):
            return current_user

        res = self.http_client.make_authed_request(
            f"/users/{str(current_user.id)}/tokens/{str(token_id)}", HttpMethod.DELETE
        )

        if isinstance(res, DtlError):
            return res

        return True
