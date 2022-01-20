import wrapt
from pydantic import ValidationError

from .utils import get_formatted_validation_error
from ..exceptions import StorageServerResponseValidationException


def validate_http_response_wrapper(function, model, **kwargs):
    try:
        return model.validate(kwargs).dict(exclude_unset=True)
    except ValidationError as e:
        errors_report = get_formatted_validation_error(e)
        error_text = f"HTTP Response validation failed during {function.__qualname__}():{errors_report}"
        raise StorageServerResponseValidationException(error_text) from None


def validate_http_response(model):
    @wrapt.decorator
    def decorator(function, instance, args, kwargs):
        (content, http_repsonse) = function(*args, **kwargs)
        validation_res = validate_http_response_wrapper(function, model, **{"body": content})
        return (validation_res["body"], http_repsonse)

    return decorator
