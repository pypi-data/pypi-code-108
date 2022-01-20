import logging
import subprocess

from biolib.biolib_logging import logger
from biolib import utils
from biolib.compute_node.cloud_utils.cloud_utils import CloudUtils
from biolib.compute_node.utils import SystemExceptionCodes
from biolib.typing_utils import Callable


class ComputeProcessException(Exception):
    def __init__(self, original_error: Exception, biolib_error_code,
                 # Not using SendSystemExceptionType since importing it leads to many circular import problems
                 # TODO: Fix circular import problems when importing SendSystemExceptionType
                 send_system_exception: Callable[[SystemExceptionCodes], None],
                 may_contain_user_data: bool = True):
        super().__init__()

        if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE and not may_contain_user_data:
            CloudUtils.log(
                log_message=str(original_error),
                level=logging.ERROR
            )

        send_system_exception(biolib_error_code)
        logger.error(original_error)


def log_disk_and_memory_usage_info() -> None:
    if not utils.IS_DEV:
        disk_usage_info = subprocess.run(['df', '-h'], check=False, capture_output=True)
        memory_usage_info = subprocess.run(['free', '-h', '--si'], check=False, capture_output=True)

        if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
            CloudUtils.log(
                log_message=disk_usage_info.stdout.decode(),
                level=logging.DEBUG
            )
            CloudUtils.log(
                log_message=memory_usage_info.stdout.decode(),
                level=logging.DEBUG
            )

        else:
            logger.debug(disk_usage_info)
            logger.debug(memory_usage_info)
