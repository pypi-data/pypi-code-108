"""
    Module containing configuration utilities
"""

import logging
import os
import six

from monasca_agent.common.config import Config
from monasca_agent.common.singleton import Singleton
from monasca_predictor import version

log = logging.getLogger(__name__)

DEFAULT_CONFIG_FILE_BASENAME = "predictor.yaml"
DEFAULT_CONFIG_FILE = f"/etc/monasca-predictor/{DEFAULT_CONFIG_FILE_BASENAME}"
DEFAULT_LOG_FILE_BASENAME = "predictor.log"
DEFAULT_LOG_DIR = "/var/log/monasca-predictor"


@six.add_metaclass(Singleton)
class PredictorConfig(Config):
    def __init__(self, configFile=None):
        from monasca_predictor.common import util

        options, _ = util.get_parsed_args()
        if configFile is not None:
            self._configFile = configFile
        elif options.config_file is not None:
            self._configFile = options.config_file
        elif os.path.exists(DEFAULT_CONFIG_FILE):
            self._configFile = DEFAULT_CONFIG_FILE
        elif os.path.exists(os.getcwd() + f"/{DEFAULT_CONFIG_FILE_BASENAME}"):
            self._configFile = os.getcwd() + f"/{DEFAULT_CONFIG_FILE_BASENAME}"
        else:
            error_msg = (
                f"No config file found at {DEFAULT_CONFIG_FILE}"
                + " nor in the working directory."
            )
            log.error(error_msg)
            raise IOError(error_msg)

        # Define default values for the possible config items
        self._config = {
            "Main": {
                "forwarder_url": "http://127.0.0.1:17123",
                "hostname": None,
                "autorestart": True,
                "version": self.get_version(),
                # NOTE: the following fields are already declared by monasca-agent
                # "check_freq": 15,
                # "dimensions": None,
                # "listen_port": None,
                # "additional_checksd": "/usr/lib/monasca/agent/custom_checks.d",
                # "limit_memory_consumption": None,
                # "skip_ssl_validation": False,
                # "non_local_traffic": False,
                # "sub_collection_warn": 6,
                # "collector_restart_interval": 24,
            },
            "Api": {
                "is_enabled": False,
                "url": "",
                "project_name": "",
                "project_id": "",
                "project_domain_name": "",
                "project_domain_id": "",
                "ca_file": "",
                "insecure": False,
                "username": "",
                "password": "",
                "use_keystone": True,
                "keystone_timeout": 20,
                "keystone_url": "",
                "api_call_timeout": 10,
                # NOTE: the following fields are already declared by monasca-agent
                # "max_buffer_size": 1000,
                # "max_measurement_buffer_size": -1,
                # "write_timeout": 10,
                # "backlog_send_rate": 5,
                # "max_batch_size": 0,
            },
            "Logging": {
                "disable_file_logging": False,
                "log_level": None,
                "predictor_log_file": DEFAULT_LOG_DIR + f"/{DEFAULT_LOG_FILE_BASENAME}",
                "enable_logrotate": True,
                "log_to_event_viewer": False,
                "log_to_syslog": False,
                "syslog_host": None,
                "syslog_port": None,
            },
        }

        self._read_config()

    def get_version(self):
        return version.version_string
