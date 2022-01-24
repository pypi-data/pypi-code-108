# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility functions for distributed scenarios."""
from typing import Any, Callable

import logging
import os
import time

from azureml.automl.core.shared.exceptions import ClientException

logger = logging.getLogger(__name__)


def is_master_process() -> bool:
    """
    Function for determining whether the current process is master.

    :return: Boolean for whether this process is master.
    """
    return os.environ.get('AZUREML_PROCESS_NAME', 'main') in {'main', 'rank_0'}


def get_unique_download_path(download_file: str) -> str:
    """
    Temporary function to make paths unique to node

    : return: String for path appended with current rank
    """

    rank = os.environ.get('AZUREML_PROCESS_NAME', 'main')
    path = os.path.join(rank, download_file)
    return path


class PollForMaster:
    def __init__(self,
                 proceed_on_condition: Callable[[], Any],
                 polling_interval: int = 5,
                 retries: int = 20):
        self.retries_remaining = retries
        self.polling_interval = polling_interval
        self.proceed_on_condition = proceed_on_condition

    def __enter__(self):
        if not is_master_process():
            logger.info("Entered polling state for non-master process. Timeout set to {:.2f} minutes."
                        .format(self.polling_interval * self.retries_remaining / 60))
            while not self.proceed_on_condition() and self.retries_remaining > 0:
                time.sleep(self.polling_interval)
                self.retries_remaining -= 1
            if not self.retries_remaining:
                raise ClientException("Maximum retries exhausted while waiting for master node to complete.",
                                      has_pii=False)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return


def horovod_initialized(func: Callable[..., Any]) -> Callable[..., Any]:
    try:
        import horovod.torch as hvd
        hvd.size()
    except ValueError:
        # Horovod is not initialized
        logger.debug("Initializing Horovod.")
        hvd.init()
    except ImportError:
        logger.info("Horovod not found in current environment. Distribution via Horovod will be disabled.")
    return func
