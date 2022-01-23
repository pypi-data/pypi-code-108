from typing import Union
from datalogue.auth.authentication import (
    Authentications,
    _authentication_ref_from_payload,
    AuthenticationsReference,
)
from datalogue.clients._http import _HttpClient, HttpMethod
from datalogue.errors import DtlError


class _TestAuthenticationClient:
    """
    Client to interact with the Authentication Schemes
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client

    def create(self, authentication_def: Authentications) -> Union[DtlError, AuthenticationsReference]:
        """
        For creating an LDAP object for test cases
        """
        res = self.http_client.make_authed_request(
            "/user-provider-configs?only-validate=false", HttpMethod.POST, authentication_def._as_payload(),
        )
        if isinstance(res, DtlError):
            return res
        return _authentication_ref_from_payload(res)
