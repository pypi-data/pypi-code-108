import logging
import datetime
from inspect import getframeinfo, stack
import os
from io import StringIO
from html.parser import HTMLParser
from crequest.middleware import CrequestMiddleware


class Log:
    logger = None
    fn_times = None
    reduce_logging = None

    def __init__(self):
        self.logger = logging.getLogger("psu")
        self.fn_times = {}

    @staticmethod
    def reduce_logging():
        request = CrequestMiddleware.get_request()
        if request:
            aws_health_check = (
                "HTTP_USER_AGENT" in request.META
                and "HealthChecker" in request.META["HTTP_USER_AGENT"]
            )
            scheduler = (
                "scheduler/run" in request.path or "scheduler/aws/run" in request.path
            )
            return aws_health_check or scheduler
        return False

    def debug(self, msg, strip_html=False):
        # Do not do debug logging for AWS Health Checks
        if not self.reduce_logging():
            self.logger.debug(strip_tags(msg) if strip_html else msg)

    def info(self, msg, strip_html=False):
        self.logger.info(strip_tags(msg) if strip_html else msg)

    def warn(self, msg, strip_html=False):
        self.logger.warning(strip_tags(msg) if strip_html else msg)

    def warning(self, msg, strip_html=False):
        self.logger.warning(strip_tags(msg) if strip_html else msg)

    def error(self, msg, trace_error=True, strip_html=False):
        filename, line, function = self.get_caller_data()
        if trace_error:
            trace = f"-- encountered in function {function}() at {filename}:{line}"
            self.logger.error(f"{strip_tags(msg) if strip_html else msg} {trace}")
        else:
            self.logger.error(f"{strip_tags(msg) if strip_html else msg}")

    def trace(self, parameters=None, function_name=None):
        if self.reduce_logging():
            return

        # If function name not specified, get it from the stack
        if function_name is None:
            function_name = self.get_calling_function()

        self.fn_times[function_name] = {"start": datetime.datetime.now()}

        if type(parameters) is dict:
            ll = [f"{kk}='{vv}'" for kk, vv in parameters.items()]
            params = ", ".join(ll)
            self.logger.debug("TRACE : {0}({1})".format(function_name, params))
            del params
        else:
            params = self.get_param_string(parameters)
            self.logger.debug("TRACE : {0}({1})".format(function_name, params))
            del params

    def end(self, result=None, function_name=None):
        if self.reduce_logging():
            # Don't log anything
            # Return the result for a one-liner -- return log.end(whatever)
            return result

        # If function name not specified, get it from the stack
        if function_name is None:
            function_name = self.get_calling_function()

        # If start time is known, log a completion time
        metric_txt_add_on = ""
        if function_name in self.fn_times and "start" in self.fn_times[function_name]:
            self.fn_times[function_name]["stop"] = datetime.datetime.now()
            delta = (
                self.fn_times[function_name]["stop"]
                - self.fn_times[function_name]["start"]
            )
            duration = str(int(delta.total_seconds() * 1000))
            metric_txt_add_on = f"-- completed in {duration} ms"
            del self.fn_times[function_name]

        # Only log a return value if a result was provided
        if result is not None:
            self.logger.debug(
                f"RETURN: {function_name}() ==> {result} {metric_txt_add_on}"
            )

        # If no result was given, just log a completion message
        else:
            self.logger.debug(f"RETURN: {function_name}() {metric_txt_add_on}")

        # Return the result for a one-liner -- return log.end(whatever)
        return result

    def summary(self, result=None, parameters=None):
        # Get function name from the stack
        function_name = self.get_calling_function()

        # One message summarizes the function called, its parameters, and the result
        return_txt = ""
        if result is not None:
            return_txt = f" ==> {str(result)}"
        param_txt = self.get_param_string(parameters)
        self.logger.debug(f"TRACED: {function_name}({param_txt}) {return_txt}")

    def get_calling_function(self):
        filename, line, function = self.get_caller_data()
        file_basename = os.path.splitext(os.path.basename(filename))[0]
        return "{0}.{1}".format(file_basename, function)

    @staticmethod
    def get_param_string(parameters=None):

        params = str("" if parameters is None else parameters).strip()

        # Parameters are probably given in a list or dict, but may also contain a list or dict
        # Cannot strip {}[] characters because it would also strip indicators of list/dict in first/last parameter
        if params.startswith("[") and params.endswith("]"):
            params = params[1:-1]
        if params.startswith("{") and params.endswith("}"):
            params = params[1:-1]
        return params

    @staticmethod
    def get_caller_data(include_full_path=False):
        """Return the calling code as (file-name, line-number, function-name)"""

        # Ignore this function, and the Log.<function> that called it
        depth = 2

        # Get the info about the function that called the log wrapper
        caller = getframeinfo(stack()[depth][0])

        # In case of nested functions within this class, may need to look deeper
        while caller.filename.endswith("Log.py"):
            depth += 1
            caller = getframeinfo(stack()[depth][0])

        return (
            caller.filename if include_full_path else os.path.basename(caller.filename),
            caller.lineno,
            caller.function,
        )


# For removing HTML from messages prior to logging them
class MLStripper(HTMLParser):
    def error(self, message):
        pass

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html_string):
    # replace br with \n
    for br in ["<br>", "<br />", '<br style="clear:both;" />']:
        if br in html_string:
            html_string = html_string.replace(br, "\n")
    s = MLStripper()
    s.feed(html_string)
    return s.get_data()
