"""
Declare all possible errors here

Steps to create errors:
1) Define error code, error message and relevant http status code in error_handling/constants.py
2) Create error class
3) call error_class.generate_error() to produce error dict response

Run this file to produce table markdown of error code with message and sample error dict response
"""

from typing import Dict

from centaur._.pyvmps.error_handling.constants import (
    ErrorCodes,
    ErrorMsgs,
    ErrorResponseKeys,
    InternalErrorMsgs,
    error_code_to_http_status_mapping,
)
from centaur._.pyvmps.logger.get_logger import get_logger

_logger = get_logger(__name__)


class Error:
    """To be used to generate error doc"""

    def __init__(self, error_code: str = "", message: str = "", details: str = ""):
        self.error_code: str = error_code
        self.message: str = message

    def generate_error(self, **kwargs) -> Dict[str, Dict]:
        """
        Returns dict with the following structure:
        {
            "error": {
                "message": ""
                "code": ""
                "details": ""
            }
        }
        """
        # res: Dict = {ErrorResponseKeys.ERROR_CODE: self.error_code, ErrorResponseKeys.ERROR_MESSAGE: self.message}
        res: Dict = {ErrorResponseKeys.ERROR_MESSAGE: self.message}
        if ErrorResponseKeys.ERROR_MESSAGE in kwargs:
            res[ErrorResponseKeys.ERROR_MESSAGE] = kwargs[ErrorResponseKeys.ERROR_MESSAGE]
        if ErrorResponseKeys.ERROR_DETAILS in kwargs:
            res[ErrorResponseKeys.ERROR_DETAILS] = kwargs[ErrorResponseKeys.ERROR_DETAILS]
        res.update(kwargs)

        return {ErrorResponseKeys.ERROR: res}


#     def generate_response(self) -> ErrorResponseStatus:
#         res: Dict = {
#             ErrorMsgs.ERROR_CODE: self.code,
#             ErrorMsgs.ERROR_MESSAGE: self.message,
#         }
#         return ErrorResponseStatus(res, self.status_code)


def general_error(error_code: str, message: str, details: str = "", **kwargs) -> Dict[str, Dict]:
    res: Dict = {ErrorResponseKeys.ERROR_CODE: error_code, ErrorResponseKeys.ERROR_MESSAGE: message}
    if details:
        res[ErrorResponseKeys.ERROR_DETAILS] = details
    res.update(kwargs)

    return {ErrorResponseKeys.ERROR: res}


# def get_http_code(response: Dict, mapping: Dict = error_code_to_http_status_mapping) -> int:
# error_dict = response.get(ErrorResponseKeys.ERROR, None)
# if not error_dict:
#     _logger.exception(InternalErrorMsgs.ERROR_RES_NO_ERROR_KEY)
#     raise Exception(InternalErrorMsgs.ERROR_RES_NO_ERROR_KEY)
# error_code = error_dict.get(ErrorResponseKeys.ERROR_CODE)
# if not error_code:
#     _logger.exception(InternalErrorMsgs.ERROR_RES_NO_ERROR_CODE)
#     raise Exception(InternalErrorMsgs.ERROR_RES_NO_ERROR_CODE)
# if error_code not in mapping:
#     _logger.exception(InternalErrorMsgs.ERROR_RES_ERROR_CODE_INVALID)
#     raise Exception(InternalErrorMsgs.ERROR_RES_ERROR_CODE_INVALID)
# return mapping[get_err_code(response)]


def get_err_code(response: Dict) -> str:
    error_dict = response.get(ErrorResponseKeys.ERROR, None)
    if not error_dict:
        _logger.exception(InternalErrorMsgs.ERROR_RES_NO_ERROR_KEY)
        raise Exception(InternalErrorMsgs.ERROR_RES_NO_ERROR_KEY)
    error_code = error_dict.get(ErrorResponseKeys.ERROR_CODE)
    if not error_code:
        _logger.exception(InternalErrorMsgs.ERROR_RES_NO_ERROR_CODE)
        raise Exception(InternalErrorMsgs.ERROR_RES_NO_ERROR_CODE)
    return error_code


def get_err_msg(response: Dict) -> str:
    error_dict = response.get(ErrorResponseKeys.ERROR, None)
    if not error_dict:
        _logger.exception(InternalErrorMsgs.ERROR_RES_NO_ERROR_KEY)
        raise Exception(InternalErrorMsgs.ERROR_RES_NO_ERROR_KEY)
    error_msg = error_dict.get(ErrorResponseKeys.ERROR_MESSAGE, "")
    return error_msg


def add_info_to_err_response(response: Dict, req_id: str, **kwargs) -> Dict:
    error_dict = response.get(ErrorResponseKeys.ERROR, None)
    if not error_dict:
        _logger.exception(InternalErrorMsgs.ERROR_RES_NO_ERROR_KEY)
        raise Exception(InternalErrorMsgs.ERROR_RES_NO_ERROR_KEY)
    error_dict[ErrorResponseKeys.ERROR_REQUEST_ID] = req_id
    for k, v in kwargs.items():
        error_dict[k] = v
    return response


# Errors and their error codes

# This error is returned as a last resort. When an internal_error is returned as an error response, this means
# an error has occured at an unexpected place and is not caught
internal_error = Error(error_code=ErrorCodes.INTERNAL_ERROR, message=InternalErrorMsgs.ERROR)

