import ast
import os.path
import re
import sys
import ujson
from pydoc import locate
from typing import Callable, Dict, List

from centaur._.pyvmps.cfg import constants
from centaur._.pyvmps.logger.get_logger import get_logger
from centaur._.pyvmps.models.exceptions import (
    InvalidModelException,
    ModelInitFailed,
    InvalidPyModelInterfaceClassException,
)
from centaur._.pyvmps.models.python.constants import ExporterVar
from centaur._.pyvmps.utils.common import abs_and_normalize_path, get_abspath
from centaur._.pyvmps.client.constants import PayloadKey
from centaur._.pyvmps.error_handling.errors import python_model_error
import importlib
from centaur._.pyvmps.tracking.tracker import tracker
from centaur._.pyvmps.tracking.constants import Tracking

_logger = get_logger(__name__)


def _validate_model_config(versioned_model_path: str, interface_class_filepath: str, interface_class_name: str) -> Dict:
    """_validate_model_config inspects given file containing implemented predict class and returns a dict
    {
        "interface_class_abs_dirpath": interface_base_path, # base path of the interface class
        "interface_class_filename_without_ext": interface_class_filename_without_ext, # file containing interface class
        "interface_class_name": interface_class_name,
        "interface_func_defined": func_verbs, # list of methods found in class
        "diff_interface_base_path": diff_interface_base_path, # bool indicating if the interface file is in a diff directory than the python model
    }
    :param versioned_model_path:
    :type versioned_model_path: str
    :param path_to_interface:
    :type path_to_interface: str
    :rtype: dict
    """

    # normalize path
    interface_class_abs_filepath = abs_and_normalize_path(interface_class_filepath)

    diff_interface_base_path = False
    if not os.path.exists(interface_class_abs_filepath):
        # Check if file exists.
        _logger.exception("File does not exist")
        raise FileNotFoundError()

    interface_base_path, interface = os.path.split(interface_class_abs_filepath)
    if not interface.endswith(".py"):
        raise InvalidPyModelInterfaceClassException(
            "Python model interface class should be a '.py' file, got: {}".format(interface_class_filepath)
        )

    interface_class_filename_without_ext = interface.rsplit(".", 1)[0]
    _logger.debug("versioned_model_path=%s, interface_base_path=%s", versioned_model_path, interface_base_path)
    # TODO:
    #   Normalize all user passed in paths at some proper uniform place.
    if versioned_model_path != interface_base_path:
        try:
            # If interface_class_filename_without_ext can be imported, this means there is another module
            # that shares this name. In this case, we raise an Exception.
            _ = importlib.import_module(interface_class_filename_without_ext)
            raise InvalidPyModelInterfaceClassException(
                "Python model interface class module name: {} conflicts with existing modules".format(
                    interface_class_filename_without_ext
                )
            )
        except ModuleNotFoundError:
            diff_interface_base_path = True

    with open(interface_class_abs_filepath) as fh:
        source_code = fh.read()
    func_verbs = extract_func_names(source_code, interface_class_name)
    return {
        "interface_class_abs_dirpath": interface_base_path,
        "interface_class_filename_without_ext": interface_class_filename_without_ext,
        "interface_class_name": interface_class_name,
        "interface_func_defined": func_verbs,
        "diff_interface_base_path": diff_interface_base_path,
    }


def extract_func_names(source: str, model_class: str) -> List[str]:
    _logger.debug("extract_func_names,model_class=%s", model_class)
    funcs: List[str] = []
    module_tree = ast.parse(source)

    for node in ast.iter_child_nodes(module_tree):
        if isinstance(node, ast.ClassDef) and node.name == model_class:
            _logger.debug("model_class %s found", model_class)
            for class_node in node.body:
                if isinstance(class_node, ast.FunctionDef):
                    func_name: str = class_node.name
                    if re.match(r"_.*_", func_name) or func_name == ExporterVar.initialize_func_name:
                        # don't use internal methods as verbs
                        continue
                    funcs.append(func_name)
    _logger.info("verbs extracted=%s", funcs)
    if not funcs:
        raise InvalidModelException("No inference methods exposed")
    return funcs


