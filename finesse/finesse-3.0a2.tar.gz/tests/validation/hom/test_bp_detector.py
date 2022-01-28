"""Tests of beam property detection against analytics."""

import numpy as np
from numpy.testing import assert_allclose
import pytest
from finesse import Model
from finesse.analysis.actions import X2axis


@pytest.fixture()
def simple_laser_model():
    IFO = Model()
    IFO.parse(
        """
    l L0 P=1
    s s0 L0.p1 END.p1
    nothing END

    gauss gL0 L0.p1.o w0=1m z=0
    """
    )

    return IFO


@pytest.mark.parametrize(
    "target", ("w0", "z", "q", "w", "rc", "s", "zr", "gouy", "div")
)
@pytest.mark.parametrize("lambda0", (1064e-9, 1550e-9))
@pytest.mark.parametrize("direction", ("x", "y", "xy"))
def test_beam_properties_with_gauss_scan(
    simple_laser_model: Model, target, lambda0, direction
):
    """Test detection of each beam property against analytics by scanning over w0[x|y],
    z[x|y] of an input beam parameter."""
    IFO = simple_laser_model
    IFO.lambda0 = lambda0
    if direction == "xy":
        IFO.parse(f"bp L0_{target}x L0.p1.o {target} x")
        IFO.parse(f"bp L0_{target}y L0.p1.o {target} y")

        # Set up sagittal plane w0, z to track tangential plane
        IFO.gL0.w0y = IFO.gL0.w0x.ref
        IFO.gL0.zy = IFO.gL0.zx.ref
        d = "x"
    else:
        IFO.parse(f"bp L0_{target} L0.p1.o {target} {direction}")
        d = direction

    # Don't want to go through z = 0 to avoid runtime warnings in analytics
    # due to division by zero for RoC at this point
    if target == "rc":
        N = 20
    else:
        N = 21

    w0s = np.linspace(10e-6, 10e-2, N)
    zs = np.linspace(-10, 10, N)

    W0S, ZS = np.meshgrid(w0s, zs)
    ZRS = np.pi * W0S ** 2 / IFO.lambda0

    analytics = {
        "w0": lambda _W0S, _ZS, _ZRS: _W0S,
        "z": lambda _W0S, _ZS, _ZRS: _ZS,
        # q(z) = z + 1j * zr
        "q": lambda _W0S, _ZS, _ZRS: _ZS + 1j * _ZRS,
        # w(z) = w0 * sqrt(1 + (z / zr)**2)
        "w": lambda _W0S, _ZS, _ZRS: _W0S * np.sqrt(1 + (_ZS / _ZRS) ** 2),
        # Rc(z) = z * (1 + (zr / z)**2)
        "rc": lambda _W0S, _ZS, _ZRS: _ZS * (1 + (_ZRS / _ZS) ** 2),
        # S(z) = z / (z**2 + zr**2)
        "s": lambda _W0S, _ZS, _ZRS: _ZS / (_ZS ** 2 + _ZRS ** 2),
        # zr = pi * w0**2 / lambda
        "zr": lambda _W0S, _ZS, _ZRS: _ZRS,
        # psi(z) = atan(z / zr),
        "gouy": lambda _W0s, _ZS, _ZRS: np.arctan2(_ZS, _ZRS),
        # Theta \approx lambda / (pi * w0)
        "div": lambda _W0S, _ZS, _ZRS: IFO.lambda0 / (np.pi * _W0S),
    }
    expect = analytics[target](W0S, ZS, ZRS)

    out = IFO.run(X2axis(
        f"gL0.w0{d}",
        "lin",
        w0s[0],
        w0s[-1],
        w0s.size - 1,
        f"gL0.z{d}",
        "lin",
        zs[0],
        zs[-1],
        zs.size - 1,
    ))
    if direction == "xy":
        psx = out[f"L0_{target}x"].T
        psy = out[f"L0_{target}x"].T

        # Make sure tangential, sagittal plane properties are equal
        assert_allclose(psx, psy)
        ps = psx
    else:
        ps = out[f"L0_{target}"].T

    assert_allclose(ps, expect)
