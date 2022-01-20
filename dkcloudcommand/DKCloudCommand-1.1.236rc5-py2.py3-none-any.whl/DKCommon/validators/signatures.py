from inspect import Signature, _empty
from typing import Optional, Type


def assert_return_type(signature: Signature, function_name: str, return_type=Optional[Type]) -> None:
    """
    Checks a signature's return type. Specifying None is equivalent to _empty
    """
    if return_type is None:
        return_type = _empty
    assert (
        signature.return_annotation == return_type or signature.return_annotation is None
    ), f"{function_name}'s return type has changed. This may break code elsewhere.\nExpected {return_type} but was {signature.return_annotation}."


def assert_signature_parameter(
    signature: Signature, function_name: str, parameter_name: str, parameter_type=Optional[Type]
) -> None:
    """Checks a individual parameter in the signature to see if its name or type has changed"""
    assert signature.parameters.get(
        parameter_name
    ), f"{function_name}'s parameter '{parameter_name}' name has changed. This may break code elsewhere."

    if parameter_type is None:
        parameter_type = _empty
    assert signature.parameters.get(parameter_name).annotation == parameter_type, (
        f"{function_name}'s parameter '{parameter_name}' type has changed.\n"
        f"Type was {parameter_type}, but now is {signature.parameters.get(parameter_name).annotation}.\n"
        "This may break code elsewhere."
    )
