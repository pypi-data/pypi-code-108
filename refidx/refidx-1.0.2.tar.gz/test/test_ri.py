#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# This file is part of refidx
# License: GPLv3
# See the documentation at benvial.gitlab.io/refidx

import pytest


def _test_material(mat):
    wr = mat.wavelength_range
    if wr is not None:
        lamb = (wr[1] + wr[0]) / 2
    else:
        lamb = 1.0
    index = mat.get_index(lamb)
    print(mat)
    # print(mat._data)
    print(mat.info)
    print("wavelength range: ", wr)
    print("wavelength", lamb)
    print("refractive index: ", index)

    if wr is not None:

        with pytest.raises(ValueError):
            lamb = mat.wavelength_range[0] / 2
            index = mat.get_index(lamb)

        with pytest.raises(ValueError):
            lamb = mat.wavelength_range[1] * 2
            index = mat.get_index(lamb)


def test_all():
    import os

    import refidx

    database = refidx.DataBase()
    materials = database.materials
    j = 0
    for key, value, dictionary in refidx.core.recursive_items(materials):
        if isinstance(value, refidx.Material):
            print("######################################################")
            _test_material(value)
            j += 1

    assert j == refidx.core.nb_mat
    mat = database.random()
    assert isinstance(mat, refidx.Material)

    mat.print_info()
    mat.print_info(True)
    mat.print_info(True, ".")
    os.remove("out.html")


def test_print_ipython(monkeypatch):
    import importlib
    import sys

    monkeypatch.setitem(sys.modules, "IPython.display", None)
    import refidx

    importlib.reload(refidx)
    database = refidx.DataBase()
    mat = database.random()
    mat.print_info(True)
