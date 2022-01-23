#
# Copyright (c) 2021 by Delphix. All rights reserved.
#
"""
This module includes classes for
dxi configuration related operations.
"""
import json

from dxi._lib import dlpx_exceptions as dxe
from dxi._lib import dx_logging as log
from dxi._lib import util
from dxi._lib.util import DXIConfigConstantsHelper


class DXIConfigConstants(object):
    """
    Define constants for Config Operations.
    """

    CONFIG = DXIConfigConstantsHelper().get_config()
    LOG_DIR = DXIConfigConstantsHelper().get_logdir()
    MODULE_NAME = __name__


class DXIConfig:
    """
    Class for dxi config related opertaions.
    """

    def __init__(
        self,
        config=DXIConfigConstants.CONFIG,
        log_dir=DXIConfigConstants.LOG_DIR,
    ):
        """
        :param config: The path to the dxtools.conf file
        :type config: `str`

        :param log_dir: The path to the logfile for this module
        :type log_dir: `str`
        """
        self.module_name = DXIConfigConstants.MODULE_NAME
        self.key = ""
        self.config = config
        self.log_dir = log_dir

    def _encryption_helper(self):
        """
        Helper for encrypt operation
        """
        try:
            with open(self.config) as config_file:
                config = json.loads(config_file.read())
        except IOError as err:
            err_msg = (
                f"\nERROR: Unable to open {config_file}. Please "
                f"check the path, permissions and retry: {err}"
            )
            log.print_exception(err_msg)
            raise dxe.DlpxException(err_msg)
        except (ValueError, TypeError, AttributeError) as err:
            err_msg = (
                f"\nERROR: Unable to read {config_file} as json."
                f"Please check if the file is in a json format and retry:{err}"
            )
            log.print_exception(err_msg)
            raise dxe.DlpxException(err_msg)
        try:
            for each in config.keys():
                temp_config = config[each]
                temp_config["hostname"] = each
                self.key = util.get_encryption_key(temp_config["ip_address"])
                try:
                    if temp_config["encrypted"].lower() == "true":
                        isEncrypted = True
                    else:
                        isEncrypted = False
                except Exception:
                    isEncrypted = False
                if not isEncrypted:
                    temp_config["username"] = util.encrypt_data(
                        self.key, temp_config["username"]
                    )
                    temp_config["password"] = util.encrypt_data(
                        self.key, temp_config["password"]
                    )
                    temp_config["encrypted"] = "true"
                config[each] = temp_config
                with open(self.config, "w") as encrypt_file:
                    json.dump(config, encrypt_file, indent=4)
        except (Exception) as err:
            log.print_exception(
                f"Error: "
                f"There was an error while encrypting {self.config}\n {err}"
            )
            raise

    def encrypt(self):
        """
        Encrypt username and password information in the dxi config file.
        """
        try:
            self.config = util.find_config_path(self.config)
            self.log_dir = util.find_log_path(
                self.log_dir, DXIConfigConstants.MODULE_NAME
            )
            log.logging_est(self.log_dir)
            log.print_info(f"Starting encryption of file:{self.config}")
            self._encryption_helper()
            log.print_info(f"Encryption of file:{self.config} successful")
            return True
        except Exception:
            return False

    def init(self):
        """
        Initializes dxi configuration
            - Creats config directory and sample dxtools.conf file
            - Creates log directory if it does not exist.
        Raises:
          Exception: General Exception
        """
        try:
            if not self.config or not self.log_dir:
                raise Exception(
                    f"One or more required inputs were not provided.\n"
                    f"dxi init operation requires config and log directory locations.\n"  # noqa
                    f"Please check your input and retry."
                )
            return self._init_helper()
        except Exception as err:
            log.print_exception(f"Exception: {repr(err)}")
            return False

    def _init_helper(self):
        """
        Helper for dxi init operation

        Raises:
          Exception
        """
        init_complete = False
        try:
            util.init_global_config_folders(self.config, self.log_dir)
            init_complete = True
        except IOError as err:
            err_msg = (
                f"Error:  There was an error initializing dxi config"
                f"Reason: {err}"
            )
            log.print_exception(err_msg)
            raise dxe.DlpxException(err_msg)
        except Exception as err:
            err_msg = (
                f"Error:  There was an error initializing dxi config"
                f"Reason: {err}"
            )
            log.print_exception(err_msg)
            raise dxe.DlpxException(err_msg)
        finally:
            return init_complete
