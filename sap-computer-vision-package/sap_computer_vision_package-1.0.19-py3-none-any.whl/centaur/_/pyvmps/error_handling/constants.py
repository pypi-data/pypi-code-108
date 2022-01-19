from typing import Dict


class ErrorDictConstants:
    """Error constants used in Error report"""

    ERROR = "error"
    ERROR_MODELS = "venv_phase_model_errors"
    ERROR_VENV_PHASE_ERRORS = "venv_phase_errors"


class ErrorMsgs:
    """Error Messages to include in error message to adhere to api guidelines"""

    # venv_creator phase error msg
    METADATA_CONFIG_JSON_ERROR = "Error Occured in Reading metadata config.json of model"
    MODEL_CONFIG_ERROR = "Error Occured in Parsing model config file"
    VENV_INSTALLATION_ERROR = "Error occurred while installing Model Dependencies"
    VERSION_MODEL_CONFIG_ERROR = "Exception occured generating versioned model config"
    # TF_VS_NOT_SUPPORTED = "Tensorflow version {} not supported"
    # VENV_CREATION_PHASE = "Error Occured in the venv Creation phase"

    # server errors
    ERROR_BAD_REQUEST = "Bad request"
    ERROR_DEADLINE_EXCEEDED = "Deadline exceeded"
    ERROR_INVALID_MODEL = "Invalid Model"
    ERROR_INVALID_VERB = "Invalid Verb"
    ERROR_INVALID_MODEL_VERSION = "Invalid Model Version"
    ERROR_MODEL_UNREACHABLE = "Model Unreachable"
    ERROR_INVALID_INPUT = "Error parsing request body"
    ERROR_INVALID_TENSOR_INPUT_FORMAT = "Invalid tensor input format"
    ERROR_INVALID_TENSOR_SIGNATURE = "Invalid tensor signature"

    ERROR_REQ_METHOD_NOT_SUPPORTED = "Invalid method used in request"
    ERROR_URL_NOT_FOUND = "Invalid url path"

    # model predict error
    ERROR_RUNNING_TF_GRAPH = "An error occured while performing actual inferencing task"
    ERROR_RUNNING_PYTHON_MODEL = "An error occured while calling python model"

    # venv creation errors
    ERROR_CREATING_VENVS = "An error occured during virtual environment creation"
    ERROR_CREATING_MODEL_SPECIFIC_VENV = "An error occured during virtual environment creation for this model"

    # model loading errors
    ERROR_LOADING_MODEL = "Model could not load successfully"

    # model output not json serializable
    ERROR_MODEL_OUTPUT_NOT_JSON_SERIALIZABLE = "Model output is not json serializable"

    ERROR_CALLING_PRE_PROCESSOR = "An error encountered while calling model pre-processor"
    ERROR_CALLING_POST_PROCESSOR = "An error encountered while calling model post-processor"
    ERROR_INVALID_RETURN_FROM_PRE_PROCESSOR = "Invalid return from model pre-processor"
    ERROR_INVALID_RETURN_FROM_POST_PROCESSOR = "Invalid return from model post-processor"


class ExceptionMsgs:
    """Execption messages to throw based on different scenarios"""

    TF_INVALID_INPUT_MISSING_KEY = "Input data does not contain required `{input_key}` input key"
    TF_INVALID_INPUT_KEY_NOT_SPECIFIED = "Input keys not specified in data"
    TF_INVALID_INPUT_NO_KEY_FOUND = "No `instances` or `inputs` key found in input data"
    TF_INVALID_INPUT_TENSOR_SHAPE = "Invalid tensor shape, expected={expected_shape}, received={received_shape}"

    VENV_PLATFORM_NOT_SUPPORTED = "{model_platform} platform is not supported"
    VENV_CREATION_PHASE = "Error Occured in the venv Creation phase"
    TF_VS_NOT_SUPPORTED = "Tensorflow version {tf_version} not supported"

    # metadata file (config.json) related exception messages
    MODEL_CONFIG_CONF_SCHEMA_ERROR = (
        "Error occured when reading metadata from model configuration: {validation_error_message}"
    )
    CONFIG_JSON_SCHEMA_ERROR = "Invalid metadata file at `{metadata_file_path}` file provided. If a tf model config.json was used:\
        {tf_err_msg}. If python model config.json was used: {py_err_msg}"
    CONFIG_JSON_NOT_DICT = "config.json is not a collection of name:value pairs"
    CONFIG_JSON_IS_INVALID_JSON = (
        "Metadata file `{metadata_file}` cannot be parsed. Please check if it is a valid json object"
    )
    CONFIG_JSON_FILE_MISSING = "Missing config.json from the model path {model_metadata_path}"

    TF_INVALID_SIGNATURE_KEY = "Invalid signature '{signature}'"
    INVALID_MODEL_NAME = "The model '{model_name}' does not exist"
    INVALID_MODEL_VERSION = "The model '{model_name}' does not have version '{model_version}'"
    MISSING_MODEL_CONF_FILE = "Missing model config object file from the path {serving_config_path}"


