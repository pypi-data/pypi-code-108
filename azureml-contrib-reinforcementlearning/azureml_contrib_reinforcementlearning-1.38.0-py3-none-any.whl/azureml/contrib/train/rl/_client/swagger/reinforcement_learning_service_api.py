# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from msrest.service_client import SDKClient
from msrest import Configuration, Serializer, Deserializer
from .version import VERSION
from .operations.reinforcement_learning_operations import ReinforcementLearningOperations
from . import models
from azureml._base_sdk_common.utils import get_retry_policy


class ReinforcementLearningServiceAPIConfiguration(Configuration):
    """Configuration for ReinforcementLearningServiceAPI
    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param credentials: Subscription credentials which uniquely identify
     client subscription.
    :type credentials: None
    :param str base_url: Service URL
    """

    def __init__(
            self, credentials, base_url=None):

        if credentials is None:
            raise ValueError("Parameter 'credentials' must not be None.")
        if not base_url:
            base_url = 'http://localhost'

        super(ReinforcementLearningServiceAPIConfiguration, self).__init__(base_url)

        self.add_user_agent('reinforcementlearningserviceapi/{}'.format(VERSION))

        self.credentials = credentials

        self.retry_policy.policy = get_retry_policy()


class ReinforcementLearningServiceAPI(SDKClient):
    """ReinforcementLearningServiceAPI

    :ivar config: Configuration for client.
    :vartype config: ReinforcementLearningServiceAPIConfiguration

    :ivar reinforcement_learning: ReinforcementLearning operations
    :vartype reinforcement_learning: swagger.operations.ReinforcementLearningOperations

    :param credentials: Subscription credentials which uniquely identify
     client subscription.
    :type credentials: None
    :param str base_url: Service URL
    """

    def __init__(
            self, credentials, base_url=None):

        self.config = ReinforcementLearningServiceAPIConfiguration(credentials, base_url)
        super(ReinforcementLearningServiceAPI, self).__init__(self.config.credentials, self.config)

        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        self.api_version = 'v1.0'
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)

        self.reinforcement_learning = ReinforcementLearningOperations(
            self._client, self.config, self._serialize, self._deserialize)
