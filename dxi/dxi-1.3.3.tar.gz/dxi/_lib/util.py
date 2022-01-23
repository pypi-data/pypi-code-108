#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

import json
import os
import sys
import uuid

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from colorama import Fore,Style
from delphixpy import exceptions
from dxi._lib import dlpx_exceptions
from dxi._lib import dxi_constants as const
from dateutil import parser

from . import dx_logging as log

class DXIConfigConstantsHelper(object):
    DXIDATA = "dxi-data"
    CONF = '/config/dxtools.conf'
    LOG= '/logs/'

    ROOT_DEFAULT = os.path.dirname(os.path.abspath(__file__))+'/../../'

    def get_dxidata_root(self):
        root = os.environ.get('DXI_DIR', self.ROOT_DEFAULT)
        if not root.endswith('/'):
            root = root + '/'

        if root == '/dxi-data/':
            return root
        else:
            return root + self.DXIDATA

    def get_config(self):
        return self.get_dxidata_root() + self.CONF

    def get_logdir(self):
        return self.get_dxidata_root() + self.LOG

def find_config_path(config_file_path):
    """
    Locate the config path if the default is passed.

    :param config_file_path: Path to the configuration file.
    :type config_file_path: `str`
    :return: config_file_path
    :rtype: `str`
    """
    try:
        if os.path.isfile(config_file_path) and os.path.isabs(
                config_file_path
        ):
            return config_file_path
        else:
            exec_path = get_executable_path()
            if exec_path is not None:
                config_file_path = str(
                    os.path.join(exec_path, "dxi-data/config/dxtools.conf")
                )
            else:
                log.print_debug(
                    f"Config location passed to dxi does not exist. "
                    f"Scanning default location."
                )
                config_file_path = DXIConfigConstantsHelper().get_config()
                #config_file_path = os.path.abspath(config_file_path)

            if not os.path.isfile(config_file_path):
                err_msg = format_err_msg(
                    const.MSG_CONFIG_NOTFOUND1,
                    msg2=const.MSG_CONFIG_NOTFOUND2,
                    err_code=const.ERR_CONFIG_NOTFOUND,
                    action=const.ACTION_CONFIG_NOTFOUND
                )
                #log.print_exception(err_msg)
                raise dlpx_exceptions.DXIException(
                    err_msg,
                    const.ERR_CONFIG_NOTFOUND
                )
        log.print_debug("Config file path is: {}".format(config_file_path))
        return config_file_path
    except Exception as err:
        raise Exception(
            f"Failed to find config path @ {config_file_path} {repr(err)}"
        )


def find_log_path(log_path, module_name):
    """
    Locate the log path if the default is passed.
    This logic will be changed once log_path is property of parent class.

    :param config_file_path: Path to the configuration file.
    :type config_file_path: `str`
    :param module_name: Module name
    :type module_name: `str`
    :return: Log file path
    :rtype: `str`
    """
    log_file_path = None
    try:
        if os.path.isfile(log_path):
            return log_path
        else:
            exec_path = get_executable_path()
            if exec_path is not None:
                # do something
                log_file_path = str(os.path.join(exec_path, "dxi-data/logs"))
            else:
                log.print_debug(
                    f"Logs location passed to dxi does not exist. "
                    f"Using default location."
                )
                log_file_path = DXIConfigConstantsHelper().get_logdir()

            if not os.path.isdir(log_file_path):
                err_msg = format_err_msg(
                    const.MSG_LOG_NOTFOUND1,
                    msg2=const.MSG_LOG_NOTFOUND2,
                    err_code=const.ERR_LOG_NOTFOUND,
                    action=const.ACTION_LOG_NOTFOUND
                )

                raise dlpx_exceptions.DXIException(
                    err_msg,
                    const.ERR_LOG_NOTFOUND
                )
            log_file_path = os.path.abspath(log_file_path)
            log_file_path = str(
                os.path.join(log_file_path, "{}.log".format(module_name))
            )
            log.print_debug("Log file path is: {}".format(log_file_path))

        return log_file_path
    except Exception as err:
        log.print_exception(f"Failed to find log path @ {log_file_path} {repr(err)}")
        raise Exception(
            f"Failed to find log path @ {log_file_path} {repr(err)}"
        )



def run_async(func):
    """
    http://code.activestate.com/recipes/576684-simple-threading-decorator/
    run_async(func)
    function decorator, intended to make "func" run in a separate
    thread (asynchronously).
    Returns the created Thread object

    E.g.:
    @run_async
    def task1():
        do_something

    @run_async
    def task2():
        do_something_too

        t1 = task1()
        t2 = task2()
        ...
        t1.join()
        t2.join()

    :param func: The callable function object to be invoked by the run
    :type func: `callable`
    :return: Decorated function
    :rtype: `callable`

    """
    from threading import Thread
    from functools import wraps

    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target=func, args=args, kwargs=kwargs)
        func_hl.start()
        return func_hl

    return async_func