def _extract_verb_func_py_model(
    versioned_model_path: str, py_model_init_params: str, validated: Dict
) -> Dict[str, Callable]:
    interface_class_abs_dirpath = validated["interface_class_abs_dirpath"]
    interface_class_filename_without_ext = validated["interface_class_filename_without_ext"]
    interface_class_name = validated["interface_class_name"]
    interface_func_defined: List[str] = validated["interface_func_defined"]
    diff_interface_base_path: bool = validated["diff_interface_base_path"]

    # Add versioned_model_path into system path.
    if os.path.isdir(versioned_model_path) and versioned_model_path not in sys.path:
        sys.path.insert(0, versioned_model_path)

        # add parent dir of versioned_model_path into sys path too
        parent_path = os.path.dirname(versioned_model_path)
        sys.path.insert(0, parent_path)

    # Append model interface class to system path if necessary.
    if diff_interface_base_path and interface_class_abs_dirpath not in sys.path:
        sys.path.append(interface_class_abs_dirpath)
        _logger.debug("appended py model interface class dir=%s to sys.path", interface_class_abs_dirpath)

    interface_class = locate(f"{interface_class_filename_without_ext}.{interface_class_name}")
    _logger.debug("interface_class=%s", type(interface_class))
    if not callable(interface_class):
        raise Exception("Python Model Interface failed to load.")
    else:
        interface_obj = interface_class()

    # initialize
    initialize_func = getattr(interface_obj, ExporterVar.initialize_func_name, None)
    if callable(initialize_func):
        kwargs = ujson.loads(py_model_init_params)
        if versioned_model_path:
            initialize_func(get_abspath(versioned_model_path), **kwargs)
        else:
            initialize_func(None, **kwargs)

    verb_funcs: Dict[str, Callable] = {}
    for func_name in interface_func_defined:
        verb_funcs[func_name] = getattr(interface_obj, func_name)
    _logger.info("verb_funcs=%s", verb_funcs)
    return verb_funcs


def batch_predict(data: Dict[str, Dict], verb_funcs):
    errs = {}
    results = {}

    for req_id, payload in data.items():
        verb = payload[PayloadKey.VERB]
        usr_data = payload[PayloadKey.USR_DATA]
        kwargs = payload[constants.KWARGS]

        if verb in verb_funcs:
            verb_func = verb_funcs[verb]
            try:
                try:
                    result = verb_func(usr_data, **kwargs)
                except TypeError:
                    result = verb_func(usr_data)
                results.update({req_id: result})
            except Exception as e:
                # Log exception here as predict error is caught here and no longer re-raised
                _logger.exception("error calling python model")
                errs[req_id] = python_model_error.generate_error(details=repr(e))
            finally:
                tracker.insert_anchor(req_id, Tracking.PYVMP_PREDICT_DONE.value)

        else:
            errs[req_id] = python_model_error.generate_error(details=f"'{verb}' is not supported")
            tracker.insert_anchor(req_id, Tracking.PYVMP_PREDICT_DONE.value)
    return results, errs


def extract_verb_func_py_wheel(
    dotted_path: str, py_model_init_params: str, versioned_model_path: str = ""
) -> Dict[str, Callable]:
    verb_funcs: Dict = {}
    try:
        imported_obj = locate(dotted_path)
    except ImportError:
        _logger.exception("Error importing dotted path module")

    if isinstance(imported_obj, type):
        # imported_obj is a class
        interface_obj = imported_obj()
        initialize_func = getattr(interface_obj, ExporterVar.initialize_func_name, None)
        if callable(initialize_func):
            kwargs = ujson.loads(py_model_init_params)
            initialize_func(versioned_model_path, **kwargs)
        interface_func_defined: List = []
        for func_name in dir(interface_obj):
            if re.match(r"_.*_", func_name) or func_name == ExporterVar.initialize_func_name:
                # don't use internal methods as verbs
                continue
            interface_func_defined.append(func_name)

        for func_name in interface_func_defined:
            verb_funcs[func_name] = getattr(interface_obj, func_name)
        _logger.info("verb_funcs=%s", verb_funcs)
        return verb_funcs
    else:
        method_name = (
            imported_obj.__qualname__  # type: ignore
        )  # see https://stackoverflow.com/questions/58108488/what-is-qualname-in-python
        verb_funcs[method_name] = imported_obj
    return verb_funcs
