import jwt
import os

import agilicus

from . import access

CONTEXT = None
API_DEFAULT = "https://api.agilicus.com"
CACERT_DEFAULT = os.getenv("SSL_CERT_FILE", None)
CLIENT_ID_DEFAULT = "agilicus-builtin-cli"
ISSUER_DEFAULT = "https://auth.agilicus.com"
HEADER_DEFAULT = True
ORG_ID_DEFAULT = ""


class ApiHelper:
    def __init__(self, ctx, token):
        self.configuration = get_api_config()
        self.configuration.host = get_value(ctx, "API")
        cacert = get_value(ctx, "CACERT")
        if cacert is not None:
            self.configuration.ssl_ca_cert = cacert

        if token:
            self.configuration.access_token = token
        else:
            self.configuration.access_token = get_token(ctx)
        self.org_api = agilicus.OrganisationsApi(agilicus.ApiClient(self.configuration))
        self.application_api = agilicus.ApplicationsApi(
            agilicus.ApiClient(self.configuration)
        )
        self.app_services_api = agilicus.ApplicationServicesApi(
            agilicus.ApiClient(self.configuration)
        )
        self.user_api = agilicus.UsersApi(agilicus.ApiClient(self.configuration))
        self.groups_api = agilicus.GroupsApi(agilicus.ApiClient(self.configuration))
        self.logs_api = agilicus.DiagnosticsApi(agilicus.ApiClient(self.configuration))
        self.metrics_api = agilicus.MetricsApi(agilicus.ApiClient(self.configuration))
        self.issuers_api = agilicus.IssuersApi(agilicus.ApiClient(self.configuration))
        self.tokens_api = agilicus.TokensApi(agilicus.ApiClient(self.configuration))
        self.audits_api = agilicus.AuditsApi(agilicus.ApiClient(self.configuration))
        self.resources_api = agilicus.ResourcesApi(
            agilicus.ApiClient(self.configuration)
        )
        self.certificates_api = agilicus.CertificatesApi(
            agilicus.ApiClient(self.configuration)
        )
        self.catalogues_api = agilicus.CataloguesApi(
            agilicus.ApiClient(self.configuration)
        )
        self.permissions_api = agilicus.PermissionsApi(
            agilicus.ApiClient(self.configuration)
        )
        self.challenges_api = agilicus.ChallengesApi(
            agilicus.ApiClient(self.configuration)
        )
        self.messages_api = agilicus.MessagesApi(agilicus.ApiClient(self.configuration))
        self.connectors_api = agilicus.ConnectorsApi(
            agilicus.ApiClient(self.configuration)
        )
        self.billing_api = agilicus.BillingApi(agilicus.ApiClient(self.configuration))
        self.launchers_api = agilicus.LaunchersApi(
            agilicus.ApiClient(self.configuration)
        )


def setup(ctx):
    ctx.ensure_object(dict)
    ctx.obj.setdefault("API", API_DEFAULT)
    ctx.obj.setdefault("CACERT", CACERT_DEFAULT)
    ctx.obj.setdefault("CLIENT_ID", CLIENT_ID_DEFAULT)
    ctx.obj.setdefault("ISSUER", ISSUER_DEFAULT)
    ctx.obj.setdefault("ISSUER", ISSUER_DEFAULT)
    ctx.obj.setdefault("ORG_ID", ORG_ID_DEFAULT)
    ctx.obj.setdefault("HEADER", HEADER_DEFAULT)
    ctx.obj.setdefault("BILLING_API_KEY", None)
    save(ctx)


def get_api_config():
    # Set discard_unknown_keys so that keys returned from server
    # (server could be a version greater than client).
    # Setting discard_unknown_keys also has side effect to allow
    # allOf schemas to not pass unknown keys to sub schemas that do
    # not accept unknown types.
    # See https://github.com/OpenAPITools/openapi-generator/issues/9684
    return agilicus.Configuration(discard_unknown_keys=True)


def get_value(ctx, value):
    if value in ctx.obj:
        return ctx.obj[value]
    if value in CONTEXT.obj:
        return CONTEXT.obj[value]


def get_token(ctx, refresh=None):
    token = get_value(ctx, "TOKEN")
    if not token or refresh:
        access_token = access.get_access_token(ctx, refresh=refresh)
        token = access_token.get()
    return token


def get_id_token(ctx, refresh=None):
    access_token = access.get_access_token(ctx, refresh=refresh)
    token = access_token.get_id_token()
    return token


def get_apiclient_from_ctx(ctx, refresh=None):
    return get_apiclient(ctx, get_token(ctx, refresh))


def header(ctx):
    return get_value(ctx, "HEADER")


def save(ctx):
    global CONTEXT
    CONTEXT = ctx


def get_apiclient(ctx, user_token=None):
    api = ApiHelper(ctx, user_token)
    return api


def get_api(ctx):
    return get_value(ctx, "API")


def get_model_config(ctx):
    return get_value(ctx, "CONFIG")


def get_cacert(ctx):
    return get_value(ctx, "CACERT")


def get_client_id(ctx):
    return get_value(ctx, "CLIENT_ID")


def get_auth_local_webserver(ctx):
    return get_value(ctx, "AUTH_LOCAL_WEBSERVER")


def get_client_secret(ctx):
    return get_value(ctx, "CLIENT_SECRET")


def get_issuer(ctx):
    return get_value(ctx, "ISSUER")


def get_org(ctx):
    return get_value(ctx, "ORGANISATION")


def get_scopes(ctx):
    return get_value(ctx, "SCOPES")


def get_value_from_token(ctx, key, user_token=None):
    # Next check to see if a token was passed in via
    # context/env
    if get_value(ctx, "TOKEN"):
        token = jwt.decode(
            get_value(ctx, "TOKEN"),
            algorithms=["ES256"],
            options={"verify_signature": False},
        )
        if key in token:
            return token[key]

    # finally check to see if the users token
    # has an org
    if user_token:
        token = jwt.decode(
            user_token, algorithms=["ES256"], options={"verify_signature": False}
        )
        if key in token:
            return token[key]

    return None


def get_org_id(ctx, user_token=None):
    # first check to see if an org is chosen
    # via context/env
    if get_value(ctx, "ORG_ID") and get_value(ctx, "ORG_ID"):
        return get_value(ctx, "ORG_ID")

    return get_value_from_token(ctx, "org", user_token=user_token)


def get_user_id(ctx, user_token=None):
    return get_value_from_token(ctx, "sub", user_token=user_token)


def output_json(ctx):
    return get_value(ctx, "output_format") == "json"


def output_console(ctx):
    return get_value(ctx, "output_format") == "console"


def get_stripe_key(ctx):
    return get_value(ctx, "BILLING_API_KEY")
