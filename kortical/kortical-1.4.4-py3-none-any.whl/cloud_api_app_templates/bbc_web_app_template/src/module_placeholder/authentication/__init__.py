from functools import wraps
import logging
import traceback

import flask

from module_placeholder.api.http_status_codes import UNAUTHORISED, UNEXPECTED_ERROR
from module_placeholder.authentication.authentication import validate_authentication

logger = logging.getLogger(__name__)


def safe_api_call(*dargs):
    # Support both @safe_api_call and @safe_api_call() as valid syntax
    if len(dargs) == 1 and callable(dargs[0]):
        return safe_api_call()(dargs[0])
    else:
        def decorated(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                valid = validate_authentication()
                if not valid:
                    return flask.Response(
                        'Request failed to authenticate.',
                        status=UNAUTHORISED
                        )
                try:
                    # Execute the wrapped API call implementation and receive the return dictionary
                    result = func(*args, **kwargs)
                    return result
                except:
                    status = UNEXPECTED_ERROR
                    message = f"Exception in call to {flask.request.path}\n\n{traceback.format_exc()}"
                    logger.exception(message)

                return flask.Response(message, status=status)

            return wrapper

        return decorated


