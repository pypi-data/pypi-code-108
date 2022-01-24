#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

"""This module takes the conf file for DDP(s) and returns an authentication
   object
"""

import json
import ssl
from time import sleep,time

from delphixpy.v1_10_2 import exceptions
from delphixpy.v1_10_2 import job_context
from delphixpy.v1_10_2 import web
from delphixpy.v1_10_2.delphix_engine import DelphixEngine
from dxi._lib import dxi_constants as const
from dxi._lib import dx_logging as log

from . import dlpx_exceptions
from . import dx_logging
from . import util
from .util import DXIConfigConstantsHelper
from .dlpx_exceptions import DXIException
from .util import format_err_msg


class GetSession:
    """
    Class to read configuration and returns an Delphix session object
    """

    def __init__(self):
        self.server_session = None
        self.dlpx_ddps = {}
        self.jobs = {}

    def get_config(self, config_file_path=DXIConfigConstantsHelper().get_config()):
        """
        This method reads in the dxtools.conf file

        :param config_file_path: path to the configuration file.
        :type config_file_path: str
        :return: dict containing engine information
        """
        # First test to see that the file is there and we can open it
        try:
            with open(config_file_path) as config_file:
                config = json.loads(config_file.read())
        except IOError:
            log.print_exception(f"ERROR: Was unable to open {config_file_path}")
            raise dlpx_exceptions.DlpxException(
                f"\nERROR: Was unable to open {config_file_path}. Please "
                f"check the path and permissions, and try again.\n"
            )
        except (ValueError, TypeError, AttributeError) as err:
            log.print_exception(f"\nERROR: Was unable to read {config_file_path} as json\n{err}")
            raise dlpx_exceptions.DlpxException(
                f"\nERROR: Was unable to read {config_file_path} as json. "
                f"Please check if the file is in a json format and try "
                f"again.\n {err}"
            )
        for each in config.keys():
            temp_config = config[each]
            # HTTPS vs HTTP
            try:
                # temp_config["encrypted"].lower() == 'true'
                use_https = temp_config["use_https"]
            except Exception:
                use_https = "False"
            if use_https.lower() == "true":
                temp_config["use_https"] = True
            else:
                temp_config["use_https"] = False
            # Decryption Logic
            try:
                if temp_config["encrypted"].lower() == "true":
                    isEncrypted = True
                else:
                    isEncrypted = False
            except Exception:
                isEncrypted = False
            if isEncrypted:
                key = util.get_encryption_key(temp_config["ip_address"])
                temp_config["username"] = util.decrypt_data(
                    key, temp_config["username"]
                )
                temp_config["password"] = util.decrypt_data(
                    key, temp_config["password"]
                )
            self.dlpx_ddps[each] = temp_config

    def dlpx_session(
        self,
        f_engine_address,
        f_engine_username,
        f_engine_password=None,
        enable_https=True,
    ):
        """
        Method to setup the session with DDP
        :param f_engine_address: The DDP's address (IP/DNS Name)
        :type f_engine_address: str
        :param f_engine_username: Username to authenticate
        :type f_engine_username: str
        :param f_engine_password: User's password
        :type f_engine_password: str
        :param enable_https: Enable or disable HTTPS
        :type enable_https: bool
        :return: delphixpy.v1_10_2.delphix_engine.DelphixEngine object
        """
        f_engine_namespace = "DOMAIN"

        # Remove the next 3 lines if using in a production environment.
        # if not os.environ.list("PYTHONHTTPSVERIFY", "") and getattr(
        #     ssl, "_create_unverified_context", None
        # ):
        ssl._create_default_https_context = ssl._create_unverified_context
        try:
            dx_logging.print_info(
                f"Initiating connection with Delphix Engine."
            )
            self.server_session = DelphixEngine(
                f_engine_address,
                f_engine_username,
                f_engine_password,
                f_engine_namespace,
                enable_https,
            )
            self.server_wait(f_engine_address)
            dx_logging.print_debug(
                f"Connected. Session Established."
            )
        except DXIException as err:
            raise err
        except (TimeoutError) as err:
            log.print_exception(f"Timeout while authenticating to "
                                f"{f_engine_address}:\n {err}\n")
            raise dlpx_exceptions.DlpxException(
                f"ERROR: Timeout while authenticating to "
                f"{f_engine_address}:\n {err}\n"
            )
        except (Exception) as err:
            log.print_exception(f"Error while authenticating to "
                                f"{f_engine_address}:{err}")
            raise dlpx_exceptions.DlpxException(
                f"ERROR: Error while authenticating to "
                f"{f_engine_address}:{err}"
            )

    def job_mode(self, single_thread=True):
        """
        This method tells the jobs to run sync or async, based on the
        single_thread variable
        :param single_thread: Execute application synchronously (True) or
                       async (False)
                       Default: True
        :type single_thread: Bool
        :return: contextlib._GeneratorContextManager
        """
        # Synchronously
        if single_thread:
            return job_context.sync(self.server_session)
        # Or asynchronously
        elif single_thread is False:
            return job_context.asyncly(self.server_session)

    def job_wait(self):
        """
        This job stops all work in the thread/process until jobs are
        completed.
        """
        # Grab all the jos on the server (the last 25, be default)
        all_jobs = web.job.get_all(self.server_session)
        # For each job in the list, check to see if it is running (not ended)
        for job_obj in all_jobs:
            if not (job_obj.job_state in ["CANCELED", "COMPLETED", "FAILED"]):
                dx_logging.print_debug(
                    f"\nDEBUG: Waiting for {job_obj.reference} "
                    f"(currently: {job_obj.job_state}) to finish running "
                    f"against the container.\n"
                )
                # If so, wait
                job_context.wait(self.server_session, job_obj.reference)

    def server_wait(self,f_engine_address):
        """
        This job waits for a successful connection to DDP.
        """
        timeout = time() + 60
        while True:
            try:
                web.system.get(self.server_session)
                break
            except exceptions.HttpError as err:
                err_msg = ""
                if hasattr(err,'status'):
                    if getattr(err,'status') == 401:
                        err_msg = format_err_msg(
                            const.MSG_AUTH_FAILED1.format(f_engine_address),
                            err_code=const.ERR_AUTH_FAILED,
                            action=const.ACTION_AUTH_FAILED
                        )
                        raise DXIException(err_msg, const.ERR_AUTH_FAILED)
            except exceptions.RequestError as err:
                err_msg = format_err_msg(
                    const.MSG_AUTH_FAILED1.format(f_engine_address),
                    msg2=err.args[0].details,
                    err_code=const.ERR_AUTH_FAILED,
                    action=err.args[0].action
                )
                dx_logging.print_exception(err_msg, ref=const.ERR_AUTH_FAILED, stdout=False)
                raise DXIException(err_msg, const.ERR_AUTH_FAILED)
            except Exception as err:
                pass
            if time() > timeout:
                err_msg = format_err_msg(
                    const.MSG_AUTH_TIMEOUT1.format(f_engine_address),
                    msg2= const.MSG_AUTH_TIMEOUT2,
                    err_code=const.ERR_AUTH_TIMEDOUT,
                    action=const.ACTION_AUTH_TIMEOUT
                )
                dx_logging.print_exception(err_msg, ref=const.ACTION_AUTH_TIMEOUT, stdout=False)
                raise DXIException(err_msg, const.ERR_AUTH_TIMEDOUT)
            dx_logging.print_info("Waiting to successfully authenticate to Delphix Engine.")
            sleep(5)


def dlpx_logout(dlpx_session):
    """
    Method to logout
    """
    try:
        dx_logging.print_debug("Terminating Engine session.")
        web.delphix.delphix.logout(dlpx_session)
    except (exceptions.HttpError, exceptions.RequestError) as err:
        dx_logging.print_exception(f"Error Terminating session:\n{err}")
