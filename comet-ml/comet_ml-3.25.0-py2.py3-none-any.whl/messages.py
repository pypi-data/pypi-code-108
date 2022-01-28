# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed without
#  the express permission of Comet ML Inc.
# *******************************************************
import json

from ._typing import Any, Callable, Dict, List, MemoryUploadable, Optional, Type
from .json_encoder import NestedEncoder
from .utils import fix_special_floats, local_timestamp


class BaseMessage(object):
    def repr_json(self):
        return {
            key: value
            for key, value in self.__dict__.items()
            if (not key.startswith("_"))
        }

    def to_json(self):
        json_re = json.dumps(
            self.repr_json(), sort_keys=True, indent=4, cls=NestedEncoder
        )
        return json_re

    def _non_null_dict(self):
        return {
            key: value
            for key, value in self.__dict__.items()
            if (value is not None and not key.startswith("_"))
        }


class CloseMessage(BaseMessage):
    """A special message indicating Streamer to ends and exit"""

    pass


class Message(BaseMessage):
    """
    A bean used to send messages to the server over websockets.
    """

    def __init__(self, context=None):
        self.local_timestamp = local_timestamp()

        # The following attributes are optional
        self.metric = None
        self.graph = None
        self.code = None
        self.stdout = None
        self.stderr = None
        self.fileName = None
        self.env_details = None
        self.html = None
        self.htmlOverride = None
        self.installed_packages = None
        self.os_packages = None
        self.log_other = None
        self.gpu_static_info = None
        self.git_meta = None
        self.log_dependency = None
        self.log_system_info = None
        self.context = context

    def set_log_other(self, key, value):
        self.log_other = {"key": key, "val": value}

    def set_log_dependency(self, name, version):
        self.log_dependency = {"name": name, "version": version}

    def set_system_info(self, key, value):
        self.log_system_info = {"key": key, "value": value}

    def set_installed_packages(self, val):
        self.installed_packages = val

    def set_os_packages(self, val):
        self.os_packages = val

    def set_metric(self, name, value, step=None, epoch=None):
        safe_value = fix_special_floats(value)
        self.metric = {
            "metricName": name,
            "metricValue": safe_value,
            "step": step,
            "epoch": epoch,
        }

    def set_html(self, value):
        self.html = value

    def set_html_override(self, value):
        self.htmlOverride = value

    def set_graph(self, graph):
        self.graph = graph

    def set_code(self, code):
        self.code = code

    def set_stdout(self, line):
        self.stdout = line
        self.stderr = False

    def set_stderr(self, line):
        self.stdout = line
        self.stderr = True

    def set_env_details(self, details):
        self.env_details = details

    def set_filename(self, fname):
        self.fileName = fname

    def set_gpu_static_info(self, info):
        self.gpu_static_info = info

    def set_git_metadata(self, metadata):
        self.git_meta = metadata

    def __repr__(self):
        filtered_dict = [(key, value) for key, value in self.__dict__.items() if value]
        string = ", ".join("%r=%r" % item for item in filtered_dict)
        return "Message(%s)" % string

    def __str__(self):
        return self.to_json()

    def __len__(self):
        return len(self.to_json())

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class UploadFileMessage(BaseMessage):
    def __init__(
        self,
        file_path,  # type: str
        upload_type,  # type: str
        additional_params,  # type: Dict[str, Optional[Any]]
        metadata,  # type: Optional[Any]
        size,  # type: int
        clean=True,  # type: bool
        critical=False,  # type: bool
        on_asset_upload=None,  # type: Optional[Callable]
        on_failed_asset_upload=None,  # type: Optional[Callable]
    ):
        # type: (...) -> None
        self.local_timestamp = local_timestamp()

        self.file_path = file_path
        self.upload_type = upload_type
        self.additional_params = additional_params
        self.metadata = metadata
        self.clean = clean
        self._size = size
        self._critical = critical
        self._on_asset_upload = on_asset_upload
        self._on_failed_asset_upload = on_failed_asset_upload

        # figName is not null and the backend fallback to figure_{FIGURE_NUMBER}
        # if not passed
        if (
            additional_params
            and "fileName" in additional_params
            and additional_params["fileName"] is None
        ):
            raise TypeError("file_name shouldn't be null")

    def _non_null_dict(self):
        return {
            key: value
            for key, value in self.__dict__.items()
            if (not key.startswith("_"))
        }


class UploadInMemoryMessage(BaseMessage):
    def __init__(
        self,
        file_like,  # type: MemoryUploadable
        upload_type,  # type: str
        additional_params,  # type: Dict[str, Optional[Any]]
        metadata,  # type: Optional[Any]
        size,  # type: int
        critical=False,  # type: bool
        on_asset_upload=None,  # type: Optional[Callable]
        on_failed_asset_upload=None,  # type: Optional[Callable]
    ):
        # type: (...) -> None
        self.local_timestamp = local_timestamp()

        self.file_like = file_like
        self.upload_type = upload_type
        self.additional_params = additional_params
        self.metadata = metadata
        self._size = size
        self._critical = critical
        self._on_asset_upload = on_asset_upload
        self._on_failed_asset_upload = on_failed_asset_upload

        # figName is not null and the backend fallback to figure_{FIGURE_NUMBER}
        # if not passed
        if (
            additional_params
            and "fileName" in additional_params
            and additional_params["fileName"] is None
        ):
            raise TypeError("file_name shouldn't be null")

    def _non_null_dict(self):
        return {
            key: value
            for key, value in self.__dict__.items()
            if (not key.startswith("_"))
        }


