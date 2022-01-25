# Copyright IBM Corp. 2021. All Rights Reserved.

import logging
from typing import Union, Iterable, Any, Sequence, TYPE_CHECKING, Optional, \
    overload, Mapping

if TYPE_CHECKING:
    from .cpd_paths import CpdScope


class ClientError(ValueError):
    def __init__(self, error_msg: str, reason: Union[str, Exception] = None):
        self.error_msg = error_msg
        self.reason = reason
        logging.getLogger(__name__).debug(str(self))

    def __str__(self):
        return str(self.error_msg) + ('\nReason: ' + str(self.reason) if self.reason is not None else '')


class PublicCloudOnlyError(ClientError):
    @overload
    def __init__(self, kind: Optional[str] = None): ...
    @overload
    def __init__(self, kind: str, feature: str): ...

    def __init__(self, kind: Optional[str] = None, feature: Optional[str] = None):
        if kind is None:
            feature_str = 'Feature used'
        elif feature is None:
            feature_str = f'{kind} used'
        else:
            feature_str = f'{kind} "{feature}"'
        msg = f'{feature_str} is only available on public cloud, but the URL provided is private cloud.'
        super().__init__(msg, None)

class NoSuchOverloadError(ClientError):
    def __init__(self, fn: str, args: Sequence[Any], kwargs: Mapping[str, Any], reason: Union[str, Exception] = None):
        args_str = ', '.join([str(arg) for arg in args])
        kwargs_str = ', '.join([f'{k}={v}' for k,v in kwargs.items()])
        if args_str != '' and kwargs_str != '':
            args_kwargs_str = args_str + ', ' + kwargs_str
        else:
            args_kwargs_str = args_str + kwargs_str

        msg = f"No overload: {fn}({args_kwargs_str})"
        super().__init__(msg, reason)

class MissingValueError(ClientError):
    def __init__(self, value_name: Union[str, Iterable[str]], reason: Union[str, Exception] = None):
        if isinstance(value_name, str):
            msg = 'No \"' + value_name + '\" provided.'
        else:
            variants = ['\"{}\"'.format(val) for val in value_name]
            variants_str = ', '.join(variants)
            msg = 'None of ' + variants_str + ' provided.'
        super().__init__(msg, reason)

class FilesResultsNotSupportedError(ClientError):
    def __init__(self, output_name: str, reason: Union[str, Exception] = None):
        msg = 'Unsupported: passing files as results. File passed as output \"' + output_name + '\". Please read the file into memory via .read() method and pass its result instead.'
        super().__init__(msg, reason)

class ConfiguredMissingError(ClientError):
    def __init__(self, service_name: str, value_name: str, reason: Union[str, Exception] = None):
        if isinstance(value_name, str):
            msg = f"Config for {service_name} resulted in no '{value_name}'."
        else:
            variants = ['\"{}\"'.format(val) for val in value_name]
            variants_str = ', '.join(variants)
            msg = f"Config for {service_name} resulted in none of {variants_str} provided."
        super().__init__(msg, reason)

class UnexpectedTypeError(ClientError):
    def __init__(self, el_name: str, expected_type: type, actual_type: type):
        expected_str = '\'{}\''.format(format_type(expected_type)) if type(expected_type) == type else expected_type
        actual_str = format_type(actual_type)
        msg = 'Unexpected type of \'{}\', expected: {}, actual: \'{}\'.'.format(el_name, expected_str, actual_str)
        super().__init__(msg)

class ConfiguredTypeError(ClientError):
    def __init__(self, service_name: str, el_name: str, expected_type: type, actual_type: type):
        expected_str = '\'{}\''.format(format_type(expected_type)) if type(expected_type) == type else expected_type
        actual_str = format_type(actual_type)
        msg = f"Config for {service_name} resulted in unexpected type of '{el_name}', expected: {expected_str}, actual: '{actual_str}'."
        super().__init__(msg)

class WmlServiceCNameNotValidError(ClientError):
    def __init__(self, crn: str, ctype: str, allowed_values: Sequence[str]):
        allowed_values_str = "|".join([f'"{val}"' for val in allowed_values])
        msg = f"CRN \"{crn}\" is not a valid WML resource, expected \"{allowed_values_str}\" cname but got \"{ctype}\"."
        super().__init__(msg)

