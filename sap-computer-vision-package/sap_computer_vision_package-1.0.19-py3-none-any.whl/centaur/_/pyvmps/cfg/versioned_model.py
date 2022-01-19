from typing import List, Dict


class _VersionedModel:
    """VersionedModel defines versioned moedl specific configs/settings"""

    def __init__(self):
        self._py_pre_proc_func_import_path = []
        self._py_post_proc_func_import_path = []
        self._py_model_init_params = "{}"

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, v: str):
        self._id = v

    @property
    def model_type(self):
        return self._model_type

    @model_type.setter
    def model_type(self, v: str):
        self._model_type = v

    @property
    def model_path(self):
        return self._model_path

    @model_path.setter
    def model_path(self, v: str):
        self._model_path = v

    @property
    def py_model_interface_filepath(self):
        return self._py_model_interface_filepath

    @py_model_interface_filepath.setter
    def py_model_interface_filepath(self, v: str):
        self._py_model_interface_filepath = v

    @property
    def py_model_interface_class_name(self):
        return self._py_model_interface_class_name

    @py_model_interface_class_name.setter
    def py_model_interface_class_name(self, v: str):
        self._py_model_interface_class_name = v

    @property
    def py_whl_model_interface_import_path(self) -> str:
        return self._py_whl_model_interface_import_path

    @py_whl_model_interface_import_path.setter
    def py_whl_model_interface_import_path(self, v: str):
        self._py_whl_model_interface_import_path = v

    @property
    def py_pre_proc_func_import_path(self) -> List[str]:
        return self._py_pre_proc_func_import_path

    @py_pre_proc_func_import_path.setter
    def py_pre_proc_func_import_path(self, v: List[str]):
        self._py_pre_proc_func_import_path = v

    @property
    def py_post_proc_func_import_path(self) -> List[str]:
        return self._py_post_proc_func_import_path

    @py_post_proc_func_import_path.setter
    def py_post_proc_func_import_path(self, v: List[str]):
        self._py_post_proc_func_import_path = v

    @property
    def py_model_init_params(self) -> str:
        return self._py_model_init_params

    @py_model_init_params.setter
    def py_model_init_params(self, v: str):
        self._py_model_init_params = v

    @property
    def target_cpus(self):
        return self._target_cpus

    @target_cpus.setter
    def target_cpus(self, v: List):
        if isinstance(v, list):
            self._target_cpus = v
        else:
            raise ValueError("provided target cpus: {} is not a valid list".format(v))

    @property
    def trailing_cpus(self):
        return self._trailing_cpus

    @trailing_cpus.setter
    def trailing_cpus(self, v: int):
        if isinstance(v, list):
            self._trailing_cpus = v
        else:
            raise ValueError("provided trailing cpus: {} is not a valid list".format(v))

    @property
    def niceness(self):
        return self._niceness

    @niceness.setter
    def niceness(self, v: int):
        self._niceness = v
