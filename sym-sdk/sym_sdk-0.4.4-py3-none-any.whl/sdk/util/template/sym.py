"""Introspection tools and helpers for the Sym API."""

from typing import Dict, List, Optional, Tuple, Union

from sym.sdk.errors import SymIntegrationErrorEnum
from sym.sdk.resource import SRN
from sym.sdk.user import User

OrganizationHandle = Union[str, SRN]

Matcher = Dict[str, str]
"""A Matcher is a single-item dictionary representing a user's identity in an external service.

Within the Sym platform, a Matcher is treated as an opaque value, though it has meaning at the
interface between Sym and external services, such as this SDK. The value itself is a unique
service-specific identifier that allows us to "match" the user in Sym with their user in that
service, while the key is a hint as to what the value represents.

For example, the matcher value might be some kind of unique user identifier, in which case the key
could be something like "user_id" or "user_arn"; or it might be a username, in which case the key
might be "username". Each Sym integration will define its own key(s) for its matchers."""


class SymSystemError(SymIntegrationErrorEnum):
    """Raised when an error occurs in Sym's internals.

    Each exception includes an error code that you can use to reach out to support."""

    HANDLER_NOT_INITIALIZED = ("The Sym API Integration has not been initialized.",)
    USER_NOT_FOUND = ("The User '{user_id}' cannot be found.",)
    ENVIRONMENT_NAME_NOT_FOUND = ("The Environment '{environment_name}' cannot be found.",)
    FLOW_NOT_REGISTERED = (
        "The Flow '{flow_name}' cannot be found in the '{environment_name}' Environment.",
    )
    UNKNOWN_ERROR = ("An unknown error has occurred.",)


def get_flows(
    *,
    user: User,
    environment: Optional[str] = None,
    name: Optional[str] = None,
) -> Dict[str, dict]:
    """Fetches the set of :class:`~sym.sdk.user.Flow`s visible to a given :class:`~sym.sdk.user.User`.

    Args:
        user: The :class:`~sym.sdk.user.User` who is making the request.
        environment: Filters the returned :class:`~sym.sdk.user.Flow`s by a given environment. Supply "*" to return all environments.
        name: Filters by :class:`~sym.sdk.user.Flow` name.
    Returns:
        Dict[str, dict]: The matching `~sym.sdk.user.Flow`s, keyed by slug.
    """


def handles_to_users(
    *,
    service_type: str,
    external_id: str,
    matchers_and_emails: List[Tuple[Matcher, Optional[str]]],
) -> Dict[str, User]:
    """Fetches the set of :class:`~sym.sdk.user.User`s for a given Integration and set of external
    identities.

    Args:
        service_type: Type of the Service.
        external_id: The external ID of the service to resolve handles for (in case there are
            multiple of the same type).
        matchers_and_emails: A list of tuples containing information about the users to identify
            within the Sym platform. The first element, which is required, is a Matcher: A single-
            item dictionary representing a service-specific unique identity for the user. The second
            element is an optional email address for the user. If email address is provided, then it
            is used to create or update user identities automatically by searching for the user by
            email in Sym if no user matches the Matcher; otherwise, automatic user creation/updating
            will not happen.
    Returns:
        Dict[str, User]: A :class:`~sym.sdk.user.User` for each valid handle, keyed by handle.
    """