class WmlServiceNameNoPrefixError(ClientError):
    def __init__(self, crn: str, service_name: str, prefix: str):
        msg = f"CRN \"{crn}\" is not a valid WML resource, expected \"{prefix}\" service name part but got \"{service_name}\"."
        super().__init__(msg)

class WmlServiceNameUnknownTypeError(ClientError):
    def __init__(self, crn: str, service_name: str):
        msg = f"CRN \"{crn}\" contains service name \"{service_name}\", the url of which is unknown."
        super().__init__(msg)

class NoWmlInstanceError(ClientError):
    format_name: str
    def __init__(self, scope: 'CpdScope', reason: Union[str, Exception] = None):
        super().__init__(f'No WML instance available for scope {str(scope)}. Please make sure that a WML instance is associated with this scope.', reason)

class WmlUnknownAuthMethodError(ClientError):
    format_name: str
    def __init__(self, scope: 'CpdScope', method: str, reason: Union[str, Exception] = None):
        super().__init__(f'Unknown authorisation method was used for WML instance for scope {str(scope)}: "{method}".', reason)


class JsonParsingError(ClientError):
    def __init__(self, value: Any, reason: Union[str, Exception] = None):
        super().__init__('Value \"' + str(value) + '\" is not valid json.', reason)


class JsonFormatError(ClientError):
    format_name: str
    def __init__(self, value: Any, msg: str, reason: Union[str, Exception] = None):
        super().__init__(f'Value "{str(value)}" is not valid {self.format_name} json, {msg}.', reason)

class JsonFormatNoFieldError(JsonFormatError):
    format_name: str
    def __init__(self, value: Any, field: str, reason: Union[str, Exception] = None):
        super().__init__(value, f'lacks field: "{field}"', reason)

class JsonFormatFieldWrongTypeError(JsonFormatError):
    def __init__(self, value: Any, field: str, expected_type: type, actual_type: type, reason: Union[str, Exception] = None):
        expected_str = '\'{}\''.format(format_type(expected_type)) if type(expected_type) == type else expected_type
        actual_str = format_type(actual_type)
        super().__init__(value, f'field "{field}" has wrong type, expected: {expected_str}, got: \'{actual_str}\'', reason)


class ScopeResponseNoFieldError(JsonFormatNoFieldError):
    format_name: str =  "scope response"

class ScopeResponseFieldWrongTypeError(JsonFormatFieldWrongTypeError):
    format_name: str =  "scope response"

class StoragePropertiesNoFieldError(JsonFormatNoFieldError):
    format_name: str =  "storage properties"

class StoragePropertiesFieldWrongTypeError(JsonFormatFieldWrongTypeError):
    format_name: str =  "storage properties"

class CredentialsNoFieldError(JsonFormatNoFieldError):
    format_name: str =  "credentials"

class CredentialsFieldWrongTypeError(JsonFormatFieldWrongTypeError):
    format_name: str =  "credentials"


class OfCpdPathError(ClientError):
    def __init__(self, value: Any, reason: Union[str, Exception] = None):
        super().__init__('Value of OF_CPD_PATH, \"' + str(value) + '\" is not valid CPD Path.', reason)

class OutputCpdPathError(ClientError):
    def __init__(self, output_name: str, value: Any, reason: Union[str, Exception] = None):
        super().__init__(f'Value of output "{output_name}": "{str(value)}" is not valid CPD Path.', reason)

class RelativeCpdPathButNoDefaultScopeError(ClientError):
    def __init__(self, output_name: str, value: Any, reason: Union[str, Exception] = None):
        super().__init__(f'Value of output "{output_name}": "{str(value)}" is relative, but no default CPD Scope provided.', reason)


def format_type(ty: type) -> str:
    if type(ty).__module__ in {'__builtin__', 'builtins'}:
        # builtin -> just show its name
        return ty.__name__
    else:
        # otherwise also show its module
        return f"{ty.__module__}.{ty.__name__}"
