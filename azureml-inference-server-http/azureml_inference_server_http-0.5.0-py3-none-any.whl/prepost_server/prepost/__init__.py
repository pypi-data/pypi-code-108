import logging
import aiotask_context as context

from sanic import Sanic
from sanic.exceptions import NotFound
from sanic_cors import CORS

from .aml_blueprint import aml_bp
from .middleware import (
    add_request_id_if_not_exists,
    add_response_request_id,
    add_response_run_function_failed,
    set_log_level,
    reset_log_level,
)
from .error_handlers import catch_404s, catch_user_code_errors, catch_triton_inference_errors
from .user.exceptions import UserCodeException, TritonInferenceException
from .log_settings import LOG_SETTINGS
from .constants import LOG_LEVEL_MAP


def create_app(name="prepost-server"):
    aml_app = Sanic(name, log_config=LOG_SETTINGS)
    aml_app.blueprint(aml_bp)

    cors = CORS(aml_app, resources={r"/score": {"methods": ["POST", "OPTIONS"]}})
    logging.getLogger("sanic_cors").level = logging.getLogger().level

    #
    # WARNING:
    #     * Request middlewares are executed in the order declared.
    #     * Response middlewares are executed in reverse order.
    #
    # Details can be found here: https://sanicframework.org/en/guide/basics/middleware.html#order-of-execution-2
    #
    aml_app.register_middleware(add_request_id_if_not_exists, "request")
    aml_app.register_middleware(set_log_level, "request")
    aml_app.register_middleware(reset_log_level, "response")
    aml_app.register_middleware(add_response_request_id, "response")
    aml_app.register_middleware(add_response_run_function_failed, "response")

    aml_app.error_handler.add(UserCodeException, catch_user_code_errors)
    aml_app.error_handler.add(NotFound, catch_404s)
    aml_app.error_handler.add(TritonInferenceException, catch_triton_inference_errors)

    aml_app.config.FALLBACK_ERROR_FORMAT = "json"
    return aml_app
