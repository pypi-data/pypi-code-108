import base64

from datalogue.clients._http import _HttpClient, Union, Optional, HttpMethod
from datalogue.clients.jobs import JobsClient
from datalogue.clients._datastore_collections import _DatastoreCollectionClient
from datalogue.clients.data_product import DataProductClient
from datalogue.clients.credentials import CredentialsClient
from datalogue.clients.datastore import DatastoreClient
from datalogue.clients._organization import OrganizationClient
from datalogue.clients._group import GroupClient
from datalogue.clients._tag import _TagClient
from datalogue.clients._user import UserClient
from datalogue.clients.ontology import OntologyClient
from datalogue.clients._classifier import _ClassifierClient
from datalogue.clients._regex import _RegexClient
from datalogue.clients.pipeline import PipelineClient
from datalogue.credentials import DtlCredentials, _get_ssl_verify_env
from datalogue.clients._authentication import _AuthenticationClient
from datalogue.errors import DtlError
from datalogue.version import __version__ as dtl_version

from uuid import UUID

from datalogue.models.organization import User


class LoginCredentials:
    def __init__(self, uri: str):
        self.uri = uri


class DtlTokenCredentials(LoginCredentials):
    def __init__(
        self, uri: str, user_id: Union[str, UUID], token: str, verify_certificate: bool = True,
    ):
        LoginCredentials.__init__(self, uri)
        self.user_id = user_id
        self.token = token
        self.verify_certificate = verify_certificate


class Dtl:
    """
    Root class to be built to interact with all the services

    :param credentials: contains the information to connect
    """

    def __init__(self, credentials: LoginCredentials):
        self.uri = credentials.uri

        if isinstance(credentials, DtlCredentials):
            self.username = credentials.username
            self.http_client = _HttpClient(
                credentials.uri, credentials.authentication_name, credentials.verify_certificate,
            )

            login_res = self.http_client.login(credentials.username, credentials.password)
            if isinstance(login_res, DtlError):
                raise login_res

        if isinstance(credentials, DtlTokenCredentials):
            user_id_with_token = f"{credentials.user_id}:{credentials.token}"
            encoded_bytes = base64.b64encode(user_id_with_token.encode("utf-8"))
            encoded_token = str(encoded_bytes, "utf-8")

            self.http_client = _HttpClient(
                credentials.uri,
                verify_certificate=credentials.verify_certificate,
                encoded_auth_header=f"TOKEN {encoded_token}",
            )
            current_user = UserClient(self.http_client).get_current_user()
            self.username = current_user.email

        self.group = GroupClient(self.http_client)
        """Client to interact with the groups"""
        self.user = UserClient(self.http_client)
        """Client to interact with the users"""
        self.organization = OrganizationClient(self.http_client)
        """Client to interact with the organization part of the stack"""
        self.jobs = JobsClient(self.http_client)
        """Client to interact with the jobs"""
        self.datastore_collection = _DatastoreCollectionClient(self.http_client)
        """Client to interact with the datastore collections"""
        self.datastore = DatastoreClient(self.http_client)
        """Client to interact with the datastores"""
        self.credentials = CredentialsClient(self.http_client)
        """Client to interact with credentials"""
        self.ontology = OntologyClient(self.http_client)
        """Client to interact with ontologies"""
        self.classifier = _ClassifierClient(self.http_client, self.ontology)
        """Client to interact with classifiers"""
        self.regex = _RegexClient(self.http_client)
        """Client to interact with regexes"""
        self.tag = _TagClient(self.http_client)
        """Client to interact with tags"""
        self.pipeline = PipelineClient(self.http_client)
        """Client to interact with the stream collections"""
        self.authentication = _AuthenticationClient(self.http_client)
        """Client to interact with the Authentication Schemes"""
        self.data_product = DataProductClient(self.http_client)
        """Client to interact with the data products"""

    def __repr__(self):
        return f"Logged in {self.uri!r} with {self.username!r} account."

    @staticmethod
    def signup(
        uri="",
        first_name="",
        last_name="",
        email="",
        password="",
        accept_terms=True,
        verify_certificate: Optional[bool] = None,
    ) -> Union[DtlError, User]:
        """
        Perform signup of user
        :param uri: The target URI where the user data will be associated in
        :param accept_terms: Whether the user accept the following terms : https://www.datalogue.io/pages/terms-of-service
        :return: User object if successful, else return DtlError
        """

        if verify_certificate is None:
            verify_certificate = _get_ssl_verify_env()

        http_client = _HttpClient(uri, verify_certificate=verify_certificate)
        http_client.get_csrf()
        registered_user = http_client.signup(first_name, last_name, email, password, accept_terms)
        return registered_user

    def version(self) -> str:
        """
        Get version information of SDK
        :return: Build number of the SDK
        """
        return dtl_version
