# flake8: noqa
import json
import os
import sys
import dataclasses
from . import context
from . import scopes
from . import credentials
from . import tokens
import jwt

from .version import __version__  # noqa

sys.path.append(os.path.dirname(__file__))  # noqa

from .agilicus_api import *  # noqa
from .agilicus_api import exceptions  # noqa
from . import patches  # noqa


ApiClient = patches.patched_api_client()


def GetClient(
    issuer=context.ISSUER_DEFAULT,
    cacert=None,
    client_id="agilicus-builtin-cli",
    authentication_document=None,
    agilicus_scopes=scopes.DEFAULT_SCOPES,
    auth_local_webserver=True,
):

    config = Configuration()
    if authentication_document:
        creds = {}
        with open(authentication_document) as fd:
            ad = json.load(fd)
        token = tokens.create_service_token(
            auth_doc=ad, scope=agilicus_scopes, client_id=client_id
        )
        config.access_token = token.get("access_token")
    else:
        creds = credentials.get_credentials(
            issuer=issuer,
            cacert=cacert,
            client_id=client_id,
            agilicus_scopes=agilicus_scopes,
            auth_local_webserver=auth_local_webserver,
        )
        config.access_token = creds.access_token

    _default_org_id = None
    access_token = jwt.decode(
        config.access_token, algorithms=["ES256"], options={"verify_signature": False}
    )
    if "org" in access_token:
        _default_org_id = access_token["org"]

    @dataclasses.dataclass
    class api:
        default_org_id = _default_org_id
        users = UsersApi(ApiClient(config))
        organisations = OrganisationsApi(ApiClient(config))
        policies = PolicyApi(ApiClient(config))
        certificates = CertificatesApi(ApiClient(config))
        applications = ApplicationsApi(ApiClient(config))
        groups = GroupsApi(ApiClient(config))
        connectors = ConnectorsApi(ApiClient(config))
        resouces = ResourcesApi(ApiClient(config))
        catalogues = CataloguesApi(ApiClient(config))
        permissions = PermissionsApi(ApiClient(config))
        audits = AuditsApi(ApiClient(config))
        files = FilesApi(ApiClient(config))
        tokens = TokensApi(ApiClient(config))
        diagnostics = DiagnosticsApi(ApiClient(config))
        metrics = MetricsApi(ApiClient(config))
        challenges = ChallengesApi(ApiClient(config))
        application_services = ApplicationServicesApi(ApiClient(config))
        services = ServicesApi(ApiClient(config))
        issuers = IssuersApi(ApiClient(config))
        messages = MessagesApi(ApiClient(config))

    return api
