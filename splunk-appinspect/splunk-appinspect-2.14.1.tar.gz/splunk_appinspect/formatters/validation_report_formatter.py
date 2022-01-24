"""
Base class for all Splunk AppInspect report formatter
"""
# Copyright 2019 Splunk Inc. All rights reserved.


class ValidationReportFormatter(object):
    """
    Base class for all Splunk AppInspect report formatter
    """

    def __init__(self):
        pass

    def format(self, validation_report):
        error_output = "Derived Formatter classes should override this"
        raise NotImplementedError(error_output)
