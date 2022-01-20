from __future__ import annotations

from enum import Enum, auto
from functools import partial
from inspect import Parameter, _ParameterKind
from typing import (
    Any,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

from .dictionary import update_with_callable
from .predicates import IS_DICT, IS_SEQUENCE

T = TypeVar("T")


class TemplateParameterDefault(Enum):
    EMPTY = Parameter.empty
    USE_NAME = auto()
    USE_DEFAULT = auto()

    @classmethod
    def of(cls, value: Any) -> TemplateParameterDefault:
        if isinstance(value, cls):
            return value
        else:
            return TemplateParameterDefault.USE_DEFAULT

    def evaluate(self, **kwargs: Any) -> Any:
        if self is TemplateParameterDefault.EMPTY:
            return self.value
        elif self is TemplateParameterDefault.USE_NAME:
            return kwargs["name"]
        else:
            return kwargs["default"]


class TemplateParameter:
    kind: ClassVar[_ParameterKind] = Parameter.POSITIONAL_OR_KEYWORD

    def __init__(
        self,
        name: str,
        default: Union[Any, TemplateParameterDefault] = TemplateParameterDefault.EMPTY,
        annotation: Any = Parameter.empty,
    ) -> None:
        self.name = name
        self.default = default
        self.annotation = annotation

    @staticmethod
    def resolve_name(name: str, substitutions: Optional[Mapping[str, Any]] = None) -> str:
        if substitutions is None:
            return name
        return name.format_map(substitutions)

    @staticmethod
    def resolve_default(default: Any, substitutions: Optional[Mapping[str, Any]] = None) -> Any:
        if substitutions is None:
            substitutions = dict()
        return TemplateParameterDefault.of(default).evaluate(**substitutions)

    def as_parameter(self) -> Parameter:
        return Parameter(self.name, self.kind, default=self.default, annotation=self.annotation)

    def resolve_value(self, dictionary: Mapping[str, Any]) -> Any:
        return dictionary.get(self.name, self.default)

    def replace(self, **changes: Any) -> TemplateParameter:
        fields = {"name": self.name, "default": self.default}

        fields.update(changes)
        update_with_callable(
            fields,
            "default",
            partial(self.resolve_default, substitutions=fields),
        )

        return TemplateParameter(**fields)

    def replace_with_substitutions(
        self, substitutions: Optional[Mapping[str, Any]] = None
    ) -> TemplateParameter:
        if substitutions:
            substituted_name = self.resolve_name(self.name, substitutions)
            return self.replace(name=substituted_name)

    def resolve(
        self, values: Mapping[str, Any], substitutions: Optional[Mapping[str, Any]]
    ) -> Tuple[TemplateParameter, Any]:
        updated_template = self.replace_with_substitutions(substitutions)
        return updated_template, updated_template.resolve_value(values)


class Template(Generic[T]):
    @staticmethod
    def is_parameter(value: Any) -> bool:
        return isinstance(value, TemplateParameter)

    @staticmethod
    def _substitute_parameters(
        parameters: Iterable[TemplateParameter],
        values: Mapping[Any, Any],
        name_substitutions: Optional[Mapping[str, Any]] = None,
    ) -> Dict[TemplateParameter, Any]:
        substituted_parameters: Dict[TemplateParameter, Any] = dict()

        for parameter in parameters:
            try:
                updated_parameter, value = parameter.resolve(values, name_substitutions)
            except (KeyError, ValueError):
                value = parameter
            substituted_parameters[parameter] = value

        return substituted_parameters

    @classmethod
    def get_parameters(cls, template: Any) -> Iterable[TemplateParameter]:
        if IS_DICT(template):
            for k, v in template.items():
                yield from cls.get_parameters(k)
                yield from cls.get_parameters(v)
        elif IS_SEQUENCE(template):
            for item in template:
                yield from cls.get_parameters(item)
        elif isinstance(template, TemplateParameter):
            yield template

    @classmethod
    def _substitute_template(
        cls, template: Any, parameter_substitutions: Mapping[TemplateParameter, Any]
    ) -> Any:
        if IS_DICT(template):
            return {
                cls._substitute_template(k, parameter_substitutions): cls._substitute_template(
                    v, parameter_substitutions
                )
                for k, v in template.items()
            }
        elif IS_SEQUENCE(template):
            return [cls._substitute_template(item, parameter_substitutions) for item in template]
        else:
            return parameter_substitutions.get(template, template)

    def __init__(self, template: T) -> None:
        self._init_template(template)

    def _init_template(self, template: T) -> None:
        self.template = template
        self._init_parameters()

    def _init_parameters(self) -> None:
        self.parameters = list(self.get_parameters(self.template))

    def substitute(
        self,
        values: Optional[Mapping[str, Any]] = None,
        name_substitutions: Optional[Mapping[str, Any]] = None,
    ) -> T:
        if values is None:
            values = dict()

        parameters = self.get_parameters(self.template)
        parameter_substitutions = self._substitute_parameters(
            parameters, values, name_substitutions
        )
        return self._substitute_template(self.template, parameter_substitutions)
