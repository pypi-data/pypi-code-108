from functools import wraps

from .cognito.exceptions import CognitoError
from .s3.exceptions import S3Error


def wrap_and_reraise_s3_errors(func):

    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except S3Error:
            raise   # Pass through S3 Exceptions
        except Exception as e:
            raise S3Error from e

    return wrapper_func


def wrap_and_reraise_cognito_errors(func):

    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CognitoError:
            raise   # Pass through Cognito Exceptions
        except Exception as e:
            raise CognitoError from e

    return wrapper_func
