from typing import NamedTuple, Tuple, Union, Type

import pytest

from arthurai.client.helper import construct_url
from arthurai.common.exceptions import UserValueError


class ConstructUrlTestCase(NamedTuple):
    parts: Tuple[str, ...]
    validate: bool
    default_https: bool
    expected: Union[str, Type[BaseException]]


CASES = [ConstructUrlTestCase(parts=("https://arthur.ai", "/api/", "/endpoint"), validate=True, default_https=True,
                              expected="https://arthur.ai/api/endpoint"),
         ConstructUrlTestCase(parts=("https://arthur.ai/", "api", "endpoint/value?foo=bar&baz=qux"), validate=True,
                              default_https=True, expected="https://arthur.ai/api/endpoint/value?foo=bar&baz=qux"),
         ConstructUrlTestCase(parts=("arthur.ai", "/api", "/endpoint"), validate=True, default_https=True,
                              expected="https://arthur.ai/api/endpoint"),
         ConstructUrlTestCase(parts=("arthur.ai", "/api", "/endpoint/"), validate=False, default_https=False,
                              expected="arthur.ai/api/endpoint"),
         ConstructUrlTestCase(parts=("arthur.ai", "/api", "/endpoint/"), validate=True, default_https=False,
                              expected=UserValueError),
         ConstructUrlTestCase(parts=("http://arthur.ai/",), validate=True, default_https=True,
                              expected="http://arthur.ai"),
         ConstructUrlTestCase(parts=("foo bar baz",), validate=True, default_https=False, expected=UserValueError)]


@pytest.mark.parametrize("case", CASES)
def test_construct_url(case: ConstructUrlTestCase):
    if isinstance(case.expected, str):
        actual = construct_url(*case.parts, validate=case.validate, default_https=case.default_https)
        assert actual == case.expected
    elif issubclass(case.expected, BaseException):
        with pytest.raises(case.expected):
            construct_url(*case.parts, validate=case.validate, default_https=case.default_https)
    else:
        raise ValueError()
