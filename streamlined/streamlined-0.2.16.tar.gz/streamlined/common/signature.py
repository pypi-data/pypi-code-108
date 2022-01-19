import inspect
from inspect import Parameter, Signature
from itertools import chain
from typing import Any, Callable, Iterable, List, Sequence


def merge(*signatures: Signature, return_annotation: Any = Signature.empty) -> Signature:
    parameters: List[Parameter] = []

    if any(
        parameter.kind is Parameter.VAR_POSITIONAL or parameter.kind is Parameter.VAR_KEYWORD
        for parameter in chain.from_iterable(
            signature.parameters.values() for signature in signatures
        )
    ):
        raise ValueError("variable argument cannot be merged")

    for kind in [
        Parameter.POSITIONAL_ONLY,
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.KEYWORD_ONLY,
    ]:
        for signature in signatures:
            parameters.extend(
                filter(lambda parameter: parameter.kind == kind, signature.parameters.values())
            )

    return Signature(parameters, return_annotation=return_annotation)


def to_definition_str(signature: Signature) -> str:
    return "(" + ", ".join(map(str, signature.parameters.values())) + ")"


def to_invocation_str(
    funcname: str, signature: Signature, *var_args: str, **var_kwargs: str
) -> str:
    sep = ", "

    def parameter_to_str(parameter: Parameter) -> str:
        if (
            parameter.kind is Parameter.POSITIONAL_ONLY
            or parameter.kind is Parameter.POSITIONAL_OR_KEYWORD
        ):
            return parameter.name
        elif parameter.kind is Parameter.KEYWORD_ONLY:
            return f"{parameter.name}={var_kwargs.pop(parameter.name, parameter.name)}"
        elif parameter.kind is Parameter.VAR_POSITIONAL:
            return sep.join(var_args)
        else:  # parameter.kind is Parameter.VAR_KEYWORD:
            return sep.join(f"{name}={value}" for name, value in var_kwargs.items())

    parameter_str = sep.join(map(parameter_to_str, signature.parameters.values()))
    return f"{funcname}({parameter_str})"
