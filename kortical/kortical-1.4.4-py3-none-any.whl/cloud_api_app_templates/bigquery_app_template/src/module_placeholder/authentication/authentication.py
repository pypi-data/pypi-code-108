import logging

from flask import request

from module_placeholder.config import read_config

authentication_config = read_config("authentication.yml")
api_token = authentication_config['api_token']

logger = logging.getLogger(__name__)


def validate_authentication():
    valid = _validate_api_key(request)
    return valid


def _validate_api_key(req):
    logger.info("Validating API key")
    # Support providing the api key in the following ways: api_key in an arg or in a form, or Api-Key as a header.
    api_key_from_request = req.args.get('api_key')
    if api_key_from_request is None:
        api_key_from_request = req.form.get('api_key')
        if api_key_from_request is None:
            api_key_from_request = req.headers.get('Api-Key')
            if api_key_from_request is None:
                logger.info("No api key was found.")
                return False

    if api_key_from_request.lower() != api_token:
        # do not show valid_api_key in this message as it will become the actual response
        logger.warning(f"The api_key in the request '{api_key_from_request}' is invalid.")
        return False

    return True
