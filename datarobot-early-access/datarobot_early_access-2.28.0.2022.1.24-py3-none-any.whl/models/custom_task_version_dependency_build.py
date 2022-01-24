#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import trafaret as t

from datarobot._compat import String
from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2


class CustomTaskVersionDependencyBuild(APIObject):
    """Metadata about a DataRobot custom task version's dependency build
    .. versionadded:: v2.27

    Attributes
    ----------
    custom_task_id: str
        id of the custom task
    custom_task_version_id: str
        id of the custom task version
    build_status: str
        the status of the custom task version's dependency build
    started_at: str
        ISO-8601 formatted timestamp of when the build was started
    completed_at: str
        ISO-8601 formatted timestamp of when the build has completed
    build_log_location: str
        Location of retrieving dependency build log
    """

    _converter = t.Dict(
        {
            t.Key("custom_task_id"): String(),
            t.Key("custom_task_version_id"): String(),
            t.Key("build_status"): String(),
            t.Key("build_start") >> "started_at": String(),
            t.Key("build_end", optional=True) >> "completed_at": String() | t.Null(),
            t.Key("build_log_location", optional=True): String() | t.Null(),
        }
    ).ignore_extra("*")

    schema = _converter

    def __init__(
        self,
        custom_task_id,
        custom_task_version_id,
        build_status,
        started_at,
        completed_at=None,
        build_log_location=None,
    ):
        self.custom_task_id = custom_task_id
        self.custom_task_version_id = custom_task_version_id
        self.build_status = build_status
        self.started_at = started_at
        self.completed_at = completed_at
        self.build_log_location = build_log_location

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}(task={!r}, version={!r}, status={!r})".format(
                self.__class__.__name__,
                self.custom_task_id,
                self.custom_task_version_id,
                self.build_status,
            )
        )
