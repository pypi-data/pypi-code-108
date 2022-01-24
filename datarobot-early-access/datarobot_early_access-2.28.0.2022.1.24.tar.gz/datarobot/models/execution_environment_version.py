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
import os
import shutil
import tempfile
import time

import trafaret as t

from datarobot import errors
from datarobot._compat import Int, String
from datarobot.enums import DEFAULT_MAX_WAIT, EXECUTION_ENVIRONMENT_VERSION_BUILD_STATUS
from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2
from datarobot.utils.pagination import unpaginate


class ExecutionEnvironmentVersion(APIObject):
    """A version of a DataRobot execution environment.

    .. versionadded:: v2.21

    Attributes
    ----------
    id: str
        the id of the execution environment version
    environment_id: str
        the id of the execution environment the version belongs to
    build_status: str
        the status of the execution environment version build
    label: str, optional
        the label of the execution environment version
    description: str, optional
        the description of the execution environment version
    created_at: str, optional
        ISO-8601 formatted timestamp of when the execution environment version was created
    docker_context_size: int, optional
        The size of the uploaded Docker context in bytes if available or None if not
    docker_image_size: int, optional
        The size of the built Docker image in bytes if available or None if not
    """

    _path = "executionEnvironments/{}/versions/"
    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("environment_id"): String(),
            t.Key("build_status"): String(),
            t.Key("label", optional=True): String(max_length=50, allow_blank=True) | t.Null(),
            t.Key("description", optional=True): String(max_length=10000, allow_blank=True)
            | t.Null(),
            t.Key("created", optional=True) >> "created_at": String(),
            t.Key("docker_context_size", optional=True): Int() | t.Null(),
            t.Key("docker_image_size", optional=True): Int() | t.Null(),
        }
    ).ignore_extra("*")

    schema = _converter

    def __init__(self, **kwargs):
        self._set_values(**kwargs)

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}({!r})".format(self.__class__.__name__, self.label or self.id)
        )

    def _set_values(
        self,
        id,
        environment_id,
        build_status,
        label=None,
        description=None,
        created_at=None,
        docker_context_size=None,
        docker_image_size=None,
    ):
        self.id = id
        self.environment_id = environment_id
        self.build_status = build_status
        self.label = label
        self.description = description
        self.created_at = created_at
        self.docker_context_size = docker_context_size
        self.docker_image_size = docker_image_size

    @classmethod
    def create(
        cls,
        execution_environment_id,
        docker_context_path,
        label=None,
        description=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """Create an execution environment version.

        .. versionadded:: v2.21

        Parameters
        ----------
        execution_environment_id: str
            the id of the execution environment
        docker_context_path: str
            the path to a docker context archive or folder
        label: str, optional
            short human readable string to label the version
        description: str, optional
            execution environment version description
        max_wait: int, optional
            max time to wait for a final build status ("success" or "failed").
            If set to None - method will return without waiting.

        Returns
        -------
        ExecutionEnvironmentVersion
            created execution environment version

        Raises
        ------
        datarobot.errors.AsyncTimeoutError
            if version did not reach final state during timeout seconds
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        if os.path.isdir(docker_context_path):
            docker_context_file = tempfile.NamedTemporaryFile(suffix=".zip")
            shutil.make_archive(
                os.path.splitext(docker_context_file.name)[0], "zip", docker_context_path
            )
        else:
            docker_context_file = open(docker_context_path, "rb")

        try:
            url = cls._path.format(execution_environment_id)

            response = cls._client.build_request_with_file(
                form_data={"label": label, "description": description},
                fname="docker_context",
                file_field_name="docker_context",
                filelike=docker_context_file,
                url=url,
                method="post",
            )

            version_id = response.json()["id"]

            if max_wait is None:
                return cls.get(execution_environment_id, version_id)
            return cls._await_final_build_status(execution_environment_id, version_id, max_wait)
        finally:
            docker_context_file.close()

    @classmethod
    def list(cls, execution_environment_id, build_status=None):
        """List execution environment versions available to the user.

        .. versionadded:: v2.21

        Parameters
        ----------
        execution_environment_id: str
            the id of the execution environment
        build_status: str, optional
            build status of the execution environment version to filter by.
            See datarobot.enums.EXECUTION_ENVIRONMENT_VERSION_BUILD_STATUS for valid options

        Returns
        -------
        List[ExecutionEnvironmentVersion]
            a list of execution environment versions.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        url = cls._path.format(execution_environment_id)
        data = unpaginate(url, {"build_status": build_status}, cls._client)
        return [cls.from_server_data(item) for item in data]

    @classmethod
    def get(cls, execution_environment_id, version_id):
        """Get execution environment version by id.

        .. versionadded:: v2.21

        Parameters
        ----------
        execution_environment_id: str
            the id of the execution environment
        version_id: str
            the id of the execution environment version to retrieve

        Returns
        -------
        ExecutionEnvironmentVersion
            retrieved execution environment version

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        url = cls._path.format(execution_environment_id)
        path = "{}{}/".format(url, version_id)
        return cls.from_location(path)

    def download(self, file_path):
        """Download execution environment version.

        .. versionadded:: v2.21

        Parameters
        ----------
        file_path: str
            path to create a file with execution environment version content

        Returns
        -------
        ExecutionEnvironmentVersion
            retrieved execution environment version

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        url = self._path.format(self.environment_id)
        path = "{}{}/download/".format(url, self.id)

        response = self._client.get(path)
        with open(file_path, "wb") as f:
            f.write(response.content)

    def get_build_log(self):
        """Get execution environment version build log and error.

        .. versionadded:: v2.21

        Returns
        -------
        Tuple[str, str]
            retrieved execution environment version build log and error.
            If there is no build error - None is returned.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        url = self._path.format(self.environment_id)
        path = "{}{}/buildLog/".format(url, self.id)
        result = self._client.get(path).json()
        log = result["log"]
        error = result["error"]
        if error == "":
            error = None
        return log, error

    def refresh(self):
        """Update execution environment version with the latest data from server.

        .. versionadded:: v2.21

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        base_url = self._path.format(self.environment_id)
        url = "{}{}/".format(base_url, self.id)
        response = self._client.get(url)

        data = response.json()
        self._set_values(**self._safe_data(data, do_recursive=True))

    @classmethod
    def _await_final_build_status(cls, execution_environment_id, version_id, max_wait):
        """Awaits until an execution environment version gets to a final state.

        Parameters
        ----------
        execution_environment_id: str
            the id of the execution environment
        version_id: str
            the id of the execution environment version to retrieve
        max_wait: int or float, optional
            max time to wait in seconds

        Returns
        -------
        ExecutionEnvironmentVersion
            execution environment version

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        datarobot.errors.AsyncTimeoutError
            if version did not reach final state during timeout seconds
        """
        timeout_at = time.time() + max_wait
        while True:
            version = cls.get(execution_environment_id, version_id)
            if version.build_status in EXECUTION_ENVIRONMENT_VERSION_BUILD_STATUS.FINAL_STATUSES:
                break
            if time.time() >= timeout_at:
                raise errors.AsyncTimeoutError(
                    "Timeout while waiting for environment version to be built. Timeout: {}, "
                    "current state: {}, environment id: {}, environment version id: {}".format(
                        max_wait, version.build_status, version.id, version.environment_id,
                    )
                )
            time.sleep(5)
        return version
