#
# The unexpected error function required a new service because its use of
# auth_service resulted in circular imports when it was added to message_service
#

from django.conf import settings
from psu_base.classes.Log import Log
from psu_base.services import utility_service
from inspect import getframeinfo, stack
from psu_base.models.error import Error
from psu_base.services import auth_service, message_service
from sentry_sdk import capture_exception
import os
import sys
import traceback

log = Log()


def record(ee, debug_info=None):
    """Shortcut for when you want a detailed log of the error without posting an error message"""

    # During local development, post the error so it doesn't get overlooked
    local_development = getattr(settings, "ENVIRONMENT").upper() == "DEV"
    if local_development:
        icon = '<span class="fa fa-bug"></span>'
        unexpected_error(f"{icon} Bug recorded: {ee}", ee, debug_info)

    else:
        unexpected_error(None, ee, debug_info)


def unexpected_error(error_display=None, error_system=None, debug_info=None):
    """
    Logs the error in the db, the log file, and posts an error on-screen
    This service cannot use auth_service (circular import), so user must be provided if you want it logged
    """

    # Gather data
    src = get_caller_data()
    request = utility_service.get_request()
    path = request.path if request else "?"
    method = request.method if request else None
    auth = auth_service.get_auth_object()

    try:
        browser = request.META["HTTP_USER_AGENT"]
    except:
        browser = "Unknown"

    # Don't record health-check errors
    # Finti downtimes clutter the error page
    if browser and "ELB-HealthChecker" in browser:
        if error_display:
            log.error(f"ELB-HealthCheck: {error_display}", trace_error=False)
        if error_system:
            log.error(f"ELB-HealthCheck: {error_system}", trace_error=False)
        return

    # Include parameters in error log
    parameters = utility_service.get_parameters()
    if not parameters:
        parameters = None  # To avoid "{}"

    # Prevent logging of certain parameters
    else:
        # CSRF token is long and unhelpful. Remove it when present.
        if "csrfmiddlewaretoken" in parameters:
            del parameters["csrfmiddlewaretoken"]
        # Mask out anything that we would never want auto-logged
        for kk in ["ssn", "password"]:
            if parameters.get(kk):
                parameters[kk] = '*' * len(str(parameters.get(kk)))

    # Gather user authentication data
    user_log_msg = f"User          : {auth.sso_user}"
    if auth.is_impersonating():
        user_log_msg += f"\n\tImpersonating : {auth.impersonated_user}"
    if auth.is_proxying():
        user_log_msg += f"\n\tProxying      : {auth.proxied_user}"

    # Get stacktrace
    stacktrace = traceback.format_exc(limit=10)

    # Log error in log file
    log.error(
        f"""\n
\t*** UNEXPECTED ERROR ***
\tSystem Error:   {error_system}
\tFriendly Error: {error_display}
\tDebug Info: {debug_info}
\tBrowser: {browser}
\t{user_log_msg}
\tRequest Path:   {f"[{method}] " if method else ''}{path}
\tParameters:     {parameters}
\tRaised From:    {src}

{stacktrace}
        """,
        trace_error=False,
    )

    # Log error in database
    try:
        ee = Error()
        ee.app_code = utility_service.get_app_code()
        ee.path = str(path)[:128] if path else path
        ee.parameters = str(parameters)[:500] if parameters else parameters
        ee.code_detail = str(src)[:128] if src else src
        ee.sso_user = auth.sso_user.username if auth.sso_user else None
        ee.browser = browser[:200] if browser else browser
        ee.impersonated_user = (
            auth.impersonated_user.username if auth.impersonated_user else None
        )
        ee.proxied_user = auth.proxied_user.username if auth.proxied_user else None
        ee.error_friendly = str(error_display)[:128] if error_display else error_display
        ee.error_system = str(error_system)[:128] if error_system else error_system
        ee.debug_info = str(debug_info)[:128] if debug_info else debug_info
        ee.stacktrace = stacktrace
        ee.save()
    except Exception as ee:
        log.warning(f"Unexpected error was not saved in database: {str(ee)}")

    # Post friendly error to the screen
    if error_display:
        message_service.post_error(error_display)

    # Log to Sentry if an actual system error was given
    # (sometimes a description of an error will be provided rather than an actual error)
    if utility_service.get_setting("USE_SENTRY") and not type(error_system) is str:
        capture_exception(error_system)


def get_caller_data():
    """Return the calling code as (file-name, line-number, function-name)"""
    try:
        # Ignore this function, and the error_service.<function> that called it
        depth = 2

        # Get the info about the function that generated the message
        caller = getframeinfo(stack()[depth][0])

        # In case of nested functions within this class, may need to look deeper
        try:
            cf = caller.filename
            while cf.endswith("message_service.py") or cf.endswith("error_service.py"):
                depth += 1
                caller = getframeinfo(stack()[depth][0])
                cf = caller.filename
        except Exception as ee:
            log.warning(
                f"Unable to navigate nested functions in error_service.get_caller_data(): {ee}"
            )

        return f"{os.path.basename(caller.filename)}.{caller.function}() at line {caller.lineno}"

    except Exception as ee:
        log.warning("Unable to get file/function/line at which the error occurred.")
        return "Unknown"