def exception_handler(function):
    def inner_function(*args, **kwargs):
        try:
            function(*args, **kwargs)
            # Here we handle what we do when the unexpected happens
            return True
        except SystemExit as err:
            # This is what we use to handle our sys.exit(#)
            log.print_exception(
                f"ERROR: Please check the ERROR message below:\n{err}"
            )
        except dlpx_exceptions.DlpxException as err:
            # We use this exception handler when an error occurs in a function.
            log.print_exception(
                f"ERROR: Please check the ERROR message below:\n{err}"
            )
        except exceptions.HttpError as err:
            # We use this exception handler when our connection to Delphix
            # fails
            log.print_exception(err)
            print(
                f"ERROR: Connection failed to the Delphix Engine. Please "
                f"check the error message below:\n{err}"
            )
        except exceptions.JobError as err:
            # We use this exception handler when a job fails in Delphix so
            # that we have actionable data
            log.print_exception(err.job)
            print(f"A job failed in the Delphix Engine:\n{err.job}")
        except KeyboardInterrupt:
            # We use this exception handler to gracefully handle ctrl+c exits
            log.print_debug(
                "You sent a CTRL+C to interrupt the process"
            )
        return False

    return inner_function


def convert_dct_str(obj_dct):
    """
    Convert dictionary into a string for printing
    :param obj_dct: Dictionary to convert into a string
    :type obj_dct: dict
    :return: string object
    """
    js_str = ""
    if isinstance(obj_dct, dict):
        for js_db, js_jdbc in obj_dct.items():
            if isinstance(js_jdbc, list):
                js_str += f'{js_db}: {", ".join(js_jdbc)}\n'
            elif isinstance(js_jdbc, str):
                js_str += f"{js_db}: {js_jdbc}\n"
    else:
        raise dlpx_exceptions.DlpxException(
            f"Passed a non-dictionary object to convert_dct_str():"
            f"{type(obj_dct)}"
        )
    return js_str


def boolean_based_system_exit(bool_status):
    """
    Exit with correct code based on boolean value
    :param bool_status:
    :type bool_status
    """
    if bool_status:
        sys.exit(0)
    else:
        sys.exit(1)


def show_progress(per, jobid, with_progress_bar=True, status='Running', total=100):
    if with_progress_bar:
        prefix = 'Progress(' + jobid + ')'
        if per >= total:
            status = 'Completed'
        bar_len = 60
        filled_len = int(round(per * bar_len / float(total)))
        bar = '=' * filled_len + '-' * (bar_len - filled_len)
        fmt = f'\r{prefix} |{bar}| {per}% {status}'
        print('\b' * len(fmt), end='')
        sys.stdout.write(fmt)
        sys.stdout.flush()


def decrypt_data(key, value):
    """
    Decryts a value with SHA265 agorithm
    :param value: value to decrypt
    return decrypted value
    """
    hashhex = value[-64:]
    enc = value[0:-64]
    try:
        dehex = bytes.fromhex(enc)
        msg_nonce = dehex[:12]
        ciphertext = dehex[12:]
        cipher = ChaCha20Poly1305(key)
        value = cipher.decrypt(msg_nonce, ciphertext, None)
        hash_object = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hash_object.update(value)
        dhash = hash_object.finalize()
        hashhex_check = dhash.hex()
        if hashhex == hashhex_check:
            return value.decode('utf-8')
        else:
            raise Exception("Password SHA256 value after decrypt is wrong")
    except InvalidTag as err:
        log.print_exception(f"Wrong decryption key: {err}")
        raise err
    except Exception as err:
        log.print_exception(f"Error: Incorrect Decrypted Value: {err}")
        raise err

def encrypt_data(key,password):
    """
    Encrypts a value with SHA 256 algorithm
    :param value : Value to encrypt
    return encryted value
    """
    try:
        hash_object = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hash_object.update(password.encode())
        dhash = hash_object.finalize()
        hashhex = dhash.hex()
        nonce = os.urandom(12)
        cipher = ChaCha20Poly1305(key)
        enc = cipher.encrypt(nonce, password.encode(), None)
        enchex = enc.hex()
        return nonce.hex() + enchex + hashhex
    except Exception as err:
        log.print_exception(f"Error: There as an exception while encrypting {err}")
        raise err

def get_encryption_key(seed):
    try:
        key = hex(uuid.getnode())+seed
        key = '{:32.32}'.format(key)
        key = key.encode()
        return key
    except Exception as err:
        log.print_exception(f"Error: There was an error creating key: {err}")
        raise


