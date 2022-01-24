import json
import logging
import os

from DKCommon.typing import JSONData
from requests import Response

LOG = logging.getLogger(__name__)


def validate_and_get_response(response):
    base_error_message = "Call to backend failed."
    reason_message = "Unknown reason."

    if response is None:
        raise Exception("%s\n%s\n" % (base_error_message, "Response was null."))

    rdict = get_json_response(response)
    if rdict is None:
        raise Exception("%s\n" % "Response was an invalid format")

    if response.status_code == 200 or response.status_code == 201:
        if "error" in rdict:
            reason_message = (
                "The status_code indicates success, " "but there is an error in response. Error is: %s" % rdict["error"]
            )
            raise Exception("%s\n" % reason_message)
        return rdict

    elif response.status_code == 400:
        default_message = "Call to backend failed (Code 400)"
        reason_message = get_error_messages(rdict, default_message=default_message)
        if "message" in rdict:
            reason_message += get_issue_messages(rdict["message"])
        raise Exception("%s\n" % reason_message)

    elif response.status_code == 403:
        reason_message = "Permission Denied"
        if response.text is not None:
            message = response.json().get("message")
            if message is not None:
                reason_message = message.get("error")
                raise Exception("%s\n" % reason_message)
    elif response.status_code == 412 or response.status_code == 417:
        default_message = "Call to backend failed (Code %s)" % str(response.status_code)
        reason_message = get_error_messages(rdict, default_message=default_message)

    elif response.status_code == 502:
        reason_message = "Server could not make a dependent connection (Code 502)."

    elif response.status_code == 504:
        reason_message = "Server timeout (Code 504)."

    else:
        reason_message = "%s (Code %s)" % (str(response.text), response.status_code)

    raise Exception("%s\n%s\n" % (base_error_message, reason_message))


def get_json_response(response: Response) -> JSONData:
    if response is None or response.text is None:
        return None
    try:
        return response.json()
    except ValueError as e:
        LOG.warning("Failed to parse response to JSON", exc_info=True)
        # TODO: Store this response in a better place (S3 maybe)
        LOG.warning("Received response: %s (first 100 characters)", response.text[:100])
        raise json.JSONDecodeError(f"Failed to  parse response to JSON, error: {str(e)}")


def get_issue_messages(param):
    issue_messages = ""
    issues = list()

    if isinstance(param, dict) and "issues" in param:
        issues = param["issues"]

    if isinstance(param, list):
        issues = param

    for issue in issues:
        issue_messages += "\n"
        if "severity" in issue:
            issue_messages += "Severity: %s\n" % issue["severity"]
        if "file" in issue:
            issue_messages += "File: %s\n" % issue["file"]
        if "description" in issue:
            issue_messages += "Description: %s\n" % issue["description"]
        issue_messages += "\n"
    return issue_messages


def get_error_messages(param_dict, default_message=""):
    reason_message = default_message
    if param_dict is None or not isinstance(param_dict, dict):
        return reason_message

    if "message" not in param_dict or "error" not in param_dict["message"]:
        return reason_message

    error = param_dict["message"]["error"]

    if error is None:
        return reason_message

    if isinstance(error, str):
        reason_message = error
    elif isinstance(error, dict):
        reason_message = error["message"]
        detail = error.get("detail")
        if detail:
            if isinstance(detail, str):
                reason_message += "%s%s" % (os.linesep, str(detail))
            if isinstance(detail, list):
                reason_message += "%s%s" % (os.linesep, get_issue_messages(detail))

    return reason_message
