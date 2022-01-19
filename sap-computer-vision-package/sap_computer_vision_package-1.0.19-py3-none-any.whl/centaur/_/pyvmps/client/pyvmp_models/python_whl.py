from typing import Dict
from centaur._.pyvmps.client.pyvmp_models.python import PymodelPyvmp
from centaur._.pyvmps.models.base_model import Model
from centaur._.pyvmps.models.python.utils import extract_verb_func_py_wheel

from centaur._.pyvmps.logger.get_logger import get_logger

_logger = get_logger(__name__)


class PythonWheel(PymodelPyvmp):
    """PythonWheel loads a model that is installed as a wheel"""

    def __init__(self, dotted_path: str, versioned_model_path: str, py_model_init_params: str):
        self.dotted_path = dotted_path
        self.versioned_model_path = versioned_model_path
        self.py_model_init_params = py_model_init_params
        _logger.debug(
            "dotted_path=%s, versioned_model_path=%s, py_model_init_params=%s",
            self.dotted_path,
            self.versioned_model_path,
            self.py_model_init_params,
        )

    def load(self) -> bool:
        self.verb_funcs: Dict = extract_verb_func_py_wheel(
            self.dotted_path, self.py_model_init_params, self.versioned_model_path
        )
        self.set_verb_funcs(self.verb_funcs)

        # call load method of class Model
        return Model.load(self)
