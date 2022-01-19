from __future__ import division

import os
import signal
import argparse
import sys
import ujson
import logging
from pathlib import Path
from typing import Dict


from centaur._.pyvmps.cfg import config
from centaur._.pyvmps.client.constants import ModelType
from centaur._.pyvmps.client.model_controller import ModelController
from centaur._.pyvmps.client.pyvmp import PyVmp
from centaur._.pyvmps.communicator.adapter import Adapter
from centaur._.pyvmps.communicator.socket_base import SocketControl
from centaur._.pyvmps.cfg.config import EnvVarGoPyCommon
from centaur._.pyvmps.cfg.versioned_model import _VersionedModel
from centaur._.pyvmps.logger.get_logger import get_logger
from centaur._.pyvmps.utils.common import get_wheel_package_path

_logger = get_logger(__name__)


def set_tf_loglevel(level):
    if level >= logging.FATAL:
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    elif level >= logging.ERROR:
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    elif level >= logging.WARNING:
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"
    else:
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "0"


log_level_name = config.EnvVarGoPyCommon.LOG_LEVEL
set_tf_loglevel(getattr(logging, log_level_name))


def catch_signals():
    # ignore SIGTERM and SIGINT as it is handled by golang. do NOT ignore SIGCHLD, it is required when using GPUs with TF
    catchable_sigs = {signal.SIGTERM, signal.SIGINT}
    for sig in catchable_sigs:
        signal.signal(sig, signal.SIG_IGN)


def construct_parser():
    parser = argparse.ArgumentParser(description="Pyvmp model loader")
    parser.add_argument("id", type=str, help="unique id assigned to pyvmp")
    parser.add_argument(
        "model_type", type=lambda s: s.lower(), choices=ModelType.all(), help="Type of model, eg tf or Python"
    )
    parser.add_argument("--tf_model_path", type=str, help="Path to load tensorflow saved model")
    parser.add_argument("--py_model_path", type=str, help="Path to model to load arbitrary python model")
    parser.add_argument("--py_model_interface_filepath", type=str, help="Python model interface path")
    parser.add_argument("--py_model_interface_class_name", type=str, help="Python model interface classname")
    parser.add_argument("--py_whl_model_interface_import_path", type=str, help="Python wheel dotted path")
    parser.add_argument(
        "--py_pre_proc_func_import_path",
        type=lambda s: s.split(EnvVarGoPyCommon.DIVIDER_COMMA),
        help="Python based pre-processing function import path",
    )
    parser.add_argument(
        "--py_post_proc_func_import_path",
        type=lambda s: s.split(EnvVarGoPyCommon.DIVIDER_COMMA),
        help="Python based post-processing function import path",
    )
    parser.add_argument("--py_model_init_params", type=str, help="Params to python model's initialize method")

    parser.add_argument("--target_cpus", type=str, help="CPU cores to assign process to")
    parser.add_argument("--trailing_cpus", type=str, help="CPU cores to bind vmp to")
    parser.add_argument("--niceness", type=int, default=0, help="Process priority to assign process with")

    return parser


def parse_and_validate_args(parser, args, versioned_model: _VersionedModel):
    """parse_and_validate_args performs all possible validation on arguments after parsing
    them

    * validate if model path exists

    :param parser:
    """
    args = parser.parse_args(args)

    _logger.debug("args got from go main engine: %s", vars(args))

    # vmp_id must be provided.
    assert args.id is not None and len(args.id) > 0, "vmp_id must be an non empty string"
    versioned_model.id = args.id

    # Validate model type.
    assert args.model_type in ModelType.all()
    versioned_model.model_type = args.model_type

    if args.model_type == ModelType.TF:
        assert hasattr(args, "tf_model_path"), "--tf_model_path required for TF model type"
        assert Path(args.tf_model_path).exists(), "Path to TF model does not exist"
        versioned_model.model_path = args.tf_model_path

    # Validate python model specific settings.
    elif versioned_model.model_type == ModelType.PYTHON:
        if hasattr(args, "py_model_path"):
            if not Path(args.py_model_path).exists():
                raise FileNotFoundError("{} does not exist".format(versioned_model.model_path))
            versioned_model.model_path = args.py_model_path

        assert args.py_model_interface_filepath, "model interface filepath is required for a python model"
        if not Path(args.py_model_interface_filepath).exists():
            raise FileNotFoundError("{} does not exist".format(args.py_model_interface_filepath))
        versioned_model.py_model_interface_filepath = args.py_model_interface_filepath

        assert args.py_model_interface_class_name, "model interface calss name is required for a python model"
        versioned_model.py_model_interface_class_name = args.py_model_interface_class_name

    elif versioned_model.model_type == ModelType.PYTHON_WHEEL:
        assert args.py_whl_model_interface_import_path, "dotted path to python model class required"
        versioned_model.py_whl_model_interface_import_path = args.py_whl_model_interface_import_path
        package_path = versioned_model.py_whl_model_interface_import_path.split(".", 1)[0]
        _logger.debug(
            "package_path=%s,whl_model_interface_import_path=%s",
            package_path,
            versioned_model.py_whl_model_interface_import_path,
        )
        # TODO: get path to site-packages of wheel file
        versioned_model.model_path = get_wheel_package_path(package_path)

    if args.py_pre_proc_func_import_path:
        versioned_model.py_pre_proc_func_import_path = args.py_pre_proc_func_import_path
    if args.py_post_proc_func_import_path:
        versioned_model.py_post_proc_func_import_path = args.py_post_proc_func_import_path

    if args.py_model_init_params:
        versioned_model.py_model_init_params = args.py_model_init_params

    versioned_model.target_cpus = [int(x) for x in args.target_cpus.split(EnvVarGoPyCommon.DIVIDER_COMMA)]
    versioned_model.trailing_cpus = [int(x) for x in args.trailing_cpus.split(EnvVarGoPyCommon.DIVIDER_COMMA)]
    versioned_model.niceness = args.niceness

    _logger.debug("versioned model specific configs: %s", vars(versioned_model))

    return args


def main():
    catch_signals()
    _logger.info("starting pyvmp..")
    parser = construct_parser()
    vm = _VersionedModel()
    args = parse_and_validate_args(parser, sys.argv[1:], vm)
    mc = ModelController(vm)
    socket_control = SocketControl(EnvVarGoPyCommon.UDS_ADDRESS)
    _logger.info("vmp_id=%s connected", args.id)
    adapter = Adapter(socket_control)
    pyvmp = PyVmp(args.id, adapter, mc)
    exit_status: Dict = pyvmp.start()
    _logger.info("exit_status=%s", exit_status)
    adapter.send(exit_status)
    socket_control.shutdown()
    _logger.info("pyvmp exit")


if __name__ == "__main__":
    main()
