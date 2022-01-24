import traceback

from oarepo_oai_pmh_harvester.decorators import rule_error_handler


@rule_error_handler("uk", "xoai")
def call_error_handler_uk(el, path, phase, results):
    error_handler(el, path, phase, results)


def error_handler(el, path, phase, results):
    exc = traceback.format_exc()
    if "rulesExceptions" not in results[-1]:
        results[-1]["rulesExceptions"] = []
    results[-1]["rulesExceptions"].append(
        {"path": path, "element": str(el), "phase": phase, "exception": exc})
