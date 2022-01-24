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
import time

import trafaret as t

from datarobot._compat import Int, String
from datarobot.enums import CUSTOM_MODEL_IMAGE_TYPE, DEFAULT_MAX_WAIT, NETWORK_EGRESS_POLICY
from datarobot.errors import AsyncProcessUnsuccessfulError
from datarobot.models.api_object import APIObject
from datarobot.utils import deprecation_warning, encode_utf8_if_py2
from datarobot.utils.pagination import unpaginate
from datarobot.utils.waiters import wait_for_async_resolution


class CustomModelTest(APIObject):
    """An custom model test.

    .. versionadded:: v2.21

    Attributes
    ----------
    id: str
        test id
    custom_model_image_id: str
        id of a custom model image
    image_type: str
        the type of the image, either CUSTOM_MODEL_IMAGE_TYPE.CUSTOM_MODEL_IMAGE if the testing
        attempt is using a CustomModelImage as its model or
        CUSTOM_MODEL_IMAGE_TYPE.CUSTOM_MODEL_VERSION if the testing attempt is
        using a CustomModelVersion with dependency management
    overall_status: str
        a string representing testing status.
        Status can be
        - 'not_tested': the check not run
        - 'failed': the check failed
        - 'succeeded': the check succeeded
        - 'warning': the check resulted in a warning, or in non-critical failure
        - 'in_progress': the check is in progress
    detailed_status: dict
        detailed testing status - maps the testing types to their status and message.
        The keys of the dict are one of 'errorCheck', 'nullValueImputation',
        'longRunningService', 'sideEffects'.
        The values are dict with 'message' and 'status' keys.
    created_by: str
        a user who created a test
    dataset_id: str, optional
        id of a dataset used for testing
    dataset_version_id: str, optional
        id of a dataset version used for testing
    completed_at: str, optional
        ISO-8601 formatted timestamp of when the test has completed
    created_at: str, optional
        ISO-8601 formatted timestamp of when the version was created
    network_egress_policy: datarobot.NETWORK_EGRESS_POLICY, optional
        Determines whether the given custom model is isolated, or can access the public network.
        Can be either 'datarobot.NONE' or 'datarobot.PUBLIC'
    maximum_memory: int, optional
        The maximum memory that might be allocated by the custom-model.
        If exceeded, the custom-model will be killed by k8s
    replicas: int, optional
        A fixed number of replicas that will be deployed in the cluster
    """

    _path = "customModelTests/"
    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("custom_model_image_id"): String(),
            t.Key("image_type"): t.Enum(*CUSTOM_MODEL_IMAGE_TYPE.ALL),
            t.Key("overall_status"): String(),
            t.Key("testing_status")
            >> "detailed_status": t.Dict(
                {
                    t.Key(test_type): t.Dict(
                        {t.Key("status"): String(), t.Key("message"): String(allow_blank=True)}
                    ).allow_extra("*")
                    for test_type in [
                        "error_check",
                        "null_value_imputation",
                        "long_running_service",
                        "side_effects",
                    ]
                }
            ).allow_extra("*"),
            t.Key("created_by"): String(),
            t.Key("dataset_id", optional=True): String(),
            t.Key("dataset_version_id", optional=True): String(),
            t.Key("completed_at", optional=True): String(allow_blank=True),
            t.Key("created", optional=True) >> "created_at": String(),
            t.Key("network_egress_policy", optional=True): t.Enum(*NETWORK_EGRESS_POLICY.ALL),
            t.Key("maximum_memory", optional=True): Int(),
            t.Key("replicas", optional=True): Int(),
        }
    ).ignore_extra("*")

    def __init__(self, **kwargs):
        self._set_values(**kwargs)

    def __repr__(self):
        return encode_utf8_if_py2(u"{}({!r})".format(self.__class__.__name__, self.id))

    def _set_values(
        self,
        id,
        custom_model_image_id,
        image_type,
        overall_status,
        detailed_status,
        created_by,
        dataset_id=None,
        dataset_version_id=None,
        completed_at=None,
        created_at=None,
        network_egress_policy=None,
        maximum_memory=None,
        replicas=None,
    ):
        self.id = id
        self.dataset_id = dataset_id
        self.dataset_version_id = dataset_version_id
        self.custom_model_image_id = custom_model_image_id
        self.image_type = image_type
        self.overall_status = overall_status
        self.detailed_status = detailed_status
        self.created_by = created_by
        self.completed_at = completed_at
        self.created_at = created_at
        self.network_egress_policy = network_egress_policy
        self.maximum_memory = maximum_memory
        self.replicas = replicas

    @classmethod
    def create(
        cls,
        custom_model_id,
        custom_model_version_id,
        dataset_id=None,
        environment_id=None,
        environment_version_id=None,
        max_wait=DEFAULT_MAX_WAIT,
        network_egress_policy=None,
        maximum_memory=None,
        replicas=None,
    ):
        """Create and start a custom model test.

        .. versionadded:: v2.21

        Parameters
        ----------
        custom_model_id: str
            the id of the custom model
        custom_model_version_id: str
            the id of the custom model version
        dataset_id: str, optional
            The id of the testing dataset for non-unstructured custom models.
            Ignored and not required for unstructured models.
        environment_id: str, optional
            the id of the execution environment.
            If specified, the environment will be used as is; if the custom model version
            has dependencies, they will not be installed at runtime. This has been deprecated in
            favor of using the base environment of the custom model version itself
        environment_version_id: str, optional
            the id of the execution environment version. This has been deprecated in
            favor of using the base environment of the custom model version itself
        max_wait: int, optional
            max time to wait for a test completion.
            If set to None - method will return without waiting.
        network_egress_policy: datarobot.NETWORK_EGRESS_POLICY, optional
            Determines whether the given custom model is isolated, or can access the public network.
            Can be either 'datarobot.NONE' or 'datarobot.PUBLIC'
        maximum_memory: int, optional
            The maximum memory that might be allocated by the custom-model.
            If exceeded, the custom-model will be killed by k8s
        replicas: int, optional
            A fixed number of replicas that will be deployed in the cluster

        Returns
        -------
        CustomModelTest
            created custom model test

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
        }

        if environment_id or environment_version_id:
            deprecation_warning(
                "Specifying an environment to use for testing has been deprecated",
                deprecated_since_version="v2.23",
                will_remove_version="v2.24",
            )

        if dataset_id:
            payload["dataset_id"] = dataset_id
        if environment_id:
            payload["environment_id"] = environment_id
        if environment_version_id:
            payload["environment_version_id"] = environment_version_id
        if network_egress_policy:
            payload["network_egress_policy"] = network_egress_policy
        if maximum_memory:
            payload["maximum_memory"] = maximum_memory
        if replicas:
            payload["replicas"] = replicas

        response = cls._client.post(cls._path, data=payload)

        # at this point custom model test is already created
        custom_model_test = cls.list(custom_model_id)[0]

        if max_wait is None:
            # return without waiting for the test to finish
            return custom_model_test
        else:
            try:
                # wait for the test to finish
                custom_model_test_loc = wait_for_async_resolution(
                    cls._client, response.headers["Location"], max_wait
                )
                return cls.from_location(custom_model_test_loc)
            except AsyncProcessUnsuccessfulError:
                # if the job was aborted server sends appropriate status and
                # `wait_for_async_resolution` raises exception,
                # but the test has been already created, and contains error log,
                # so return the test

                # the test needs some time to update its state
                max_state_wait = 10
                custom_model_test.refresh()

                start_time = time.time()
                while custom_model_test.overall_status == "in_progress":
                    if time.time() >= start_time + max_state_wait:
                        raise
                    time.sleep(1)
                    custom_model_test.refresh()

                return custom_model_test

    @classmethod
    def list(cls, custom_model_id):
        """List custom model tests.

        .. versionadded:: v2.21

        Parameters
        ----------
        custom_model_id: str
            the id of the custom model

        Returns
        -------
        List[CustomModelTest]
            a list of custom model tests

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        payload = {"custom_model_id": custom_model_id}
        data = unpaginate(cls._path, payload, cls._client)
        return [cls.from_server_data(item) for item in data]

    @classmethod
    def get(cls, custom_model_test_id):
        """Get custom model test by id.

        .. versionadded:: v2.21

        Parameters
        ----------
        custom_model_test_id: str
            the id of the custom model test

        Returns
        -------
        CustomModelTest
            retrieved custom model test

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        path = "{}{}/".format(cls._path, custom_model_test_id)
        return cls.from_location(path)

    def get_log(self):
        """Get log of a custom model test.

        .. versionadded:: v2.21

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        path = "{}{}/log/".format(self._path, self.id)
        return self._client.get(path).text

    def get_log_tail(self):
        """Get log tail of a custom model test.

        .. versionadded:: v2.21

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        path = "{}{}/tail/".format(self._path, self.id)
        return self._client.get(path).text

    def cancel(self):
        """Cancel custom model test that is in progress.

        .. versionadded:: v2.21

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        path = "{}{}/".format(self._path, self.id)
        self._client.delete(path)

    def refresh(self):
        """Update custom model test with the latest data from server.

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
