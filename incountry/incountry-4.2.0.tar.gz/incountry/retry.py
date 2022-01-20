from random import random
import time

import wrapt

from .exceptions import StorageServerException
from .validation.utils import path_to_obj
from .models.http_options import BASE_DELAY_DEFAULT, MAX_DELAY_DEFAULT


def get_delay_with_jitter(delay):
    # @SONAR-OFF
    return delay * (0.8 + random() * 0.4)  # nosec: disable=B311
    # @SONAR-ON


def retry_on_server_exception(
    status_code, retry_base_delay=BASE_DELAY_DEFAULT, retry_max_delay=MAX_DELAY_DEFAULT, instance_config_path=()
):
    @wrapt.decorator
    def decorator(function, instance, args, kwargs):
        if (
            instance is not None
            and path_to_obj(instance, instance_config_path + ("retry_base_delay",))
            and path_to_obj(instance, instance_config_path + ("retry_max_delay",))
        ):
            base_delay_sec = path_to_obj(instance, instance_config_path + ("retry_base_delay",))
            max_delay_sec = path_to_obj(instance, instance_config_path + ("retry_max_delay",))
        else:
            base_delay_sec = retry_base_delay
            max_delay_sec = retry_max_delay

        current_delay_sec = base_delay_sec
        total_retries = 0
        should_execute = True

        while should_execute:
            try:
                should_execute = False
                total_retries = total_retries + 1
                return function(*args, **kwargs)
            except StorageServerException as e:
                if (
                    not getattr(e, "status_code", None)
                    or getattr(e, "status_code", None)
                    and e.status_code != status_code
                ):
                    raise

                if current_delay_sec <= max_delay_sec:
                    should_execute = True
                    time.sleep(get_delay_with_jitter(current_delay_sec))
                    current_delay_sec = current_delay_sec * 2
                    continue

                raise

    return decorator
