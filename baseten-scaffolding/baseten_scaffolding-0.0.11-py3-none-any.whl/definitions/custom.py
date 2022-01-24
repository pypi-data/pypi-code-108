import ast
from typing import Any, List, Dict
from pathlib import Path

from baseten_scaffolding.constants import CUSTOM
from baseten_scaffolding.definitions.base import WrittenModelScaffoldDefinition
from baseten_scaffolding.errors import ModelFilesMissingError, ModelClassImplementationError
from baseten_scaffolding.model_inference import parse_requirements_file


def _validate_custom_model_definition(class_name: str, model_files: List[str]) -> str:
    """Asserts that the model class is in the files and conforms to the API

    Args:
        class_name (str): The class_name for the model.
        model_files List[str]): A list of files to be packaged as the model deployment.

    Returns:
        (str): The validated file of the class_name for the model.

    Raises:
        ModelFilesMissingError: If a file defining the model class is not supplied.
        ModelClassImplementationError: If the model class does not implement the required `load` and
            `predict` methods.

    """
    if not model_files:
        raise ModelFilesMissingError(f'The file defining the model class `{class_name}` is missing.')
    has_supplied_model_class_definition = False
    python_files = [f for f in model_files if f.endswith('.py')]
    class_def_file = None
    for filepath in python_files:
        with open(filepath, 'r') as _file:
            file_contents = _file.read()
            parsed_contents = ast.parse(file_contents)
            model_class_definion_file = [
                stmt for stmt in parsed_contents.body
                if type(stmt) == ast.ClassDef
                and stmt.name == class_name
            ]
            if model_class_definion_file:
                cls_function_names = [stmt.name for stmt in model_class_definion_file[0].body]
                if 'load' not in cls_function_names or 'predict' not in cls_function_names:
                    raise ModelClassImplementationError(f'The model class in {filepath} does not \
                        implement the required `load` and `predict` methods.')
                class_def_file = Path(filepath).name
                has_supplied_model_class_definition = True
                break
    if not has_supplied_model_class_definition:
        raise ModelFilesMissingError(f'The file defining the model class `{class_name}` is missing.')
    return class_def_file


class CustomScaffoldDefinition(WrittenModelScaffoldDefinition):

    model_framework = CUSTOM
    model_filename = 'model.zip'
    _build_args = {}

    def __init__(
            self,
            model: Any,
            model_files: List[str] = None,
            data_files: List[str] = None,
            path_to_scaffold: str = None,
            requirements_file: str = None,
            model_class: str = None
    ):
        self.model_class = model_class
        super().__init__(
            model, CUSTOM, model_files, data_files, path_to_scaffold, requirements_file
        )

    @property
    def model_framework_requirements(self) -> Dict:
        if self.requirements_file is None:
            return {}
        return parse_requirements_file(self.requirements_file)

    @property
    def build_args(self) -> Dict:
        return self._build_args

    def serialize_model_to_directory(self, model_directory):
        if self.model_class is not None:
            class_def_file = _validate_custom_model_definition(self.model_class, self.model_files)

            self._build_args['MODEL_CLASS'] = self.model_class
            self._build_args['MODEL_CLASS_DEFINITION_FILE'] = class_def_file
