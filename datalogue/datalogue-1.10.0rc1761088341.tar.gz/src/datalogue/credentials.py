import os
from typing import Optional
from urllib.parse import urlparse

from datalogue.errors import DtlError


class DtlCredentials:
    """
    Information to be able to connect to the platform
    if verify_certificate is set, this variable will be used
    otherwise we look at the environment variable `DTL_SSL_VERIFY_CERT`
    if none is set then we use True as a default

    :param username: username to be used to login on the platform
    :param password: password to be used to login on the platform
    :param uri: root url where the system lives ie: https://test.datalogue.io/api
    :param verify_certificate: (Optional) verify the certificate when connecting to remote, no value means true.
    :param authentication_name: can be used to specify login via a configured alternate authentication method,
    e.g. LDAP. If None, will use the default email/password login
    """

    def __init__(
        self,
        username: str,
        password: str,
        uri: str,
        verify_certificate: Optional[bool] = None,
        authentication_name: Optional[str] = None,
    ):
        self.username = username.strip()
        self.password = password.strip()

        if verify_certificate is None:
            verify_certificate = _get_ssl_verify_env()

        self.verify_certificate = verify_certificate

        self.authentication_name = authentication_name
        uri = uri.strip()

        if self.validate_url(uri) is not True:
            raise DtlError("The URL you provided is invalid")

        if not uri.endswith("/api"):
            raise DtlError("The URL you provided doesn't end with '/api' it is most likely invalid")

        self.uri = uri

    def validate_url(self, uri: str) -> bool:
        parsed_url = urlparse(uri)
        return all([parsed_url.scheme, parsed_url.netloc])

    def __repr__(self):
        res = f"{self.__class__.__name__}(username: {self.username!r}, password: ****, uri: {self.uri!r})"
        if self.verify_certificate is None:
            return res
        else:
            return res[:-1] + f", verify_certificate: {self.verify_certificate!r})"


def _get_ssl_verify_env() -> bool:
    verify_certificate = os.environ.get("DTL_SSL_VERIFY_CERT")
    return verify_certificate is None or verify_certificate.lower() != "false"
