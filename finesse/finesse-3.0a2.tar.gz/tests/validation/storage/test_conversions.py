import pytest
import numpy as np
from finesse.utilities.storage import np_dtype_from_json, np_dtype_to_json
from finesse.utilities.storage import type_from_json, type_to_json
from finesse.solutions import ArraySolution


@pytest.mark.parametrize(
    "descr",
    (
        float,
        "float",
        "d",
        "<f8",
        "i4",
        [
            ("refl", "<f8"),
            ("circ", "<f8"),
            ("trns", "<f8"),
            ("E", "<c16", (6,)),
            ("Z", "<f8", (1, 2, 3)),
        ],
    ),
)
def test_dtype_json(descr):
    dtype_in = np.dtype(descr)
    dtype_out = np_dtype_from_json(np_dtype_to_json(dtype_in))
    assert dtype_in == dtype_out


@pytest.mark.parametrize("descr", (float, int, ArraySolution, str))
def test_type_json(descr):
    type_in = descr
    type_out = type_from_json(type_to_json(type_in))
    assert type_in == type_out
