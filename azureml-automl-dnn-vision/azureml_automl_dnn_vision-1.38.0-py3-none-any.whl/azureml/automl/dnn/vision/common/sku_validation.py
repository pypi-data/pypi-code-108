# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Helper Utils for sku validation."""

import pynvml
import torch

from .exceptions import AutoMLVisionValidationException
from . import distributed_utils
from .logging_utils import get_logger

MEGABYTE = 1024.0 * 1024.0
# Set MIN_GPU_MEM to be between 11321.8750MB (the max observed gpu mem consumption)
# and 11,441.1875MB (NC6 GPU mem size got by pynvml).
MIN_GPU_MEM = 11400 * MEGABYTE

logger = get_logger(__name__)


def validate_gpu_sku(device: str, min_gpu_mem: float = MIN_GPU_MEM) -> None:
    """Validate gpu sku requirements.

    :param device: Target device
    :type device: Pytorch device or str
    :param min_gpu_mem: the min value of the gpu mem.
    :type min_gpu_mem: int
    """

    if device == 'cpu' or not torch.cuda.is_available() or not distributed_utils.master_process():
        return

    pynvml.nvmlInit()
    try:
        is_valid = True
        per_device_infos = []
        device_count = pynvml.nvmlDeviceGetCount()
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            if mem_info.total < min_gpu_mem:
                is_valid = False
                per_device_infos.append(
                    "{}: mem_info_total:({} MB) is smaller than min_gpu_mem:({} MB)".format(
                        pynvml.nvmlDeviceGetName(handle),
                        mem_info.total / MEGABYTE,
                        min_gpu_mem / MEGABYTE
                    )
                )
        if is_valid:
            logger.info("GPU memory validated to be above the minimum threshold of {} MB."
                        .format(min_gpu_mem / MEGABYTE))
        else:
            error = "Failed to validate gpu sku requirements. {}".format("; ".join(per_device_infos))
            logger.error(error)
            raise AutoMLVisionValidationException(error, has_pii=False)
    except pynvml.NVMLError as error:
        logger.info("Exception while validating gpu sku requirements. {}".format(error))
    finally:
        pynvml.nvmlShutdown()
