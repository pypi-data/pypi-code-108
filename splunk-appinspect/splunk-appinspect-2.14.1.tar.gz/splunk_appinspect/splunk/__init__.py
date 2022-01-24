"""
Splunk AppInspect Splunk version object definition module.
Represent a version like splunk_7_2_0
"""
import re
from builtins import filter

from .telemetry import telemetry_whitelist  # noqa: F401
from .util import normalizeBoolean  # noqa: F401


class TargetSplunkVersion(object):
    """
    An object to abstract the target Splunk version that is inspected against, meanwhile providing some useful APIs.
    '"""

    def __init__(self, tags):
        """
        If there are mutiple splunk_x_x tags. Only the last one is considered.
        """
        splunk_tags = list(filter(lambda e: re.match(r"splunk_\d+_\d+", e), tags))
        if not splunk_tags:
            self._target_version_value = float("inf")
        else:
            self._target_version_value = self._version_value(splunk_tags[-1])

    def __le__(self, other):
        return self._target_version_value <= self._version_value(other)

    def __eq__(self, other):
        return self._target_version_value == self._version_value(other)

    def __ge__(self, other):
        return self._target_version_value >= self._version_value(other)

    def __lt__(self, other):
        return self._target_version_value < self._version_value(other)

    def __gt__(self, other):
        return self._target_version_value > self._version_value(other)

    def __str__(self):
        return f"<{self.__class__.__name__}: {self._target_version_value}>"

    __repr__ = __str__

    @staticmethod
    def _version_value(tag):
        """
        Convert version number in a splunk_tag into an integer of two digits.
        For example: splunk_7_2 -> 72
        """
        numbers = tag.split("_")[1:]
        numbers = list(map(int, numbers))
        assert len(numbers) <= 2
        value = 0
        for i in range(len(numbers)):
            value += 10 ** (1 - i) * numbers[i]
        return value
