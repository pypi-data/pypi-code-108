from typing import Callable, Dict, List

from centaur._.pyvmps.logger.get_logger import get_logger
from centaur._.pyvmps.models.base_model import Model
from centaur._.pyvmps.models.python.utils import _validate_model_config, _extract_verb_func_py_model
from centaur._.pyvmps.utils.common import abs_and_normalize_path

_logger = get_logger(__name__)


class PythonModel(Model):
    """PythonModel."""

    def __init__(
        self,
        versioned_model_path: str,
        py_model_interface_filepath: str,
        py_model_interface_class_name: str,
        py_model_init_params: str,
    ):
        self.versioned_model_path = versioned_model_path
        self.py_model_interface_filepath = py_model_interface_filepath
        self.py_model_interface_class_name = py_model_interface_class_name
        self.py_model_init_params = py_model_init_params

    def set_verb_funcs(self, verb_funcs: Dict[str, Callable]):
        _logger.debug("init python model")
        for verb, func in verb_funcs.items():
            _logger.debug("verb=%s,func=%s", verb, func)
            setattr(self, verb, func)
        self._log_supported_methods()

    def load(self) -> bool:
        """load python model

        :param versioned_model_path: path to python model
        :type versioned_model_path: str
        :param model_attrs: Tuple containing path to python interface class, and interface class name
        :type model_attrs: Tuple[str, str]
        :param model_class:
        :type model_class: Type[Model]
        :rtype: Tuple[Callable, Any]
        """
        versioned_model_path = abs_and_normalize_path(self.versioned_model_path)
        self.validated: Dict = _validate_model_config(
            self.versioned_model_path, self.py_model_interface_filepath, self.py_model_interface_class_name
        )
        _logger.debug("Model validated by PyModelLoader")
        self.verb_funcs: Dict = _extract_verb_func_py_model(
            versioned_model_path, self.py_model_init_params, self.validated
        )

        self.set_verb_funcs(self.verb_funcs)
        return super().load()

    def _log_supported_methods(self):
        _logger.info("PyModel|supported methods: %s", ",".join([verb for verb in self.verb_funcs.keys()]))

    def predict(self, data: Dict, **kwargs):
        """Empty implementation, real method set in load()"""

    def get_verbs(self) -> List[str]:
        return [verb for verb in self.verb_funcs.keys()]
