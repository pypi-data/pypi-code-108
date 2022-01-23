from datetime import datetime, timedelta
from typing import List, Union
from uuid import UUID

from datalogue.clients._http import _HttpClient, HttpMethod
from datalogue.models.organization import (
    Organization,
    _organization_from_payload,
    User,
    _users_from_payload,
    Group,
    _group_from_payload,
    Domain,
    _domain_from_payload,
    CreateUserRequest,
)
from datalogue.errors import DtlError
from datalogue.dtl_utils import _parse_list


class OrganizationClient:
    """
    Client to interact with the Organization objects
    """

    errorMsg = "you may not have permission to do the action or the organization was not found"

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client

    def create(self, name: str) -> Union[DtlError, Organization]:
        """
        Creates an organization

        :param name: Organization to be created
        :return: string with error message if failed, the organization otherwise
        """
        res = self.http_client.make_authed_request("/organization", HttpMethod.POST, {"name": name})

        if isinstance(res, DtlError):
            return res

        return _organization_from_payload(res)

    def delete(self, org_id: UUID) -> Union[DtlError, bool]:
        """
        Delete the organization with the provided id.
        This action can only be successfully done by the organization 
        owner.

        :param org_id: id of the organization to be retrieved
        :return: Error if it fails or True if it succeeds
        """

        res = self.http_client.make_authed_request(f"/organization/{str(org_id)}", HttpMethod.DELETE)

        if isinstance(res, DtlError):
            return res
        else:
            return True

    def get(self, org_id: UUID) -> Union[DtlError, Organization]:
        """
        From the provided id, get the corresponding Organization

        :param org_id: id of the organization to be retrieved
        :return: Error if it fails or Organization object otherwise
        """

        res = self.http_client.make_authed_request(f"/organization/{str(org_id)}/public", HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return _organization_from_payload(res)

    def add_users(
        self, org_id: UUID, users: List[CreateUserRequest], expiry_date: datetime
    ) -> Union[DtlError, List[str]]:
        """
        Add users to given organization and return reset password links for each user
        :param org_id: id of the organization
        :param users: list of CreateUserRequests
        :param expiry_date: expiration date of reset uri
        :return:
            List of set password link
            Error if expiration date was in past
            Error if there is email duplication or if at least one users with given email exists
        """
        body = {
            "users": [user.as_payload() for user in users],
            "expirationDate": expiry_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        res = self.http_client.make_authed_request(f"/organization/{str(org_id)}/users", HttpMethod.POST, body)
        return res

    def get_all_users(self, org_id: UUID, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[User]]:
        """
        From the provided organization id, get all users in the Organization

        :param org_id: id of the organization
        :param page: page to be retrieved
        :param item_per_page: number of users to be put in a page
        :return: Error if it fails or list of all users in the organization otherwise
        """

        res = self.http_client.make_authed_request(
            f"/organization/{str(org_id)}/users?page={page}&size={item_per_page}", HttpMethod.GET,
        )
        if isinstance(res, DtlError):
            return DtlError(
                f"Could not retreive all users of the organization: {res.message}", OrganizationClient.errorMsg,
            )

        return _parse_list(_users_from_payload)(res)

    def get_groups(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[Group]]:
        """
        Get all groups in the current organization in which the user is a member

        :param page: page to be retrieved
        :param item_per_page: number of groups to be put in a page
        :return: Error if it fails or list of all groups in the organization otherwise
        """

        res = self.http_client.make_authed_request(f"/groups?page={page}&size={item_per_page}", HttpMethod.GET)

        if isinstance(res, DtlError):
            return DtlError(f"Could not retreive your groups of your organization: {res.message}")

        return _parse_list(_group_from_payload)(res)

    def get_all_groups(self, org_id: UUID, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[Group]]:
        """
        From the provided organization id, get all groups in the Organization when admin, or user groups for non admin

        :param org_id: id of the organization
        :param page: page to be retrieved
        :param item_per_page: number of groups to be put in a page
        :return: Error if it fails or list of groups
        """

        res = self.http_client.make_authed_request(
            f"/organization/{str(org_id)}/groups?page={page}&size={item_per_page}", HttpMethod.GET,
        )

        if isinstance(res, DtlError):
            return DtlError(
                f"Could not retrieve all groups of the organization: {res.message}", OrganizationClient.errorMsg,
            )

        return _parse_list(_group_from_payload)(res)

    def add_domain(self, org_id: UUID, domain: str) -> Union[DtlError, bool]:
        """
        Add domain to provided organization

        :param org_id: id of the organization
        :return: Error if it fails or true if it's added
        """

        res = self.http_client.make_authed_request(
            f"/organization/{str(org_id)}/domain", HttpMethod.POST, {"domain": domain}
        )

        if isinstance(res, DtlError):
            return res
        else:
            return True

    def remove_domain(self, org_id: UUID, domain: str) -> Union[DtlError, bool]:
        """
        Remove domain from provided organization

        :param org_id: id of the organization
        :return: Error if it fails or true if it's deleted
        """

        res = self.http_client.make_authed_request(
            f"/organization/{str(org_id)}/domain", HttpMethod.DELETE, {"domain": domain}
        )

        if isinstance(res, DtlError):
            return res
        else:
            return True

    def get_all_domains(self, org_id: UUID, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[Domain]]:
        """
        Get all domains of the provided organization

        :param org_id: id of the organization
        :param page: page to be retrieved
        :param item_per_page: number of domains to be put in a page
        :return: Error if it fails or list of domains
        """

        res = self.http_client.make_authed_request(
            f"/organization/{str(org_id)}/domains?page={page}&size={item_per_page}", HttpMethod.GET,
        )

        if isinstance(res, DtlError):
            return DtlError(f"Could not retreive all domains: {res.message}", OrganizationClient.errorMsg,)

        return _parse_list(_domain_from_payload)(res)
