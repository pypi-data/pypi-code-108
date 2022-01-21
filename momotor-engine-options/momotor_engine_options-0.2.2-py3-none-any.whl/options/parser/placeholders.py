import typing

from momotor.options.providers import Providers
from momotor.options.parser.reference import resolve_reference_value


def replace_placeholders(
    value: typing.Optional[str], bundles: Providers, *,
    value_processor: typing.Callable[[typing.Optional[str]], str] = None
) -> typing.Optional[str]:
    """ Replace all :ref:`placeholders <placeholder>` in `value` with their resolved values.
    Placeholders are resolved recursively, i.e. if a resolved value contains more placeholders,
    these will be resolved as well.

    :param value: the string containing placeholders to resolve
    :param bundles: the bundles to resolve the references too
    :param value_processor: a callable that is called with every resolved value, can be used to modify placeholders.
                            If not supplied, uses :py:obj:`str` to cast the returned value to a string.
    :return: the `value` with all placeholders resolved
    """
    if not value:
        return value

    assert isinstance(value, str)

    if value_processor is None:
        value_processor = str

    remaining = value
    result = ''

    while '${' in remaining:
        prefix, remaining = remaining.split('${', 1)
        result += prefix

        if prefix.endswith('$'):
            result += '{'
            continue

        value, remaining = resolve_reference_value(remaining, bundles)

        if value is None:
            result += '${'
            continue

        if '}' not in remaining:
            raise ValueError

        garbage, remaining = remaining.split('}', 1)
        if garbage.strip():
            raise ValueError

        result += replace_placeholders(
            value_processor(value), bundles,
            value_processor=value_processor
        )

    result += remaining

    return result
