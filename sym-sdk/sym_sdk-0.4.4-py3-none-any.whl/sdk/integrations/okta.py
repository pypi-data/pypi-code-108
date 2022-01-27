"""Helpers for interacting with the Okta API within the Sym SDK."""


from sym.sdk.errors import SymIntegrationErrorEnum
from sym.sdk.user import User


class OktaError(SymIntegrationErrorEnum):
    """Raised when an error occurs while interacting with the Okta API"""

    MISSING_ARG = (
        "Required argument {arg} for method {method} not provided.",
        "Please check your implementation file to ensure that all required arguments are passed.",
    )
    API_ERROR = (
        "An error occurred while interacting with the Okta API in the {method} method: {err}",
        "Please check your implementation file for errors, or contact Sym support.",
    )
    IDENTITY_NOT_FOUND = (
        "An Okta identity was not found for the user {email}.",
        "Please add an identity for the user using the symflow CLI.",
    )
    UNKNOWN_ERROR = "An unknown error occurred while interacting with the Okta API: {err}"


def is_user_in_group(user: User, *, group_id: str) -> bool:
    """Checks if the provided user is a member of the Okta group specified.

    The Okta group's ID must be given, and the method will check that the group exists and is
    accessible. An exception will be thrown if not.

    Args:
        user: The user to check group membership of.
        group_id: The ID of the Okta group.

    Returns:
        True if the user is a member of the specified Okta group, False otherwise.
    """
