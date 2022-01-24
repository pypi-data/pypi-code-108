from functools import wraps
from json.decoder import JSONDecodeError
from logging import getLogger
from typing import List

from requests import HTTPError, Response
from simplejson.errors import JSONDecodeError as SimpleJSONDecodeError

## logger definition
logger = getLogger(__name__)


class RallyError(Exception):
    """Rally Error"""

    def __init__(self, *args, response: Response = None):
        self._response: Response = response
        super().__init__(*args)

    def __str__(self):
        return f"RallyError: \n{str(chr(10).join(self.args))}"

    @property
    def response(self):
        """Resquests Response object"""
        return self._response


def requests_error_handling(func):
    """Decorator for rally requests error handling."""

    @wraps(func)
    def wrapper(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except HTTPError as err:
            response: Response = err.response
            logger.error(f"Error for request to: {response.request.url}")
            logger.error(f"{response.request.method}: {response.status_code}: Error reason: {response.reason}")
            raise err

        except RallyError as err:
            logger.error(err)
            raise err

    return wrapper


def rally_raise_errors(response: Response):
    """If errors found Raise error from Requests or Rally internal errors RallyError"""
    ## Requests errors
    response.raise_for_status()

    if response.reason == "Origin Time-out":
        raise RallyError(response.reason,
                         f"Time-Out for request to: {response.request.url}",
                         response=response)
    # Find out if response is not json
    try:
        response.json()
    except (JSONDecodeError, SimpleJSONDecodeError) as jde:
        raise RallyError(f"Unable to decode JSON response. Reason: {response.reason}, {response.status_code}",
                         f"Error for request to: {response.request.url}",
                         f"{response.request.method}: Error reason: {response.reason}",
                         response=response) from JSONDecodeError(jde.msg, jde.doc, jde.pos)
    errors: list = []
    try:
        if response.json().get("QueryResult"):
            errors = response.json()["QueryResult"]["Errors"]
        elif response.json().get("OperationalResult"):
            errors = response.json()["OperationResult"]["Errors"]
        elif response.json().get("CreateResult"):
            errors = response.json()["CreateResult"]["Errors"]
        elif response.json().get("BatchResult"):
            errors = response.json()["BatchResult"]["Errors"]
        else:
            root_element_name = list(response.json().keys())[0]
            errors = response.json()[root_element_name]["Errors"]

    except KeyError as kerr:
        raise RallyError(f"Unexpected JSON Response for '{response.request.method}': {kerr.args[0]}",
                         f"Error for request url: {response.request.url}",
                         f"Error reason: {response.reason}",
                         response=response) from KeyError

    if num_errors := len(errors):
        args: List[str] = []
        if len(list(filter(lambda e: e.count("unique"), errors))):
            args.append("Unique restriction raised!")
        args.extend([f"Error for request to: {response.request.url}",
                     f"{response.request.method}: Error reason: {response.reason}",
                     f"Error List: Total '{num_errors}' \n" + "\n".join(errors)])
        raise RallyError(*args, response=response)

    if not response.ok:
        raise RallyError(f"Error for request to: {response.request.url}",
                         f"{response.request.method} Error reason: {response.reason}",
                         response=response)
#
