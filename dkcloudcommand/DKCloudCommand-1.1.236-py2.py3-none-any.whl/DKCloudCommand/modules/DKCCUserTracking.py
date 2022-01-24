from typing import Any, Dict

import DKCommon.DKUserTracking as DKTracking


class UserTracking:
    """
    Simple wrapper around the UserTracking in DKCommon specific to CLI usage
    """

    @staticmethod
    def log_event(user_name: str, customer: str, event_name: str, event_data: Dict[str, Any]) -> None:
        # Release candidates and local testing installs won't create events
        DKTracking.log_event(DKTracking.TrackingSource.CLI, user_name, customer, event_name, event_data)
