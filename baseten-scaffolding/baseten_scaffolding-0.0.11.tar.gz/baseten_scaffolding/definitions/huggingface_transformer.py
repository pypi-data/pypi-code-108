from typing import Any, List, Dict

from baseten_scaffolding.errors import InvalidConfigurationError
from baseten_scaffolding.constants import HUGGINGFACE_TRANSFORMER
from baseten_scaffolding.definitions.base import WrittenModelScaffoldDefinition
from baseten_scaffolding.model_inference import parse_requirements_file, infer_huggingface_packages


def _task_id_to_build_args(hf_task: str = None):
    build_args = {
        'hf_task': hf_task,
        # for legacy reasons
        'task': hf_task,
        'has_hybrid_args': 'False',
        'has_named_args': 'False',
    }
    if hf_task in {'text-generation'}:
        build_args['has_hybrid_args'] = 'True'
    elif hf_task in {'zero-shot-classification'}:
        build_args['has_named_args'] = 'True'
    return build_args


class HuggingFaceTransformerPipelineScaffold(WrittenModelScaffoldDefinition):

    model_framework = HUGGINGFACE_TRANSFORMER
    _build_args = {}

    def __init__(
            self,
            model: Any = None,
            model_type: str = None,
            model_files: List[str] = None,
            data_files: List[str] = None,
            path_to_scaffold: str = None,
            requirements_file: str = None,
    ):
        if model_type is None:
            raise InvalidConfigurationError('This scaffold requires a huggingface task ID as a model type')

        super().__init__(
            model, model_type, model_files, data_files, path_to_scaffold, requirements_file
        )


    @property
    def model_framework_requirements(self):
        if self.requirements_file is None:
            return infer_huggingface_packages()
        return parse_requirements_file(self.requirements_file)

    @property
    def build_args(self) -> Dict:
        return self._build_args

    def serialize_model_to_directory(self, model_directory):
        self._build_args.update(_task_id_to_build_args(self.model_type))