def init_global_config_folders(config, log_dir):
    """
    Called as part of init operation.
    Does the following
        - Creates the config directory if it does not exist
        - Creates Log Directory if it does not exist.
    Args:
         config_dir: Full path to the config directory
         log_dir: Full path to the logs directory

    Raises:
        General Exception
    """
    try:
        exec_path = get_executable_path()
        if exec_path is not None:
            config_path = str(
                os.path.join(exec_path, "dxi-data/config/dxtools.conf")
            )
            log_path = str(os.path.join(exec_path, "dxi-data/logs"))
        else:
            log_path = get_abs_path(log_dir)
            config_path = get_abs_path(config)
    except Exception as err:
        log.print_exception(
            f" There was an exception while "
            f"resolving config and log root directories {err}"
        )
        raise Exception(
            f"There was an exception while "
            f"resolving config and log root directories {err}"
        )
    try:
        log.print_debug("Log Directory full path " + log_path)
        if not os.path.exists(log_path):
            os.makedirs(log_path, exist_ok=True)
        log.print_info(f"Log directory created at {log_path}")
    except Exception as err:
        log.print_exception(
            f"init_global_config_folders(): "
            f"There was an error while creating log directory: {err}"
        )
        raise err
    try:
        log.print_debug("Config Directory full path " + config_path)
        if not os.path.exists(config_path):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
        _add_default_config_value(config_path)
        log.print_debug(f"Config directory created at @ {config_path}")
    except Exception as err:
        log.print_exception(
            f"init_global_config_folders(): "
            f"There was an exception while creating config file : {err}"
        )
        raise err


def get_abs_path(relative_path, base_dir=__file__):
    """
    Returns the absolute path
    Args:
        base_dir: Base directory for relative path
        relative_path: Relative path
    Returns:
        abs_path: Absolute path for relative path
    Raises:
        Exception: General Exception
    """
    if str(relative_path).startswith("/"):
        return relative_path

    try:
        path = os.path.dirname(base_dir)
        levels = relative_path.split("/")
        for level in levels:
            path = os.path.join(path, level)
        abs_path = os.path.abspath(path)
        return str(abs_path)
    except Exception as err:
        log.print_exception(
            f"There was an error getting "
            f"the absolute path for: {relative_path}: {err}"
        )

def get_executable_path():
    """
    Check if this is an executable distribution.
    If executable, return the path of the exe file.

    Returns:
        path: Executable location
    """
    exec_dir = None
    if getattr(sys, "frozen", False):
        exec_location = sys.argv[0]
        # log.print_info("Identified Packaged Distribution at " + exec_location)
        abs_path = os.path.abspath(exec_location)
        # log.print_info("Absolute Path: " + abs_path)
        exec_dir = os.path.dirname(abs_path)
        # log.print_info(f"Executable located at :{exec_dir}")
    return exec_dir


def _add_default_config_value(config_path):
    """
    Add default value in a config path
    Args:
        config_path: Absolute config location
    """
    info = {
        "engine_name_1": {
            "hostname": "engine_name_1",
            "ip_address": "11.111.11.111",
            "username": "user",
            "password": "pass",
            "port": "80",
            "default": "true",
            "encrypted": "false",
            "use_https": "false",
        },
        "engine_name_2": {
            "hostname": "engine_name_2",
            "ip_address": "22.222.222.22",
            "username": "user",
            "password": "pass",
            "port": "80",
            "default": "true",
            "encrypted": "false",
            "use_https": "false",
        },
    }
    log.print_info(
        "Config file created at {config_path} ".format(config_path=config_path)
    )
    with open(config_path, "w+") as out:
        json.dump(info, out, indent=4)


def format_err_msg(
        msg1,
        msg2=None,
        engine_name=None,
        object_name=None,
        err_code='ERR_DXI_GEN',
        operation=None,
        action='Rectify the error and re-try.',
):
    '''
    Function to format an error message to print for user.
    Format:
        error_code: msg1
        msg2
        Details: Engine - engine_name, Object - object_name, Operation - operation
        Possible Action: action
    Args:
        msg1: Error message string
        msg2: Error message descriptive string.
        engine_name: Name (hostname/ip) of the engine where error occurred.
        object_name: Name of the Delphix data object
        err_code: An error code if applicable
        operation: The delphix operation ( refresh, rewind etc) related to failure
        action: Possible resolution

    Returns:
        err_str: A formatted error message.
    '''
    # e = '{}:\n\t{}\n\t{}\n\tDetails- Engine:{}, Object:{}, ' \
    #     'Operation:{}\n\n\tPossible Action: {}'.format(
    #     err_code,
    #     msg1,
    #     msg2,
    #     engine_name,
    #     object_name,
    #     operation,
    #     action
    # )
    e = f"{Fore.RED}{err_code}{Style.RESET_ALL}:\n\t{msg1}" \
        f"\n\tMessage: {msg2}" \
        f"\n\tDetails- Engine:{engine_name}, Object:{object_name}, " \
        f"Operation:{operation}\n\tPossible Action: {action}"
    return e

def convert_string_to_datetime(tstr):
    """
    Converts timestamp in string format to datetime.
    Args:
        tstr (string): Timestamp string.
    Returns:
        ts_dt (datetime): Timestamp as a datetime object
    Raises:
        Exception: General Exception.
    """
    ts_dt = parser.parse(tstr)
    return ts_dt