# Get (hopefully useful, but at least obvious) output from segfaults, etc.
import faulthandler

faulthandler.enable()

try:
    import spark_preamble
except ImportError:
    pass

try:
    # Workaround to ensure that MDC is imported before other modules

    # When sklern Ridge (and probably other libraries) are imported before MDC
    # MDC can't connect to storage. That doesn't happen if MDC is imported first.

    # We still don't have a root cause for this, so this is a workaround until we
    # can find a better solution
    # Bug: 494716
    from azureml.monitoring import ModelDataCollector
except ImportError:
    pass

import traceback
import json
import threading

import aml_framework
from azureml.contrib.services.aml_request  import AMLRequest
from azureml.contrib.services.aml_response import AMLResponse

from aml_blueprint import AMLBlueprint
from run_function_exception import RunFunctionException
from timeout_exception import TimeoutException



main = AMLBlueprint('main', __name__)
user_main = main.user_main


class Watchdog(BaseException):
    def __init__(self, timeout, userHandler=None):  # timeout in seconds
        self.timeout = timeout
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = threading.Timer(self.timeout, self.handler)
        self.timer.start()

    def reset(self):
        self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self.handler)
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def defaultHandler(self):
        raise self


def get_service_input_from_url(g, request, is_raw):
    g.apiName = "/score"

    if is_raw:
        service_input = request
        service_input.__class__ = AMLRequest # upcast
    else:
        # Some Notes:
        #   - Request arg keys are case-sensitive(RFC 3986)
        #   - If there are repeated arg in the url, its values will be put as an array in the request body
        #
        # For example:
        #   - GET http://127.0.0.1:31311/score?foo=bar1&Foo=bar2&x=y
        #     * run() will receive
        #         {
        #             "Foo": "bar2",
        #             "foo": "bar1",
        #             "x": "y"
        #         }
        #   - GET http://127.0.0.1:31311/score?foo=bar1&foo=bar2&x=y
        #     * run() will receive
        #         {
        #             "x": "y",
        #             "foo": [
        #                 "bar1",
        #                 "bar2"
        #             ]
        #         }

        aml_input = {}
        for k in request.args.keys():
            values = request.args.getlist(k)
            if len(values) == 1:
                aml_input[k] = json.loads(values[0]) if is_json(values[0]) else values[0]
            else:
                value_list = []
                for v in values:
                    value_list.append(json.loads(v) if is_json(v) else v)

                aml_input[k] = value_list
        if main.request_is_parsed_json:
            service_input = aml_input
        else:
            service_input = json.dumps(aml_input)

    return service_input


def wrap_response(response):
    response_headers = {}
    response_body = response
    response_status_code = 200

    if isinstance(response, dict):
        if 'aml_response_headers' in response:
            main.logger.info("aml_response_headers are available from run() output")
            response_body = None
            response_headers = response['aml_response_headers']

        if 'aml_response_body' in response:
            main.logger.info("aml_response_body is available from run() output")
            response_body = response['aml_response_body']

    return AMLResponse(response_body, response_status_code, response_headers, json_str=True)


def prepare_user_params(service_input, headers, is_raw):
    if is_raw:
        params = {main.run_input_parameter_name: service_input}
    elif main.request_is_parsed_json:
        if main.wrapped:
            params = {main.run_input_parameter_name: service_input[main.wrapped_parameter_name]}
        else:
            params = service_input.copy()
    else:
        params = {main.run_input_parameter_name: service_input}
    # Flask request.headers is not python dict but werkzeug.datastructures.EnvironHeaders which is not json serializable
    # Per RFC 2616 sec 4.2,
    # 1. HTTP headers are case-insensitive: https://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.2
    #    So if user scores with header ("foo": "bar") from client, but what we give run() function could be ("FOO": "bar")
    # 2. HTTP header key could be duplicate. In this case, request_headers[key] will be a list of values.
    #    Values are connected by ", ". For example a request contains "FOO": "bAr" and "foO": "raB",
    #    the request_headers["Foo"] = "bAr, raB".

    if main.support_request_header:
        params["request_headers"] = dict(headers)

    return params


def alarm_handler(signum, frame):
    error_message = "Scoring timeout after {} ms".format(main.scoring_timeout_in_ms)
    raise TimeoutException(error_message)


def is_json(input_string):
    try:
        json_object = json.loads(input_string)
    except ValueError:
        return False
    return True


@main.route('/swagger.json', methods=['GET'])
def get_swagger_specification():
    aml_framework.g.apiName = "/swagger.json"
    if main.swagger:
        return AMLResponse(main.swagger, 200, json_str=True)
    main.logger.info("Swagger file not present")
    return AMLResponse("Swagger not found", 404, json_str=True)


# Health probe endpoint
@main.route('/', methods=['GET'])
def health_probe():
    return "Healthy"


# Errors from Server Side
def handle_server_exception(error):
    main.logger.debug("Server side exception caught")
    main.stop_hooks()
    main.logger.error("Encountered Exception: {0}".format(traceback.format_exc()))
    return AMLResponse(error.to_dict(), error.status_code, json_str=True)


# Errors from Client Request
def handle_client_exception(error):
    main.logger.debug("Client request exception caught")
    main.stop_hooks()
    main.logger.error("Encountered Exception: {0}".format(traceback.format_exc()))
    return AMLResponse(error.to_dict(), error.status_code, json_str=True)


# Errors from User Run Function
def handle_run_exception(error):
    main.logger.debug("Run function exception caught")
    main.stop_hooks()
    main.logger.error("Encountered Exception: {0}".format(traceback.format_exc()))
    return AMLResponse(error.message, error.status_code, json_str=False, run_function_failed=True)


# Errors of Scoring Timeout
def handle_timeout_exception(error):
    main.logger.debug("Run function timeout caught")
    main.stop_hooks()
    main.logger.error("Encountered Exception: {0}".format(traceback.format_exc()))
    return AMLResponse(error.message, error.status_code, json_str=False, run_function_failed=True)


# Unhandled Error
# catch all unhandled exceptions here and return the stack encountered in the response body
def all_unhandled_exception(error):
    main.stop_hooks()
    main.logger.debug("Unhandled exception generated")
    error_message = "Encountered Exception: {0}".format(traceback.format_exc())
    main.logger.error(error_message)
    internal_error = "An unexpected internal error occurred. {0}".format(error_message)
    return AMLResponse(internal_error, 500, json_str=False)


# log all response status code after request is done
@main.after_request
def after_request(response):
    if getattr(aml_framework.g, 'apiName', None):
        main.logger.info(response.status_code)
    return response


# Load framework-specific part of the routes
if aml_framework.is_async:
    import asynchronous.routes
else:
    import synchronous.routes
