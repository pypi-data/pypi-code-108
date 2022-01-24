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
from datarobot.enums import DEFAULT_MAX_WAIT
from datarobot.models.api_object import APIObject
from datarobot.models.validators import feature_impact_trafaret
from datarobot.utils import deprecated, encode_utf8_if_py2, logger
from datarobot.utils.pagination import unpaginate
from datarobot.utils.waiters import wait_for_async_resolution

from .job import filter_feature_impact_result

logger = logger.get_logger(__name__)


class CustomInferenceImage(APIObject):
    """An image of a custom model.

    .. versionadded:: v2.21
    .. deprecated:: v2.23

    Attributes
    ----------
    id: str
        image id
    custom_model: dict
        dict with 2 keys: `id` and `name`,
        where `id` is the ID of the custom model
        and `name` is the model name
    custom_model_version: dict
        dict with 2 keys: `id` and `label`,
        where `id` is the ID of the custom model version
        and `label` is the version label
    execution_environment: dict
        dict with 2 keys: `id` and `name`,
        where `id` is the ID of the execution environment
        and `name` is the environment name
    execution_environment_version: dict
        dict with 2 keys: `id` and `label`,
        where `id` is the ID of the execution environment version
        and `label` is the version label
    latest_test: dict, optional
        dict with 3 keys: `id`, `status` and `completedAt`,
        where `id` is the ID of the latest test,
        `status` is the testing status
        and `completedAt` is ISO-8601 formatted timestamp of when the testing was completed
    """

    _path = "customInferenceImages/"
    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("custom_model"): t.Dict({t.Key("id"): String(), t.Key("name"): String()}),
            t.Key("custom_model_version"): t.Dict(
                {t.Key("id"): String(), t.Key("label"): String()}
            ),
            t.Key("execution_environment"): t.Dict(
                {t.Key("id"): String(), t.Key("name"): String()}
            ),
            t.Key("execution_environment_version"): t.Dict(
                {t.Key("id"): String(), t.Key("label"): String()}
            ),
            t.Key("latest_test", optional=True): t.Dict(
                {
                    t.Key("id"): String(),
                    t.Key("status"): String(),
                    t.Key("completed_at"): String(allow_blank=True),
                }
            ),
        }
    ).ignore_extra("*")

    def __init__(self, **kwargs):
        self._set_values(**kwargs)

    def __repr__(self):
        return encode_utf8_if_py2(u"{}({!r})".format(self.__class__.__name__, self.id))

    def _set_values(
        self,
        id,
        custom_model,
        custom_model_version,
        execution_environment,
        execution_environment_version,
        latest_test=None,
    ):
        self.id = id
        self.custom_model = custom_model
        self.custom_model_version = custom_model_version
        self.execution_environment = execution_environment
        self.execution_environment_version = execution_environment_version
        self.latest_test = latest_test

    @classmethod
    @deprecated(
        deprecated_since_version="v2.23",
        will_remove_version="v2.24",
        message="CustomModelImages have been deprecated. "
        "Please use CustomModelVersions with base_environment_id",
    )
    def create(
        cls, custom_model_id, custom_model_version_id, environment_id, environment_version_id=None,
    ):
        """Create a custom model image.

        .. versionadded:: v2.21

        Parameters
        ----------
        custom_model_id: str
            the id of the custom model
        custom_model_version_id: str
            the id of the custom model version
        environment_id: str
            the id of the execution environment
        environment_version_id: str, optional
            the id of the execution environment version

        Returns
        -------
        CustomInferenceImage
            created custom model image

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        payload = {
            "custom_model_id": custom_model_id,
            "custom_model_version_id": custom_model_version_id,
            "environment_id": environment_id,
            "environment_version_id": environment_version_id,
        }
        response = cls._client.post(cls._path, data=payload)
        return cls.from_server_data(response.json())

    @classmethod
    @deprecated(
        deprecated_since_version="v2.23",
        will_remove_version="v2.24",
        message="CustomModelImages have been deprecated. "
        "Please use CustomModelVersions with base_environment_id",
    )
    def list(
        cls,
        testing_status=None,
        custom_model_id=None,
        custom_model_version_id=None,
        environment_id=None,
        environment_version_id=None,
    ):
        """List custom model images.

        .. versionadded:: v2.21

        Parameters
        ----------
        testing_status: str, optional
            the testing status to filter results by
        custom_model_id: str, optional
            the id of the custom model
        custom_model_version_id: str, optional
            the id of the custom model version
        environment_id: str, optional
            the id of the execution environment
        environment_version_id: str, optional
            the id of the execution environment version

        Returns
        -------
        List[CustomModelImage]
            a list of custom model images

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        payload = {
            "testing_status": testing_status,
            "custom_model_id": custom_model_id,
            "custom_model_version_id": custom_model_version_id,
            "environment_id": environment_id,
            "environment_version_id": environment_version_id,
        }
        data = unpaginate(cls._path, payload, cls._client)
        return [cls.from_server_data(item) for item in data]

    @classmethod
    @deprecated(
        deprecated_since_version="v2.23",
        will_remove_version="v2.24",
        message="CustomModelImages have been deprecated. "
        "Please use CustomModelVersions with base_environment_id",
    )
    def get(cls, custom_model_image_id):
        """Get custom model image by id.

        .. versionadded:: v2.21

        Parameters
        ----------
        custom_model_image_id: str
            the id of the custom model image

        Returns
        -------
        CustomInferenceImage
            retrieved custom model image

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        path = "{}{}/".format(cls._path, custom_model_image_id)
        return cls.from_location(path)

    @deprecated(
        deprecated_since_version="v2.23",
        will_remove_version="v2.24",
        message="CustomModelImages have been deprecated. "
        "Please use CustomModelVersions with base_environment_id",
    )
    def refresh(self):
        """Update custom inference image with the latest data from server.

        .. versionadded:: v2.21

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        path = "{}{}/".format(self._path, self.id)

        response = self._client.get(path)

        data = response.json()
        self._set_values(**self._safe_data(data, do_recursive=True))

    @deprecated(
        deprecated_since_version="v2.23",
        will_remove_version="v2.24",
        message="CustomModelImages have been deprecated. "
        "Please use CustomModelVersions with base_environment_id",
    )
    def get_feature_impact(self, with_metadata=False):
        """Get custom model feature impact.

        .. versionadded:: v2.21

        Parameters
        ----------
        with_metadata : bool
            The flag indicating if the result should include the metadata as well.

        Returns
        -------
        feature_impacts : list of dict
           The feature impact data. Each item is a dict with the keys 'featureName',
           'impactNormalized', and 'impactUnnormalized', and 'redundantWith'.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        path = "{}{}/featureImpact/".format(self._path, self.id)
        data = self._client.get(path).json()
        data = feature_impact_trafaret.check(data)
        return filter_feature_impact_result(data, with_metadata=with_metadata)

    @deprecated(
        deprecated_since_version="v2.23",
        will_remove_version="v2.24",
        message="CustomModelImages have been deprecated. "
        "Please use CustomModelVersions with base_environment_id",
    )
    def calculate_feature_impact(self, max_wait=DEFAULT_MAX_WAIT):
        """Calculate custom model feature impact.

        .. versionadded:: v2.22

        Parameters
        ----------
        max_wait: int, optional
            max time to wait for feature impact calculation.
            If set to None - method will return without waiting.
            Defaults to 10 min

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        path = "{}{}/featureImpact/".format(self._path, self.id)
        response = self._client.post(path)

        if max_wait is not None:
            wait_for_async_resolution(self._client, response.headers["Location"], max_wait)
