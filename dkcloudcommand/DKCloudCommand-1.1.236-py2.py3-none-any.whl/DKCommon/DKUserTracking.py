import os
from typing import Any, Dict
from enum import Enum

from mixpanel import Mixpanel, MixpanelException

from DKCloudCommand.version import DK_VERSION


# Normally we want to skip the User Tracking in non-prod-installs (and release candidates),
# So we check the version to see if it's a "prod install" or not
# This gives us an env variable to set as `DKCLI_FORCE_TRACKING` which allows us
# to enable user tracking in "non-prod installs" so we can test events when we want to.
# The default assumption (no env var at all) will make it skip tracking for non-prod installs
def skip_tracking():
    if os.getenv("DKCLI_FORCE_TRACKING", "false").lower() == "true":
        return False
    return "rc" in DK_VERSION or DK_VERSION == "1.0.0"


TRACKER = None if skip_tracking() else Mixpanel("971745954800ddbc7ca6ad5ff049c935")


class TrackingSource(Enum):
    API = 0
    CLI = 1


class UserTrackingException(Exception):
    def __init__(self, msg) -> None:
        super().__init__(msg)


def _as_string(src: TrackingSource) -> str:
    return {TrackingSource.API: "api", TrackingSource.CLI: "cli"}[src]


def log_event(
    source: TrackingSource, user_name: str, customer: str, event_name: str, event_data: Dict[str, Any]
) -> None:
    if TRACKER is None:
        return
    event_data["source"] = _as_string(source)
    try:
        TRACKER.track(f"{user_name}@{customer}", event_name, event_data)
    except MixpanelException as mxe:
        raise UserTrackingException(str(mxe))
    except OSError as e:
        print(f"FOUND EXCEPTION: {e.__class__.__name__}")
