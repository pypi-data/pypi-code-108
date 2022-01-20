
import re

# -- import all external validators, some of them will be overloaded
# -- with the custom implementations
import validators as vals  # noqa
from .exceptions import ValidatorError


NULL = 'NULL'


#
# FIELD VALIDATORS
#
def not_null(field_name, value):

    message = f'env.{field_name}: Null value are not allowed'

    if value is None:
        raise ValidatorError(message)


def url(field_name, url_text):

    message = f'env.{field_name}: Text "{url_text}" is not valid URL'

    # -- in order to force the underlying library to work correctly
    # -- with websockets protocol as well as some other future protocols
    # -- the following trick must be included
    modified_url_text = re.sub(r'^wss?', 'http', url_text)
    if vals.url(modified_url_text) is not True:
        raise ValidatorError(message)

    return True


def length(field_name, text, min_length=None, max_length=None):

    if min_length:
        message = (
            f'env.{field_name}: Text "{text}" is too short. '
            f'min length: {min_length}')

        if vals.length(text, min=min_length) is not True:
            raise ValidatorError(message)

    if max_length:
        message = (
            f'env.{field_name}: Text "{text}" is too long. '
            f'max length: {max_length}')

        if vals.length(text, max=max_length) is not True:
            raise ValidatorError(message)

    return True
