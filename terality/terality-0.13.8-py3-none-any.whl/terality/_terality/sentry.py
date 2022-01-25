"""Utilities to report client errors to Sentry (sentry.io).

See the Sentry docs for details.
"""
import os
from typing import Optional

import sentry_sdk
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
import numpy as np
import pandas as pd

from .constants import ENV_PROD, TERALITY_DISABLE_TELEMETRY_ENV_VAR


def _drop_non_prod_events(event, hint):  # pylint: disable=unused-argument
    # Allows for explicitly disabling Sentry.
    if os.environ.get(TERALITY_DISABLE_TELEMETRY_ENV_VAR, "0") == "1":
        return None
    # Only send events in production. Don't clutter Sentry with other events.
    if event["environment"] != ENV_PROD:
        return None

    # Never report KeyboardInterrupt.
    if "exc_info" in hint:
        _exc_type, exc_value, _traceback = hint["exc_info"]
        if isinstance(exc_value, KeyboardInterrupt):
            return None

    # Only report exceptions that have somehow a source in the Terality module.
    # (we are not interested in exceptions from the user code outside Terality, but Sentry applies
    # to the whole Python session, e.g the whole Jupyter Lab).
    # We can't inspect the top-level "module" key in the Sentry event, because this module may not
    # be "terality", but one called by terality (e.g "socket" for network issues).
    # Instead, inspect the stack trace, and check that at some point the Terality module appears.
    try:
        values = event["exception"]["values"]
        for value in values:
            frames = value["stacktrace"]["frames"]
            for frame in frames:
                if frame["module"].split(".")[0] == "terality":
                    return event
    except KeyError:
        # Drop events with an unexpected schema - they probably don't interest us.
        return None
    return None


def set_up_sentry(environment: str, release: Optional[str], user_id: Optional[str] = None) -> None:
    """Configure the Sentry integration (for client-side error reporting).

    If the user ID is not known when calling this method, it can be set later with `set_user_for_sentry`.
    """
    if release is None:
        release = "unknown"
    # This Sentry DSN is not security sensitive.
    sentry_sdk.init(
        "https://478ff7ea710140e895b0c8734b9fb802@o923608.ingest.sentry.io/5871105",
        traces_sample_rate=1.0,
        release=release,
        environment=environment,
        before_send=_drop_non_prod_events,
        # By default, Sentry would not send events coming from a REPL.
        # However, a Jupyter notebook is a REPL, and we do want events from the Jupyter notebook.
        # The _drop_non_prod_events function should take care of removing simple typos and other
        # uninteresting events from Sentry events.
        integrations=[ExcepthookIntegration(always_run=True)],
    )
    if user_id is not None:
        set_user_for_sentry(user_id)
    set_sentry_tags()


def set_user_for_sentry(user_id: str):
    """Associate the current Terality user ID to Sentry events."""
    sentry_sdk.set_user({"id": user_id, "username": user_id})


def set_sentry_tags():
    # Sentry does send these versions as part of the event context, but settings them as tags
    # allows for searching issues by these versions (Sentry context is not searchable).
    sentry_sdk.set_tag("versions.numpy", np.__version__)
    sentry_sdk.set_tag("versions.pandas", pd.__version__)
