from typing import List, Union
from uuid import UUID

from datalogue.auth.authentication import (
    Authentications,
    _authentication_ref_from_payload,
)
from datalogue.clients._http import _HttpClient, HttpMethod
from datalogue.dtl_utils import _parse_list
from datalogue.errors import DtlError


class _AuthenticationClient:
    """
    Client to interact with the Authentication Schemes
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = ""

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[Authentications]]:
        """
        Lists all the Authentication schemes defined for the users Organization

        :param page: Optional page number, default 1
        :param item_per_page: Optional items per page, default 25
        :return: A list of all the authentication schemes defined for the users organization
        """
        res = self.http_client.make_authed_request(
            self.service_uri + f"/user-provider-configs/public?page={page}&size={item_per_page}", HttpMethod.GET,
        )

        if isinstance(res, DtlError):
            return res

        return _parse_list(_authentication_ref_from_payload)(res)

    # todo - this method should return AuthenticationReference object
    def update(self, authentication_id: UUID, authentication_def: Authentications) -> Union[DtlError, bool]:
        """
        Updates the given authentication definition

        :param authentication_id: UUID of the Authentication being updated
        :param authentication_def: Updated Authentication definition
        :return:
        """
        res = self.http_client.make_authed_request(
            self.service_uri + "/user-provider-configs/" + str(authentication_id),
            HttpMethod.PUT,
            authentication_def._as_payload(),
        )
        if isinstance(res, DtlError):
            return res
        return True

    def delete(self, authentication_id: UUID) -> Union[DtlError, bool]:
        """
        Delete an authentication definition

        :param authentication_id: UUID of the authentication to be deleted
        :return: DtlError if unsuccessful, or True is successful
        """
        res = self.http_client.make_authed_request(
            self.service_uri + "/user-provider-configs/" + str(authentication_id), HttpMethod.DELETE,
        )
        if isinstance(res, DtlError):
            return res
        return True
