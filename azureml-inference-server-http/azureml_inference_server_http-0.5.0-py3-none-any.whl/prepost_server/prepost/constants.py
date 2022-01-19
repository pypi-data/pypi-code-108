import logging

SCRIPT_CLASS_NAME = "ModelHandler"

# Default Values
DEFAULT_APP_ROOT = "/var/azureml-app"
DEFAULT_AZUREML_BACKEND_HOST = "localhost"
DEFAULT_BACKEND_REST_PORT = "8000"
DEFAULT_BACKEND_GRPC_PORT = "8001"

# Environment Variables
ENV_AML_APP_ROOT = "AML_APP_ROOT"
ENV_AML_ENTRY_SCRIPT = "AZUREML_ENTRY_SCRIPT"
ENV_AZUREML_BACKEND_HOST = "AZUREML_BACKEND_HOST"
ENV_AZUREML_BACKEND_PORT = "AZUREML_BACKEND_PORT"
ENV_BACKEND_TRANSPORT_PROTOCOL = "TRANSPORT_PROTOCOL"

LOG_LEVEL_MAP = {
    "notset": logging.NOTSET,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}
