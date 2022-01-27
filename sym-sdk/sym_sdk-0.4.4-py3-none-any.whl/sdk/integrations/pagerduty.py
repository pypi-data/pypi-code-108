"""Helpers for interacting with the PagerDuty API."""

from typing import List, Optional

from sym.sdk.errors import SymIntegrationErrorEnum
from sym.sdk.user import User


class PagerDutyError(SymIntegrationErrorEnum):
    """Raised when there is an error connecting to PagerDuty's API."""

    UNKNOWN_ERROR = ("An unexpected error occurred while trying to connect to PagerDuty.",)
    API_ERROR = ("An error occurred with the {endpoint} endpoint of the PagerDuty API: {err}",)
    API_TOKEN_ERROR = ("A PagerDuty API Token has not been set",)
    API_TOKEN_LOOKUP_ERROR = ("A PagerDuty API token could not be looked up",)


def is_on_call(
    user: User,
    *,
    escalation_policy_name: Optional[str] = None,
    escalation_policy_id: Optional[str] = None,
    schedule_name: Optional[str] = None,
    schedule_id: Optional[str] = None,
) -> bool:
    """Checks if the provided user is currently on-call according to PagerDuty.

    If a name or ID is provided for either escalation policy or schedule, checks if the user is
    on-call for specified escalation policy or schedule.

    If no name or ID is provided for either escalation policy or schedule, checks if the user is
    on-call for ANY escalation policy or schedule.

    Args:
        escalation_policy_name: The name of a specific Escalation Policy to check.
        escalation_policy_id: The ID of a specific Escalation Policy to check.
        schedule_name: The name of a specific Schedule to check.
        schedule_id: The ID of a specific Schedule to check.
    """


def users_on_call(
    *,
    escalation_policy_name: Optional[str] = None,
    escalation_policy_id: Optional[str] = None,
    schedule_name: Optional[str] = None,
    schedule_id: Optional[str] = None,
) -> List[User]:
    """Get all on-call users for the specified escalation policy or schedule from PagerDuty.

    Escalation policy or schedule can be specified by name or ID. If none are provided, returns
    on-call users for ALL escalation policies + schedules.

    Args:
        escalation_policy_name: The name of a specific Escalation Policy to check.
        escalation_policy_id: The ID of a specific Escalation Policy to check.
        schedule_name: The name of a specific Schedule to check.
        schedule_id: The ID of a specific Schedule to check.
    """