class RemoteAssetMessage(BaseMessage):
    def __init__(
        self,
        remote_uri,  # type: Any
        upload_type,  # type: str
        additional_params,  # type: Dict[str, Optional[Any]]
        metadata,  # type: Optional[Dict[str, str]]
        size,  # type: int
        critical=False,  # type: bool
        on_asset_upload=None,
        on_failed_asset_upload=None,
    ):
        # type: (...) -> None
        self.remote_uri = remote_uri
        self.upload_type = upload_type
        self.additional_params = additional_params
        self.metadata = metadata
        self._size = size
        self._critical = critical
        self._on_asset_upload = on_asset_upload
        self._on_failed_asset_upload = on_failed_asset_upload

    def _non_null_dict(self):
        return {
            key: value
            for key, value in self.__dict__.items()
            if (not key.startswith("_"))
        }


class OsPackagesMessage(BaseMessage):
    def __init__(self, os_packages):
        # type: (List[str]) -> None
        self.os_packages = os_packages

    def _non_null_dict(self):
        return self.__dict__


class ModelGraphMessage(BaseMessage):
    def __init__(self, graph):
        # type: (str) -> None
        self.graph = graph

    def _non_null_dict(self):
        return self.__dict__


class SystemDetailsMessage(BaseMessage):
    def __init__(
        self,
        command,  # type: str
        env,  # type: Optional[Dict[str, str]]
        hostname,  # type: str
        ip,  # type: str
        machine,  # type: str
        os_release,  # type: str
        os_type,  # type: str
        os,  # type: str
        pid,  # type: int
        processor,  # type: str
        python_exe,  # type: str
        python_version_verbose,  # type: str
        python_version,  # type: str
        user,  # type: str
    ):
        # type: (...) -> None

        self.command = command
        self.env = env
        self.hostname = hostname
        self.ip = ip
        self.machine = machine
        self.os = os
        self.os_release = os_release
        self.os_type = os_type
        self.pid = pid
        self.processor = processor
        self.python_exe = python_exe
        self.python_version = python_version
        self.python_version_verbose = python_version_verbose
        self.user = user

    def _non_null_dict(self):
        return self.__dict__


class CloudDetailsMessage(BaseMessage):
    def __init__(
        self,
        provider,  # type: str
        cloud_metadata,  # type: Dict[str, Any]
    ):
        # type: (...) -> None

        self.provider = provider
        self.cloud_metadata = cloud_metadata

    def _non_null_dict(self):
        return self.__dict__


class ParameterMessage(BaseMessage):

    message_type = "parameter_msg"

    """The Message type to encapsulate named parameter value.
    The parameter value can be either float or the list of floats."""

    def __init__(self, context=None, timestamp=None):
        # type: (Optional[str], Optional[int]) -> None
        if timestamp is None:
            timestamp = local_timestamp()

        self.context = context
        self.local_timestamp = timestamp

        # The following attributes are optional
        self.param = None  # type: Optional[Dict[str, Any]]
        self.params = None  # type: Optional[Dict[str, Any]]

    def set_param(self, name, value, step=None):
        # type: (str, Any, Optional[int]) -> None
        safe_value = fix_special_floats(value)
        self.param = {"paramName": name, "paramValue": safe_value, "step": step}

    def set_params(self, name, values, step=None):
        # type: (str, List[Any], Optional[int]) -> None
        safe_values = list(map(fix_special_floats, values))
        self.params = {"paramName": name, "paramValue": safe_values, "step": step}

    def get_param_name(self):
        # type: () -> Optional[str]
        """Returns the name of the parameter associated with this message."""
        if self.param:
            return self.param["paramName"]
        elif self.params:
            return self.params["paramName"]
        else:
            return None

    @classmethod
    def deserialize(cls, message_dict):
        # type: (Type['ParameterMessage'], Dict[str, Any]) -> 'ParameterMessage'
        """Recreate a ParameterMessage from its Dict representation"""
        parameter_message = cls(
            context=message_dict.get("context", None),
            timestamp=message_dict.get("local_timestamp", None),
        )

        if message_dict.get("param", None):
            parameter_message.set_param(
                message_dict["param"]["paramName"],
                message_dict["param"]["paramValue"],
                step=message_dict["param"]["step"],
            )
        elif message_dict.get("params", None):
            parameter_message.set_params(
                message_dict["params"]["paramName"],
                message_dict["params"]["paramValue"],
                step=message_dict["params"]["step"],
            )
        else:
            # TODO: WHAT TO DO?
            pass

        return parameter_message
