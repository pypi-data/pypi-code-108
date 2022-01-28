import numpy as np
import finesse


def test_zpk_filter():
    model = finesse.Model()
    model.parse(
        """
    # Finesse always expects some optics to be present
    # so we make a laser incident on some photodiode
    l l1 P=1
    readout_dc PD l1.p1.o
    # Amplitude modulate a laser
    sgen sig l1.amp

    variable R 1
    variable C 1
    zpk ZPK_RC [] [-1/(&R*&C)]
    link(PD.DC, ZPK_RC)
    ad lpf ZPK_RC.p2.o f=&fsig

    fsig(1/(2*pi*&R*&C))
    """
    )

    sol = model.run()
    # Should always get the 1/sqrt(2) drop at the pole frequency
    # for a single pole filter.
    assert np.allclose(abs(sol["lpf"]), 1 / np.sqrt(2))
    model.ZPK_RC.gain *= 0
    sol = model.run()
    assert np.allclose(abs(sol["lpf"]), 0)
    model.ZPK_RC.gain = 1
    model.ZPK_RC.p = []
    sol = model.run()
    assert np.allclose(abs(sol["lpf"]), 1)
    # Try resetting as symbols
    model.ZPK_RC.p = [-1 / (model.R.ref * model.C.ref)]
    sol = model.run()
    assert np.allclose(abs(sol["lpf"]), 1 / np.sqrt(2))
    # cancel out poles with zeros
    model.ZPK_RC.z = [-1 / (model.R.ref * model.C.ref)]
    model.ZPK_RC.p = [-1 / (model.R.ref * model.C.ref)]
    sol = model.run()
    assert np.allclose(abs(sol["lpf"]), 1)
