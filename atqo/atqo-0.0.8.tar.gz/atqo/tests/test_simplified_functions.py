from itertools import chain, product

import pytest

from atqo import parallel_map
from atqo.distributed_apis import DIST_API_MAP


def add2(x):
    return x + 2


def extstr(x):
    return f"{x}-add"


def div(x):
    return 10 / x


@pytest.mark.parametrize(
    ["fun", "inl"],
    product(
        [add2, extstr, div], [[1, 2, 3, 4], ["a", 10, "b", 3], [None, 2, 0]]
    ),
)
def test_batch(fun, inl):
    res = []
    exs = []
    for x in inl:
        try:
            res.append(fun(x))
        except Exception as e:
            exs.append(e)

    map_outs = chain(
        *[
            [parallel_map(fun, inl, dapi), parallel_map(fun, iter(inl), dapi)]
            for dapi in DIST_API_MAP.keys()
        ]
    )
    for mout in map_outs:
        mres = []
        mex = []
        for o in mout:
            if isinstance(o, Exception):
                mex.append(o)
            else:
                mres.append(o)
        assert sorted(mres) == sorted(res)
        for _w in [str, type]:
            assert set(map(_w, mex)) == set(map(_w, exs))


def test_extras():

    with pytest.raises(TypeError):
        parallel_map(
            add2,
            [1, 2, 3, "X", "Y"],
            batch_size=3,
            pbar=True,
            raise_errors=True,
        )
