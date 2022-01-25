"""
Copyright 2021 DataRobot, Inc. and its affiliates.

All rights reserved.

DataRobot, Inc. Confidential.

This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.

The copyright notice above does not evidence any actual or intended publication of such source code.

Released under the terms of DataRobot Tool and Utility Agreement.
"""

import re
from typing import Type

from ._version import __version__
from .datarobot_client import UserBlueprint, APIObject
from .friendly_repr import FriendlyRepr
from .settings import Settings


class TaskInput(object):
    """
    The types available to use as input data in Tasks.
    """

    NUMERIC = "NUM"
    CATEGORICAL = "CAT"
    TEXT = "TXT"
    DATE = "DATE"
    DATE_DURATION = "DATE_DURATION"
    IMAGE = "IMG"
    COUNT_DICT = "COUNT_DICT"
    GEOSPATIAL = "GEO"
    ALL = "ALL"

    @classmethod
    def all(cls):
        return [
            cls.ALL,
            cls.CATEGORICAL,
            cls.COUNT_DICT,
            cls.DATE,
            cls.DATE_DURATION,
            cls.GEOSPATIAL,
            cls.IMAGE,
            cls.NUMERIC,
            cls.TEXT,
        ]

    @classmethod
    def get_long_name(cls, input_type):
        type_map = {
            cls.NUMERIC: "Numeric",
            cls.CATEGORICAL: "Categorical",
            cls.TEXT: "Text",
            cls.DATE: "Date",
            cls.DATE_DURATION: "Date Duration",
            cls.IMAGE: "Image",
            cls.COUNT_DICT: "Summarized Categorical",
            cls.GEOSPATIAL: "Geospatial",
            cls.ALL: "All",
        }
        return type_map[input_type]

    @classmethod
    def get_variable_name(cls, value):
        lookup = {
            cls.NUMERIC: "NUMERIC",
            cls.CATEGORICAL: "CATEGORICAL",
            cls.TEXT: "TEXT",
            cls.DATE: "DATE",
            cls.DATE_DURATION: "DATE_DURATION",
            cls.IMAGE: "IMAGE",
            cls.COUNT_DICT: "COUNT_DICT",
            cls.GEOSPATIAL: "GEOSPATIAL",
            cls.ALL: "All",
        }
        if value not in lookup:
            return '"ILLEGAL_INPUT"'
        return "TaskInput.{}".format(lookup[value])


ValidInputSet = set(TaskInput.all())


class TaskOutputMethod(object):
    """
    The methods which can be used with Tasks to produce output data.
    """

    TRANSFORM = "T"
    TRANSFORM_STACK = "TS"
    STACK_MARGIN = "Sm"
    STACK = "S"
    PREDICT = "P"
    PREDICT_MARGIN = "Pm"

    @classmethod
    def all(cls):
        return [
            cls.TRANSFORM,
            cls.TRANSFORM_STACK,
            cls.STACK,
            cls.STACK_MARGIN,
            cls.PREDICT,
            cls.PREDICT_MARGIN,
        ]

    @classmethod
    def is_estimator(cls, task_method):
        return task_method in (
            cls.STACK,
            cls.STACK_MARGIN,
            cls.PREDICT,
            cls.PREDICT_MARGIN,
        )

    @classmethod
    def get_variable_name(cls, value):
        lookup = {
            cls.TRANSFORM: "TRANSFORM",
            cls.TRANSFORM_STACK: "TRANSFORM_STACK",
            cls.STACK_MARGIN: "STACK_MARGIN",
            cls.STACK: "STACK",
            cls.PREDICT: "PREDICT",
            cls.PREDICT_MARGIN: "PREDICT_MARGIN",
        }
        if value not in lookup:
            return '"ILLEGAL_INPUT"'
        return "TaskOutputMethod.{}".format(lookup[value])


def represents_input_data(string: str) -> bool:
    """
    Check if a string represents input data (e.g. 'NUM' or 'AUDIO').

    Parameters
    ----------
    string: string
        The id of a task/task in the graph.
    """
    return string in ValidInputSet


def refresh_cached(obj, attr_to_refresh, attr_to_exclude=None):
    """Refresh cached attributes (set to None) of obj.

    Parameters
    ----------
    obj:
        The cached attributes of this object are to be refreshed.
    attr_to_refresh:
        A list of attributes to be refreshed.
    attr_to_exclude:
        A list of attributes which are not to be refreshed.
    """

    attr_to_refresh = set(attr_to_refresh)
    excluded = attr_to_exclude or []
    excluded = set(excluded)
    attr_to_refresh = attr_to_refresh - excluded
    for attr_name in attr_to_refresh:
        setattr(obj, attr_name, None)


def documentation(task_definition, auto_open=False):
    url_object = task_definition.url
    if url_object is not None:
        url_path = url_object.documentation
        if url_path is not None:
            url = UserBlueprint._client.domain + url_path
            if auto_open:
                open_link(url)
            return url
    print("No documentation available for this task.")


def open_link(url):
    """ Try to directly open the provided url in the browser. """
    import sys

    if sys.platform == "win32":
        import os

        os.startfile(url)
        return

    import subprocess

    if sys.platform == "darwin":
        subprocess.Popen(["open", url])
        return

    try:
        subprocess.Popen(["xdg-open", url])
    except OSError:
        print("Please visit: {}".format(url))


def upper_case(match_obj):
    char_elem = match_obj.group(1)
    return char_elem.upper()


def safe_name(name):
    name = name.replace(" ", "_")
    name = re.sub(r"\W+", "", name)
    return re.sub(r"_(\w)", upper_case, name)


def task_ref(task):
    return "{}__{}".format(safe_name(task.label), task.task_code)


class PrettyString(FriendlyRepr, str):
    def __friendly_repr__(self):
        return self


class PrettyList(FriendlyRepr, list):
    def __friendly_repr__(self):
        return "\n\n".join([a.__repr__() for a in self])


class HiddenList(FriendlyRepr, list):
    def __friendly_repr__(self):
        return ""


def colorize(string: str, color: str):
    if not Settings().allow_color:
        return string

    """ Color a string for customized UX. """
    colors = {
        Colors.BLACK: "\u001b[30m",
        Colors.RED: "\u001b[31m",
        Colors.GREEN: "\u001b[32m",
        Colors.YELLOW: "\u001b[33m",
        Colors.BLUE: "\u001b[34m",
        Colors.MAGENTA: "\u001b[35m",
        Colors.CYAN: "\u001b[36m",
        Colors.WHITE: "\u001b[37m",
    }
    return "{}{}\x1b[0m".format(colors[color], string)


class Colors:
    BLACK = "black"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"
    WHITE = "white"
    # Meta-Colors
    SUCCESS = "green"
    ERROR = "red"
    WARNING = "yellow"


class Roles:
    OWNER = "OWNER"
    EDITOR = "USER"
    CONSUMER = "CONSUMER"


class RecipientType:
    USER = "user"
    GROUP = "group"
    ORGANIZATION = "organization"


def override_user_agent(api_object: Type[APIObject]) -> Type[APIObject]:
    """ Override the user agent to show using blueprint workshop. """
    try:
        api_object._client.headers["User-Agent"] = "BlueprintWorkshop/{}".format(
            __version__
        )
    except Exception:
        print("Unable to override User-Agent, falling back to default")
    return api_object