class InternalErrorMsgs:
    """Internal Error handling messages"""

    ERROR = "Unknown error has occured"
    ERROR_RES_NO_ERROR_KEY = "Internal Error - Error response missing error key"
    ERROR_RES_NO_ERROR_CODE = "Internal Error - Error response missing error code"
    ERROR_RES_ERROR_CODE_INVALID = "Internal Error - Error code invalid"
    ERROR_PREPPING_RES_UDS_HANDLER = "Internal Error - Error preparing response"
    ERROR_SLIPPED_THROUGH_TO_HANDLER = "Unknown exception occured"


class ErrorResponseKeys:
    """Keys inside error response message"""

    ERROR = "error"
    ERROR_CODE = "code"
    ERROR_MESSAGE = "message"
    ERROR_DETAILS = "details"
    ERROR_TARGET = "target"
    ERROR_REQUEST_ID = "requestId"


class ErrorCodes:
    """Error codes to send as part of error messages. Each error message should have a specific error code.
    Some messages may be generated dynamically (eg. only when tensorflow evaluates incoming inputs.
    This cannot be helped. We can group the messages under specific error codes if needed)

    Structure: AABBXXXX
    * AA - Centaur code (10)
    * BB - Category of error
    * XX - phase in which error occured
    * YY - specific error code within the category

    Categories of errors (BB):
    0 - User issue
    1 - model issue
    2 - system issue
    3 - venv issue

    Phases that produce error (XX):
    1) Method & url path errors
    2) Validity errors (venv created, model version valid, model loaded)
    3) Request body errors (json validity, schema validity)
    4) Model inferencing errors
    5) Broker
    0) Occured at unexpected place



    Each error code falls under a combination of a phase and category of error

    """

    URL_NOT_FOUND = "10000000"
    METHOD_NOT_SUPPORTED = "10000001"
    INVALID_MODEL_OR_VERSION = "10000100"
    INVALID_INPUT = "10000200"  # input cannot be parsed (i.e. invalid json object)
    INVALID_TENSOR_INPUT = (
        "10000201"  # input structure is not valid..ie missing certain keys that a tensorflow predict input requires
    )
    INVALID_TENSOR_SIGNATURE = (
        "10000202"  # signature name in input does not match signature names that the model offers
    )

    ERROR_RUNNING_TF_GRAPH = "10010300"  # error running predict method of tf model
    ERROR_RUNNING_PYTHON_MODEL = "10010301"  # error running predict method in python model

    MODEL_LOADING_ERROR = "10020100"
    DEADLINE_EXCEEDED = "10020400"
    INTERNAL_ERROR = "10029999"

    VENV_CREATION_GLOBAL_ERROR = "10030100"
    VENV_CREATION_MODEL_SPECIFIC_ERROR = "10030101"


error_code_to_http_status_mapping: Dict = {
    ErrorCodes.ERROR_RUNNING_TF_GRAPH: 400,
    ErrorCodes.DEADLINE_EXCEEDED: 400,
    ErrorCodes.INVALID_MODEL_OR_VERSION: 404,
    ErrorCodes.INVALID_INPUT: 400,
    ErrorCodes.INTERNAL_ERROR: 500,
    ErrorCodes.INVALID_TENSOR_INPUT: 400,
    ErrorCodes.INVALID_TENSOR_SIGNATURE: 400,
    ErrorCodes.MODEL_LOADING_ERROR: 503,
    ErrorCodes.VENV_CREATION_MODEL_SPECIFIC_ERROR: 503,
    ErrorCodes.VENV_CREATION_GLOBAL_ERROR: 503,
    ErrorCodes.METHOD_NOT_SUPPORTED: 405,
    ErrorCodes.URL_NOT_FOUND: 404,
    ErrorCodes.ERROR_RUNNING_PYTHON_MODEL: 400,
}
