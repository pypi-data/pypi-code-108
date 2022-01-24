#  Copyright (c) 2020 DataRobot, Inc. and its affiliates. All rights reserved.
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

import json
import logging
import os
from py4j.java_gateway import GatewayParameters, CallbackServerParameters
from py4j.java_gateway import JavaGateway
import re
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import yaml

from datarobot.mlops.common import config
from datarobot.mlops.common.config import ConfigConstants
from datarobot.mlops.common.enums import SpoolerType
from datarobot.mlops.common.exception import DRApiException


API_TOKEN = "apiToken"
MLOPS_URL = "mlopsUrl"
VERIFY_SSL = "verifySSL"
STAT_PATH = "statsPath"
SPOOLER_DIR = "spoolDirectoryPath"
CHANNEL_CONF = "channelConfigs"

AGENT_CONFIG_FILE = "agent.yaml"
LOG4J2_PROPERTIES_FILE = "mlops.log4j2.properties"

log_level = os.environ.get("MLOPS_LIB_LOGLEVEL", "INFO").upper()
logger = logging.getLogger(__name__)

AGENT_ENTRY_POINT_CLASS = "com.datarobot.mlops.agent.GatewayEntryPoint"
MLOPS_URL_DEFAULT = "https://app.datarobot.com/"
CLEAN_SHUTDOWN_MESSAGE = "Clean Shutdown"