# Returned when the request stays in the incoming_req_q longer than HTTP_RESPONSE_TIMEOUT_IN_SECONDS
deadline_exceeded = Error(ErrorCodes.DEADLINE_EXCEEDED, ErrorMsgs.ERROR_DEADLINE_EXCEEDED)

# Returned when request body does not contain the correct structure for a tensorflow model to perform the inference
# Eg. missing input key, or incorrect nesting of object. Only applicable to http requests for tensorflow models.
invalid_tensor_input = Error(
    error_code=ErrorCodes.INVALID_TENSOR_INPUT, message=ErrorMsgs.ERROR_INVALID_TENSOR_INPUT_FORMAT
)

# Returned when the signature name in the request body for a tensorflow model does not match the
# signature names the model supports. Only applicable to http requests for tensorflow models.
invalid_tensor_signature = Error(
    error_code=ErrorCodes.INVALID_TENSOR_SIGNATURE, message=ErrorMsgs.ERROR_INVALID_TENSOR_SIGNATURE
)

# Returned when there is an issue parsing the request body. This is different from schema issues. Applicable to
# http requests for python and tensorflow models
invalid_input = Error(error_code=ErrorCodes.INVALID_INPUT, message=ErrorMsgs.ERROR_INVALID_INPUT)

# Returned when there is an issue running the tensorflow graph to produce an inference output
tf_graph_error = Error(error_code=ErrorCodes.ERROR_RUNNING_TF_GRAPH, message=ErrorMsgs.ERROR_RUNNING_TF_GRAPH)

# Returned when there is an issue calling the predict method of a python model
python_model_error = Error(
    error_code=ErrorCodes.ERROR_RUNNING_PYTHON_MODEL, message=ErrorMsgs.ERROR_RUNNING_PYTHON_MODEL
)

# Returned when model status is not AVAILABLE. This object is referenced only in the validity method
# is_versioned_model_loaded
model_loading_error = Error(error_code=ErrorCodes.MODEL_LOADING_ERROR, message=ErrorMsgs.ERROR_LOADING_MODEL)

# Returned when model or version in request path is invalid. This object is referenced only in the validity method
# is_model_version_valid
invalid_model = Error(error_code=ErrorCodes.INVALID_MODEL_OR_VERSION)

invalid_verb = Error(error_code=ErrorCodes.INVALID_INPUT, message=ErrorMsgs.ERROR_INVALID_VERB)

# Returned when venv_phase produces model specific errors. This object is referenced only in the validity method
# is_venv_creation_valid
venv_creation_model_specific_error = Error(
    error_code=ErrorCodes.VENV_CREATION_MODEL_SPECIFIC_ERROR, message=ErrorMsgs.ERROR_CREATING_MODEL_SPECIFIC_VENV
)

# Returned when venv_phase produces a global error. For now, this only happens when there is a problem parsing
# the model_config_object.conf file.
# This object is referenced only in the validity method is_venv_creation_valid
venv_creation_error = Error(error_code=ErrorCodes.VENV_CREATION_GLOBAL_ERROR, message=ErrorMsgs.ERROR_CREATING_VENVS)

# Returned when incoming request specifies the wrong method in for a particular url path
method_not_supported_error = Error(
    error_code=ErrorCodes.METHOD_NOT_SUPPORTED, message=ErrorMsgs.ERROR_REQ_METHOD_NOT_SUPPORTED
)

# Returned when a request url path is invalid
url_not_found_error = Error(error_code=ErrorCodes.URL_NOT_FOUND, message=ErrorMsgs.ERROR_URL_NOT_FOUND)

# Returned when model output cannot be serialized
model_output_not_json_serializable = Error(message=ErrorMsgs.ERROR_MODEL_OUTPUT_NOT_JSON_SERIALIZABLE)

failed_to_call_pre_processor = Error(message=ErrorMsgs.ERROR_CALLING_PRE_PROCESSOR)
failed_to_call_post_processor = Error(message=ErrorMsgs.ERROR_CALLING_POST_PROCESSOR)
invalid_return_from_pre_processor = Error(message=ErrorMsgs.ERROR_INVALID_RETURN_FROM_PRE_PROCESSOR)
invalid_return_from_post_processor = Error(message=ErrorMsgs.ERROR_INVALID_RETURN_FROM_POST_PROCESSOR)


errors = [
    url_not_found_error,
    method_not_supported_error,
    invalid_model,
    invalid_input,
    invalid_tensor_input,
    invalid_tensor_signature,
    tf_graph_error,
    python_model_error,
    model_loading_error,
    deadline_exceeded,
    venv_creation_error,
    venv_creation_model_specific_error,
    internal_error,
    model_output_not_json_serializable,
    failed_to_call_pre_processor,
    failed_to_call_post_processor,
    invalid_return_from_pre_processor,
    invalid_return_from_post_processor,
]


if __name__ == "__main__":

    print("Error Code | Error Response | Http Status Code")
    print("--- | --- | ---")
    for err in errors:
        print(
            "{err_code} | `{err_resp}` | {http_status_code}".format(
                err_code=err.error_code,
                err_resp=err.generate_error(details="{ErrorSpecificDetail}"),
                http_status_code=error_code_to_http_status_mapping[err.error_code],
            )
        )
