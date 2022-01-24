import ast
import pathlib
from typing import Any, List, Dict

from baseten_scaffolding.constants import PYTORCH
from baseten_scaffolding.definitions.base import WrittenModelScaffoldDefinition
from baseten_scaffolding.errors import ModelFilesMissingError
from baseten_scaffolding.model_inference import infer_pytorch_packages, parse_requirements_file


def _serialize_pytorch_model(model: Any, path_to_weight_file: str, model_files: List[str] = None) -> Dict:
    """Serializes a PyTorch model as a .pt file.

    Args:
        model (Any): The model object.
        path_to_weight_file (str): Destination for the weight file
        model_files List(str): Files to be includeded

    Returns:
        tempfile.NamedTemporaryFile: A temporary zipfile.ZipFile wrapper.
    """
    model_class = model.__class__
    class_name = model_class.__name__
    if not model_files:
        raise ModelFilesMissingError(f'The file defining the PyTorch model class `{class_name}` is missing.')

    has_supplied_model_class_definition = False
    model_files_dict = {'files': {}, 'model_class': class_name}

    for filepath in model_files:
        with open(filepath, 'r') as _file:
            file_contents = _file.read()
            model_files_dict['files'][filepath] = file_contents
            parsed_contents = ast.parse(file_contents)
            is_model_class_definion_file = (
                True if [
                    stmt for stmt in parsed_contents.body
                    if type(stmt) == ast.ClassDef
                    and stmt.name == class_name
                ] else False)
            if is_model_class_definion_file:
                model_files_dict['class_def_file'] = filepath
            has_supplied_model_class_definition = has_supplied_model_class_definition or is_model_class_definion_file

    if not has_supplied_model_class_definition:
        raise ModelFilesMissingError(f'The file defining the PyTorch model class `{class_name}` is missing.')

    import torch
    torch.save(model.state_dict(), path_to_weight_file)
    return model_files_dict


class PyTorchScaffoldDefinition(WrittenModelScaffoldDefinition):

    model_framework = PYTORCH
    model_filename = 'model.pt'
    _build_args = {}

    @property
    def model_framework_requirements(self):
        if self.requirements_file is None:
            return infer_pytorch_packages()
        return parse_requirements_file(self.requirements_file)

    @property
    def build_args(self) -> Dict:
        return self._build_args

    def serialize_model_to_directory(self, model_directory):
        path_to_weight_file = pathlib.Path(model_directory, self.model_filename)
        model_files_dict = _serialize_pytorch_model(self.model, str(path_to_weight_file), self.model_files)

        self._build_args['MODEL_CLASS'] = model_files_dict['model_class']
        self._build_args['MODEL_CLASS_DEFINITION_FILE'] = model_files_dict['class_def_file']
