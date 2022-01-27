import re


class BinaryNotFoundError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class OMParsingError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class OMExecutionError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class OMBuildError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class OMAssertionError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class NotImplementedError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class UnknownParameterError(Exception):
    def __init__(self, param_name: str):
        msg = f"Parameter '{param_name}' is not a recognised parameter name"
        Exception.__init__(self, msg)


class UnknownModelError(Exception):
    def __init__(self, model_name: str):
        msg = f"Model '{model_name}' is not a recognised model name."
        Exception.__init__(self, msg)


class ResultRetrievalError(Exception):
    def __init__(self):
        msg = "Failed to retrieve simulation results, could not read output files."
        Exception.__init__(self, msg)


class UnknownOptionError(Exception):
    def __init__(self, opt_name: str):
        msg = f"Option '{opt_name}' is not a recognised simulation option"
        Exception.__init__(self, msg)


class ModelicaFileGenerationError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class UnknownLibraryError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


def parse_error_string_compiler(out_string: str, error_string: str):
    if "Failed to parse file" in out_string:
        _error = [i for i in out_string.split("\n") if i and i[0] == "["]
        raise OMParsingError(", ".join(_error))
    elif "Execution failed!" in error_string:
        raise OMExecutionError(f"Failed to execute compiled code:\n{out_string}")
    elif "failed" in out_string:
        raise OMBuildError(
            ", ".join([i for i in out_string.split("\n") if "failed" in i.lower()])
        )


def parse_error_string_simulate(out_string: str, terminate_on_assert: str = "error"):
    if "division by zero" in out_string:
        _line = [i for i in out_string.split("\n") if "division by zero" in i]
        raise ZeroDivisionError(_line[0].split("|")[-1].strip())
    elif "simulation terminated by an assertion" in out_string:
        raise OMAssertionError(f"Simulation run failed:\n{out_string}")

    _find_assert = re.compile(r"assert\s*\|\s*(\w+)\s*\|", re.IGNORECASE)
    _asserts = _find_assert.findall(out_string)

    _assertion_ranking = ("debug", "info", "warning", "error", "never")

    if not _asserts:
        return

    _assertion_rank_pass = [
        _assertion_ranking.index(i) >= _assertion_ranking.index(terminate_on_assert)
        for i in _asserts
    ]

    if any(_assertion_rank_pass):
        raise OMAssertionError(out_string)
