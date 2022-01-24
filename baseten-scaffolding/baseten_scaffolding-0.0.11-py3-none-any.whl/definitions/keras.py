from typing import Dict

from baseten_scaffolding.constants import KERAS
from baseten_scaffolding.definitions.base import WrittenModelScaffoldDefinition
from baseten_scaffolding.model_inference import infer_keras_packages, parse_requirements_file


class KerasScaffoldDefinition(WrittenModelScaffoldDefinition):

    model_framework = KERAS
    _build_args = {}

    @property
    def model_framework_requirements(self):
        if self.requirements_file is None:
            return infer_keras_packages()
        return parse_requirements_file(self.requirements_file)

    @property
    def build_args(self) -> Dict:
        return self._build_args

    def serialize_model_to_directory(self, model_directory):
        self.model.save(model_directory)
