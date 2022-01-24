from __future__ import annotations
import pytest
import numpy as np
from myqueue.caching import encode, decode, CachedFunction
from datetime import datetime
from math import inf
from myqueue.workflow import create_task

objects = [
    [27, 1.4, {'a': 7, 'b': [1, 2]}, inf, -inf],
    1 + 2j,
    None,
    datetime.now(),
    np.zeros((0, 3), complex),
    np.zeros((3, 0), complex),
    np.zeros((2, 1), complex),
    np.zeros(2, np.float32),
    np.ones((2, 2), int)]


@pytest.mark.parametrize('obj1', objects)
def test_encoding(obj1):
    """Test encoding/decoding."""
    text1 = encode(obj1)
    obj2 = decode(text1)
    text2 = encode(obj2)
    assert text1 == text2
    print(text1)
    if isinstance(obj1, np.ndarray):
        assert (obj1 == obj2).all()
        assert obj1.shape == obj2.shape
        assert obj1.dtype == obj2.dtype
    else:
        assert obj1 == obj2


def test_has():
    """Test function that returns non-jsonable object."""
    function = CachedFunction(
        function=lambda: Exception,
        has=lambda *args, **kwargs: True)
    task = create_task(function=function)
    task.cmd.run()
