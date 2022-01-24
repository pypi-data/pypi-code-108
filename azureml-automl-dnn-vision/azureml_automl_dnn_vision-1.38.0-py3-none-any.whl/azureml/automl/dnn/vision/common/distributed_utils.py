# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Helper Utils for distributed mode."""
import logging
import json
import os
import pickle
import sys
import torch
from torch.tensor import Tensor
import torch.distributed as dist
from typing import Any, Dict, List, cast

from azureml.automl.core._logging import log_server

from .constants import DistributedLiterals, DistributedParameters
from .exceptions import AutoMLVisionSystemException


def dist_available_and_initialized() -> bool:
    """ Check if distributed mode is available and is initialized.

    :return: distributed mode or not.
    :rtype: bool
    """
    return cast(bool, dist.is_available() and dist.is_initialized())


def get_world_size() -> int:
    """ Get the world size when running in distributed mode.
    Returns 1 if not in distributed mode.

    :return: world_size
    :rtype: int
    """
    if dist_available_and_initialized():
        return cast(int, dist.get_world_size())
    return 1


def get_rank() -> int:
    """Get the rank of the current process when running in distributed mode.
    Returns 0 if not in distributed mode.

    :return: rank
    :rtype: int
    """
    if dist_available_and_initialized():
        return cast(int, dist.get_rank())
    return 0


def master_process() -> bool:
    """ Return if the current process is the master process.
    If in distributed mode, return true for process with rank 0.
    Else, return True.

    :return: If the current process is the master process.
    :rtype: bool
    """
    return get_rank() == 0


def all_gather(data: Any) -> List[Any]:
    """Run distributed all_gather on pickle-able objects.

    Note (Important!!!):
        Make sure that "data" entirely resides in cpu memory. There are deadlocks otherwise.

        - Say Process P0 uses cuda:0 and P1 uses cuda:1. In this function, the data is pickled and converted
          to a tensor on current gpu before calling dist.all_gather(). Data from P0 (say D0) has device cuda:0 and
          data from P1 (say D1) has device cuda:1.
        - During the dist.all_gather() call, data is moved to the target gpu on which it is requested.
          After dist.all_gather() call, P0 gets [D0, D1] in tensor_list and both of them have device "cuda:0".
          P1 gets [D0, D1] in tensor_list and both of them have device "cuda:1".
        - When some values in data are on gpu, the dist.all_gather() does not move those values to the target gpu.
          This results in memory on a gpu being accessed by two processes, which results in deadlocks and stuck runs.

    Note: This code has been copied from PyTorch example code here:
    https://github.com/pytorch/vision/blob/master/references/detection/utils.py#L75

    :param data: data that has be to be gathered on all processes.
    :type data: any
    :return: List of data objects from all processes.
    :rtype: List
    """
    world_size = get_world_size()
    if world_size == 1:
        return [data]

    # serialized to a Tensor
    buffer = pickle.dumps(data)
    storage = torch.ByteStorage.from_buffer(buffer)
    tensor = torch.ByteTensor(storage).to("cuda")

    # obtain Tensor size of each rank
    local_size = torch.tensor([tensor.numel()], device="cuda")
    size_list = [torch.tensor([0], device="cuda") for _ in range(world_size)]
    dist.all_gather(size_list, local_size)
    size_list_int = [int(size.item()) for size in size_list]
    max_size = max(size_list_int)

    # receiving Tensor from all ranks
    # we pad the tensor because torch all_gather does not support
    # gathering tensors of different shapes
    tensor_list = []
    for _ in size_list_int:
        tensor_list.append(torch.empty((max_size,), dtype=torch.uint8, device="cuda"))
    if local_size != max_size:
        padding = torch.empty(size=(max_size - local_size,), dtype=torch.uint8, device="cuda")
        tensor = torch.cat((tensor, padding), dim=0)
    dist.all_gather(tensor_list, tensor)

    data_list = []
    for size, tensor in zip(size_list_int, tensor_list):
        buffer = tensor.cpu().numpy().tobytes()[:size]
        data_list.append(pickle.loads(buffer))

    return data_list


def all_gather_uneven_tensors(input_tensor: Tensor) -> List[Tensor]:
    """Run distributed all_gather on tensors with size only differing in first dimension.

    Assumptions:
        - The tensor should be on the current gpu device.
        - The tensors being gathered from all processes
            - should have same number of dimensions and
            - should have same size in all dimensions other than dimension 0

    :param input_tensor: tensor that has to be gathered on all processes.
    :type input_tensor: torch.Tensor
    :return: List of tensors gathered from all processes.
    :rtype: List[torch.Tensor]
    """
    world_size = get_world_size()
    if world_size == 1:
        return [input_tensor]

    # obtain tensor size of each rank
    local_size = torch.tensor(input_tensor.size(), dtype=torch.long, device="cuda")
    size_list = [torch.zeros(input_tensor.ndim, dtype=torch.long, device="cuda") for _ in range(world_size)]
    dist.all_gather(size_list, local_size)

    # Verify that tensor sizes are equal in dimensions other than 0.
    rank = get_rank()
    for index, size in enumerate(size_list):
        if not torch.all(torch.eq(local_size[1:], size[1:])):
            raise AutoMLVisionSystemException(
                "Tensor from process {} is of size {} and tensor from process {} is of size {}. "
                "Cannot gather tensors having different sizes in dimensions other than 0."
                .format(rank, local_size, index, size), has_pii=False)

    max_size, _ = torch.max(torch.stack(size_list), dim=0)

    # receiving tensor from all ranks
    # we pad the tensor because torch all_gather does not support
    # gathering tensors of different shapes
    tensor_list = [torch.empty(max_size.tolist(), dtype=input_tensor.dtype, device="cuda") for _ in range(world_size)]
    if local_size[0] != max_size[0]:
        # Padding the tensor along first dimension with zeros
        padding_size = local_size.clone().detach()
        padding_size[0] = max_size[0] - local_size[0]
        padding = torch.empty(padding_size.tolist(), dtype=input_tensor.dtype, device="cuda")
        input_tensor = torch.cat((input_tensor, padding), dim=0)
    dist.all_gather(tensor_list, input_tensor)

    output_list = []
    for index, (size, tensor) in enumerate(zip(size_list, tensor_list)):
        tensor = tensor[:size[0], ...]
        output_list.append(tensor)

    return output_list


