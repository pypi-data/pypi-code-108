import functools
import logging
import sys
from warnings import warn
from collections import OrderedDict
from traceback import format_exception
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Iterable,
    Mapping,
    Union,
)
import boto3  # type: ignore
from botocore.exceptions import (  # type: ignore
    ClientError,
    NoCredentialsError,
)
from cerberus import CerberusClientException  # type: ignore
from cerberus.client import CerberusClient  # type: ignore
from .utilities import sys_argv_pop, iter_sys_argv_pop

__all__: List[str] = [
    "get_cerberus_secrets",
    "get_cerberus_secret",
    "apply_sys_argv_cerberus_arguments",
]
lru_cache: Callable[..., Any] = functools.lru_cache
# For backwards compatibility:
sys.modules["daves_dev_tools.utilities.cerberus"] = sys.modules[__name__]


@lru_cache()
def get_cerberus_secrets(
    cerberus_url: str,
    path: str,
) -> Dict[str, str]:
    """
    This function attempts to access Cerberus secrets at the given `path`
    with each AWS profile until successful, or until having run out of
    profiles, and returns the secrets if successful (or raises an error if
    not).

    Parameters:

    - **cerberus_url** (str): The Cerberus API endpoint
    - **path** (str): The Cerberus path containing the desired secret(s)
    """
    if (boto3 is None) or (CerberusClient is None):
        raise RuntimeError(
            "The `boto3` and `cerberus-python-client` packages must be "
            "installed in order to use this function."
        )
    secrets: Optional[Dict[str, str]] = None
    errors: Dict[str, str] = OrderedDict()
    for profile_name in boto3.Session().available_profiles + [None]:
        arn: str = ""
        try:
            session: boto3.Session = boto3.Session(profile_name=profile_name)
            arn = session.client("sts").get_caller_identity().get("Arn")
            secrets = CerberusClient(
                cerberus_url, aws_session=session
            ).get_secrets_data(path)
            break
        except (CerberusClientException, ClientError, NoCredentialsError):
            errors[arn or profile_name] = "".join(
                format_exception(*sys.exc_info())
            )
    if secrets is None:
        error_text: str = "\n".join(
            f'{key or "[default]"}:\n{value}\n'
            for key, value in errors.items()
        )
        warn(error_text)
        logging.warning(error_text)
        raise PermissionError(
            "No AWS profile was found with access to the requested secrets"
        )
    return secrets


def get_cerberus_secret(cerberus_url: str, path: str) -> Tuple[str, str]:
    """
    This is a convenience function for retrieving individual values from a
    Cerberus secret, and which return both the key (the last part of the
    path), as well as the retrieved secret value, as a `tuple`. This is
    useful under a common scenario where a username is a key in a secrets
    dictionary, and the client application needs both the username as password.

    Parameters:

    - **cerberus_url** (str): The Cerberus API endpoint
    - **path** (str): The Cerberus path containing the desired secret,
      *including* a dictionary key. For example: "path/to/secrets/key".
    """
    value: str
    parts: List[str] = path.strip("/").split("/")
    # Ensure the path includes the dictionary key
    assert len(parts) == 4
    key: str = parts.pop()
    # Retrieve the secrets dictionary
    secrets: Dict[str, str] = get_cerberus_secrets(
        cerberus_url, "/".join(parts)
    )
    # Return the key and the value stored at the secret's "key" index
    return key, secrets[key]


def apply_sys_argv_cerberus_arguments(
    url_parameter_name: Iterable[str],
    parameter_map: Union[
        Mapping[str, Iterable[str]],
        Iterable[Tuple[str, Iterable[str]]],
    ],
    argv: Optional[List[str]] = None,
) -> None:
    """
    This function modifies `sys.argv` by performing lookups against a specified
    Cerberus API and inserting the retrieved values into mapped keyword
    argument values.

    Parameters:

    - url_parameter_name (str): The base URL of the Cerberus API.
    - parameter_map ({str: [str]}): Maps final keyword argument names to
      keyword argument names wherein to find Cerberus paths to lookup
      values to pass to the final keyword arguments. Cerberus path keyword
      arguments are removed from `sys.argv` and final keyword arguments are
      inserted into `sys.argv`.
    - argv ([str]) = sys.argv: If provided, this list will be modified instead
      of `sys.argv`.
    """
    if argv is None:
        argv = sys.argv
    parameter_map_items: Iterable[Tuple[str, Iterable[str]]]
    if isinstance(parameter_map, Mapping):
        parameter_map_items = parameter_map.items()
    else:
        parameter_map_items = parameter_map
    cerberus_url: str = sys_argv_pop(  # type: ignore
        keys=url_parameter_name, flag=False
    )
    if cerberus_url:
        key: str
        cerberus_path_keys: Iterable[str]
        for key, cerberus_path_keys in parameter_map_items:
            value: str
            for value in iter_sys_argv_pop(  # type: ignore
                keys=cerberus_path_keys, argv=argv, flag=False
            ):
                argv += [key, get_cerberus_secret(cerberus_url, value)[-1]]
