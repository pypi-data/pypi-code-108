# -*- mode: python; coding: utf-8 -*-
# Copyright 2019 the AAS WorldWide Telescope project
# Licensed under the MIT License.

import numpy as np
import pytest

from .. import pyramid
from ..pyramid import Pos


def test_next_highest_power_of_2():
    assert pyramid.next_highest_power_of_2(1) == 256
    assert pyramid.next_highest_power_of_2(256) == 256
    assert pyramid.next_highest_power_of_2(257) == 512


def test_depth2tiles():
    assert pyramid.depth2tiles(0) == 1
    assert pyramid.depth2tiles(1) == 5
    assert pyramid.depth2tiles(2) == 21
    assert pyramid.depth2tiles(10) == 1398101


def test_is_subtile():
    from ..pyramid import is_subtile

    assert is_subtile(Pos(2, 0, 0), Pos(1, 0, 0)) == True

    with pytest.raises(ValueError):
        is_subtile(Pos(1, 0, 0), Pos(2, 0, 0))


def test_pos_parent():
    from ..pyramid import pos_parent

    assert pos_parent(Pos(7, 65, 33)) == (Pos(6, 32, 16), 1, 1)

    with pytest.raises(ValueError):
        pos_parent(Pos(0, 0, 0))


def test_generate_pos():
    from ..pyramid import generate_pos

    assert list(generate_pos(0)) == [Pos(0, 0, 0)]

    assert list(generate_pos(1)) == [
        Pos(1, 0, 0),
        Pos(1, 1, 0),
        Pos(1, 0, 1),
        Pos(1, 1, 1),
        Pos(0, 0, 0),
    ]
