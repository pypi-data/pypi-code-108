from vtb_django_utils.model_versions.models import VersionModel, VersionedModelMixin
from vtb_django_utils.model_versions.utils.consts import VERSION_MODEL_SUFFIX
from vtb_django_utils.utils.inspect import get_module_classes_inheritor


def get_version_model_name(versioned_model_name: str) -> str:
    """ Возвращает имя модели с версиями для заданной модели """
    return f'{versioned_model_name}{VERSION_MODEL_SUFFIX}'


def get_version_models(module_name: str):
    """ Возвращает список моделей с версиями других моделей """
    return get_module_classes_inheritor(module_name, VersionModel)


def get_versioned_models(module_name: str):
    """ Возвращает список версионных моделей """
    return get_module_classes_inheritor(module_name, VersionedModelMixin)
