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
import json
import os

import contextlib2
from requests_toolbelt import MultipartEncoder
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject
from datarobot.models.custom_model_version import (
    CustomDependency,
    CustomModelFileItem,
    RequiredMetadataValue,
)
from datarobot.models.custom_task_version_dependency_build import CustomTaskVersionDependencyBuild
from datarobot.models.trafarets import UserBlueprintTaskArgument_
from datarobot.models.user_blueprints.models import UserBlueprintTaskArgument
from datarobot.utils import camelize, deprecation_warning, encode_utf8_if_py2
from datarobot.utils.pagination import unpaginate
from datarobot.utils.waiters import wait_for_custom_resolution


class CustomTaskFileItem(CustomModelFileItem):
    """A file item attached to a DataRobot custom task version.

    .. versionadded:: v2.26

    Attributes
    ----------
    id: str
        id of the file item
    file_name: str
        name of the file item
    file_path: str
        path of the file item
    file_source: str
        source of the file item
    created_at: str
        ISO-8601 formatted timestamp of when the version was created
    """

    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("file_name"): String(),
            t.Key("file_path"): String(),
            t.Key("file_source"): String(),
            t.Key("created") >> "created_at": String(),
        }
    ).ignore_extra("*")

    schema = _converter


class CustomTaskVersion(APIObject):
    """A version of a DataRobot custom task.

    .. versionadded:: v2.26

    Attributes
    ----------
    id: str
        id of the custom task version
    custom_task_id: str
        id of the custom task
    version_minor: int
        a minor version number of custom task version
    version_major: int
        a major version number of custom task version
    label: str
        short human readable string to label the version
    created_at: str
        ISO-8601 formatted timestamp of when the version was created
    is_frozen: bool
        a flag if the custom task version is frozen
    items: List[CustomTaskFileItem]
        a list of file items attached to the custom task version
    description: str, optional
        custom task version description
    required_metadata: Dict[str, str]
        Deprecated in v2.26. Use require_metadata_values instead.

        Additional parameters required by the execution environment. The required keys are
        defined by the fieldNames in the base environment's requiredMetadataKeys. Once set,
        they cannot be changed. If you want to change them, make a new version.
    base_environment_id: str, optional
        id of the environment to use with the task
    base_environment_version_id: str, optional
        id of the environment version to use with the task
    dependencies: List[CustomDependency]
        the parsed dependencies of the custom task version if the
        version has a valid requirements.txt file
    required_metadata_values: List[RequiredMetadataValue]
        Additional parameters required by the execution environment. The required keys are
        defined by the fieldNames in the base environment's requiredMetadataKeys.
    arguments: List[UserBlueprintTaskArgument]
        A list of custom task version arguments.
    """

    _path = "customTasks/{}/versions/"
    _dependency_build_path = "customTasks/{}/versions/{}/dependencyBuild/"
    _dependency_build_log_path = "customTasks/{}/versions/{}/dependencyBuildLog/"

    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("custom_task_id"): String(),
            t.Key("version_major"): Int(),
            t.Key("version_minor"): Int(),
            t.Key("label"): String(),
            t.Key("created") >> "created_at": String(),
            t.Key("is_frozen"): t.Bool(),
            t.Key("items"): t.List(CustomTaskFileItem.schema),
            # because `from_server_data` scrubs Nones, this must be optional here.
            t.Key("description", optional=True): String(max_length=10000, allow_blank=True)
            | t.Null(),
            t.Key("maximum_memory", optional=True): Int(),
            t.Key("required_metadata", optional=True): t.Mapping(String(), String()),
            t.Key("base_environment_id", optional=True): String() | t.Null(),
            t.Key("base_environment_version_id", optional=True): String() | t.Null(),
            t.Key("dependencies", optional=True): t.List(CustomDependency.schema),
            t.Key("required_metadata_values", optional=True): t.List(RequiredMetadataValue.schema),
            t.Key("arguments", optional=True): t.List(UserBlueprintTaskArgument_),
        }
    ).ignore_extra("*")

    schema = _converter

    def __init__(
        self,
        id,
        custom_task_id,
        version_major,
        version_minor,
        label,
        created_at,
        is_frozen,
        items,
        description=None,
        required_metadata=None,
        base_environment_id=None,
        maximum_memory=None,
        base_environment_version_id=None,
        dependencies=None,
        required_metadata_values=None,
        arguments=None,
    ):
        if dependencies is None:
            dependencies = []
        arguments = arguments or []

        self.id = id
        self.custom_task_id = custom_task_id
        self.description = description
        self.version_major = version_major
        self.version_minor = version_minor
        self.label = label
        self.created_at = created_at
        self.is_frozen = is_frozen
        self.items = [CustomTaskFileItem(**data) for data in items]

        self.required_metadata = required_metadata
        self.maximum_memory = maximum_memory
        self.required_metadata_values = (
            [RequiredMetadataValue(**val) for val in required_metadata_values]
            if required_metadata_values
            else None
        )
        self.base_environment_id = base_environment_id
        self.base_environment_version_id = base_environment_version_id
        self.dependencies = [CustomDependency(**data) for data in dependencies]
        self.arguments = [UserBlueprintTaskArgument(**argument) for argument in arguments]

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}({!r})".format(self.__class__.__name__, self.label or self.id)
        )

    def _update_values(self, new_response):
        # type (CustomTaskVersion) -> None
        for attr in self._fields():
            new_value = getattr(new_response, attr)
            setattr(self, attr, new_value)

    @classmethod
    def _all_versions_path(cls, task_id):
        # type: (str) -> str
        return cls._path.format(task_id)

    @classmethod
    def _single_version_path(cls, task_id, version_id):
        # type: (str, str) -> str
        return cls._all_versions_path(task_id) + "{}/".format(version_id)

    @classmethod
    def from_server_data(cls, data, keep_attrs=None):
        initial = super(CustomTaskVersion, cls).from_server_data(data, keep_attrs)
        # from_server_data will make the keys in requiredMetadata lowercase,
        # which is not OK. we need to preserve case
        initial.required_metadata = data.get("requiredMetadata")
        return initial

    @classmethod
    def create_clean(
        cls,
        custom_task_id,
        base_environment_id,
        maximum_memory=None,
        is_major_update=True,
        folder_path=None,
        required_metadata=None,
        required_metadata_values=None,
    ):
        """Create a custom task version without files from previous versions.

        .. versionadded:: v2.26

        Parameters
        ----------
        custom_task_id: str
            the id of the custom task
        base_environment_id: str
            the id of the base environment to use with the custom task version
        is_major_update: bool, optional
            if the current version is 2.3, `True` would set the new version at `3.0`.
            `False` would set the new version at `2.4`.
            Default to `True`
        folder_path: str, optional
            the path to a folder containing files to be uploaded.
            Each file in the folder is uploaded under path relative
            to a folder path
        required_metadata: Dict[str, str]
            Deprecated in v2.26. Use require_metadata_values instead.

            Additional parameters required by the execution environment. The required keys are
            defined by the fieldNames in the base environment's requiredMetadataKeys. Once set,
            they cannot be changed. If you want to change them, make a new version.
        required_metadata_values: List[RequiredMetadataValue]
            Additional parameters required by the execution environment. The required keys are
            defined by the fieldNames in the base environment's requiredMetadataKeys.
        maximum_memory: int
            A number in bytes about how much memory custom tasks' inference containers can run with.

        Returns
        -------
        CustomTaskVersion
            created custom task version

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        return cls._create(
            "post",
            custom_task_id,
            is_major_update,
            base_environment_id,
            folder_path,
            maximum_memory=maximum_memory,
            required_metadata=required_metadata,
            required_metadata_values=required_metadata_values,
        )

    @classmethod
    def create_from_previous(
        cls,
        custom_task_id,
        base_environment_id,
        is_major_update=True,
        folder_path=None,
        files_to_delete=None,
        required_metadata=None,
        required_metadata_values=None,
        maximum_memory=None,
    ):
        """Create a custom task version containing files from a previous version.

        .. versionadded:: v2.26

        Parameters
        ----------
        custom_task_id: str
            the id of the custom task
        base_environment_id: str
            the id of the base environment to use with the custom task version
        is_major_update: bool, optional
            if the current version is 2.3, `True` would set the new version at `3.0`.
            `False` would set the new version at `2.4`.
            Default to `True`
        folder_path: str, optional
            the path to a folder containing files to be uploaded.
            Each file in the folder is uploaded under path relative
            to a folder path
        files_to_delete: list, optional
            the list of a file items ids to be deleted
            Example: ["5ea95f7a4024030aba48e4f9", "5ea6b5da402403181895cc51"]
        required_metadata: Dict[str, str]
            Deprecated in v2.26. Use require_metadata_values instead.

            Additional parameters required by the execution environment. The required keys are
            defined by the fieldNames in the base environment's requiredMetadataKeys. Once set,
            they cannot be changed. If you want to change them, make a new version.
        required_metadata_values: List[RequiredMetadataValue]
            Additional parameters required by the execution environment. The required keys are
            defined by the fieldNames in the base environment's requiredMetadataKeys.
        maximum_memory: int
            A number in bytes about how much memory custom tasks' inference containers can run with.

        Returns
        -------
        CustomTaskVersion
            created custom task version

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        return cls._create(
            "patch",
            custom_task_id,
            is_major_update,
            base_environment_id,
            folder_path,
            maximum_memory,
            files_to_delete=files_to_delete,
            required_metadata=required_metadata,
            required_metadata_values=required_metadata_values,
        )

    @classmethod
    def _create(
        cls,
        method,
        custom_task_id,
        is_major_update,
        base_environment_id,
        folder_path=None,
        maximum_memory=None,
        files_to_delete=None,
        required_metadata=None,
        required_metadata_values=None,
    ):
        url = cls._all_versions_path(custom_task_id)

        upload_data = [
            ("isMajorUpdate", str(is_major_update)),
            ("baseEnvironmentId", base_environment_id),
        ]
        if files_to_delete:
            upload_data += [("filesToDelete", file_id) for file_id in files_to_delete]
        if required_metadata is not None:
            deprecation_warning(
                "required_metadata",
                deprecated_since_version="2.26",
                will_remove_version="2.27",
                message="Use required_metadata_values instead.",
            )
            if required_metadata_values is not None:
                raise ValueError(
                    "Cannot specify both required_metadata and required_metadata_values. "
                    "Please use required_metadata_values."
                )
            upload_data.append(("requiredMetadata", json.dumps(required_metadata)))

        if required_metadata_values is not None:
            upload_data.append(
                (
                    "requiredMetadataValues",
                    json.dumps(
                        [
                            {camelize(k): v for k, v in val.to_dict().items()}
                            for val in required_metadata_values
                        ]
                    ),
                )
            )

        if maximum_memory:
            upload_data.append(("maximumMemory", str(maximum_memory)))

        cls._verify_folder_path(folder_path)

        with contextlib2.ExitStack() as stack:
            if folder_path:
                for dir_name, _, file_names in os.walk(folder_path):
                    for file_name in file_names:
                        file_path = os.path.join(dir_name, file_name)
                        file = stack.enter_context(open(file_path, "rb"))

                        upload_data.append(("file", (os.path.basename(file_path), file)))
                        upload_data.append(("filePath", os.path.relpath(file_path, folder_path)))

            encoder = MultipartEncoder(fields=upload_data)
            headers = {"Content-Type": encoder.content_type}
            response = cls._client.request(method, url, data=encoder, headers=headers)
        return cls.from_server_data(response.json())

    @staticmethod
    def _verify_folder_path(folder_path):
        if folder_path and not os.path.exists(folder_path):
            raise ValueError("The folder: {} does not exist.".format(folder_path))

    @classmethod
    def list(cls, custom_task_id):
        """List custom task versions.

        .. versionadded:: v2.26

        Parameters
        ----------
        custom_task_id: str
            the id of the custom task

        Returns
        -------
        List[CustomTaskVersion]
            a list of custom task versions

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        url = cls._all_versions_path(custom_task_id)
        data = unpaginate(url, None, cls._client)
        return [cls.from_server_data(item) for item in data]

    @classmethod
    def get(cls, custom_task_id, custom_task_version_id):
        """Get custom task version by id.

        .. versionadded:: v2.26

        Parameters
        ----------
        custom_task_id: str
            the id of the custom task
        custom_task_version_id: str
            the id of the custom task version to retrieve

        Returns
        -------
        CustomTaskVersion
            retrieved custom task version

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        path = cls._single_version_path(custom_task_id, custom_task_version_id)
        return cls.from_location(path)

    def download(self, file_path):
        """Download custom task version.

        .. versionadded:: v2.26

        Parameters
        ----------
        file_path: str
            path to create a file with custom task version content

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """

        response = self._client.get(
            self._single_version_path(self.custom_task_id, self.id) + "download/"
        )
        with open(file_path, "wb") as f:
            f.write(response.content)

    def update(self, description=None, required_metadata=None, required_metadata_values=None):
        """Update custom task version properties.

        .. versionadded:: v2.26

        Parameters
        ----------
        description: str
            new custom task version description
        required_metadata: Dict[str, str]
            Deprecated in v2.26. Use require_metadata_values instead.

            Additional parameters required by the execution environment. The required keys are
            defined by the fieldNames in the base environment's requiredMetadataKeys. Once set,
            they cannot be changed. If you want to change them, make a new version.
        required_metadata_values: List[RequiredMetadataValue]
            Additional parameters required by the execution environment. The required keys are
            defined by the fieldNames in the base environment's requiredMetadataKeys.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        payload = {}
        if description:
            payload.update({"description": description})
        if required_metadata is not None:
            deprecation_warning(
                "required_metadata",
                deprecated_since_version="2.26",
                will_remove_version="2.27",
                message="Use required_metadata_values instead.",
            )
            if required_metadata_values is not None:
                raise ValueError(
                    "Cannot specify both required_metadata and required_metadata_values. "
                    "Please use required_metadata_values."
                )
            payload.update({"requiredMetadata": required_metadata})

        if required_metadata_values is not None:
            payload.update(
                {"requiredMetadataValues": [val.to_dict() for val in required_metadata_values]}
            )

        url = self._path.format(self.custom_task_id)
        path = "{}{}/".format(url, self.id)

        response = self._client.patch(path, data=payload)

        data = response.json()
        new_version = CustomTaskVersion.from_server_data(data)
        self._update_values(new_version)

    def refresh(self):
        """Update custom task version with the latest data from server.

        .. versionadded:: v2.26

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """

        new_object = self.get(self.custom_task_id, self.id)
        self._update_values(new_object)

    def start_dependency_build(self):
        """Start the dependency build for a custom task version and return build status.
        .. versionadded:: v2.27

        Returns
        -------
        CustomTaskVersionDependencyBuild
            DTO of custom task version dependency build.
        """
        url = self._dependency_build_path.format(self.custom_task_id, self.id)
        response = self._client.post(url)
        server_data = response.json()
        return CustomTaskVersionDependencyBuild.from_server_data(server_data)

    def start_dependency_build_and_wait(self, max_wait):
        """Start the dependency build for a custom task version and wait while pulling status.
        .. versionadded:: v2.27

        Parameters
        ----------
        max_wait: int
            max time to wait for a build completion

        Returns
        -------
        CustomTaskVersionDependencyBuild
            DTO of custom task version dependency build.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        datarobot.errors.AsyncTimeoutError
            Raised if the dependency build is not finished after max_wait.
        """
        custom_task_id = self.custom_task_id
        custom_task_version_id = self.id

        def build_complete(response):
            server_data = response.json()
            if server_data["buildStatus"] in ["success", "failed"]:
                return CustomTaskVersionDependencyBuild.from_server_data(server_data)
            return None

        url = self._dependency_build_path.format(custom_task_id, custom_task_version_id)
        self._client.post(url)
        return wait_for_custom_resolution(self._client, url, build_complete, max_wait)

    def cancel_dependency_build(self):
        """Cancel custom task version dependency build that is in progress.
        .. versionadded:: v2.27

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """

        url = self._dependency_build_path.format(self.custom_task_id, self.id)
        self._client.delete(url)

    def get_dependency_build(self):
        """Retrieve information about a custom task version's dependency build.
        .. versionadded:: v2.27

        Returns
        -------
        CustomTaskVersionDependencyBuild
            DTO of custom task version dependency build.
        """

        url = self._dependency_build_path.format(self.custom_task_id, self.id)
        response = self._client.get(url)
        server_data = response.json()
        return CustomTaskVersionDependencyBuild.from_server_data(server_data)

    def download_dependency_build_log(self, file_directory="."):
        """Get log of a custom task version dependency build.
        .. versionadded:: v2.27

        Parameters
        ----------
        file_directory: str (optional, default is ".")
            Directory path where downloaded file is to save.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """

        url = self._dependency_build_log_path.format(self.custom_task_id, self.id)
        response = self._client.get(url)
        content_disposition = response.headers["Content-Disposition"]
        fiie_name = content_disposition[len("attachment; filename=") :]
        with open(os.path.join(file_directory, fiie_name), "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
