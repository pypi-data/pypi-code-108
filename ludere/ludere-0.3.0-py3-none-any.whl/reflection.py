import inspect
from typing import Type, List


def resolve_constructor_parameter_types(cls: Type) -> List[Type]:
    signature = inspect.signature(cls.__init__)

    parameters = dict(signature.parameters)
    parameters.pop("self")
    parameters.pop("args", None)
    parameters.pop("kwargs", None)

    required_parameters = [p for n, p in parameters.items() if p.default is inspect.Parameter.empty]
    types = [p.annotation for p in required_parameters]

    return types


def resolve_function_parameter_types(f) -> List[Type]:
    signature = inspect.signature(f)

    parameters = dict(signature.parameters)
    parameters.pop("args", None)
    parameters.pop("kwargs", None)

    required_parameters = [p for n, p in parameters.items() if p.default is inspect.Parameter.empty]
    types = [p.annotation for p in required_parameters]

    return types


def has_return_type(f) -> bool:
    signature = inspect.signature(f)

    return signature.return_annotation != signature.empty
