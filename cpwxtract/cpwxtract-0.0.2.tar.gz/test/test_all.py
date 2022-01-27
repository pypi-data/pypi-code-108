#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# This file is part of cpwxtract
# License: GPLv3
# See the documentation at benvial.gitlab.io/cpwxtract

import pytest


def test_metadata(monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "importlib.metadata", None)
    import cpwxtract


def test_nometadata():
    import importlib

    import cpwxtract

    importlib.reload(cpwxtract.__about__)


def test_data():
    import cpwxtract

    cpwxtract.__about__.get_meta(None)


def test_import():
    import cpwxtract


def init_cpw(grounded, thickness):

    import cpwxtract as cp

    ###############################################################################
    # Define CPW

    L = 5  # Length of transmission line in mm
    w = 0.347  # width of central conductor in mm
    s = 0.175  # gap from centre to ground in mm
    h_metal = 1e-3
    cpw = cp.CPW(L, w, s, h_metal, thickness=thickness, epsilon=1, grounded=grounded)
    return cpw


def init_meas():
    import numpy as np

    import cpwxtract as cp

    # sample_file = f"testdata.s2p"
    sample_file = f"examples/data/alumina-uncoated-5mm.s2p"
    frequencies = np.arange(1.5, 5, 0.025)
    Smeas = cp.get_Smeas(sample_file, frequencies)
    return frequencies, Smeas


@pytest.mark.parametrize("backend,compile", [("nlopt", True), ("scipy", False)])
def test_extract(backend, compile):
    import numpy as np

    import cpwxtract as cp

    frequencies, Smeas = init_meas()

    grounded = False
    thickness = None

    cpw = init_cpw(grounded, thickness)

    ###############################################################################
    # Extract

    guess = 11 * (1 - 0 * 1j)

    ext = cp.Extractor(
        frequencies,
        Smeas,
        guess,
        cpw,
        eps_min=1 - 20 * 1j,
        eps_max=20 + 0 * 1j,
        options=None,
        verbose=True,
        backend=backend,
        compile=compile,
    )
    ext.run()

    eps_opt = ext.eps_opt
    print(f">>> objective = {ext.opt.fun}")


def test_err():
    import cpwxtract as cp

    frequencies, Smeas = init_meas()

    with pytest.raises(ValueError):
        cpw = init_cpw(False, None)
        ext = cp.Extractor(frequencies, Smeas, 1, cpw, backend="fake")

    with pytest.raises(ValueError):
        cpw = init_cpw(True, None)


@pytest.mark.parametrize("grounded,thickness", [(False, None), (False, 5), (True, 5)])
def test_xpw(grounded, thickness):
    cpw = init_cpw(grounded, thickness)
    print(cpw.effective_epsilon)
    print(cpw.impedance)


def test_help():
    import numpy as np

    import cpwxtract as cp

    cp.unwrap(np.linspace(0, 3, 10))
    cp.complex2aphi((3 + 1j) * np.linspace(0, 1, 10))
