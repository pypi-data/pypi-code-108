import logging
import urllib.parse

from databricks_cli.configure import provider
from databricks_registry_webhooks.exceptions import RegistryWebhooksException
from databricks_registry_webhooks.protos.databricks_pb2 import INVALID_PARAMETER_VALUE

_logger = logging.getLogger(__name__)


class ModelRegistryHostCreds:
    """
    Provides a hostname and optional authentication for talking to an MLflow Model Registry server.

    :param host: Hostname (e.g., http://localhost:5000) of the MLflow Model Registry server.
    :param username: Username to use with Basic authentication when talking to server.
        If this is specified, password must also be specified.
    :param password: Password to use with Basic authentication when talking to server.
        If this is specified, username must also be specified.
    :param token: Token to use with Bearer authentication when talking to server.
        If provided, user/password authentication will be ignored.
    :param ignore_tls_verification: If true, we will not verify the server's hostname or TLS
        certificate. This is useful for certain testing situations, but should never be
        true in production.
        If this is set to true ``server_cert_path`` must not be set.
    :param client_cert_path: Path to ssl client cert file (.pem).
        Sets the cert param of the ``requests.request``
        function (see https://requests.readthedocs.io/en/master/api/).
    :param server_cert_path: Path to a CA bundle to use.
        Sets the verify param of the ``requests.request``
        function (see https://requests.readthedocs.io/en/master/api/).
        If this is set ``ignore_tls_verification`` must be false.
    """

    def __init__(
        self,
        host,
        username=None,
        password=None,
        token=None,
        ignore_tls_verification=False,
        client_cert_path=None,
        server_cert_path=None,
    ):
        if not host:
            raise RegistryWebhooksException(
                "host is a required parameter for ModelRegistryHostCreds",
                error_code=INVALID_PARAMETER_VALUE,
            )
        if ignore_tls_verification and (server_cert_path is not None):
            raise RegistryWebhooksException(
                "When 'ignore_tls_verification' is true then 'server_cert_path' "
                "must not be set!",
                error_code=INVALID_PARAMETER_VALUE,
            )
        self.host = host
        self.username = username
        self.password = password
        self.token = token
        self.ignore_tls_verification = ignore_tls_verification
        self.client_cert_path = client_cert_path
        self.server_cert_path = server_cert_path


def get_databricks_host_creds(server_uri=None):
    """
    Reads in configuration necessary to make HTTP requests to a Databricks server. This
    uses the Databricks CLI's ConfigProvider interface to load the DatabricksConfig object.
    If no Databricks CLI profile is found corresponding to the server URI, this function
    will attempt to retrieve these credentials from the Databricks Secret Manager. For that to work,
    the server URI will need to be of the following format: "databricks://scope:prefix". In the
    Databricks Secret Manager, we will query for a secret in the scope "<scope>" for secrets with
    keys of the form "<prefix>-host" and "<prefix>-token". Note that this prefix *cannot* be empty
    if trying to authenticate with this method. If found, those host credentials will be used. This
    method will throw an exception if sufficient auth cannot be found.

    :param server_uri: A URI that specifies the Databricks profile you want to use for making
                       requests.
    :return: A :py:class:`ModelRegistryHostCreds` instance that includes the hostname and
             authentication information necessary to talk to the Databricks server.
    """
    profile, path = _get_db_info_from_uri(server_uri)
    if not hasattr(provider, "get_config"):
        _logger.warning(
            "Support for databricks-cli<0.8.0 is deprecated and will be removed"
            " in a future version."
        )
        config = provider.get_config_for_profile(profile)
    elif profile:
        config = provider.ProfileConfigProvider(profile).get_config()
    else:
        config = provider.get_config()
    # if a path is specified, that implies a Databricks tracking URI of the form:
    # databricks://profile-name/path-specifier
    if (not config or not config.host) and path:
        dbutils = _get_dbutils()
        if dbutils:
            # Prefix differentiates users and is provided as path information in the URI
            key_prefix = path
            host = dbutils.secrets.get(scope=profile, key=key_prefix + "-host")
            token = dbutils.secrets.get(scope=profile, key=key_prefix + "-token")
            if host and token:
                config = provider.DatabricksConfig.from_token(
                    host=host, token=token, insecure=False
                )
    if not config or not config.host:
        _fail_malformed_databricks_auth(profile)

    insecure = hasattr(config, "insecure") and config.insecure

    if config.username is not None and config.password is not None:
        return ModelRegistryHostCreds(
            config.host,
            username=config.username,
            password=config.password,
            ignore_tls_verification=insecure,
        )
    elif config.token:
        return ModelRegistryHostCreds(config.host, token=config.token, ignore_tls_verification=insecure)
    _fail_malformed_databricks_auth(profile)


def _get_db_info_from_uri(uri):
    """
    Get the Databricks profile specified by the tracking URI (if any), otherwise
    returns None.
    """
    parsed_uri = urllib.parse.urlparse(uri)
    if parsed_uri.scheme == "databricks":
        # netloc should not be an empty string unless URI is formatted incorrectly.
        if parsed_uri.netloc == "":
            raise RegistryWebhooksException(
                "URI is formatted incorrectly: no netloc in URI '%s'." % uri
                + " This may be the case if there is only one slash in the URI.",
                error_code=INVALID_PARAMETER_VALUE,
            )
        profile_tokens = parsed_uri.netloc.split(":")
        parsed_scope = profile_tokens[0]
        if len(profile_tokens) == 1:
            parsed_key_prefix = None
        elif len(profile_tokens) == 2:
            parsed_key_prefix = profile_tokens[1]
        else:
            # parse the content before the first colon as the profile.
            parsed_key_prefix = ":".join(profile_tokens[1:])
        validate_db_scope_prefix_info(parsed_scope, parsed_key_prefix)
        return parsed_scope, parsed_key_prefix
    return None, None


# Both scope and key_prefix should not contain special chars for URIs, like '/'
# and ':'.
def validate_db_scope_prefix_info(scope, prefix):
    for c in ["/", ":", " "]:
        if c in scope:
            raise RegistryWebhooksException(
                "Unsupported Databricks profile name: %s." % scope
                + " Profile names cannot contain '%s'." % c,
                error_code=INVALID_PARAMETER_VALUE,
            )
        if prefix and c in prefix:
            raise RegistryWebhooksException(
                "Unsupported Databricks profile key prefix: %s." % prefix
                + " Key prefixes cannot contain '%s'." % c,
                error_code=INVALID_PARAMETER_VALUE,
            )
    if prefix is not None and prefix.strip() == "":
        raise RegistryWebhooksException(
            "Unsupported Databricks profile key prefix: '%s'." % prefix
            + " Key prefixes cannot be empty.",
            error_code=INVALID_PARAMETER_VALUE,
        )


def _get_dbutils():
    try:
        import IPython

        ip_shell = IPython.get_ipython()
        if ip_shell is None:
            raise _NoDbutilsError
        return ip_shell.ns_table["user_global"]["dbutils"]
    except ImportError:
        raise _NoDbutilsError
    except KeyError:
        raise _NoDbutilsError


class _NoDbutilsError(RegistryWebhooksException):
    pass


def _fail_malformed_databricks_auth(profile):
    raise RegistryWebhooksException(
        "Got malformed Databricks CLI profile '%s'. Please make sure the "
        "Databricks CLI is properly configured as described at "
        "https://github.com/databricks/databricks-cli." % profile,
        error_code=INVALID_PARAMETER_VALUE,
    )