def reduce_dict(input_dict: Dict[Any, Tensor], average: bool = True) -> Dict[Any, Tensor]:
    """Reduce a dictionary of tensors from all processes and return a dictionary with
    same keys as input_dict and reduced values.

    To be used with similar tensors from all processes with the below restrictions.
        1) Restrictions on input_dict within a process
            - Tensors for all the keys should already be on the current gpu device.
            - Tensors for all the keys in input_dict should have same size. This is because tensors for all keys
              are stacked using torch.stack before calling dist.all_reduce() and
              stack only works with tensors of same size.
        2) Restrictions on input_dict across processes.
            - input_dict on all processes should have same set of keys.
            - Tensors should have same size across processes i.e. tensors from process 1 should have
              same size as tensors from process 2 and so on.

    Note: The tensors in return dict will not have grad_fn as the below code is executed in torch.no_grad block.

    Note: This code has been copied from PyTorch example code here:
    https://github.com/pytorch/vision/blob/master/references/detection/utils.py#L118

    :param input_dict: Dictionary of tensors to be reduced.
    :type input_dict: Dict
    :param average: Whether to do average or sum for reduce.
    :type average: Boolean
    :return: Dictionary with same keys as data and reduced tensors as values.
    :rtype data: Dict
    """
    world_size = get_world_size()
    if world_size < 2:
        return input_dict

    with torch.no_grad():
        keys = []
        values = []
        # sort the keys so that they are consistent across processes.
        for key in sorted(input_dict.keys()):
            keys.append(key)
            values.append(input_dict[key])
        # Combine the tensors into a single tensor.
        tensor_values = torch.stack(values, dim=0)
        dist.all_reduce(tensor_values)
        if average:
            tensor_values /= world_size

        result = dict(zip(keys, tensor_values))
    return result


def update_settings_for_distributed_training(settings: Dict[str, Any], device_count: int) -> None:
    """ Update the settings and environment variables required for distributed training
    before launching worker processes.

    :param settings: Dictionary with all training and model settings
    :type settings: dict
    :param device_count: Number of gpu devices
    :type device_count: int
    """
    settings.update({
        DistributedLiterals.WORLD_SIZE: device_count,
        log_server.TELEMETRY_ENV_NAME: os.environ.get(log_server.TELEMETRY_ENV_NAME),
        log_server.LOGFILE_ENV_NAME: os.environ.get(log_server.LOGFILE_ENV_NAME),
        log_server.VERBOSITY_ENV_NAME: os.environ.get(log_server.VERBOSITY_ENV_NAME),
        "custom_dimensions": json.dumps(log_server.custom_dimensions)
    })


def enable_distributed_logging(settings: Dict[str, Any], rank: int) -> None:
    """Enable logging when operating in a distributed environment.

    :param settings: Dictionary with all settings
    :type settings: dict
    :param rank: Child process rank
    :type rank: int
    """
    if settings[DistributedLiterals.DISTRIBUTED]:
        parent_log_path = os.path.split(os.environ.get(log_server.LOGFILE_ENV_NAME, 'debug.log'))
        log_filename_split = os.path.splitext(parent_log_path[1])
        child_log_path = os.path.join(
            parent_log_path[0], "{}-{}{}".format(log_filename_split[0], rank, log_filename_split[1]))
        log_server.set_log_file(child_log_path)

        log_server.enable_telemetry(settings.get(log_server.TELEMETRY_ENV_NAME))
        try:
            log_server.set_verbosity(int(os.environ.get(log_server.VERBOSITY_ENV_NAME, str(logging.INFO))))
        except Exception:
            pass

        log_server.update_custom_dimensions(json.loads(settings["custom_dimensions"]))

        # Add console handler
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d - %(levelname)s - %(pid)d - %(name)s.%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        stdout_handler.setFormatter(formatter)
        log_server.add_handler('stdout', stdout_handler)


def setup_distributed_training(rank: int, settings: Dict[str, Any], logger: logging.Logger) -> None:
    """ Setup distributed training for a worker process.

    :param rank: Rank of the process
    :type rank: int
    :param settings: Dictionary with all training and model settings
    :type settings: dict
    :param logger: Logger to use for log messages
    :type logger: logging.Logger
    """
    world_size = settings.get(DistributedLiterals.WORLD_SIZE, None)
    if world_size is None:
        msg = "{} parameter is missing from settings in distributed mode.".format(DistributedLiterals.WORLD_SIZE)
        logger.error(msg)
        raise AutoMLVisionSystemException(msg, has_pii=False)

    # init process group
    logger.info("Setting up process group for worker {}".format(rank))
    os.environ[DistributedLiterals.MASTER_ADDR] = settings[DistributedLiterals.MASTER_ADDR]
    os.environ[DistributedLiterals.MASTER_PORT] = settings[DistributedLiterals.MASTER_PORT]
    torch.cuda.set_device(rank)
    dist.init_process_group(backend=DistributedParameters.DEFAULT_BACKEND,
                            rank=rank, world_size=world_size)