class Agent:
    def __init__(self, datarobot_url, token,
                 agent_jar_path=None, path_prefix=None, verify_ssl=True):
        if datarobot_url is None:
            raise DRApiException("Missing DataRobot URL")
        if token is None:
            raise DRApiException("Missing User token")
        self._datarobot_server_url = datarobot_url
        self._user_token = token
        self._verify_ssl = verify_ssl
        self._agent_jar_path = agent_jar_path
        self._path_prefix = path_prefix

        self._config_path = None
        self._agent_config = None
        self._log4j2_conf_path = None
        self._java_path = None
        # py4j default port
        self._py4j_port = 25333

        self._cleanup_path = False
        self._process = None
        self._process_args = ""

        self._gateway = None
        self._agent_py4j_instance = None
        self._conf_host_path = os.path.join(sys.prefix, "share", "mlops")
        self._spooler_conf = None

    def validate_and_init_config(self):
        self._set_path_prefix()

        # load default configuration from pip installed YAML
        self._set_config_path()
        self._validate_and_set_jar_path()
        self._validate_and_set_log4j2_config()
        self._validate_and_set_java_path()

        with open(self._config_path) as agent_configuration:
            self._agent_config = yaml.safe_load(agent_configuration)
            if not self._agent_config:
                raise Exception("Error: Agent configuration failed")

        self._validate_and_set_spooler()
        self._update_agent_config()
        self._init_process()

    def _set_path_prefix(self):
        if self._path_prefix is None:
            self._path_prefix = tempfile.mkdtemp()
            logger.info("Created temporary directory {}".format(self._path_prefix))
            self._cleanup_path = True

    def _validate_and_set_jar_path(self):
        """
        Find the path to the Tracking-Agent JAR file
        :return:
        """
        if self._agent_jar_path:
            if not os.path.isfile(self._agent_jar_path):
                raise DRApiException("Invalid agent jar path specified: " + self._agent_jar_path)
        else:
            # get Agent JAR from the virtualenv
            # find JAR file with prefix agent, suffix jar
            jar_finder = (os.path.join(self._conf_host_path, lfile)
                          for lfile in os.listdir(self._conf_host_path)
                          if os.path.isfile(os.path.join(self._conf_host_path, lfile))
                          and "agent-" in lfile and ".jar" in lfile)
            self._agent_jar_path = next(jar_finder, None)
            if self._agent_jar_path is None:
                raise Exception("Error: MLOps Agent JAR file not found")

    def _set_config_path(self):
        # get Agent config from install in the virtualenv
        self._config_path = os.path.join(self._conf_host_path, AGENT_CONFIG_FILE)
        if not os.path.isfile(self._config_path):
            raise Exception("Error: Agent configuration file not found")

    def _validate_and_set_log4j2_config(self):
        # get log4j2 config from install in the virtualenv
        self._log4j2_conf_path = os.path.join(self._conf_host_path, LOG4J2_PROPERTIES_FILE)
        if not os.path.isfile(self._log4j2_conf_path):
            raise Exception("Error: log4j2 configuration file not found")

    def _validate_and_set_java_path(self):
        output = subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT)
        if output is None:
            raise Exception("Failed to check Java version on the system")

        for line in output.decode("utf-8").split("\n"):
            # output example: openjdk version "11.0.10" 2021-01-19
            # or: openjdk version "1.8.0_222"
            if "version" in line:
                versions = re.findall(r"\"(.+?)\"", line)
                if len(versions) < 1:
                    raise Exception("Unsupported Java: '" + line + "'")
                try:
                    major = int(versions[0].split(".")[0])
                    minor = int(versions[0].split(".")[1])
                except (ValueError, IndexError):
                    major = 0
                if major != 11 and major != 8 and (major != 1 or minor != 8):
                    raise Exception("Unsupported Java version (expected 8 or 11): " + versions[0])

        path = subprocess.check_output(["which", "java"], stderr=subprocess.STDOUT)
        if path is None:
            raise Exception("Could not find Java installation path on the machine")

        self._java_path = path.decode("utf-8").split("\n")[0]

    def _validate_and_set_spooler(self):
        spooler_type = config.get_config_default(ConfigConstants.SPOOLER_TYPE, None)
        if spooler_type is None or spooler_type == SpoolerType.FILESYSTEM.name:
            self._spooler_conf, spooler_dir_path = self._get_fs_spool_channel_conf()
            if spooler_type is None:
                # export environment variables for the library
                os.environ[ConfigConstants.FILESYSTEM_DIRECTORY.name] = spooler_dir_path
                os.environ[ConfigConstants.SPOOLER_TYPE.name] = SpoolerType.FILESYSTEM.name
        elif spooler_type == SpoolerType.RABBITMQ.name:
            self._spooler_conf = self._get_rabbitmq_spool_channel_conf()
        elif spooler_type == SpoolerType.SQS.name:
            self._spooler_conf = self._get_sqs_spool_channel_conf()
        elif spooler_type == SpoolerType.PUBSUB.name:
            self._spooler_conf = self._get_pubsub_spool_channel_conf()
        elif spooler_type == SpoolerType.KAFKA.name:
            self._spooler_conf = self._get_kafka_spool_channel_conf()
        else:
            raise Exception("Embedded Agent mode supports only file spooler channel"
                            " - {} was detected in configuration".format(spooler_type))

    def _get_fs_spool_channel_conf(self):
        spooler_dir_path = config.get_config_default(ConfigConstants.FILESYSTEM_DIRECTORY, None)
        if not spooler_dir_path:
            # We want to at least support file system spooler if nothing is configured
            spooler_dir_path = os.path.join(self._path_prefix, "spool")
        if not os.path.exists(spooler_dir_path):
            os.makedirs(spooler_dir_path)

        return {
                   "type": "FS_SPOOL",
                   "details": {
                       "name": "default_fs_spool",
                       SPOOLER_DIR: spooler_dir_path
                   }
               }, spooler_dir_path

    def _get_rabbitmq_spool_channel_conf(self):
        rabbitmq_url = config.get_config_default(ConfigConstants.RABBITMQ_QUEUE_URL, None)
        if not rabbitmq_url:
            raise Exception(
                "Missing RabbitMQ queue URL in environment variable, '{}'".format(
                    ConfigConstants.RABBITMQ_QUEUE_URL.name
                )
            )

        rabbitmq_name = config.get_config_default(ConfigConstants.RABBITMQ_QUEUE_NAME, None)
        if not rabbitmq_name:
            raise Exception(
                "Missing RabbitMQ queue name in environment variable, '{}'".format(
                    ConfigConstants.RABBITMQ_QUEUE_NAME.name
                )
            )

        return {
                   "type": "RABBITMQ_SPOOL",
                   "details": {
                       "name": "default_rabbitmq_spool",
                       "rabbitmq_queue_name": rabbitmq_name,
                       "rabbitmq_queue_url": rabbitmq_url,
                   }
               }

    def _get_sqs_spool_channel_conf(self):
        sqs_url = config.get_config_default(ConfigConstants.SQS_QUEUE_URL, None)
        if not sqs_url:
            raise Exception(
                "Missing SQS queue URL in environment variable, '{}'".format(
                    ConfigConstants.SQS_QUEUE_URL.name
                )
            )

        sqs_name = config.get_config_default(ConfigConstants.SQS_QUEUE_NAME, None)
        if not sqs_name:
            raise Exception(
                "Missing RabbitMQ queue name in environment variable, '{}'".format(
                    ConfigConstants.SQS_QUEUE_NAME.name
                )
            )

        return {
                   "type": "SQS_SPOOL",
                   "details": {
                       "name": "default_sqs_spool",
                       "queueName": sqs_name,
                       "queueUrl": sqs_url,
                   }
               }

    def _get_pubsub_spool_channel_conf(self):
        pubsub_project_id = config.get_config_default(ConfigConstants.PUBSUB_PROJECT_ID, None)
        if not pubsub_project_id:
            raise Exception(
                "Missing PubSub Project ID in environment variable, '{}'".format(
                    ConfigConstants.PUBSUB_PROJECT_ID.name
                )
            )

        pubsub_topic_name = config.get_config_default(ConfigConstants.PUBSUB_TOPIC_NAME, None)
        if not pubsub_topic_name:
            raise Exception(
                "Missing PubSub Topic name in environment variable, '{}'".format(
                    ConfigConstants.PUBSUB_TOPIC_NAME.name
                )
            )

        return {
                   "type": "PUBSUB_SPOOL",
                   "details": {
                       "name": "default_pubsub_spool",
                       "projectId": pubsub_project_id,
                       "topicName": pubsub_topic_name,
                   }
               }

    def _get_kafka_spool_channel_conf(self):
        kafka_topic_name = config.get_config_default(ConfigConstants.KAFKA_TOPIC_NAME, None)
        if not kafka_topic_name:
            raise Exception(
                "Missing Kafka Topic name in environment variable, '{}'".format(
                    ConfigConstants.KAFKA_TOPIC_NAME.name
                )
            )

        return {
                   "type": "KAFKA_SPOOL",
                   "details": {
                       "name": "default_kafka_spool",
                       "topicName": kafka_topic_name,
                   }
               }

    def _update_agent_config(self):
        """
        Utility function to update the Agent Configuration using
        the provided overrides by the user
        :return:
        """
        self._agent_config[MLOPS_URL] = self._datarobot_server_url
        self._agent_config[API_TOKEN] = self._user_token
        self._agent_config[VERIFY_SSL] = self._verify_ssl

        stat_path = self._agent_config.get(STAT_PATH)
        if stat_path is not None and not os.path.isabs(stat_path):
            if stat_path.startswith("./"):
                stat_path = stat_path.replace(".", self._path_prefix, 1)
                self._agent_config[STAT_PATH] = stat_path

        channel_list = [self._spooler_conf]

        self._agent_config[CHANNEL_CONF] = channel_list

    def _init_process(self):
        self._cmdline = self._java_path + \
                        " -Dlog4j.configurationFile=file:" + "".join(self._log4j2_conf_path) + \
                        " -cp " + "".join(self._agent_jar_path) + \
                        " " + AGENT_ENTRY_POINT_CLASS
        # Log file location is as dictated by "property.filename" in log4j2 config, typically
        # "./logs/mlops.agent.log" unless changed

    def start(self, force_flag=False):
        if force_flag and self._process:
            self._process.kill()
            self._process = None
        if not self._process:
            logger.info("Starting agent, Agent log: ./logs/mlops.agent.log")
            logger.debug("Agent command line: " + self._cmdline)
            self._process_args = shlex.split(self._cmdline)
            self._process = subprocess.Popen(
                self._process_args,
                stdin=None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=True
            )
        else:
            logger.info(
                "Existing agent subprocess {} processID: {}".format(
                    self._process_args, self._process.pid
                )
            )

    def _ensure_gateway_server_is_up_and_running(self, port, timeout=120):
        gateway_running = False
        timeout = min(timeout, 120)
        while timeout > 0:
            time.sleep(1)
            try:
                int_port = int(port)
                addr = "127.0.0.1"
                logger.info("Connecting to java process: addr: {} port: {}".format(addr, int_port))
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((addr, int_port))
                s.shutdown(socket.SHUT_RDWR)
                gateway_running = True
                logger.info("Gateway is up and running")
                break
            except Exception as e:
                timeout -= 1
                logger.info(
                    "Got error connecting to gateway: timeout {} error: {}".format(timeout, e))
                continue

        if not gateway_running:
            raise DRApiException(
                "Agent gateway is not running yet on port: {}, giving up\nCmdline: {}".format(
                    port, self._cmdline
                )
            )

    def _ensure_mlops_agent_is_up_and_running(self, timeout=120):
        # Wait for couple of mins (max) to see if agent is up and running
        agent_running = False
        agent_exception = None
        timeout = min(timeout, 120)
        logger.info("Checking if agent is active")
        while timeout > 0:
            time.sleep(1)

            try:
                agent_running = self._gateway.entry_point.isActive()
                agent_exception = self._gateway.entry_point.gotException()
            except Exception as ex:
                logger.error(
                    "Failed to check agent status\n config: " + json.dumps(self._agent_config)
                )
                raise ex

            if agent_running:
                logger.info("MLOps agent is up and running")
                break

            if agent_exception:
                logger.error("Agent got exception: {}".format(agent_exception))
                raise Exception("Got exception while running agent: {}".format(agent_exception))
            timeout -= 1

        if not agent_running:
            raise Exception("Failed to start agent\n config: " + json.dumps(self._agent_config))

    def connect_to_gateway(self, gateway_port=25333):
        self._ensure_gateway_server_is_up_and_running(gateway_port)

        gateway_params = GatewayParameters(
            port=gateway_port, auto_field=True, auto_close=True, eager_load=True
        )

        callback_server_params = CallbackServerParameters(
            port=0, daemonize=True, daemonize_connections=True, eager_load=True
        )

        self._gateway = JavaGateway(
            gateway_parameters=gateway_params,
            callback_server_parameters=callback_server_params,
            python_server_entry_point=self
        )

        string_json_args = json.dumps(self._agent_config)
        self._agent_py4j_instance = self._gateway.entry_point.startAgent(string_json_args)

        if not self._agent_py4j_instance:
            raise Exception(
                "Failed to connect to agent gateway\nConfig: {}".format(
                    json.dumps(self._agent_config)
                )
            )

        self._ensure_mlops_agent_is_up_and_running()

    @staticmethod
    def _stats_get_sum_key_values(stats_dict):
        if stats_dict is None:
            return 0

        total = 0
        for key, value in stats_dict.items():
            if isinstance(value, dict):
                total += sum(value.values())
            else:
                total += value
        return total

    def cleanup(self, message="Execution interrupted"):
        logger.debug("Cleanup: {}".format(message))

        if self._process is not None:
            try:
                self._process.terminate()
            except Exception as ex:
                logger.info("Exception occurred: {}".format(ex))

            logger.info("Stopping MLOps Agent")
            if message != CLEAN_SHUTDOWN_MESSAGE:
                logger.info("Agent stdout \n {}".format(
                    "".join([line.decode("utf-8") for line in self._process.stdout.readlines()])
                )
                )
                logger.info("Agent stderr \n {}".format(
                    "".join([line.decode("utf-8") for line in self._process.stderr.readlines()])
                )
                )

            self._process = None
            self._process_args = None
        if self._cleanup_path:
            logger.info("Removing temporary directory: {}".format(self._path_prefix))
            # In case directory is not empty or other error
            # 'ignore_errors=True' will not raise exception
            shutil.rmtree(self._path_prefix, ignore_errors=True)

    def wait_for_stats_sent_to_mmm(self, submitted_stats, timeout=3600):
        if len(submitted_stats) == 0:
            return

        records_submitted_to_lib = self._stats_get_sum_key_values(submitted_stats)
        if records_submitted_to_lib == 0:
            return

        if timeout == 0:
            # set a long timeout (1hr)
            timeout = 3600
        logger.info(
            "Waiting for agent to send all records to DataRobot MLOps, timeout: " + str(timeout)
            + " sec"
        )

        num_checks = 0
        status_freq = 10
        while timeout > 0:
            records_submitted_to_lib = self._stats_get_sum_key_values(submitted_stats)
            agent_processed_records = self._gateway.entry_point.getNumRecordsProcessed()
            if num_checks % status_freq == 0:
                logger.info("Library sent {} records. Agent has processed {} records.".format(
                    submitted_stats, agent_processed_records))
            num_checks += 1
            # It's possible that agent can send more records in a case where upload is restarting
            # after initial stop and there are already some records in the spool that weren't
            # uploaded in the previous run.
            if records_submitted_to_lib <= agent_processed_records:
                logger.info("All records sent to DataRobot MLOps.")
                break
            time.sleep(1)
            timeout -= 1

    def stop(self):
        # shutdown py4j gateway connection
        self._gateway.shutdown()

        self.cleanup(CLEAN_SHUTDOWN_MESSAGE)
