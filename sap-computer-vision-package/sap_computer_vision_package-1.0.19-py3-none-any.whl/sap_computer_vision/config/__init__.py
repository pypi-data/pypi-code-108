"""This module provides functions to manage the configuration included in the package"""
import logging
import os
import platform
from typing import Union, Iterable
import pathlib

import torch
from detectron2.config import get_cfg as _get_cfg
from detectron2 import model_zoo
from detectron2.utils import comm
from detectron2.utils.collect_env import collect_env_info
from detectron2.utils.logger import setup_logger

from sap_computer_vision import DISCLAIMER


CONFIGS_DIR = pathlib.Path(__file__).parent / 'configs'


def get_cfg(*args, apply_MP_if_macos=True, **kwargs):
    """ This functions is a replacement for detectrons get_cfg functions.
    In automatically sets 'cfg.MODEL.DEVICE' and 'KMP_DUPLICATE_LIB_OK' env parameter.

    Parameters
    ----------
    apply_MP_if_macos: bool, optional, defaul=True
        Whether the 'KMP_DUPLICATE_LIB_OK' env should be set when the stuff is executed
        on MacOS.

    *args/**kwargs
        All other arguments and keyword arguments are passed to detectron2.config.get_cfg.
        See https://detectron2.readthedocs.io/en/latest/modules/config.html#detectron2.config.get_cfg
        for details.

    Returns
    ----------
    CfgNode
       a detectron2 CfgNode instance.
    """
    cfg = _get_cfg(*args, **kwargs)
    cfg.set_new_allowed(is_new_allowed=True)
    if torch.cuda.is_available():
        cfg.MODEL.DEVICE = 'cuda'
    else:
        logger = logging.getLogger(__name__)
        logger.warning("CUDA not found, using CPU")
        cfg.MODEL.DEVICE = 'cpu'
        if platform.system() == 'Darwin' and apply_MP_if_macos:
            # Probably not the best place, but hard to find a better place
            os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
    return cfg


def get_config_file(model_name: str, extensions: Union[str, Iterable[str]]='.yaml'):
    """This functions is a replacement for detectron2.model_zoo.get_config file function.

    The functions check if the config is a sap_cv config. If detectron2.model_zoo.get_config_file
    is called.

    Parameters
    ----------
    model_name: str
        Name of the config.

    extensions: str or Iterable of str
        model_name can be provided with a file extension. With extensions all file types set
        should be consider can be set.

    Returns
    ----------
    str
       path of the config file

    """
    if isinstance(extensions, str):
        extensions = [extensions]

    for ext in extensions:
        cfg_file = (CONFIGS_DIR / model_name).with_suffix(ext)
        if cfg_file.exists():
            return str(cfg_file)
    return model_zoo.get_config_file(model_name)


def setup_loggers(output_dir: None=None, additional_loggers: Union[None, Iterable[str]]=None, color=True):
    """Function to setup the 'fvcore', 'sap_computer_vision' and 'detectron2' loggers

    Parameters
    ----------
    output_dir: str or None, optional, default=None
        Path of a directory used to store log files.
        If None logs are only printed to stdout and not stored into files.

    additional_loggers: None or Iterable of str
        Name of the modules for which a logger should be setup.
    """
    if additional_loggers is None:
        additional_loggers = []
    rank = comm.get_rank()
    setup_logger(output_dir, distributed_rank=rank, name="fvcore", color=color)
    setup_logger(output_dir, distributed_rank=rank, name="sap_computer_vision", abbrev_name="sap_cv", color=color)
    for logger in additional_loggers:
        setup_logger(output_dir, distributed_rank=rank, name=logger, abbrev_name="script", color=color)
    logger = setup_logger(output_dir, distributed_rank=rank, color=color)

    if pathlib.Path(DISCLAIMER).exists():
        with pathlib.Path(DISCLAIMER).open() as stream:
            disclaimer_txt = stream.read()
        logger.info("DISCLAIMER:\n{}".format(disclaimer_txt))
    logger.info("Rank of current process: {}. World size: {}".format(rank, comm.get_world_size()))
    logger.info("Environment info:\n" + collect_env_info())
