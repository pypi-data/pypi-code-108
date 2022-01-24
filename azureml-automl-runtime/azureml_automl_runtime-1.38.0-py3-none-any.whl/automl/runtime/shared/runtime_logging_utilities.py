# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility module for logging."""
from typing import Optional
import logging

from .types import DataInputType
from .memory_utilities import get_data_memory_size


logger = logging.getLogger(__name__)


def log_data_info(data_name: str,
                  data: DataInputType,
                  run_id: Optional[str] = None,
                  streaming: Optional[bool] = False) -> None:
    """
    Log datatype, shape and datasize.

    :param data_name: Name of the data.
    :param data: Data for the run.
    :param run_id: Run ID.
    :streaming: Whether streaming is enabled for the run.
    :return: None
    """
    prefix = "[ParentRunId:{}]".format(run_id) if run_id is not None else ""
    extra_info = {
        'properties': {
            'DataName': data_name,
            'DataType': str(type(data)),
            'Streaming': streaming
        }
    }

    if streaming:
        message = "{}{} datatype is {}."
        logger.info(message.format(prefix, data_name, type(data)), extra=extra_info)
    else:
        memory_size = get_data_memory_size(data)
        message = "{}{} datatype is {}, shape is {}, datasize is {}."
        logger.info(message.format(prefix, data_name, type(data), data.shape, memory_size), extra=extra_info)
