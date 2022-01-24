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
from datarobot.models.execution_environment_version import ExecutionEnvironmentVersion
from datarobot.utils import encode_utf8_if_py2
from datarobot.utils.pagination import unpaginate


class RequiredMetadataKey(APIObject):
    """Definition of a metadata key that custom models using this environment must define

    .. versionadded:: v2.25

    Attributes
    ----------
    field_name: str
        The required field key. This value will be added as an environment
        variable when running custom models.
    display_name: str
        A human readable name for the required field.
    """

    _converter = t.Dict({t.Key("field_name"): String(), t.Key("display_name"): String()})

    schema = _converter

    def __init__(self, **kwargs):
        self._set_values(**kwargs)

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}(field_name={!r}, display_name={!r})".format(
                self.__class__.__name__, self.field_name, self.display_name,
            )
        )

    def _set_values(self, field_name, display_name):
        self.field_name = field_name
        self.display_name = display_name

    def to_dict(self):
        return self._converter.check(
            {"field_name": self.field_name, "display_name": self.display_name}
        )


class ExecutionEnvironment(APIObject):
    """An execution environment entity.

    .. versionadded:: v2.21

    Attributes
    ----------
    id: str
        the id of the execution environment
    name: str
        the name of the execution environment
    description: str, optional
        the description of the execution environment
    programming_language: str, optional
        the programming language of the execution environment.
        Can be "python", "r", "java" or "other"
    is_public: bool, optional
        public accessibility of environment, visible only for admin user
    created_at: str, optional
        ISO-8601 formatted timestamp of when the execution environment version was created
    latest_version: ExecutionEnvironmentVersion, optional
        the latest version of the execution environment
    """

    _path = "executionEnvironments/"
    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("name"): String(max_length=255),
            t.Key("description", optional=True): String(max_length=10000, allow_blank=True)
            | t.Null(),
            t.Key("programming_language", optional=True): String(),
            t.Key("is_public", optional=True): t.Bool(),
            t.Key("created", optional=True) >> "created_at": String(),
            t.Key("latest_version", optional=True): ExecutionEnvironmentVersion.schema,
            t.Key("required_metadata_keys", optional=True, default=list): t.List(
                RequiredMetadataKey.schema
            ),
        }
    ).ignore_extra("*")

    def __init__(self, **kwargs):
        self._set_values(**kwargs)

    def __repr__(self):
        return encode_utf8_if_py2(u"{}({!r})".format(self.__class__.__name__, self.name or self.id))

    def _set_values(
        self,
        id,
        name,
        description=None,
        programming_language=None,
        is_public=None,
        created_at=None,
        latest_version=None,
        required_metadata_keys=None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.programming_language = programming_language
        self.is_public = is_public
        self.created_at = created_at
        self.required_metadata_keys = [
            RequiredMetadataKey.from_data(key) for key in required_metadata_keys
        ]

        if latest_version is not None:
            latest_version.pop("image_id", None)  # "image_id" is being removed in RAPTOR-2460
            self.latest_version = ExecutionEnvironmentVersion(**latest_version)
        else:
            self.latest_version = None

    @classmethod
    def create(cls, name, description=None, programming_language=None, required_metadata_keys=None):
        """Create an execution environment.

        .. versionadded:: v2.21

        Parameters
        ----------
        name: str
            execution environment name
        description: str, optional
            execution environment description
        programming_language: str, optional
            programming language of the environment to be created.
            Can be "python", "r", "java" or "other". Default value - "other"
        required_metadata_keys: List[RequiredMetadataKey]
            Definition of a metadata keys that custom models using this environment must define

        Returns
        -------
        ExecutionEnvironment
            created execution environment

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        required_metadata_keys = required_metadata_keys or []
        payload = {
            "name": name,
            "description": description,
            "programming_language": programming_language,
        }
        if required_metadata_keys:
            payload["required_metadata_keys"] = [key.to_dict() for key in required_metadata_keys]
        response = cls._client.post(cls._path, data=payload)
        environment_id = response.json()["id"]
        return cls.get(environment_id)

    @classmethod
    def list(cls, search_for=None):
        """List execution environments available to the user.

        .. versionadded:: v2.21

        Parameters
        ----------
        search_for: str, optional
            the string for filtering execution environment - only execution
            environments that contain the string in name or description will
            be returned.

        Returns
        -------
        List[ExecutionEnvironment]
            a list of execution environments.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        data = unpaginate(cls._path, {"search_for": search_for}, cls._client)
        return [cls.from_server_data(item) for item in data]

    @classmethod
    def get(cls, execution_environment_id):
        """Get execution environment by it's id.

        .. versionadded:: v2.21

        Parameters
        ----------
        execution_environment_id: str
            ID of the execution environment to retrieve

        Returns
        -------
        ExecutionEnvironment
            retrieved execution environment

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        path = "{}{}/".format(cls._path, execution_environment_id)
        return cls.from_location(path)

    def delete(self):
        """Delete execution environment.

        .. versionadded:: v2.21

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        url = "{}{}/".format(self._path, self.id)
        self._client.delete(url)

    def update(self, name=None, description=None, required_metadata_keys=None):
        """Update execution environment properties.

        .. versionadded:: v2.21

        Parameters
        ----------
        name: str, optional
            new execution environment name
        description: str, optional
            new execution environment description
        required_metadata_keys: List[RequiredMetadataKey]
            Definition of a metadata keys that custom models using this environment must define

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        payload = {"name": name, "description": description}
        if required_metadata_keys is not None:
            payload["required_metadata_keys"] = [key.to_dict() for key in required_metadata_keys]

        url = "{}{}/".format(self._path, self.id)
        response = self._client.patch(url, data=payload)

        data = response.json()
        self._set_values(**self._safe_data(data, do_recursive=True))

    def refresh(self):
        """Update execution environment with the latest data from server.

        .. versionadded:: v2.21

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        url = "{}{}/".format(self._path, self.id)
        response = self._client.get(url)

        data = response.json()
        self._set_values(**self._safe_data(data, do_recursive=True))
