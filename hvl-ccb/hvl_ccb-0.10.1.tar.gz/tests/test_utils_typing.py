#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Test for typing utils
"""
import sys
from typing import List, Union, Callable

import pytest

from hvl_ccb.utils.typing import (
    is_generic_type_hint,
    check_generic_type,
)


def test_is_generic_type_hint():

    for type_ in (1, "a", (), list, int, str, object):
        assert not is_generic_type_hint(type_)

    for type_ in (List[int], List, Union[None, List[int]], Union, Callable):
        assert is_generic_type_hint(type_)

    if sys.version_info >= (3, 9):
        for type_ in (list[int],):  # PEP 585
            assert is_generic_type_hint(type_)


def test_check_generic_type():

    with pytest.raises(ValueError):
        check_generic_type([], list)

    assert check_generic_type([], List) is None

    with pytest.raises(TypeError):
        check_generic_type(["a"], List[int])

    assert check_generic_type([1, 2], List[int]) is None

    with pytest.raises(TypeError):
        check_generic_type([1, 1.0], List[int])

    assert check_generic_type([1, 1.0], List[Union[int, float]]) is None
    assert check_generic_type(None, Union[None, List[int]]) is None
    assert check_generic_type([1, 2], Union[None, List[int]]) is None
