from six.moves import urllib

from databricks_registry_webhooks.exceptions import RegistryWebhooksException
from databricks_registry_webhooks.protos.databricks_pb2 import INVALID_PARAMETER_VALUE


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


def get_db_info_from_uri(uri):
    """
    Get the Databricks profile specified by the tracking URI (if any), otherwise
    returns None.
    """
    parsed_uri = urllib.parse.urlparse(uri)
    if parsed_uri.scheme == "databricks":
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
