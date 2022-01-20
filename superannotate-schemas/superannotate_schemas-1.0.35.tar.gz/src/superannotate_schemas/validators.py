import copy

from abc import ABCMeta
from abc import abstractmethod
from typing import Any
from typing import Type

from superannotate_schemas.utils import wrap_error
from superannotate_schemas.schemas.external import PixelAnnotation as ExternalPixelAnnotation
from superannotate_schemas.schemas.external import VectorAnnotation as ExternalVectorAnnotation
from superannotate_schemas.schemas.external import VideoAnnotation as ExternalVideoAnnotation
from superannotate_schemas.schemas.external import DocumentAnnotation as ExternalDocumentAnnotation

from superannotate_schemas.schemas.internal import PixelAnnotation as InternalPixelAnnotation
from superannotate_schemas.schemas.internal import VectorAnnotation as InternalVectorAnnotation
from superannotate_schemas.schemas.internal import VideoAnnotation as InternalVideoAnnotation
from superannotate_schemas.schemas.internal import DocumentAnnotation as InternalDocumentAnnotation


from superannotate_schemas.schemas.base import BaseModel
from pydantic import Extra
from pydantic import ValidationError


class BaseValidator(metaclass=ABCMeta):
    MODEL: Type[BaseModel]

    def __init__(self, data: Any, allow_extra: bool = True):
        self.data = data
        self._validation_output = None
        self._extra = Extra.allow if allow_extra else Extra.forbid

    @classmethod
    def validate(cls, data: Any, extra=True):
        return cls.MODEL(**data)

    def _validate(self):
        model = copy.deepcopy(self.MODEL)
        model.Config.extra = self._extra
        self.data = model(**self.data).dict(by_alias=True, exclude_none=True)

    @abstractmethod
    def is_valid(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def generate_report(self) -> str:
        raise NotImplementedError


class BaseSchemaValidator(BaseValidator):
    MODEL = BaseModel()

    def is_valid(self) -> bool:
        try:
            self._validate()
        except ValidationError as e:
            self._validation_output = e
        return not bool(self._validation_output)

    def generate_report(self) -> str:
        return wrap_error(self._validation_output)


class ValidatorFactory:
    @staticmethod
    def _get_default_schema():
        return type('CopyOfB', BaseSchemaValidator.__bases__, dict(BaseSchemaValidator.__dict__))

    @staticmethod
    def get_validator(model: Any):
        schema = ValidatorFactory._get_default_schema()
        schema.MODEL = model
        return schema

    def __class_getitem__(cls, item):
        return cls.get_validator(item)


class AnnotationValidators:
    VALIDATORS = {
        "pixel": (
            ValidatorFactory.get_validator(ExternalPixelAnnotation),
            ValidatorFactory.get_validator(InternalPixelAnnotation)
        ),
        "vector": (
            ValidatorFactory.get_validator(ExternalVectorAnnotation),
            ValidatorFactory.get_validator(InternalVectorAnnotation)
        ),
        "video": (
            ValidatorFactory.get_validator(ExternalVideoAnnotation),
            ValidatorFactory.get_validator(InternalVideoAnnotation)
        ),
        "document": (
            ValidatorFactory.get_validator(ExternalDocumentAnnotation),
            ValidatorFactory.get_validator(InternalDocumentAnnotation)
        )
    }

    @classmethod
    def get_validator(cls, project_type: str, internal=False):
        idx = 1 if internal else 0
        return cls.VALIDATORS[project_type.lower()][idx]

