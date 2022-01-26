import sys

from vatis.asr_commons.config import Language
from vatis.asr_commons.custom_models.model import Model, ModelType
from vatis.asr_commons.custom_models import ro_RO, en_GB

from pathlib import Path

__all__ = (
    'Model',
    'ModelType'
    'ro_RO',
    'en_GB'
    'get_default',
    'compute_model_path'
)


def get_default(language: Language) -> Model:
    try:
        current_module = sys.modules[__name__]

        lang_module = current_module.__getattribute__(language.value)

        return lang_module.default
    except AttributeError:
        msg = f'Models for language {language.value} are not implemented yet'
        print(msg)
        raise ModuleNotFoundError(msg)


def compute_model_path(custom_model: Model, model_type: ModelType, extension_no_dot: str) -> Path:
    file_name: str = f'{str(custom_model.uid)}_{custom_model.language.value}_{model_type.value}.{extension_no_dot}'
    path: Path = Path(custom_model.language.value, str(custom_model.uid), file_name)

    return path
