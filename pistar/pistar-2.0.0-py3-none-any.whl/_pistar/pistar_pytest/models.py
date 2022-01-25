from enum import Enum
from typing import List

from attr import Factory
from attr import attrib
from attr import attrs

TEST_CASE_PATTERN = "{prefix}-result.json"
ATTACHMENT_PATTERN = "{prefix}-attachment.{ext}"


class AttachmentType(Enum):
    def __init__(self, mime_type, extension):
        self.mime_type = mime_type
        self.extension = extension

    TEXT = ("text/plain", "log")


@attrs
class Executable:
    """
    Base Class to describe the result information.

    """

    name = attrib(default=None)
    result = attrib(default=None)
    exception = attrib(type=List["Exceptions"], default=Factory(list))
    description = attrib(default=None)
    attachments = attrib(default=Factory(list))
    start_time = attrib(default=0)
    end_time = attrib(default=0)
    duration = attrib(default=None)

    def add_exception(self, exceptions: "Exceptions"):
        if exceptions is None:
            return

        self.exception = [exceptions]

    def cal_duration(self):
        val = self.end_time - self.start_time
        # in pistar,time must be more than 1ms
        if val > 0:
            self.duration = val
        else:
            self.duration = 1


@attrs
class TestResult(Executable):
    file_pattern = TEST_CASE_PATTERN
    uuid = attrib(default=None)
    testCaseId = attrib(default=None)
    fullName = attrib(default=None)
    step_type = attrib(default="test")
    labels = attrib(default=Factory(list))
    before = attrib(default=Factory(list))
    after = attrib(default=Factory(list))
    test = attrib(default=None)


@attrs
class BeforeResult(Executable):
    pass


@attrs
class AfterResult(Executable):
    pass


@attrs
class Attachment:
    name = attrib(type=str, default=None)
    path = attrib(type=str, default=None)
    type = attrib(type=str, default=None)


@attrs
class Label:
    name = attrib(type=str, default=None)
    value = attrib(type=str, default=None)


@attrs
class Exceptions:
    title = attrib(type=str, default=None)
    detail = attrib(type=str, default=None)


class LabelType(str):
    PARENT_SUITE = "parentSuite"
    SUITE = "suite"
    SUB_SUITE = "subSuite"


class Status(Enum):
    """
    The case execution status.
    Because pytest use string to describe the result,
    we need to convert string to a value-based enum.

    Ignore TIMOUT and ERROR (just a placeholder now).
    """

    def __init__(self, key, val):
        self.key = key
        self.val = val

    PASSED = ("passed", 1)
    FAILED = ("failed", 2)
    TIMEOUT = ("timeout", 3)
    ERROR = ("error", 4)
    BROKEN = ("broken", 5)
    SKIPPED = ("skipped", 6)
    UNKNOWN = ("unknown", 7)
