"""
mlops library for reporting statistics.

MLOps library can be used to report ML metrics to DataRobot MLOps for centralized monitoring.
"""
#  Copyright (c) 2019 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2021.
#
#  DataRobot, Inc. Confidential.
#  This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.
#  The copyright notice above does not evidence any actual or intended publication of
#  such source code.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.

import atexit
from enum import Enum
import os


from datarobot.mlops.agent import Agent
from datarobot.mlops.event import Event
from datarobot.mlops.model import Model
from datarobot.mlops.common import config
from datarobot.mlops.common.config import ConfigConstants
from datarobot.mlops.common.enums import SpoolerType
from datarobot.mlops.common.exception import DRAlreadyInitialized, DRApiException
from datarobot.mlops.constants import Constants


class MLOpsLibMode(Enum):
    EMBEDED_AGENT_MODE = 1
    DAEMON_AGENT_MODE = 2


class MLOps:
    def __init__(self):
        self._initialized = False
        self._model = None
        self._libmode = MLOpsLibMode.DAEMON_AGENT_MODE
        self._agent = None
        self._default_deployment_id = None
        self._default_model_id = None

    @staticmethod
    def get_version():
        return Constants.MLOPS_VERSION

    def set_deployment_id(self, deployment_id):
        """
        Set the deployment ID of the deployment for which the reporting will be targeted.

        :param deployment_id: the unique deployment ID
        :type deployment_id: str
        :returns: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(deployment_id, "deployment_id")
        config.set_config_safely(ConfigConstants.DEPLOYMENT_ID, deployment_id)
        return self

    def set_model_id(self, model_id):
        """
        The model ID for which the reporting information is related.

        :param model_id: a unique model ID that identifies the given model
        :type model_id: str
        :returns: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(model_id, "model_id")
        config.set_config_safely(ConfigConstants.MODEL_ID, model_id)
        return self

    def set_async_reporting(self, async_reporting=True):
        """
        Set mode of reporting metrics. Asynchronous mode buffers the reported metrics in memory
        while a separate process sends them to the spooler.
        :param async_reporting: whether to report asynchronously or not
        :return:
        """
        config.set_config_safely(ConfigConstants.ASYNC_REPORTING, async_reporting)
        return self

    def set_no_spooler(self):
        """
        Set no spooler. This disables MLOps reporting.
        :returns: the MLOps instance
        :rtype: MLOps
        """
        config.set_config_safely(ConfigConstants.SPOOLER_TYPE, SpoolerType.NONE.name)
        return self

    def set_stdout_spooler(self):
        """
        Use STDOUT in place of a spooler. Any reported metrics will go to stdout instead of
        being routed to the agent.
        :returns: the MLOps instance
        :rtype: MLOps
        """
        config.set_config_safely(ConfigConstants.SPOOLER_TYPE, SpoolerType.STDOUT.name)
        return self

    def set_filesystem_spooler(self, directory):
        """
        Set the spooler type to 'Filesystem' and set its output to the directory specified.

        :param directory: local filesystem directory path
        :type directory: str
        :returns: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(directory, "directory")
        config.set_config_safely(ConfigConstants.SPOOLER_TYPE, SpoolerType.FILESYSTEM.name)
        config.set_config_safely(ConfigConstants.FILESYSTEM_DIRECTORY, directory)
        return self

    def set_pubsub_spooler(self, project_id, topic_name):
        """
        Set the spooler type to PubSub. Note that PubSub only supports Python3.

        :param project_id: GCP PubSub project id. This should be the full project id path.
        :type project_id: str
        :param topic_name: GCP PubSub topic name. This should be name of the topic within the
          project, not the full topic path that includes the project id.
        :type topic_name: str
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(project_id, "project_id")
        self._validate_input_string(topic_name, "topic_name")
        config.set_config_safely(ConfigConstants.SPOOLER_TYPE, SpoolerType.PUBSUB.name)
        config.set_config_safely(ConfigConstants.PUBSUB_PROJECT_ID, project_id)
        config.set_config_safely(ConfigConstants.PUBSUB_TOPIC_NAME, topic_name)
        return self

    def set_sqs_spooler(self, queue):
        """
        Set the spooler type to SQS.

        :param queue: AWS SQS queue name or queue URL. If the parameter begins with "http", it is
          assumed to be the queue URL. Otherwise, it is assumed to be the queue name.
        :type queue: str
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(queue, "queue_url")
        if queue.startswith("http"):
            config.set_config_safely(ConfigConstants.SQS_QUEUE_URL, queue)
        else:
            config.set_config_safely(ConfigConstants.SQS_QUEUE_NAME, queue)

        config.set_config_safely(ConfigConstants.SPOOLER_TYPE, SpoolerType.SQS.name)
        return self

    def set_rabbitmq_spooler(
            self,
            queue_url,
            queue_name,
            ca_certificate_path=None,
            certificate_path=None,
            keyfile_path=None,
            tls_version=None,
    ):
        """
        Set the spooler type to RABBITMQ.

        :param queue_url: RabbitMQ queue URL
        :type queue_url: str
        :param queue_name: RabbitMQ queue name
        :type queue_name: str
        :param ca_certificate_path: the path for CA certificate (only used for mTLS connections)
        :type ca_certificate_path: str
        :param certificate_path: the path for client certificate (only used for mTLS connections)
        :type certificate_path: str
        :param keyfile_path: the client key file path (only used for mTLS connections)
        :type keyfile_path: str
        :param tls_version: the tls client version (only used for mTLS connections)
        :type tls_version: str
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(queue_url, "queue_url")
        self._validate_input_string(queue_name, "queue_name")
        config.set_config_safely(ConfigConstants.SPOOLER_TYPE, SpoolerType.RABBITMQ.name)
        config.set_config_safely(ConfigConstants.RABBITMQ_QUEUE_URL, queue_url)
        config.set_config_safely(ConfigConstants.RABBITMQ_QUEUE_NAME, queue_name)
        if ca_certificate_path:
            config.set_config_safely(
                ConfigConstants.RABBITMQ_SSL_CA_CERTIFICATE_PATH, ca_certificate_path
            )
        if certificate_path:
            config.set_config_safely(
                ConfigConstants.RABBITMQ_SSL_CERTIFICATE_PATH, certificate_path
            )
        if keyfile_path:
            config.set_config_safely(ConfigConstants.RABBITMQ_SSL_KEYFILE_PATH, keyfile_path)
        if tls_version:
            config.set_config_safely(ConfigConstants.RABBITMQ_SSL_TLS_VERSION, tls_version)

        return self

    def set_kafka_spooler(self, topic_name, bootstrap_servers=None):
        """
        Set the spooler type to KAFKA.

        :param topic_name: Kafka topic name
        :type topic_name: str
        :param bootstrap_servers: Optional, 'host[:port]' string (or list of 'host[:port]' strings)
            that the consumer should contact to bootstrap initial cluster metadata.
        :type bootstrap_servers: str
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(topic_name, "topic_name")
        config.set_config_safely(ConfigConstants.SPOOLER_TYPE, SpoolerType.KAFKA.name)
        config.set_config_safely(ConfigConstants.KAFKA_TOPIC_NAME, topic_name)

        if bootstrap_servers:
            config.set_config_safely(
                ConfigConstants.KAFKA_BOOTSTRAP_SERVERS, bootstrap_servers
            )

        return self

    def set_feature_data_rows_in_one_message(self, rows):
        """
        Set how many feature data rows will be in one message.
        Use for channels which have a size limit for each message.
        :param rows: how many feature data rows will be in one message
        :type rows: int
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_positive_num(rows, "feature_data_rows_in_one_message")
        config.set_config_safely(ConfigConstants.FEATURE_DATA_ROWS_IN_ONE_MESSAGE, rows)
        return self

    def set_channel_config(self, channel_config):
        """
        List of settings in a semicolon separated string

        :param channel_config: key=value params separated by semicolon
        :type channel_config: str
        :return: MLOps
        """
        config.set_channel_config_from_str(channel_config)
        return self

    def agent(self, mlops_service_url=None, mlops_api_token=None, agent_jar_path=None,
              path_prefix=None, verify_ssl=True):
        """
        Setup agent in an "embedded" mode, MLOps SDK will transparently manage to configure and run
        the agent.  When this mode is enabled, the agent service should not be started separately.

        :param mlops_service_url: Required, URL of the DataRobot MLOps service
        :type mlops_service_url: str
        :param mlops_api_token: Required, DataRobot MLOps API token
        :type mlops_api_token: str
        :param agent_jar_path: Optional, default - uses JAR file included in the pip package
        :type agent_jar_path: str
        :param path_prefix: Optional, Path prefix to use to store spool / logs of agent, default
            a temporary directory
        :type path_prefix: str
        :param verify_ssl: Optional, default - verify SSL certificate, if False then skip ssl
                        verification
        :type verify_ssl: bool
        :returns: the MLOps instance
        :rtype: MLOps
        """
        self._agent = Agent(mlops_service_url,
                            mlops_api_token,
                            agent_jar_path,
                            path_prefix,
                            verify_ssl)
        self._libmode = MLOpsLibMode.EMBEDED_AGENT_MODE

        # register call back for cleanup
        atexit.register(self._cleanup)

        return self

    def init(self):
        """
        Finalize the initialization of the MLOps instance. Reporting can be done only
        after calling this method.

        :raises: DRAlreadyInitialized if MLOps library is already initialized.
        :returns: the MLOps instance
        :rtype: MLOps
        """
        if self._initialized:
            raise DRAlreadyInitialized("MLOps library already initialized.")

        if self._libmode is MLOpsLibMode.EMBEDED_AGENT_MODE and self._agent is not None:
            self._agent.validate_and_init_config()
            self._agent.start()
            self._agent.connect_to_gateway()

        self._default_deployment_id = \
            config.get_config_default(ConfigConstants.DEPLOYMENT_ID, None)
        self._default_model_id = config.get_config_default(ConfigConstants.MODEL_ID, None)

        self._model = Model()
        self._initialized = True
        return self

    def shutdown(self, timeout_sec=0):
        """
        Safe MLOps shutdown.
        Ensures that all metrics are processed and forwarded to the configured output.
        """
        if self._libmode == MLOpsLibMode.EMBEDED_AGENT_MODE and self._agent is not None:
            submitted_stats = self._model.get_stats_counters()
            self._agent.wait_for_stats_sent_to_mmm(submitted_stats, timeout_sec)
            self._agent.stop()
            self._agent = None

        config.clear_config()
        self._model.shutdown(timeout_sec=timeout_sec)
        del self._model
        self._initialized = False

        return

    def _cleanup(self):
        if self._agent is not None:
            self._agent.cleanup()

    def _validate(self):
        if not self._initialized:
            raise DRApiException("MLOps library is not initialized."
                                 "Make sure to call `init()` function.")

    @staticmethod
    def _validate_input_positive_num(num, field_name):
        if num <= 0:
            raise DRApiException(field_name + " needs to be a positive number.")

    @staticmethod
    def _validate_input_string(string, field_name):
        if not string:
            raise DRApiException(field_name + " is empty.")

    def _get_id(self, id_param, config_constant):
        _id = id_param

        if _id is None:
            if config_constant == ConfigConstants.DEPLOYMENT_ID:
                _id = self._default_deployment_id
            elif config_constant == ConfigConstants.MODEL_ID:
                _id = self._default_model_id
            if _id is None:
                raise DRApiException(
                    "Config key '{}' not found. Export as an environment variable "
                    "or set programmatically."
                    .format(config_constant.name))
        return _id

    def report_deployment_stats(self, num_predictions, execution_time_ms,
                                deployment_id=None, model_id=None):
        """
        Report the number of predictions and execution time
        to DataRobot MLOps.

        :param num_predictions: number of predictions
        :type num_predictions: int
        :param execution_time_ms: time in milliseconds
        :type execution_time_ms: float
        :param deployment_id: the deployment for these metrics
        :type deployment_id: str
        :param model_id: the model for these metrics
        :type model_id: str
        :raises: DRApiException if parameters have the wrong type
        :returns: report status - True on success, False otherwise.
        :rtype: bool
        """
        self._validate()
        if not isinstance(num_predictions, int):
            raise DRApiException("num_predictions must be an integer.")
        if not isinstance(execution_time_ms, int) and not isinstance(execution_time_ms, float):
            raise DRApiException("execution_time_ms must be a float.")
        _deployment_id = self._get_id(deployment_id, ConfigConstants.DEPLOYMENT_ID)
        _model_id = self._get_id(model_id, ConfigConstants.MODEL_ID)
        return self._model.report_deployment_stats(_deployment_id, _model_id,
                                                   num_predictions, execution_time_ms)

    def report_predictions_data(
            self, features_df=None, predictions=None, association_ids=None, class_names=None,
            deployment_id=None, model_id=None):
        """
        Report features and predictions to DataRobot MLOps for tracking and monitoring.

        :param features_df: Dataframe containing features to track and monitor.  All the features
            in the dataframe are reported.  Omit the features from the dataframe that do not need
            reporting.
        :type features_df: pandas dataframe
        :param predictions: List of predictions.  For Regression deployments, this is a 1D list
            containing prediction values.  For Classification deployments, this is a 2D list, in
            which the inner list is the list of probabilities for each class type
            Regression Predictions: e.g. [1, 2, 4, 3, 2]
            Binary Classification: e.g. [[0.2, 0.8], [0.3, 0.7]].
        :type predictions: list

        At least one of `features` or `predictions` must be specified.

        :param association_ids: an optional list of association IDs corresponding to each
            prediction. Used for accuracy calculations.  Association IDs have to be unique for each
            prediction to report.  The number of `predictions` should be equal to number of
            `association_ids` in the list
        :type association_ids: list
        :param class_names: names of predicted classes, e.g. ["class1", "class2", "class3"].  For
            classification deployments, class names must be in the same order as the prediction
            probabilities reported. If not specified, this prediction order defaults to the order
            of the class names on the deployment.
            This argument is ignored for Regression deployments.
        :type class_names: list
        :param deployment_id: the deployment for these metrics
        :type deployment_id: str
        :param model_id: the model for these metrics
        :type model_id: str
        :returns: report status - True on success, False otherwise.
        :rtype: bool
        """
        self._validate()
        _deployment_id = self._get_id(deployment_id, ConfigConstants.DEPLOYMENT_ID)
        _model_id = self._get_id(model_id, ConfigConstants.MODEL_ID)
        return self._model.report_predictions_data(_deployment_id, _model_id,
                                                   features_df, predictions,
                                                   association_ids, class_names)

    def report_event(self, event, deployment_id=None):
        # type: (Event) -> None
        """
        Report an external event to DataRobot MLOps.

        :param event: an Event object specifying type, message, and other attributes
        :type: event: Event
        :param deployment_id: the deployment for these metrics
        :type deployment_id: str
        :returns status of submission to queue - True on success, False otherwise.
        :rtype: bool
        """
        self._validate()
        _deployment_id = self._get_id(deployment_id, ConfigConstants.DEPLOYMENT_ID)
        return self._model.report_event(_deployment_id, None, event)

    # ---------------- Pickling MLOps -----------------------------
    def __getstate__(self):
        """
        Simply store the config parameters for this MLOps object into a dictionary.  Make sure
        even the environment variables are saved.  This is sufficient information to reconstruct
        the MLOps object

        In order to serialize the MLOps object, we are not going to verify if the current config
        is valid or not.  We will simply serialize the current state
        :return: dictionary containing MLOps config
        """
        return config.dump_config()

    def __setstate__(self, state):
        """
        Build the MLOps object using the config.  Simply export all the keys in the 'state'
        as environment variables and call init().  As long as all the config values are exported as
        environment variables, MLOps library will use it correctly for its operation.
        :param state: Configuration dictionary
        """
        self.__init__()
        for key in state:
            os.environ[key] = str(state[key])

        self.init()
